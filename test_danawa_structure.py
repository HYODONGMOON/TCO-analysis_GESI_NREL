#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
다나와 사이트 HTML 구조 확인 테스트 스크립트
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """크롬 드라이버 설정"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--lang=ko-KR')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def test_danawa_structure():
    """다나와 사이트 구조 테스트"""
    driver = setup_driver()
    
    try:
        # 실제 차량 페이지로 직접 접근 (예시 URL)
        test_urls = [
            'https://auto.danawa.com/newcar/?Work=Estimate&Brand=303&Model=4361',  # 현대 아반떼
            'https://auto.danawa.com/newcar/?Work=Estimate&Brand=304&Model=4603',  # 기아 K3
            'https://auto.danawa.com/newcar/?Work=Estimate&Brand=307&Model=4647',  # 제네시스 G80
        ]
        
        for i, url in enumerate(test_urls):
            print(f"\n=== 테스트 {i+1}: {url} ===")
            driver.get(url)
            time.sleep(5)
            
            print(f"페이지 제목: {driver.title}")
            
            # 차량명 찾기
            print("\n=== 차량명 찾기 ===")
            name_selectors = [
                'h1', 'h2', 'h3',
                '.car_name', '.model_name', '.vehicle_name',
                '.title', '.car_title', '.model_title',
                '.car_info h1', '.car_info h2',
                '.vehicle_info h1', '.vehicle_info h2'
            ]
            
            for selector in name_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"\n선택자 '{selector}': {len(elements)}개 발견")
                        for j, elem in enumerate(elements[:3]):
                            text = elem.text.strip()
                            if text and len(text) > 2:
                                print(f"  {j+1}. '{text}'")
                except Exception as e:
                    continue
            
            # 가격 정보 찾기
            print("\n=== 가격 정보 찾기 ===")
            price_selectors = [
                '.price_compare', '.detail_info', '.price_info',
                '.cost_info', '.purchase_info', '.price_detail',
                '.price_section', '.cost_section'
            ]
            
            for selector in price_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"\n선택자 '{selector}': {len(elements)}개 발견")
                        for j, elem in enumerate(elements[:2]):
                            text = elem.text.strip()[:100]
                            if text:
                                print(f"  {j+1}. '{text}...'")
                except Exception as e:
                    continue
            
            # 스펙 정보 찾기
            print("\n=== 스펙 정보 찾기 ===")
            spec_selectors = [
                '.spec_detail', '.spec_info', '.vehicle_spec',
                '.car_spec', '.specification', '.specs',
                '.spec_section', '.vehicle_info'
            ]
            
            for selector in spec_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"\n선택자 '{selector}': {len(elements)}개 발견")
                        for j, elem in enumerate(elements[:2]):
                            text = elem.text.strip()[:100]
                            if text:
                                print(f"  {j+1}. '{text}...'")
                except Exception as e:
                    continue
            
            # 모든 dl 태그 찾기 (가격/스펙 정보용)
            print("\n=== dl 태그 찾기 ===")
            try:
                dl_elements = driver.find_elements(By.TAG_NAME, 'dl')
                print(f"dl 태그 {len(dl_elements)}개 발견")
                for j, dl in enumerate(dl_elements[:5]):
                    try:
                        dt = dl.find_element(By.TAG_NAME, 'dt')
                        dd = dl.find_element(By.TAG_NAME, 'dd')
                        dt_text = dt.text.strip()
                        dd_text = dd.text.strip()
                        if dt_text and dd_text:
                            print(f"  {j+1}. {dt_text}: {dd_text}")
                    except:
                        continue
            except Exception as e:
                print(f"dl 태그 검색 오류: {e}")
        
        input("\n엔터를 눌러서 브라우저를 종료하세요...")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_danawa_structure() 