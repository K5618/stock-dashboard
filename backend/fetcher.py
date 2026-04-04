import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import requests
from concurrent.futures import ThreadPoolExecutor
import json
import os
import math

REGION_INDICES = {
    "US": { "^DJI": "Dow Jones", "^GSPC": "S&P 500", "^IXIC": "NASDAQ", "^SOX": "PHLX Semiconductor", "^RUT": "Russell 2000" },
    "Europe": { "^GDAXI": "DAX", "^FCHI": "CAC 40", "^FTSE": "FTSE 100" },
    "Asia": { "^TWII": "TAIEX", "^TWOII": "OTC", "^N225": "Nikkei 225", "^KS11": "KOSPI", "^AXJO": "ASX 200", "^HSI": "Hang Seng", "XIN9.FGI": "China A50", "000300.SS": "CSI 300", "000001.SS": "SSE Composite" }
}

SECTOR_ETFS = {
    "XLK": "Technology", "XLV": "Health Care", "XLF": "Financials", "XLY": "Consumer Discretionary", "XLI": "Industrials", "XLP": "Consumer Staples", "XLE": "Energy", "XLU": "Utilities", "XLRE": "Real Estate", "XLB": "Materials", "XLC": "Communication Services"
}

YF_SECTOR_MAPPING = {
    "Healthcare": "Health Care", "Financial Services": "Financials", "Consumer Cyclical": "Consumer Discretionary", "Consumer Defensive": "Consumer Staples", "Basic Materials": "Materials"
}

def get_screener_universe():
    """Fetch Top 1200 US stocks with all necessary quantitative fields from TV Scanner"""
    try:
        url = "https://scanner.tradingview.com/america/scan"
        query = {
            "columns": ["name", "description", "sector", "industry", "close", "change", "volume", "market_cap_basic", "price_earnings_ttm", "High.1M", "High.3M", "High.6M", "High.All", "Low.1M", "Low.3M", "Low.6M", "Low.All"],
            "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
            "range": [0, 1200]
        }
        res = requests.post(url, json=query).json()
        stocks = []
        for x in res['data']:
            d = x['d']
            # Format: 'name', 'desc', 'sector', 'industry', 'close', 'change', 'vol', 'cap', 'pe', H1, H3, H6, HAll, L1, L3, L6, LAll
            obj = {
                "symbol": d[0], "name": d[1], "sector": d[2], "industry": d[3], 
                "close_price": d[4], "change_pct": d[5], "volume": d[6], 
                "market_cap": d[7], "pe_ratio": d[8],
                "h_30": d[9], "h_90": d[10], "h_180": d[11], "h_all": d[12],
                "l_30": d[13], "l_90": d[14], "l_180": d[15], "l_all": d[16]
            }
            stocks.append(obj)
        return stocks
    except Exception as e:
        print("Error getting screener data:", e)
        return []

def fetch_info(sym):
    try:
        info = yf.Ticker(sym).info
        return sym, info.get("sector", "Unknown"), info.get("industry", "Unknown"), info.get("marketCap", 0)
    except:
        return sym, "Unknown", "Unknown", 0

def update_all_data():
    now_str = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S (UTC+8)")
    print(f"Starting data generation at {now_str}")
    
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
        }
    }
    
    # 1. Update Regional Indices
    for region, indices in REGION_INDICES.items():
        for symbol, name in indices.items():
            try:
                hist = yf.Ticker(symbol).history(period="5d")
                if len(hist) >= 2:
                    close = float(hist['Close'].iloc[-1])
                    prev = float(hist['Close'].iloc[-2])
                    change = close - prev
                    change_pct = (change / prev) * 100
                    vol = float(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0
                    date_str = hist.index[-1].strftime("%Y-%m-%d")
                    result_data["indices"]["data"][region].append({
                        "symbol": symbol, "name": name, "date": date_str, "close_price": close, "change_pt": change, "change_pct": change_pct, "volume": vol
                    })
            except Exception as e:
                pass

    # 2. Update Sector ETFs
    for symbol, name in SECTOR_ETFS.items():
        try:
            hist = yf.Ticker(symbol).history(period="5d")
            if len(hist) >= 2:
                close = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                change = close - prev
                change_pct = (change / prev) * 100
                date_str = hist.index[-1].strftime("%Y-%m-%d")
                result_data["sectors"]["data"].append({
                    "symbol": symbol, "name": name, "date": date_str, "close_price": close, "change_pt": change, "change_pct": change_pct
                })
        except Exception as e:
            pass

    # 3. New Unified Top 1200 Screener & Top Stocks Logic
    universe = get_screener_universe()
    print(f"Fetched {len(universe)} stocks from screener")
    
    # Process for Top 10 by Sector (replacing yfinance fallback entirely for performance)
    sector_group = {}
    for s in universe:
        sec = s.get('sector', 'Unknown')
        sec = YF_SECTOR_MAPPING.get(sec, sec) # normalize
        sector_group.setdefault(sec, []).append(s)
        
        # Block 1: Upward Gains
        cg = s.get('change_pct', 0)
        c = s.get('close_price', 0)
        
        # Format object for frontend screener
        screen_obj = {
            "symbol": s['symbol'], "name": s['name'], "sector": s['sector'], "industry": s['industry'],
            "close_price": c, "change_pct": cg, "volume": s['volume'], "market_cap": s['market_cap'], "pe_ratio": s['pe_ratio'], "date": now_str[:10]
        }
        
        if cg != None:
            if cg >= 10: result_data["screener"]["block1"]["gain_10"].append(screen_obj)
            if cg >= 5: result_data["screener"]["block1"]["gain_5"].append(screen_obj)
            if cg >= 3: result_data["screener"]["block1"]["gain_3"].append(screen_obj)
            
            if cg <= -10: result_data["screener"]["block3"]["loss_10"].append(screen_obj)
            if cg <= -5: result_data["screener"]["block3"]["loss_5"].append(screen_obj)
            if cg <= -3: result_data["screener"]["block3"]["loss_3"].append(screen_obj)
        
        # Block 2 & 4: New Highs & Lows (tolerance 0.5% for precise matching)
        if c != None:
            def near(val, target): return val != None and target != None and abs(val - target) / target < 0.005
            if near(c, s.get('h_30')): result_data["screener"]["block2"]["h_30"].append(screen_obj)
            if near(c, s.get('h_90')): result_data["screener"]["block2"]["h_90"].append(screen_obj)
            if near(c, s.get('h_180')): result_data["screener"]["block2"]["h_180"].append(screen_obj)
            if near(c, s.get('h_all')): result_data["screener"]["block2"]["h_all"].append(screen_obj)
            
            if near(c, s.get('l_30')): result_data["screener"]["block4"]["l_30"].append(screen_obj)
            if near(c, s.get('l_90')): result_data["screener"]["block4"]["l_90"].append(screen_obj)
            if near(c, s.get('l_180')): result_data["screener"]["block4"]["l_180"].append(screen_obj)
            if near(c, s.get('l_all')): result_data["screener"]["block4"]["l_all"].append(screen_obj)

    # Dump Top 10 by sector
    for sec, lst in sector_group.items():
        top_mc = sorted(lst, key=lambda x: x['market_cap'] if x['market_cap'] else 0, reverse=True)[:10]
        result_data["top_stocks"]["data"][sec] = {"top_market_cap": top_mc}

    # Remove any completely empty blocks internally if needed (optional)

    def clean_nan(obj):
        if isinstance(obj, dict): return {k: clean_nan(v) for k, v in obj.items()}
        elif isinstance(obj, list): return [clean_nan(v) for v in obj]
        elif isinstance(obj, float) and math.isnan(obj): return None
        return obj
    
    clean_data = clean_nan(result_data)
    
    try:
        from supabase import create_client, Client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if url and key:
            supabase: Client = create_client(url, key)
            res = supabase.table("market_snapshots").insert({"data": clean_data}).execute()
            print("Successfully uploaded snapshot to Supabase.")
        else:
            print("Supabase credentials not found in environment. Saving locally as fallback.")
            out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public'))
            if not os.path.exists(out_dir): os.makedirs(out_dir)
            out_file = os.path.join(out_dir, 'data.json')
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(clean_data, f, ensure_ascii=False, indent=2)
            print(f"Data successfully generated at {out_file}")
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")

if __name__ == '__main__':
    update_all_data()
