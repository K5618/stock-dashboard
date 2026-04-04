import yfinance as yf

# Standard futures tickers guess
tickers = {
    "Gold": "GC=F", "Silver": "SI=F", "Platinum": "PL=F", "Palladium": "PA=F",
    "Copper": "HG=F", "Aluminum": "ALI=F", "Zinc": "ZNC=F", "Lead": "LED=F", "Nickel": "NIK=F", "Tin": "TIN=F",
    "Iron Ore": "TIO=F", "HRC": "HRC=F", "Rebar": "SRB=F", "Scrap Steel": "BUS=F",
    "Lithium": "LIT", "Cobalt": "COB=F", 
    "WTI": "CL=F", "Brent": "BZ=F", "RBOB Gasoline": "RB=F", "Heating Oil": "HO=F",
    "Naphtha": "NPH=F", "LLDPE": "LLDPE=F", "PP": "PP=F", "PVC": "PVC=F",
    "Soybeans": "ZS=F", "Soybean Oil": "ZL=F", "Soybean Meal": "ZM=F", "Corn": "ZC=F", "Wheat": "ZW=F", "Oats": "ZO=F",
    "Coffee": "KC=F", "Cocoa": "CC=F", "Sugar No. 11": "SB=F", "Cotton": "CT=F", "FCOJ": "OJ=F",
    "Live Cattle": "LE=F", "Feeder Cattle": "GF=F", "Lean Hogs": "HE=F",
    "Crude Palm Oil": "CPO=F", "Natural Rubber": "RUB=F"
}

results = {}
for name, symbol in tickers.items():
    try:
        hist = yf.Ticker(symbol).history(period="1d")
        if not hist.empty:
            results[name] = {"symbol": symbol, "found": True, "close": hist['Close'].iloc[-1]}
        else:
            results[name] = {"symbol": symbol, "found": False}
    except Exception as e:
         results[name] = {"symbol": symbol, "found": False}

print("Available:")
for name, res in results.items():
    if res["found"]:
        print(f"{name}: {res['symbol']}")

print("\nMissing:")
for name, res in results.items():
    if not res["found"]:
        print(f"{name}: {res['symbol']}")
