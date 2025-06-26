#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrected TCO Analysis with PDF Formula Implementation
PDF의 정확한 수식을 반영한 TCO 분석
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

warnings.filterwarnings('ignore')

# Set Korean font for matplotlib
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Malgun Gothic', 'NanumGothic']
plt.rcParams['axes.unicode_minus'] = False

class CorrectedTCOAnalyzer:
    def __init__(self, excel_file_path='TCO_분석_입력템플릿.xlsx'):
        """수정된 TCO 분석기 초기화"""
        self.excel_path = excel_file_path
        self.data = None
        self.scenario_data = None
        self.yearly_data = None
        self.ownership_years = 5
        
        # PDF 기반 정확한 매개변수
        self.empirical_parameters = {
            'ev_price_elasticity': -2.5,  # -2.0 ~ -2.8 범위에서 중간값
            'base_preference_constant': 0.18,  # 기본 선호도 상수
            'infrastructure_coefficient': 0.12,  # 인프라 준비도 계수
            'environmental_coefficient': 0.10,  # 환경 우려 계수
            'market_share_effect': 0.27,  # 시장 점유율 효과 (2030년 예측)
            'uncertainty_weights': {
                'range_anxiety': 0.3,
                'charging_infrastructure': 0.4,
                'technology_uncertainty': 0.3
            }
        }
        
    def load_data(self):
        """엑셀 데이터 로드"""
        try:
            self.data = pd.read_excel(self.excel_path, sheet_name='차량분류')
            self.scenario_data = pd.read_excel(self.excel_path, sheet_name='지원제거시나리오')
            self.yearly_data = pd.read_excel(self.excel_path, sheet_name='연도별TCO')
            print("✅ Data loaded successfully.")
            print(f"📊 Total {len(self.data)} vehicle models analyzed")
            return True
        except FileNotFoundError:
            print(f"❌ File not found: {self.excel_path}")
            return False
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def calculate_base_preference(self, infrastructure_readiness=0.5, environmental_concern=0.6):
        """PDF 기반 기본 선호도 계산"""
        # PDF 수식: Base_preference = 0.18 + 0.12 × infrastructure_readiness + 0.10 × environmental_concern
        base_pref = (self.empirical_parameters['base_preference_constant'] + 
                    self.empirical_parameters['infrastructure_coefficient'] * infrastructure_readiness +
                    self.empirical_parameters['environmental_coefficient'] * environmental_concern)
        
        return np.clip(base_pref, 0, 1)
    
    def calculate_uncertainty(self, range_anxiety=0.4, charging_infrastructure=0.5, technology_uncertainty=0.3):
        """PDF 기반 통합 불확실성 계산"""
        # PDF 수식: Uncertainty = √(range_anxiety² + charging_infrastructure² + technology_uncertainty²)
        uncertainty = np.sqrt(range_anxiety**2 + charging_infrastructure**2 + technology_uncertainty**2)
        return np.clip(uncertainty, 0, 1)
    
    def calculate_tco_effect(self, tco_diff, vehicle_price, current_market_share=0.05):
        """PDF 기반 TCO 효과 계산"""
        # PDF 수식: TCO_effect = price_elasticity × (TCO_difference / vehicle_price) × base_market_share × (1 - base_market_share)
        relative_tco_impact = tco_diff / vehicle_price
        tco_effect = (self.empirical_parameters['ev_price_elasticity'] * 
                     relative_tco_impact * 
                     current_market_share * 
                     (1 - current_market_share))
        return tco_effect
    
    def calculate_corrected_bev_probability(self, tco_diff, vehicle_price, 
                                          infrastructure_readiness=0.5, 
                                          environmental_concern=0.6,
                                          range_anxiety=0.4, 
                                          charging_infrastructure=0.5, 
                                          technology_uncertainty=0.3,
                                          current_market_share=0.05):
        """PDF 기반 수정된 BEV 선택 확률 계산"""
        
        # 1. 기본 선호도 계산 (PDF 수식)
        base_preference = self.calculate_base_preference(infrastructure_readiness, environmental_concern)
        
        # 2. TCO 효과 계산 (PDF 수식)
        tco_effect = self.calculate_tco_effect(tco_diff, vehicle_price, current_market_share)
        
        # 3. 시장 점유율 효과
        market_share_effect = self.empirical_parameters['market_share_effect'] * (1 - current_market_share)
        
        # 4. 통합 불확실성 계산 (PDF 수식)
        uncertainty = self.calculate_uncertainty(range_anxiety, charging_infrastructure, technology_uncertainty)
        
        # 5. 최종 확률 계산 (불확실성 고려)
        raw_probability = base_preference + tco_effect + market_share_effect
        final_probability = raw_probability * (1 - uncertainty)  # 불확실성이 높을수록 확률 감소
        
        return np.clip(final_probability, 0, 1), {
            'base_preference': base_preference,
            'tco_effect': tco_effect,
            'market_share_effect': market_share_effect,
            'uncertainty': uncertainty,
            'raw_probability': raw_probability
        }
    
    def calculate_tco(self, row):
        """개별 차종의 TCO 계산"""
        try:
            # 기본 비용 구성요소
            initial_cost = row['초기투자비용_만원']
            annual_fuel = row['연간연료비_만원']
            annual_maintenance = row['연간유지보수비_만원']
            annual_tax_insurance = row['연간세금보험_만원']
            annual_depreciation = row['연간감가상각_만원']
            annual_other = row['연간기타비용_만원'] if pd.notna(row['연간기타비용_만원']) else 0
            
            # 연간 운영비 계산
            annual_operating_cost = annual_fuel + annual_maintenance + annual_tax_insurance + annual_other
            
            # 총 운영비 (5년)
            total_operating_cost = annual_operating_cost * self.ownership_years
            
            # 잔존가치 계산
            residual_rate = row['잔존가치율'] if pd.notna(row['잔존가치율']) else 0.3  # 기본값 30%
            residual_value = initial_cost * residual_rate
            
            # 총 TCO 계산
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
        """모든 차종의 TCO 계산"""
        print("🔧 Calculating TCO...")
        
        for idx, row in self.data.iterrows():
            if pd.isna(row['총TCO_만원']):  # If TCO not calculated
                tco_values = self.calculate_tco(row)
                
                # Update calculated values to dataframe
                for key, value in tco_values.items():
                    self.data.at[idx, key] = value
        
        print("✅ TCO calculation completed")
        
    def analyze_by_vehicle_model(self):
        """차종별 세부 분석"""
        print("\n" + "="*60)
        print("🚗 Detailed TCO Analysis by Vehicle Model (Corrected)")
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
    
    def analyze_consumer_choice_by_model(self):
        """차종별 소비자 선택 분석 (수정된 모델)"""
        print("\n" + "="*60)
        print("🎯 Corrected Consumer Choice Analysis by Vehicle Model")
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
                    
                    # Calculate corrected BEV selection probability
                    bev_probability, components = self.calculate_corrected_bev_probability(tco_diff, avg_price)
                    
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
                        'Base_Preference': components['base_preference'],
                        'TCO_Effect': components['tco_effect'],
                        'Market_Share_Effect': components['market_share_effect'],
                        'Uncertainty': components['uncertainty'],
                        'Raw_Probability': components['raw_probability']
                    })
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(results)
        
        print("📊 Corrected Consumer Choice Analysis Results:")
        print(results_df.round(4))
        
        # Visualization
        self.plot_corrected_analysis(results_df)
        
        return results_df
    
    def plot_corrected_analysis(self, results_df):
        """수정된 분석 결과 시각화"""
        plt.figure(figsize=(16, 12))
        
        # 1. 수정된 BEV 선택 확률 vs TCO 차이
        plt.subplot(2, 2, 1)
        plt.scatter(results_df['TCO_Difference'], results_df['BEV_Selection_Probability'], 
                   s=100, alpha=0.7, c='green')
        
        for i, row in results_df.iterrows():
            plt.annotate(row['Category'], (row['TCO_Difference'], row['BEV_Selection_Probability']), 
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        plt.xlabel('TCO Difference (BEV - ICE, KRW)')
        plt.ylabel('Corrected BEV Selection Probability')
        plt.title('Corrected BEV Selection Probability vs TCO Difference')
        plt.grid(True, alpha=0.3)
        
        # 2. 확률 구성요소 분해
        plt.subplot(2, 2, 2)
        categories = results_df['Category']
        base_pref = results_df['Base_Preference']
        tco_effect = results_df['TCO_Effect']
        market_effect = results_df['Market_Share_Effect']
        uncertainty = results_df['Uncertainty']
        
        x = np.arange(len(categories))
        width = 0.2
        
        plt.bar(x - width*1.5, base_pref, width, label='Base Preference', color='lightblue')
        plt.bar(x - width*0.5, tco_effect, width, label='TCO Effect', color='lightgreen')
        plt.bar(x + width*0.5, market_effect, width, label='Market Share Effect', color='lightcoral')
        plt.bar(x + width*1.5, uncertainty, width, label='Uncertainty', color='lightyellow')
        
        plt.xlabel('Vehicle Category')
        plt.ylabel('Probability Components')
        plt.title('Probability Components by Category')
        plt.xticks(x, categories, rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 3. 수정 전후 비교
        plt.subplot(2, 2, 3)
        corrected_prob = results_df['BEV_Selection_Probability']
        raw_prob = results_df['Raw_Probability']
        
        x = np.arange(len(categories))
        width = 0.35
        
        plt.bar(x - width/2, raw_prob, width, label='Raw Probability', color='skyblue')
        plt.bar(x + width/2, corrected_prob, width, label='Corrected Probability', color='lightgreen')
        plt.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='50% Baseline')
        
        plt.xlabel('Vehicle Category')
        plt.ylabel('BEV Selection Probability')
        plt.title('Raw vs Corrected Probability')
        plt.xticks(x, categories, rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 4. 불확실성 영향
        plt.subplot(2, 2, 4)
        plt.scatter(results_df['Uncertainty'], results_df['BEV_Selection_Probability'], 
                   s=100, alpha=0.7, c='purple')
        
        for i, row in results_df.iterrows():
            plt.annotate(row['Category'], (row['Uncertainty'], row['BEV_Selection_Probability']), 
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        plt.xlabel('Uncertainty')
        plt.ylabel('Corrected BEV Selection Probability')
        plt.title('Uncertainty Impact on Selection Probability')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('Corrected_TCO_Analysis.png', dpi=300, bbox_inches='tight')
        print("✅ Corrected TCO analysis graph saved as 'Corrected_TCO_Analysis.png'")
        
        return plt.gcf()
    
    def save_corrected_results_to_excel(self, vehicle_analysis, choice_results):
        """수정된 분석 결과를 엑셀 파일로 저장"""
        print("\n" + "="*60)
        print("💾 Saving Corrected Analysis Results to Excel")
        print("="*60)
        
        # Create Excel writer
        excel_filename = 'Corrected_TCO_Analysis_Results.xlsx'
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            
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
            
            # 2. Corrected Consumer Choice Analysis Results
            if not choice_results.empty:
                choice_results.to_excel(writer, sheet_name='Corrected_Consumer_Choice_Analysis', index=False)
            
            # 3. Probability Components Analysis
            if not choice_results.empty:
                components_df = choice_results[['Category', 'Base_Preference', 'TCO_Effect', 
                                              'Market_Share_Effect', 'Uncertainty', 'Raw_Probability', 
                                              'BEV_Selection_Probability']].copy()
                components_df.to_excel(writer, sheet_name='Probability_Components', index=False)
            
            # 4. Model Parameters
            params_data = []
            for key, value in self.empirical_parameters.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        params_data.append({
                            'Parameter': f"{key}_{sub_key}",
                            'Value': sub_value,
                            'Description': f'PDF-based parameter: {key} - {sub_key}'
                        })
                else:
                    params_data.append({
                        'Parameter': key,
                        'Value': value,
                        'Description': f'PDF-based parameter: {key}'
                    })
            
            params_df = pd.DataFrame(params_data)
            params_df.to_excel(writer, sheet_name='Model_Parameters', index=False)
        
        print(f"✅ Corrected analysis results saved to '{excel_filename}'")
        print("📊 Excel file contains the following sheets:")
        print("   • Detailed_TCO_by_Model: Individual vehicle TCO calculations")
        print("   • Corrected_Consumer_Choice_Analysis: PDF-based BEV selection probability")
        print("   • Probability_Components: Detailed probability breakdown")
        print("   • Model_Parameters: PDF-based model parameters")
        
        return excel_filename
    
    def run_corrected_analysis(self):
        """수정된 전체 분석 실행"""
        print("🚀 Starting corrected TCO analysis with PDF formulas...")
        
        # Load data
        if not self.load_data():
            return
        
        # Detailed analysis by vehicle model
        vehicle_analysis = self.analyze_by_vehicle_model()
        
        # Corrected consumer choice analysis
        choice_results = self.analyze_consumer_choice_by_model()
        
        # Save corrected results to Excel
        excel_file = self.save_corrected_results_to_excel(vehicle_analysis, choice_results)
        
        print("\n" + "="*60)
        print("🎉 Corrected TCO analysis completed!")
        print("="*60)
        
        return {
            'vehicle_analysis': vehicle_analysis,
            'choice_results': choice_results,
            'excel_file': excel_file
        }

def main():
    """Main function"""
    analyzer = CorrectedTCOAnalyzer()
    results = analyzer.run_corrected_analysis()
    
    if results:
        print("\n📊 Corrected Analysis Summary:")
        print(f"• Total vehicle models analyzed: {len(analyzer.data)}")
        print(f"• ICE models: {len(analyzer.data[analyzer.data['차량유형'] == 'ICE'])}")
        print(f"• BEV models: {len(analyzer.data[analyzer.data['차량유형'] == 'BEV'])}")
        print(f"• Subcategories: {analyzer.data['중분류'].nunique()}")
        print(f"• PDF-based formulas applied successfully")

if __name__ == "__main__":
    main() 