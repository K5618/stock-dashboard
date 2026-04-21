# src/services/tw_aggregator.py
from datetime import datetime, timezone, timedelta
from src.config.constants import TW_INDICES, TW_SECTORS, TWSE_REQ_SECTORS, TPEX_REQ_SECTORS, TWSE_CODE_MAP, TPEX_CODE_MAP
from src.providers.tv_scraper import TradingViewScanner
from src.providers.tw_client import TwseProvider, TpexProvider, TaifexProvider
from src.utils.parsers import parse_tw_int, parse_tw_float, clean_nan

class TaiwanDataAggregator:
    def __init__(self):
        self.tv_scanner = TradingViewScanner(market="taiwan")
        self.twse_provider = TwseProvider()
        self.tpex_provider = TpexProvider()
        self.taifex_provider = TaifexProvider()

    def gather_data(self) -> dict:
        now_tz = datetime.now(timezone(timedelta(hours=8)))
        now_str = now_tz.strftime("%Y-%m-%d %H:%M:%S (UTC+8)")
        date_str = now_tz.strftime("%Y-%m-%d")
        
        twse_date = date_str.replace('-', '')
        tpex_date = f"{int(date_str[:4])-1911}/{date_str[5:7]}/{date_str[8:10]}"

        print(f"Starting TW Data generation at {now_str}")

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

        # 1. Fetch Indices from Official Open APIs
        try:
            twse_idx_data = self.twse_provider.fetch_data("latest_index")
            if twse_idx_data and isinstance(twse_idx_data, list) and len(twse_idx_data) > 0:
                dt = twse_idx_data[0].get("日期", "")
                if dt and len(dt) >= 7:
                    y, m, d = int(dt[:-4]) + 1911, dt[-4:-2], dt[-2:]
                    twse_date = f"{y}{m}{d}"
                    tpex_date = f"{dt[:-4]}/{m}/{d}"
                    date_str = f"{y}-{m}-{d}"
            
            for row in twse_idx_data:
                name = row.get("指數", "")
                if name in TW_INDICES.get("TWSE", {}):
                    sign = 1 if row.get("漲跌", "") == "+" else (-1 if row.get("漲跌", "") == "-" else 0)
                    result_data["indices"]["data"].append({
                        "symbol": f"TWSE_{name}",
                        "name": TW_INDICES["TWSE"][name],
                        "close_price": parse_tw_float(row.get("收盤指數", 0)),
                        "change_pt": sign * abs(parse_tw_float(row.get("漲跌點數", 0))),
                        "change_pct": sign * abs(parse_tw_float(row.get("漲跌百分比", 0))),
                        "volume": 0,
                        "date": date_str
                    })
        except Exception as e:
            print(f"Error fetching TWSE Indices: {e}")

        try:
            tpex_idx_data = self.tpex_provider.fetch_data("latest_index")
            if isinstance(tpex_idx_data, dict) and "tables" in tpex_idx_data and len(tpex_idx_data["tables"]) > 0:
                tbl = tpex_idx_data["tables"][0]
                if "收市指數" in tbl.get("fields", []):
                        for row in tbl.get("data", []):
                            name = str(row[0])
                            if name in TW_INDICES.get("TPEX", {}):
                                result_data["indices"]["data"].append({
                                    "symbol": f"TPEX_{name}",
                                    "name": TW_INDICES["TPEX"][name],
                                    "close_price": parse_tw_float(row[1]),
                                    "change_pt": parse_tw_float(row[2]),
                                    "change_pct": parse_tw_float(row[3]),
                                    "date": date_str
                                })
        except Exception as e:
            print(f"Error fetching TPEX Indices: {e}")

        # Fetch Sector ETFs from TradingView
        try:
            sector_symbols = list(TW_SECTORS.keys())
            batch_etfs = self.tv_scanner.fetch_specific_symbols(sector_symbols)
            for item in batch_etfs:
                sym = item.get("symbol")
                if sym in TW_SECTORS:
                    item["name"] = TW_SECTORS[sym]
                    item["date"] = date_str
                    close_p = item.get("close_price")
                    pct = item.get("change_pct")
                    if close_p and pct is not None:
                        try:
                            item['change_pt'] = close_p - (close_p / (1 + pct / 100))
                        except Exception:
                            item['change_pt'] = 0
                    else:
                        item['change_pt'] = 0
                    result_data["sectors"]["data"].append(item)
        except Exception as e:
            print(f"Error fetching Sector ETFs from TV: {e}")

        # 2. TV Screener filtering 
        try:
            tv_stocks = self.tv_scanner.fetch_data(3000)
        except Exception:
            tv_stocks = []

        for s in tv_stocks:
            s['date'] = date_str
            cg = s.get('change_pct')
            c = s.get('close_price')
            bucket = s.get('exchange', 'TWSE')
            
            if bucket in result_data["screener"]:
                if cg is not None:
                    if cg >= 9.5: result_data["screener"][bucket]["block1"]["gain_10"].append(s)
                    elif cg >= 5: result_data["screener"][bucket]["block1"]["gain_5"].append(s)
                    elif cg >= 3: result_data["screener"][bucket]["block1"]["gain_3"].append(s)
                    
                    if cg <= -9.5: result_data["screener"][bucket]["block3"]["loss_10"].append(s)
                    elif cg <= -5: result_data["screener"][bucket]["block3"]["loss_5"].append(s)
                    elif cg <= -3: result_data["screener"][bucket]["block3"]["loss_3"].append(s)
                
                if c is not None and c > 0:
                    def near(val, target): return val is not None and target is not None and target > 0 and abs(val - target) / target < 0.005
                    if near(c, s.get('h_30')): result_data["screener"][bucket]["block2"]["h_30"].append(s)
                    if near(c, s.get('h_90')): result_data["screener"][bucket]["block2"]["h_90"].append(s)
                    if near(c, s.get('h_180')): result_data["screener"][bucket]["block2"]["h_180"].append(s)
                    if near(c, s.get('h_all')): result_data["screener"][bucket]["block2"]["h_all"].append(s)
                    
                    if near(c, s.get('l_30')): result_data["screener"][bucket]["block4"]["l_30"].append(s)
                    if near(c, s.get('l_90')): result_data["screener"][bucket]["block4"]["l_90"].append(s)
                    if near(c, s.get('l_180')): result_data["screener"][bucket]["block4"]["l_180"].append(s)
                    if near(c, s.get('l_all')): result_data["screener"][bucket]["block4"]["l_all"].append(s)

        # 3. Market Sector details & Open API fetching
        stock_sector_map = {}
        try:
            req_twse = self.twse_provider.fetch_data("opendata_sectors")
            for row in req_twse:
                stock_sector_map[str(row.get("公司代號"))] = {"market": "TWSE", "sector": TWSE_CODE_MAP.get(str(row.get("產業別")), str(row.get("產業別"))), "chinese_name": row.get("公司簡稱", row.get("公司名稱"))}
        except Exception: pass
        
        try:
            req_tpex = self.tpex_provider.fetch_data("opendata_sectors")
            for row in req_tpex:
                ic = row.get("SecuritiesIndustryCode")
                cc = row.get("SecuritiesCompanyCode")
                if ic and cc:
                    stock_sector_map[str(cc)] = {"market": "TPEx", "sector": TPEX_CODE_MAP.get(str(ic), str(ic)), "chinese_name": row.get("CompanyAbbreviation", row.get("CompanyName"))}
        except Exception: pass

        twse_stocks_by_sec = {s: [] for s in TWSE_REQ_SECTORS}
        tpex_stocks_by_sec = {s: [] for s in TPEX_REQ_SECTORS}

        for s in tv_stocks:
            sym_raw = s.get('symbol', '')
            sym = sym_raw.split('.')[0] if '.' in sym_raw else sym_raw
            info = stock_sector_map.get(sym)
            if info:
                s['name'] = info.get("chinese_name", s.get('name'))
                s['sector'] = info.get("sector", s.get('sector'))
                s['industry'] = info.get("market", "")
                sec, market = info["sector"], info["market"]
                if market == "TWSE" and sec in twse_stocks_by_sec:
                    twse_stocks_by_sec[sec].append(s)
                elif market == "TPEx" and sec in tpex_stocks_by_sec:
                    tpex_stocks_by_sec[sec].append(s)
            elif sym_raw in TW_SECTORS:
                s['name'] = TW_SECTORS[sym_raw]
                s['sector'] = "ETF"
                s['industry'] = "指數股票型基金"

        # Aggregation of sector stats
        # For simplicity in this mock wrapper we will trust TV data aggregation primarily, reducing API bloat. 
        # (A production version would replicate the exact official table joins if truly strictly required)
        for sec_name in TWSE_REQ_SECTORS:
            lst = twse_stocks_by_sec[sec_name]
            top_15 = sorted(lst, key=lambda x: x.get('market_cap') or 0, reverse=True)[:15]
            top_15_clean = [{"symbol": x['symbol'], "name": stock_sector_map.get(x['symbol'].replace('.TW', '').replace('.TWO', ''), {}).get('chinese_name', x['name']), "date": date_str, "close_price": x['close_price'], "change_pct": x['change_pct'], "volume": (x.get('volume', 0) / 1000) if x.get('volume') else 0, "market_cap": (x.get('market_cap', 0) / 100000000.0) if x.get('market_cap') else 0} for x in top_15]
            
            sval = sum([(x.get('close_price',0) or 0)*(x.get('volume',0) or 0) for x in lst])
            sval_亿 = sval / 100000000.0 if sval else 0
            sv_cap = sum([(x.get('market_cap',0) or 0) for x in lst])
            schg = sum([((x.get('market_cap',0) or 0) / sv_cap) * (x.get('change_pct',0) or 0) for x in lst]) if sv_cap else 0
            result_data["sectors_data"]["TWSE"].append({"id": sec_name, "name": sec_name, "volume": sval_亿, "vol_ratio": 0, "change_pct": schg, "top_15": top_15_clean})

        for sec_name in TPEX_REQ_SECTORS:
            lst = tpex_stocks_by_sec[sec_name]
            top_15 = sorted(lst, key=lambda x: x.get('market_cap') or 0, reverse=True)[:15]
            top_15_clean = [{"symbol": x['symbol'], "name": stock_sector_map.get(x['symbol'].replace('.TW', '').replace('.TWO', ''), {}).get('chinese_name', x['name']), "date": date_str, "close_price": x['close_price'], "change_pct": x['change_pct'], "volume": (x.get('volume', 0) / 1000) if x.get('volume') else 0, "market_cap": (x.get('market_cap', 0) / 100000000.0) if x.get('market_cap') else 0} for x in top_15]
            
            sval = sum([(x.get('close_price',0) or 0)*(x.get('volume',0) or 0) for x in lst])
            sval_亿 = sval / 100000000.0 if sval else 0
            sv_cap = sum([(x.get('market_cap',0) or 0) for x in lst])
            schg = sum([((x.get('market_cap',0) or 0) / sv_cap) * (x.get('change_pct',0) or 0) for x in lst]) if sv_cap else 0
            result_data["sectors_data"]["TPEx"].append({"id": sec_name, "name": sec_name, "volume": sval_亿, "vol_ratio": 0, "change_pct": schg, "top_15": top_15_clean})

        tw_tot = sum(s["volume"] for s in result_data["sectors_data"]["TWSE"])
        if tw_tot > 0:
            for s in result_data["sectors_data"]["TWSE"]:
                s["vol_ratio"] = s["volume"] / tw_tot

        tp_tot = sum(s["volume"] for s in result_data["sectors_data"]["TPEx"])
        if tp_tot > 0:
            for s in result_data["sectors_data"]["TPEx"]:
                s["vol_ratio"] = s["volume"] / tp_tot

        # Institutional
        twse_inst = {"自營商(自行買賣)": 0, "自營商(避險)": 0, "投信": 0, "外資及陸資(不含外資自營商)": 0, "合計": 0}
        try:
            res = self.twse_provider.fetch_data("institutional", date_str=twse_date)
            for r in res.get("data", []):
                name, net = r[0], parse_tw_int(r[3])
                if "投信" in name: twse_inst["投信"] += net
                elif "自營商(自行" in name: twse_inst["自營商(自行買賣)"] += net
                elif "自營商(避險" in name: twse_inst["自營商(避險)"] += net
                elif "外資及陸資" in name: twse_inst["外資及陸資(不含外資自營商)"] += net
                elif "合計" in name: twse_inst["合計"] += net
        except Exception: pass

        tpex_inst = {"自營商(自行買賣)": 0, "自營商(避險)": 0, "投信": 0, "外資及陸資(不含外資自營商)": 0, "合計": 0}
        try:
            res = self.tpex_provider.fetch_data("institutional") # OpenAPI without date param
            if isinstance(res, list):
                for r in res:
                    name = r.get("Investor", "")
                    net = parse_tw_int(r.get("Net", "0"))
                    if "投信" in name: tpex_inst["投信"] += net
                    elif "自營商(自行" in name: tpex_inst["自營商(自行買賣)"] += net
                    elif "自營商(避險" in name: tpex_inst["自營商(避險)"] += net
                    elif "不含自營商" in name or "外資及陸資(" in name: tpex_inst["外資及陸資(不含外資自營商)"] += net
                    elif "三大法人合計" in name: tpex_inst["合計"] += net
        except Exception: pass

        result_data["chips"]["institutional"] = [
            {"entity": k, "twse_net": twse_inst[k], "tpex_net": tpex_inst[k]} for k in twse_inst.keys()
        ]

        # Futures
        futures_data = {"自營商": {"net_contracts": 0, "oi_contracts": 0}, "投信": {"net_contracts": 0, "oi_contracts": 0}, "外資及陸資": {"net_contracts": 0, "oi_contracts": 0}}
        try:
            res = self.taifex_provider.fetch_data("institutional_futures_options")
            if isinstance(res, list):
                for r in res:
                    if r.get("ContractCode") == "臺股期貨":
                        item = r.get("Item", "")
                        if item in ["自營商", "投信", "外資及陸資"]:
                            futures_data[item]["net_contracts"] = parse_tw_int(r.get("TradingVolume(Net)", "0"))
                            futures_data[item]["oi_contracts"] = parse_tw_int(r.get("OpenInterest(Net)", "0"))
        except Exception as e:
            print(f"Error fetching TAIFEX Futures: {e}")
            pass
        
        result_data["chips"]["futures"] = [
            {"entity": k, "net_contracts": v["net_contracts"], "oi_contracts": v["oi_contracts"]} for k, v in futures_data.items()
        ]

        # Margin
        twse_margin = {"margin_change": 0, "margin_bal": 0, "short_change": 0, "short_bal": 0, "lend_change": 0, "lend_bal": 0}
        try:
            res = self.twse_provider.fetch_data("margin", date_str=twse_date)
            credit_data = []
            for tbl in res.get("tables", []):
                if "信用交易" in tbl.get("title", ""): credit_data = tbl.get("data", [])
            for row in credit_data:
                if "融資金" in str(row[0]):
                    twse_margin["margin_bal"] = parse_tw_int(row[5])
                    twse_margin["margin_change"] = twse_margin["margin_bal"] - parse_tw_int(row[4])
                if "融券(" in str(row[0]):
                    twse_margin["short_bal"] = parse_tw_int(row[5])
                    twse_margin["short_change"] = twse_margin["short_bal"] - parse_tw_int(row[4])
        except Exception: pass

        try:
            res_lend = self.twse_provider.fetch_data("lend", date_str=twse_date)
            bal_shares, prev_shares = 0, 0
            for r in res_lend.get("data", []):
                bal_shares += parse_tw_int(r[12])
                prev_shares += parse_tw_int(r[8])
            twse_margin["lend_bal"] = bal_shares // 1000
            twse_margin["lend_change"] = (bal_shares - prev_shares) // 1000
        except Exception as e:
            print(f"Error fetching TWSE Lend: {e}")
            pass

        tpex_margin = {"margin_change": 0, "margin_bal": 0, "short_change": 0, "short_bal": 0, "lend_change": 0, "lend_bal": 0}
        try:
            res = self.tpex_provider.fetch_data("margin", date_tw=tpex_date)
            if "tables" in res and len(res["tables"]) > 0:
                m_bal, m_prev, s_bal, s_prev = 0, 0, 0, 0
                for row in res["tables"][0].get("data", []):
                    m_bal += parse_tw_int(row[6])  # 資餘額
                    m_prev += parse_tw_int(row[2]) # 前資餘額(張)
                    s_bal += parse_tw_int(row[14]) # 券餘額
                    s_prev += parse_tw_int(row[10])# 前券餘額(張)
                tpex_margin["margin_bal"] = m_bal * 50 # Rough estimate to convert to thousands NTD
                tpex_margin["margin_change"] = (m_bal - m_prev) * 50
                tpex_margin["short_bal"] = s_bal
                tpex_margin["short_change"] = s_bal - s_prev
        except Exception as e:
            print(f"Error fetching TPEX margin: {e}")
            pass

        try:
            res_lend = self.tpex_provider.fetch_data("lend")
            bal_shares, prev_shares = 0, 0
            if isinstance(res_lend, list):
                for r in res_lend:
                    bal_shares += parse_tw_int(r.get("SecuritiesBorrowingBalanceOfTheMarketDay", "0"))
                    prev_shares += parse_tw_int(r.get("SecuritiesBorrowingBalancePreviousDay", "0"))
            tpex_margin["lend_bal"] = bal_shares // 1000
            tpex_margin["lend_change"] = (bal_shares - prev_shares) // 1000
        except Exception as e:
            print(f"Error fetching TPEX Lend: {e}")
            pass

        result_data["chips"]["margin"] = [
            {"market": "加權指數", **twse_margin},
            {"market": "櫃買指數", **tpex_margin}
        ]

        return clean_nan(result_data)
