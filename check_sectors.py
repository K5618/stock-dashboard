import yfinance as yf

symbols = ['AAPL', 'JNJ', 'JPM', 'AMZN', 'GE', 'PG', 'XOM', 'DUK', 'PLD', 'LIN', 'GOOG']
for s in symbols:
    info = yf.Ticker(s).info
    print(f"{s}: {info.get('sector', 'Unknown')}")
