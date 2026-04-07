import os
import json
from FinMind.data import DataLoader

def fetch_42_data():
    api = DataLoader()
    
    date = '2026-04-02'
    
    # 1. Institutional
    try:
        df_inst = api.taiwan_stock_total_institutional_investors(start_date=date, end_date=date)
        inst_data = df_inst.to_dict(orient="records") if not df_inst.empty else []
    except Exception as e:
        inst_data = str(e)
        
    # 2. Futures
    try:
        df_fut = api.taiwan_futures_institutional_investors(start_date=date, end_date=date)
        fut_data = df_fut.to_dict(orient="records") if not df_fut.empty else []
    except Exception as e:
        fut_data = str(e)
        
    # 3. Margin
    try:
        df_margin = api.taiwan_stock_total_margin_purchase_short_sale(start_date=date, end_date=date)
        margin_data = df_margin.to_dict(orient="records") if not df_margin.empty else []
    except Exception as e:
        margin_data = str(e)
        
    output = {
        "Institutional (三大法人)": inst_data,
        "Futures (期貨)": fut_data,
        "Margin (融資券)": margin_data
    }
    
    with open("finmind_42_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("Saved finmind_42_output.json")

if __name__ == "__main__":
    fetch_42_data()
