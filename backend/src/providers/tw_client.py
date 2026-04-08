# src/providers/tw_client.py
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Dict, Any, List
from src.providers.base import BaseDataProvider

class TwseProvider(BaseDataProvider):
    """
    Fetches data from TWSE Open API and standard endpoints.
    """
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def fetch_data(self, endpoint: str, **kwargs) -> Any:
        url = ""
        if endpoint == "opendata_sectors":
            url = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
        elif endpoint == "sector_summary":
            # kwargs require date string like "20240101"
            date_str = kwargs.get("date_str")
            url = f"https://www.twse.com.tw/rwd/zh/fund/BFIAMU?date={date_str}&response=json"
        elif endpoint == "index_summary":
            date_str = kwargs.get("date_str")
            url = f"https://www.twse.com.tw/rwd/zh/fund/MI_INDEX?response=json&date={date_str}&type=IND"
        elif endpoint == "institutional":
            date_str = kwargs.get("date_str")
            url = f"https://www.twse.com.tw/rwd/zh/fund/BFI82U?date={date_str}&response=json"
        elif endpoint == "margin":
            date_str = kwargs.get("date_str")
            url = f"https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN?date={date_str}&response=json"
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")

        res = requests.get(url, timeout=15)
        res.raise_for_status()
        return res.json()


class TpexProvider(BaseDataProvider):
    """
    Fetches data from TPEx Open API.
    """
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def fetch_data(self, endpoint: str, **kwargs) -> Any:
        url = ""
        date_tw = kwargs.get("date_tw") # e.g. "113/01/01"
        
        if endpoint == "opendata_sectors":
            url = "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O"
        elif endpoint == "sector_summary":
            url = f"https://www.tpex.org.tw/web/stock/aftertrading/index_summary/summary_result.php?l=zh-tw&o=json&d={date_tw}"
        elif endpoint == "institutional":
            url = f"https://www.tpex.org.tw/web/stock/3insti/3insti_summary/3itidy_result.php?l=zh-tw&o=json&d={date_tw}"
        elif endpoint == "margin":
            url = f"https://www.tpex.org.tw/web/stock/margin_trading/margin_balance/margin_bal_result.php?l=zh-tw&o=json&d={date_tw}"
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")

        res = requests.get(url, timeout=15)
        res.raise_for_status()
        return res.json()
