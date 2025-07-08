#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
다나와 자동차 신차 가격 정보 및 판매실적 수집 스크립트 (Selenium 기반)
차량 가격, 보험료, 취득세, 부대비용, 재원정보 및 판매실적 수집
"""

import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """크롬 드라이버 설정"""
    chrome_options = Options()
    
    # 기본 옵션 설정
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--lang=ko-KR')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User-Agent 설정
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # 창 크기 설정
    chrome_options.add_argument('--window-size=1920,1080')
    
    # headless 모드 (브라우저 창 안 띄우기) - 테스트 시에는 주석 처리
    # chrome_options.add_argument('--headless')
    
    # 크롬드라이버 자동 설치 및 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 자동화 감지 방지
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def get_car_list(driver, main_url):
    """신차검색 페이지에서 차량 목록 수집"""
    car_list = []
    page = 1
    max_pages = 50  # 전체 모델 수집을 위해 충분히 큰 값으로 설정
    
    print("차량 목록 수집 중...")
    
    while page <= max_pages:
        try:
            # 페이지 URL 구성
            if page == 1:
                url = main_url
            else:
                # URL에서 page 파라미터 업데이트
                if 'page=' in main_url:
                    url = main_url.replace('page=1', f'page={page}')
                else:
                    url = main_url + f'&page={page}'
            
            print(f"페이지 {page} 접속 중: {url}")
            driver.get(url)
            time.sleep(random.uniform(3, 4))
            
            # 차량 목록 찾기 (개선된 선택자)
            car_selectors = [
                'a[name="modelDetailLink"]',  # 차량 링크
                '.name.sendGA',  # 차량명 클래스
                'a[href*="javascript:void(0);"][model]',  # 모델 정보가 있는 링크
                '.car_item a',  # 차량 아이템 링크
                '.vehicle_item a'  # 차량 아이템 링크
            ]
            
            page_cars = []
            for selector in car_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        try:
                            # 모델 ID 추출
                            model_id = element.get_attribute('model')
                            if not model_id:
                                # href에서 모델 ID 추출 시도
                                href = element.get_attribute('href')
                                if href and 'model=' in href:
                                    model_id = href.split('model=')[1].split('&')[0]
                            
                            # 차량명 추출
                            car_name = element.text.strip()
                            
                            if model_id and car_name and len(car_name) > 2:
                                car_info = {
                                    'model_id': model_id,
                                    'car_name': car_name,
                                    'tco_url': f'https://auto.danawa.com/next/auto/tco?Model={model_id}'
                                }
                                page_cars.append(car_info)
                        except Exception as e:
                            continue
                
                    if page_cars:
                        print(f"선택자 '{selector}'로 {len(page_cars)}개 차량 발견")
                        break
                except Exception as e:
                    print(f"선택자 '{selector}' 처리 중 오류: {e}")
                    continue
            
            if not page_cars:
                print(f"페이지 {page}에서 더 이상 차량을 찾을 수 없습니다.")
                break
            
            # 중복 제거
            new_cars = []
            for car in page_cars:
                if car not in car_list:
                    new_cars.append(car)
            
            car_list.extend(new_cars)
            print(f"페이지 {page}: {len(new_cars)}개 차량 수집 (총 {len(car_list)}개)")
            
            # 다음 페이지로
            page += 1
            
            # 서버 부하 방지
            time.sleep(random.uniform(2, 3))
            
        except Exception as e:
            print(f"페이지 {page} 처리 중 오류 발생: {e}")
            break

    print(f"총 {len(car_list)}개 차량 목록 수집 완료")
    return car_list

def get_car_detail_info(driver, car_info):
    """개별 차량의 상세 정보 추출"""
    try:
        print(f"차량 정보 수집 중: {car_info['car_name']}")
        
        # TCO 페이지 접속
        driver.get(car_info['tco_url'])
        time.sleep(random.uniform(4, 5))
        
        car_data = {
            '모델명': car_info['car_name'],
            '차종': '',
            '연료': '',
            '배기량': '',
            '차량가격': '',
            '취득세/부대비용': '',
            '보험료(년)': ''
        }
        
        # 차량 기본 정보 추출 (차종, 연료, 배기량)
        try:
            # 차종 정보 - 더 일반적인 선택자 사용
            segment_selectors = [
                'p.leading-[20px]',
                '.vehicle_info p',
                '.car_info p',
                '.spec_info p',
                '.car_spec p',
                'p.text-dnw-gray-800'
            ]
            
            for selector in segment_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if 'SUV' in text or '세단' in text or '해치백' in text or '왜건' in text:
                            car_data['차종'] = text
                            break
                    if car_data['차종']:
                        break
                except:
                    continue
            
            # 연료 정보
            fuel_selectors = [
                'p.leading-[20px]',
                '.fuel_info p',
                '.engine_info p',
                'p.text-dnw-gray-800'
            ]
            
            for selector in fuel_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if any(keyword in text for keyword in ['가솔린', '디젤', '전기', '하이브리드', 'LPG']):
                            car_data['연료'] = text
                            break
                    if car_data['연료']:
                        break
                except:
                    continue
            
            # 배기량 정보
            displacement_selectors = [
                'p.leading-[20px]',
                '.engine_spec p',
                '.displacement_info p',
                'p.text-dnw-gray-800'
            ]
            
            for selector in displacement_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if 'cc' in text or '배기량' in text:
                            car_data['배기량'] = text
                            break
                    if car_data['배기량']:
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"차량 기본 정보 추출 실패: {e}")
        
        # 구매 비용 정보 추출 - 수정된 선택자 사용
        try:
            # 차량 가격 - 위치 기반 수집
            price_selectors = [
                'p.mt-[4px].text-right.tracking-tight.text-[14px].leading-[21px].font-bold.undefined',
                'p.mt-[4px].text-right.tracking-tight.text-[14px].leading-[21px].font-bold',
                'p.text-right.font-bold',
                '.price_info p.text-right'
            ]
            
            for selector in price_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and text.replace(',', '').replace('원', '').isdigit():
                            amount = int(text.replace(',', '').replace('원', ''))
                            if amount > 10000000:  # 1000만원 이상
                                car_data['차량가격'] = text
                                break
                    if car_data['차량가격']:
                        break
                except:
                    continue
            
            # 취득세/부대비용 - 위치 기반 수집
            tax_selectors = [
                'p.mt-[4px].text-right.tracking-tight.text-[14px].leading-[21px].font-bold.undefined',
                'p.mt-[4px].text-right.tracking-tight.text-[14px].leading-[21px].font-bold',
                'p.text-right.font-bold',
                '.tax_info p.text-right'
            ]
            
            for selector in tax_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and text.replace(',', '').replace('원', '').isdigit():
                            amount = int(text.replace(',', '').replace('원', ''))
                            if 1000000 <= amount <= 10000000:  # 100만원~1000만원
                                car_data['취득세/부대비용'] = text
                                break
                    if car_data['취득세/부대비용']:
                        break
                except:
                    continue
            
            # 보험료 - 의미 기반으로 수집 (차량 구매 비용 비교 섹션에서)
            insurance_found = False
            try:
                # 페이지에서 "보험료(년)" 텍스트가 포함된 모든 요소 찾기
                insurance_text_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '보험료(년)')]")
                
                for element in insurance_text_elements:
                    try:
                        # 부모 요소에서 금액 찾기
                        parent = element.find_element(By.XPATH, "./..")
                        text_elements = parent.find_elements(By.TAG_NAME, "p")
                        
                        for text_element in text_elements:
                            text = text_element.text.strip()
                            if text and text.replace(',', '').replace('원', '').isdigit():
                                amount = int(text.replace(',', '').replace('원', ''))
                                # 보험료는 보통 50만원~200만원 정도
                                if 500000 <= amount <= 2000000:
                                    car_data['보험료(년)'] = text
                                    insurance_found = True
                                    print(f"보험료 찾음: {text}")
                                    break
                        
                        if insurance_found:
                            break
                            
                    except Exception as e:
                        continue
                
                # 의미 기반으로 찾지 못한 경우, 위치 기반으로 백업
                if not insurance_found:
                    print("의미 기반 보험료 검색 실패, 위치 기반으로 백업...")
                    insurance_selectors = [
                        'p.mt-[4px].text-right.tracking-tight.text-[14px].leading-[21px].font-bold.undefined',
                        'p.mt-[4px].text-right.tracking-tight.text-[14px].leading-[21px].font-bold',
                        'p.text-right.font-bold',
                        '.insurance_info p.text-right'
                    ]
                    
                    for selector in insurance_selectors:
                        try:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                text = element.text.strip()
                                if text and text.replace(',', '').replace('원', '').isdigit():
                                    amount = int(text.replace(',', '').replace('원', ''))
                                    # 보험료는 보통 50만원~200만원 정도
                                    if 500000 <= amount <= 2000000:
                                        car_data['보험료(년)'] = text
                                        break
                            if car_data['보험료(년)']:
                                break
                        except:
                            continue
                    
                    # 캐쉬백 혜택이 보험료로 잘못 연결된 경우 수정
                    if car_data['보험료(년)']:
                        try:
                            # 캐쉬백 혜택 확인 (파란색 텍스트)
                            cashback_elements = driver.find_elements(By.CSS_SELECTOR, 'p.mt-[4px].text-right.tracking-tight.text-[14px].leading-[21px].font-bold.text-dnw-blue-450')
                            for element in cashback_elements:
                                text = element.text.strip()
                                if text and text.replace(',', '').replace('원', '').isdigit():
                                    amount = int(text.replace(',', '').replace('원', ''))
                                    # 캐쉬백은 보통 30만원~50만원 정도
                                    if 300000 <= amount <= 500000:
                                        # 실제 보험료 찾기 (undefined 클래스)
                                        real_insurance_elements = driver.find_elements(By.CSS_SELECTOR, 'p.mt-[4px].text-right.tracking-tight.text-[14px].leading-[21px].font-bold.undefined')
                                        for ins_element in real_insurance_elements:
                                            ins_text = ins_element.text.strip()
                                            if ins_text and ins_text.replace(',', '').replace('원', '').isdigit():
                                                ins_amount = int(ins_text.replace(',', '').replace('원', ''))
                                                # 보험료는 보통 100만원~200만원 정도
                                                if 1000000 <= ins_amount <= 2000000:
                                                    car_data['보험료(년)'] = ins_text
                                                    break
                                        break
                        except:
                            pass
                            
            except Exception as e:
                print(f"보험료 수집 중 오류: {e}")
        
        except Exception as e:
            print(f"구매 비용 정보 추출 실패: {e}")
        
        # 페이지 소스에서 직접 정보 추출 시도 (백업 방법)
        if not car_data['차량가격'] or not car_data['취득세/부대비용'] or not car_data['보험료(년)']:
            try:
                page_source = driver.page_source
                
                # 차량 가격 패턴 찾기
                import re
                price_pattern = r'(\d{1,3}(?:,\d{3})*)\s*원'
                prices = re.findall(price_pattern, page_source)
                
                if prices:
                    # 가장 큰 금액을 차량 가격으로
                    max_price = max([int(p.replace(',', '')) for p in prices])
                    car_data['차량가격'] = f"{max_price:,}원"
                    
                    # 나머지 금액들을 취득세/부대비용, 보험료로 분류
                    other_prices = [p for p in prices if int(p.replace(',', '')) < max_price]
                    if len(other_prices) >= 2:
                        car_data['취득세/부대비용'] = f"{int(other_prices[0].replace(',', '')):,}원"
                        car_data['보험료(년)'] = f"{int(other_prices[1].replace(',', '')):,}원"
                        
            except Exception as e:
                print(f"페이지 소스에서 정보 추출 실패: {e}")
        
        return car_data
        
    except Exception as e:
        print(f"차량 정보 추출 중 오류 발생 ({car_info['car_name']}): {e}")
        return None

def get_sales_data(driver):
    """판매실적 데이터 수집"""
    print("\n📊 판매실적 데이터 수집을 시작합니다...")
    
    try:
        # 1. 판매실적 페이지로 이동
        sales_url = 'https://auto.danawa.com/newcar/?Work=record'
        print("판매실적 페이지 접속 중...")
        driver.get(sales_url)
        time.sleep(random.uniform(3, 4))
        
        # 2. 모델별 탭 클릭
        print("모델별 탭 클릭 중...")
        model_tab_selectors = [
            'button[type="button"]:contains("모델별")',
            'button:contains("모델별")',
            '.tab_button:contains("모델별")',
            'a:contains("모델별")'
        ]
        
        model_tab_clicked = False
        for selector in model_tab_selectors:
            try:
                # JavaScript로 텍스트가 포함된 버튼 찾기
                if ':contains' in selector:
                    text = selector.split('contains("')[1].split('")')[0]
                    elements = driver.find_elements(By.TAG_NAME, 'button')
                    for element in elements:
                        if text in element.text:
                            element.click()
                            model_tab_clicked = True
                            print(f"모델별 탭 클릭 성공")
                            break
                    if model_tab_clicked:
                        break
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        elements[0].click()
                        model_tab_clicked = True
                        print(f"모델별 탭 클릭 성공")
                        break
            except Exception as e:
                print(f"선택자 '{selector}' 처리 중 오류: {e}")
                continue
        
        if not model_tab_clicked:
            print("모델별 탭을 찾을 수 없습니다. 페이지 구조를 확인해주세요.")
            return []
        
        time.sleep(random.uniform(2, 3))
        
        # 3. 기간 설정 (2024년 7월 ~ 2025년 6월)
        print("기간 설정 중...")
        try:
            # 1) 기간 선택 라디오 버튼 클릭
            period_radio_selectors = [
                'input[name="rdoMonthPeriod"][value="period"]',
                'input[type="radio"][value="period"]',
                'input[name="rdoMonthPeriod"]'
            ]
            
            period_radio_clicked = False
            for selector in period_radio_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.get_attribute('value') == 'period':
                            element.click()
                            period_radio_clicked = True
                            print("기간 선택 라디오 버튼 클릭 성공")
                            break
                    if period_radio_clicked:
                        break
                except Exception as e:
                    print(f"기간 선택 라디오 버튼 처리 중 오류: {e}")
                    continue
            
            time.sleep(random.uniform(1, 2))
            
            # 2) 시작 연도 설정 (2024년)
            start_year_selectors = [
                '#selMonthFrom',
                'select[id="selMonthFrom"]',
                'select[name="selMonthFrom"]'
            ]
            
            for selector in start_year_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        from selenium.webdriver.support.ui import Select
                        select = Select(elements[0])
                        select.select_by_value('2024')
                        print("시작 연도 2024년 설정 완료")
                        break
                except Exception as e:
                    print(f"시작 연도 설정 중 오류: {e}")
                    continue
            
            time.sleep(random.uniform(1, 2))
            
            # 3) 시작 월 설정 (7월)
            start_month_selectors = [
                '#selDayFrom',
                'select[id="selDayFrom"]',
                'select[name="selDayFrom"]'
            ]
            
            for selector in start_month_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        from selenium.webdriver.support.ui import Select
                        select = Select(elements[0])
                        select.select_by_value('07')
                        print("시작 월 7월 설정 완료")
                        break
                except Exception as e:
                    print(f"시작 월 설정 중 오류: {e}")
                    continue
            
            time.sleep(random.uniform(1, 2))
            
            # 4) 종료 연도 설정 (2025년)
            end_year_selectors = [
                '#selMonthTo',
                'select[id="selMonthTo"]',
                'select[name="selMonthTo"]'
            ]
            
            for selector in end_year_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        from selenium.webdriver.support.ui import Select
                        select = Select(elements[0])
                        select.select_by_value('2025')
                        print("종료 연도 2025년 설정 완료")
                        break
                except Exception as e:
                    print(f"종료 연도 설정 중 오류: {e}")
                    continue
            
            time.sleep(random.uniform(1, 2))
            
            # 5) 종료 월 설정 (6월)
            end_month_selectors = [
                '#selDayTo',
                'select[id="selDayTo"]',
                'select[name="selDayTo"]'
            ]
            
            for selector in end_month_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        from selenium.webdriver.support.ui import Select
                        select = Select(elements[0])
                        select.select_by_value('06')
                        print("종료 월 6월 설정 완료")
                        break
                except Exception as e:
                    print(f"종료 월 설정 중 오류: {e}")
                    continue
            
            time.sleep(random.uniform(2, 3))
            
        except Exception as e:
            print(f"기간 설정 중 오류: {e}")
        
        # 4. 조회 버튼 클릭
        print("조회 버튼 클릭 중...")
        search_selectors = [
            'input[type="button"][value="조회"]',
            'input[onclick*="selectRecord"]',
            'input[type="button"]:contains("조회")',
            'button:contains("조회")',
            'input[type="submit"]',
            '.search_button',
            '.submit_button'
        ]
        
        search_clicked = False
        for selector in search_selectors:
            try:
                if ':contains' in selector:
                    text = selector.split('contains("')[1].split('")')[0]
                    elements = driver.find_elements(By.TAG_NAME, 'input')
                    for element in elements:
                        if text in element.get_attribute('value', ''):
                            element.click()
                            search_clicked = True
                            print("조회 버튼 클릭 성공")
                            break
                    if search_clicked:
                        break
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.get_attribute('type') == 'button' and '조회' in element.get_attribute('value', ''):
                            element.click()
                            search_clicked = True
                            print("조회 버튼 클릭 성공")
                            break
                    if search_clicked:
                        break
            except Exception as e:
                print(f"조회 버튼 처리 중 오류: {e}")
                continue
        
        if not search_clicked:
            print("조회 버튼을 찾을 수 없습니다. JavaScript로 직접 실행합니다.")
            try:
                driver.execute_script("selectRecord('period');")
                print("JavaScript로 조회 실행 성공")
            except Exception as e:
                print(f"JavaScript 실행 중 오류: {e}")
        
        time.sleep(random.uniform(4, 5))
        
        # 5. 판매 데이터 수집 - 수정된 선택자 사용
        print("판매 데이터 수집 중...")
        sales_data = []
        
        # 테이블에서 데이터 추출 - 수정된 선택자
        table_selectors = [
            'table',
            '.sales_table',
            '.data_table',
            '.result_table'
        ]
        
        for selector in table_selectors:
            try:
                tables = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    
                    for row in rows:
                        try:
                            cells = row.find_elements(By.TAG_NAME, 'td')
                            
                            if len(cells) >= 3:  # 최소 3개 컬럼 (모델명, 판매량, 점유율)
                                car_name = ''
                                sales_volume = ''
                                market_share = ''
                                
                                # 모델명 추출 - 수정된 선택자
                                name_cells = row.find_elements(By.CSS_SELECTOR, 'td.title span, td.title')
                                if name_cells:
                                    car_name = name_cells[0].text.strip()
                                
                                # 판매량 추출 - 수정된 선택자
                                volume_cells = row.find_elements(By.CSS_SELECTOR, 'td.num')
                                if volume_cells:
                                    sales_volume = volume_cells[0].text.strip()
                                
                                # 점유율 추출 - 수정된 선택자
                                share_cells = row.find_elements(By.CSS_SELECTOR, 'td:not(.num):not(.title)')
                                for cell in share_cells:
                                    text = cell.text.strip()
                                    if '%' in text:
                                        market_share = text
                                        break
                                
                                if car_name and sales_volume:
                                    sales_data.append({
                                        '모델명': car_name,
                                        '판매량': sales_volume,
                                        '점유율': market_share
                                    })
                                    
                        except Exception as e:
                            continue
                    
                    if sales_data:
                        print(f"테이블에서 {len(sales_data)}개 데이터 수집")
                        break
                
                if sales_data:
                    break
                    
            except Exception as e:
                print(f"테이블 처리 중 오류: {e}")
                continue
        
        # 6. 세부 모델 데이터 수집 (등급별 보기)
        print("세부 모델 데이터 수집 중...")
        detail_sales_data = []
        
        # 등급별 보기 버튼 찾기
        detail_button_selectors = [
            'button.viewMore',
            'button[class*="viewMore"]',
            'button:contains("등급별 보기")'
        ]
        
        for selector in detail_button_selectors:
            try:
                if ':contains' in selector:
                    text = selector.split('contains("')[1].split('")')[0]
                    elements = driver.find_elements(By.TAG_NAME, 'button')
                    for element in elements:
                        if text in element.text:
                            # 모델 ID 추출
                            model_id = element.get_attribute('model')
                            if model_id:
                                print(f"세부 모델 데이터 수집: {model_id}")
                                # 여기서 세부 모델 데이터를 수집하는 로직 추가
                                # 실제 구현은 사이트 구조에 따라 달라질 수 있음
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        model_id = element.get_attribute('model')
                        if model_id:
                            print(f"세부 모델 데이터 수집: {model_id}")
                            # 세부 모델 데이터 수집 로직
            except Exception as e:
                continue
        
        return sales_data
        
    except Exception as e:
        print(f"판매실적 데이터 수집 중 오류 발생: {e}")
        return []

def main():
    """메인 함수"""
    # 다나와 신차검색 페이지 URL
    main_url = 'https://auto.danawa.com/newcar/?listSortType=1&tab=all&rangeMinPrice=&rangeMaxPrice=&searchKeyword=&listCount=30&page=1&brandList=&segmentList=&attributeList='
    
    print("🚗 다나와 자동차 신차 가격 정보 및 판매실적 수집을 시작합니다...")
    print("="*60)
    
    # 드라이버 설정
    driver = setup_driver()
    
    try:
        # 1. 차량 가격 정보 수집
        print("📋 1단계: 차량 가격 정보 수집")
        car_list = get_car_list(driver, main_url)

    all_car_data = []
        if car_list:
            # 개별 차량 정보 수집
            success_count = 0
            error_count = 0
            
            print(f"\n📊 {len(car_list)}개 차량의 상세 정보 수집 중...")
            
            for i, car_info in enumerate(car_list, 1):
                try:
                    data = get_car_detail_info(driver, car_info)
                    if data:
            all_car_data.append(data)
                        success_count += 1
                        print(f"[{i}/{len(car_list)}] ✅ {data['모델명']} - {data['차종']}")
                    else:
                        error_count += 1
                        print(f"[{i}/{len(car_list)}] ❌ 데이터 추출 실패")
                        
        except Exception as e:
                    error_count += 1
                    print(f"[{i}/{len(car_list)}] ❌ 오류: {e}")
                
                # 서버 부하 방지
                time.sleep(random.uniform(2, 3))
            
            print(f"\n📈 차량 가격 정보 수집 결과:")
            print(f"• 총 차량 수: {len(car_list)}")
            print(f"• 성공: {success_count}")
            print(f"• 실패: {error_count}")
            print(f"• 성공률: {success_count/len(car_list)*100:.1f}%")
            
            # 차종별 통계
            segment_stats = {}
            for car_data in all_car_data:
                segment = car_data.get('차종', '')
                segment_stats[segment] = segment_stats.get(segment, 0) + 1
            
            print(f"\n📊 차종별 분포:")
            for segment, count in segment_stats.items():
                print(f"• {segment}: {count}개")
        
        # 2. 판매실적 데이터 수집
        print("\n📋 2단계: 판매실적 데이터 수집")
        sales_data = get_sales_data(driver)
        
        # 3. 결과 저장
        filename = 'car_price_spec_data_detailed.xlsx'
        
        with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
            # 가격 정보 시트
            if all_car_data:
                df_price = pd.DataFrame(all_car_data)
                df_price.to_excel(writer, sheet_name='차량가격정보', index=False)
                print(f"\n💾 차량 가격 정보가 '{filename}'의 '차량가격정보' 시트에 저장되었습니다.")
            
            # 판매실적 시트
            if sales_data:
                df_sales = pd.DataFrame(sales_data)
                df_sales.to_excel(writer, sheet_name='판매실적', index=False)
                print(f"💾 판매실적 데이터가 '{filename}'의 '판매실적' 시트에 저장되었습니다.")
                
                print(f"\n📊 판매실적 수집 결과:")
                print(f"• 총 모델 수: {len(sales_data)}")
                
                # 샘플 데이터 출력
                print(f"\n📋 판매실적 샘플 데이터 (처음 5개):")
                print(df_sales.head().to_string(index=False))
            else:
                print("❌ 판매실적 데이터 수집에 실패했습니다.")
        
        if not all_car_data and not sales_data:
            print("❌ 수집된 데이터가 없습니다.")
        
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
    
    finally:
        # 드라이버 종료
        driver.quit()
        print("\n🔚 크롤링 완료!")

if __name__ == "__main__":
    main()