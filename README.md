# 🚀 Propell Valuation 
### US & Indian Equity Valuation Engine

**A Python-based multi-factor stock valuation system covering US and Indian equities, combining intrinsic valuation, peer comparison, financial quality analysis, and weighted scoring to classify stocks as undervalued, fairly valued, or overvalued.**

This project is built to go beyond a single-ratio approach by combining multiple valuation methods, including **DCF**, **peer comparison**, **profitability metrics**, **cash flow analysis**, and **balance sheet strength**, to create a more structured and realistic view of valuation.

---
## Markets Supported

- **US equities** — enter the ticker as-is (e.g. `AAPL`, `NVDA`)
- **Indian equities (NSE)** — append `.NS` to the symbol (e.g. `RELIANCE.NS`, `HDFCBANK.NS`)

Peer matching, market-cap bucketing, and DCF discount rates are handled separately per market (Indian market caps are converted to USD internally for consistent bucketing; the DCF uses an India-specific risk-free rate for `.NS` tickers).

---

## Key Features

### 1. Discounted Cash Flow (DCF) Valuation
FCFE-based, with terminal growth averaged across historical periods and a CAPM-style discount rate.

### 2. Relative / Peer Valuation
Compares a company against same-market industry peers using P/E, Forward P/E, PEG, P/B, EV/EBITDA, EV/Sales, and P/FCF.

### 3. Quality Analysis
Evaluates ROE, ROA, FCF yield, debt-to-equity, and interest coverage. Thresholds are **archetype-aware** — banks, REITs/utilities, cyclicals, and high-growth companies are judged against sector-appropriate cutoffs, not one universal standard.

### 4. Weighted Scoring System
Combines all methods into a single score rather than relying on a single ratio.

### 5. Industry-Aware Logic
Industry-specific weights, archetype-specific quality thresholds, asset-intensity checks, and selective P/B use for asset-heavy businesses.

---

## How It Works

The model follows a broad pipeline like this:

1. **Fetch company financial data**
2. **Clean and standardize the extracted data**
3. **Calculate standalone valuation metrics**
4. **Identify peer companies (matched within the same market)**
5. **Compare valuation ratios against peer medians**
6. **Evaluate business quality**
7. **Apply weighted scoring**
8. **Generate final classification**

---

## Steps to Run the Project

1. **Clone the repository:**
```bash
   git clone https://github.com/aaronshibutho-prog/propell-valuation-engine.git
   cd propell-valuation-engine
```
   or download the project files directly and keep them in the same folder.

2. **Install dependencies:**
```bash
   pip install pandas numpy yfinance
```

3. **Ensure all project files are in the same directory:**
   *valuator.py, yfinextractor.py, peer_allocator.py, peer_accelerator.py, peer_accelerator_india.py, industry_ticks.xlsx, industry_ticks_india.xlsx, industry_ticks_weighted.xlsx, industry_quality_weights.xlsx, indian_equities.csv*
    ```
    python valuator.py
    ```
Enter a US ticker (e.g. `AAPL`) or an Indian ticker with the `.NS` suffix (e.g. `RELIANCE.NS`) when prompted.  

---

## Disclaimer

This project is for educational and research purposes only.
The valuation produced by this model is based on available financial data and model assumptions, both of which may change over time. It should not be considered financial advice, investment advice, or a recommendation to buy or sell any security. Always do your own research before making investment decisions.

