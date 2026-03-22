from peer_allocator import peers, stk, bs, fin, cf
import yfinance as yf
import pandas as pd
import numpy as np
peers_ratio=[]

def pe_ratio_calculator(stock):
    try:
        try:
            market_price=stock.fast_info.get('lastPrice')
        except:
            market_price=stock.history(period="1d")['Close'].iloc[-1]
    except:
        market_price=None

    try: 
        earnings_per_share=fin.loc['Net Income Common Stock'].iloc[0] / stock.info.get('sharesOutstanding')
    except:
        earnings_per_share=None
    if market_price is not None and earnings_per_share is not None:
        pe_ratio=market_price / earnings_per_share
    elif stk.info.get('trailingPE') is not None:
        pe_ratio=stk.info.get('trailingPE')
    else:
        pe_ratio=None
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
    if market_price is not None and book_value_per_share is not None:
            pb_ratio=market_price / book_value_per_share
    elif stock.info.get('priceToBook') is not None:
        pb_ratio=stock.info.get('priceToBook')
    else:
        pb_ratio=None
    return pb_ratio

def forward_pe_ratio_calculator(stock):
    try:
        forward_pe_ratio=stock.info.get('forwardPE')
    except:
        forward_pe_ratio=None
    return forward_pe_ratio

def peg_ratio_calculator(stock):
    try:
        earnings_growth_rate=stock.info.get('earningsGrowth')   
    except:
        earnings_growth_rate=None
    try:
        pe_ratio=stock.info.get('trailingPE')
    except:
        pe_ratio=None
    if pe_ratio is not None and earnings_growth_rate is not None and earnings_growth_rate > 0:
        peg_ratio=pe_ratio / (earnings_growth_rate * 100)
    elif stock.info.get('pegRatio') is not None:
        peg_ratio=stock.info.get('pegRatio')
    else:                
        peg_ratio=None
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
    elif stock.info.get('enterpriseToEbitda') is not None:
        ev_to_ebitda=stock.info.get('enterpriseToEbitda')
    else:
        ev_to_ebitda=None
    return ev_to_ebitda

def ev_to_ebit_calculator(stock, financials):
    try:
        try:
            enterprise_value=stock.info.get('marketCap') + stock.info.get('totalDebt') - stock.info.get('cash')
        except:
            enterprise_value=stock.info.get('enterpriseValue')
        
    except:
        enterprise_value=None
    try:
        try:
            ebit=stock.info.get('ebit')
        except:
            ebit=financials.loc['Ebit'].iloc[0]
    except:
        ebit=None
    if enterprise_value is not None and ebit is not None and ebit > 0:
        ev_to_ebit=enterprise_value / ebit
    elif stock.info.get('enterpriseToEbit') is not None:
        ev_to_ebit=stock.info.get('enterpriseToEbit')
    else:
        ev_to_ebit=None
    return ev_to_ebit

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
    if enterprise_value is not None and sales is not None and sales > 0:
        ev_sales=enterprise_value / sales   
    elif stock.info.get('enterpriseToRevenue') is not None:
        ev_sales=stock.info.get('enterpriseToRevenue')  
    else:
        ev_sales=None
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
    if market_cap is not None and free_cash_flow is not None and free_cash_flow > 0:
        p_fcf=market_cap / free_cash_flow
    else:
        p_fcf=None
    return p_fcf

def discounted_cash_flow_calculator(stock, cashflow, financials, balance_sheet):
    int_expense=abs(financials.loc['Interest Expense'].iloc[0])
    if pd.isna(int_expense):
        int_expense=0
    issued_debt=cashflow.loc['Issuance Of Debt'].iloc[0]
    if pd.isna(issued_debt):
        issued_debt=0
    repayed_debt=abs(cashflow.loc['Repayment Of Debt'].iloc[0])
    if pd.isna(repayed_debt):
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
            free_cash_flow_to_firm=cashflow.loc['Operating Cash Flow'].iloc[0] + int_expense * (1 - tax_rate) - abs(cashflow.loc['Capital Expenditure'].iloc[0])
    if free_cash_flow_to_equity is not None:
        tnx = yf.Ticker("^TNX")
        if tnx.fast_info['last_price'] / 100 is not None and tnx.fast_info['last_price'] / 100 > 0:
            r_f=tnx.fast_info['last_price'] / 100
        else:
            r_f=0.0425
        equity_risk_premium=0.045
        beta=stock.info.get('beta')
        if beta is not None:
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
        if stock.info.get('earningsGrowth') is not None and stock.info.get('earningsGrowth') > 0:
            growth_rate=stock.info.get('earningsGrowth')
        elif stock.info.get('revenueGrowth') is not None and stock.info.get('revenueGrowth') > 0:
            growth_rate=stock.info.get('revenueGrowth')
        else:
            growth_rate=0.08
        if growth_rate <= 0.08:
            terminal_growth_rate = 0.02
        elif growth_rate <= 0.15:
            terminal_growth_rate = 0.03
        else:
            terminal_growth_rate = 0.04
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
        if shares_outstanding is not None and shares_outstanding > 0:
            intrinsic_value_per_share = equity_value / shares_outstanding
        if stock.info.get("currentPrice") is not None:
            market_price=stock.info.get("currentPrice")
        elif stock.fast_info.get("lastPrice") is not None:
            market_price=stock.fast_info.get("lastPrice")
        else:
            market_price=stock.history(period="1d")['Close'].iloc[-1]
        if intrinsic_value_per_share is not None and market_price is not None and market_price > 0:
            dcf_valuation= ((intrinsic_value_per_share- market_price) / market_price) *100
        return dcf_valuation
    elif free_cash_flow_to_firm is not None:
        cost_of_debt=int_expense / balance_sheet.loc['Total Debt'].iloc[0]
        if cost_of_debt is not None and cost_of_debt > 0:
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
        if tnx.fast_info['last_price'] / 100 is not None and tnx.fast_info['last_price'] / 100 > 0:
            r_f=tnx.fast_info['last_price'] / 100
        else:
            r_f=0.0425
        equity_risk_premium=0.045
        beta=stock.info.get('beta')
        if beta is not None:
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
        if stock.info.get('earningsGrowth') is not None and stock.info.get('earningsGrowth') > 0:
            growth_rate=stock.info.get('earningsGrowth')
        elif stock.info.get('revenueGrowth') is not None and stock.info.get('revenueGrowth') > 0:
            growth_rate=stock.info.get('revenueGrowth')
        else:
            growth_rate=0.08
        if growth_rate <= 0.08:
            terminal_growth_rate = 0.02 
        elif growth_rate <= 0.15:
            terminal_growth_rate = 0.03
        else:
            terminal_growth_rate = 0.04
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
        if shares_outstanding is not None and shares_outstanding > 0:
            intrinsic_value_per_share = equity_value / shares_outstanding
        if stock.info.get("currentPrice") is not None:
            market_price=stock.info.get("currentPrice")
        elif stock.fast_info.get("lastPrice") is not None:
            market_price=stock.fast_info.get("lastPrice")
        else:
            market_price=stock.history(period="1d")['Close'].iloc[-1]
        if intrinsic_value_per_share is not None and market_price is not None and market_price > 0:
            dcf_valuation= ((intrinsic_value_per_share- market_price) / market_price) *100
        return dcf_valuation
    else:
            return None