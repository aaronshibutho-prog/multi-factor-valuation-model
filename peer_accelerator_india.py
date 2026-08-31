import pandas as pd

india_industries = set(pd.read_excel('industry_ticks_india.xlsx')['Industry'].dropna())
weighted_industries = set(pd.read_excel('industry_ticks_weighted.xlsx')['Industry'])
quality_industries = set(pd.read_excel('industry_quality_weights.xlsx')['Industry'])

missing_from_weighted = india_industries - weighted_industries
missing_from_quality = india_industries - quality_industries

print(f"Indian industries missing peer weights: {len(missing_from_weighted)}")
print(missing_from_weighted)
print(f"\nIndian industries missing quality weights: {len(missing_from_quality)}")
print(missing_from_quality)