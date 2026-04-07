import requests
import json
import traceback

def fetch_twse_margin():
    try:
        url = "https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN?date=20260402&response=json"
        res = requests.get(url).json()
        margin_tables = res.get("tables", [])
        
        # Table 0: 信用交易統計 (Credit transaction statistics)
        # 欄位: 項目, 買進, 賣出, 現金(券)償還, 前日餘額, 今日餘額, 限額
        # 融資(千元)
        credit_data = []
        for table in margin_tables:
            if "信用交易" in table.get("title", ""):
                credit_data = table.get("data", [])
                
        if not credit_data and margin_tables:
            credit_data = margin_tables[0].get("data", [])
            
        print("TWSE 融資(原始資料):")
        for row in credit_data:
            print("  ", row)
    except Exception as e:
        print("TWSE Margin Error:", e)

def fetch_tpex_inst():
    try:
        url = "https://www.tpex.org.tw/web/stock/3insti/3insti_summary/3itidy_result.php?l=zh-tw&o=json&d=115/04/02"
        res = requests.get(url).json()
        print("TPEx 三大法人(原始資料aaData):")
        for row in res.get("aaData", [])[:5]:
            print("  ", row)
    except Exception as e:
        print("TPEx Inst Error:", e)

def fetch_taifex():
    try:
        from FinMind.data import DataLoader
        api = DataLoader()
        df = api.taiwan_futures_institutional_investors(start_date="2026-04-02", end_date="2026-04-02")
        print("TAIFEX 期貨大台(TXF):")
        # Filter TXF
        txf = df[df["contract_id"] == "TXF"] if not df.empty and "contract_id" in df else df
        print(txf[["name", "long_short_net_volume", "open_interest_net_volume"]].to_string())
    except Exception as e:
        print("TAIFEX Error:", e)

if __name__ == "__main__":
    fetch_twse_margin()
    fetch_tpex_inst()
    fetch_taifex()
