#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCO (Total Cost of Ownership) 분석 모델
ICE vs BEV 총소유비용 비교 및 소비자 선택 변화 분석
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['axes.unicode_minus'] = False

class TCOAnalyzer:
    """TCO 분석 클래스"""
    
    def __init__(self, excel_file='TCO_분석_입력템플릿.xlsx'):
        """초기화"""
        self.excel_file = excel_file
        self.df = None
        self.scenario_df = None
        self.results = {}
        
    def load_data(self):
        """데이터 로드"""
        try:
            self.df = pd.read_excel(self.excel_file, sheet_name='차량분류')
            self.scenario_df = pd.read_excel(self.excel_file, sheet_name='지원제거시나리오')
            print("✅ 데이터 로드 완료")
            print(f"   - 기본 데이터: {len(self.df)} 행")
            print(f"   - 시나리오 데이터: {len(self.scenario_df)} 행")
            return True
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def basic_analysis(self):
        """기본 TCO 분석"""
        if self.df is None:
            print("❌ 데이터가 로드되지 않았습니다.")
            return
        
        print("\n=== 기본 TCO 분석 ===")
        
        # ICE vs BEV 평균 TCO 비교
        tco_by_type = self.df.groupby('차량유형')['연간TCO_만원'].agg(['mean', 'std', 'count'])
        print("\n1. 차량유형별 평균 TCO:")
        print(tco_by_type)
        
        # 분류별 TCO 분석
        tco_by_category = self.df.groupby(['대분류', '중분류', '소분류', '차량유형'])['연간TCO_만원'].mean().unstack()
        print("\n2. 분류별 평균 TCO:")
        print(tco_by_category)
        
        # 비용 구성 요소 분석
        cost_components = ['구매비용_만원', '연료비_만원', '유지보수비_만원', 
                          '세금보험_만원', '감가상각_만원', '보조금_만원']
        
        ice_costs = self.df[self.df['차량유형'] == 'ICE'][cost_components].mean()
        bev_costs = self.df[self.df['차량유형'] == 'BEV'][cost_components].mean()
        
        cost_comparison = pd.DataFrame({
            'ICE_평균': ice_costs,
            'BEV_평균': bev_costs,
            'BEV-ICE_차이': bev_costs - ice_costs
        })
        
        print("\n3. 비용 구성요소 비교:")
        print(cost_comparison)
        
        self.results['basic_analysis'] = {
            'tco_by_type': tco_by_type,
            'tco_by_category': tco_by_category,
            'cost_comparison': cost_comparison
        }
    
    def scenario_analysis(self):
        """시나리오 분석 (ICE 지원 제거 후)"""
        if self.scenario_df is None:
            print("❌ 시나리오 데이터가 로드되지 않았습니다.")
            return
        
        print("\n=== 시나리오 분석 (ICE 지원 제거) ===")
        
        # 조정 전후 TCO 비교
        original_tco = self.scenario_df.groupby('차량유형')['연간TCO_만원'].mean()
        adjusted_tco = self.scenario_df.groupby('차량유형')['조정후TCO_만원'].mean()
        
        scenario_comparison = pd.DataFrame({
            '조정전_TCO': original_tco,
            '조정후_TCO': adjusted_tco,
            'TCO_변화': adjusted_tco - original_tco,
            '변화율_%': ((adjusted_tco - original_tco) / original_tco * 100).round(2)
        })
        
        print("\n1. 조정 전후 TCO 비교:")
        print(scenario_comparison)
        
        # ICE vs BEV 경쟁력 변화
        print("\n2. 경쟁력 변화:")
        ice_original = original_tco['ICE']
        bev_original = original_tco['BEV'] 
        ice_adjusted = adjusted_tco['ICE']
        bev_adjusted = adjusted_tco['BEV']
        
        print(f"   조정 전: ICE {ice_original:.0f}만원 vs BEV {bev_original:.0f}만원 (차이: {bev_original-ice_original:.0f}만원)")
        print(f"   조정 후: ICE {ice_adjusted:.0f}만원 vs BEV {bev_adjusted:.0f}만원 (차이: {bev_adjusted-ice_adjusted:.0f}만원)")
        
        competitiveness_change = (bev_adjusted-ice_adjusted) - (bev_original-ice_original)
        print(f"   BEV 경쟁력 개선: {-competitiveness_change:.0f}만원")
        
        self.results['scenario_analysis'] = {
            'scenario_comparison': scenario_comparison,
            'competitiveness_change': competitiveness_change
        }
    
    def choice_model_analysis(self):
        """소비자 선택 모델 분석"""
        if self.scenario_df is None:
            return
        
        print("\n=== 소비자 선택 모델 분석 ===")
        
        # 특성 변수 생성
        self.scenario_df['tco_difference'] = self.scenario_df.apply(
            lambda x: x['조정후TCO_만원'] if x['차량유형'] == 'BEV' else -x['조정후TCO_만원'], axis=1
        )
        
        # 더미 변수 생성
        category_dummies = pd.get_dummies(self.scenario_df[['대분류', '중분류', '소분류']], prefix=['대분류', '중분류', '소분류'])
        
        # 특성 매트릭스 생성
        X = pd.concat([
            self.scenario_df[['조정후TCO_만원', '구매비용_만원', '연료비_만원']],
            category_dummies
        ], axis=1)
        
        # 타겟 변수 (BEV 선택 여부)
        y = (self.scenario_df['차량유형'] == 'BEV').astype(int)
        
        # 로지스틱 회귀 모델
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_train, y_train)
        
        # 예측
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        print("1. 모델 성능:")
        print(classification_report(y_test, y_pred))
        
        # 특성 중요도
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'coefficient': model.coef_[0],
            'abs_coefficient': np.abs(model.coef_[0])
        }).sort_values('abs_coefficient', ascending=False)
        
        print("\n2. 특성 중요도 (상위 10개):")
        print(feature_importance.head(10))
        
        # TCO 변화에 따른 BEV 선택 확률 시뮬레이션
        tco_range = np.linspace(-2000, 2000, 100)  # TCO 차이 범위
        base_features = X_train.mean().values.reshape(1, -1)
        
        bev_probabilities = []
        for tco_diff in tco_range:
            features = base_features.copy()
            features[0, 0] = 5000 + tco_diff  # 조정후TCO_만원
            prob = model.predict_proba(features)[0, 1]
            bev_probabilities.append(prob)
        
        self.results['choice_model'] = {
            'model': model,
            'feature_importance': feature_importance,
            'tco_range': tco_range,
            'bev_probabilities': bev_probabilities
        }
    
    def visualize_results(self):
        """결과 시각화"""
        if not self.results:
            print("❌ 분석 결과가 없습니다.")
            return
        
        print("\n=== 결과 시각화 ===")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('TCO 분석 결과', fontsize=16, fontweight='bold')
        
        # 1. 차량유형별 TCO 비교
        if 'basic_analysis' in self.results:
            tco_data = self.results['basic_analysis']['tco_by_type']
            ax1 = axes[0, 0]
            tco_data['mean'].plot(kind='bar', ax=ax1, color=['skyblue', 'lightgreen'])
            ax1.set_title('차량유형별 평균 TCO')
            ax1.set_ylabel('TCO (만원)')
            ax1.tick_params(axis='x', rotation=0)
        
        # 2. 비용 구성요소 비교
        if 'basic_analysis' in self.results:
            cost_data = self.results['basic_analysis']['cost_comparison']
            ax2 = axes[0, 1]
            cost_data[['ICE_평균', 'BEV_평균']].plot(kind='bar', ax=ax2)
            ax2.set_title('비용 구성요소 비교')
            ax2.set_ylabel('비용 (만원)')
            ax2.tick_params(axis='x', rotation=45)
            ax2.legend()
        
        # 3. 시나리오 분석 결과
        if 'scenario_analysis' in self.results:
            scenario_data = self.results['scenario_analysis']['scenario_comparison']
            ax3 = axes[1, 0]
            scenario_data[['조정전_TCO', '조정후_TCO']].plot(kind='bar', ax=ax3)
            ax3.set_title('시나리오 분석: 조정 전후 TCO')
            ax3.set_ylabel('TCO (만원)')
            ax3.tick_params(axis='x', rotation=0)
            ax3.legend()
        
        # 4. BEV 선택 확률
        if 'choice_model' in self.results:
            choice_data = self.results['choice_model']
            ax4 = axes[1, 1]
            ax4.plot(choice_data['tco_range'], choice_data['bev_probabilities'], 
                    linewidth=2, color='green')
            ax4.set_title('TCO 차이에 따른 BEV 선택 확률')
            ax4.set_xlabel('TCO 차이 (만원)')
            ax4.set_ylabel('BEV 선택 확률')
            ax4.grid(True, alpha=0.3)
            ax4.axhline(y=0.5, color='red', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig('TCO_분석_결과.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ 시각화 완료 (TCO_분석_결과.png 저장)")
    
    def generate_report(self):
        """분석 리포트 생성"""
        if not self.results:
            print("❌ 분석 결과가 없습니다.")
            return
        
        print("\n" + "="*50)
        print("           TCO 분석 리포트")
        print("="*50)
        
        # 주요 발견사항
        if 'basic_analysis' in self.results:
            tco_data = self.results['basic_analysis']['tco_by_type']
            ice_tco = tco_data.loc['ICE', 'mean']
            bev_tco = tco_data.loc['BEV', 'mean']
            
            print(f"\n📊 현재 상황:")
            print(f"   • ICE 평균 TCO: {ice_tco:.0f}만원")
            print(f"   • BEV 평균 TCO: {bev_tco:.0f}만원")
            print(f"   • BEV가 ICE보다 {bev_tco-ice_tco:.0f}만원 {'비쌈' if bev_tco > ice_tco else '저렴'}")
        
        if 'scenario_analysis' in self.results:
            scenario_data = self.results['scenario_analysis']['scenario_comparison']
            competitiveness = self.results['scenario_analysis']['competitiveness_change']
            
            print(f"\n🔄 ICE 지원 제거 시:")
            print(f"   • ICE TCO 증가: {scenario_data.loc['ICE', 'TCO_변화']:.0f}만원")
            print(f"   • BEV 경쟁력 개선: {-competitiveness:.0f}만원")
        
        if 'choice_model' in self.results:
            feature_importance = self.results['choice_model']['feature_importance']
            top_feature = feature_importance.iloc[0]
            
            print(f"\n🎯 소비자 선택 요인:")
            print(f"   • 가장 중요한 요인: {top_feature['feature']}")
            print(f"   • 계수: {top_feature['coefficient']:.3f}")
        
        print(f"\n💡 정책 시사점:")
        print(f"   • ICE에 대한 직간접 지원 제거 시 BEV 경쟁력 크게 향상")
        print(f"   • 총소유비용이 소비자 선택에 핵심적 영향")
        print(f"   • 차량 분류별 맞춤형 정책 필요")
        
        print("\n" + "="*50)
    
    def run_full_analysis(self):
        """전체 분석 실행"""
        print("🚀 TCO 분석 시작...")
        
        if not self.load_data():
            return
        
        self.basic_analysis()
        self.scenario_analysis() 
        self.choice_model_analysis()
        self.visualize_results()
        self.generate_report()
        
        print("\n✅ TCO 분석 완료!")

def main():
    """메인 함수"""
    # TCO 분석기 생성 및 실행
    analyzer = TCOAnalyzer()
    analyzer.run_full_analysis()

if __name__ == "__main__":
    main() 