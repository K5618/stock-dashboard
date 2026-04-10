# src/providers/yfinance_client.py
import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Dict, Any, List, Optional
from src.providers.base import BaseDataProvider

class YFinanceProvider(BaseDataProvider):
    """
    DataProvider wrapper for yfinance library.
    """
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        retry_error_callback=lambda retry_state: None
    )
    def fetch_data(self, symbol: str, period: str = "5d") -> Optional[Dict[str, Any]]:
        """
        Fetches historical data for a single symbol to extract close, change, and volume.
        """
        import time
        time.sleep(0.5)  # Anti-DDoS safety margin for YFinance API
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty or len(hist) < 2:
                return None
                
            close = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-2])
            change = close - prev
            change_pct = (change / prev) * 100
            vol = float(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0.0
            date_str = hist.index[-1].strftime("%Y-%m-%d")
            
            return {
                "symbol": symbol,
                "date": date_str,
                "close_price": close,
                "change_pt": change,
                "change_pct": change_pct,
                "volume": vol
            }
        except Exception as e:
            print(f"YFinance fetch error for {symbol}: {e}")
            raise e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(Exception),
        retry_error_callback=lambda retry_state: None
    )
    def fetch_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetches basic info: sector, industry, market_cap.
        """
        try:
            info = yf.Ticker(symbol).info
            return {
                "symbol": symbol,
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap", 0)
            }
        except Exception as e:
            print(f"YFinance info fetch error for {symbol}: {e}")
            raise e
