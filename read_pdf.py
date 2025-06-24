#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 파일 읽기 스크립트
실증 연구 기반 매개변수 확인
"""

import PyPDF2
import re

def read_pdf_content(pdf_path):
    """PDF 파일의 내용을 읽어옵니다."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"PDF 읽기 오류: {e}")
        return None

def extract_key_parameters(text):
    """PDF 내용에서 주요 매개변수들을 추출합니다."""
    parameters = {}
    
    # TCO 관련 매개변수 찾기
    tco_patterns = [
        r'TCO.*?(\d+(?:\.\d+)?).*?%',
        r'(\d+(?:\.\d+)?).*?TCO.*?변화',
        r'(\d+(?:\.\d+)?).*?달러.*?변화',
        r'(\d+(?:\.\d+)?).*?만원.*?변화'
    ]
    
    for pattern in tco_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            parameters['TCO_change_percentage'] = matches[0]
            break
    
    # 차량 가격 관련 매개변수
    price_patterns = [
        r'차량.*?가격.*?(\d+(?:\.\d+)?).*?%',
        r'(\d+(?:\.\d+)?).*?차량.*?가격',
        r'가격.*?임계값.*?(\d+(?:\.\d+)?).*?%'
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            parameters['price_threshold_percentage'] = matches[0]
            break
    
    # 기본 선호도 관련
    preference_patterns = [
        r'기본.*?선호도.*?(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?).*?기본.*?선호',
        r'BEV.*?선호.*?(\d+(?:\.\d+)?)'
    ]
    
    for pattern in preference_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            parameters['base_preference'] = matches[0]
            break
    
    # 민감도 관련
    sensitivity_patterns = [
        r'민감도.*?(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?).*?민감도',
        r'계수.*?(\d+(?:\.\d+)?)'
    ]
    
    for pattern in sensitivity_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            parameters['sensitivity_factor'] = matches[0]
            break
    
    return parameters

def main():
    """메인 함수"""
    pdf_path = "TCO 기반 전기차 소비자 선택 모델 수정_ 실증 연구 기반 매개변수 조정.pdf"
    
    print("="*60)
    print("📄 PDF 파일 읽기 시작")
    print("="*60)
    
    # PDF 내용 읽기
    content = read_pdf_content(pdf_path)
    if content is None:
        print("❌ PDF 파일을 읽을 수 없습니다.")
        return
    
    print(f"✅ PDF 파일 읽기 완료 (총 {len(content)} 문자)")
    
    # 주요 매개변수 추출
    parameters = extract_key_parameters(content)
    
    print("\n" + "="*60)
    print("🔍 추출된 주요 매개변수")
    print("="*60)
    
    if parameters:
        for key, value in parameters.items():
            print(f"{key}: {value}")
    else:
        print("❌ 주요 매개변수를 찾을 수 없습니다.")
    
    # 전체 내용의 일부 출력 (디버깅용)
    print("\n" + "="*60)
    print("📋 PDF 내용 일부 (처음 1000자)")
    print("="*60)
    print(content[:1000])
    
    # 키워드 검색
    keywords = ['TCO', '변화', '달러', '만원', '차량', '가격', '선호도', '민감도', '계수', '매개변수']
    print("\n" + "="*60)
    print("🔍 키워드 검색 결과")
    print("="*60)
    
    for keyword in keywords:
        if keyword in content:
            # 키워드 주변 텍스트 찾기
            index = content.find(keyword)
            start = max(0, index - 50)
            end = min(len(content), index + 100)
            context = content[start:end].replace('\n', ' ')
            print(f"'{keyword}': {context}")

if __name__ == "__main__":
    main() 