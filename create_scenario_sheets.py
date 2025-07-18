#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시나리오 시트 생성 스크립트
"""

import pandas as pd
import numpy as np
from datetime import datetime

def create_scenario_sheets():
    """시나리오1과 시나리오2 시트 생성"""
    
    # 기존 차량분류 시트 읽기
    try:
        base_df = pd.read_excel('TCO_분석_입력템플릿.xlsx', sheet_name='차량분류')
        print(f"✅ 기존 차량분류 시트 로드 완료: {len(base_df)}개 모델")
    except Exception as e:
        print(f"❌ 기존 파일을 찾을 수 없습니다: {e}")
        return
    
    # 시나리오1: ICE 비용 증가 + BEV 보조금 증가
    scenario1_df = base_df.copy()
    
    # 시나리오1 적용
    for idx, row in scenario1_df.iterrows():
        if row['차량유형'] == 'ICE':
            # ICE 차량 비용 10% 증가
            scenario1_df.at[idx, '구매비용_만원'] = row['구매비용_만원'] * 1.10
            scenario1_df.at[idx, '연간연료비_만원'] = row['연간연료비_만원'] * 1.20  # 연료비 20% 증가
        elif row['차량유형'] == 'BEV':
            # BEV 차량 보조금 15% 증가
            scenario1_df.at[idx, '보조금_만원'] = row['보조금_만원'] * 1.15
    
    # 시나리오2: BEV 비용 감소 + 연료가격 상승
    scenario2_df = base_df.copy()
    
    # 시나리오2 적용
    for idx, row in scenario2_df.iterrows():
        if row['차량유형'] == 'BEV':
            # BEV 차량 구매비용 15% 감소
            scenario2_df.at[idx, '구매비용_만원'] = row['구매비용_만원'] * 0.85
            scenario2_df.at[idx, '연간연료비_만원'] = row['연간연료비_만원'] * 0.90  # 전기요금 10% 감소
        elif row['차량유형'] == 'ICE':
            # ICE 차량 연료비 25% 증가
            scenario2_df.at[idx, '연간연료비_만원'] = row['연간연료비_만원'] * 1.25
    
    # 기존 파일에 시나리오 시트 추가
    try:
        with pd.ExcelWriter('TCO_분석_입력템플릿.xlsx', engine='openpyxl', mode='a') as writer:
            scenario1_df.to_excel(writer, sheet_name='시나리오1', index=False)
            scenario2_df.to_excel(writer, sheet_name='시나리오2', index=False)
        
        print("✅ 시나리오1과 시나리오2 시트가 추가되었습니다.")
        
        # 시나리오 요약 출력
        print("\n📊 시나리오1 요약:")
        ice_count1 = len(scenario1_df[scenario1_df['차량유형'] == 'ICE'])
        bev_count1 = len(scenario1_df[scenario1_df['차량유형'] == 'BEV'])
        print(f"  • ICE 차량: {ice_count1}개 (비용 10% 증가, 연료비 20% 증가)")
        print(f"  • BEV 차량: {bev_count1}개 (보조금 15% 증가)")
        
        print("\n📊 시나리오2 요약:")
        ice_count2 = len(scenario2_df[scenario2_df['차량유형'] == 'ICE'])
        bev_count2 = len(scenario2_df[scenario2_df['차량유형'] == 'BEV'])
        print(f"  • ICE 차량: {ice_count2}개 (연료비 25% 증가)")
        print(f"  • BEV 차량: {bev_count2}개 (구매비용 15% 감소, 전기요금 10% 감소)")
        
    except Exception as e:
        print(f"❌ 시나리오 시트 추가 중 오류 발생: {e}")
        
        # 새 파일로 저장
        try:
            with pd.ExcelWriter('TCO_분석_입력템플릿_시나리오추가.xlsx', engine='openpyxl') as writer:
                base_df.to_excel(writer, sheet_name='차량분류', index=False)
                scenario1_df.to_excel(writer, sheet_name='시나리오1', index=False)
                scenario2_df.to_excel(writer, sheet_name='시나리오2', index=False)
            
            print("✅ 새 파일 'TCO_분석_입력템플릿_시나리오추가.xlsx'가 생성되었습니다.")
        except Exception as e2:
            print(f"❌ 새 파일 생성 중 오류 발생: {e2}")

if __name__ == "__main__":
    create_scenario_sheets() 