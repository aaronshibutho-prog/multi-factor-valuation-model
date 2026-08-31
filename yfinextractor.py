import yfinance as yf
import pandas as pd
import time
pd.options.display.float_format = '{:,.0f}'.format
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

def fetch_with_retry(fn, *args, retries=3, base_delay=1.5, label=None, **kwargs):
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if attempt == retries - 1:
                print(f"Skipped {label or args}: {e}")
                return None
            time.sleep(base_delay * (2 ** attempt))

def inform(ticker):
    stk=yf.Ticker(ticker)
    bs=stk.balance_sheet
    fin=stk.financials
    cf=stk.cashflow
    bs.dropna(axis=1,how="all",inplace=True)
    fin.dropna(axis=1,how="all",inplace=True)
    cf.dropna(axis=1,how="all",inplace=True)
    bs = bs.iloc[:, :4]
    fin = fin.iloc[:, :4]
    cf = cf.iloc[:, :4]
    return(stk,bs,fin,cf)
if __name__ == "__main__":
    print("Enter the Stock Ticker (e.g., AAPL or RELIANCE.NS):")
    name=input().strip().upper()
    stk, bs, fin, cf = inform(name)
    print(f"Balance Sheet of {name}:")
    print(bs)
    print(f"\nFinancials of {name}:")
    print(fin)
    print(f"\nCash Flow of {name}:")
    print(cf)