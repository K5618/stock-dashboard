# src/services/global_aggregator.py
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
from src.config.constants import REGION_INDICES, SECTOR_ETFS, COMMODITIES_HIERARCHY, YF_SECTOR_MAPPING, COMMODITIES_EXCHANGE_MAPPING
from src.providers.yfinance_client import YFinanceProvider
from src.providers.tv_scraper import TradingViewScanner
from src.utils.parsers import clean_nan

class GlobalDataAggregator:
    def __init__(self):
        self.yf_provider = YFinanceProvider()
        self.tv_scanner = TradingViewScanner(market="america")

    def gather_data(self) -> dict:
        now_str = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S (UTC+8)")
        print(f"Starting Global Data generation at {now_str}")

        result_data = {
            "status": { "last_updated": now_str },
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

        # 1. Update Regional Indices
        for region, indices in REGION_INDICES.items():
            for symbol, name in indices.items():
                try:
                    data = self.yf_provider.fetch_data(symbol)
                    if data:
                        data['name'] = name
                        result_data["indices"]["data"][region].append(data)
                except Exception:
                    pass

        # 2. Update Sector ETFs
        for symbol, name in SECTOR_ETFS.items():
            try:
                data = self.yf_provider.fetch_data(symbol)
                if data:
                    data['name'] = name
                    result_data["sectors"]["data"].append(data)
            except Exception:
                pass

        # 3. New Commodities
        for major_cat, sub_cat_obj in COMMODITIES_HIERARCHY.items():
            for sub_cat, items in sub_cat_obj.items():
                result_data["commodities"][major_cat][sub_cat] = []
                for name, symbol in items.items():
                    try:
                        data = self.yf_provider.fetch_data(symbol)
                        if data:
                            data['name'] = name
                            exchange = COMMODITIES_EXCHANGE_MAPPING.get(symbol, "CME/ICE")
                            if symbol == "LIT": exchange = "ETF Proxy"
                            data['exchange'] = exchange
                            result_data["commodities"][major_cat][sub_cat].append(data)
                    except Exception:
                        pass

        # 4. TV Screener
        try:
            tv_stocks = self.tv_scanner.fetch_data(1200)
        except Exception:
            tv_stocks = []

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

        # 5. Top Stocks (YFinance check matching GICS)
        tickers_500 = [x['symbol'] for x in tv_stocks[:500]] if tv_stocks else []
        info_dict = {}
        if tickers_500:
            with ThreadPoolExecutor(max_workers=10) as executor:
                results = executor.map(self.yf_provider.fetch_info, tickers_500)
                for res in results:
                    if res:
                        info_dict[res['symbol']] = res

        all_hf_stocks = []
        for sym in tickers_500:
            try:
                hist = self.yf_provider.fetch_data(sym)
                if hist:
                    sec = info_dict.get(sym, {}).get('sector', "Unknown")
                    sec = YF_SECTOR_MAPPING.get(sec, sec)
                    cap = info_dict.get(sym, {}).get('market_cap', 0)
                    
                    if sec != "Unknown" and cap > 0:
                        hist['sector'] = sec
                        hist['market_cap'] = cap
                        all_hf_stocks.append(hist)
            except Exception:
                pass

        sector_group = {}
        for s in all_hf_stocks:
            sector_group.setdefault(s['sector'], []).append(s)

        for sec, lst in sector_group.items():
            top_mc = sorted(lst, key=lambda x: x.get('market_cap', 0), reverse=True)[:10]
            result_data["top_stocks"]["data"][sec] = {"top_market_cap": top_mc}

        return clean_nan(result_data)
