#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 파일에서 정확한 매개변수값 추출
"""

import PyPDF2
import re

def extract_pdf_parameters():
    """PDF에서 매개변수값 추출"""
    
    file_path = 'TCO 기반 전기차 소비자 선택 모델 수정_ 실증 연구 기반 매개변수 조정.pdf'
    
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
        
        print("="*80)
        print("📄 PDF 파일 매개변수 추출")
        print("="*80)
        
        # 주요 매개변수 검색
        print("🔍 주요 매개변수 검색:")
        
        # 가격 탄력성 검색
        price_elasticity_patterns = [
            r'가격 탄력성[:\s]*(-?\d+\.?\d*)',
            r'price elasticity[:\s]*(-?\d+\.?\d*)',
            r'(-?\d+\.?\d*)[\s]*~[\s]*(-?\d+\.?\d*)',
            r'전기차.*가격 탄력성[:\s]*(-?\d+\.?\d*)',
            r'(-?\d+\.?\d*)[\s]*~[\s]*(-?\d+\.?\d*).*전기차'
        ]
        
        for pattern in price_elasticity_patterns:
            matches = re.findall(pattern, text)
            if matches:
                print(f"   가격 탄력성 패턴 '{pattern}': {matches}")
        
        # 기본 선호도 검색
        base_preference_patterns = [
            r'기본선호도[:\s]*(\d+\.?\d*)',
            r'base preference[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)%.*기본선호도',
            r'기본.*선호도[:\s]*(\d+\.?\d*)',
            r'순수 기술 선호자.*(\d+\.?\d*)'
        ]
        
        for pattern in base_preference_patterns:
            matches = re.findall(pattern, text)
            if matches:
                print(f"   기본 선호도 패턴 '{pattern}': {matches}")
        
        # 시장 점유율 효과 검색
        market_share_patterns = [
            r'시장.*점유율[:\s]*(\d+\.?\d*)',
            r'market share[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)%.*시장',
            r'시장.*(\d+\.?\d*)%'
        ]
        
        for pattern in market_share_patterns:
            matches = re.findall(pattern, text)
            if matches:
                print(f"   시장 점유율 패턴 '{pattern}': {matches}")
        
        # 숫자 매개변수 전체 검색
        print(f"\n📊 전체 숫자 매개변수 (처음 30개):")
        all_numbers = re.findall(r'(-?\d+\.?\d*)', text)
        print(f"   {all_numbers[:30]}")
        
        # 특정 키워드 주변 검색
        print(f"\n🔍 키워드 주변 매개변수:")
        
        # "전기차 가격 탄력성" 주변
        ev_elasticity_context = re.findall(r'.{0,50}전기차.*가격.*탄력성.{0,50}', text)
        for context in ev_elasticity_context[:3]:
            print(f"   전기차 가격 탄력성 컨텍스트: {context}")
        
        # "기본선호도" 주변
        base_pref_context = re.findall(r'.{0,50}기본선호도.{0,50}', text)
        for context in base_pref_context[:3]:
            print(f"   기본선호도 컨텍스트: {context}")
        
        # "시장점유율" 주변
        market_context = re.findall(r'.{0,50}시장.*점유율.{0,50}', text)
        for context in market_context[:3]:
            print(f"   시장점유율 컨텍스트: {context}")
        
        # 현재 코드에서 사용하는 값과 비교
        print(f"\n🔄 현재 코드 vs PDF 매개변수 비교:")
        print(f"   현재 코드:")
        print(f"     • EV Price Elasticity: -2.5")
        print(f"     • Base Preference: 0.175 (17.5%)")
        print(f"     • Market Share Effect: 0.15 (15%)")
        
        # PDF에서 추출된 값들
        print(f"\n   PDF에서 추출된 값들:")
        print(f"     • TCO_change_percentage: 1")
        print(f"     • price_threshold_percentage: 10")
        print(f"     • base_preference: 30")
        print(f"     • sensitivity_factor: 25")
        
        return text
        
    except Exception as e:
        print(f"❌ PDF 읽기 오류: {e}")
        return None

if __name__ == "__main__":
    extract_pdf_parameters() 