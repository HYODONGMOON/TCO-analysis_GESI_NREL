#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCO (Total Cost of Ownership) 분석 스크립트
5년 소유기간 기준 올바른 TCO 계산 적용
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

class ImprovedTCOAnalyzer:
    def __init__(self, excel_file_path='TCO_분석_입력템플릿.xlsx'):
        """TCO 분석기 초기화"""
        self.excel_path = excel_file_path
        self.data = None
        self.scenario_data = None
        self.yearly_data = None
        self.ownership_years = 5
        
    def load_data(self):
        """엑셀 데이터 로드"""
        try:
            self.data = pd.read_excel(self.excel_path, sheet_name='차량분류')
            self.scenario_data = pd.read_excel(self.excel_path, sheet_name='지원제거시나리오')
            self.yearly_data = pd.read_excel(self.excel_path, sheet_name='연도별TCO')
            print("✅ 데이터가 성공적으로 로드되었습니다.")
            return True
        except FileNotFoundError:
            print(f"❌ 파일을 찾을 수 없습니다: {self.excel_path}")
            return False
        except Exception as e:
            print(f"❌ 데이터 로드 중 오류 발생: {e}")
            return False
    
    def calculate_weighted_tco(self, df, tco_column='총TCO_만원'):
        """차량 대수를 고려한 가중평균 TCO 계산"""
        total_vehicles = df['차량대수'].sum()
        weighted_tco = (df[tco_column] * df['차량대수']).sum() / total_vehicles
        return weighted_tco
    
    def analyze_by_vehicle_type(self):
        """차량 유형별 TCO 분석"""
        print("\n" + "="*60)
        print("🚗 차량 유형별 TCO 분석 (5년 소유기간 기준)")
        print("="*60)
        
        # 기본 TCO 분석
        vehicle_type_analysis = self.data.groupby('차량유형').agg({
            '총TCO_만원': 'mean',
            '연평균TCO_만원': 'mean',
            '초기투자비용_만원': 'mean',
            '연간운영비_만원': 'mean',
            '잔존가치_만원': 'mean',
            '차량대수': 'sum'
        }).round(2)
        
        # 가중평균 계산
        ice_data = self.data[self.data['차량유형'] == 'ICE']
        bev_data = self.data[self.data['차량유형'] == 'BEV']
        
        ice_weighted_tco = self.calculate_weighted_tco(ice_data, '총TCO_만원')
        bev_weighted_tco = self.calculate_weighted_tco(bev_data, '총TCO_만원')
        
        print(f"ICE 평균 총TCO (5년): {ice_weighted_tco:,.0f}만원")
        print(f"BEV 평균 총TCO (5년): {bev_weighted_tco:,.0f}만원")
        print(f"TCO 차이 (BEV-ICE): {bev_weighted_tco - ice_weighted_tco:+,.0f}만원")
        
        # 연평균 TCO
        ice_weighted_annual = ice_weighted_tco / self.ownership_years
        bev_weighted_annual = bev_weighted_tco / self.ownership_years
        
        print(f"\nICE 연평균 TCO: {ice_weighted_annual:,.0f}만원/년")
        print(f"BEV 연평균 TCO: {bev_weighted_annual:,.0f}만원/년")
        print(f"연평균 차이 (BEV-ICE): {bev_weighted_annual - ice_weighted_annual:+,.0f}만원/년")
        
        return vehicle_type_analysis
    
    def analyze_cost_components(self):
        """비용 구성요소별 분석"""
        print("\n" + "="*60)
        print("💰 비용 구성요소별 분석")
        print("="*60)
        
        cost_components = ['초기투자비용_만원', '총운영비_만원', '잔존가치_만원']
        
        ice_data = self.data[self.data['차량유형'] == 'ICE']
        bev_data = self.data[self.data['차량유형'] == 'BEV']
        
        comparison = pd.DataFrame({
            'ICE': [
                self.calculate_weighted_tco(ice_data, '초기투자비용_만원'),
                self.calculate_weighted_tco(ice_data, '총운영비_만원'),
                self.calculate_weighted_tco(ice_data, '잔존가치_만원')
            ],
            'BEV': [
                self.calculate_weighted_tco(bev_data, '초기투자비용_만원'),
                self.calculate_weighted_tco(bev_data, '총운영비_만원'),
                self.calculate_weighted_tco(bev_data, '잔존가치_만원')
            ]
        }, index=['초기투자비용', '5년총운영비', '5년후잔존가치'])
        
        comparison['차이(BEV-ICE)'] = comparison['BEV'] - comparison['ICE']
        comparison['차이비율(%)'] = (comparison['차이(BEV-ICE)'] / comparison['ICE'] * 100).round(1)
        
        print(comparison.round(0))
        
        return comparison
    
    def scenario_analysis(self):
        """시나리오 분석 (ICE 숨겨진 지원 제거)"""
        print("\n" + "="*60)
        print("📊 시나리오 분석: ICE 숨겨진 지원 제거 시")
        print("="*60)
        
        # 원래 TCO
        ice_original = self.calculate_weighted_tco(
            self.scenario_data[self.scenario_data['차량유형'] == 'ICE'], '총TCO_만원'
        )
        bev_original = self.calculate_weighted_tco(
            self.scenario_data[self.scenario_data['차량유형'] == 'BEV'], '총TCO_만원'
        )
        
        # 조정된 TCO (ICE 지원 제거 후)
        ice_adjusted = self.calculate_weighted_tco(
            self.scenario_data[self.scenario_data['차량유형'] == 'ICE'], '조정후총TCO_만원'
        )
        bev_adjusted = bev_original  # BEV는 변화 없음
        
        print(f"현재 상황:")
        print(f"  ICE 총TCO: {ice_original:,.0f}만원")
        print(f"  BEV 총TCO: {bev_original:,.0f}만원")
        print(f"  차이: {bev_original - ice_original:+,.0f}만원 (BEV 불리)")
        
        print(f"\nICE 지원 제거 후:")
        print(f"  ICE 총TCO: {ice_adjusted:,.0f}만원 (+{ice_adjusted - ice_original:,.0f}만원)")
        print(f"  BEV 총TCO: {bev_adjusted:,.0f}만원 (변화없음)")
        print(f"  차이: {bev_adjusted - ice_adjusted:+,.0f}만원", end="")
        
        if bev_adjusted < ice_adjusted:
            print(" (BEV 유리)")
        elif bev_adjusted > ice_adjusted:
            print(" (ICE 유리)")
        else:
            print(" (동등)")
        
        return {
            'ice_original': ice_original,
            'ice_adjusted': ice_adjusted,
            'bev': bev_original,
            'support_removal_impact': ice_adjusted - ice_original
        }
    
    def yearly_analysis(self):
        """연도별 TCO 분석"""
        print("\n" + "="*60)
        print("📈 연도별 TCO 분석")
        print("="*60)
        
        yearly_summary = self.yearly_data.groupby(['차량유형', '연도']).agg({
            '해당연도TCO_만원': 'mean',
            '누적TCO_만원': 'mean'
        }).round(0)
        
        print("연도별 평균 TCO:")
        print(yearly_summary)
        
        return yearly_summary
    
    def consumer_choice_model(self):
        """소비자 선택 모델 (실증 연구 기반 매개변수 적용)"""
        print("\n" + "="*60)
        print("🎯 실증 연구 기반 소비자 선택 모델 분석")
        print("="*60)
        
        # 1. 기본 특성 변수 선택
        features = ['총TCO_만원', '초기투자비용_만원', '연간운영비_만원', '잔존가치_만원']
        X = self.data[features]
        y = (self.data['차량유형'] == 'BEV').astype(int)  # BEV=1, ICE=0
        
        # 2. 실증 연구 기반 매개변수 설정 (PDF 3페이지 기준)
        empirical_parameters = {
            # 전기차 가격 탄력성: -2.0 ~ -2.8 (실증 연구 기반)
            'ev_price_elasticity': -2.5,
            
            # 차량가격 10% 변화당 약 25~30% 선택률 변화
            'price_change_effect': 0.275,  # 25~30%의 중간값
            
            # 기본 선호도: 순수 기술 선호자 15-20%
            'base_preference': 0.175,  # 15-20%의 중간값
            
            # 시장 점유율 효과 계수
            'market_share_effect': 0.15,
            
            # 현재 BEV 시장 점유율 (가정)
            'current_market_share': 0.05
        }
        
        print("📊 실증 연구 기반 매개변수:")
        for key, value in empirical_parameters.items():
            print(f"  {key}: {value}")
        
        # 3. 실증 연구 기반 BEV 선택 확률 계산 함수
        def calculate_empirical_bev_probability(tco_diff, vehicle_price, current_market_share=0.05):
            """
            실증 연구 기반 BEV 선택 확률 계산 (PDF 3페이지 공식 적용)
            
            Args:
                tco_diff: TCO 차이 (BEV - ICE, 만원)
                vehicle_price: 차량 구매 가격 (만원)
                current_market_share: 현재 BEV 시장 점유율
            """
            
            # PDF 3페이지 공식: TCO_effect = price_elasticity × (TCO_difference / vehicle_price) × base_market_share × (1 - base_market_share)
            relative_tco_impact = tco_diff / vehicle_price
            tco_effect = (empirical_parameters['ev_price_elasticity'] * 
                         relative_tco_impact * 
                         current_market_share * 
                         (1 - current_market_share))
            
            # 기본 선호도 (순수 기술 선호자)
            base_effect = empirical_parameters['base_preference']
            
            # 시장 점유율 효과 (포화 상태에 가까워질수록 감소)
            market_share_effect = empirical_parameters['market_share_effect'] * (1 - current_market_share)
            
            # 최종 확률 계산
            probability = base_effect + tco_effect + market_share_effect
            
            # 0~1 범위로 제한
            probability = np.clip(probability, 0, 1)
            
            return probability
        
        # 4. 현재 TCO 값들
        current_ice_tco = self.calculate_weighted_tco(self.data[self.data['차량유형'] == 'ICE'], '총TCO_만원')
        current_bev_tco = self.calculate_weighted_tco(self.data[self.data['차량유형'] == 'BEV'], '총TCO_만원')
        
        print(f"\n현재 TCO 차이 (BEV-ICE): {current_bev_tco - current_ice_tco:+.0f}만원")
        
        # 5. 차량 가격별 시나리오 분석
        vehicle_scenarios = [
            {'name': '경제형', 'price': 2000, 'description': '2000만원 차량'},
            {'name': '중급형', 'price': 5000, 'description': '5000만원 차량'},
            {'name': '고급형', 'price': 10000, 'description': '1억원 차량'},
            {'name': '럭셔리형', 'price': 20000, 'description': '2억원 차량'}
        ]
        
        print("\n📊 차량 가격별 BEV 선택 확률 (실증 연구 기반):")
        print("차량 유형 | 구매가격 | TCO 차이 | 선택확률 | 상대적영향")
        print("-" * 70)
        
        tco_differences = [-1000, -500, 0, 500, 1000]
        for scenario in vehicle_scenarios:
            price = scenario['price']
            name = scenario['name']
            
            for tco_diff in tco_differences:
                prob = calculate_empirical_bev_probability(tco_diff, price)
                relative_impact = tco_diff / price * 100
                
                print(f"{name:8s} | {price:6.0f}만원 | {tco_diff:+5.0f}만원 | {prob:.1%} | {relative_impact:+6.1f}%")
        
        # 6. TCO 차이 변화 시뮬레이션
        tco_differences_range = np.linspace(-3000, 3000, 61)
        bev_probabilities = []
        
        # 중급차(5000만원) 기준으로 시뮬레이션
        base_price = 5000
        
        for tco_diff in tco_differences_range:
            prob = calculate_empirical_bev_probability(tco_diff, base_price)
            bev_probabilities.append(prob)
        
        # 7. 주요 지점별 선택률 분석
        key_points = [-2000, -1000, -500, 0, 500, 1000, 2000]
        print("\n주요 TCO 차이별 BEV 선택률 (실증 연구 기반):")
        for diff in key_points:
            idx = np.argmin(np.abs(tco_differences_range - diff))
            prob = bev_probabilities[idx]
            print(f"  TCO 차이 {diff:+5.0f}만원: BEV 선택률 {prob:.1%}")
        
        # 8. 현재 상황에서의 선택률
        current_diff = current_bev_tco - current_ice_tco
        current_prob_idx = np.argmin(np.abs(tco_differences_range - current_diff))
        current_prob = bev_probabilities[current_prob_idx]
        print(f"\n현재 상황에서 BEV 선택률: {current_prob:.1%}")
        
        # 9. 정책 시사점 분석
        print("\n📈 정책 시사점:")
        
        # TCO 차이별 시장 점유율 변화
        tco_improvements = [-1000, -500, 0, 500, 1000]
        print("TCO 개선에 따른 BEV 시장 점유율 변화:")
        for improvement in tco_improvements:
            new_diff = current_diff + improvement
            idx = np.argmin(np.abs(tco_differences_range - new_diff))
            new_prob = bev_probabilities[idx]
            change = new_prob - current_prob
            print(f"  TCO {improvement:+5.0f}만원 개선: {current_prob:.1%} → {new_prob:.1%} ({change:+.1%}p)")
        
        # 10. 기존 모델과 비교
        print("\n🔄 기존 모델 vs 실증 연구 기반 모델 비교:")
        
        def old_logistic(tco_diff):
            return 1 / (1 + np.exp(tco_diff / 1000))
        
        comparison_cases = [
            {'price': 5000, 'tco_diff': 1000, 'description': '중급차 1000만원 차이'},
            {'price': 10000, 'tco_diff': 1000, 'description': '고급차 1000만원 차이'}
        ]
        
        print("시나리오 | 기존모델 | 실증모델 | 차이")
        print("-" * 50)
        
        for case in comparison_cases:
            old_prob = old_logistic(case['tco_diff'])
            new_prob = calculate_empirical_bev_probability(case['tco_diff'], case['price'])
            difference = new_prob - old_prob
            
            print(f"{case['description']:15s} | {old_prob:.1%} | {new_prob:.1%} | {difference:+.1%}")
        
        # 11. 로지스틱 회귀 모델 (기존 방식)
        print("\n🤖 기계학습 모델 (로지스틱 회귀):")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        model = LogisticRegression(random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"모델 정확도: {accuracy:.2%}")
        
        # 특성 중요도
        feature_importance = pd.DataFrame({
            '특성': features,
            '계수': model.coef_[0],
            '중요도': np.abs(model.coef_[0])
        }).sort_values('중요도', ascending=False)
        
        print("\n특성별 영향도:")
        for _, row in feature_importance.iterrows():
            direction = "BEV 선호" if row['계수'] > 0 else "ICE 선호"
            print(f"  {row['특성']}: {row['계수']:.4f} ({direction})")
        
        # 12. 시각화
        self.plot_empirical_tco_simulation(tco_differences_range, bev_probabilities, current_diff, current_prob)
        
        return model, feature_importance, accuracy, (tco_differences_range, bev_probabilities)
    
    def plot_empirical_tco_simulation(self, tco_differences, bev_probabilities, current_diff, current_prob):
        """실증 연구 기반 TCO 변화에 따른 BEV 선택률 시뮬레이션 시각화"""
        plt.figure(figsize=(14, 10))
        
        # 메인 플롯
        plt.plot(tco_differences, bev_probabilities, linewidth=3, color='green', 
                label='BEV 선택 확률 (실증 연구 기반)')
        
        # 현재 상황 표시
        plt.axvline(x=current_diff, color='red', linestyle='--', linewidth=2, 
                   label=f'현재 상황 (차이: {current_diff:+.0f}만원, 선택률: {current_prob:.1%})')
        plt.axhline(y=0.5, color='gray', linestyle=':', alpha=0.7, label='50% 선택률 기준선')
        
        # 주요 지점 표시
        key_points = [-2000, -1000, -500, 0, 500, 1000, 2000]
        for point in key_points:
            idx = np.argmin(np.abs(tco_differences - point))
            prob = bev_probabilities[idx]
            plt.plot(point, prob, 'o', markersize=8, color='blue')
            plt.annotate(f'{prob:.1%}', (point, prob), 
                        xytext=(10, 10), textcoords='offset points', fontsize=9)
        
        # 정책 구간 표시
        plt.axvspan(-1000, 1000, alpha=0.2, color='yellow', label='정책 개입 가능 구간')
        
        plt.xlabel('TCO 차이 (BEV - ICE, 만원)', fontsize=12)
        plt.ylabel('BEV 선택 확률', fontsize=12)
        plt.title('실증 연구 기반 TCO 변화에 따른 BEV 선택률 시뮬레이션', 
                 fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=11, loc='upper left')
        
        # x축, y축 범위 설정
        plt.xlim(-3000, 3000)
        plt.ylim(0, 1)
        
        # 실증 연구 기반 정책 시사점 추가
        policy_text = f"""실증 연구 기반 정책 시사점:
• 현재 BEV 선택률: {current_prob:.1%}
• TCO 500만원 개선 시: {bev_probabilities[np.argmin(np.abs(tco_differences - (current_diff + 500)))]:.1%}
• TCO 1000만원 개선 시: {bev_probabilities[np.argmin(np.abs(tco_differences - (current_diff + 1000)))]:.1%}
• 차량가격 10% 변화당 25~30% 선택률 변화
• 전기차 가격 탄력성: -2.5 (실증 연구 기반)"""
        
        plt.figtext(0.02, 0.02, policy_text, fontsize=10, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('TCO_선택률_시뮬레이션_실증연구.png', dpi=300, bbox_inches='tight')
        print("✅ 실증 연구 기반 TCO 선택률 시뮬레이션 그래프가 'TCO_선택률_시뮬레이션_실증연구.png'로 저장되었습니다.")
        
        return plt.gcf()
    
    def create_visualizations(self):
        """분석 결과 시각화"""
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('TCO 분석 결과 (5년 소유기간 기준)', fontsize=16, fontweight='bold')
        
        # 1. 차량 유형별 총TCO 비교
        vehicle_tco = self.data.groupby('차량유형')['총TCO_만원'].mean()
        axes[0, 0].bar(vehicle_tco.index, vehicle_tco.values, color=['skyblue', 'lightgreen'])
        axes[0, 0].set_title('차량 유형별 평균 총TCO (5년)')
        axes[0, 0].set_ylabel('총TCO (만원)')
        for i, v in enumerate(vehicle_tco.values):
            axes[0, 0].text(i, v + 1000, f'{v:,.0f}만원', ha='center', fontweight='bold')
        
        # 2. 비용 구성요소 비교
        ice_data = self.data[self.data['차량유형'] == 'ICE']
        bev_data = self.data[self.data['차량유형'] == 'BEV']
        
        components = ['초기투자비용_만원', '총운영비_만원', '잔존가치_만원']
        comp_labels = ['초기투자', '5년운영비', '잔존가치']
        
        ice_values = [ice_data[comp].mean() for comp in components]
        bev_values = [bev_data[comp].mean() for comp in components]
        
        x = np.arange(len(comp_labels))
        width = 0.35
        
        axes[0, 1].bar(x - width/2, ice_values, width, label='ICE', color='skyblue')
        axes[0, 1].bar(x + width/2, bev_values, width, label='BEV', color='lightgreen')
        axes[0, 1].set_title('비용 구성요소 비교')
        axes[0, 1].set_ylabel('금액 (만원)')
        axes[0, 1].set_xticks(x)
        axes[0, 1].set_xticklabels(comp_labels)
        axes[0, 1].legend()
        
        # 3. 연도별 누적TCO
        yearly_pivot = self.yearly_data.pivot_table(
            values='누적TCO_만원', index='연도', columns='차량유형', aggfunc='mean'
        )
        
        for vehicle_type in yearly_pivot.columns:
            axes[1, 0].plot(yearly_pivot.index, yearly_pivot[vehicle_type], 
                           marker='o', linewidth=2, label=vehicle_type)
        
        axes[1, 0].set_title('연도별 누적TCO 추이')
        axes[1, 0].set_xlabel('소유년도')
        axes[1, 0].set_ylabel('누적TCO (만원)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 시나리오 비교 (지원 제거 전후)
        scenario_comparison = pd.DataFrame({
            '현재': [
                self.calculate_weighted_tco(self.scenario_data[self.scenario_data['차량유형'] == 'ICE'], '총TCO_만원'),
                self.calculate_weighted_tco(self.scenario_data[self.scenario_data['차량유형'] == 'BEV'], '총TCO_만원')
            ],
            '지원제거후': [
                self.calculate_weighted_tco(self.scenario_data[self.scenario_data['차량유형'] == 'ICE'], '조정후총TCO_만원'),
                self.calculate_weighted_tco(self.scenario_data[self.scenario_data['차량유형'] == 'BEV'], '총TCO_만원')
            ]
        }, index=['ICE', 'BEV'])
        
        scenario_comparison.plot(kind='bar', ax=axes[1, 1], color=['skyblue', 'orange'])
        axes[1, 1].set_title('시나리오 분석: ICE 지원 제거 영향')
        axes[1, 1].set_ylabel('총TCO (만원)')
        axes[1, 1].set_xlabel('차량 유형')
        axes[1, 1].legend()
        axes[1, 1].tick_params(axis='x', rotation=0)
        
        plt.tight_layout()
        plt.savefig('TCO_분석_결과.png', dpi=300, bbox_inches='tight')
        print("✅ 분석 결과 그래프가 'TCO_분석_결과.png'로 저장되었습니다.")
        
        return fig
    
    def generate_summary_report(self):
        """분석 결과 요약 보고서 생성"""
        ice_tco = self.calculate_weighted_tco(self.data[self.data['차량유형'] == 'ICE'], '총TCO_만원')
        bev_tco = self.calculate_weighted_tco(self.data[self.data['차량유형'] == 'BEV'], '총TCO_만원')
        
        report = f"""
# TCO 분석 결과 요약 보고서 (5년 소유기간 기준)

## 📊 주요 분석 결과

### 1. 차량 유형별 총소유비용 (5년)
- **ICE (내연기관)**: {ice_tco:,.0f}만원
- **BEV (전기차)**: {bev_tco:,.0f}만원
- **차이**: {bev_tco - ice_tco:+,.0f}만원 ({'BEV 불리' if bev_tco > ice_tco else 'BEV 유리'})

### 2. 연평균 소유비용
- **ICE**: {ice_tco/self.ownership_years:,.0f}만원/년
- **BEV**: {bev_tco/self.ownership_years:,.0f}만원/년

### 3. 비용 구성 분석
- **초기투자**: BEV가 ICE보다 높음 (보조금 반영 후)
- **운영비용**: BEV가 ICE보다 낮음 (연료비, 유지보수비 절약)
- **잔존가치**: ICE가 BEV보다 높음

### 4. 정책 시사점
1. **총소유비용 관점**: 5년 기준으로 현재는 {'ICE가 경제적' if ice_tco < bev_tco else 'BEV가 경제적'}
2. **지원정책 영향**: ICE 숨겨진 지원 제거 시 BEV 경쟁력 향상
3. **소비자 의사결정**: 총소유비용이 차량 선택에 중요한 영향

### 5. 권장사항
- 차량 분류별 맞춤형 정책 수립 필요
- 총소유비용 기준 정책 효과성 평가 중요
- 연도별 TCO 변화 지속 모니터링 필요

---
*분석 기준: {self.ownership_years}년 소유기간, 가중평균 적용*
        """
        
        return report
    
    def run_complete_analysis(self):
        """전체 분석 실행"""
        print("🚀 TCO 분석을 시작합니다... (5년 소유기간 기준)")
        
        # 데이터 로드
        if not self.load_data():
            return
        
        # 각종 분석 실행
        vehicle_analysis = self.analyze_by_vehicle_type()
        cost_analysis = self.analyze_cost_components()
        scenario_results = self.scenario_analysis()
        yearly_results = self.yearly_analysis()
        model, importance, accuracy, simulation_data = self.consumer_choice_model()
        
        # 시각화 생성
        self.create_visualizations()
        
        # 요약 보고서
        summary = self.generate_summary_report()
        print(summary)
        
        print("\n" + "="*60)
        print("🎉 TCO 분석이 완료되었습니다!")
        print("="*60)
        
        return {
            'vehicle_analysis': vehicle_analysis,
            'cost_analysis': cost_analysis,
            'scenario_results': scenario_results,
            'yearly_results': yearly_results,
            'model_accuracy': accuracy,
            'summary': summary,
            'simulation_data': simulation_data
        }

def main():
    """메인 실행 함수"""
    analyzer = ImprovedTCOAnalyzer()
    results = analyzer.run_complete_analysis()
    return results

if __name__ == "__main__":
    main() 