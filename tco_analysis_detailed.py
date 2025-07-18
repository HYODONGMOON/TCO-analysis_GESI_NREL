#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed TCO Analysis by Vehicle Model (16 vehicle types individual analysis)
Empirical research-based parameters applied
Extended with segment-based sales volume analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import warnings
import os
from datetime import datetime
import matplotlib.font_manager as fm

warnings.filterwarnings('ignore')

# Set Korean font for matplotlib
def setup_korean_font():
    """한글 폰트 설정"""
    try:
        # Windows에서 가장 안정적인 한글 폰트 설정
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
        print("✅ 한글 폰트 설정 완료: Malgun Gothic")
    except:
        try:
            # 대안 폰트
            plt.rcParams['font.family'] = 'DejaVu Sans'
            plt.rcParams['axes.unicode_minus'] = False
            print("✅ 폰트 설정 완료: DejaVu Sans")
        except:
            # 기본 설정
            plt.rcParams['font.family'] = ['sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            print("⚠️ 기본 폰트 사용")

# 폰트 설정 실행
setup_korean_font()

class SegmentSalesAnalyzer:
    """세그먼트별 판매량 변화 분석 클래스"""
    
    def __init__(self):
        """세그먼트별 분석 초기화"""
        # 실제 데이터의 세그먼트 정의
        self.segments = {
            'B1': '소형차',
            'C1': '준중형차', 
            'D1': '중형차',
            'E1': '대형차',
            'D2': '중형SUV',
            'E2': '대형SUV'
        }
        
        # 소유 기간 설정
        self.ownership_years = 5
        
        # 연료별 온실가스 배출계수 (kgCO2/L)
        self.emission_factors = {
            '가솔린': 2.1797,
            '디젤': 2.5950,
            '전기': 0.0  # 전기차는 직접 배출 없음
        }
        
        # 연평균 운행거리 (km/년)
        self.annual_mileage = {
            '승용차': 15000,
            '소형화물': 56609,
            '중형화물1': 70752,
            '중형화물2': 89981,
            '대형화물1': 166007,
            '대형화물2': 138146,
            '대형화물3': 103428
        }
        
        # 결과 저장 폴더 생성
        self.create_results_folder()
    
    def create_results_folder(self):
        """분석 완료 시간을 폴더명으로 하는 결과 폴더 생성"""
        current_time = datetime.now()
        folder_name = current_time.strftime("%Y%m%d_%H%M%S")
        self.results_folder = f"분석결과_{folder_name}"
        
        if not os.path.exists(self.results_folder):
            os.makedirs(self.results_folder)
            print(f"📁 결과 저장 폴더 생성: {self.results_folder}")
        
        return self.results_folder
    
    def calculate_ghg_emissions(self, vehicle_data):
        """온실가스 배출량 계산"""
        emissions_data = []
        
        for idx, row in vehicle_data.iterrows():
            # 차량 정보 추출
            vehicle_name = row['차량명'] if '차량명' in row else row['소분류']
            vehicle_type = row['차량유형']
            main_category = row['대분류'] if '대분류' in row else '승용차'
            fuel_efficiency = row['연비'] if '연비' in row and pd.notna(row['연비']) else 0
            
            # 연료 종류 결정
            if vehicle_type == 'BEV':
                fuel_type = '전기'
            elif main_category == '화물':
                fuel_type = '디젤'
            else:
                fuel_type = '가솔린'
            
            # 연평균 운행거리 결정
            if main_category == '화물':
                # 화물차 세부 분류에 따른 운행거리
                sub_category = row['중분류'] if '중분류' in row else '소형화물'
                annual_distance = self.annual_mileage.get(sub_category, 15000)
            else:
                annual_distance = self.annual_mileage['승용차']
            
            # 온실가스 배출계수
            emission_factor = self.emission_factors.get(fuel_type, 0.0)
            
            # 온실가스 배출량 계산 (kgCO2/년)
            if fuel_efficiency > 0:
                ghg_emission = annual_distance * emission_factor / fuel_efficiency
                # 디버깅용 출력 (모든 화물차)
                if main_category == '화물':
                    print(f"🔍 {vehicle_name} ({sub_category}):")
                    print(f"   연평균운행거리: {annual_distance:,.0f} km/년")
                    print(f"   연비: {fuel_efficiency:.1f} km/L")
                    print(f"   배출계수: {emission_factor:.4f} kgCO2/L")
                    print(f"   연간배출량: {ghg_emission:,.0f} kgCO2/년")
                    print(f"   차량대수: {row['차량대수'] if '차량대수' in row else 1}")
                    print(f"   총배출량: {ghg_emission * (row['차량대수'] if '차량대수' in row else 1):,.0f} kgCO2/년")
                    print(f"   계산식: {annual_distance:,.0f} × {emission_factor:.4f} ÷ {fuel_efficiency:.1f} × {row['차량대수'] if '차량대수' in row else 1} = {ghg_emission * (row['차량대수'] if '차량대수' in row else 1):,.0f}")
                    print()
            else:
                ghg_emission = 0.0
            
            emissions_data.append({
                '차량명': vehicle_name,
                '차량유형': vehicle_type,
                '대분류': main_category,
                '연료종류': fuel_type,
                '연비': fuel_efficiency,
                '연평균운행거리_km': annual_distance,
                '온실가스배출계수_kgCO2_L': emission_factor,
                '연간온실가스배출량_kgCO2': ghg_emission,
                '차량대수': row['차량대수'] if '차량대수' in row else 1,
                '총온실가스배출량_kgCO2': ghg_emission * (row['차량대수'] if '차량대수' in row else 1)
            })
        
        return pd.DataFrame(emissions_data)
    
    def get_segment_data(self, vehicle_data, segment):
        """특정 세그먼트의 차량 데이터 추출"""
        segment_data = vehicle_data[vehicle_data['중분류'] == segment].copy()
        
        if segment_data.empty:
            return pd.DataFrame()
        
        # 시장점유율 계산
        total_sales = segment_data['차량대수'].sum()
        
        # 각 차량별 시장점유율 및 브랜드파워 계산
        market_shares = []
        for _, vehicle in segment_data.iterrows():
            share = vehicle['차량대수'] / total_sales if total_sales > 0 else 0
            
            # 브랜드파워 계산 (구매지수만 사용)
            purchase_index = vehicle['구매지수'] if '구매지수' in vehicle and pd.notna(vehicle['구매지수']) else 0
            brand_power = purchase_index
            
            market_shares.append({
                '차량명': vehicle['소분류'],
                '차량유형': vehicle['차량유형'],
                '차량등급': vehicle['차량등급'],
                '현재판매량': vehicle['차량대수'],
                '현재시장점유율': share,
                'TCO_만원': vehicle['총TCO_만원'],
                '초기투자비용_만원': vehicle['초기투자비용_만원'],
                '구매지수': purchase_index,
                '관성계수': vehicle['관성계수'] if '관성계수' in vehicle and pd.notna(vehicle['관성계수']) else 1.0,
                '브랜드파워': brand_power
            })
        
        return pd.DataFrame(market_shares)
    
    def calculate_choice_probability_matrix(self, segment_data):
        """세그먼트 내 차량 간 선택 확률 매트릭스 계산 (동일 등급 내에서만)"""
        vehicles = segment_data['차량명'].tolist()
        vehicle_grades = segment_data['차량등급'].tolist()
        n_vehicles = len(vehicles)
        probability_matrix = np.zeros((n_vehicles, n_vehicles))
        base_probabilities = {}
        for i, vehicle_i in enumerate(vehicles):
            for j, vehicle_j in enumerate(vehicles):
                if i != j and vehicle_grades[i] == vehicle_grades[j]:
                    tco_i = segment_data.iloc[i]['TCO_만원']
                    tco_j = segment_data.iloc[j]['TCO_만원']
                    price_i = segment_data.iloc[i]['초기투자비용_만원']
                    price_j = segment_data.iloc[j]['초기투자비용_만원']
                    tco_diff = tco_j - tco_i
                    avg_price = (price_i + price_j) / 2
                    grade_i = segment_data.iloc[i]['차량등급']
                    grade_j = segment_data.iloc[j]['차량등급']
                    sensitivity_i = 1.2 if grade_i == 'volume' else 0.8 if grade_i == 'premium' else 1.0
                    sensitivity_j = 1.2 if grade_j == 'volume' else 0.8 if grade_j == 'premium' else 1.0
                    avg_sensitivity = (sensitivity_i + sensitivity_j) / 2
                    adjusted_tco_diff = tco_diff * avg_sensitivity
                    purchase_index_i = segment_data.iloc[i]['구매지수'] if pd.notna(segment_data.iloc[i]['구매지수']) else 0
                    purchase_index_j = segment_data.iloc[j]['구매지수'] if pd.notna(segment_data.iloc[j]['구매지수']) else 0
                    brand_power_i = purchase_index_i
                    brand_power_j = purchase_index_j
                    base_probability, _ = self.calculate_empirical_bev_probability(adjusted_tco_diff, avg_price, brand_power_i, brand_power_j)
                    inertia_i = segment_data.iloc[i]['관성계수'] if pd.notna(segment_data.iloc[i]['관성계수']) else 0.0
                    inertia_j = segment_data.iloc[j]['관성계수'] if pd.notna(segment_data.iloc[j]['관성계수']) else 0.0
                    final_probability = base_probability + inertia_j - inertia_i
                    final_probability = np.clip(final_probability, 0, 1)
                    probability_matrix[i][j] = final_probability
                    base_probabilities[(i, j)] = {
                        'base_probability': base_probability,
                        'inertia_i': inertia_i,
                        'inertia_j': inertia_j,
                        'final_probability': final_probability
                    }
        # 각 차량별 최종 소비자 선택률 계산 (다른 차량들로부터 선택받을 확률의 평균)
        final_choice_probabilities = []
        for i in range(n_vehicles):
            selection_probabilities = []
            for j in range(n_vehicles):
                if i != j and vehicle_grades[i] == vehicle_grades[j]:
                    selection_probabilities.append(probability_matrix[j][i])
            if selection_probabilities:
                avg_selection_probability = np.mean(selection_probabilities)
            else:
                avg_selection_probability = 0.0
            final_choice_probabilities.append(avg_selection_probability)
        return probability_matrix, vehicles, final_choice_probabilities
    
    def calculate_empirical_bev_probability(self, tco_diff, vehicle_price, brand_power_i=0, brand_power_j=0):
        """PDF 기반 올바른 BEV 선택 확률 계산 (브랜드파워 추가)"""
        
        # PDF 기반 정확한 매개변수
        empirical_parameters = {
            'ev_price_elasticity': -2.5,  # -2.0 ~ -2.8 범위에서 중간값
            'base_preference_constant': 0.18,  # 기본 선호도 상수
            'infrastructure_coefficient': 0.12,  # 인프라 준비도 계수
            'environmental_coefficient': 0.10,  # 환경 우려 계수
            'brand_power_coefficient': 0.15,  # 브랜드파워 계수
        }
        
        # 1. TCO 효과 계산 (PDF 수식)
        relative_tco_impact = tco_diff / vehicle_price
        tco_effect = empirical_parameters['ev_price_elasticity'] * relative_tco_impact
        
        # 2. 기본 선호도 계산 (PDF 수식)
        infrastructure_readiness = 0.5  # 기본값
        environmental_concern = 0.6     # 기본값
        base_preference = (empirical_parameters['base_preference_constant'] + 
                          empirical_parameters['infrastructure_coefficient'] * infrastructure_readiness +
                          empirical_parameters['environmental_coefficient'] * environmental_concern)
        
        # 3. 브랜드파워 효과 계산 (구매지수만 사용)
        # 브랜드파워가 높은 차량이 선택될 확률이 높아지도록 설정
        brand_power_effect = empirical_parameters['brand_power_coefficient'] * (brand_power_j - brand_power_i)
        
        # 4. 통합 불확실성 계산 (PDF 수식)
        range_anxiety = 0.4
        charging_infrastructure = 0.5
        technology_uncertainty = 0.3
        uncertainty_combined = np.sqrt(range_anxiety**2 + charging_infrastructure**2 + technology_uncertainty**2)
        
        # 5. 정규분포 불확실성 생성
        np.random.seed(42)  # 재현성을 위한 시드 설정
        uncertainty_noise = np.random.normal(0, uncertainty_combined)
        
        # 6. 최종 확률 계산 (TCO, 기본선호도, 불확실성, 브랜드파워)
        def sigmoid(x):
            return 1 / (1 + np.exp(-x))
        
        combined_effect = tco_effect + base_preference + brand_power_effect + uncertainty_noise
        probability = sigmoid(combined_effect)
        
        return probability, {
            'tco_effect': tco_effect,
            'base_preference': base_preference,
            'brand_power_effect': brand_power_effect,
            'uncertainty_combined': uncertainty_combined,
            'uncertainty_noise': uncertainty_noise,
            'combined_effect': combined_effect
        }
    
    def simulate_tco_scenarios(self, segment_data, scenarios):
        """TCO 시나리오별 판매량 변화 시뮬레이션"""
        results = []
        
        for scenario_name, scenario_params in scenarios.items():
            print(f"\n📊 시나리오: {scenario_name}")
            
            # 각 시나리오는 해당 시트의 데이터를 사용
            scenario_data = scenario_params['scenario_data']
            
            # 세그먼트에 해당하는 차량들만 필터링
            segment_vehicles = segment_data['차량명'].tolist()
            
            # 컬럼명 확인 및 필터링
            vehicle_column = None
            for col in scenario_data.columns:
                if '소분류' in col or '차량명' in col or '모델' in col:
                    vehicle_column = col
                    break
            
            if vehicle_column is None:
                print(f"⚠️ {scenario_name}에서 차량명 컬럼을 찾을 수 없습니다.")
                print(f"🔍 사용 가능한 컬럼: {list(scenario_data.columns)}")
                modified_data = segment_data.copy()
            else:
                scenario_segment_data = scenario_data[scenario_data[vehicle_column].isin(segment_vehicles)].copy()
                
                if scenario_segment_data.empty:
                    print(f"⚠️ {scenario_name}에서 해당 세그먼트 차량을 찾을 수 없습니다.")
                    modified_data = segment_data.copy()
                else:
                    print(f"✅ {scenario_name}에서 {len(scenario_segment_data)}개 차량 데이터 찾음")
                    # 해당 시나리오의 데이터를 사용하여 TCO 재계산
                    modified_data = self.calculate_scenario_tco(scenario_segment_data)
            
            # 수정된 TCO로 선택 확률 매트릭스 재계산
            probability_matrix, vehicles, final_choice_probabilities = self.calculate_choice_probability_matrix(modified_data)
            
            # 시장점유율 변화 계산
            market_shares = self.calculate_market_share_changes(segment_data, modified_data, probability_matrix)
            
            results.append({
                'scenario': scenario_name,
                'original_data': segment_data.copy(),
                'modified_data': modified_data,
                'probability_matrix': probability_matrix,
                'market_shares': market_shares,
                'vehicles': vehicles,
                'final_choice_probabilities': final_choice_probabilities
            })
            
            print(f"✅ {scenario_name} 시나리오 완료")
        
        return results
    
    def calculate_scenario_tco(self, scenario_data):
        """시나리오 데이터로 TCO 재계산 (등급별 계수 적용)"""
        modified_data = scenario_data.copy()
        if '소분류' in modified_data.columns and '차량명' not in modified_data.columns:
            modified_data = modified_data.rename(columns={'소분류': '차량명'})
        
        for idx, row in modified_data.iterrows():
            initial_cost = row['구매비용_만원'] - row['보조금_만원']
            annual_fuel = row['연간연료비_만원']
            annual_maintenance = row['연간유지보수비_만원']
            annual_tax_insurance = row['연간세금보험_만원']
            annual_depreciation = row['연간감가상각_만원']
            annual_other = row['연간기타비용_만원'] if pd.notna(row['연간기타비용_만원']) else 0
            annual_operating_cost = annual_fuel + annual_maintenance + annual_tax_insurance + annual_other
            total_operating_cost = annual_operating_cost * self.ownership_years
            residual_rate = row['잔존가치율'] if pd.notna(row['잔존가치율']) else 0.3
            residual_value = initial_cost * residual_rate
            total_tco = initial_cost + total_operating_cost - residual_value
            
            # 화물차 TCO 변화율 디버깅 정보 출력
            main_category = row['대분류'] if '대분류' in row else ''
            if main_category == '화물':
                print(f"🔧 화물차 TCO 계산: {row['차량명'] if '차량명' in row else row['소분류']}")
                print(f"  - 초기투자비용: {initial_cost:,.0f}만원")
                print(f"  - 총운영비: {total_operating_cost:,.0f}만원")
                print(f"  - 잔존가치: {residual_value:,.0f}만원")
                print(f"  - 총TCO: {total_tco:,.0f}만원")
            
            # 등급별 TCO 계수 적용 (가성비 민감도 반영)
            vehicle_grade = row['차량등급']
            vehicle_type = row['차량유형'] if '차량유형' in row else 'ICE'
            main_category = row['대분류'] if '대분류' in row else ''
            
            # 화물차는 등급별 계수 적용하지 않음 (TCO 변화율이 너무 커지는 것을 방지)
            if main_category == '화물':
                tco_multiplier = 1.0  # 화물차는 기본값 적용
            elif vehicle_grade == 'volume':
                tco_multiplier = 1.2  # volume 모델은 TCO 변화에 더 민감 (가성비 중시)
            elif vehicle_grade == 'premium':
                tco_multiplier = 0.8  # premium 모델은 TCO 변화에 덜 민감 (브랜드/품질 중시)
            else:
                tco_multiplier = 1.0  # 기본값
            
            # TCO에 등급별 계수 적용 (민감도 반영)
            adjusted_tco = total_tco * tco_multiplier
            
            modified_data.at[idx, 'TCO_만원'] = adjusted_tco
            modified_data.at[idx, '초기투자비용_만원'] = initial_cost
            modified_data.at[idx, '연간운영비_만원'] = annual_operating_cost
            modified_data.at[idx, '총운영비_만원'] = total_operating_cost
            modified_data.at[idx, '잔존가치_만원'] = residual_value
            modified_data.at[idx, '연평균TCO_만원'] = adjusted_tco / self.ownership_years
            modified_data.at[idx, 'TCO_계수'] = tco_multiplier
        
        return modified_data
    
    def calculate_market_share_changes(self, original_data, modified_data, probability_matrix):
        """시장점유율 변화 계산"""
        n_vehicles = len(original_data)
        original_shares = original_data['현재시장점유율'].values
        modified_shares = np.zeros(n_vehicles)
        
        # 각 차량의 새로운 시장점유율 계산
        for i in range(n_vehicles):
            # 다른 차량들로부터의 선택 확률 고려
            share_change = 0
            for j in range(n_vehicles):
                if i != j:
                    # j 차량이 i 차량을 선택할 확률
                    share_change += original_shares[j] * probability_matrix[j][i]
                    # i 차량이 j 차량을 선택할 확률 (손실)
                    share_change -= original_shares[i] * probability_matrix[i][j]
            
            modified_shares[i] = original_shares[i] + share_change
        
        # 정규화 (총합이 1이 되도록)
        modified_shares = np.maximum(modified_shares, 0)  # 음수 방지
        modified_shares = modified_shares / np.sum(modified_shares)
        
        return modified_shares
    
    def plot_segment_analysis(self, segment_results, segment_name):
        """세그먼트별 분석 결과 시각화"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'{segment_name} 세그먼트 분석 결과', fontsize=16, fontweight='bold')
        
        # 1. 원본 TCO 비교 (등급별 구분)
        ax1 = axes[0, 0]
        original_data = segment_results[0]['original_data']
        vehicles = original_data['차량명']
        tco_values = original_data['TCO_만원']
        
        # 등급별로 색상 구분
        colors = []
        for _, vehicle in original_data.iterrows():
            if vehicle['차량유형'] == 'ICE':
                if vehicle['차량등급'] == 'volume':
                    colors.append('lightblue')
                else:  # premium
                    colors.append('darkblue')
            else:  # BEV
                if vehicle['차량등급'] == 'volume':
                    colors.append('lightgreen')
                else:  # premium
                    colors.append('darkgreen')
        
        bars1 = ax1.bar(vehicles, tco_values, color=colors, alpha=0.7)
        ax1.set_title('원본 TCO 비교 (등급별)')
        ax1.set_ylabel('TCO (만원)')
        ax1.tick_params(axis='x', rotation=45)
        
        # 범례 추가 (등급별 구분)
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='lightblue', label='ICE Volume'),
            Patch(facecolor='darkblue', label='ICE Premium'),
            Patch(facecolor='lightgreen', label='BEV Volume'),
            Patch(facecolor='darkgreen', label='BEV Premium')
        ]
        ax1.legend(handles=legend_elements)
        
        # 2. 시나리오별 TCO 변화
        ax2 = axes[0, 1]
        scenario_names = [result['scenario'] for result in segment_results]
        scenario_data = []
        
        for result in segment_results:
            modified_tco = result['modified_data']['TCO_만원'].values
            scenario_data.append(modified_tco)
        
        # 배열 길이 통일
        max_length = max(len(data) for data in scenario_data)
        scenario_data_padded = []
        for data in scenario_data:
            if len(data) < max_length:
                # 부족한 길이만큼 0으로 패딩
                padded_data = np.pad(data, (0, max_length - len(data)), 'constant', constant_values=0)
                scenario_data_padded.append(padded_data)
            else:
                scenario_data_padded.append(data)
        
        scenario_data = np.array(scenario_data_padded)
        
        for i, vehicle in enumerate(vehicles):
            ax2.plot(scenario_names, scenario_data[:, i], marker='o', label=vehicle)
        
        ax2.set_title('시나리오별 TCO 변화')
        ax2.set_ylabel('TCO (만원)')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 3. 시나리오별 시장점유율 변화
        ax3 = axes[1, 0]
        x = np.arange(len(vehicles))
        width = 0.8 / len(segment_results)  # 시나리오 개수에 따라 너비 조정
        # 원본 시장점유율 bar 제거
        # 시나리오별 시장점유율만 표시
        for i, result in enumerate(segment_results):
            modified_shares = result['market_shares']
            ax3.bar(x + width * i, modified_shares, width, label=result['scenario'], alpha=0.7)
        ax3.set_title('시나리오별 시장점유율 변화')
        ax3.set_ylabel('시장점유율')
        ax3.set_xticks(x + width * (len(segment_results) - 1) / 2)
        ax3.set_xticklabels(vehicles, rotation=45)
        ax3.legend()
        
        # 4. BEV vs ICE 시장점유율 변화
        ax4 = axes[1, 1]
        bev_shares = []
        ice_shares = []
        for result in segment_results:
            modified_data = result['modified_data']
            modified_shares = result['market_shares']
            bev_total = 0
            ice_total = 0
            for i, vehicle_type in enumerate(modified_data['차량유형']):
                if i < len(modified_shares):
                    if vehicle_type == 'BEV':
                        bev_total += modified_shares[i]
                    else:
                        ice_total += modified_shares[i]
            bev_shares.append(bev_total)
            ice_shares.append(ice_total)
        # 원본 bar 제거, 시나리오별 결과만 표시
        x_pos = np.arange(len(scenario_names))
        ax4.bar(x_pos, bev_shares, label='BEV', color='lightgreen', alpha=0.7)
        ax4.bar(x_pos, ice_shares, bottom=bev_shares, label='ICE', color='skyblue', alpha=0.7)
        ax4.set_title('BEV vs ICE 시장점유율 변화')
        ax4.set_ylabel('시장점유율')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(scenario_names, rotation=45)
        ax4.legend()
        
        plt.tight_layout()
        
        # 결과 폴더에 저장
        filename = f'{segment_name}_세그먼트_분석.png'
        filepath = os.path.join(self.results_folder, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✅ {segment_name} 세그먼트 분석 그래프 저장 완료: {filepath}")
        
        return fig

class DetailedTCOAnalyzer:
    def __init__(self, excel_file_path='TCO_분석_입력템플릿.xlsx'):
        """Initialize detailed TCO analyzer"""
        self.excel_path = excel_file_path
        self.data = None
        self.scenario_data = None
        self.yearly_data = None
        self.ownership_years = 5
        self.segment_analyzer = SegmentSalesAnalyzer()
        
        # 결과 폴더 경로 가져오기
        self.results_folder = self.segment_analyzer.results_folder
        
    def load_data(self):
        """Load Excel data"""
        try:
            self.data = pd.read_excel(self.excel_path, sheet_name='기본시나리오')
            # 시나리오 시트 자동 탐색 (시트명에 "시나리오"가 포함된 시트만)
            xl = pd.ExcelFile(self.excel_path)
            scenario_sheets = [s for s in xl.sheet_names if '시나리오' in s]
            self.scenarios = {}
            for sheet in scenario_sheets:
                self.scenarios[sheet] = pd.read_excel(self.excel_path, sheet_name=sheet)
                print(f"✅ {sheet} 데이터 로드 완료")
            # 기존 데이터도 로드 (호환성 유지)
            try:
                self.scenario_data = pd.read_excel(self.excel_path, sheet_name='지원제거시나리오')
            except:
                self.scenario_data = None
            try:
                self.yearly_data = pd.read_excel(self.excel_path, sheet_name='연도별TCO')
            except:
                self.yearly_data = None
            print("✅ Data loaded successfully.")
            print(f"📊 Total {len(self.data)} vehicle models analyzed")
            print(f"📊 Loaded scenarios: {list(self.scenarios.keys())}")
            
            # 소형화물 데이터 확인
            small_cargo = self.data[self.data['중분류'] == '소형화물']
            if not small_cargo.empty:
                print("🔍 소형화물 데이터 확인:")
                for idx, row in small_cargo.iterrows():
                    print(f"  {row['소분류']}: 차량대수 {row['차량대수']:,}대, 연비 {row['연비']} km/L")
            
            return True
        except FileNotFoundError:
            print(f"❌ File not found: {self.excel_path}")
            return False
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def calculate_tco(self, row):
        """Calculate TCO for individual vehicle model"""
        try:
            # Basic cost components
            initial_cost = row['초기투자비용_만원']
            annual_fuel = row['연간연료비_만원']
            annual_maintenance = row['연간유지보수비_만원']
            annual_tax_insurance = row['연간세금보험_만원']
            annual_depreciation = row['연간감가상각_만원']
            annual_other = row['연간기타비용_만원'] if pd.notna(row['연간기타비용_만원']) else 0
            
            # Calculate annual operating cost
            annual_operating_cost = annual_fuel + annual_maintenance + annual_tax_insurance + annual_other
            
            # Total operating cost (5 years)
            total_operating_cost = annual_operating_cost * self.ownership_years
            
            # Calculate residual value
            residual_rate = row['잔존가치율'] if pd.notna(row['잔존가치율']) else 0.3  # Default 30%
            residual_value = initial_cost * residual_rate
            
            # Calculate total TCO
            total_tco = initial_cost + total_operating_cost - residual_value
            
            return {
                '연간운영비_만원': annual_operating_cost,
                '총운영비_만원': total_operating_cost,
                '잔존가치_만원': residual_value,
                '총TCO_만원': total_tco,
                '연평균TCO_만원': total_tco / self.ownership_years
            }
        except Exception as e:
            print(f"TCO calculation error ({row['소분류']}): {e}")
            return {
                '연간운영비_만원': 0,
                '총운영비_만원': 0,
                '잔존가치_만원': 0,
                '총TCO_만원': 0,
                '연평균TCO_만원': 0
            }
    
    def calculate_all_tco(self):
        """Calculate TCO for all vehicle models"""
        print("🔧 Calculating TCO...")
        
        for idx, row in self.data.iterrows():
            if pd.isna(row['총TCO_만원']):  # If TCO not calculated
                tco_values = self.calculate_tco(row)
                
                # Update calculated values to dataframe
                for key, value in tco_values.items():
                    self.data.at[idx, key] = value
        
        print("✅ TCO calculation completed")
        
    def analyze_segment_sales_changes(self):
        """세그먼트별 판매량 변화 분석"""
        print("\n" + "="*60)
        print("🚗 세그먼트별 판매량 변화 분석")
        print("="*60)
        # TCO 계산
        self.calculate_all_tco()
        # 실제 데이터에서 사용 가능한 세그먼트들 확인
        available_segments = self.data['중분류'].unique()
        print(f"📊 사용 가능한 세그먼트: {list(available_segments)}")
        # 시나리오 정의 (차량분류 = 기본시나리오, 나머지 = 변화된 시나리오)
        scenarios = {'기본시나리오': {'scenario_data': self.data}}
        # 엑셀에서 로드된 시나리오 추가
        for scenario_name, scenario_data in self.scenarios.items():
            scenarios[scenario_name] = {'scenario_data': scenario_data}
        print(f"📊 분석할 시나리오: {list(scenarios.keys())}")
        segment_results = {}
        # 각 세그먼트별 분석
        for segment in available_segments:
            segment_name = self.segment_analyzer.segments.get(segment, segment)
            print(f"\n📊 {segment_name} ({segment}) 세그먼트 분석 중...")
            # 세그먼트 내 차량 데이터 추출
            segment_data = self.segment_analyzer.get_segment_data(self.data, segment)
            if not segment_data.empty:
                print(f"  ✅ {len(segment_data)}개 차량 모델 발견:")
                for _, vehicle in segment_data.iterrows():
                    brand_power = vehicle['브랜드파워'] if '브랜드파워' in vehicle else 0
                    print(f"    • {vehicle['차량명']} ({vehicle['차량유형']}, {vehicle['차량등급']}) - TCO: {vehicle['TCO_만원']:,.0f}만원, 브랜드파워: {brand_power:.2f}")
                # 시나리오별 시뮬레이션
                results = self.segment_analyzer.simulate_tco_scenarios(segment_data, scenarios)
                segment_results[segment] = results
                # 시각화
                self.segment_analyzer.plot_segment_analysis(results, f"{segment}_{segment_name}")
                
                # 온실가스 배출량 분석 (전체 결과에서 호출)
                # self.segment_analyzer.plot_ghg_emissions_analysis(results)
                
                # 결과 출력
                print(f"\n📈 {segment_name} 세그먼트 결과 요약:")
                original_bev = sum(segment_data[segment_data['차량유형'] == 'BEV']['현재시장점유율'])
                original_ice = sum(segment_data[segment_data['차량유형'] == 'ICE']['현재시장점유율'])
                print(f"  • 원본 BEV 점유율: {original_bev:.1%}")
                print(f"  • 원본 ICE 점유율: {original_ice:.1%}")
                for result in results:
                    scenario_name = result['scenario']
                    modified_data = result['modified_data']
                    market_shares = result['market_shares']
                    modified_bev = 0
                    modified_ice = 0
                    for i, vehicle_type in enumerate(modified_data['차량유형']):
                        if i < len(market_shares):
                            if vehicle_type == 'BEV':
                                modified_bev += market_shares[i]
                            else:
                                modified_ice += market_shares[i]
                    bev_change = (modified_bev - original_bev) * 100
                    print(f"  • {scenario_name}: BEV {original_bev:.1%} → {modified_bev:.1%} ({bev_change:+.1f}%p)")
            else:
                print(f"  ⚠️ {segment_name} 세그먼트에 해당하는 차량 데이터가 없습니다.")
        return segment_results
    
    def save_segment_analysis_results(self, segment_results):
        """세그먼트별 분석 결과를 Excel로 저장"""
        print("\n" + "="*60)
        print("💾 세그먼트별 분석 결과 저장")
        print("="*60)
        
        excel_filename = 'Segment_Sales_Analysis_Results.xlsx'
        excel_filepath = os.path.join(self.results_folder, excel_filename)
        
        try:
            with pd.ExcelWriter(excel_filepath, engine='openpyxl') as writer:
                
                # 온실가스 배출량 분석 추가
                self.save_ghg_emissions_analysis(segment_results, writer)
                
                # 1. 세그먼트별 요약
                summary_data = []
                for segment, results in segment_results.items():
                    segment_name = self.segment_analyzer.segments.get(segment, segment)
                    
                    for result in results:
                        scenario_name = result['scenario']
                        original_data = result['original_data']
                        modified_data = result['modified_data']
                        market_shares = result['market_shares']
                        
                        # BEV/ICE 점유율 변화
                        original_bev = sum(original_data[original_data['차량유형'] == 'BEV']['현재시장점유율'])
                        original_ice = sum(original_data[original_data['차량유형'] == 'ICE']['현재시장점유율'])
                        
                        modified_bev = 0
                        modified_ice = 0
                        for i, vehicle_type in enumerate(modified_data['차량유형']):
                            if i < len(market_shares):
                                if vehicle_type == 'BEV':
                                    modified_bev += market_shares[i]
                                else:
                                    modified_ice += market_shares[i]
                        
                        summary_data.append({
                            '세그먼트': segment,
                            '세그먼트명': segment_name,
                            '시나리오': scenario_name,
                            '원본_BEV_점유율': original_bev,
                            '원본_ICE_점유율': original_ice,
                            '변화후_BEV_점유율': modified_bev,
                            '변화후_ICE_점유율': modified_ice,
                            'BEV_점유율_변화': modified_bev - original_bev,
                            'ICE_점유율_변화': modified_ice - original_ice
                        })
                
                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='세그먼트별_요약', index=False)
                
                # 2. 차량별 상세 결과
                detailed_data = []
                for segment, results in segment_results.items():
                    segment_name = self.segment_analyzer.segments.get(segment, segment)
                    
                    for result in results:
                        scenario_name = result['scenario']
                        original_data = result['original_data']
                        modified_data = result['modified_data']
                        market_shares = result['market_shares']
                        
                        for i, (_, vehicle) in enumerate(original_data.iterrows()):
                            # 원본 차량대수
                            if '현재판매량' in vehicle:
                                original_count = vehicle['현재판매량']
                            elif '차량대수' in vehicle:
                                original_count = vehicle['차량대수']
                            else:
                                original_count = 0
                            # 총판매량(원본)
                            total_original_count = original_data['현재판매량'].sum() if '현재판매량' in original_data.columns else original_data['차량대수'].sum() if '차량대수' in original_data.columns else 0
                            # 변화후 차량대수: 원본 총판매량 × 변화후 시장점유율
                            changed_count = total_original_count * market_shares[i] if total_original_count > 0 else 0
                            # 차량대수 변화
                            count_diff = changed_count - original_count
                            # 최종 소비자 선택률
                            final_choice_prob = None
                            if 'final_choice_probabilities' in result:
                                final_choice_prob = result['final_choice_probabilities'][i]
                            elif 'final_choice_probabilities' in locals():
                                final_choice_prob = final_choice_probabilities[i]
                            else:
                                final_choice_prob = None
                            detailed_data.append({
                                '세그먼트': segment,
                                '세그먼트명': segment_name,
                                '시나리오': scenario_name,
                                '차량명': vehicle['차량명'],
                                '차량유형': vehicle['차량유형'],
                                '원본_TCO_만원': vehicle['TCO_만원'],
                                '변화후_TCO_만원': modified_data.iloc[i]['TCO_만원'],
                                'TCO_변화율': (modified_data.iloc[i]['TCO_만원'] - vehicle['TCO_만원']) / vehicle['TCO_만원'],
                                '원본_시장점유율': vehicle['현재시장점유율'],
                                '변화후_시장점유율': market_shares[i],
                                '시장점유율_변화': market_shares[i] - vehicle['현재시장점유율'],
                                '원본_차량대수': original_count,
                                '변화후_차량대수': changed_count,
                                '차량대수_변화': count_diff,
                                '최종_소비자_선택률': final_choice_prob,
                                '구매지수': vehicle['구매지수'] if '구매지수' in vehicle else 0,
                                '관성계수': vehicle['관성계수'] if '관성계수' in vehicle else 1.0,
                                '브랜드파워': vehicle['브랜드파워'] if '브랜드파워' in vehicle else 0
                            })
                
                if detailed_data:
                    detailed_df = pd.DataFrame(detailed_data)
                    detailed_df.to_excel(writer, sheet_name='차량별_상세결과', index=False)
                
                # 3. 시나리오별 효과 분석
                scenario_analysis = []
                for segment, results in segment_results.items():
                    segment_name = self.segment_analyzer.segments.get(segment, segment)
                    
                    for result in results:
                        scenario_name = result['scenario']
                        original_data = result['original_data']
                        market_shares = result['market_shares']
                        
                        # BEV 점유율 변화
                        original_bev = sum(original_data[original_data['차량유형'] == 'BEV']['현재시장점유율'])
                        modified_bev = 0
                        for i, vehicle_type in enumerate(original_data['차량유형']):
                            if i < len(market_shares):
                                if vehicle_type == 'BEV':
                                    modified_bev += market_shares[i]
                        
                        bev_change_pct = (modified_bev - original_bev) * 100
                        
                        scenario_analysis.append({
                            '세그먼트': segment,
                            '세그먼트명': segment_name,
                            '시나리오': scenario_name,
                            'BEV_점유율_변화_%p': bev_change_pct,
                            '정책효과': '높음' if abs(bev_change_pct) > 5 else '보통' if abs(bev_change_pct) > 2 else '낮음'
                        })
                
                if scenario_analysis:
                    scenario_df = pd.DataFrame(scenario_analysis)
                    scenario_df.to_excel(writer, sheet_name='시나리오별_효과분석', index=False)
                
                # 4. 세그먼트별 현황 요약
                segment_summary = []
                for segment in self.data['중분류'].unique():
                    segment_data = self.data[self.data['중분류'] == segment]
                    segment_name = self.segment_analyzer.segments.get(segment, segment)
                    
                    total_sales = segment_data['차량대수'].sum()
                    ice_sales = segment_data[segment_data['차량유형'] == 'ICE']['차량대수'].sum()
                    bev_sales = segment_data[segment_data['차량유형'] == 'BEV']['차량대수'].sum()
                    
                    segment_summary.append({
                        '세그먼트': segment,
                        '세그먼트명': segment_name,
                        '총판매량': total_sales,
                        'ICE_판매량': ice_sales,
                        'BEV_판매량': bev_sales,
                        'ICE_점유율': ice_sales / total_sales if total_sales > 0 else 0,
                        'BEV_점유율': bev_sales / total_sales if total_sales > 0 else 0,
                        '차량모델수': len(segment_data)
                    })
                
                if segment_summary:
                    segment_summary_df = pd.DataFrame(segment_summary)
                    segment_summary_df.to_excel(writer, sheet_name='세그먼트별_현황', index=False)
            
            print(f"✅ 세그먼트별 분석 결과가 '{excel_filepath}'에 저장되었습니다.")
            return excel_filepath
            
        except Exception as e:
            print(f"⚠️ Excel 파일 저장 중 오류 발생: {e}")
            return None
    
    def save_ghg_emissions_analysis(self, segment_results, writer):
        """온실가스 배출량 분석 결과 저장 (groupby로 중복 없이 정확히 저장)"""
        print("\n🌍 온실가스 배출량 분석 중...")
        
        scenario_emissions = []
        
        for segment, results in segment_results.items():
            segment_name = self.segment_analyzer.segments.get(segment, segment)
            for result in results:
                scenario_name = result['scenario']
                original_data = result['original_data']
                modified_data = result['modified_data']
                market_shares = result['market_shares']
                
                # 원본/수정 데이터의 온실가스 배출량 계산
                original_emissions = self.segment_analyzer.calculate_ghg_emissions(original_data)
                modified_emissions = self.segment_analyzer.calculate_ghg_emissions(modified_data)
                adjusted_emissions = self.calculate_adjusted_ghg_emissions(modified_emissions, market_shares)
                
                # 차량유형별로 groupby 집계
                for df, label in [(original_emissions, '원본_총온실가스배출량_kgCO2'), (adjusted_emissions, '변화후_총온실가스배출량_kgCO2')]:
                    grouped = df.groupby('차량유형')['총온실가스배출량_kgCO2'].sum().reset_index()
                    for _, row in grouped.iterrows():
                        scenario_emissions.append({
                            '세그먼트': segment,
                            '세그먼트명': segment_name,
                            '시나리오': scenario_name,
                            '차량유형': row['차량유형'],
                            label: row['총온실가스배출량_kgCO2']
                        })
        
        # groupby로 동일 세그먼트/시나리오/차량유형별로 합치기
        if scenario_emissions:
            emissions_df = pd.DataFrame(scenario_emissions)
            emissions_df = emissions_df.groupby(['세그먼트','세그먼트명','시나리오','차량유형'], as_index=False).sum()
            emissions_df.to_excel(writer, sheet_name='온실가스배출량_분석', index=False)
            print("✅ 온실가스 배출량 분석 데이터가 Excel에 저장되었습니다.")
        else:
            print("⚠️ 온실가스 배출량 데이터가 없습니다.")
    
    def calculate_adjusted_ghg_emissions(self, emissions_data, market_shares):
        """시장점유율 변화를 반영한 온실가스 배출량 계산"""
        adjusted_emissions = emissions_data.copy()
        
        for idx, row in emissions_data.iterrows():
            if idx < len(market_shares):
                # 시장점유율 변화에 따른 차량대수 조정
                original_share = row['차량대수'] / emissions_data['차량대수'].sum() if emissions_data['차량대수'].sum() > 0 else 0
                new_share = market_shares[idx]
                
                # 새로운 차량대수 계산
                total_vehicles = emissions_data['차량대수'].sum()
                new_vehicle_count = new_share * total_vehicles
                
                # 온실가스 배출량 조정
                adjusted_emissions.at[idx, '차량대수'] = new_vehicle_count
                # 연간온실가스배출량_kgCO2는 1대당 연간 배출량이므로, 새로운 차량대수를 곱함
                adjusted_emissions.at[idx, '총온실가스배출량_kgCO2'] = row['연간온실가스배출량_kgCO2'] * new_vehicle_count
        
        return adjusted_emissions
    
    def plot_ghg_emissions_analysis(self, segment_results):
        """온실가스 배출량 분석 시각화"""
        print("\n📊 온실가스 배출량 분석 그래프 생성 중...")
        
        # 시나리오별 온실가스 배출량 데이터 수집
        scenario_emissions = []
        
        for segment, results in segment_results.items():
            segment_name = self.segment_analyzer.segments.get(segment, segment)
            
            for result in results:
                scenario_name = result['scenario']
                original_data = result['original_data']
                modified_data = result['modified_data']
                market_shares = result['market_shares']
                
                # 온실가스 배출량 계산
                original_emissions = self.segment_analyzer.calculate_ghg_emissions(original_data)
                modified_emissions = self.segment_analyzer.calculate_ghg_emissions(modified_data)
                adjusted_emissions = self.calculate_adjusted_ghg_emissions(modified_emissions, market_shares)
                
                scenario_emissions.append({
                    '세그먼트': segment,
                    '세그먼트명': segment_name,
                    '시나리오': scenario_name,
                    '원본_총온실가스배출량_kgCO2': original_emissions['총온실가스배출량_kgCO2'].sum(),
                    '변화후_총온실가스배출량_kgCO2': adjusted_emissions['총온실가스배출량_kgCO2'].sum()
                })
        
        if not scenario_emissions:
            print("⚠️ 온실가스 배출량 데이터가 없습니다.")
            return
        
        # 그래프 생성 - 승용차와 화물차 분리
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        emissions_df = pd.DataFrame(scenario_emissions)
        
        # 대분류별 중분류 순서 정의
        passenger_categories = ['경형', '소형', '준중형', '중형1', '중형2', '준대형', '대형1', '대형2']
        cargo_categories = ['소형화물', '중형화물1', '중형화물2', '대형화물1', '대형화물2', '대형화물3']
        
        # 시나리오별 데이터 수집
        scenarios = emissions_df['시나리오'].unique()
        
        # 중분류별 세부 데이터 수집
        passenger_categories = ['경형', '소형', '준중형', '중형1', '중형2', '준대형', '대형1', '대형2']
        cargo_categories = ['소형화물', '중형화물1', '중형화물2', '대형화물1', '대형화물2', '대형화물3']
        
        # 시나리오별 중분류 데이터 수집
        scenario_detailed_data = []
        
        for scenario in scenarios:
            scenario_data = emissions_df[emissions_df['시나리오'] == scenario]
            
            # 승용차 중분류별 데이터
            passenger_by_category = {}
            for category in passenger_categories:
                category_emissions = scenario_data[scenario_data['세그먼트명'] == category]
                passenger_by_category[category] = category_emissions['변화후_총온실가스배출량_kgCO2'].sum()
            
            # 화물차 중분류별 데이터
            cargo_by_category = {}
            for category in cargo_categories:
                category_emissions = scenario_data[scenario_data['세그먼트명'] == category]
                cargo_by_category[category] = category_emissions['변화후_총온실가스배출량_kgCO2'].sum()
            
            scenario_detailed_data.append({
                'scenario': scenario,
                'passenger': passenger_by_category,
                'cargo': cargo_by_category
            })
        
        # 승용차 그래프 (왼쪽)
        x = np.arange(len(scenarios))
        width = 0.8
        
        # 승용차 누적 막대 (중분류별 음영 변화)
        passenger_colors = ['#FFE6E6', '#FFCCCC', '#FFB3B3', '#FF9999', '#FF8080', '#FF6666', '#FF4D4D', '#FF3333']
        passenger_bottom = np.zeros(len(scenarios))
        
        for i, category in enumerate(passenger_categories):
            category_data = [data['passenger'][category] for data in scenario_detailed_data]
            ax1.bar(x, category_data, width, bottom=passenger_bottom, 
                   label=category, color=passenger_colors[i], alpha=0.8)
            passenger_bottom += np.array(category_data)
        
        ax1.set_title('승용차 온실가스 배출량 변화', fontsize=14, fontweight='bold')
        ax1.set_ylabel('온실가스 배출량 (kgCO2)', fontsize=12)
        ax1.set_xlabel('시나리오', fontsize=12)
        ax1.set_xticks(x)
        ax1.set_xticklabels(scenarios, rotation=45, ha='right')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 승용차 총합 값 표시
        for i, scenario in enumerate(scenarios):
            passenger_total = sum([scenario_detailed_data[i]['passenger'][cat] for cat in passenger_categories])
            ax1.text(x[i], passenger_total + passenger_total*0.01, f'{passenger_total:,.0f}', 
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 화물차 그래프 (오른쪽)
        # 화물차 누적 막대 (중분류별 음영 변화)
        cargo_colors = ['#E6F3FF', '#CCE7FF', '#B3DBFF', '#99CFFF', '#80C3FF', '#66B7FF']
        cargo_bottom = np.zeros(len(scenarios))
        
        for i, category in enumerate(cargo_categories):
            category_data = [data['cargo'][category] for data in scenario_detailed_data]
            ax2.bar(x, category_data, width, bottom=cargo_bottom, 
                   label=category, color=cargo_colors[i], alpha=0.8)
            cargo_bottom += np.array(category_data)
        
        ax2.set_title('화물차 온실가스 배출량 변화', fontsize=14, fontweight='bold')
        ax2.set_ylabel('온실가스 배출량 (kgCO2)', fontsize=12)
        ax2.set_xlabel('시나리오', fontsize=12)
        ax2.set_xticks(x)
        ax2.set_xticklabels(scenarios, rotation=45, ha='right')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        # 화물차 총합 값 표시
        for i, scenario in enumerate(scenarios):
            cargo_total = sum([scenario_detailed_data[i]['cargo'][cat] for cat in cargo_categories])
            ax2.text(x[i], cargo_total + cargo_total*0.01, f'{cargo_total:,.0f}', 
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        
        # 결과 폴더에 저장
        filename = '온실가스배출량_분석.png'
        filepath = os.path.join(self.results_folder, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✅ 온실가스 배출량 분석 그래프 저장 완료: {filepath}")
        
        return fig
    
    def analyze_by_vehicle_model(self):
        """Detailed analysis by vehicle model"""
        print("\n" + "="*60)
        print("🚗 Detailed TCO Analysis by Vehicle Model")
        print("="*60)
        
        # Calculate TCO
        self.calculate_all_tco()
        
        # Vehicle model TCO analysis
        vehicle_analysis = self.data.groupby(['소분류', '차량유형']).agg({
            '총TCO_만원': 'mean',
            '초기투자비용_만원': 'mean',
            '연간운영비_만원': 'mean',
            '잔존가치_만원': 'mean',
            '차량대수': 'sum'
        }).round(2)
        
        print("📊 Vehicle Model TCO Analysis Results:")
        print(vehicle_analysis)
        
        # ICE vs BEV comparison (within same category)
        print("\n🔄 ICE vs BEV Comparison within Same Category:")
        
        # Group by subcategory for comparison
        for category in self.data['중분류'].unique():
            category_data = self.data[self.data['중분류'] == category]
            if len(category_data) >= 2:  # If both ICE and BEV exist
                print(f"\n{category} Category:")
                for _, row in category_data.iterrows():
                    print(f"  {row['소분류']} ({row['차량유형']}): {row['총TCO_만원']:,.0f} KRW")
                
                # Calculate TCO difference
                ice_data = category_data[category_data['차량유형'] == 'ICE']
                bev_data = category_data[category_data['차량유형'] == 'BEV']
                
                if len(ice_data) > 0 and len(bev_data) > 0:
                    ice_tco = ice_data['총TCO_만원'].iloc[0]
                    bev_tco = bev_data['총TCO_만원'].iloc[0]
                    diff = bev_tco - ice_tco
                    print(f"  TCO Difference (BEV-ICE): {diff:+,.0f} KRW")
        
        return vehicle_analysis
    
    def calculate_empirical_bev_probability(self, tco_diff, vehicle_price, current_market_share=0.05):
        """PDF 기반 올바른 BEV 선택 확률 계산"""
        
        # PDF 기반 정확한 매개변수
        empirical_parameters = {
            'ev_price_elasticity': -2.5,  # -2.0 ~ -2.8 범위에서 중간값
            'base_preference_constant': 0.18,  # 기본 선호도 상수
            'infrastructure_coefficient': 0.12,  # 인프라 준비도 계수
            'environmental_coefficient': 0.10,  # 환경 우려 계수
        }
        
        # 1. TCO 효과 계산 (PDF 수식)
        relative_tco_impact = tco_diff / vehicle_price
        tco_effect = empirical_parameters['ev_price_elasticity'] * relative_tco_impact
        
        # 2. 기본 선호도 계산 (PDF 수식)
        infrastructure_readiness = 0.5  # 기본값
        environmental_concern = 0.6     # 기본값
        base_preference = (empirical_parameters['base_preference_constant'] + 
                          empirical_parameters['infrastructure_coefficient'] * infrastructure_readiness +
                          empirical_parameters['environmental_coefficient'] * environmental_concern)
        
        # 3. 통합 불확실성 계산 (PDF 수식)
        range_anxiety = 0.4
        charging_infrastructure = 0.5
        technology_uncertainty = 0.3
        uncertainty_combined = np.sqrt(range_anxiety**2 + charging_infrastructure**2 + technology_uncertainty**2)
        
        # 4. 정규분포 불확실성 생성
        np.random.seed(42)  # 재현성을 위한 시드 설정
        uncertainty_noise = np.random.normal(0, uncertainty_combined)
        
        # 5. 최종 확률 계산 (PDF 수식)
        def sigmoid(x):
            return 1 / (1 + np.exp(-x))
        
        combined_effect = tco_effect + base_preference + uncertainty_noise
        probability = sigmoid(combined_effect)
        
        return probability, {
            'tco_effect': tco_effect,
            'base_preference': base_preference,
            'uncertainty_combined': uncertainty_combined,
            'uncertainty_noise': uncertainty_noise,
            'combined_effect': combined_effect
        }
    
    def analyze_consumer_choice_by_model(self):
        """Consumer choice analysis by vehicle model"""
        print("\n" + "="*60)
        print("🎯 Empirical Research-Based Consumer Choice Analysis by Vehicle Model")
        print("="*60)
        
        # Group by subcategory for analysis
        results = []
        
        for category in self.data['중분류'].unique():
            category_data = self.data[self.data['중분류'] == category]
            
            if len(category_data) >= 2:  # If both ICE and BEV exist
                ice_data = category_data[category_data['차량유형'] == 'ICE']
                bev_data = category_data[category_data['차량유형'] == 'BEV']
                
                if len(ice_data) > 0 and len(bev_data) > 0:
                    ice_model = ice_data['소분류'].iloc[0]
                    bev_model = bev_data['소분류'].iloc[0]
                    ice_tco = ice_data['총TCO_만원'].iloc[0]
                    bev_tco = bev_data['총TCO_만원'].iloc[0]
                    ice_price = ice_data['초기투자비용_만원'].iloc[0]
                    bev_price = bev_data['초기투자비용_만원'].iloc[0]
                    
                    tco_diff = bev_tco - ice_tco
                    avg_price = (ice_price + bev_price) / 2
                    
                    # Calculate BEV selection probability
                    bev_probability, empirical_parameters = self.calculate_empirical_bev_probability(tco_diff, avg_price)
                    
                    results.append({
                        'Category': category,
                        'ICE_Model': ice_model,
                        'BEV_Model': bev_model,
                        'ICE_TCO': ice_tco,
                        'BEV_TCO': bev_tco,
                        'TCO_Difference': tco_diff,
                        'Average_Price': avg_price,
                        'BEV_Selection_Probability': bev_probability,
                        'Relative_Impact': (tco_diff / avg_price) * 100,
                        'tco_effect': empirical_parameters['tco_effect'],
                        'base_preference': empirical_parameters['base_preference'],
                        'uncertainty_combined': empirical_parameters['uncertainty_combined'],
                        'uncertainty_noise': empirical_parameters['uncertainty_noise'],
                        'combined_effect': empirical_parameters['combined_effect']
                    })
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(results)
        
        print("📊 Consumer Choice Analysis Results by Vehicle Model:")
        print(results_df.round(2))
        
        # Visualization
        self.plot_vehicle_choice_analysis(results_df)
        
        return results_df
    
    def plot_vehicle_choice_analysis(self, results_df):
        """Visualization of vehicle choice analysis"""
        plt.figure(figsize=(16, 12))
        
        # 1. BEV Selection Probability by TCO Difference
        plt.subplot(2, 2, 1)
        plt.scatter(results_df['TCO_Difference'], results_df['BEV_Selection_Probability'], 
                   s=100, alpha=0.7, c='green')
        
        for i, row in results_df.iterrows():
            plt.annotate(row['Category'], (row['TCO_Difference'], row['BEV_Selection_Probability']), 
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        plt.xlabel('TCO Difference (BEV - ICE, KRW)')
        plt.ylabel('BEV Selection Probability')
        plt.title('BEV Selection Probability by TCO Difference')
        plt.grid(True, alpha=0.3)
        
        # 2. BEV Selection Probability by Relative Impact
        plt.subplot(2, 2, 2)
        plt.scatter(results_df['Relative_Impact'], results_df['BEV_Selection_Probability'], 
                   s=100, alpha=0.7, c='blue')
        
        for i, row in results_df.iterrows():
            plt.annotate(row['Category'], (row['Relative_Impact'], row['BEV_Selection_Probability']), 
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        plt.xlabel('Relative TCO Impact (%)')
        plt.ylabel('BEV Selection Probability')
        plt.title('BEV Selection Probability by Relative Impact')
        plt.grid(True, alpha=0.3)
        
        # 3. TCO Comparison by Vehicle Category
        plt.subplot(2, 2, 3)
        categories = results_df['Category']
        ice_tco = results_df['ICE_TCO']
        bev_tco = results_df['BEV_TCO']
        
        x = np.arange(len(categories))
        width = 0.35
        
        plt.bar(x - width/2, ice_tco, width, label='ICE', color='skyblue')
        plt.bar(x + width/2, bev_tco, width, label='BEV', color='lightgreen')
        
        plt.xlabel('Vehicle Category')
        plt.ylabel('Total TCO (KRW)')
        plt.title('TCO Comparison by Vehicle Category')
        plt.xticks(x, categories, rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 4. BEV Selection Probability Distribution
        plt.subplot(2, 2, 4)
        plt.bar(categories, results_df['BEV_Selection_Probability'], color='lightgreen', alpha=0.7)
        plt.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='50% Baseline')
        
        plt.xlabel('Vehicle Category')
        plt.ylabel('BEV Selection Probability')
        plt.title('BEV Selection Probability by Vehicle Category')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 결과 폴더에 저장
        filename = 'Vehicle_Category_TCO_Analysis.png'
        filepath = os.path.join(self.results_folder, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✅ Vehicle category TCO analysis graph saved as '{filepath}'")
        
        return plt.gcf()
    
    def policy_recommendations(self, choice_results):
        """정책 권장사항 생성"""
        print("\n============================================================")
        print("📋 Policy Recommendations by Vehicle Category")
        print("============================================================")
        
        # BEV 선택률 기준으로 분류
        low_adoption = []
        high_adoption = []
        
        for _, row in choice_results.iterrows():
            category = row['Category']
            current_prob = row['BEV_Selection_Probability']
            
            if current_prob < 0.3:  # 30% 미만
                low_adoption.append((category, current_prob, row['TCO_Difference']))
            else:
                high_adoption.append((category, current_prob, row['TCO_Difference']))
        
        # 정책 시뮬레이션
        print("📈 Policy Effect Simulation:")
        for category, current_prob, tco_diff in low_adoption:
            # TCO 개선 시나리오 (10% 감소)
            improved_tco_diff = tco_diff * 0.9
            avg_price = choice_results[choice_results['Category'] == category]['Average_Price'].iloc[0]
            
            # 개선된 확률 계산
            improved_prob, _ = self.calculate_empirical_bev_probability(improved_tco_diff, avg_price)
            improvement = improved_prob - current_prob
            
            print(f"  • {category}: {current_prob:.1%} → {improved_prob:.1%} (+{improvement:.1%})")
        
        # 결과 출력
        if low_adoption:
            print("\n🔴 Priority Policy Support Categories (BEV Selection Rate < 30%):")
            for category, prob, tco_diff in low_adoption:
                print(f"  • {category}: {prob:.1%} (TCO Difference: {tco_diff:+.0f} KRW)")
        
        if high_adoption:
            print("\n🟢 Successful Policy Support Categories (BEV Selection Rate ≥ 30%):")
            for category, prob, tco_diff in high_adoption:
                print(f"  • {category}: {prob:.1%} (TCO Difference: {tco_diff:+.0f} KRW)")
        
        # TCO 개선이 필요한 카테고리
        expensive_bev = [row for _, row in choice_results.iterrows() if row['TCO_Difference'] > 0]
        if expensive_bev:
            print("\n💰 Categories Needing TCO Improvement (BEV more expensive than ICE):")
            for row in expensive_bev:
                print(f"  • {row['Category']}: {row['TCO_Difference']:+.0f} KRW")
    
    def save_results_to_excel(self, vehicle_analysis, choice_results):
        """Save analysis results to Excel file"""
        print("\n" + "="*60)
        print("💾 Saving Analysis Results to Excel")
        print("="*60)
        
        # Create Excel writer
        excel_filename = 'TCO_Analysis_Results_Detailed.xlsx'
        excel_filepath = os.path.join(self.results_folder, excel_filename)
        with pd.ExcelWriter(excel_filepath, engine='openpyxl') as writer:
            
            # 1. Detailed TCO by Vehicle Model
            detailed_tco = self.data[['대분류', '중분류', '소분류', '차량유형', '차량대수', 
                                    '구매비용_만원', '보조금_만원', '초기투자비용_만원',
                                    '연간연료비_만원', '연간유지보수비_만원', '연간세금보험_만원',
                                    '연간감가상각_만원', '연간기타비용_만원', '연간운영비_만원',
                                    '총운영비_만원', '잔존가치율', '잔존가치_만원', 
                                    '총TCO_만원', '연평균TCO_만원', '소유기간_년']].copy()
            
            # Add English column names
            detailed_tco.columns = ['Main_Category', 'Sub_Category', 'Model_Name', 'Vehicle_Type', 'Vehicle_Count',
                                  'Purchase_Cost_KRW', 'Subsidy_KRW', 'Initial_Investment_KRW',
                                  'Annual_Fuel_Cost_KRW', 'Annual_Maintenance_KRW', 'Annual_Tax_Insurance_KRW',
                                  'Annual_Depreciation_KRW', 'Annual_Other_Cost_KRW', 'Annual_Operating_Cost_KRW',
                                  'Total_Operating_Cost_KRW', 'Residual_Rate', 'Residual_Value_KRW',
                                  'Total_TCO_KRW', 'Annual_Average_TCO_KRW', 'Ownership_Years']
            
            detailed_tco.to_excel(writer, sheet_name='Detailed_TCO_by_Model', index=False)
            
            # 2. Consumer Choice Analysis Results
            if not choice_results.empty:
                choice_results.to_excel(writer, sheet_name='Consumer_Choice_Analysis', index=False)
            
            # 3. Summary by Category
            summary_data = []
            for category in self.data['중분류'].unique():
                category_data = self.data[self.data['중분류'] == category]
                ice_data = category_data[category_data['차량유형'] == 'ICE']
                bev_data = category_data[category_data['차량유형'] == 'BEV']
                
                if len(ice_data) > 0 and len(bev_data) > 0:
                    summary_data.append({
                        'Category': category,
                        'ICE_Model': ice_data['소분류'].iloc[0],
                        'BEV_Model': bev_data['소분류'].iloc[0],
                        'ICE_TCO_KRW': ice_data['총TCO_만원'].iloc[0],
                        'BEV_TCO_KRW': bev_data['총TCO_만원'].iloc[0],
                        'TCO_Difference_KRW': bev_data['총TCO_만원'].iloc[0] - ice_data['총TCO_만원'].iloc[0],
                        'ICE_Price_KRW': ice_data['초기투자비용_만원'].iloc[0],
                        'BEV_Price_KRW': bev_data['초기투자비용_만원'].iloc[0],
                        'ICE_Annual_Operating_KRW': ice_data['연간운영비_만원'].iloc[0],
                        'BEV_Annual_Operating_KRW': bev_data['연간운영비_만원'].iloc[0],
                        'ICE_Residual_Value_KRW': ice_data['잔존가치_만원'].iloc[0],
                        'BEV_Residual_Value_KRW': bev_data['잔존가치_만원'].iloc[0]
                    })
            
            summary_df = pd.DataFrame(summary_data)
            if not summary_df.empty:
                summary_df.to_excel(writer, sheet_name='Category_Summary', index=False)
            
            # 4. Policy Recommendations
            policy_data = []
            if not choice_results.empty:
                for _, row in choice_results.iterrows():
                    policy_data.append({
                        'Category': row['Category'],
                        'BEV_Selection_Probability': row['BEV_Selection_Probability'],
                        'TCO_Difference_KRW': row['TCO_Difference'],
                        'Relative_Impact_Percent': row['Relative_Impact'],
                        'Policy_Priority': 'High' if row['BEV_Selection_Probability'] < 0.3 else 'Medium',
                        'TCO_Improvement_Needed': 'Yes' if row['TCO_Difference'] > 0 else 'No',
                        'Current_Status': 'Needs Support' if row['BEV_Selection_Probability'] < 0.3 else 'Successful'
                    })
            
            policy_df = pd.DataFrame(policy_data)
            if not policy_df.empty:
                policy_df.to_excel(writer, sheet_name='Policy_Recommendations', index=False)
            
            # 5. Market Analysis
            market_data = []
            total_vehicles = self.data['차량대수'].sum()
            ice_total = self.data[self.data['차량유형'] == 'ICE']['차량대수'].sum()
            bev_total = self.data[self.data['차량유형'] == 'BEV']['차량대수'].sum()
            
            market_data.append({
                'Metric': 'Total Vehicles',
                'Value': total_vehicles,
                'Unit': 'Units'
            })
            market_data.append({
                'Metric': 'ICE Vehicles',
                'Value': ice_total,
                'Unit': 'Units'
            })
            market_data.append({
                'Metric': 'BEV Vehicles', 
                'Value': bev_total,
                'Unit': 'Units'
            })
            market_data.append({
                'Metric': 'ICE Market Share',
                'Value': ice_total / total_vehicles * 100,
                'Unit': '%'
            })
            market_data.append({
                'Metric': 'BEV Market Share',
                'Value': bev_total / total_vehicles * 100,
                'Unit': '%'
            })
            
            market_df = pd.DataFrame(market_data)
            market_df.to_excel(writer, sheet_name='Market_Analysis', index=False)
        
        print(f"✅ Analysis results saved to '{excel_filepath}'")
        print("📊 Excel file contains the following sheets:")
        print("   • Detailed_TCO_by_Model: Individual vehicle TCO calculations")
        print("   • Consumer_Choice_Analysis: BEV selection probability analysis")
        print("   • Category_Summary: ICE vs BEV comparison by category")
        print("   • Policy_Recommendations: Policy priority recommendations")
        print("   • Market_Analysis: Overall market statistics")
        
        return excel_filepath
    
    def run_detailed_analysis(self):
        """Run complete detailed analysis"""
        print("🚀 Starting detailed vehicle category TCO analysis...")
        
        # Load data
        if not self.load_data():
            return
        
        # Detailed analysis by vehicle model
        vehicle_analysis = self.analyze_by_vehicle_model()
        
        # Consumer choice analysis by vehicle model
        choice_results = self.analyze_consumer_choice_by_model()
        
        # Policy recommendations
        self.policy_recommendations(choice_results)
        
        # Save results to Excel
        excel_file = self.save_results_to_excel(vehicle_analysis, choice_results)
        
        print("\n" + "="*60)
        print("🎉 Detailed vehicle category TCO analysis completed!")
        print("="*60)
        
        return {
            'vehicle_analysis': vehicle_analysis,
            'choice_results': choice_results,
            'excel_file': excel_file
        }
    
    def run_segment_analysis(self):
        """세그먼트별 판매량 변화 분석 실행"""
        print("🚀 세그먼트별 판매량 변화 분석을 시작합니다...")
        
        # Load data
        if not self.load_data():
            return None
        
        results = self.analyze_segment_sales_changes()
        
        if results:
            print("\n📊 세그먼트 분석 요약:")
            print(f"• 분석된 세그먼트: {len(results)}")
            for segment, segment_name in self.segment_analyzer.segments.items():
                if segment in results:
                    print(f"  • {segment_name} ({segment})")
        
        print("\n✅ 분석이 완료되었습니다!")
        return results

def main():
    """Main function"""
    analyzer = DetailedTCOAnalyzer()
    
    # 세그먼트별 분석 직접 실행
    print("🚀 세그먼트별 판매량 변화 분석을 시작합니다...")
    results = analyzer.run_segment_analysis()
    
    if results:
        print("\n📊 세그먼트 분석 요약:")
        print(f"• 분석된 세그먼트: {len(results)}")
        for segment in results.keys():
            segment_name = analyzer.segment_analyzer.segments.get(segment, segment)
            print(f"  • {segment_name} ({segment})")
        
        # 온실가스 배출량 분석 그래프 생성
        analyzer.plot_ghg_emissions_analysis(results)
        
        # 결과 저장
        excel_file = analyzer.save_segment_analysis_results(results)
        print(f"\n💾 분석 결과가 '{excel_file}'에 저장되었습니다.")
    
    print("\n✅ 분석이 완료되었습니다!")

if __name__ == "__main__":
    main() 