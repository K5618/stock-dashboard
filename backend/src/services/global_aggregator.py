# src/services/global_aggregator.py
from datetime import datetime, timezone, timedelta
from src.config.constants import REGION_INDICES, SECTOR_ETFS, COMMODITIES_HIERARCHY
from src.providers.tv_scraper import TradingViewScanner
from src.utils.parsers import clean_nan

class GlobalDataAggregator:
    def __init__(self):
        self.tv_scanner = TradingViewScanner(market="america")

    def gather_data(self) -> dict:
        now_str = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S (UTC+8)")
        print(f"Starting Global Data generation at {now_str}")

        result_data = {
            "status": { "last_updated": now_str, "warnings": [] },
            "indices": {"data": { "US": [], "Europe": [], "Asia": [] }},
            "sectors": {"data": []},
            "top_stocks": {"data": {}},
            "screener": {
                "block1": {"gain_3": [], "gain_5": [], "gain_10": []},
                "block2": {"h_30": [], "h_90": [], "h_180": [], "h_all": []},
                "block3": {"loss_3": [], "loss_5": [], "loss_10": []},
                "block4": {"l_30": [], "l_90": [], "l_180": [], "l_all": []}
            },
            "commodities": {
                "Metals": {},
                "Energy, Petrochemicals & Chemicals": {},
                "Agricultural Products": {}
            }
        }

        tv_errors = 0
        
        # Collect all tickers needed
        index_tickers = [sym for items in REGION_INDICES.values() for sym in items.keys()]
        sector_tickers = list(SECTOR_ETFS.keys())
        commodity_tickers = [sym for cats in COMMODITIES_HIERARCHY.values() for items in cats.values() for sym in items.values()]
        
        all_tickers = list(set(index_tickers + sector_tickers + commodity_tickers))
        fetched_data = {}
        
        try:
            batch_result = self.tv_scanner.fetch_specific_symbols(all_tickers)
            for item in batch_result:
                close_p = item['close_price']
                pct = item['change_pct']
                if close_p and pct is not None:
                    try:
                        item['change_pt'] = close_p - (close_p / (1 + pct / 100))
                    except:
                        item['change_pt'] = 0
                else:
                    item['change_pt'] = 0
                item['date'] = now_str[:10]
                fetched_data[item['symbol']] = item
        except Exception as e:
            print(f"Error fetching specific symbols from TV: {e}")
            tv_errors += 1
            result_data["status"]["warnings"].append("TradingView Global specific symbols fetch failed.")

        # 1. Update Regional Indices
        for region, indices in REGION_INDICES.items():
            for symbol, name in indices.items():
                if symbol in fetched_data:
                    data = fetched_data[symbol].copy()
                    data['name'] = name
                    result_data["indices"]["data"][region].append(data)

        # 2. Update Sector ETFs
        for symbol, name in SECTOR_ETFS.items():
            if symbol in fetched_data:
                data = fetched_data[symbol].copy()
                data['name'] = name
                result_data["sectors"]["data"].append(data)

        # 3. New Commodities
        for major_cat, sub_cat_obj in COMMODITIES_HIERARCHY.items():
            for sub_cat, items in sub_cat_obj.items():
                result_data["commodities"][major_cat][sub_cat] = []
                for name, symbol in items.items():
                    if symbol in fetched_data:
                        data = fetched_data[symbol].copy()
                        data['name'] = name
                        result_data["commodities"][major_cat][sub_cat].append(data)

        # 4. TV Screener
        try:
            tv_stocks = self.tv_scanner.fetch_data(1200)
        except Exception:
            tv_stocks = []
            result_data["status"]["warnings"].append("TradingView Scanner API unavailable")

        for s in tv_stocks:
            s['date'] = now_str[:10]
            cg = s.get('change_pct')
            c = s.get('close_price')
            
            if cg is not None:
                if cg >= 10: result_data["screener"]["block1"]["gain_10"].append(s)
                elif cg >= 5: result_data["screener"]["block1"]["gain_5"].append(s)
                elif cg >= 3: result_data["screener"]["block1"]["gain_3"].append(s)
                
                if cg <= -10: result_data["screener"]["block3"]["loss_10"].append(s)
                elif cg <= -5: result_data["screener"]["block3"]["loss_5"].append(s)
                elif cg <= -3: result_data["screener"]["block3"]["loss_3"].append(s)
                
            if c is not None and c > 0:
                def near(val, target): return val is not None and target is not None and abs(val - target) / target < 0.005
                if near(c, s.get('h_30')): result_data["screener"]["block2"]["h_30"].append(s)
                if near(c, s.get('h_90')): result_data["screener"]["block2"]["h_90"].append(s)
                if near(c, s.get('h_180')): result_data["screener"]["block2"]["h_180"].append(s)
                if near(c, s.get('h_all')): result_data["screener"]["block2"]["h_all"].append(s)
                
                if near(c, s.get('l_30')): result_data["screener"]["block4"]["l_30"].append(s)
                if near(c, s.get('l_90')): result_data["screener"]["block4"]["l_90"].append(s)
                if near(c, s.get('l_180')): result_data["screener"]["block4"]["l_180"].append(s)
                if near(c, s.get('l_all')): result_data["screener"]["block4"]["l_all"].append(s)

        # 5. Top Stocks (TradingView based, mapped to GICS)
        import os
        import json
        sector_map = {}
        map_path = os.path.join(os.path.dirname(__file__), "..", "config", "sector_map.json")
        try:
            with open(map_path, "r", encoding="utf-8") as f:
                sector_map = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load sector_map.json: {e}")

        all_hf_stocks = []
        for s in (tv_stocks[:500] if tv_stocks else []):
            sym = s.get('symbol')
            if not sym: continue
            
            # Exclude preferred and depositary shares
            name_lower = s.get('name', '').lower()
            if '/' in sym or '-' in sym or 'pfd' in name_lower or 'depositary' in name_lower or 'preferred' in name_lower:
                continue
            
            # Map TV sector to GICS via our loaded local map (fallback to TV sector if not found)
            sec = sector_map.get(sym, s.get('sector', 'Unknown'))
            cap = s.get('market_cap', 0)
            
            if sec != "Unknown" and cap > 0:
                stock_data = {
                    'symbol': sym,
                    'name': s.get('name', sym),
                    'sector': sec,
                    'market_cap': cap,
                    'date': now_str[:10],
                    'close_price': s.get('close_price', 0),
                    'change_pct': s.get('change_pct', 0),
                    'volume': s.get('volume', 0)
                }
                
                # Optional absolute change calculation
                close_p = stock_data['close_price']
                pct = stock_data['change_pct']
                if close_p and pct is not None:
                    try:
                        stock_data['change_pt'] = close_p - (close_p / (1 + pct / 100))
                    except:
                        stock_data['change_pt'] = 0
                else:
                    stock_data['change_pt'] = 0

                all_hf_stocks.append(stock_data)

        sector_group = {}
        for s in all_hf_stocks:
            sector_group.setdefault(s['sector'], []).append(s)

        for sec, lst in sector_group.items():
            top_mc = sorted(lst, key=lambda x: x.get('market_cap', 0), reverse=True)[:10]
            result_data["top_stocks"]["data"][sec] = {"top_market_cap": top_mc}

        if tv_errors > 0:
            result_data["status"]["warnings"].append(f"TradingView API encountered errors fetching batch symbols.")

        return clean_nan(result_data)
