#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find Inertia Coefficients for Zero Market Share Change
Iterative optimization to find inertia coefficients that make market share changes zero
"""

import pandas as pd
import numpy as np
from scipy.optimize import least_squares
import warnings
warnings.filterwarnings('ignore')

class InertiaCoefficientFinder:
    def __init__(self, excel_file_path='TCO_분석_입력템플릿.xlsx'):
        """Initialize inertia coefficient finder"""
        self.excel_path = excel_file_path
        self.data = None
        self.scenarios = {}
        self.ownership_years = 5
        
    def load_data(self):
        """Load Excel data"""
        try:
            self.data = pd.read_excel(self.excel_path, sheet_name='기본시나리오')
            # Load all scenario sheets
            xl = pd.ExcelFile(self.excel_path)
            scenario_sheets = [s for s in xl.sheet_names if '시나리오' in s]
            for sheet in scenario_sheets:
                self.scenarios[sheet] = pd.read_excel(self.excel_path, sheet_name=sheet)
            print("✅ Data loaded successfully.")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def calculate_tco(self, row):
        """Calculate TCO for individual vehicle model"""
        try:
            initial_cost = row['초기투자비용_만원']
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
        for idx, row in self.data.iterrows():
            if pd.isna(row['총TCO_만원']):
                tco_values = self.calculate_tco(row)
                for key, value in tco_values.items():
                    self.data.at[idx, key] = value
    
    def calculate_choice_probability_matrix(self, segment_data, inertia_coefficients):
        """Calculate choice probability matrix with given inertia coefficients"""
        vehicles = segment_data['차량명'].tolist()
        vehicle_grades = segment_data['차량등급'].tolist()
        n_vehicles = len(vehicles)
        probability_matrix = np.zeros((n_vehicles, n_vehicles))
        
        for i, vehicle_i in enumerate(vehicles):
            for j, vehicle_j in enumerate(vehicles):
                if i != j:
                    if vehicle_grades[i] == vehicle_grades[j]:
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
                        
                        # Use provided inertia coefficients
                        inertia_i = inertia_coefficients[i] if i < len(inertia_coefficients) else 1.0
                        inertia_j = inertia_coefficients[j] if j < len(inertia_coefficients) else 1.0
                        
                        brand_power_i = purchase_index_i * inertia_i
                        brand_power_j = purchase_index_j * inertia_j
                        
                        probability, _ = self.calculate_empirical_bev_probability(adjusted_tco_diff, avg_price, brand_power_i, brand_power_j)
                        probability_matrix[i][j] = probability
                    else:
                        probability_matrix[i][j] = 0
        
        return probability_matrix
    
    def calculate_empirical_bev_probability(self, tco_diff, vehicle_price, brand_power_i=0, brand_power_j=0):
        """Calculate BEV selection probability"""
        empirical_parameters = {
            'ev_price_elasticity': -2.5,
            'base_preference_constant': 0.18,
            'infrastructure_coefficient': 0.12,
            'environmental_coefficient': 0.10,
            'brand_power_coefficient': 0.15,
        }
        
        relative_tco_impact = tco_diff / vehicle_price
        tco_effect = empirical_parameters['ev_price_elasticity'] * relative_tco_impact
        
        infrastructure_readiness = 0.5
        environmental_concern = 0.6
        base_preference = (empirical_parameters['base_preference_constant'] + 
                          empirical_parameters['infrastructure_coefficient'] * infrastructure_readiness +
                          empirical_parameters['environmental_coefficient'] * environmental_concern)
        
        brand_power_effect = empirical_parameters['brand_power_coefficient'] * (brand_power_j - brand_power_i)
        
        range_anxiety = 0.4
        charging_infrastructure = 0.5
        technology_uncertainty = 0.3
        uncertainty_combined = np.sqrt(range_anxiety**2 + charging_infrastructure**2 + technology_uncertainty**2)
        
        np.random.seed(42)
        uncertainty_noise = np.random.normal(0, uncertainty_combined)
        
        def sigmoid(x):
            return 1 / (1 + np.exp(-x))
        
        combined_effect = tco_effect + base_preference + brand_power_effect + uncertainty_noise
        probability = sigmoid(combined_effect)
        
        return probability, {}
    
    def calculate_market_share_changes(self, original_data, modified_data, probability_matrix):
        """Calculate market share changes"""
        n_vehicles = len(original_data)
        original_shares = original_data['현재시장점유율'].values
        modified_shares = np.zeros(n_vehicles)
        
        for i in range(n_vehicles):
            share_change = 0
            for j in range(n_vehicles):
                if i != j:
                    share_change += original_shares[j] * probability_matrix[j][i]
                    share_change -= original_shares[i] * probability_matrix[i][j]
            
            modified_shares[i] = original_shares[i] + share_change
        
        modified_shares = np.maximum(modified_shares, 0)
        modified_shares = modified_shares / np.sum(modified_shares)
        
        return modified_shares
    
    def calculate_scenario_tco(self, scenario_data):
        """Calculate scenario TCO with grade-specific coefficients"""
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
            
            vehicle_grade = row['차량등급']
            if vehicle_grade == 'volume':
                tco_multiplier = 1.2
            elif vehicle_grade == 'premium':
                tco_multiplier = 0.8
            else:
                tco_multiplier = 1.0
            
            adjusted_tco = total_tco * tco_multiplier
            
            modified_data.at[idx, 'TCO_만원'] = adjusted_tco
            modified_data.at[idx, '초기투자비용_만원'] = initial_cost
            modified_data.at[idx, '연간운영비_만원'] = annual_operating_cost
            modified_data.at[idx, '총운영비_만원'] = total_operating_cost
            modified_data.at[idx, '잔존가치_만원'] = residual_value
            modified_data.at[idx, '연평균TCO_만원'] = adjusted_tco / self.ownership_years
            modified_data.at[idx, 'TCO_계수'] = tco_multiplier
        
        return modified_data
    
    def market_share_error_function(self, inertia_coefficients, original_data, scenario_data, scenario_name):
        """Error function for market share optimization"""
        try:
            # Apply inertia coefficients to scenario data
            modified_data = scenario_data.copy()
            for i, (_, row) in enumerate(modified_data.iterrows()):
                if i < len(inertia_coefficients):
                    modified_data.at[row.name, '관성계수'] = inertia_coefficients[i]
            
            # Calculate probability matrix with new inertia coefficients
            probability_matrix = self.calculate_choice_probability_matrix(modified_data, inertia_coefficients)
            
            # Calculate market share changes
            modified_shares = self.calculate_market_share_changes(original_data, modified_data, probability_matrix)
            
            # Calculate errors (target: zero change)
            original_shares = original_data['현재시장점유율'].values
            errors = modified_shares - original_shares
            
            return errors
            
        except Exception as e:
            print(f"Error in market_share_error_function: {e}")
            return np.ones(len(original_data)) * 1000  # Large error
    
    def find_optimal_inertia_coefficients(self, segment_name, max_iterations=3):
        """Find optimal inertia coefficients for zero market share change"""
        print(f"\n🔍 {segment_name} 세그먼트 관성계수 최적화 시작")
        
        # Get segment data
        segment_data = self.data[self.data['중분류'] == segment_name].copy()
        if segment_data.empty:
            print(f"⚠️ {segment_name} 세그먼트 데이터가 없습니다.")
            return None
        
        # Calculate market shares
        total_sales = segment_data['차량대수'].sum()
        market_shares = []
        for _, vehicle in segment_data.iterrows():
            share = vehicle['차량대수'] / total_sales if total_sales > 0 else 0
            market_shares.append({
                '차량명': vehicle['소분류'],
                '차량유형': vehicle['차량유형'],
                '차량등급': vehicle['차량등급'],
                '현재판매량': vehicle['차량대수'],
                '현재시장점유율': share,
                'TCO_만원': vehicle['총TCO_만원'],
                '초기투자비용_만원': vehicle['초기투자비용_만원'],
                '구매지수': vehicle['구매지수'] if '구매지수' in vehicle and pd.notna(vehicle['구매지수']) else 0,
                '관성계수': vehicle['관성계수'] if '관성계수' in vehicle and pd.notna(vehicle['관성계수']) else 1.0,
                '브랜드파워': vehicle['구매지수'] * vehicle['관성계수'] if '구매지수' in vehicle and '관성계수' in vehicle else 0
            })
        
        original_data = pd.DataFrame(market_shares)
        
        # Get scenario data
        scenario_name = list(self.scenarios.keys())[0] if self.scenarios else '기본시나리오'
        scenario_data = self.scenarios.get(scenario_name, self.data)
        
        # Filter scenario data for this segment
        vehicle_column = None
        for col in scenario_data.columns:
            if '소분류' in col or '차량명' in col or '모델' in col:
                vehicle_column = col
                break
        
        if vehicle_column is None:
            print(f"⚠️ {scenario_name}에서 차량명 컬럼을 찾을 수 없습니다.")
            return None
        
        segment_vehicles = segment_data['소분류'].tolist()
        scenario_segment_data = scenario_data[scenario_data[vehicle_column].isin(segment_vehicles)].copy()
        
        if scenario_segment_data.empty:
            print(f"⚠️ {scenario_name}에서 해당 세그먼트 차량을 찾을 수 없습니다.")
            return None
        
        # Calculate scenario TCO
        modified_scenario_data = self.calculate_scenario_tco(scenario_segment_data)
        
        # Initialize inertia coefficients
        n_vehicles = len(original_data)
        current_inertia = np.ones(n_vehicles)
        
        print(f"📊 {len(original_data)}개 모델에 대해 관성계수 최적화 시작")
        
        # Iterative optimization
        for iteration in range(max_iterations):
            print(f"\n🔄 반복 {iteration + 1}/{max_iterations}")
            
            # Define bounds for inertia coefficients based on vehicle type
            # BEV: 0.1~1.0, ICE: 0.01~100.0
            lower_bounds = []
            upper_bounds = []
            for _, vehicle in original_data.iterrows():
                if vehicle['차량유형'] == 'BEV':
                    lower_bounds.append(0.1)  # BEV: 0.1~1.0
                    upper_bounds.append(1.0)
                else:
                    lower_bounds.append(0.01)  # ICE: 0.01~100.0
                    upper_bounds.append(100.0)
            
            # Optimize inertia coefficients with vehicle-specific bounds
            result = least_squares(
                self.market_share_error_function,
                current_inertia,
                args=(original_data, modified_scenario_data, scenario_name),
                bounds=(lower_bounds, upper_bounds),
                method='trf',
                ftol=1e-8,
                xtol=1e-8
            )
            
            if result.success:
                current_inertia = result.x
                final_errors = result.fun
                
                print(f"✅ 반복 {iteration + 1} 완료")
                print(f"   최적화 성공: {result.success}")
                print(f"   최종 오차: {np.mean(np.abs(final_errors)):.6f}")
                
                # Show current results
                for i, (_, vehicle) in enumerate(original_data.iterrows()):
                    if i < len(current_inertia):
                        print(f"   {vehicle['차량명']}: 관성계수 = {current_inertia[i]:.3f}, 오차 = {final_errors[i]:.6f}")
            else:
                print(f"⚠️ 반복 {iteration + 1}에서 최적화 실패")
                break
        
        # Final results
        print(f"\n📈 {segment_name} 세그먼트 최종 결과:")
        results = []
        for i, (_, vehicle) in enumerate(original_data.iterrows()):
            if i < len(current_inertia):
                results.append({
                    '세그먼트': segment_name,
                    '차량명': vehicle['차량명'],
                    '차량유형': vehicle['차량유형'],
                    '차량등급': vehicle['차량등급'],
                    '최적_관성계수': current_inertia[i],
                    '원본_관성계수': vehicle['관성계수'],
                    '변화율': (current_inertia[i] - vehicle['관성계수']) / vehicle['관성계수'] * 100 if vehicle['관성계수'] != 0 else 0
                })
        
        results_df = pd.DataFrame(results)
        print(results_df.round(3))
        
        return results_df
    
    def find_all_segments_inertia_coefficients(self):
        """Find optimal inertia coefficients for all segments"""
        print("🚀 모든 세그먼트 관성계수 최적화 시작")
        
        if not self.load_data():
            return None
        
        self.calculate_all_tco()
        
        # Get all segments
        segments = self.data['중분류'].unique()
        print(f"📊 분석할 세그먼트: {list(segments)}")
        
        all_results = []
        
        for segment in segments:
            segment_results = self.find_optimal_inertia_coefficients(segment)
            if segment_results is not None:
                all_results.append(segment_results)
        
        if all_results:
            # Combine all results
            combined_results = pd.concat(all_results, ignore_index=True)
            
            # Save results
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Elasticity_Optimization_Results_{timestamp}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                combined_results.to_excel(writer, sheet_name='최적_관성계수', index=False)
                
                # Summary statistics
                summary = combined_results.groupby('세그먼트').agg({
                    '최적_관성계수': ['mean', 'std', 'min', 'max'],
                    '변화율': ['mean', 'std', 'min', 'max']
                }).round(3)
                summary.to_excel(writer, sheet_name='세그먼트별_요약')
            
            print(f"\n✅ 결과가 '{filename}'에 저장되었습니다.")
            print(f"\n📊 전체 결과 요약:")
            print(combined_results.round(3))
            
            return combined_results
        
        return None

def main():
    """Main function"""
    finder = InertiaCoefficientFinder()
    results = finder.find_all_segments_inertia_coefficients()
    
    if results is not None:
        print("\n🎉 모든 세그먼트 관성계수 최적화 완료!")
    else:
        print("\n❌ 관성계수 최적화 중 오류가 발생했습니다.")

if __name__ == "__main__":
    main() 