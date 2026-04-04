import requests

url = "https://scanner.tradingview.com/america/scan"

query = {
    "columns": ["name", "description", "sector", "industry", "close", "change", "volume", "market_cap_basic", "price_earnings_ttm"],
    "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
    "range": [0, 5]
}
try:
    res = requests.post(url, json=query).json()
    print("Columns requested:")
    print(query["columns"])
    print("\nData:")
    for ticker in res.get('data', []):
        print(ticker['d'])
except Exception as e:
    print("Error:", e)
