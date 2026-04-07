import requests
import json
import pandas as pd

def test_twse_sectors():
    try:
        # TWSE MI_INDEX
        url = "https://www.twse.com.tw/rwd/zh/fund/MI_INDEX?response=json&date=20260402&type=ALL"
        res = requests.get(url).json()
        print("MI_INDEX tables found:")
        for idx, table in enumerate(res.get("tables", [])):
            print(f"{idx}: {table.get('title')}")
            
    except Exception as e:
        print("Error TWSE:", e)

if __name__ == "__main__":
    test_twse_sectors()
