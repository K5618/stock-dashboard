import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import requests
from concurrent.futures import ThreadPoolExecutor
import json
import os
import math

# Major TW Indices
TW_INDICES = {
    "^TWII": "加權指數",
    "0050.TW": "台灣50",
    "0051.TW": "中型100",
    "^TWOII": "櫃買指數",
    "020020.TWO": "富櫃200" # TPEx 200 TR Index or ETF
}

# Sectors (using representative ETFs or Indices)
TW_SECTORS = {
    "0052.TW": "科技",
    "0056.TW": "高股息",
    "0055.TW": "金融",
    "00728.TW": "工業",
    "00881.TW": "5G通訊",
    "00891.TW": "半導體",
    "00709.TW": "生技醫療",
    "00742.TW": "材料"
}

def get_tv_screener_taiwan(limit=3000):
    try:
        url = "https://scanner.tradingview.com/taiwan/scan"
        query = {
            "columns": ["name", "description", "sector", "industry", "close", "change", "volume", "market_cap_basic", "price_earnings_ttm", "High.1M", "High.3M", "High.6M", "High.All", "Low.1M", "Low.3M", "Low.6M", "Low.All", "exchange"],
            "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
            "range": [0, limit]
        }
        res = requests.post(url, json=query).json()
        stocks = []
        for x in res.get('data', []):
            d = x['d']
            stocks.append({
                "symbol": d[0], "name": d[1], "sector": d[2], "industry": d[3], 
                "close_price": d[4], "change_pct": d[5], "volume": d[6], 
                "market_cap": d[7], "pe_ratio": d[8],
                "h_30": d[9], "h_90": d[10], "h_180": d[11], "h_all": d[12],
                "l_30": d[13], "l_90": d[14], "l_180": d[15], "l_all": d[16],
                "exchange": d[17]
            })
        return stocks
    except Exception as e:
        print("Error getting screener data:", e)
        return []

def update_tw_data():
    now_tz = datetime.now(timezone(timedelta(hours=8)))
    now_str = now_tz.strftime("%Y-%m-%d %H:%M:%S (UTC+8)")
    date_str = now_tz.strftime("%Y-%m-%d")
    print(f"Starting TW data generation at {now_str}")
    
    result_data = {
        "status": { "last_updated": now_str },
        "indices": {"data": []},
        "chips": {"institutional": [], "futures": [], "margin": []},
        "sectors": {"data": []},
        "sectors_data": { "TWSE": [], "TPEx": [] },
        "top_stocks": {"data": {}},
        "screener": {
            "TWSE": {
                "block1": {"gain_3": [], "gain_5": [], "gain_10": []},
                "block2": {"h_30": [], "h_90": [], "h_180": [], "h_all": []},
                "block3": {"loss_3": [], "loss_5": [], "loss_10": []},
                "block4": {"l_30": [], "l_90": [], "l_180": [], "l_all": []}
            },
            "TPEX": {
                "block1": {"gain_3": [], "gain_5": [], "gain_10": []},
                "block2": {"h_30": [], "h_90": [], "h_180": [], "h_all": []},
                "block3": {"loss_3": [], "loss_5": [], "loss_10": []},
                "block4": {"l_30": [], "l_90": [], "l_180": [], "l_all": []}
            },
            "Emerging": {
                "block1": {"gain_3": [], "gain_5": [], "gain_10": []},
                "block2": {"h_30": [], "h_90": [], "h_180": [], "h_all": []},
                "block3": {"loss_3": [], "loss_5": [], "loss_10": []},
                "block4": {"l_30": [], "l_90": [], "l_180": [], "l_all": []}
            }
        }
    }
    
    # 1. Fetch Indices
    for symbol, name in TW_INDICES.items():
        try:
            hist = yf.Ticker(symbol).history(period="5d")
            if len(hist) >= 2:
                close = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                change = close - prev
                change_pct = (change / prev) * 100
                vol = float(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0
                result_data["indices"]["data"].append({
                    "symbol": symbol, "name": name, "date": date_str, "close_price": close, "change_pt": change, "change_pct": change_pct, "volume": vol
                })
        except:
            pass

    # 2. Fetch Sector ETFs
    for symbol, name in TW_SECTORS.items():
        try:
            hist = yf.Ticker(symbol).history(period="5d")
            if len(hist) >= 2:
                close = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                change = close - prev
                change_pct = (change / prev) * 100
                result_data["sectors"]["data"].append({
                    "symbol": symbol, "name": name, "date": date_str, "close_price": close, "change_pt": change, "change_pct": change_pct
                })
        except:
            pass

    # 3. TV Screener for Taiwan Blocks
    tv_stocks = get_tv_screener_taiwan(3000)
    for s in tv_stocks:
        cg = s.get('change_pct', 0)
        c = s.get('close_price', 0)
        market = s.get('exchange', 'TWSE') # 'TWSE' or 'TPEX'
        
        # Determine Market Bucket
        # If symbol length > 4 typically emerging or odd, but TradingView might mix. 
        # Fallback to TAIEX and TPEx. If 'Emerging' logic isn't clean from TV, we map it into 'Emerging' bucket.
        bucket = market
        
        screen_obj = {
            "symbol": s['symbol'], "name": s['name'], "sector": s['sector'], "industry": s['industry'],
            "close_price": c, "change_pct": cg, "volume": s['volume'], "market_cap": s['market_cap'], "pe_ratio": s['pe_ratio'], "date": date_str
        }
        
        if bucket in result_data["screener"]:
            if cg != None:
                if cg >= 9.5: result_data["screener"][bucket]["block1"]["gain_10"].append(screen_obj) # Limit UP ~10%
                elif cg >= 5: result_data["screener"][bucket]["block1"]["gain_5"].append(screen_obj)
                elif cg >= 3: result_data["screener"][bucket]["block1"]["gain_3"].append(screen_obj)
                
                if cg <= -9.5: result_data["screener"][bucket]["block3"]["loss_10"].append(screen_obj) # Limit Down ~10%
                elif cg <= -5: result_data["screener"][bucket]["block3"]["loss_5"].append(screen_obj)
                elif cg <= -3: result_data["screener"][bucket]["block3"]["loss_3"].append(screen_obj)
            
            if c != None:
                def near(val, target): return val != None and target != None and target > 0 and abs(val - target) / target < 0.005
                if near(c, s.get('h_30')): result_data["screener"][bucket]["block2"]["h_30"].append(screen_obj)
                if near(c, s.get('h_90')): result_data["screener"][bucket]["block2"]["h_90"].append(screen_obj)
                if near(c, s.get('h_180')): result_data["screener"][bucket]["block2"]["h_180"].append(screen_obj)
                if near(c, s.get('h_all')): result_data["screener"][bucket]["block2"]["h_all"].append(screen_obj)
                
                if near(c, s.get('l_30')): result_data["screener"][bucket]["block4"]["l_30"].append(screen_obj)
                if near(c, s.get('l_90')): result_data["screener"][bucket]["block4"]["l_90"].append(screen_obj)
                if near(c, s.get('l_180')): result_data["screener"][bucket]["block4"]["l_180"].append(screen_obj)
                if near(c, s.get('l_all')): result_data["screener"][bucket]["block4"]["l_all"].append(screen_obj)

    # 4. TWSE and TPEx Sectors API + Top 15 constituents per logic
    twse_req_sectors = ["水泥工業", "食品工業", "塑膠工業", "紡織纖維", "電機機械", "電器電纜", "玻璃陶瓷", "造紙工業", "鋼鐵工業", "橡膠工業", "汽車工業", "電子工業", "建材營造", "航運業", "觀光餐旅", "金融保險", "貿易百貨", "化學工業", "生技醫療業", "油電燃氣業", "綠能環保", "數位雲端", "運動休閒", "居家生活", "其他", "半導體業", "電腦及週邊設備業", "光電業", "通信網路業", "電子零組件業", "電子通路業", "資訊服務業", "其他電子業"]
    tpex_req_sectors = ["食品工業", "塑膠工業", "紡織纖維", "電機機械", "電器電纜", "玻璃陶瓷", "鋼鐵工業", "橡膠工業", "汽車工業", "建材營造", "航運業", "觀光餐旅", "金融業", "貿易百貨", "其他", "化學工業", "生技醫療業", "油電燃氣業", "半導體業", "電腦及週邊設備業", "光電業", "通信網路業", "電子零組件業", "電子通路業", "資訊服務業", "其他電子業", "文化創意業", "農業科技業", "電子商務", "綠能環保", "數位雲端", "運動休閒", "居家生活"]
    twse_code_map = {"01": "水泥工業", "02": "食品工業", "03": "塑膠工業", "04": "紡織纖維", "05": "電機機械", "06": "電器電纜", "07": "玻璃陶瓷", "08": "造紙工業", "09": "鋼鐵工業", "10": "橡膠工業", "11": "汽車工業", "12": "電子工業", "14": "建材營造", "15": "航運業", "16": "觀光餐旅", "17": "金融保險", "18": "貿易百貨", "20": "其他", "21": "化學工業", "22": "生技醫療業", "23": "油電燃氣業", "24": "半導體業", "25": "電腦及週邊設備業", "26": "光電業", "27": "通信網路業", "28": "電子零組件業", "29": "電子通路業", "30": "資訊服務業", "31": "其他電子業", "35": "綠能環保", "36": "數位雲端", "37": "運動休閒", "38": "居家生活"}
    tpex_code_map = {"02": "食品工業", "03": "塑膠工業", "04": "紡織纖維", "05": "電機機械", "06": "電器電纜", "08": "玻璃陶瓷", "09": "鋼鐵工業", "10": "橡膠工業", "11": "汽車工業", "14": "建材營造", "15": "航運業", "16": "觀光餐旅", "17": "金融業", "18": "貿易百貨", "20": "其他", "21": "化學工業", "22": "生技醫療業", "23": "油電燃氣業", "24": "半導體業", "25": "電腦及週邊設備業", "26": "光電業", "27": "通信網路業", "28": "電子零組件業", "29": "電子通路業", "30": "資訊服務業", "31": "其他電子業", "32": "文化創意業", "33": "農業科技業", "34": "電子商務", "35": "綠能環保", "36": "數位雲端", "37": "運動休閒", "38": "居家生活"}
    
    stock_sector_map = {}
    try:
        req_twse = requests.get("https://openapi.twse.com.tw/v1/opendata/t187ap03_L").json()
        for row in req_twse:
            sec_name = twse_code_map.get(str(row.get("產業別")), str(row.get("產業別")))
            stock_sector_map[str(row.get("公司代號"))] = {"market": "TWSE", "sector": sec_name, "chinese_name": row.get("公司簡稱", row.get("公司名稱"))}
    except Exception as e: print("TWSE OpenData Err:", e)
    try:
        req_tpex = requests.get("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O").json()
        for row in req_tpex:
            ic = row.get("SecuritiesIndustryCode")
            cc = row.get("SecuritiesCompanyCode")
            name = row.get("CompanyAbbreviation", row.get("CompanyName"))
            if ic and cc:
                sec_name = tpex_code_map.get(str(ic), str(ic))
                stock_sector_map[str(cc)] = {"market": "TPEx", "sector": sec_name, "chinese_name": name}
    except Exception as e: print("TPEx OpenData Err:", e)

    twse_stocks_by_sec = {s: [] for s in twse_req_sectors}
    tpex_stocks_by_sec = {s: [] for s in tpex_req_sectors}
    twse_total_vol = 0
    tpex_total_vol = 0

    for s in tv_stocks:
        sym = s.get('symbol', '').replace('.TW', '').replace('.TWO', '')
        info = stock_sector_map.get(sym)
        vol = s.get('volume', 0) or 0
        if info:
            sec = info["sector"]
            market = info["market"]
            if market == "TWSE" and sec in twse_stocks_by_sec:
                twse_stocks_by_sec[sec].append(s)
                twse_total_vol += vol
            elif market == "TPEx" and sec in tpex_stocks_by_sec:
                tpex_stocks_by_sec[sec].append(s)
                tpex_total_vol += vol

    def parse_tw_int(val):
        if val is None: return 0
        if isinstance(val, (int, float)): return int(val)
        return int(str(val).replace(',', '').strip() or 0)
        
    def parse_tw_float(val):
        if val is None: return 0.0
        if isinstance(val, (int, float)): return float(val)
        return float(str(val).replace('%','').replace(',','').replace('+','').strip() or 0.0)

    twse_official_sectors = {}
    twse_official_total_val = 0
    try:
        twse_date = date_str.replace('-','')
        api_bfi = requests.get(f"https://www.twse.com.tw/rwd/zh/fund/BFIAMU?date={twse_date}&response=json").json()
        for row in api_bfi.get("data", []):
            name = str(row[1]).replace("類", "").replace("工業", "")
            val_num = parse_tw_int(row[4])
            twse_official_sectors[name] = {"vol": parse_tw_int(row[2]), "val": val_num, "pct": parse_tw_float(row[3]) / 100.0, "change": 0.0}
            twse_official_total_val += val_num
        api_ind = requests.get(f"https://www.twse.com.tw/rwd/zh/fund/MI_INDEX?response=json&date={twse_date}&type=IND").json()
        if api_ind.get("tables"):
            for row in api_ind["tables"][0].get("data", []):
                name = str(row[0]).replace("指數", "")
                change_sign = 1 if "+" in str(row[2]) else (-1 if "-" in str(row[2]) else 0)
                for k in twse_official_sectors.keys():
                    if k in name or name in k: twse_official_sectors[k]["change"] = parse_tw_float(row[4]) * change_sign; break
    except Exception as e: print("TWSE Sector API Err:", e)
    
    tpex_official_sectors = {}
    tpex_official_total_val = 0
    try:
        t_date = f"{int(date_str[:4])-1911}/{date_str[5:7]}/{date_str[8:10]}"
        api_tpe = requests.get(f"https://www.tpex.org.tw/web/stock/aftertrading/index_summary/summary_result.php?l=zh-tw&o=json&d={t_date}").json()
        for row in api_tpe.get("aaData", []):
            name = str(row[0]).replace("類", "")
            val_num = parse_tw_int(row[4])
            tpex_official_sectors[name] = {"val": val_num, "change": parse_tw_float(row[3]), "vol": 0, "pct": 0.0}
            tpex_official_total_val += val_num
    except Exception as e: print("TPEx Sector API Err:", e)

    twse_total_val_tw_stocks = sum([(x.get('close_price',0) or 0)*(x.get('volume',0) or 0) for x in tv_stocks if stock_sector_map.get(x.get('symbol', '').replace('.TW', '').replace('.TWO', ''), {}).get('market') == 'TWSE'])
    tpex_total_val_tw_stocks = sum([(x.get('close_price',0) or 0)*(x.get('volume',0) or 0) for x in tv_stocks if stock_sector_map.get(x.get('symbol', '').replace('.TW', '').replace('.TWO', ''), {}).get('market') == 'TPEx'])

    for sec_name in twse_req_sectors:
        lst = twse_stocks_by_sec[sec_name]
        top_15 = sorted(lst, key=lambda x: x.get('market_cap') or 0, reverse=True)[:15]
        top_15_clean = [{"symbol": x['symbol'], "name": stock_sector_map.get(x['symbol'].replace('.TW', '').replace('.TWO', ''), {}).get('chinese_name', x['name']), "date": date_str, "close_price": x['close_price'], "change_pct": x['change_pct'], "volume": (x['volume'] / 1000) if x.get('volume') else 0, "market_cap": (x['market_cap'] / 100000000.0) if x.get('market_cap') else 0} for x in top_15]
        
        matched, s_short = None, sec_name.replace("工業", "").replace("業", "")
        for ko, vo in twse_official_sectors.items():
            if s_short in ko or ko in s_short: matched = vo; break
                
        # we assign Value (in 億) to the `volume` field for left side display
        if matched:
            sval_亿 = matched["val"] / 100000000.0
            sratio = matched["pct"]
            schg = matched["change"] or sum([((x.get('market_cap',0) or 0) / sum([(l.get('market_cap',0) or 0) for l in lst])) * (x.get('change_pct',0) or 0) for x in lst]) if sum([(l.get('market_cap',0) or 0) for l in lst]) else 0
        else:
            sval = sum([(x.get('close_price',0) or 0)*(x.get('volume',0) or 0) for x in lst])
            sval_亿 = sval / 100000000.0 if sval else 0
            sratio = (sval / twse_total_val_tw_stocks) if twse_total_val_tw_stocks else 0
            sv_cap = sum([(x.get('market_cap',0) or 0) for x in lst])
            schg = sum([((x.get('market_cap',0) or 0) / sv_cap) * (x.get('change_pct',0) or 0) for x in lst]) if sv_cap else 0
            
        result_data["sectors_data"]["TWSE"].append({"id": sec_name, "name": sec_name, "volume": sval_亿, "vol_ratio": sratio, "change_pct": schg, "top_15": top_15_clean})

    for sec_name in tpex_req_sectors:
        lst = tpex_stocks_by_sec[sec_name]
        top_15 = sorted(lst, key=lambda x: x.get('market_cap') or 0, reverse=True)[:15]
        top_15_clean = [{"symbol": x['symbol'], "name": stock_sector_map.get(x['symbol'].replace('.TW', '').replace('.TWO', ''), {}).get('chinese_name', x['name']), "date": date_str, "close_price": x['close_price'], "change_pct": x['change_pct'], "volume": (x['volume'] / 1000) if x.get('volume') else 0, "market_cap": (x['market_cap'] / 100000000.0) if x.get('market_cap') else 0} for x in top_15]
        
        matched, s_short = None, sec_name.replace("工業", "").replace("業", "")
        for ko, vo in tpex_official_sectors.items():
            if s_short in ko or ko in s_short: matched = vo; break
                
        if matched:
            sval_亿 = matched["val"] / 100000.0 # TPEx val is in 千元
            sratio = (matched["val"] / tpex_official_total_val) if tpex_official_total_val else 0
            schg = matched["change"] 
        else:
            sval = sum([(x.get('close_price',0) or 0)*(x.get('volume',0) or 0) for x in lst])
            sval_亿 = sval / 100000000.0 if sval else 0
            sratio = (sval / tpex_total_val_tw_stocks) if tpex_total_val_tw_stocks else 0
            sv_cap = sum([(x.get('market_cap',0) or 0) for x in lst])
            schg = sum([((x.get('market_cap',0) or 0) / sv_cap) * (x.get('change_pct',0) or 0) for x in lst]) if sv_cap else 0
            
        result_data["sectors_data"]["TPEx"].append({"id": sec_name, "name": sec_name, "volume": sval_亿, "vol_ratio": sratio, "change_pct": schg, "top_15": top_15_clean})

    # 1. Institutional
    twse_inst = {"投信": 0, "外資及陸資": 0, "自營商(自行)": 0, "自營商(避險)": 0, "三大法人合計": 0}
    try:
        twse_date = date_str.replace('-','')
        res = requests.get(f"https://www.twse.com.tw/rwd/zh/fund/BFI82U?date={twse_date}&response=json").json()
        for r in res.get("data", []):
            name, net = r[0], parse_tw_int(r[3])
            if "投信" in name: twse_inst["投信"] += net
            elif "自營商(自行" in name: twse_inst["自營商(自行)"] += net
            elif "自營商(避險" in name: twse_inst["自營商(避險)"] += net
            elif "外資及陸資" in name: twse_inst["外資及陸資"] += net
            elif "合計" in name: twse_inst["三大法人合計"] += net
    except Exception as e: print("TWSE Inst Err:", e)

    tpex_inst = {"投信": 0, "外資及陸資": 0, "自營商(自行)": 0, "自營商(避險)": 0, "三大法人合計": 0}
    try:
        t_date = f"{int(date_str[:4])-1911}/{date_str[5:7]}/{date_str[8:10]}"
        res = requests.get(f"https://www.tpex.org.tw/web/stock/3insti/3insti_summary/3itidy_result.php?l=zh-tw&o=json&d={t_date}").json()
        for r in res.get("aaData", []):
            name, net = r[0], parse_tw_int(r[3])
            if "投信" in name: tpex_inst["投信"] += net
            elif "自營商(自行" in name: tpex_inst["自營商(自行)"] += net
            elif "自營商(避險" in name: tpex_inst["自營商(避險)"] += net
            elif "外資及陸資" in name: tpex_inst["外資及陸資"] += net
            elif "合計" in name: tpex_inst["三大法人合計"] += net
    except Exception as e: print("TPEx Inst Err:", e)

    result_data["chips"]["institutional"] = [
        {"entity": k, "twse_net": twse_inst[k], "tpex_net": tpex_inst[k]} for k in twse_inst.keys()
    ]

    # 2. Futures
    result_data["chips"]["futures"] = []
    try:
        from FinMind.data import DataLoader
        api = DataLoader()
        df = api.taiwan_futures_institutional_investors(start_date=date_str, end_date=date_str)
        if not df.empty and "contract_id" in df:
            for _, row in df[df["contract_id"] == "TXF"].iterrows():
                result_data["chips"]["futures"].append({"entity": row.get("name",""), "net_contracts": parse_tw_int(row.get("long_short_net_volume",0)), "oi_contracts": parse_tw_int(row.get("open_interest_net_volume",0))})
    except Exception as e: print("TAIFEX Err:", e)

    # 3. Margin
    twse_margin = {"margin_change": 0, "margin_bal": 0, "short_change": 0, "short_bal": 0, "lend_change": 0, "lend_bal": 0}
    try:
        res = requests.get(f"https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN?date={date_str.replace('-','')}&response=json").json()
        margin_tables = res.get("tables", [])
        credit_data = []
        for tbl in margin_tables:
            if "信用交易" in tbl.get("title", ""): credit_data = tbl.get("data", [])
            elif not credit_data: credit_data = margin_tables[0].get("data", [])
            
        for row in credit_data:
            if "融資金" in str(row[0]):
                twse_margin["margin_bal"] = parse_tw_int(row[5])
                twse_margin["margin_change"] = twse_margin["margin_bal"] - parse_tw_int(row[4])
            if "融券(" in str(row[0]):
                twse_margin["short_bal"] = parse_tw_int(row[5])
                twse_margin["short_change"] = twse_margin["short_bal"] - parse_tw_int(row[4])
    except Exception as e: print("TWSE Margin Err:", e)

    tpex_margin = {"margin_change": 0, "margin_bal": 0, "short_change": 0, "short_bal": 0, "lend_change": 0, "lend_bal": 0}
    try:
        res = requests.get(f"https://www.tpex.org.tw/web/stock/margin_trading/margin_balance/margin_bal_result.php?l=zh-tw&o=json&d={t_date}").json()
        if "aaData" in res and res["aaData"]:
            last = res["aaData"][-1]
            if "合計" in str(last[0]):
                tpex_margin["margin_bal"] = parse_tw_int(last[5]) # roughly picking indexes standard for tpex
                tpex_margin["margin_change"] = parse_tw_int(last[5]) - parse_tw_int(last[4])
    except Exception as e: print("TPEx Margin Err:", e)

    result_data["chips"]["margin"] = [
        {"market": "加權指數", **twse_margin},
        {"market": "櫃買指數", **tpex_margin}
    ]

    def clean_nan(obj):
        if isinstance(obj, dict): return {k: clean_nan(v) for k, v in obj.items()}
        elif isinstance(obj, list): return [clean_nan(v) for v in obj]
        elif isinstance(obj, float) and math.isnan(obj): return None
        return obj
    
    clean_data = clean_nan(result_data)
    
    try:
        from supabase import create_client, Client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if url and key:
            supabase: Client = create_client(url, key)
            
            # Upsert into a separate TW table if exists, else tw_data.json
            try:
                # Keep small size
                res = supabase.table("tw_market_snapshots").select("id").order("created_at", desc=True).execute()
                if res.data and len(res.data) > 2:
                    ids_to_del = [x['id'] for x in res.data[2:]]
                    for idx in ids_to_del:
                        supabase.table("tw_market_snapshots").delete().eq("id", idx).execute()
                
                supabase.table("tw_market_snapshots").insert({"data": clean_data}).execute()
                print("Uploaded to tw_market_snapshots.")
            except Exception as e:
                print(f"Subapase TW table error (falling back to json): {e}")
                raise e
        else:
            raise Exception("No Supabase vars")
    except Exception as e:
        print("Saving locally to public/tw_data.json")
        out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public'))
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        out_file = os.path.join(out_dir, 'tw_data.json')
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    update_tw_data()
