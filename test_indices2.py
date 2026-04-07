import requests
import json

def test():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        url = "https://www.twse.com.tw/rwd/zh/fund/BFIAMU?date=20260402&response=json"
        res = requests.get(url, headers=headers).json()
        print("BFIAMU tables:", [t.get('title') for t in res.get('tables', [])])
        if res.get("data"):
            print("BFIAMU Data Example:", res["data"][0])
    except Exception as e:
        print("BFIAMU Error:", e)

    try:
        url = "https://www.twse.com.tw/rwd/zh/fund/MI_INDEX?response=json&date=20260402&type=IND"
        res = requests.get(url, headers=headers).json()
        print("MI_INDEX tables:", [t.get('title') for t in res.get('tables', [])])
        if res.get('tables'):
            print("MI_INDEX Data Example:", res['tables'][0]['data'][:2])
    except Exception as e:
        print("MI_INDEX Error:", e)
        
    try:
        # TPEx indices
        url = "https://www.tpex.org.tw/web/stock/aftertrading/index_summary/summary_result.php?l=zh-tw&o=json&d=115/04/02"
        res = requests.get(url, headers=headers).json()
        print("TPEx Indices Data Example:")
        print(res.get("aaData", [])[:2])
    except Exception as e:
        print("TPEx Error:", e)

if __name__ == "__main__":
    test()
