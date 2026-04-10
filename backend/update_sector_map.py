# backend/update_sector_map.py
import os
import json
import requests

TV_TO_GICS_MAPPING = {
    "Electronic Technology": "Technology",
    "Technology Services": "Technology",
    "Health Technology": "Health Care",
    "Health Services": "Health Care",
    "Finance": "Financials",
    "Consumer Durables": "Consumer Discretionary",
    "Consumer Services": "Consumer Discretionary",
    "Retail Trade": "Consumer Discretionary",
    "Consumer Non-Durables": "Consumer Staples",
    "Distribution Services": "Consumer Staples",
    "Producer Manufacturing": "Industrials",
    "Transportation": "Industrials",
    "Industrial Services": "Industrials",
    "Commercial Services": "Industrials",
    "Energy Minerals": "Energy",
    "Utilities": "Utilities",
    "Non-Energy Minerals": "Materials",
    "Process Industries": "Materials",
    "Communications": "Communication Services",
    "Miscellaneous": "Unknown",
    "Government": "Unknown"
}

def update_sector_mapping():
    url = "https://scanner.tradingview.com/america/scan"
    query = {
        "columns": ["name", "sector", "industry", "market_cap_basic"],
        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
        "range": [0, 3000],
        "filter": [
            {"left": "exchange", "operation": "in_range", "right": ["AMEX", "NASDAQ", "NYSE"]},
            {"left": "type", "operation": "in_range", "right": ["stock", "dr"]}
        ]
    }
    
    print("Fetching Top 3000 stocks from TradingView to update sector map...")
    try:
        res = requests.post(url, json=query, timeout=15)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"Failed to fetch data from TradingView: {e}")
        return

    sector_map = {}
    for x in data.get('data', []):
        d = x['d']
        symbol = str(d[0])
        tv_sector = str(d[1]) if d[1] is not None else "Unknown"
        tv_industry = str(d[2]) if d[2] is not None else "Unknown"
        
        # Translate to standard GICS sector used by the dashboard
        standard_sector = TV_TO_GICS_MAPPING.get(tv_sector, tv_sector)
        
        # Override for Real Estate since TV puts them under Finance
        if "Real Estate" in tv_industry:
            standard_sector = "Real Estate"
        
        sector_map[symbol] = standard_sector

    # Ensure config directory exists
    config_dir = os.path.join(os.path.dirname(__file__), "src", "config")
    os.makedirs(config_dir, exist_ok=True)
    
    out_path = os.path.join(config_dir, "sector_map.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sector_map, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully updated sector_map.json with {len(sector_map)} symbols.")
    print(f"File path: {out_path}")

if __name__ == "__main__":
    update_sector_mapping()
