from peer_allocator import peers, stk, bs, fin, cf
import yfinance as yf
import pandas as pd
import numpy as np
pd.set_option("display.float_format", lambda x: f"{x:.2f}")
def industry_weight(stock):
    industry=stock.info.get('industry')
    weight_df = pd.read_excel('industry_ticks_weighted.xlsx')
    row = weight_df[weight_df['Industry'] == industry]
    if not row.empty:
        return {
            "P/E Ratio": row["P/E Ratio %"].iloc[0] / 100,
            "P/B Ratio": row["P/B Ratio %"].iloc[0] / 100,
            "Forward P/E Ratio": row["Forward P/E Ratio %"].iloc[0] / 100,
            "PEG Ratio": row["PEG Ratio %"].iloc[0] / 100,
            "EV/EBITDA": row["EV/EBITDA %"].iloc[0] / 100,
            "EV/Sales": row["EV/Sales %"].iloc[0] / 100,
            "P/FCF": row["P/FCF %"].iloc[0] / 100
        }
    else:
        return {
            "P/E Ratio": 1,
            "P/B Ratio": 1,
            "Forward P/E Ratio": 1,
            "PEG Ratio": 1,
            "EV/EBITDA": 1,
            "EV/Sales": 1,
            "P/FCF": 1
        }
def industry_quality_weight(stock):
    industry=stock.info.get('industry')
    weight_df = pd.read_excel('industry_quality_weights.xlsx')
    row = weight_df[weight_df['Industry'] == industry]
    if not row.empty:
        return {
            "ROA": row["ROA %"].iloc[0] / 100,
            "ROIC": row["ROIC %"].iloc[0] / 100,
            "Asset Turnover": row["Asset Turnover %"].iloc[0] / 100,
            "Receivable Stress": row["Receivable Stress %"].iloc[0] / 100,
            "Inventory Stress": row["Inventory Stress %"].iloc[0] / 100,
            "FCF Yield": row["FCF Yield %"].iloc[0] / 100,
            "Debt to Equity Ratio": row["Debt to Equity Ratio %"].iloc[0] / 100,
            "Interest Coverage": row["Interest Coverage %"].iloc[0] / 100
        }
    else:
        return {
            "ROA": 2,
            "ROIC": 3,
            "Asset Turnover": 2,
            "Receivable Stress": 2,
            "Inventory Stress": 2,
            "FCF Yield": 2,
            "Debt to Equity Ratio": 2,
            "Interest Coverage": 2
        }
    
def pe_ratio_calculator(stock, financials):
    try:
        try:
            market_price=stock.fast_info.get('lastPrice')
        except:
            market_price=stock.history(period="1d")['Close'].iloc[-1]
    except:
        market_price=None
    try: 
        earnings_per_share=financials.loc['Net Income Common Stock'].iloc[0] / stock.info.get('sharesOutstanding')
    except:
        earnings_per_share=None
    if market_price is not None and earnings_per_share is not None and earnings_per_share > 0 and pd.notna(market_price) and pd.notna(earnings_per_share):
        pe_ratio=market_price / earnings_per_share
    elif stock.info.get('trailingPE') is not None and pd.notna(stock.info.get('trailingPE')):
        pe_ratio=stock.info.get('trailingPE')
    else: pe_ratio=None
    return pe_ratio

def pb_ratio_calculator(stock,balance_sheet):
    try:
        try:
            book_value_per_share=(balance_sheet.loc['Stockholders Equity'].iloc[0]-balance_sheet.loc['Preferred Stock'].iloc[0]) / stock.info.get('sharesOutstanding')
        except:
            book_value_per_share=stock.info.get('bookValue')
    except:
        book_value_per_share=None
    try:
        try:
            market_price=stock.fast_info.get('lastPrice')
        except:
            market_price=stock.history(period="1d")['Close'].iloc[-1]
    except:
        market_price=None
    if market_price is not None and book_value_per_share is not None and pd.notna(book_value_per_share) and pd.notna(market_price) and book_value_per_share > 0:
            pb_ratio=market_price / book_value_per_share
    elif stock.info.get('priceToBook') is not None and pd.notna(stock.info.get('priceToBook')):
        pb_ratio=stock.info.get('priceToBook')
    else: pb_ratio=None
    return pb_ratio

def forward_pe_ratio_calculator(stock):
    try:
        forward_pe_ratio=stock.info.get('forwardPE')
    except:
        forward_pe_ratio=None
    return forward_pe_ratio

def peg_ratio_calculator(stock):
    try:
        earnings_growth_rate=float(stock.info.get('earningsGrowth')) 
    except:
        earnings_growth_rate=None
    try:
        pe_ratio=float(stock.info.get('trailingPE'))
    except:
        pe_ratio=None
    if pe_ratio is not None and earnings_growth_rate is not None and earnings_growth_rate > 0 and pd.notna(pe_ratio) and pd.notna(earnings_growth_rate):
        peg_ratio=float(pe_ratio / (earnings_growth_rate * 100))
    elif stock.info.get('pegRatio') is not None and pd.notna(stock.info.get('pegRatio')):
        peg_ratio=float(stock.info.get('pegRatio'))
    else: peg_ratio=None
    return peg_ratio
        
def ev_to_ebitda_calculator(stock, financials):
    try:
        try:
            enterprise_value=stock.info.get('marketCap') + stock.info.get('totalDebt') - stock.info.get('cash')
        except:
            enterprise_value=stock.info.get('enterpriseValue')
        
    except:
        enterprise_value=None
    try:
        try:
            ebitda=stock.info.get('ebitda')
        except:
            ebitda=financials.loc['Ebitda'].iloc[0]
    except:
        ebitda=None
    if enterprise_value is not None and ebitda is not None and ebitda > 0:
        ev_to_ebitda=enterprise_value / ebitda
    elif stock.info.get('enterpriseToEbitda') is not None and pd.notna(stock.info.get('enterpriseToEbitda')):
        ev_to_ebitda=stock.info.get('enterpriseToEbitda')
    else: ev_to_ebitda=None
    return ev_to_ebitda


def ev_sales_calculator(stock, financials):
    try:
        try:
            enterprise_value=stock.info.get('marketCap') + stock.info.get('totalDebt') - stock.info.get('cash')
        except:
            enterprise_value=stock.info.get('enterpriseValue')
    except:
        enterprise_value=None
    try:
        try:
            sales=stock.info.get('totalRevenue')
        except:
            sales=financials.loc['Total Revenue'].iloc[0]   
    except:
        sales=None
    if enterprise_value is not None and sales is not None and sales > 0 and pd.notna(enterprise_value) and pd.notna(sales):
        ev_sales=enterprise_value / sales   
    elif stock.info.get('enterpriseToRevenue') is not None and pd.notna(stock.info.get('enterpriseToRevenue')):
        ev_sales=stock.info.get('enterpriseToRevenue')  
    else: ev_sales=None
    return ev_sales

def p_fcf_calculator(stock, cashflow):
    try:
        try:
            market_cap=stock.info.get('marketCap')
        except:
            market_cap=stock.info.get('enterpriseValue') - stock.info.get('totalDebt') + stock.info.get('cash')
    except:
        market_cap=None
    try:
        try:
            free_cash_flow=stock.info.get('freeCashflow')
        except:
            free_cash_flow=cashflow.loc['Free Cash Flow'].iloc[0]
    except:
        free_cash_flow=None
    if market_cap is not None and free_cash_flow is not None and free_cash_flow > 0 and pd.notna(market_cap) and pd.notna(free_cash_flow):
        p_fcf=market_cap / free_cash_flow
    else: p_fcf=None
    return p_fcf

def discounted_cash_flow_calculator(stock, cashflow, financials, balance_sheet):
    free_cash_flow_to_equity = None
    free_cash_flow_to_firm = None
    try:
        int_expense=abs(financials.loc['Interest Expense'].iloc[0])
        if pd.isna(int_expense): int_expense=0
    except (KeyError, IndexError):
        int_expense=0
    try:
        issued_debt=cashflow.loc['Issuance Of Debt'].iloc[0]
        if pd.isna(issued_debt): issued_debt=0
    except (KeyError, IndexError):
        issued_debt=0
    try:
        repayed_debt=abs(cashflow.loc['Repayment Of Debt'].iloc[0])
        if pd.isna(repayed_debt): repayed_debt=0
    except (KeyError, IndexError):
        repayed_debt=0
    try:
        tax_rate = financials.loc['Tax Provision'].iloc[0] / financials.loc['Pretax Income'].iloc[0]
        if tax_rate < 0 or tax_rate > 1:
            tax_rate = 0.21
    except:
        tax_rate = 0.21
    try:
        try:
            free_cash_flow_to_equity= stock.info.get('operatingCashflow') -abs (cashflow.loc['Capital Expenditure'].iloc[0]) + issued_debt - repayed_debt
        except:
            cy_wc=balance_sheet.loc['Current Assets'].iloc[0] - balance_sheet.loc['Current Liabilities'].iloc[0]
            py_wc=balance_sheet.loc['Current Assets'].iloc[1] - balance_sheet.loc['Current Liabilities'].iloc[1]
            wc_change=cy_wc - py_wc
            free_cash_flow_to_equity= financials.loc['Net Income Common Stockholders'].iloc[0] + cashflow.loc['Depreciation And Amortization'].iloc[0] - abs(cashflow.loc['Capital Expenditure'].iloc[0]) - wc_change + issued_debt - repayed_debt
    except:
        try:
            free_cash_flow_to_firm=financials.loc['EBIT'].iloc[0] * (1 - tax_rate) + cashflow.loc['Depreciation And Amortization'].iloc[0] - abs(cashflow.loc['Capital Expenditure'].iloc[0]) - cashflow.loc['Change In Working Capital'].iloc[0]
        except:
            try:
                free_cash_flow_to_firm=cashflow.loc['Operating Cash Flow'].iloc[0] + int_expense * (1 - tax_rate) - abs(cashflow.loc['Capital Expenditure'].iloc[0])
            except:
                free_cash_flow_to_firm=None
    if free_cash_flow_to_equity is not None and pd.notna(free_cash_flow_to_equity):
        tnx = yf.Ticker("^TNX")
        if tnx.fast_info['last_price'] / 100 is not None and tnx.fast_info['last_price'] / 100 > 0 and pd.notna(tnx.fast_info['last_price'] / 100):
            r_f=tnx.fast_info['lastPrice'] / 100
        else: r_f=0.0425
        equity_risk_premium=0.045
        beta=stock.info.get('beta')
        if beta is not None and pd.notna(beta):
            cost_of_equity=r_f + beta * equity_risk_premium
        else:
            sp500=yf.Ticker("^GSPC")
            market_return=sp500.history(period="5y")["Close"].resample('ME').last().pct_change()
            stock_return=stock.history(period="5y")["Close"].resample('ME').last().pct_change()
            df= pd.concat([stock_return, market_return], axis=1).dropna()
            df.columns=["stock_return", "market_return"]
            beta=df["stock_return"].cov(df["market_return"]) / df["market_return"].var()
            cost_of_equity=r_f + beta * equity_risk_premium
        discount_rate=cost_of_equity
        if stock.info.get('earningsGrowth') is not None and stock.info.get('earningsGrowth') > 0 and pd.notna(stock.info.get('earningsGrowth')):
            growth_rate=stock.info.get('earningsGrowth')
        elif stock.info.get('revenueGrowth') is not None and stock.info.get('revenueGrowth') > 0 and pd.notna(stock.info.get('revenueGrowth')):
            growth_rate=stock.info.get('revenueGrowth')
        else: growth_rate=0.08
        growth_rate = min(growth_rate, 0.12)
        terminal_growth_rate = 0.025
        projection_years=5
        projected_fcfe=[]
        pv=[]
        for i in range(1, projection_years + 1):
            projected_fcfe.append(free_cash_flow_to_equity * (1 + growth_rate) ** i)
            pv.append(projected_fcfe[i - 1] / (1 + discount_rate) ** i)
        tv= projected_fcfe[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
        pv.append(tv / (1 + discount_rate) ** projection_years)
        equity_value=sum(pv)
        shares_outstanding = stock.info.get("sharesOutstanding")
        if shares_outstanding is not None and shares_outstanding > 0 and pd.notna(shares_outstanding):
            intrinsic_value_per_share = equity_value / shares_outstanding
        if stock.info.get("currentPrice") is not None and pd.notna(stock.info.get("currentPrice")):
            market_price=stock.info.get("currentPrice")
        elif stock.fast_info.get("lastPrice") is not None and pd.notna(stock.fast_info.get("lastPrice")):
            market_price=stock.fast_info.get("lastPrice")
        else: market_price=stock.history(period="1d")['Close'].iloc[-1]
        if intrinsic_value_per_share is not None and market_price is not None and market_price > 0:
            dcf_valuation= ((intrinsic_value_per_share- market_price) / market_price) *100
        return dcf_valuation
    elif free_cash_flow_to_firm is not None:
        equity_weight = None
        debt_weight = None
        cost_of_debt=int_expense / balance_sheet.loc['Total Debt'].iloc[0]
        if cost_of_debt is not None and cost_of_debt > 0 and pd.notna(cost_of_debt):
            tax_rate = financials.loc['Tax Provision'].iloc[0] / financials.loc['Pretax Income'].iloc[0]
            if tax_rate < 0 or tax_rate > 1:
                tax_rate = 0.21
            after_tax_cost_of_debt=cost_of_debt * (1 - tax_rate)
        total_debt=balance_sheet.loc['Total Debt'].iloc[0]
        market_capital=stock.info.get('marketCap')
        if (market_capital + total_debt) > 0:
            equity_weight= market_capital / (market_capital + total_debt)
            debt_weight= total_debt / (market_capital + total_debt)
        tnx = yf.Ticker("^TNX")
        if tnx.fast_info['last_price'] / 100 is not None and tnx.fast_info['last_price'] / 100 > 0 and pd.notna(tnx.fast_info['last_price'] / 100):
            r_f=tnx.fast_info['last_price'] / 100
        else: r_f=0.0425
        equity_risk_premium=0.045
        beta=stock.info.get('beta')
        if beta is not None and pd.notna(beta):
            cost_of_equity=r_f + beta * equity_risk_premium
        else:
            sp500=yf.Ticker("^GSPC")
            market_return=sp500.history(period="5y")["Close"].resample('ME').last().pct_change()
            stock_return=stock.history(period="5y")["Close"].resample('ME').last().pct_change()
            df= pd.concat([stock_return, market_return], axis=1).dropna()
            df.columns=["stock_return", "market_return"]
            beta=df["stock_return"].cov(df["market_return"]) / df["market_return"].var()
            cost_of_equity=r_f + beta * equity_risk_premium
        wacc= (equity_weight * cost_of_equity) + (debt_weight * after_tax_cost_of_debt)
        discount_rate=wacc
        if stock.info.get('earningsGrowth') is not None and stock.info.get('earningsGrowth') > 0 and pd.notna(stock.info.get('earningsGrowth')):
            growth_rate=stock.info.get('earningsGrowth')
        elif stock.info.get('revenueGrowth') is not None and stock.info.get('revenueGrowth') > 0 and pd.notna(stock.info.get('revenueGrowth')):
            growth_rate=stock.info.get('revenueGrowth')
        else: growth_rate=0.08
        growth_rate = min(growth_rate, 0.12)
        terminal_growth_rate = 0.025
        projection_years=5
        projected_fcff=[]
        pv=[]
        for i in range(1, projection_years + 1):
            projected_fcff.append(free_cash_flow_to_firm * (1 + growth_rate) ** i)
            pv.append(projected_fcff[i - 1] / (1 + discount_rate) ** i)
        tv= projected_fcff[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
        pv.append(tv / (1 + discount_rate) ** projection_years)
        enterprise_value=sum(pv)
        equity_value= enterprise_value - balance_sheet.loc['Total Debt'].iloc[0] + balance_sheet.loc['Cash And Cash Equivalents'].iloc[0]
        shares_outstanding = stock.info.get("sharesOutstanding")
        if shares_outstanding is not None and shares_outstanding > 0 and pd.notna(shares_outstanding):
            intrinsic_value_per_share = equity_value / shares_outstanding
        if stock.info.get("currentPrice") is not None and pd.notna(stock.info.get("currentPrice")):
            market_price=stock.info.get("currentPrice")
        elif stock.fast_info.get("lastPrice") is not None and pd.notna(stock.fast_info.get("lastPrice")):
            market_price=stock.fast_info.get("lastPrice")
        else:
            market_price=stock.history(period="1d")['Close'].iloc[-1]
        if intrinsic_value_per_share is not None and market_price is not None and market_price > 0:
            dcf_valuation= ((intrinsic_value_per_share- market_price) / market_price) *100
        return dcf_valuation
    else: return None

def asset_quality_calculator(stock, cashflow,financials, balance_sheet):
    try:
        cy_revenue=financials.loc['Total Revenue'].iloc[0]
        py_revenue=financials.loc['Total Revenue'].iloc[1]
    except (KeyError, IndexError):
        cy_revenue=None
        py_revenue=None
    try:
        cy_Receivables=balance_sheet.loc['Receivables'].iloc[0]
        py_Receivables=balance_sheet.loc['Receivables'].iloc[1]
    except (KeyError, IndexError):
        cy_Receivables=None
        py_Receivables=None
    try:
        cy_inventory = balance_sheet.loc['Inventory'].iloc[0]
        py_inventory = balance_sheet.loc['Inventory'].iloc[1]
    except (KeyError, IndexError):
        cy_inventory = None
        py_inventory = None
    try:
        total_assets=balance_sheet.loc['Total Assets'].iloc[0]
    except (KeyError, IndexError):
        total_assets=None
    try:
        net_income=financials.loc['Net Income'].iloc[0]
    except (KeyError, IndexError):
        net_income=None
    try:
        EBIT=financials.loc['EBIT'].iloc[0]
        tax_expense=financials.loc['Tax Provision'].iloc[0]
        pretax_income=financials.loc['Pretax Income'].iloc[0]
        nopat=EBIT * (1 - (tax_expense / pretax_income))
    except (KeyError, IndexError, ZeroDivisionError, TypeError):
        nopat=None
    try:
        invested_capital=balance_sheet.loc['Total Debt'].iloc[0] + balance_sheet.loc['Stockholders Equity'].iloc[0] - balance_sheet.loc['Cash And Cash Equivalents'].iloc[0]
    except (KeyError, IndexError):
        invested_capital=None
    if pd.notna(net_income) and pd.notna(total_assets):
        roa=float(net_income / total_assets)
    elif stock.info.get('returnOnAssets') is not None and pd.notna(stock.info.get('returnOnAssets')):
        roa= stock.info.get('returnOnAssets')
    else: roa= None
    if pd.notna(nopat) and pd.notna(invested_capital):
        roic= float(nopat / invested_capital)
    else: roic= None
    if pd.notna(cy_revenue)  and pd.notna(total_assets):
        asset_turnover= float(cy_revenue / total_assets)
    else: asset_turnover= None
    if pd.notna(cy_Receivables) and pd.notna(cy_revenue) and pd.notna(py_Receivables) and pd.notna(py_revenue) and cy_revenue > 0 and py_revenue > 0:
        receivable_stress= float(((cy_Receivables-py_Receivables)/py_Receivables) - ((cy_revenue-py_revenue)/py_revenue))
    else: receivable_stress= None
    if pd.notna(cy_inventory) and pd.notna(cy_revenue) and pd.notna(py_inventory) and pd.notna(py_revenue) and cy_revenue > 0 and py_revenue > 0:
        inventory_stress= float(((cy_inventory-py_inventory)/py_inventory) - ((cy_revenue-py_revenue)/py_revenue))
    else: inventory_stress= None
    return roa, roic, asset_turnover, receivable_stress, inventory_stress

def fcf_yield_calculator(stock, cashflow):
    try:
        if 'Free Cash Flow' in cashflow.index:
            free_cash_flow = float(cashflow.loc['Free Cash Flow'].iloc[0])
        else:
            free_cash_flow = float(cashflow.loc['Operating Cash Flow'].iloc[0] - abs(cashflow.loc['Capital Expenditure'].iloc[0]))
    except:
        free_cash_flow=None
    if stock.info.get('marketCap') is not None and stock.info.get('marketCap') > 0 and pd.notna(stock.info.get('marketCap')):
        market_cap=float(stock.info.get('marketCap'))
    else: market_cap=float(stock.info.get('enterpriseValue') - stock.info.get('totalDebt') + stock.info.get('cash'))
    if market_cap is not None and free_cash_flow is not None and pd.notna(market_cap) and pd.notna(free_cash_flow):
        fcf_yield=float(free_cash_flow / market_cap)
    else: fcf_yield=None
    return fcf_yield
def Debt_to_Equity_calculator(stock, balance_sheet):
    try:
        total_debt=balance_sheet.loc['Total Debt'].iloc[0]
    except:
        total_debt=None
    try:
        stockholders_equity=balance_sheet.loc['Stockholders Equity'].iloc[0]
    except:
        stockholders_equity=None
    if total_debt is not None and stockholders_equity is not None and stockholders_equity > 0 and pd.notna(total_debt) and pd.notna(stockholders_equity):
        debt_to_equity=float(total_debt / stockholders_equity)
    elif stock.info.get('debtToEquity') is not None and pd.notna(stock.info.get('debtToEquity')):
        debt_to_equity=float(stock.info.get('debtToEquity'))
    else: debt_to_equity=None
    return debt_to_equity
def interest_coverage_calculator(stock, financials):
    try:
        ebit=financials.loc['EBIT'].iloc[0]
    except:
        ebit=None
    try:
        interest_expense=abs(financials.loc['Interest Expense'].iloc[0])
    except:
        interest_expense=None
    if ebit is not None and interest_expense is not None and interest_expense > 0 and pd.notna(ebit) and pd.notna(interest_expense):
        interest_coverage=ebit / interest_expense
    elif stock.info.get('interestCoverage') is not None and pd.notna(stock.info.get('interestCoverage')):
        interest_coverage=stock.info.get('interestCoverage')
    else: interest_coverage=None
    return interest_coverage

if peers is not None and len(peers) > 0:
    peer_over=0
    peer_under=0
    peer_fair=0
    peer = pd.DataFrame(columns=['Ticker', 'P/E Ratio', 'P/B Ratio', 'Forward P/E Ratio', 'PEG Ratio', 'EV/EBITDA', 'EV/Sales', 'P/FCF'])
    equity= pd.DataFrame(columns=['Ticker', 'DCF Valuation (%)', 'ROA', 'ROIC', 'Asset Turnover', 'Receivable Stress', 'Inventory Stress', 'FCF Yield', 'Debt to Equity Ratio', 'Interest Coverage'])
    peer_equity = pd.DataFrame(columns=['Ticker', 'P/E Ratio', 'P/B Ratio', 'Forward P/E Ratio', 'PEG Ratio', 'EV/EBITDA', 'EV/Sales', 'P/FCF'])
    equity_pe_ratio=pe_ratio_calculator(stk, fin)
    equity_pb_ratio=pb_ratio_calculator(stk, bs)
    equity_forward_pe_ratio=forward_pe_ratio_calculator(stk)
    equity_peg_ratio=peg_ratio_calculator(stk)
    equity_ev_to_ebitda=ev_to_ebitda_calculator(stk, fin)
    equity_ev_sales=ev_sales_calculator(stk, fin)
    equity_p_fcf=p_fcf_calculator(stk, cf)
    new_row= {
        'Ticker': stk.ticker,
        'P/E Ratio': equity_pe_ratio,
        'P/B Ratio': equity_pb_ratio,
        'Forward P/E Ratio': equity_forward_pe_ratio,
        'PEG Ratio': equity_peg_ratio,
        'EV/EBITDA': equity_ev_to_ebitda,
        'EV/Sales': equity_ev_sales,
        'P/FCF': equity_p_fcf
    }
    peer_equity = pd.concat([peer_equity, pd.DataFrame([new_row])], ignore_index=True)
    for ticker in peers:
        peer_info = yf.Ticker(ticker)
        peer_bs = peer_info.balance_sheet
        peer_fin = peer_info.financials
        peer_cf = peer_info.cashflow
        peer_pe_ratio=pe_ratio_calculator(peer_info, peer_fin)
        peer_pb_ratio=pb_ratio_calculator(peer_info, peer_bs)
        peer_forward_pe_ratio=forward_pe_ratio_calculator(peer_info)
        peer_peg_ratio = peg_ratio_calculator(peer_info)
        peer_ev_to_ebitda=ev_to_ebitda_calculator(peer_info, peer_fin)
        peer_ev_sales=ev_sales_calculator(peer_info, peer_fin)
        peer_p_fcf=p_fcf_calculator(peer_info, peer_cf)
        new_row = {
            'Ticker': ticker,
            'P/E Ratio': peer_pe_ratio,
            'P/B Ratio': peer_pb_ratio,
            'Forward P/E Ratio': peer_forward_pe_ratio,
            'PEG Ratio': peer_peg_ratio,
            'EV/EBITDA': peer_ev_to_ebitda,
            'EV/Sales': peer_ev_sales,
            'P/FCF': peer_p_fcf
        }
        peer = pd.concat([peer, pd.DataFrame([new_row])], ignore_index=True)
    equity_dcf = discounted_cash_flow_calculator(stk, cf, fin, bs)
    equity_roa, equity_roic, equity_asset_turnover, equity_receivable_stress, equity_inventory_stress = asset_quality_calculator(stk, cf, fin, bs)
    equity_fcf_yield = fcf_yield_calculator(stk, cf)
    equity_debt_to_equity = Debt_to_Equity_calculator(stk, bs)
    equity_interest_coverage = interest_coverage_calculator(stk, fin)
    new_row = {
        'Ticker': stk.ticker,
        'DCF Valuation (%)': equity_dcf,
        'ROA': equity_roa,
        'ROIC': equity_roic,
        'Asset Turnover': equity_asset_turnover,
        'Receivable Stress': equity_receivable_stress,
        'Inventory Stress': equity_inventory_stress,
        'FCF Yield': equity_fcf_yield,
        'Debt to Equity Ratio': equity_debt_to_equity,
        'Interest Coverage': equity_interest_coverage
    }
    equity = pd.concat([equity, pd.DataFrame([new_row])], ignore_index=True)
    equity=equity.dropna(subset=['DCF Valuation (%)', 'ROA', 'ROIC', 'Asset Turnover', 'Receivable Stress', 'Inventory Stress', 'FCF Yield', 'Debt to Equity Ratio', 'Interest Coverage'], how='all')
    peer=peer.dropna(subset=['P/E Ratio', 'P/B Ratio', 'Forward P/E Ratio', 'PEG Ratio', 'EV/EBITDA', 'EV/Sales', 'P/FCF'], how='all')
    pe_median= peer['P/E Ratio'].median()
    pb_median = peer['P/B Ratio'].median()
    forward_pe_median = peer['Forward P/E Ratio'].median()
    peg_median = peer['PEG Ratio'].median()
    ev_ebitda_median = peer['EV/EBITDA'].median()
    ev_sales_median = peer['EV/Sales'].median()
    p_fcf_median = peer['P/FCF'].median()
    weights=industry_weight(stk)
    peer_pe = peer_equity['P/E Ratio'].iloc[0]
    if pd.notna(peer_pe) and pe_median is not None and pd.notna(pe_median):
        if peer_equity['P/E Ratio'].iloc[0] > pe_median * 1.05:
            peer_over += weights['P/E Ratio']
        elif peer_equity['P/E Ratio'].iloc[0] < pe_median * 0.95:
            peer_under += weights['P/E Ratio']
        else: peer_fair += weights['P/E Ratio']
    peer_pb = peer_equity['P/B Ratio'].iloc[0]
    if pd.notna(peer_pb) and pb_median is not None and pd.notna(pb_median):
        if peer_equity['P/B Ratio'].iloc[0] > pb_median * 1.05:
            peer_over += weights['P/B Ratio']
        elif peer_equity['P/B Ratio'].iloc[0] < pb_median * 0.95:
            peer_under += weights['P/B Ratio']
        else: peer_fair += weights['P/B Ratio']
    peer_forward_pe = peer_equity['Forward P/E Ratio'].iloc[0]
    if pd.notna(peer_forward_pe) and forward_pe_median is not None and pd.notna(forward_pe_median):   
        if peer_equity['Forward P/E Ratio'].iloc[0] > forward_pe_median * 1.05:
            peer_over += weights['Forward P/E Ratio']
        elif peer_equity['Forward P/E Ratio'].iloc[0] < forward_pe_median * 0.95:
            peer_under += weights['Forward P/E Ratio']
        else: peer_fair += weights['Forward P/E Ratio']
    peer_peg = peer_equity['PEG Ratio'].iloc[0]
    if pd.notna(peer_peg) and peg_median is not None and pd.notna(peg_median):
        if peer_equity['PEG Ratio'].iloc[0] > peg_median * 1.05:
            peer_over += weights['PEG Ratio']
        elif peer_equity['PEG Ratio'].iloc[0] < peg_median * 0.95:
            peer_under += weights['PEG Ratio']
        else: peer_fair += weights['PEG Ratio']
    peer_ev_ebitda = peer_equity['EV/EBITDA'].iloc[0]
    if pd.notna(peer_ev_ebitda) and ev_ebitda_median is not None and pd.notna(ev_ebitda_median):
        if peer_equity['EV/EBITDA'].iloc[0] > ev_ebitda_median * 1.05:
            peer_over += weights['EV/EBITDA']
        elif peer_equity['EV/EBITDA'].iloc[0] < ev_ebitda_median * 0.95:
            peer_under += weights['EV/EBITDA']
        else: peer_fair += weights['EV/EBITDA']
    peer_ev_sales = peer_equity['EV/Sales'].iloc[0]
    if pd.notna(peer_ev_sales) and ev_sales_median is not None and pd.notna(ev_sales_median):
        if peer_equity['EV/Sales'].iloc[0] > ev_sales_median * 1.05:
            peer_over += weights['EV/Sales']
        elif peer_equity['EV/Sales'].iloc[0] < ev_sales_median * 0.95:
            peer_under += weights['EV/Sales']
        else: peer_fair += weights['EV/Sales']
    peer_p_fcf = peer_equity['P/FCF'].iloc[0]
    if pd.notna(peer_p_fcf) and p_fcf_median is not None and pd.notna(p_fcf_median):
        if peer_equity['P/FCF'].iloc[0] > p_fcf_median * 1.05:
            peer_over += weights['P/FCF']
        elif peer_equity['P/FCF'].iloc[0] < p_fcf_median * 0.95:
            peer_under += weights['P/FCF']
        else: peer_fair += weights['P/FCF']
    quality_good=0
    quality_bad=0
    quality_neutral=0
    quality_weights=industry_quality_weight(stk)
    if pd.notna(equity['ROA'].iloc[0]):
        if equity['ROA'].iloc[0] >= 0.10:
            quality_good += quality_weights['ROA']
        elif equity['ROA'].iloc[0] < 0.05:
            quality_bad += quality_weights['ROA']
        else: quality_neutral += quality_weights['ROA']

    if pd.notna(equity['ROIC'].iloc[0]):
        if equity['ROIC'].iloc[0] >= 0.15:
            quality_good += quality_weights['ROIC']
        elif equity['ROIC'].iloc[0] < 0.08:
            quality_bad += quality_weights['ROIC']
        else: quality_neutral += quality_weights['ROIC']

    if pd.notna(equity['Asset Turnover'].iloc[0]):
        if equity['Asset Turnover'].iloc[0] >= 1:
            quality_good += quality_weights['Asset Turnover']
        elif equity['Asset Turnover'].iloc[0] < 0.5:
            quality_bad += quality_weights['Asset Turnover']
        else: quality_neutral += quality_weights['Asset Turnover']

    if pd.notna(equity['Receivable Stress'].iloc[0]):
        if equity['Receivable Stress'].iloc[0] <= 0.1:
            quality_good += quality_weights['Receivable Stress']
        elif equity['Receivable Stress'].iloc[0] > 0.2:
            quality_bad += quality_weights['Receivable Stress']
        else: quality_neutral += quality_weights['Receivable Stress']

    if pd.notna(equity['Inventory Stress'].iloc[0]):
        if equity['Inventory Stress'].iloc[0] <= 0.1:
            quality_good += quality_weights['Inventory Stress']
        elif equity['Inventory Stress'].iloc[0] > 0.2:
            quality_bad += quality_weights['Inventory Stress']
        else: quality_neutral += quality_weights['Inventory Stress']

    if pd.notna(equity['FCF Yield'].iloc[0]):
        if equity['FCF Yield'].iloc[0] >= 0.05:
            quality_good += quality_weights['FCF Yield']
        elif equity['FCF Yield'].iloc[0] < 0.02:
            quality_bad += quality_weights['FCF Yield']
        else: quality_neutral += quality_weights['FCF Yield']

    if pd.notna(equity['Debt to Equity Ratio'].iloc[0]):
        if equity['Debt to Equity Ratio'].iloc[0] <= 0.5:
            quality_good += quality_weights['Debt to Equity Ratio']
        elif equity['Debt to Equity Ratio'].iloc[0] > 1.5:
            quality_bad += quality_weights['Debt to Equity Ratio']
        else: quality_neutral += quality_weights['Debt to Equity Ratio']

    if pd.notna(equity['Interest Coverage'].iloc[0]):
        if equity['Interest Coverage'].iloc[0] >= 5:
            quality_good += quality_weights['Interest Coverage']
        elif equity['Interest Coverage'].iloc[0] < 2:
            quality_bad += quality_weights['Interest Coverage']
        else: quality_neutral += quality_weights['Interest Coverage']
    quality_total = quality_good + quality_bad + quality_neutral
    peer_total = peer_under + peer_over + peer_fair
    quality_score = (quality_good - quality_bad) / quality_total if quality_total != 0 else None
    peer_score = (peer_under - peer_over) / peer_total if peer_total != 0 else None
    dcf_score = max(-1, min(1, equity_dcf / 30)) if equity_dcf is not None else None

    if peer_score is None or quality_score is None or dcf_score is None:
        print(f"{stk.ticker}: Insufficient data for full interpretation.")

    else:
        final_score = 0.4 * peer_score + 0.2 * quality_score + 0.4 * dcf_score

        if equity_dcf >= 0:
            dcf_text = f"{equity_dcf:.2f}% undervalued by DCF"
        else:
            dcf_text = f"{abs(equity_dcf):.2f}% overvalued by DCF"

        if peer_score >= 0.50:
            peer_label = "Strongly Undervalued vs Peers"
        elif peer_score >= 0.15:
            peer_label = "Undervalued vs Peers"
        elif peer_score > -0.15:
            peer_label = "Fairly Valued vs Peers"
        elif peer_score > -0.50:
            peer_label = "Overvalued vs Peers"
        else:
            peer_label = "Strongly Overvalued vs Peers"

        if quality_score >= 0.50:
            quality_label = "Strong Quality"
        elif quality_score >= 0.15:
            quality_label = "Good Quality"
        elif quality_score > -0.15:
            quality_label = "Average Quality"
        elif quality_score > -0.50:
            quality_label = "Weak Quality"
        else:
            quality_label = "Very Weak Quality"

        if equity_dcf >= 30:
            dcf_label = "Strongly Undervalued by DCF"
        elif equity_dcf >= 15:
            dcf_label = "Undervalued by DCF"
        elif equity_dcf > -15:
            dcf_label = "Fairly Valued by DCF"
        elif equity_dcf > -30:
            dcf_label = "Overvalued by DCF"
        else:
            dcf_label = "Strongly Overvalued by DCF"

        if peer_score >= 0.15 and dcf_score >= 0.15 and quality_score >= 0.15:
            if peer_score >= 0.50 and dcf_score >= 0.50 and quality_score >= 0.50:
                final_label = "High Conviction Undervalued"
                final_message = "The stock looks cheap relative to peers, business quality is strong, and DCF also supports strong upside."
            else:
                final_label = "Undervalued"
                final_message = "The stock looks attractively valued with supportive peer valuation, good quality, and positive DCF upside."

        elif peer_score <= -0.15 and dcf_score <= -0.15 and quality_score >= 0.15:
            final_label = "Premium Quality, Rich Valuation"
            final_message = "The business quality is strong, but the stock is trading at a premium relative to peers and DCF does not support enough upside."

        elif peer_score >= 0.15 and dcf_score >= 0.15 and quality_score <= -0.15:
            final_label = "Possible Value Trap"
            final_message = "The stock looks cheap on valuation, but business quality is weak. This may be a value trap."

        elif peer_score <= -0.15 and dcf_score <= -0.15 and quality_score <= -0.15:
            if peer_score <= -0.50 and dcf_score <= -0.50 and quality_score <= -0.50:
                final_label = "Strong Overvaluation Warning"
                final_message = "The stock looks expensive, business quality is weak, and DCF also points to significant downside."
            else:
                final_label = "Overvalued"
                final_message = "The stock appears expensive relative to peers and DCF, while business quality is also weak."

        elif peer_score >= 0.15 and dcf_score <= -0.15:
            if quality_score >= 0.15:
                final_label = "Mixed Signals - Premium vs DCF Conflict"
                final_message = "Peer valuation suggests upside, but DCF suggests downside. Business quality is supportive, so the case depends heavily on assumptions."
            else:
                final_label = "Mixed Signals - Weak Support"
                final_message = "Peer valuation and DCF are in conflict, and business quality is not strong enough to create confidence."

        elif peer_score <= -0.15 and dcf_score >= 0.15:
            if quality_score >= 0.15:
                final_label = "Premium Multiple but DCF-Supported"
                final_message = "The stock looks expensive relative to peers, but DCF still indicates upside and business quality is strong."
            else:
                final_label = "Mixed Signals"
                final_message = "DCF indicates upside, but peer valuation is rich and business quality is not strong."

        else:
            if final_score >= 0.15:
                final_label = "Mild Positive / Mixed"
                final_message = "The stock has somewhat favorable signals overall, but not enough to call it clearly undervalued."
            elif final_score <= -0.15:
                final_label = "Mild Negative / Mixed"
                final_message = "The stock has somewhat unfavorable signals overall, but not enough to call it clearly overvalued."
            else:
                final_label = "Fair / Inconclusive"
                final_message = "The stock appears roughly fairly valued or has mixed signals without a clear edge."

        print(f"\n----- {stk.ticker} VALUATION SUMMARY -----")
        print(f"Peer View       : {peer_label}")
        print(f"Quality View    : {quality_label}")
        print(f"DCF View        : {dcf_label} ({dcf_text})")
        print(f"Peer Score      : {peer_score:.2f}")
        print(f"Quality Score   : {quality_score:.2f}")
        print(f"DCF Score       : {dcf_score:.2f}")
        print(f"Final Score     : {final_score:.2f}")
        print(f"Final Verdict   : {final_label}")
        print(f"Interpretation  : {final_message}")


else:
    equity= pd.DataFrame(columns=['Ticker', 'DCF Valuation (%)', 'ROA', 'ROIC', 'Asset Turnover', 'Receivable Stress', 'Inventory Stress', 'FCF Yield', 'Debt to Equity Ratio', 'Interest Coverage'])
    equity_dcf = discounted_cash_flow_calculator(stk, cf, fin, bs)
    equity_roa, equity_roic, equity_asset_turnover, equity_receivable_stress, equity_inventory_stress = asset_quality_calculator(stk, cf, fin, bs)
    equity_fcf_yield = fcf_yield_calculator(stk, cf)
    equity_debt_to_equity = Debt_to_Equity_calculator(stk, bs)
    equity_interest_coverage = interest_coverage_calculator(stk, fin)
    new_row = {
        'Ticker': stk.ticker,
        'DCF Valuation (%)': equity_dcf,
        'ROA': equity_roa,
        'ROIC': equity_roic,
        'Asset Turnover': equity_asset_turnover,
        'Receivable Stress': equity_receivable_stress,
        'Inventory Stress': equity_inventory_stress,
        'FCF Yield': equity_fcf_yield,
        'Debt to Equity Ratio': equity_debt_to_equity,
        'Interest Coverage': equity_interest_coverage
    }
    equity = pd.concat([equity, pd.DataFrame([new_row])], ignore_index=True)
    equity=equity.dropna(subset=['DCF Valuation (%)', 'ROA', 'ROIC', 'Asset Turnover', 'Receivable Stress', 'Inventory Stress', 'FCF Yield', 'Debt to Equity Ratio', 'Interest Coverage'], how='all')
    quality_good=0
    quality_bad=0
    quality_neutral=0
    quality_weights=industry_quality_weight(stk)
    if pd.notna(equity['ROA'].iloc[0]):
        if equity['ROA'].iloc[0] >= 0.10:
            quality_good += quality_weights['ROA']
        elif equity['ROA'].iloc[0] < 0.05:
            quality_bad += quality_weights['ROA']
        else: quality_neutral += quality_weights['ROA']

    if pd.notna(equity['ROIC'].iloc[0]):
        if equity['ROIC'].iloc[0] >= 0.15:
            quality_good += quality_weights['ROIC']
        elif equity['ROIC'].iloc[0] < 0.08:
            quality_bad += quality_weights['ROIC']
        else: quality_neutral += quality_weights['ROIC']

    if pd.notna(equity['Asset Turnover'].iloc[0]):
        if equity['Asset Turnover'].iloc[0] >= 1:
            quality_good += quality_weights['Asset Turnover']
        elif equity['Asset Turnover'].iloc[0] < 0.5:
            quality_bad += quality_weights['Asset Turnover']
        else: quality_neutral += quality_weights['Asset Turnover']

    if pd.notna(equity['Receivable Stress'].iloc[0]):
        if equity['Receivable Stress'].iloc[0] <= 0.1:
            quality_good += quality_weights['Receivable Stress']
        elif equity['Receivable Stress'].iloc[0] > 0.2:
            quality_bad += quality_weights['Receivable Stress']
        else: quality_neutral += quality_weights['Receivable Stress']

    if pd.notna(equity['Inventory Stress'].iloc[0]):
        if equity['Inventory Stress'].iloc[0] <= 0.1:
            quality_good += quality_weights['Inventory Stress']
        elif equity['Inventory Stress'].iloc[0] > 0.2:
            quality_bad += quality_weights['Inventory Stress']
        else: quality_neutral += quality_weights['Inventory Stress']

    if pd.notna(equity['FCF Yield'].iloc[0]):
        if equity['FCF Yield'].iloc[0] >= 0.05:
            quality_good += quality_weights['FCF Yield']
        elif equity['FCF Yield'].iloc[0] < 0.02:
            quality_bad += quality_weights['FCF Yield']
        else: quality_neutral += quality_weights['FCF Yield']

    if pd.notna(equity['Debt to Equity Ratio'].iloc[0]):
        if equity['Debt to Equity Ratio'].iloc[0] <= 0.5:
            quality_good += quality_weights['Debt to Equity Ratio']
        elif equity['Debt to Equity Ratio'].iloc[0] > 1.5:
            quality_bad += quality_weights['Debt to Equity Ratio']
        else: quality_neutral += quality_weights['Debt to Equity Ratio']

    if pd.notna(equity['Interest Coverage'].iloc[0]):
        if equity['Interest Coverage'].iloc[0] >= 5:
            quality_good += quality_weights['Interest Coverage']
        elif equity['Interest Coverage'].iloc[0] < 2:
            quality_bad += quality_weights['Interest Coverage']
        else: quality_neutral += quality_weights['Interest Coverage']
    quality_total = quality_good + quality_bad + quality_neutral
    quality_score = (quality_good - quality_bad) / quality_total if quality_total != 0 else None
    dcf_score = max(-1, min(1, equity_dcf / 30)) if equity_dcf is not None else None
    if quality_score is not None:
        if quality_score >= 0.50:
            quality_label = "Strong Quality"
        elif quality_score >= 0.15:
            quality_label = "Good Quality"
        elif quality_score > -0.15:
            quality_label = "Average Quality"
        elif quality_score > -0.50:
            quality_label = "Weak Quality"
        else:
            quality_label = "Very Weak Quality"
    else:
        quality_label = "Insufficient Data"
    if equity_dcf is not None:
        if equity_dcf >= 30:
            dcf_label = "Strongly Undervalued by DCF"
        elif equity_dcf >= 15:
            dcf_label = "Undervalued by DCF"
        elif equity_dcf > -15:
            dcf_label = "Fairly Valued by DCF"
        elif equity_dcf > -30:
            dcf_label = "Overvalued by DCF"
        else:
            dcf_label = "Strongly Overvalued by DCF"
    else:
        dcf_label = "Insufficient Data" 
    if quality_score is not None and dcf_score is not None:
        non_peer_score = (0.4 * quality_score) + (0.6 * dcf_score)
    else:
        non_peer_score = None
    if non_peer_score is None:
        non_peer_label = "Insufficient Data"
        non_peer_message = "Not enough non-peer data to form a conclusion."

    elif equity_dcf >= 15 and quality_score >= 0.15:
        if equity_dcf >= 30 and quality_score >= 0.50:
            non_peer_label = "High Conviction Undervalued"
            non_peer_message = "DCF shows strong upside and the business quality is strong."
        else:
            non_peer_label = "Undervalued"
            non_peer_message = "DCF suggests upside and the business quality is supportive."

    elif equity_dcf >= 15 and quality_score < -0.15:
        non_peer_label = "Undervalued but Weak Quality"
        non_peer_message = "DCF suggests upside, but weak business quality increases risk."

    elif equity_dcf <= -15 and quality_score >= 0.15:
        non_peer_label = "Premium Quality, Rich Valuation"
        non_peer_message = "The business quality is good, but DCF suggests the stock is priced above intrinsic value."

    elif equity_dcf <= -15 and quality_score < -0.15:
        if equity_dcf <= -30 and quality_score <= -0.50:
            non_peer_label = "Strong Overvaluation Warning"
            non_peer_message = "DCF suggests significant downside and business quality is weak."
        else:
            non_peer_label = "Overvalued"
            non_peer_message = "DCF suggests downside and business quality is not supportive."

    else:
        if non_peer_score >= 0.15:
            non_peer_label = "Mild Positive / Mixed"
            non_peer_message = "The non-peer signals are somewhat favorable, but not strongly enough."
        elif non_peer_score <= -0.15:
            non_peer_label = "Mild Negative / Mixed"
            non_peer_message = "The non-peer signals are somewhat unfavorable, but not strongly enough."
        else:
            non_peer_label = "Fair / Inconclusive"
            non_peer_message = "DCF and quality together do not give a strong directional signal."   
    if equity_dcf is not None:
        if equity_dcf >= 0:
            dcf_text = f"{equity_dcf:.2f}% undervalued by DCF"
        else:
            dcf_text = f"{abs(equity_dcf):.2f}% overvalued by DCF"
    else:
        dcf_text = "DCF unavailable"

    print(f"\n----- {stk.ticker} NON-PEER SUMMARY -----")
    print(f"Quality View    : {quality_label}")
    print(f"DCF View        : {dcf_label} ({dcf_text})")
    print(f"Quality Score   : {quality_score:.2f}" if quality_score is not None else "Quality Score   : None")
    print(f"DCF Score       : {dcf_score:.2f}" if dcf_score is not None else "DCF Score       : None")
    print(f"Non-Peer Score  : {non_peer_score:.2f}" if non_peer_score is not None else "Non-Peer Score  : None")
    print(f"Final Verdict   : {non_peer_label}")
    print(f"Interpretation  : {non_peer_message}")    
print("\nWARNING: This model is a decision-support and screening tool, not a definitive valuation authority. Outputs depend on data quality, assumptions, and simplified rules, so results should always be cross-checked with company filings, earnings reports, industry context, and independent analysis before making any investment decision.")