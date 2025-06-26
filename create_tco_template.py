#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCO 분석용 엑셀 템플릿 생성 스크립트
5년 소유기간 기준 올바른 TCO 계산 적용
기존 파일 보존 기능 추가
승용/승합/화물 → 자가/상용 → 소형/중형/대형 분류 구조 사용
"""

import pandas as pd
import numpy as np
import os

def create_tco_template(force_overwrite=False):
    """TCO 분석용 엑셀 템플릿 생성 (5년 소유기간 기준)"""
    
    output_file = 'TCO_분석_입력템플릿.xlsx'
    
    # 기존 파일 존재 확인
    if os.path.exists(output_file) and not force_overwrite:
        print(f"⚠️  기존 파일이 존재합니다: {output_file}")
        print("   기존 파일을 보존하고 새 파일을 생성합니다.")
        
        # 백업 파일명 생성
        backup_file = f'TCO_분석_입력템플릿_backup_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        try:
            # 기존 파일을 백업으로 복사
            import shutil
            shutil.copy2(output_file, backup_file)
            print(f"✅ 기존 파일이 백업되었습니다: {backup_file}")
        except Exception as e:
            print(f"❌ 백업 생성 실패: {e}")
            return None
    
    # 분류 조합 생성
    data = []
    main_types = ['승용', '승합', '화물']
    sub_types = ['자가', '상용']  
    size_types = ['소형', '중형', '대형']
    car_types = ['ICE', 'BEV']
    
    # 소유기간 설정
    ownership_years = 5
    
    # 기존 데이터가 있으면 로드하여 참조
    existing_data = None
    if os.path.exists(output_file):
        try:
            existing_df = pd.read_excel(output_file, sheet_name='차량분류')
            if len(existing_df) > 0:
                existing_data = existing_df
                print("📊 기존 데이터를 참조하여 템플릿을 생성합니다.")
        except:
            pass
    
    # 예시 데이터로 채우기 (실제 사용시에는 빈 값으로 두거나 실제 데이터로 교체)
    np.random.seed(42)  # 재현 가능한 랜덤 값
    
    for main in main_types:
        for sub in sub_types:
            for size in size_types:
                for car in car_types:
                    # 기존 데이터가 있으면 해당 값을 사용, 없으면 새로 생성
                    if existing_data is not None:
                        existing_row = existing_data[
                            (existing_data['대분류'] == main) & 
                            (existing_data['중분류'] == sub) & 
                            (existing_data['소분류'] == size) & 
                            (existing_data['차량유형'] == car)
                        ]
                        
                        if len(existing_row) > 0:
                            # 기존 데이터 사용
                            row = existing_row.iloc[0]
                            purchase_cost = row['구매비용_만원']
                            vehicle_count = row['차량대수']
                            subsidy = row['보조금_만원']
                            
                            # 기존 데이터에서 비용 구성요소 추출 (있다면)
                            if '연간연료비_만원' in row:
                                annual_fuel_cost = row['연간연료비_만원']
                                annual_maintenance = row['연간유지보수비_만원']
                                annual_tax_insurance = row['연간세금보험_만원']
                                annual_depreciation = row['연간감가상각_만원']
                                annual_other_cost = row['연간기타비용_만원']
                            else:
                                # 기존 데이터에 없는 필드는 새로 생성
                                if car == 'ICE':
                                    annual_fuel_cost = np.random.randint(800, 1500)
                                    annual_maintenance = np.random.randint(200, 500)
                                    annual_tax_insurance = np.random.randint(100, 300)
                                    annual_depreciation = purchase_cost * 0.15
                                    annual_other_cost = np.random.randint(50, 200)
                                else:  # BEV
                                    annual_fuel_cost = np.random.randint(200, 600)
                                    annual_maintenance = np.random.randint(100, 300)
                                    annual_tax_insurance = np.random.randint(80, 250)
                                    annual_depreciation = purchase_cost * 0.18
                                    annual_other_cost = np.random.randint(50, 200)
                        else:
                            # 기존 데이터에 없는 조합은 새로 생성
                            if car == 'ICE':
                                purchase_cost = np.random.randint(2000, 8000)
                                annual_fuel_cost = np.random.randint(800, 1500)
                                annual_maintenance = np.random.randint(200, 500)
                                annual_tax_insurance = np.random.randint(100, 300)
                                annual_depreciation = purchase_cost * 0.15
                                subsidy = 0
                                annual_other_cost = np.random.randint(50, 200)
                            else:  # BEV
                                purchase_cost = np.random.randint(3000, 10000)
                                annual_fuel_cost = np.random.randint(200, 600)
                                annual_maintenance = np.random.randint(100, 300)
                                annual_tax_insurance = np.random.randint(80, 250)
                                annual_depreciation = purchase_cost * 0.18
                                subsidy = np.random.randint(500, 1200)
                                annual_other_cost = np.random.randint(50, 200)
                            vehicle_count = np.random.randint(50, 500)
                    else:
                        # 완전히 새로운 데이터 생성
                        if car == 'ICE':
                            purchase_cost = np.random.randint(2000, 8000)
                            annual_fuel_cost = np.random.randint(800, 1500)
                            annual_maintenance = np.random.randint(200, 500)
                            annual_tax_insurance = np.random.randint(100, 300)
                            annual_depreciation = purchase_cost * 0.15
                            subsidy = 0
                            residual_value_rate = 0.4
                        else:  # BEV
                            purchase_cost = np.random.randint(3000, 10000)
                            annual_fuel_cost = np.random.randint(200, 600)
                            annual_maintenance = np.random.randint(100, 300)
                            annual_tax_insurance = np.random.randint(80, 250)
                            annual_depreciation = purchase_cost * 0.18
                            subsidy = np.random.randint(500, 1200)
                            residual_value_rate = 0.25
                        
                        vehicle_count = np.random.randint(50, 500)
                        annual_other_cost = np.random.randint(50, 200)
                    
                    # 잔존가치율 설정
                    if car == 'ICE':
                        residual_value_rate = 0.4
                    else:  # BEV
                        residual_value_rate = 0.25
                    
                    # TCO 계산 구성요소
                    initial_investment = purchase_cost - subsidy
                    annual_operating_cost = (annual_fuel_cost + annual_maintenance + 
                                           annual_tax_insurance + annual_depreciation + 
                                           annual_other_cost)
                    total_operating_cost = annual_operating_cost * ownership_years
                    residual_value = purchase_cost * residual_value_rate
                    total_tco = initial_investment + total_operating_cost - residual_value
                    annual_average_tco = total_tco / ownership_years
                    
                    data.append({
                        '대분류': main,
                        '중분류': sub, 
                        '소분류': size,
                        '차량유형': car,
                        '차량대수': vehicle_count,
                        '구매비용_만원': purchase_cost,
                        '보조금_만원': subsidy,
                        '초기투자비용_만원': int(initial_investment),
                        '연간연료비_만원': annual_fuel_cost,
                        '연간유지보수비_만원': annual_maintenance,
                        '연간세금보험_만원': annual_tax_insurance,
                        '연간감가상각_만원': int(annual_depreciation),
                        '연간기타비용_만원': annual_other_cost,
                        '연간운영비_만원': int(annual_operating_cost),
                        '총운영비_만원': int(total_operating_cost),
                        '잔존가치율': residual_value_rate,
                        '잔존가치_만원': int(residual_value),
                        '총TCO_만원': int(total_tco),
                        '연평균TCO_만원': int(annual_average_tco),
                        '소유기간_년': ownership_years
                    })
    
    # DataFrame 생성
    df = pd.DataFrame(data)
    
    # 엑셀 파일로 저장
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 메인 데이터 시트
        df.to_excel(writer, sheet_name='차량분류', index=False)
        
        # 보조금 시나리오 시트 (ICE 지원 제거 시나리오)
        df_scenario = df.copy()
        # ICE에 숨겨진 지원(예: 연료세 감면, 도로세 등) 제거 시나리오
        ice_hidden_support = np.random.randint(100, 300, size=len(df_scenario))
        df_scenario['숨겨진지원제거_연간_만원'] = np.where(
            df_scenario['차량유형'] == 'ICE', ice_hidden_support, 0
        )
        df_scenario['숨겨진지원제거_총액_만원'] = df_scenario['숨겨진지원제거_연간_만원'] * ownership_years
        df_scenario['조정후총TCO_만원'] = df_scenario['총TCO_만원'] + df_scenario['숨겨진지원제거_총액_만원']
        df_scenario['조정후연평균TCO_만원'] = df_scenario['조정후총TCO_만원'] / ownership_years
        df_scenario.to_excel(writer, sheet_name='지원제거시나리오', index=False)
        
        # 연도별 TCO 시트
        yearly_data = []
        for _, row in df.iterrows():
            for year in range(1, ownership_years + 1):
                if year == 1:
                    # 첫해: 초기투자 + 연간운영비
                    year_tco = row['초기투자비용_만원'] + row['연간운영비_만원']
                elif year == ownership_years:
                    # 마지막해: 연간운영비 - 잔존가치
                    year_tco = row['연간운영비_만원'] - row['잔존가치_만원']
                else:
                    # 중간년도: 연간운영비만
                    year_tco = row['연간운영비_만원']
                
                yearly_data.append({
                    '대분류': row['대분류'],
                    '중분류': row['중분류'],
                    '소분류': row['소분류'],
                    '차량유형': row['차량유형'],
                    '연도': year,
                    '해당연도TCO_만원': int(year_tco),
                    '누적TCO_만원': int(sum([yearly_data[i]['해당연도TCO_만원'] 
                                          for i in range(len(yearly_data)) 
                                          if yearly_data[i]['대분류'] == row['대분류'] and
                                             yearly_data[i]['중분류'] == row['중분류'] and
                                             yearly_data[i]['소분류'] == row['소분류'] and
                                             yearly_data[i]['차량유형'] == row['차량유형']] + [year_tco]))
                })
        
        df_yearly = pd.DataFrame(yearly_data)
        df_yearly.to_excel(writer, sheet_name='연도별TCO', index=False)
        
        # 설명 시트
        explanation = pd.DataFrame({
            '항목': ['대분류', '중분류', '소분류', '차량유형', '차량대수', '구매비용_만원', 
                    '보조금_만원', '초기투자비용_만원', '연간연료비_만원', '연간유지보수비_만원', 
                    '연간세금보험_만원', '연간감가상각_만원', '연간기타비용_만원', '연간운영비_만원',
                    '총운영비_만원', '잔존가치율', '잔존가치_만원', '총TCO_만원', '연평균TCO_만원', '소유기간_년'],
            '설명': ['승용/승합/화물', '자가/상용', '소형/중형/대형', 'ICE/BEV', 
                    '해당 분류의 차량 대수', '차량 구매 비용', '정부 보조금', '실제 초기 투자비용 (구매비용-보조금)',
                    '연간 연료비 또는 전기비', '연간 유지보수비', '연간 세금 및 보험료', '연간 감가상각비',
                    '연간 기타 운영비용', '연간 총 운영비용', f'{ownership_years}년간 총 운영비용', 
                    f'{ownership_years}년 후 잔존가치 비율', f'{ownership_years}년 후 잔존가치', 
                    f'{ownership_years}년 총소유비용', f'{ownership_years}년 연평균 소유비용', '차량 소유기간']
        })
        explanation.to_excel(writer, sheet_name='항목설명', index=False)
        
        # TCO 계산식 설명 시트
        formula_explanation = pd.DataFrame({
            '계산단계': ['1단계', '2단계', '3단계', '4단계', '5단계'],
            '항목': ['초기투자비용', '연간운영비용', '총운영비용', '잔존가치', '총TCO'],
            '계산식': [
                '구매비용 - 보조금',
                '연료비 + 유지보수비 + 세금보험 + 감가상각 + 기타비용',
                f'연간운영비용 × {ownership_years}년',
                '구매비용 × 잔존가치율',
                '초기투자비용 + 총운영비용 - 잔존가치'
            ],
            '설명': [
                '차량 구매 시 실제 지불 금액',
                '매년 지불하는 운영비용',
                f'{ownership_years}년간 총 운영비용',
                f'{ownership_years}년 후 차량 매각 시 회수 가능한 금액',
                f'{ownership_years}년간 실제 총소유비용'
            ]
        })
        formula_explanation.to_excel(writer, sheet_name='계산식설명', index=False)
    
    print("✅ TCO_분석_입력템플릿.xlsx 파일이 생성되었습니다.")
    print(f"✅ 총 {len(df)} 개의 차량 분류 조합이 생성되었습니다.")
    print(f"✅ {ownership_years}년 소유기간 기준으로 올바른 TCO 계산이 적용되었습니다.")
    
    if existing_data is not None:
        print("✅ 기존 사용자 입력 데이터가 보존되었습니다.")
    
    return df

if __name__ == "__main__":
    create_tco_template() 