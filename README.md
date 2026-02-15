# multi-factor-valuation-model
Built a multi-factor stock valuation model in Python that automates intrinsic value estimation using real-time financial data. The model integrates DCF, capital structure analysis, profitability metrics, and scoring logic to produce structured buy/fair/sell signals. I have made it Tech-Savvy by using pandas and Yfinance for data structuring and extraction.


**Methodology Used**

-*1️ Price-to-Book (P/B) Ratio:*
Used with the ROE context to avoid misleading signals.

-*2️ PEG Ratio*
Price-to-Earnings relative to growth.

-*3️ Free Cash Flow Yield:*
FCF / Market Cap to measure value relative to cash generation.

-*4️ Return on Equity (ROE):*
Profitability efficiency measure.

-*5️ Discounted Cash Flow (DCF):*
Revenue CAGR-based growth estimation
CAPM for the cost of equity
WACC for the discount rate
Terminal value via the Gordon Growth Model
Enterprise value adjusted to equity value

-*6️ Debt-to-Equity Ratio:*
Balance sheet risk analysis.


**Scoring Methodology & Weights**

To ensure a balanced valuation, the model assigns weights to each factor based on its reliability as a value indicator:

| Factor | Weight | Rationale |
| :--- | :---: | :--- |
| **DCF Intrinsic Value** | **35%** | The core fundamental value based on future cash flows. |
| **Free Cash Flow Yield** | **25%** | Measures actual "cash-in-hand" relative to market cap. |
| **PEG Ratio** | **10%** | Balances valuation with projected earnings growth. |
| **Return on Equity (ROE)** | **10%** | Profitability efficiency check. |
| **Price-to-Book (P/B)** | **10%** | Asset-based valuation (adjusted for sector norms). |
| **Debt-to-Equity (D/E)** | **10%** | Risk multiplier; penalizes over-leveraged companies. |


**How to Run This Project**

-*Step 1: Clone the Repository:*
```bash
git clone https://github.com/aaronshibutho-prog/multi-factor-valuation-model.git
```
```bash
cd multi-factor-valuation-model  
```
Or download the ZIP file from GitHub and extract it.

-*Step 2: Install Required Libraries:*
```bash
pip install yfinance pandas
```
-*Step 3: Run the Script:*
```bash
python valuation_model.py
```
-*Step 4: Enter Stock Ticker:*
For Example: NVDA, AAPL, RELIANCE.NS or HDFCBANK.NS


**Disclaimer**

This project is for educational and research purposes only.
It does not constitute financial advice.
All valuations are based on publicly available financial data and assumptions.
Investors should conduct independent research before making investment decisions.

