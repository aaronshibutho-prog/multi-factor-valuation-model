# 🚀 Propell
### Equity Valuation Engine

**A Python-based multi-factor stock valuation system that combines intrinsic valuation, peer comparison, financial quality analysis, and weighted scoring to classify stocks as undervalued, fairly valued, or overvalued.**

This project is built to go beyond a single-ratio approach by using multiple valuation methods together, including **DCF**, **peer comparison**, **profitability metrics**, **cash flow analysis**, and **balance sheet strength**, to create a more structured and realistic view of valuation.

---

## Overview

Valuing a stock using only one metric can be misleading. A low P/E ratio may not mean a stock is cheap, and a high P/E ratio may not always mean it is expensive. This model attempts to solve that problem by combining several methods into one framework.

The valuation engine:

- Extracts financial data using `yfinance.`
- Performs **non-peer valuation**
- Performs **peer-based valuation**
- Evaluates **quality and financial health**
- Applies a **weighted scoring logic**
- Produces a final classification such as:
  - **Undervalued**
  - **Fairly Valued**
  - **Overvalued**
  - **Inconclusive**

---

## Key Features

### 1. Discounted Cash Flow (DCF) Valuation
Uses projected future cash flows and discounts them back to present value.

- Supports **FCFE-based valuation**
- Includes **terminal growth assumptions**
- Uses a **CAPM-style discount rate**
- Allows different assumptions for **US and Indian stocks**

### 2. Relative / Peer Valuation
Compares a company against similar companies in its industry using:

- P/E Ratio
- Forward P/E
- PEG Ratio
- P/B Ratio
- EV/EBITDA
- EV/EBIT
- EV/Sales
- P/FCF

### 3. Quality Analysis
Evaluates the strength of the business using metrics such as:

- ROE
- ROA
- Operating Margin
- Net Margin
- Free Cash Flow Yield
- Debt-to-Equity
- Interest Coverage
- Current Ratio
- Asset quality indicators

### 4. Weighted Scoring System
Instead of depending on one ratio, the model assigns weights to different metrics and produces a combined view.

### 5. Industry-Aware Logic
Different industries may require different weights and interpretations. The model is designed to support:

- Industry-specific weights
- Asset-intensity checks
- Selective use of P/B for asset-heavy businesses
- Better peer relevance

---

## How It Works

The model follows a broad pipeline like this:

1. **Fetch company financial data**
2. **Clean and standardize the extracted data**
3. **Calculate standalone valuation metrics**
4. **Identify peer companies**
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
   or
   Download the project files directly from the repository and keep them in the same folder.
   
2. **Install the required dependencies manually:**
   ```bash
   pip install pandas numpy yfinance
   ```

3. **Ensure all project files are in the same directory:**
   *valuator.py,*
   *yfinextractor.py,*
   *peer_allocator.py,*
   *peer_accelerator.py,*
   *industry_ticks.xlsx,*
   *industry_ticks_weighted.xlsx,*
   *industry_quality_weights.xlsx,*
   and finally, run the main valuation script. 
    ```
    python valuator.py
    ```

    
---

## Disclaimer

This project is for educational and research purposes only.
The valuation produced by this model is based on available financial data and model assumptions, both of which may change over time. It should not be considered financial advice, investment advice, or a recommendation to buy or sell any security. Always do your own research before making investment decisions.

