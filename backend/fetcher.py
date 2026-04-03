import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import requests
from concurrent.futures import ThreadPoolExecutor
import json
import os

GLOBAL_INDICES = {
    "^DJI": "Dow Jones", "^GSPC": "S&P 500", "^IXIC": "NASDAQ", 
    "^SOX": "PHLX Semiconductor", "^RUT": "Russell 2000", "^GDAXI": "DAX", 
    "^FCHI": "CAC 40", "^FTSE": "FTSE 100", "^N225": "Nikkei 225", "^KS11": "KOSPI"
}

SECTOR_ETFS = {
    "XLK": "Technology", "XLV": "Health Care", "XLF": "Financials",
    "XLY": "Consumer Discretionary", "XLI": "Industrials", "XLP": "Consumer Staples",
    "XLE": "Energy", "XLU": "Utilities", "XLRE": "Real Estate",
    "XLB": "Materials", "XLC": "Communication Services"
}

def get_stock_universe():
    try:
        url = "https://scanner.tradingview.com/america/scan"
        query = {
            "columns": ["name", "description"],
            "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
            "range": [0, 600]
        }
        res = requests.post(url, json=query).json()
        clean_tickers = {}
        for x in res['data']:
            t = x['d'][0]
            desc = x['d'][1]
            if "/" not in t:
                clean = t.replace(".", "-")
                clean_tickers[clean] = desc
        return clean_tickers
    except Exception as e:
        print("Error getting universe from tradingview:", e)
        return {"AAPL": "Apple Inc.", "MSFT": "Microsoft", "NVDA": "NVIDIA", "TSM": "TSMC"}

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
        "indices": {"data": []},
        "sectors": {"data": []},
        "top_stocks": {"data": {}}
    }
    
    # 1. Update Global Indices
    for symbol, name in GLOBAL_INDICES.items():
        try:
            hist = yf.Ticker(symbol).history(period="5d")
            if len(hist) >= 2:
                close = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                change = close - prev
                change_pct = (change / prev) * 100
                vol = float(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0
                date_str = hist.index[-1].strftime("%Y-%m-%d")
                
                result_data["indices"]["data"].append({
                    "symbol": symbol, "name": name, "date": date_str,
                    "close_price": close, "change_pt": change, "change_pct": change_pct, "volume": vol
                })
        except Exception as e:
            print(f"Error fetching index {symbol}: {e}")

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
                    "symbol": symbol, "name": name, "date": date_str,
                    "close_price": close, "change_pt": change, "change_pct": change_pct
                })
        except Exception as e:
            print(f"Error fetching ETF {symbol}: {e}")

    # 3. Update Stocks
    ticker_dict = get_stock_universe()
    tickers = list(ticker_dict.keys())
    if tickers:
        print(f"Fetching prices for {len(tickers)} stocks...")
        prices = yf.download(tickers, period="5d", group_by="ticker", auto_adjust=True, threads=True)
        
        info_dict = {}
        print("Fetching info concurrently...")
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = executor.map(fetch_info, tickers)
            for res in results:
                sym, sec, ind, cap = res
                info_dict[sym] = {'sector': sec, 'industry': ind, 'market_cap': cap}

        # Build list of all valid stocks
        all_stocks = []
        for sym in tickers:
            try:
                hist = prices[sym] if len(tickers) > 1 else prices
                hist = hist.dropna()
                if len(hist) >= 2:
                    close = float(hist['Close'].iloc[-1])
                    prev = float(hist['Close'].iloc[-2])
                    change = close - prev
                    change_pct = (change / prev) * 100
                    vol = float(hist['Volume'].iloc[-1])
                    date_str = hist.index[-1].strftime("%Y-%m-%d")
                    
                    sec = info_dict.get(sym, {}).get('sector', "Unknown")
                    ind = info_dict.get(sym, {}).get('industry', "Unknown")
                    cap = info_dict.get(sym, {}).get('market_cap', 0)
                    
                    if sec != "Unknown" and cap > 0:
                        company_name = ticker_dict.get(sym, sym)
                        all_stocks.append({
                            "symbol": sym, "name": company_name, "sector": sec, "industry": ind,
                            "date": date_str, "close_price": close, "change_pt": change,
                            "change_pct": change_pct, "volume": vol, "market_cap": cap
                        })
            except Exception as e:
                pass

        sector_group = {}
        for s in all_stocks:
            sector_group.setdefault(s['sector'], []).append(s)

        for sec, lst in sector_group.items():
            top_mc = sorted(lst, key=lambda x: x['market_cap'], reverse=True)[:3]
            top_gain = sorted(lst, key=lambda x: x['change_pct'], reverse=True)[:3]
            result_data["top_stocks"]["data"][sec] = {
                "top_market_cap": top_mc,
                "top_gainers": top_gain
            }

    # Write to target path
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public'))
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    out_file = os.path.join(out_dir, 'data.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    print(f"Data successfully generated at {out_file}")

if __name__ == '__main__':
    update_all_data()
