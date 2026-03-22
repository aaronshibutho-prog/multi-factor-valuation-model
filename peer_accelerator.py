import pandas as pd
import yfinance as yf
import time
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
url1 = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
url2 = "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"
df1 = pd.read_csv(url1, sep='|')
df2 = pd.read_csv(url2, sep='|')
df1=df1[['Symbol']]
df2=df2[['ACT Symbol']].rename(columns={'ACT Symbol': 'Symbol'})
df = pd.concat([df1, df2], ignore_index=True)
results = []
df = df[df['Symbol'].notna()]
df = df[df['Symbol'] != 'File Creation Time']
print("Processing tickers to retrieve industry information...")
for i in range(len(df)):
    symbol=df['Symbol'].iloc[i]
    try:
        ticker = yf.Ticker(symbol)
        indus = ticker.info.get('industry')
        if indus is not None:
            results.append({'Symbol': symbol, 'Industry': indus})
    except:
        continue
    time.sleep(0.1)
df3 = pd.DataFrame(results)
df3.to_excel('industry_ticks.xlsx', index=False)
print("Successfully retrieved industry information for tickers.")
print(df3) 