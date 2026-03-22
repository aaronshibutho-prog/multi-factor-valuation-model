import pandas as pd
from yfinextractor import inform
import yfinance as yf
print("Enter the US Stock Ticker (e.g., NVDA, AAPL):")
name = input().strip().upper()
stk, bs, fin, cf = inform(name)
industry = stk.info.get('industry')
mark_cap=stk.info.get('marketCap')
company_industry=pd.read_excel('industry_ticks.xlsx')
peers=[]
if mark_cap is None:
    print(f"Market capitalization information for {stk.ticker} is not available. Unable to determine peers based valuation.")
elif industry is None:
    print(f"Industry information for {stk.ticker} is not available. Unable to determine peers based valuation.")
else:

    for i in range(len(company_industry)):
        if company_industry['Industry'].iloc[i] == industry:
            peer_info=yf.Ticker(company_industry['Symbol'].iloc[i])
            peer_mark_cap=peer_info.info.get('marketCap')
            if peer_mark_cap is None:
                pass
            elif peer_mark_cap >= 200_000_000_000 and mark_cap >= 200_000_000_000:
                if peer_info.ticker != stk.ticker:
                    peers.append(peer_info.ticker)
            elif peer_mark_cap >= 10_000_000_000 and peer_mark_cap < 200_000_000_000 and mark_cap >= 10_000_000_000 and mark_cap < 200_000_000_000:
                if peer_info.ticker != stk.ticker:
                    peers.append(peer_info.ticker)
            elif peer_mark_cap >= 2_000_000_000 and peer_mark_cap < 10_000_000_000 and mark_cap >= 2_000_000_000 and mark_cap < 10_000_000_000:
                if peer_info.ticker != stk.ticker:
                    peers.append(peer_info.ticker)
            elif peer_mark_cap >= 300_000_000 and peer_mark_cap < 2_000_000_000 and mark_cap >= 300_000_000 and mark_cap < 2_000_000_000:
                if peer_info.ticker != stk.ticker:
                    peers.append(peer_info.ticker)
            elif peer_mark_cap < 300_000_000 and mark_cap < 300_000_000:
                if peer_info.ticker != stk.ticker:
                    peers.append(peer_info.ticker)