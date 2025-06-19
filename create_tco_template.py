#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCO 분석용 엑셀 템플릿 생성 스크립트
승용/승합/화물 → 자가/상용 → 소형/중형/대형 분류 구조 사용
"""

import pandas as pd
import numpy as np

def create_tco_template():
    """TCO 분석용 엑셀 템플릿 생성"""
    
    # 분류 조합 생성
    data = []
    main_types = ['승용', '승합', '화물']
    sub_types = ['자가', '상용']  
    size_types = ['소형', '중형', '대형']
    car_types = ['ICE', 'BEV']
    
    # 예시 데이터로 채우기 (실제 사용시에는 빈 값으로 두거나 실제 데이터로 교체)
    np.random.seed(42)  # 재현 가능한 랜덤 값
    
    for main in main_types:
        for sub in sub_types:
            for size in size_types:
                for car in car_types:
                    # 예시 데이터 (실제로는 사용자가 입력)
                    if car == 'ICE':
                        purchase_cost = np.random.randint(2000, 8000)  # 만원
                        fuel_cost = np.random.randint(800, 1500)      # 연간 연료비
                        maintenance = np.random.randint(200, 500)     # 연간 유지보수비
                        tax_insurance = np.random.randint(100, 300)   # 연간 세금/보험
                        depreciation = purchase_cost * 0.15           # 연간 감가상각
                        subsidy = 0                                   # ICE 보조금
                    else:  # BEV
                        purchase_cost = np.random.randint(3000, 10000)
                        fuel_cost = np.random.randint(200, 600)       # 전기비
                        maintenance = np.random.randint(100, 300)     # 낮은 유지보수비
                        tax_insurance = np.random.randint(80, 250)    # 세금 혜택
                        depreciation = purchase_cost * 0.18           # 높은 감가상각
                        subsidy = np.random.randint(500, 1200)        # BEV 보조금
                    
                    vehicle_count = np.random.randint(50, 500)  # 차량 대수
                    
                    data.append({
                        '대분류': main,
                        '중분류': sub, 
                        '소분류': size,
                        '차량유형': car,
                        '차량대수': vehicle_count,
                        '구매비용_만원': purchase_cost,
                        '연료비_만원': fuel_cost,
                        '유지보수비_만원': maintenance,
                        '세금보험_만원': tax_insurance,
                        '감가상각_만원': int(depreciation),
                        '보조금_만원': subsidy,
                        '기타비용_만원': np.random.randint(50, 200)
                    })
    
    # DataFrame 생성
    df = pd.DataFrame(data)
    
    # TCO 계산
    df['연간TCO_만원'] = (df['구매비용_만원'] + df['연료비_만원'] + 
                        df['유지보수비_만원'] + df['세금보험_만원'] + 
                        df['감가상각_만원'] + df['기타비용_만원'] - 
                        df['보조금_만원'])
    
    # 엑셀 파일로 저장
    with pd.ExcelWriter('TCO_분석_입력템플릿.xlsx', engine='openpyxl') as writer:
        # 메인 데이터 시트
        df.to_excel(writer, sheet_name='차량분류', index=False)
        
        # 보조금 시나리오 시트 (ICE 지원 제거 시나리오)
        df_scenario = df.copy()
        # ICE에 숨겨진 지원(예: 연료세 감면, 도로세 등) 제거 시나리오
        df_scenario.loc[df_scenario['차량유형'] == 'ICE', '숨겨진지원제거_만원'] = np.random.randint(100, 300)
        df_scenario.loc[df_scenario['차량유형'] == 'BEV', '숨겨진지원제거_만원'] = 0
        
        df_scenario['조정후TCO_만원'] = df_scenario['연간TCO_만원'] + df_scenario['숨겨진지원제거_만원']
        df_scenario.to_excel(writer, sheet_name='지원제거시나리오', index=False)
        
        # 설명 시트
        explanation = pd.DataFrame({
            '항목': ['대분류', '중분류', '소분류', '차량유형', '차량대수', '구매비용_만원', 
                    '연료비_만원', '유지보수비_만원', '세금보험_만원', '감가상각_만원', 
                    '보조금_만원', '기타비용_만원', '연간TCO_만원'],
            '설명': ['승용/승합/화물', '자가/상용', '소형/중형/대형', 'ICE/BEV', 
                    '해당 분류의 차량 대수', '차량 구매 비용', '연간 연료비 또는 전기비',
                    '연간 유지보수비', '연간 세금 및 보험료', '연간 감가상각비',
                    '정부 보조금 (차감)', '기타 운영비용', '총소유비용 (연간)']
        })
        explanation.to_excel(writer, sheet_name='항목설명', index=False)
    
    print("✅ TCO_분석_입력템플릿.xlsx 파일이 생성되었습니다.")
    print(f"✅ 총 {len(df)} 개의 차량 분류 조합이 생성되었습니다.")
    
    return df

if __name__ == "__main__":
    create_tco_template() 