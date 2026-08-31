import pandas as pd
from yfinextractor import inform
import yfinance as yf
print("Enter the Stock Ticker (e.g., AAPL or RELIANCE.NS):")
name = input().strip().upper()
stk, bs, fin, cf = inform(name)
industry = stk.info.get('industry')
mark_cap = stk.info.get('marketCap')
target_market = 'IN' if name.endswith('.NS') else 'US'
ticks_us = pd.read_excel('industry_ticks.xlsx')
ticks_us['Market'] = 'US'
ticks_in = pd.read_excel('industry_ticks_india.xlsx')
company_industry = pd.concat([ticks_us, ticks_in], ignore_index=True)
company_industry = company_industry[company_industry['Market'] == target_market]
fx = 1
if target_market == 'IN':
    fx = yf.Ticker('USDINR=X').fast_info['lastPrice']
    mark_cap = mark_cap / fx
peers = []
if mark_cap is None:
    print(f"Market capitalization information for {stk.ticker} is not available. Unable to determine peers based valuation.")
elif industry is None:
    print(f"Industry information for {stk.ticker} is not available. Unable to determine peers based valuation.")
else:
    for i in range(len(company_industry)):
        if company_industry['Industry'].iloc[i] == industry:
            peer_info = yf.Ticker(company_industry['Symbol'].iloc[i])
            try:
                peer_mark_cap = peer_info.info.get('marketCap')
            except Exception:
                continue
            if peer_mark_cap is None:
                continue
            if target_market == 'IN':
                peer_mark_cap = peer_mark_cap / fx
            if peer_info.ticker == stk.ticker:
                continue
            if peer_mark_cap >= 200_000_000_000 and mark_cap >= 200_000_000_000:
                peers.append(peer_info.ticker)
            elif 10_000_000_000 <= peer_mark_cap < 200_000_000_000 and 10_000_000_000 <= mark_cap < 200_000_000_000:
                peers.append(peer_info.ticker)
            elif 2_000_000_000 <= peer_mark_cap < 10_000_000_000 and 2_000_000_000 <= mark_cap < 10_000_000_000:
                peers.append(peer_info.ticker)
            elif 300_000_000 <= peer_mark_cap < 2_000_000_000 and 300_000_000 <= mark_cap < 2_000_000_000:
                peers.append(peer_info.ticker)
            elif peer_mark_cap < 300_000_000 and mark_cap < 300_000_000:
                peers.append(peer_info.ticker)
