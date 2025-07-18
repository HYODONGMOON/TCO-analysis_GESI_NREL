import pandas as pd
from tco_analysis_detailed import DetailedTCOAnalyzer

analyzer = DetailedTCOAnalyzer()
analyzer.load_data()
df = analyzer.data

small_cargo_ice = df[(df['중분류']=='소형화물') & (df['차량유형']=='ICE')]
print('소형화물 ICE 차량별 배출량:')
for idx, row in small_cargo_ice.iterrows():
    차량대수 = row['차량대수']
    연비 = row['연비']
    배출량 = 56609 * 2.5950 / 연비 * 차량대수
    print(f"{row['소분류']}: 차량대수={차량대수}, 연비={연비}, 배출량={배출량:,.0f} kgCO2")
print(f'총합: {small_cargo_ice.apply(lambda row: 56609 * 2.5950 / row["연비"] * row["차량대수"], axis=1).sum():,.0f} kgCO2') 