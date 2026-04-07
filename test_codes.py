import requests
import json

def test():
    req_twse = requests.get("https://openapi.twse.com.tw/v1/opendata/t187ap03_L").json()
    codes = set(row.get("產業別") for row in req_twse)
    print("TWSE unique codes:", codes)
    
    # check specific stocks to their codes
    # 綠能環保 e.g., 雲豹能源 (6869) or 森崴能源 (6806)?
    for r in req_twse:
        if r.get("公司代號") in ["1802", "6869", "6806", "6901"]:
            print("TWSE sample stock:", r.get("公司名稱"), r.get("產業別"))
            
    # tpex OpenData check
    try:
        req_tpex = requests.get("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O").json()
        print("TPEx count:", len(req_tpex))
        if len(req_tpex) > 0:
            print("TPEx sample keys:", req_tpex[0].keys())
            print("TPEx codes:", set(r.get("產業別") for r in req_tpex))
    except Exception as e:
        print("TPEx Error:", e)

if __name__ == "__main__":
    test()
