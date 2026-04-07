import requests

def test_amounts():
    twse_date = "20240402" # hardcoded past date for consistency
    print("----- TWSE BFIAMU -----")
    res1 = requests.get(f"https://www.twse.com.tw/rwd/zh/fund/BFIAMU?date={twse_date}&response=json").json()
    total_ratio = 0
    total_val = 0
    if "data" in res1:
        for r in res1["data"]:
            name = r[1]
            vol_shares = int(str(r[2]).replace(",", ""))
            ratio = float(r[3])
            val_ntd = int(str(r[4]).replace(",", ""))
            total_ratio += ratio
            total_val += val_ntd
            if "半導體" in name or "水泥" in name:
                print(f"{name}: 股數={vol_shares}, 金額={val_ntd}, 比重={ratio}%")
        print(f"TWSE總金額: {total_val} 元, TWSE比重加總: {total_ratio}%")
    
    print("\n----- TPEx index_summary check -----")
    t_date = "113/04/02"
    res2 = requests.get(f"https://www.tpex.org.tw/web/stock/aftertrading/index_summary/summary_result.php?l=zh-tw&o=json&d={t_date}").json()
    total_val2 = 0
    if "aaData" in res2:
        for r in res2["aaData"]:
            name = r[0]
            val_ntd = int(str(r[4]).replace(",", "")) # the field for 成交金額
            total_val2 += val_ntd
            if "半導體" in name or "食品" in name:
                print(f"{name}: 金額={val_ntd} (單位是什麼？)")
        print(f"TPEx 類股總金額加總: {total_val2}")

test_amounts()
