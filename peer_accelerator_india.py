import pandas as pd
import yfinance as yf
df = pd.read_csv('indian_equities.csv')
df.columns = df.columns.str.strip()
df = df[df['SERIES'].str.strip()=='EQ']
df['Ticker'] = df['SYMBOL'].str.strip() + '.NS'
symbols = df['Ticker'].tolist()
results = []
print("Fetching industry data for Indian equities...")
for i , sym in enumerate(symbols):
    try:
        industry = yf.Ticker(sym).info.get('industry')
        if industry is not None:
            results.append({'Symbol': sym, 'Industry': industry, 'Market': 'IN'})
    except:
        continue
    if i % 100 == 0:
        print(f"{i}/{len(symbols)} processed")

