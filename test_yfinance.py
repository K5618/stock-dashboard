import yfinance as yf

symbols = {
    "us": ["^DJI", "^GSPC", "^IXIC", "^SOX", "^RUT"],
    "eu": ["^GDAXI", "^FCHI", "^FTSE"],
    "as": ["^TWII", "^TWOII", "TWOII.TW", "^N225", "^KS11", "^AXJO", "^HSI", "XIN9.FGI", "^XIN9", "000300.SS", "000001.SS"]
}

print("Testing yfinance capabilities:")
for region, tickers in symbols.items():
    print(f"\nRegion: {region}")
    for ticker in tickers:
        try:
            data = yf.Ticker(ticker).history(period="1d")
            if not data.empty:
                print(f"[OK] {ticker} - Close: {data['Close'].iloc[-1]:.2f}")
            else:
                print(f"[FAIL] {ticker} - Empty dataframe")
        except Exception as e:
            print(f"[FAIL] {ticker} - Exception: {e}")
