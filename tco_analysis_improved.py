#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 TCO (Total Cost of Ownership) 분석 모델
올바른 TCO 계산 로직 적용
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class ImprovedTCOAnalyzer:
    """개선된 TCO 분석 클래스"""
    
    def __init__(self, ownership_years=5):
        """
        초기화
        ownership_years: 차량 소유 기간 (기본 5년)
        """
        self.ownership_years = ownership_years
        
    def calculate_correct_tco(self, df):
        """올바른 TCO 계산"""
        
        # 1. 초기 투자비용 (구매 시점)
        df['초기투자비용_만원'] = df['구매비용_만원'] - df['보조금_만원']
        
        # 2. 연간 운영비용
        df['연간운영비_만원'] = (df['연료비_만원'] + df['유지보수비_만원'] + 
                              df['세금보험_만원'] + df['감가상각_만원'] + 
                              df['기타비용_만원'])
        
        # 3. 총 운영비용 (소유기간 동안)
        df['총운영비_만원'] = df['연간운영비_만원'] * self.ownership_years
        
        # 4. 잔존가치 계산 (구매가의 일정 비율)
        # ICE: 5년 후 40% 잔존, BEV: 5년 후 25% 잔존 (배터리 감가상각)
        df['잔존가치_만원'] = df.apply(
            lambda x: x['구매비용_만원'] * (0.4 if x['차량유형'] == 'ICE' else 0.25), 
            axis=1
        )
        
        # 5. 총 TCO 계산
        df['총TCO_만원'] = df['초기투자비용_만원'] + df['총운영비_만원'] - df['잔존가치_만원']
        
        # 6. 연평균 TCO 계산
        df['연평균TCO_만원'] = df['총TCO_만원'] / self.ownership_years
        
        return df
    
    def analyze_by_year(self, df):
        """연도별 TCO 분석"""
        results = []
        
        for year in range(1, self.ownership_years + 1):
            if year == 1:
                # 첫해: 구매비용 + 운영비 - 보조금
                year_tco = df['구매비용_만원'] + df['연간운영비_만원'] - df['보조금_만원']
            else:
                # 2년차 이후: 운영비만
                year_tco = df['연간운영비_만원']
            
            year_data = df.copy()
            year_data['연도'] = year
            year_data['해당연도TCO_만원'] = year_tco
            results.append(year_data)
        
        return pd.concat(results, ignore_index=True)

def create_improved_analysis():
    """개선된 분석 예시"""
    
    # 예시 데이터 생성
    data = []
    np.random.seed(42)
    
    for vehicle_type in ['ICE', 'BEV']:
        for size in ['소형', '중형', '대형']:
            if vehicle_type == 'ICE':
                purchase_cost = np.random.randint(3000, 8000)
                fuel_cost = np.random.randint(800, 1500)
                maintenance = np.random.randint(300, 600)
                tax_insurance = np.random.randint(200, 400)
                depreciation = purchase_cost * 0.15
                subsidy = 0
            else:  # BEV
                purchase_cost = np.random.randint(4000, 12000)
                fuel_cost = np.random.randint(200, 500)
                maintenance = np.random.randint(150, 350)
                tax_insurance = np.random.randint(150, 300)
                depreciation = purchase_cost * 0.18
                subsidy = np.random.randint(800, 1500)
            
            data.append({
                '차량유형': vehicle_type,
                '크기': size,
                '구매비용_만원': purchase_cost,
                '연료비_만원': fuel_cost,
                '유지보수비_만원': maintenance,
                '세금보험_만원': tax_insurance,
                '감가상각_만원': int(depreciation),
                '보조금_만원': subsidy,
                '기타비용_만원': np.random.randint(100, 300)
            })
    
    df = pd.DataFrame(data)
    
    # 개선된 TCO 분석 실행
    analyzer = ImprovedTCOAnalyzer(ownership_years=5)
    df_improved = analyzer.calculate_correct_tco(df)
    
    # 결과 출력
    print("="*60)
    print("           개선된 TCO 분석 결과")
    print("="*60)
    
    print("\n📊 차량유형별 TCO 비교 (5년 소유 기준):")
    tco_summary = df_improved.groupby('차량유형').agg({
        '초기투자비용_만원': 'mean',
        '연간운영비_만원': 'mean', 
        '총운영비_만원': 'mean',
        '잔존가치_만원': 'mean',
        '총TCO_만원': 'mean',
        '연평균TCO_만원': 'mean'
    }).round(0)
    
    print(tco_summary)
    
    print("\n💰 TCO 구성 요소 분석:")
    ice_data = df_improved[df_improved['차량유형'] == 'ICE'].iloc[0]
    bev_data = df_improved[df_improved['차량유형'] == 'BEV'].iloc[0]
    
    print(f"\n🚗 ICE 차량 예시 (5년 소유):")
    print(f"   초기투자: {ice_data['초기투자비용_만원']:,.0f}만원")
    print(f"   총운영비: {ice_data['총운영비_만원']:,.0f}만원")
    print(f"   잔존가치: -{ice_data['잔존가치_만원']:,.0f}만원")
    print(f"   ────────────────────────")
    print(f"   총 TCO:   {ice_data['총TCO_만원']:,.0f}만원")
    print(f"   연평균:   {ice_data['연평균TCO_만원']:,.0f}만원")
    
    print(f"\n⚡ BEV 차량 예시 (5년 소유):")
    print(f"   초기투자: {bev_data['초기투자비용_만원']:,.0f}만원")
    print(f"   총운영비: {bev_data['총운영비_만원']:,.0f}만원")
    print(f"   잔존가치: -{bev_data['잔존가치_만원']:,.0f}만원")
    print(f"   ────────────────────────")
    print(f"   총 TCO:   {bev_data['총TCO_만원']:,.0f}만원")
    print(f"   연평균:   {bev_data['연평균TCO_만원']:,.0f}만원")
    
    # 연도별 분석
    yearly_analysis = analyzer.analyze_by_year(df_improved)
    
    print(f"\n📅 연도별 TCO 분석:")
    yearly_summary = yearly_analysis.groupby(['차량유형', '연도'])['해당연도TCO_만원'].mean().unstack()
    print(yearly_summary.round(0))
    
    return df_improved

if __name__ == "__main__":
    create_improved_analysis() 