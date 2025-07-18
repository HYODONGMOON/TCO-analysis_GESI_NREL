#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
분석 결과 확인 스크립트
"""

import pandas as pd

def check_analysis_results():
    """생성된 분석 결과 파일 확인"""
    try:
        # 세그먼트별 분석 결과 파일 읽기
        excel_file = 'Segment_Sales_Analysis_Results.xlsx'
        
        print("📊 세그먼트별 분석 결과 확인")
        print("="*50)
        
        # Excel 파일의 모든 시트 확인
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        
        print(f"📋 Excel 파일 '{excel_file}'의 시트 목록:")
        for sheet_name in excel_data.keys():
            print(f"  • {sheet_name}")
        
        print("\n" + "="*50)
        
        # 1. 세그먼트별 현황 확인
        if '세그먼트별_현황' in excel_data:
            print("📈 세그먼트별 현황:")
            segment_summary = excel_data['세그먼트별_현황']
            print(segment_summary.to_string(index=False))
        
        print("\n" + "="*50)
        
        # 2. 세그먼트별 요약 확인
        if '세그먼트별_요약' in excel_data:
            print("📊 세그먼트별 요약 (일부):")
            summary = excel_data['세그먼트별_요약']
            print(summary.head(10).to_string(index=False))
        
        print("\n" + "="*50)
        
        # 3. 시나리오별 효과 분석 확인
        if '시나리오별_효과분석' in excel_data:
            print("🎯 시나리오별 효과 분석:")
            scenario_analysis = excel_data['시나리오별_효과분석']
            print(scenario_analysis.to_string(index=False))
        
        print("\n" + "="*50)
        
        # 4. 차량별 상세 결과 확인 (일부)
        if '차량별_상세결과' in excel_data:
            print("🚗 차량별 상세 결과 (일부):")
            detailed = excel_data['차량별_상세결과']
            print(detailed.head(10).to_string(index=False))
        
        return excel_data
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

if __name__ == "__main__":
    check_analysis_results() 