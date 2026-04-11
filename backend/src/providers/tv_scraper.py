# src/providers/tv_scraper.py
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import List, Dict, Any
from src.providers.base import BaseDataProvider

class TradingViewScanner(BaseDataProvider):
    """
    Scrapes TradingView screeners.
    """
    def __init__(self, market: str = "america", proxy: str = None):
        self.market = market
        self.url = f"https://scanner.tradingview.com/{market}/scan"
        self.proxy = proxy

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, ValueError))
    )
    def fetch_data(self, limit: int = 3000) -> List[Dict[str, Any]]:
        query = {
            "columns": [
                "name", "description", "sector", "industry", "close", "change", 
                "volume", "market_cap_basic", "price_earnings_ttm", 
                "High.1M", "High.3M", "High.6M", "High.All", 
                "Low.1M", "Low.3M", "Low.6M", "Low.All", "exchange"
            ],
            "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
            "range": [0, limit]
        }
        
        if self.market == "america":
            query["filter"] = [
                {"left": "exchange", "operation": "in_range", "right": ["AMEX", "NASDAQ", "NYSE"]},
                {"left": "type", "operation": "in_range", "right": ["stock", "dr"]}
            ]
        
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        
        try:
            res = requests.post(self.url, json=query, proxies=proxies, timeout=15)
            res.raise_for_status()
            data = res.json()
        except Exception as e:
            print(f"TradingViewScanner fetch error ({self.market}): {e}")
            raise e

        stocks = []
        for x in data.get('data', []):
            d = x['d']
            stocks.append({
                "symbol": str(d[0]), 
                "name": str(d[1]), 
                "sector": str(d[2]), 
                "industry": str(d[3]), 
                "close_price": float(d[4]) if d[4] is not None else 0.0, 
                "change_pct": float(d[5]) if d[5] is not None else None, 
                "volume": float(d[6]) if d[6] is not None else 0.0, 
                "market_cap": float(d[7]) if d[7] is not None else 0.0, 
                "pe_ratio": float(d[8]) if d[8] is not None else None,
                "h_30": float(d[9]) if d[9] is not None else None, 
                "h_90": float(d[10]) if d[10] is not None else None, 
                "h_180": float(d[11]) if d[11] is not None else None, 
                "h_all": float(d[12]) if d[12] is not None else None,
                "l_30": float(d[13]) if d[13] is not None else None, 
                "l_90": float(d[14]) if d[14] is not None else None, 
                "l_180": float(d[15]) if d[15] is not None else None, 
                "l_all": float(d[16]) if d[16] is not None else None,
                "exchange": str(d[17]) if len(d) > 17 and d[17] is not None else ""
            })
        return stocks

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, ValueError))
    )
    def fetch_specific_symbols(self, symbols: List[str]) -> List[Dict[str, Any]]:
        url = "https://scanner.tradingview.com/global/scan"
        query = {
            "symbols": {"tickers": symbols},
            "columns": [
                "name", "description", "close", "change", "volume", "exchange", "type"
            ]
        }
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        
        try:
            res = requests.post(url, json=query, proxies=proxies, timeout=15)
            res.raise_for_status()
            data = res.json()
        except Exception as e:
            print(f"TradingViewScanner symbol fetch error: {e}")
            raise e

        result = []
        for x in data.get('data', []):
            s = x['s']
            d = x['d']
            result.append({
                "symbol": s,
                "name": str(d[1]),
                "close_price": float(d[2]) if d[2] is not None else 0.0,
                "change_pct": float(d[3]) if d[3] is not None else 0.0,
                "volume": float(d[4]) if d[4] is not None else 0.0,
                "exchange": str(d[5]) if len(d) > 5 and d[5] is not None else "",
                "type": str(d[6]) if len(d) > 6 and d[6] is not None else ""
            })
        return result

