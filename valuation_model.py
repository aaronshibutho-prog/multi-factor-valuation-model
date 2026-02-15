import yfinance as yf
import pandas as pd
print("Enter the Stock Ticker (e.g., NVDA, AAPL, RELIANCE.BO):")
name=input().strip().upper()
over = fair = under = 0
stk=yf.Ticker(name)
info=stk.info
bs=stk.balance_sheet
fin=stk.financials
cf=stk.cashflow
ROE=None
MP=info.get('currentPrice')
print(f"Current Price: {MP}")
try:
    TE = bs.loc['Stockholders Equity'].iloc[0]
except:
    try:
        TE = bs.loc['Common Stock Equity'].iloc[0]
    except:
        try:
            TE = bs.loc['Total Equity Gross Minority Interest'].iloc[0]
        except:
            print("Information Unavailable for Equity")
            TE = None
try:
    SO=info.get('sharesOutstanding')
except:
    SO=None
if pd.isna(TE) or TE <= 0 or SO is None or pd.isna(SO) or SO <= 0 or MP is None or pd.isna(MP):
    print('P/B ratio will not be used due to insufficient data' )
else:
    net_income = fin.loc['Net Income'].iloc[0]
    if pd.notna(net_income):
        ROE = net_income / TE
    PB = MP / (TE / SO)
    if ROE is not None and pd.notna(ROE) and PB > 1 and ROE < 0.15:
        over += 1
    elif PB < 1:
        under += 1
    else:
        fair += 1
    print(f"PB: {PB:.3f} | Score -> over:{over}, fair:{fair}, under:{under}")
try:
    peg = info.get("trailingPegRatio") or info.get("pegRatio") or info.get("forwardPegRatio")
except:
    print('Information Unavailable for PEG Ratio')
    peg=None
if peg is None or pd.isna(peg) or peg<0:
    print('PEG ratio will not be used due to insufficient data' )
else:
    if peg>2:
        over+=1
    elif peg<1:
        under+=1
    else:
        fair+=1
    print(f"PEG: {peg:.3f} | Score -> over:{over}, fair:{fair}, under:{under}")
MC = info.get('marketCap')
if 'Free Cash Flow' in cf.index:
    FCF = cf.loc['Free Cash Flow'].dropna().iloc[0]
else:
    FCF = None
if FCF is None or pd.isna(FCF) or FCF<0 or MC is None or pd.isna(MC) or MC <= 0:
    print('Free Cash Flow Yield ratio will not be used due to insufficient data' )
else:
    FCFy=FCF/MC
    if FCFy>0.05:
        under+=2
    elif FCFy<0.02:
        over+=2
    else:
        fair+=2
    print(f"FCFy: {FCFy:.3f} | Score -> over:{over}, fair:{fair}, under:{under}")
if ROE is None:
    try:
        net_income = fin.loc['Net Income'].iloc[0]
    except:
        net_income = None
    if net_income is not None and TE is not None and TE > 0:
        ROE = net_income / TE
        if ROE > 0.20:
            under += 1
        elif ROE < 0.10:
            over += 1
        else:
            fair += 1
        print(f"ROE: {ROE:.3f} | Score -> over:{over}, fair:{fair}, under:{under}")
    else:
        print("ROE will not be used due to insufficient data.")
elif ROE>0:
    if ROE > 0.20:
        under += 1
    elif ROE < 0.10:
        over += 1
    else:
        fair += 1
    print(f"ROE: {ROE:.3f} | Score -> over:{over}, fair:{fair}, under:{under}")
PV_sum = 0
n = 5
try:
    revenue = fin.loc['Total Revenue']
    rev_latest = revenue.iloc[0]
    rev_oldest = revenue.iloc[-1]
    years = len(revenue) - 1
    if years > 0 and pd.notna(rev_oldest) and rev_oldest != 0:
        g = (rev_latest / rev_oldest) ** (1/years) - 1
    else:
        g = 0.05
except:
    g = 0.05 
g = min(g, 0.15)
g = max(g, -0.05)
if name.endswith((".NS", ".BO")):
    Rf = 0.07
    gt = 0.035
else:
    Rf = 0.045
    gt = 0.025
market_premium = 0.055
beta = info.get("beta")

if beta is not None and not pd.isna(beta):
    Re = Rf + beta * market_premium
else:
    Re = Rf + 0.06
try:
    interest = fin.loc['Interest Expense'].iloc[0]
    total_debt = bs.loc['Total Debt'].iloc[0]
    if pd.notna(total_debt) and total_debt > 0 and pd.notna(interest):
        Rd = abs(interest) / total_debt
    else:
        Rd = 0.05
        total_debt = 0
except Exception:
    Rd = 0.05
    total_debt = 0
try:
    tax = fin.loc['Tax Provision'].iloc[0]
    pretax = fin.loc['Pretax Income'].iloc[0]
    if pd.notna(tax) and pd.notna(pretax) and pretax != 0:
        T = tax / pretax
    else:
        T = 0.25
except Exception:
    T = 0.25
T = max(0.0, min(T, 0.35))
MC = info.get('marketCap')
if MC and total_debt and (MC + total_debt) > 0:
    we = MC / (MC + total_debt)
    wd = total_debt / (MC + total_debt)
else:
    we = 1
    wd = 0
r = we * Re + wd * Rd * (1 - T)
try:
    if 'Free Cash Flow' in cf.index:
        FCF0 = cf.loc['Free Cash Flow'].dropna().mean()
    elif 'Operating Cash Flow' in cf.index and 'Capital Expenditure' in cf.index:
        FCF0 = (cf.loc['Operating Cash Flow'] - cf.loc['Capital Expenditure']).mean()
    else:
        FCF0 = None
except:
    FCF0 = None
if FCF0 is None or pd.isna(FCF0) or FCF0 <= 0 or SO is None or pd.isna(SO) or SO <= 0 or MP is None or pd.isna(MP) or MP <= 0 or r <= gt:
    print("Information Unavailable for Discounted Cash Flow")
else:
    for t in range(1,n+1):
        FFCF=FCF0*(1+g)**t
        FCFPV=FFCF/(1+r)**t
        PV_sum+=FCFPV
    FCF_n=FCF0*(1+g)**n
    TV=FCF_n*(1+gt)/(r-gt)
    PVTV=TV/(1+r)**n
    EV=PVTV+PV_sum
    cash = info.get("totalCash")
    equity_value = EV - total_debt + (cash if cash else 0)
    IV = equity_value / SO
    up=(IV-MP)/MP
    if up>= 0.3:
        under+=2
    elif up>=0.15:
        under+=1
    elif up>=-0.1 and up<0.15:
        fair+=2
    elif up>=-0.3 and up<-0.1:
        over+=1
    else:
        over+=2
    print(f"DCF: {up:.3%} | Score -> over:{over}, fair:{fair}, under:{under}")
try:
    if TE is not None and TE > 0:
        DE = bs.loc['Total Debt'].iloc[0] / TE
    else:
        DE = None
except Exception:
    print('Information Unavailable for Debt to Equity ratio')
    DE = None
if DE is None:
    print("D/E unavailable")
else:
    if DE < 0.5:
        under += 1
    elif DE <= 1.5:
        fair += 1
    else:
        over += 1
    print(f"DE: {DE:.3f} | Score -> over:{over}, fair:{fair}, under:{under}")
total = under + fair + over

if total == 0:
    print("FINAL: No signals available")
else:
    winner = max(under, fair, over)
    confidence = winner / total
    winners = [under, fair, over].count(winner)
    if winners > 1:
        verdict = "Fair / Inconclusive"
    elif winner == under:
        verdict="Undervalued"
    elif winner==over:
        verdict="Overvalued"
    else:
        verdict="Fairly Valued"
    print(f"FINAL: {verdict} | Confidence: {confidence:.0%}")
    print("\nDISCLAIMER:")
    print("This valuation is based on publicly available financial data and assumptions.")
    print("It does not constitute financial advice. Please conduct your own research before investing.")