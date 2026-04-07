import requests
import pandas as pd
from bs4 import BeautifulSoup
import json

def fetch_twse_inst(date="20260402"):
    url = f"https://www.twse.com.tw/rwd/zh/fund/BFI82U?date={date}&response=json"
    res = requests.get(url).json()
    return res

def fetch_tpex_inst(date="115/04/02"):
    url = f"https://www.tpex.org.tw/web/stock/3insti/3insti_summary/3itidy_result.php?l=zh-tw&d={date}"
    res = requests.get(url).json()
    return res

def fetch_taifex_futures(date="2026/04/02"):
    url = "https://www.taifex.com.tw/cht/3/futContractsDate"
    data = {
        "queryType": "1",
        "goDay": "",
        "doQuery": "1",
        "dateaddcnt": "",
        "queryDate": date,
        "commodityId": "TXF"
    }
    res = requests.post(url, data=data)
    try:
        dfs = pd.read_html(res.text)
        if len(dfs) >= 3:
            return dfs[3].to_json(orient="records", force_ascii=False)
        else:
            return "No data table found in HTML"
    except Exception as e:
        return str(e)

def fetch_twse_margin(date="20260402"):
    url = f"https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN?date={date}&response=json"
    res = requests.get(url).json()
    return res

def fetch_tpex_margin(date="115/04/02"):
    # TPEx margin
    url = f"https://www.tpex.org.tw/web/stock/margin_trading/margin_balance/margin_bal_result.php?l=zh-tw&d={date}"
    res = requests.get(url).json()
    return res

if __name__ == "__main__":
    print("--- TWSE Inst 4/2 ---")
    try:
        d = fetch_twse_inst("20260402")
        print(json.dumps(d.get("data", [])[-5:], ensure_ascii=False))
    except Exception as e:
        print(e)
        
    print("\n--- TPEx Inst 4/2 ---")
    try:
        d = fetch_tpex_inst("115/04/02")
        print(json.dumps(d.get("aaData", []), ensure_ascii=False))
    except Exception as e:
        print(e)

    print("\n--- TAIFEX Futures (TXF) 4/2 ---")
    try:
        print(fetch_taifex_futures("2026/04/02"))
    except Exception as e:
        print(e)

    print("\n--- TWSE Margin 4/2 ---")
    try:
        d = fetch_twse_margin("20260402")
        print("CreditList:", json.dumps(d.get("tables", [{}])[0].get("data", [])[:2], ensure_ascii=False))
    except Exception as e:
        print(e)

    print("\n--- TPEx Margin 4/2 ---")
    try:
        d = fetch_tpex_margin("115/04/02")
        print("TPEx Margin:", json.dumps(d.get("iTotalRecords", 0), ensure_ascii=False))
        if "aaData" in d and len(d["aaData"]) > 0:
            print("Summary row:", json.dumps(d["aaData"][-1], ensure_ascii=False))
    except Exception as e:
        print(e)
