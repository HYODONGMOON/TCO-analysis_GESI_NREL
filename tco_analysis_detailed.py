#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed TCO Analysis by Vehicle Model (16 vehicle types individual analysis)
Empirical research-based parameters applied
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

class DetailedTCOAnalyzer:
    def __init__(self, excel_file_path='TCO_분석_입력템플릿.xlsx'):
        """Initialize detailed TCO analyzer"""
        self.excel_path = excel_file_path
        self.data = None
        self.scenario_data = None
        self.yearly_data = None
        self.ownership_years = 5
        
    def load_data(self):
        """Load Excel data"""
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
        # price_elasticity × (TCO_difference / vehicle_price)
        relative_tco_impact = tco_diff / vehicle_price
        tco_effect = empirical_parameters['ev_price_elasticity'] * relative_tco_impact
        
        # 2. 기본 선호도 계산 (PDF 수식)
        # [0.18 + 0.12 × infrastructure + 0.10 × environment]
        infrastructure_readiness = 0.5  # 기본값
        environmental_concern = 0.6     # 기본값
        base_preference = (empirical_parameters['base_preference_constant'] + 
                          empirical_parameters['infrastructure_coefficient'] * infrastructure_readiness +
                          empirical_parameters['environmental_coefficient'] * environmental_concern)
        
        # 3. 통합 불확실성 계산 (PDF 수식)
        # Uncertainty = √(range_anxiety² + charging_infrastructure² + technology_uncertainty²)
        range_anxiety = 0.4
        charging_infrastructure = 0.5
        technology_uncertainty = 0.3
        uncertainty_combined = np.sqrt(range_anxiety**2 + charging_infrastructure**2 + technology_uncertainty**2)
        
        # 4. 정규분포 불확실성 생성
        # normal_distribution(0, uncertainty_combined)
        np.random.seed(42)  # 재현성을 위한 시드 설정
        uncertainty_noise = np.random.normal(0, uncertainty_combined)
        
        # 5. 최종 확률 계산 (PDF 수식)
        # BEV_probability = sigmoid(price_elasticity × (TCO_difference / vehicle_price) + 
        #                          [0.18 + 0.12 × infrastructure + 0.10 × environment] + 
        #                          normal_distribution(0, uncertainty_combined))
        
        # Sigmoid 함수 정의
        def sigmoid(x):
            return 1 / (1 + np.exp(-x))
        
        # 각 요소를 더한 후 sigmoid 적용
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
        plt.savefig('Vehicle_Category_TCO_Analysis.png', dpi=300, bbox_inches='tight')
        print("✅ Vehicle category TCO analysis graph saved as 'Vehicle_Category_TCO_Analysis.png'")
        
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
        
        print(f"✅ Analysis results saved to '{excel_filename}'")
        print("📊 Excel file contains the following sheets:")
        print("   • Detailed_TCO_by_Model: Individual vehicle TCO calculations")
        print("   • Consumer_Choice_Analysis: BEV selection probability analysis")
        print("   • Category_Summary: ICE vs BEV comparison by category")
        print("   • Policy_Recommendations: Policy priority recommendations")
        print("   • Market_Analysis: Overall market statistics")
        
        return excel_filename
    
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

def main():
    """Main function"""
    analyzer = DetailedTCOAnalyzer()
    results = analyzer.run_detailed_analysis()
    
    if results:
        print("\n📊 Analysis Summary:")
        print(f"• Total vehicle models analyzed: {len(analyzer.data)}")
        print(f"• ICE models: {len(analyzer.data[analyzer.data['차량유형'] == 'ICE'])}")
        print(f"• BEV models: {len(analyzer.data[analyzer.data['차량유형'] == 'BEV'])}")
        print(f"• Subcategories: {analyzer.data['중분류'].nunique()}")

if __name__ == "__main__":
    main() 