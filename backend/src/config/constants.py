# src/config/constants.py

# --- Global Market Constants ---

REGION_INDICES = {
    "US": { "DJ:DJI": "Dow Jones", "SP:SPX": "S&P 500", "NASDAQ:IXIC": "NASDAQ", "NASDAQ:SOX": "PHLX Semiconductor", "TVC:RUT": "Russell 2000" },
    "Europe": { "XETR:DAX": "DAX", "EURONEXT:PX1": "CAC 40", "TVC:UKX": "FTSE 100" },
    "Asia": { "TVC:NI225": "Nikkei 225", "KRX:KOSPI": "KOSPI", "ASX:XJO": "ASX 200", "HSI:HSI": "Hang Seng", "SGX:CN1!": "China A50", "SSE:000300": "CSI 300", "SSE:000001": "SSE Composite" }
}

SECTOR_ETFS = {
    "AMEX:XLK": "Technology", "AMEX:XLV": "Health Care", "AMEX:XLF": "Financials", "AMEX:XLY": "Consumer Discretionary", 
    "AMEX:XLI": "Industrials", "AMEX:XLP": "Consumer Staples", "AMEX:XLE": "Energy", "AMEX:XLU": "Utilities", 
    "AMEX:XLRE": "Real Estate", "AMEX:XLB": "Materials", "AMEX:XLC": "Communication Services"
}

COMMODITIES_HIERARCHY = {
    "Metals": {
        "Precious Metals": {"Gold": "COMEX:GC1!", "Silver": "COMEX:SI1!", "Platinum": "NYMEX:PL1!", "Palladium": "NYMEX:PA1!"},
        "Base Metals": {"Copper": "COMEX:HG1!", "Aluminum": "COMEX:ALI1!", "Zinc": "COMEX:ZNC1!", "Lead": "COMEX:LED1!"},
        "Ferrous Metals": {"Iron Ore": "SGX:FEF1!", "HRC": "COMEX:HRC1!"},
        "Battery Metals": {"Lithium": "AMEX:LIT"}
    },
    "Energy, Petrochemicals & Chemicals": {
        "Energy & Crude Oil": {"WTI Crude Oil": "NYMEX:CL1!", "Brent Crude Oil": "NYMEX:BZ1!", "RBOB Gasoline": "NYMEX:RB1!", "Heating Oil": "NYMEX:HO1!"}
    },
    "Agricultural Products": {
        "Grains & Oilseeds": {"Soybeans": "CBOT:ZS1!", "Soybean Oil": "CBOT:ZL1!", "Soybean Meal": "CBOT:ZM1!", "Corn": "CBOT:ZC1!", "Wheat": "CBOT:ZW1!", "Oats": "CBOT:ZO1!"},
        "Softs": {"Coffee": "ICEUS:KC1!", "Cocoa": "ICEUS:CC1!", "Sugar No. 11": "ICEUS:SB1!", "Cotton": "ICEUS:CT1!", "FCOJ": "ICEUS:OJ1!"},
        "Livestock & Meats": {"Live Cattle": "CME:LE1!", "Feeder Cattle": "CME:GF1!", "Lean Hogs": "CME:HE1!"},
        "Regional & Specialty": {"Crude Palm Oil": "MYX:FCPO1!"}
    }
}

# --- Taiwan Market Constants ---

TW_INDICES = {
    "^TWII": "加權指數",
    "0050.TW": "台灣50",
    "0051.TW": "中型100",
    "^TWOII": "櫃買指數",
    "020020.TWO": "富櫃200"
}

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

TWSE_REQ_SECTORS = ["水泥工業", "食品工業", "塑膠工業", "紡織纖維", "電機機械", "電器電纜", "玻璃陶瓷", "造紙工業", "鋼鐵工業", "橡膠工業", "汽車工業", "電子工業", "建材營造", "航運業", "觀光餐旅", "金融保險", "貿易百貨", "化學工業", "生技醫療業", "油電燃氣業", "綠能環保", "數位雲端", "運動休閒", "居家生活", "其他", "半導體業", "電腦及週邊設備業", "光電業", "通信網路業", "電子零組件業", "電子通路業", "資訊服務業", "其他電子業"]
TPEX_REQ_SECTORS = ["食品工業", "塑膠工業", "紡織纖維", "電機機械", "電器電纜", "玻璃陶瓷", "鋼鐵工業", "橡膠工業", "汽車工業", "建材營造", "航運業", "觀光餐旅", "金融業", "貿易百貨", "其他", "化學工業", "生技醫療業", "油電燃氣業", "半導體業", "電腦及週邊設備業", "光電業", "通信網路業", "電子零組件業", "電子通路業", "資訊服務業", "其他電子業", "文化創意業", "農業科技業", "電子商務", "綠能環保", "數位雲端", "運動休閒", "居家生活"]

TWSE_CODE_MAP = {"01": "水泥工業", "02": "食品工業", "03": "塑膠工業", "04": "紡織纖維", "05": "電機機械", "06": "電器電纜", "07": "玻璃陶瓷", "08": "造紙工業", "09": "鋼鐵工業", "10": "橡膠工業", "11": "汽車工業", "12": "電子工業", "14": "建材營造", "15": "航運業", "16": "觀光餐旅", "17": "金融保險", "18": "貿易百貨", "20": "其他", "21": "化學工業", "22": "生技醫療業", "23": "油電燃氣業", "24": "半導體業", "25": "電腦及週邊設備業", "26": "光電業", "27": "通信網路業", "28": "電子零組件業", "29": "電子通路業", "30": "資訊服務業", "31": "其他電子業", "35": "綠能環保", "36": "數位雲端", "37": "運動休閒", "38": "居家生活"}
TPEX_CODE_MAP = {"02": "食品工業", "03": "塑膠工業", "04": "紡織纖維", "05": "電機機械", "06": "電器電纜", "08": "玻璃陶瓷", "09": "鋼鐵工業", "10": "橡膠工業", "11": "汽車工業", "14": "建材營造", "15": "航運業", "16": "觀光餐旅", "17": "金融業", "18": "貿易百貨", "20": "其他", "21": "化學工業", "22": "生技醫療業", "23": "油電燃氣業", "24": "半導體業", "25": "電腦及週邊設備業", "26": "光電業", "27": "通信網路業", "28": "電子零組件業", "29": "電子通路業", "30": "資訊服務業", "31": "其他電子業", "32": "文化創意業", "33": "農業科技業", "34": "電子商務", "35": "綠能環保", "36": "數位雲端", "37": "運動休閒", "38": "居家生活"}
