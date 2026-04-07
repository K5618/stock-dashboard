import requests
import json

def test():
    try:
        url = "https://www.twse.com.tw/rwd/zh/fund/MI_INDEX?response=json&date=20260402&type=IND"
        res = requests.get(url).json()
        for idx, table in enumerate(res.get("tables", [])):
            if "指數" in table.get("title", ""):
                print(f"Table {idx}: {table['title']}")
                print(table["data"][:3]) # Show first 3 indices
    except Exception as e:
        print("Error:", e)
        
    try:
        url = "https://www.tpex.org.tw/web/stock/aftertrading/index_summary/summary_result.php?l=zh-tw&o=json&d=115/04/02"
        res = requests.get(url).json()
        print("TPEx Indices:")
        print(res.get("aaData", [])[:3])
    except Exception as e:
        print("Error TPEx:", e)

if __name__ == "__main__":
    test()
