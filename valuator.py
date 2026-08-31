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
STANDARD_QUALITY_THRESHOLDS = {
    "ROA": (0.10, 0.05),
    "ROIC": (0.15, 0.08),
    "Asset Turnover": (1.0, 0.5),
    "Receivable Stress": (0.10, 0.20),
    "Inventory Stress": (0.10, 0.20),
    "FCF Yield": (0.05, 0.02),
    "Debt to Equity Ratio": (0.5, 1.5),
    "Interest Coverage": (5, 2)
}

QUALITY_THRESHOLD_PROFILES = {
    "standard": STANDARD_QUALITY_THRESHOLDS,
    "leverage_financial": {
        "ROA": (0.012, 0.006),
        "Debt to Equity Ratio": (2.0, 6.0),
        "Interest Coverage": (2.0, 1.0)
    },
    "capital_intensive": {
        "ROA": (0.03, 0.015),
        "ROIC": (0.08, 0.05),
        "Asset Turnover": (0.5, 0.25),
        "FCF Yield": (0.04, 0.015),
        "Debt to Equity Ratio": (1.5, 3.0),
        "Interest Coverage": (2.5, 1.5)
    },
    "cyclical_commodity": {
        "ROA": (0.08, 0.02),
        "ROIC": (0.12, 0.05),
        "Asset Turnover": (0.6, 0.3),
        "Inventory Stress": (0.15, 0.30),
        "FCF Yield": (0.06, 0.01),
        "Debt to Equity Ratio": (0.6, 1.5),
        "Interest Coverage": (4, 2)
    },
    "early_stage_burn": {
        "ROA": (0.0, -0.15),
        "ROIC": (0.0, -0.15),
        "Asset Turnover": (0.3, 0.1),
        "FCF Yield": (-0.05, -0.20),
        "Debt to Equity Ratio": (0.3, 1.0),
        "Interest Coverage": (3, 1)
    }
}

ARCHETYPE_QUALITY_PROFILE = {
    "Consumer Discretionary & Services": "standard",
    "Consumer Staples": "standard",
    "Industrials & Transportation": "standard",
    "Healthcare Profitable": "standard",
    "Semis & Hardware": "standard",
    "Software & Internet": "standard",
    "Media & Telecom": "standard",
    "Shell/No Meaningful Fundamentals": "standard",
    "Banks": "leverage_financial",
    "Diversified Financials": "capital_intensive",
    "REIT/Real Estate": "capital_intensive",
    "Utilities": "capital_intensive",
    "Energy": "cyclical_commodity",
    "Materials & Mining": "cyclical_commodity",
    "Biotech/Early-Stage Life Science": "early_stage_burn"
}

def resolve_quality_thresholds(archetype):
    profile_name = ARCHETYPE_QUALITY_PROFILE.get(archetype, "standard")
    profile = QUALITY_THRESHOLD_PROFILES.get(profile_name, STANDARD_QUALITY_THRESHOLDS)
    return {**STANDARD_QUALITY_THRESHOLDS, **profile}

def industry_quality_weight(stock):
    industry=stock.info.get('industry')
    weight_df = pd.read_excel('industry_quality_weights.xlsx')
    row = weight_df[weight_df['Industry'] == industry]
    if not row.empty:
        weights = {
            "ROA": row["ROA %"].iloc[0] / 100,
            "ROIC": row["ROIC %"].iloc[0] / 100,
            "Asset Turnover": row["Asset Turnover %"].iloc[0] / 100,
            "Receivable Stress": row["Receivable Stress %"].iloc[0] / 100,
            "Inventory Stress": row["Inventory Stress %"].iloc[0] / 100,
            "FCF Yield": row["FCF Yield %"].iloc[0] / 100,
            "Debt to Equity Ratio": row["Debt to Equity Ratio %"].iloc[0] / 100,
            "Interest Coverage": row["Interest Coverage %"].iloc[0] / 100
        }
        thresholds = resolve_quality_thresholds(row["Archetype"].iloc[0])
    else:
        weights = {
            "ROA": 2,
            "ROIC": 3,
            "Asset Turnover": 2,
            "Receivable Stress": 2,
            "Inventory Stress": 2,
            "FCF Yield": 2,
            "Debt to Equity Ratio": 2,
            "Interest Coverage": 2
        }
        thresholds = STANDARD_QUALITY_THRESHOLDS
    return weights, thresholds

def score_quality_metrics(equity_row, quality_weights, quality_thresholds):
    quality_good = 0
    quality_bad = 0
    quality_neutral = 0
    higher_is_better = {"ROA", "ROIC", "Asset Turnover", "FCF Yield", "Interest Coverage"}
    for metric in quality_thresholds:
        value = equity_row[metric].iloc[0]
        if not pd.notna(value):
            continue
        good_cutoff, bad_cutoff = quality_thresholds[metric]
        if metric in higher_is_better:
            if value >= good_cutoff:
                quality_good += quality_weights[metric]
            elif value < bad_cutoff:
                quality_bad += quality_weights[metric]
            else:
                quality_neutral += quality_weights[metric]
        else:
            if value <= good_cutoff:
                quality_good += quality_weights[metric]
            elif value > bad_cutoff:
                quality_bad += quality_weights[metric]
            else:
                quality_neutral += quality_weights[metric]
    return quality_good, quality_bad, quality_neutral


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

def average_period_growth(financials, row_label):
    try:
        series = financials.loc[row_label]
    except (KeyError, IndexError):
        return None
    growth_rates = []
    for i in range(len(series) - 1):
        current, prior = series.iloc[i], series.iloc[i + 1]
        if pd.notna(current) and pd.notna(prior) and prior > 0:
            growth_rates.append((current - prior) / prior)
    if len(growth_rates) < 2:
        return None
    return sum(growth_rates) / len(growth_rates)

def estimate_growth_rate(stock, financials):
    growth_rate = average_period_growth(financials, 'Total Revenue')
    if growth_rate is None or growth_rate <= 0:
        alt_growth_rate = average_period_growth(financials, 'Net Income Common Stockholders')
        if alt_growth_rate is None:
            alt_growth_rate = average_period_growth(financials, 'Net Income')
        if alt_growth_rate is not None and alt_growth_rate > 0:
            growth_rate = alt_growth_rate
    if growth_rate is None or growth_rate <= 0:
        if stock.info.get('earningsGrowth') is not None and stock.info.get('earningsGrowth') > 0 and pd.notna(stock.info.get('earningsGrowth')):
            growth_rate = stock.info.get('earningsGrowth')
        elif stock.info.get('revenueGrowth') is not None and stock.info.get('revenueGrowth') > 0 and pd.notna(stock.info.get('revenueGrowth')):
            growth_rate = stock.info.get('revenueGrowth')
        else:
            growth_rate = 0.08
    return min(growth_rate, 0.12)

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
        r_f = get_risk_free_rate(stock)
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
        growth_rate = estimate_growth_rate(stock, financials)
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
        r_f = get_risk_free_rate(stock)
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
        growth_rate = estimate_growth_rate(stock, financials)
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
def get_risk_free_rate(stock):
    is_india = stock.ticker.endswith('.NS')
    if is_india:
        return 0.069  # India 10Y G-Sec fallback — update periodically, no live yfinance source
    tnx = yf.Ticker("^TNX")
    try:
        rate = tnx.fast_info['lastPrice'] / 100
        if rate is not None and rate > 0 and pd.notna(rate):
            return rate
    except Exception:
        pass
    return 0.0425

VALUATION_RATIO_COLUMNS = ['Ticker', 'P/E Ratio', 'P/B Ratio', 'Forward P/E Ratio', 'PEG Ratio', 'EV/EBITDA', 'EV/Sales', 'P/FCF']
QUALITY_METRIC_COLUMNS = ['Ticker', 'DCF Valuation (%)', 'ROA', 'ROIC', 'Asset Turnover', 'Receivable Stress', 'Inventory Stress', 'FCF Yield', 'Debt to Equity Ratio', 'Interest Coverage']

def build_valuation_ratios_row(ticker_label, stock, financials, balance_sheet, cashflow):
    return {
        'Ticker': ticker_label,
        'P/E Ratio': pe_ratio_calculator(stock, financials),
        'P/B Ratio': pb_ratio_calculator(stock, balance_sheet),
        'Forward P/E Ratio': forward_pe_ratio_calculator(stock),
        'PEG Ratio': peg_ratio_calculator(stock),
        'EV/EBITDA': ev_to_ebitda_calculator(stock, financials),
        'EV/Sales': ev_sales_calculator(stock, financials),
        'P/FCF': p_fcf_calculator(stock, cashflow)
    }

def build_equity_dataframe(ticker_label, stock, financials, balance_sheet, cashflow):
    equity_dcf = discounted_cash_flow_calculator(stock, cashflow, financials, balance_sheet)
    roa, roic, asset_turnover, receivable_stress, inventory_stress = asset_quality_calculator(stock, cashflow, financials, balance_sheet)
    row = {
        'Ticker': ticker_label,
        'DCF Valuation (%)': equity_dcf,
        'ROA': roa,
        'ROIC': roic,
        'Asset Turnover': asset_turnover,
        'Receivable Stress': receivable_stress,
        'Inventory Stress': inventory_stress,
        'FCF Yield': fcf_yield_calculator(stock, cashflow),
        'Debt to Equity Ratio': Debt_to_Equity_calculator(stock, balance_sheet),
        'Interest Coverage': interest_coverage_calculator(stock, financials)
    }
    equity = pd.DataFrame([row], columns=QUALITY_METRIC_COLUMNS)
    equity = equity.dropna(subset=QUALITY_METRIC_COLUMNS[1:], how='all')
    return equity, equity_dcf

def compute_peer_score(peer_equity, peer, weights):
    peer_over = peer_under = peer_fair = 0
    for metric in VALUATION_RATIO_COLUMNS[1:]:
        value = peer_equity[metric].iloc[0]
        median = peer[metric].median()
        if pd.notna(value) and median is not None and pd.notna(median):
            if value > median * 1.05:
                peer_over += weights[metric]
            elif value < median * 0.95:
                peer_under += weights[metric]
            else:
                peer_fair += weights[metric]
    peer_total = peer_under + peer_over + peer_fair
    return (peer_under - peer_over) / peer_total if peer_total != 0 else None

def compute_peer_relative_valuation(stock, peer_tickers, financials, balance_sheet, cashflow):
    peer_equity = pd.DataFrame([build_valuation_ratios_row(stock.ticker, stock, financials, balance_sheet, cashflow)], columns=VALUATION_RATIO_COLUMNS)
    peer_rows = []
    for ticker in peer_tickers:
        peer_info = yf.Ticker(ticker)
        peer_bs = peer_info.balance_sheet
        peer_fin = peer_info.financials
        peer_cf = peer_info.cashflow
        peer_rows.append(build_valuation_ratios_row(ticker, peer_info, peer_fin, peer_bs, peer_cf))
    peer = pd.DataFrame(peer_rows, columns=VALUATION_RATIO_COLUMNS)
    peer = peer.dropna(subset=VALUATION_RATIO_COLUMNS[1:], how='all')
    weights = industry_weight(stock)
    return compute_peer_score(peer_equity, peer, weights)

def classify_five_tier(value, labels, high, mid, neutral, low):
    if value >= high:
        return labels[0]
    elif value >= mid:
        return labels[1]
    elif value > neutral:
        return labels[2]
    elif value > low:
        return labels[3]
    else:
        return labels[4]

def format_dcf_text(equity_dcf):
    if equity_dcf is None:
        return "DCF unavailable"
    if equity_dcf >= 0:
        return f"{equity_dcf:.2f}% undervalued by DCF"
    return f"{abs(equity_dcf):.2f}% overvalued by DCF"

def classify_verdict_peer(peer_score, quality_score, dcf_score, final_score):
    if peer_score >= 0.15 and dcf_score >= 0.15 and quality_score >= 0.15:
        if peer_score >= 0.50 and dcf_score >= 0.50 and quality_score >= 0.50:
            return "High Conviction Undervalued", "The stock looks cheap relative to peers, business quality is strong, and DCF also supports strong upside."
        return "Undervalued", "The stock looks attractively valued with supportive peer valuation, good quality, and positive DCF upside."

    elif peer_score <= -0.15 and dcf_score <= -0.15 and quality_score >= 0.15:
        return "Premium Quality, Rich Valuation", "The business quality is strong, but the stock is trading at a premium relative to peers and DCF does not support enough upside."

    elif peer_score >= 0.15 and dcf_score >= 0.15 and quality_score <= -0.15:
        return "Possible Value Trap", "The stock looks cheap on valuation, but business quality is weak. This may be a value trap."

    elif peer_score <= -0.15 and dcf_score <= -0.15 and quality_score <= -0.15:
        if peer_score <= -0.50 and dcf_score <= -0.50 and quality_score <= -0.50:
            return "Strong Overvaluation Warning", "The stock looks expensive, business quality is weak, and DCF also points to significant downside."
        return "Overvalued", "The stock appears expensive relative to peers and DCF, while business quality is also weak."

    elif peer_score >= 0.15 and dcf_score <= -0.15:
        if quality_score >= 0.15:
            return "Mixed Signals - Premium vs DCF Conflict", "Peer valuation suggests upside, but DCF suggests downside. Business quality is supportive, so the case depends heavily on assumptions."
        return "Mixed Signals - Weak Support", "Peer valuation and DCF are in conflict, and business quality is not strong enough to create confidence."

    elif peer_score <= -0.15 and dcf_score >= 0.15:
        if quality_score >= 0.15:
            return "Premium Multiple but DCF-Supported", "The stock looks expensive relative to peers, but DCF still indicates upside and business quality is strong."
        return "Mixed Signals", "DCF indicates upside, but peer valuation is rich and business quality is not strong."

    else:
        if final_score >= 0.15:
            return "Mild Positive / Mixed", "The stock has somewhat favorable signals overall, but not enough to call it clearly undervalued."
        elif final_score <= -0.15:
            return "Mild Negative / Mixed", "The stock has somewhat unfavorable signals overall, but not enough to call it clearly overvalued."
        return "Fair / Inconclusive", "The stock appears roughly fairly valued or has mixed signals without a clear edge."

def classify_verdict_non_peer(equity_dcf, quality_score, non_peer_score):
    if non_peer_score is None:
        return "Insufficient Data", "Not enough non-peer data to form a conclusion."

    elif equity_dcf >= 15 and quality_score >= 0.15:
        if equity_dcf >= 30 and quality_score >= 0.50:
            return "High Conviction Undervalued", "DCF shows strong upside and the business quality is strong."
        return "Undervalued", "DCF suggests upside and the business quality is supportive."

    elif equity_dcf >= 15 and quality_score < -0.15:
        return "Undervalued but Weak Quality", "DCF suggests upside, but weak business quality increases risk."

    elif equity_dcf <= -15 and quality_score >= 0.15:
        return "Premium Quality, Rich Valuation", "The business quality is good, but DCF suggests the stock is priced above intrinsic value."

    elif equity_dcf <= -15 and quality_score < -0.15:
        if equity_dcf <= -30 and quality_score <= -0.50:
            return "Strong Overvaluation Warning", "DCF suggests significant downside and business quality is weak."
        return "Overvalued", "DCF suggests downside and business quality is not supportive."

    else:
        if non_peer_score >= 0.15:
            return "Mild Positive / Mixed", "The non-peer signals are somewhat favorable, but not strongly enough."
        elif non_peer_score <= -0.15:
            return "Mild Negative / Mixed", "The non-peer signals are somewhat unfavorable, but not strongly enough."
        return "Fair / Inconclusive", "DCF and quality together do not give a strong directional signal."

def print_peer_summary(stock, peer_label, quality_label, dcf_label, dcf_text, peer_score, quality_score, dcf_score, final_score, final_label, final_message):
    print(f"\n----- {stock.ticker} VALUATION SUMMARY -----")
    print(f"Peer View       : {peer_label}")
    print(f"Quality View    : {quality_label}")
    print(f"DCF View        : {dcf_label} ({dcf_text})")
    print(f"Peer Score      : {peer_score:.2f}")
    print(f"Quality Score   : {quality_score:.2f}")
    print(f"DCF Score       : {dcf_score:.2f}")
    print(f"Final Score     : {final_score:.2f}")
    print(f"Final Verdict   : {final_label}")
    print(f"Interpretation  : {final_message}")

def print_non_peer_summary(stock, quality_label, dcf_label, dcf_text, quality_score, dcf_score, non_peer_score, non_peer_label, non_peer_message):
    print(f"\n----- {stock.ticker} NON-PEER SUMMARY -----")
    print(f"Quality View    : {quality_label}")
    print(f"DCF View        : {dcf_label} ({dcf_text})")
    print(f"Quality Score   : {quality_score:.2f}" if quality_score is not None else "Quality Score   : None")
    print(f"DCF Score       : {dcf_score:.2f}" if dcf_score is not None else "DCF Score       : None")
    print(f"Non-Peer Score  : {non_peer_score:.2f}" if non_peer_score is not None else "Non-Peer Score  : None")
    print(f"Final Verdict   : {non_peer_label}")
    print(f"Interpretation  : {non_peer_message}")

QUALITY_LABELS = ("Strong Quality", "Good Quality", "Average Quality", "Weak Quality", "Very Weak Quality")
PEER_LABELS = ("Strongly Undervalued vs Peers", "Undervalued vs Peers", "Fairly Valued vs Peers", "Overvalued vs Peers", "Strongly Overvalued vs Peers")
DCF_LABELS = ("Strongly Undervalued by DCF", "Undervalued by DCF", "Fairly Valued by DCF", "Overvalued by DCF", "Strongly Overvalued by DCF")

def compute_quality_score(stock, equity):
    quality_weights, quality_thresholds = industry_quality_weight(stock)
    quality_good, quality_bad, quality_neutral = score_quality_metrics(equity, quality_weights, quality_thresholds)
    quality_total = quality_good + quality_bad + quality_neutral
    return (quality_good - quality_bad) / quality_total if quality_total != 0 else None

def run_peer_valuation(stock, peer_tickers, financials, balance_sheet, cashflow):
    peer_score = compute_peer_relative_valuation(stock, peer_tickers, financials, balance_sheet, cashflow)
    equity, equity_dcf = build_equity_dataframe(stock.ticker, stock, financials, balance_sheet, cashflow)
    quality_score = compute_quality_score(stock, equity)
    dcf_score = max(-1, min(1, equity_dcf / 30)) if equity_dcf is not None else None

    if peer_score is None or quality_score is None or dcf_score is None:
        print(f"{stock.ticker}: Insufficient data for full interpretation.")
        return

    final_score = 0.4 * peer_score + 0.2 * quality_score + 0.4 * dcf_score
    dcf_text = format_dcf_text(equity_dcf)
    peer_label = classify_five_tier(peer_score, PEER_LABELS, 0.50, 0.15, -0.15, -0.50)
    quality_label = classify_five_tier(quality_score, QUALITY_LABELS, 0.50, 0.15, -0.15, -0.50)
    dcf_label = classify_five_tier(equity_dcf, DCF_LABELS, 30, 15, -15, -30)
    final_label, final_message = classify_verdict_peer(peer_score, quality_score, dcf_score, final_score)
    print_peer_summary(stock, peer_label, quality_label, dcf_label, dcf_text, peer_score, quality_score, dcf_score, final_score, final_label, final_message)

def run_non_peer_valuation(stock, financials, balance_sheet, cashflow):
    equity, equity_dcf = build_equity_dataframe(stock.ticker, stock, financials, balance_sheet, cashflow)
    quality_score = compute_quality_score(stock, equity)
    dcf_score = max(-1, min(1, equity_dcf / 30)) if equity_dcf is not None else None
    quality_label = classify_five_tier(quality_score, QUALITY_LABELS, 0.50, 0.15, -0.15, -0.50) if quality_score is not None else "Insufficient Data"
    dcf_label = classify_five_tier(equity_dcf, DCF_LABELS, 30, 15, -15, -30) if equity_dcf is not None else "Insufficient Data"
    non_peer_score = (0.4 * quality_score) + (0.6 * dcf_score) if quality_score is not None and dcf_score is not None else None
    non_peer_label, non_peer_message = classify_verdict_non_peer(equity_dcf, quality_score, non_peer_score)
    dcf_text = format_dcf_text(equity_dcf)
    print_non_peer_summary(stock, quality_label, dcf_label, dcf_text, quality_score, dcf_score, non_peer_score, non_peer_label, non_peer_message)

def main():
    if peers is not None and len(peers) > 0:
        run_peer_valuation(stk, peers, fin, bs, cf)
    else:
        run_non_peer_valuation(stk, fin, bs, cf)
    print("\nWARNING: This model is a decision-support and screening tool, not a definitive valuation authority. Outputs depend on data quality, assumptions, and simplified rules, so results should always be cross-checked with company filings, earnings reports, industry context, and independent analysis before making any investment decision.")

if __name__ == "__main__":
    main()