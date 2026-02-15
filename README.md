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

**Disclaimer**

This project is for educational and research purposes only.
It does not constitute financial advice.
All valuations are based on publicly available financial data and assumptions.
Investors should conduct independent research before making investment decisions.

