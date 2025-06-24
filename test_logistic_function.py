#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로지스틱 함수 작동 원리 테스트
NREL 연구 기반 TCO 효과 분석
"""

import numpy as np
import matplotlib.pyplot as plt

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

def test_logistic_function():
    """로지스틱 함수 테스트"""
    
    print("="*60)
    print("📊 로지스틱 함수 작동 원리 분석")
    print("="*60)
    
    # 현재 구현된 로지스틱 함수
    def current_logistic(tco_diff):
        return 1 / (1 + np.exp(tco_diff / 1000))
    
    # 기본 로지스틱 함수 (비교용)
    def basic_logistic(x):
        return 1 / (1 + np.exp(-x))
    
    # TCO 차이 테스트
    tco_differences = [-2000, -1000, -500, 0, 500, 1000, 2000]
    
    print("\n현재 구현된 로지스틱 함수 결과:")
    print("TCO 차이 (BEV-ICE) | 로지스틱 값 | 해석")
    print("-" * 50)
    
    for diff in tco_differences:
        logistic_value = current_logistic(diff)
        interpretation = "BEV 매우 유리" if logistic_value > 0.8 else \
                        "BEV 유리" if logistic_value > 0.6 else \
                        "BEV 약간 유리" if logistic_value > 0.5 else \
                        "ICE 약간 유리" if logistic_value > 0.4 else \
                        "ICE 유리" if logistic_value > 0.2 else "ICE 매우 유리"
        
        print(f"{diff:+6.0f}만원        | {logistic_value:.3f}     | {interpretation}")
    
    # 변화율 계산
    print("\n📈 TCO 차이별 변화율 분석:")
    print("TCO 차이 변화 | 확률 변화 | 변화율")
    print("-" * 40)
    
    # -1000에서 0으로 변화
    prob_neg1000 = current_logistic(-1000)
    prob_0 = current_logistic(0)
    change_neg1000_to_0 = prob_0 - prob_neg1000
    
    # 0에서 +1000으로 변화
    prob_plus1000 = current_logistic(1000)
    change_0_to_plus1000 = prob_plus1000 - prob_0
    
    print(f"-1000 → 0만원    | {change_neg1000_to_0:+.3f}    | {change_neg1000_to_0*100:+.1f}%p")
    print(f"0 → +1000만원    | {change_0_to_plus1000:+.3f}    | {change_0_to_plus1000*100:+.1f}%p")
    
    # 1000달러당 변화율 (NREL 연구와 비교)
    print(f"\n🔍 NREL 연구 비교:")
    print(f"현재 모델: 1000만원 차이당 약 {abs(change_0_to_plus1000)*100:.1f}%p 변화")
    print(f"NREL 연구: 1000달러 차이당 2-3%p 변화")
    
    # 시각화
    tco_range = np.linspace(-3000, 3000, 100)
    logistic_values = [current_logistic(diff) for diff in tco_range]
    
    plt.figure(figsize=(12, 8))
    plt.plot(tco_range, logistic_values, linewidth=3, color='blue', label='Current Logistic Function')
    
    # 주요 지점 표시
    key_points = [-2000, -1000, -500, 0, 500, 1000, 2000]
    for point in key_points:
        prob = current_logistic(point)
        plt.plot(point, prob, 'ro', markersize=8)
        plt.annotate(f'{prob:.3f}', (point, prob), 
                    xytext=(10, 10), textcoords='offset points', fontsize=10)
    
    plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.7, label='50% Baseline')
    plt.axvline(x=0, color='gray', linestyle=':', alpha=0.7, label='TCO Equal Line')
    
    plt.xlabel('TCO Difference (BEV - ICE, 10K KRW)', fontsize=12)
    plt.ylabel('Logistic Value (TCO Effect)', fontsize=12)
    plt.title('Logistic Function Operation Principle', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # 분석 결과 추가
    analysis_text = f"""Analysis Results:
• TCO -1000: {current_logistic(-1000):.3f} (BEV Favorable)
• TCO 0: {current_logistic(0):.3f} (Equal)
• TCO +1000: {current_logistic(1000):.3f} (ICE Favorable)
• Change per 1000: {abs(change_0_to_plus1000)*100:.1f}%p"""
    
    plt.figtext(0.02, 0.02, analysis_text, fontsize=10, 
               bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('logistic_function_analysis.png', dpi=300, bbox_inches='tight')
    print("\n✅ 로지스틱 함수 분석 그래프가 'logistic_function_analysis.png'로 저장되었습니다.")
    
    return current_logistic

def analyze_vehicle_price_impact():
    """차량 가격에 따른 상대적 TCO 영향 분석"""
    
    print("\n" + "="*60)
    print("🚗 차량 가격에 따른 상대적 TCO 영향 분석")
    print("="*60)
    
    # 차량 가격별 시나리오
    vehicle_scenarios = [
        {'name': '경제형', 'price': 2000, 'description': '2000만원 차량'},
        {'name': '중급형', 'price': 5000, 'description': '5000만원 차량'},
        {'name': '고급형', 'price': 10000, 'description': '1억원 차량'},
        {'name': '럭셔리형', 'price': 20000, 'description': '2억원 차량'}
    ]
    
    print("\n📊 차량 가격별 TCO 차이의 상대적 영향:")
    print("차량 유형 | 구매가격 | TCO 차이 | 상대적 영향 | 해석")
    print("-" * 70)
    
    tco_differences = [-1000, 0, 1000]  # 테스트할 TCO 차이
    
    for scenario in vehicle_scenarios:
        price = scenario['price']
        name = scenario['name']
        description = scenario['description']
        
        for tco_diff in tco_differences:
            # 상대적 영향 (TCO 차이 / 차량 가격)
            relative_impact = tco_diff / price * 100  # 백분율로 표현
            
            # 해석
            if relative_impact < -10:
                impact_desc = "BEV 매우 유리"
            elif relative_impact < -5:
                impact_desc = "BEV 유리"
            elif relative_impact < 0:
                impact_desc = "BEV 약간 유리"
            elif relative_impact < 5:
                impact_desc = "ICE 약간 유리"
            elif relative_impact < 10:
                impact_desc = "ICE 유리"
            else:
                impact_desc = "ICE 매우 유리"
            
            print(f"{name:8s} | {price:6.0f}만원 | {tco_diff:+5.0f}만원 | {relative_impact:+6.1f}% | {impact_desc}")
    
    # 개선된 로지스틱 함수 제안
    print("\n🔧 개선된 로지스틱 함수 제안:")
    print("기존: f(tco_diff) = 1 / (1 + exp(tco_diff / 1000))")
    print("개선: f(tco_diff, price) = 1 / (1 + exp(tco_diff / (price * 0.1)))")
    print("→ 차량 가격의 10%를 기준으로 상대적 영향 계산")
    
    return vehicle_scenarios

def improved_logistic_function():
    """개선된 로지스틱 함수 (차량 가격 고려)"""
    
    print("\n" + "="*60)
    print("🔧 개선된 로지스틱 함수 테스트")
    print("="*60)
    
    def improved_logistic(tco_diff, vehicle_price, sensitivity_factor=0.1):
        """
        개선된 로지스틱 함수
        - tco_diff: TCO 차이 (BEV - ICE)
        - vehicle_price: 차량 구매 가격
        - sensitivity_factor: 민감도 계수 (기본값: 0.1 = 차량 가격의 10%)
        """
        # 차량 가격의 일정 비율을 기준으로 상대적 영향 계산
        price_threshold = vehicle_price * sensitivity_factor
        return 1 / (1 + np.exp(tco_diff / price_threshold))
    
    # 차량 가격별 테스트
    vehicle_prices = [2000, 5000, 10000, 20000]  # 만원 단위
    tco_differences = [-2000, -1000, -500, 0, 500, 1000, 2000]
    
    print("\n개선된 로지스틱 함수 결과 (차량 가격별):")
    print("차량가격 | TCO차이 | 상대적임계값 | 로지스틱값 | 해석")
    print("-" * 65)
    
    for price in vehicle_prices:
        threshold = price * 0.1  # 차량 가격의 10%
        print(f"\n{price:6.0f}만원 차량 (임계값: {threshold:.0f}만원):")
        
        for diff in tco_differences:
            prob = improved_logistic(diff, price)
            relative_threshold = diff / threshold
            
            interpretation = "BEV 매우 유리" if prob > 0.8 else \
                            "BEV 유리" if prob > 0.6 else \
                            "BEV 약간 유리" if prob > 0.5 else \
                            "ICE 약간 유리" if prob > 0.4 else \
                            "ICE 유리" if prob > 0.2 else "ICE 매우 유리"
            
            print(f"         | {diff:+5.0f}만원 | {relative_threshold:+6.1f}배 | {prob:.3f}     | {interpretation}")
    
    # 시각화
    plt.figure(figsize=(15, 10))
    
    colors = ['blue', 'green', 'orange', 'red']
    for i, price in enumerate(vehicle_prices):
        tco_range = np.linspace(-3000, 3000, 100)
        logistic_values = [improved_logistic(diff, price) for diff in tco_range]
        
        plt.plot(tco_range, logistic_values, linewidth=2, color=colors[i], 
                label=f'{price:,.0f}만원 차량 (임계값: {price*0.1:.0f}만원)')
    
    plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.7, label='50% Baseline')
    plt.axvline(x=0, color='gray', linestyle=':', alpha=0.7, label='TCO Equal Line')
    
    plt.xlabel('TCO Difference (BEV - ICE, 10K KRW)', fontsize=12)
    plt.ylabel('Improved Logistic Value', fontsize=12)
    plt.title('Improved Logistic Function: Vehicle Price Consideration', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # 분석 결과 추가
    analysis_text = """Improved Model Features:
• Vehicle price-dependent sensitivity
• Relative TCO impact consideration
• More realistic consumer behavior modeling
• Price threshold = 10% of vehicle price"""
    
    plt.figtext(0.02, 0.02, analysis_text, fontsize=10, 
               bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('improved_logistic_function.png', dpi=300, bbox_inches='tight')
    print("\n✅ 개선된 로지스틱 함수 그래프가 'improved_logistic_function.png'로 저장되었습니다.")
    
    return improved_logistic

def analyze_nrel_comparison():
    """NREL 연구와의 비교 분석"""
    
    print("\n" + "="*60)
    print("🔬 NREL 연구와의 비교 분석")
    print("="*60)
    
    # NREL 연구 결과 (가정)
    nrel_change_per_1000 = 0.025  # 1000달러당 2.5%p 변화
    
    # 현재 모델 결과
    def current_logistic(tco_diff):
        return 1 / (1 + np.exp(tco_diff / 1000))
    
    current_change = abs(current_logistic(1000) - current_logistic(0))
    
    print(f"NREL 연구: 1000달러당 {nrel_change_per_1000*100:.1f}%p 변화")
    print(f"현재 모델: 1000만원당 {current_change*100:.1f}%p 변화")
    
    # 환율 고려 (1달러 = 약 1300원)
    usd_to_krw = 1300
    nrel_change_per_krw = nrel_change_per_1000 / (1000 * usd_to_krw / 1000000)  # 100만원당 변화
    
    print(f"\n환율 고려 시:")
    print(f"NREL 연구: 100만원당 {nrel_change_per_krw*100:.1f}%p 변화")
    print(f"현재 모델: 100만원당 {current_change*100:.1f}%p 변화")
    
    # 조정 계수 계산
    adjustment_factor = nrel_change_per_krw / current_change
    print(f"\n조정 계수: {adjustment_factor:.3f}")
    
    # 조정된 로지스틱 함수
    def adjusted_logistic(tco_diff):
        return 1 / (1 + np.exp(tco_diff / (1000 * adjustment_factor)))
    
    adjusted_change = abs(adjusted_logistic(1000) - adjusted_logistic(0))
    print(f"조정 후: 1000만원당 {adjusted_change*100:.1f}%p 변화")
    
    return adjusted_logistic

def explain_logistic_mechanism():
    """로지스틱 메커니즘 상세 설명"""
    
    print("\n" + "="*60)
    print("🔍 로지스틱 함수 메커니즘 상세 설명")
    print("="*60)
    
    print("\n1. 기본 로지스틱 함수:")
    print("   f(x) = 1 / (1 + e^(-x))")
    print("   - x가 증가하면 f(x)가 증가 (0 → 1)")
    print("   - S자 곡선 형태")
    
    print("\n2. 현재 구현된 함수:")
    print("   f(tco_diff) = 1 / (1 + e^(tco_diff / 1000))")
    print("   - tco_diff가 증가하면 f(tco_diff)가 감소 (1 → 0)")
    print("   - BEV가 비쌀수록 선택 확률이 감소")
    
    print("\n3. 핵심 포인트:")
    print("   ✅ 기본 로지스틱 곡선이 존재")
    print("   ✅ TCO 차이에 따라 곡선 위의 점이 이동")
    print("   ✅ 1000만원 단위로 변화율이 결정됨")
    
    print("\n4. NREL 연구와의 차이:")
    print("   ❌ 현재 모델: 1000만원당 23.1%p 변화")
    print("   ✅ NREL 연구: 1000달러당 2-3%p 변화")
    print("   ⚠️  약 8-10배 차이 (환율 고려 시에도 큰 차이)")
    
    print("\n5. 문제점:")
    print("   - NREL 연구의 구체적인 수치 확인 필요")
    print("   - 현재 모델이 너무 민감하게 반응")
    print("   - 실제 소비자 행동과의 차이 가능성")

def explain_1000_basis():
    """1000만원 기준의 결정 근거 분석"""
    
    print("\n" + "="*60)
    print("🔍 1000만원 기준의 결정 근거 분석")
    print("="*60)
    
    print("\n❌ 현재 1000만원 기준의 문제점:")
    print("1. 임의로 설정된 값 (코드에서 확인됨)")
    print("2. 차량 가격에 따른 상대적 영향 무시")
    print("3. NREL 연구와 8-10배 차이")
    print("4. 실제 소비자 행동과 불일치 가능성")
    
    print("\n📊 차량 가격별 상대적 영향 예시:")
    print("차량 가격 | 1000만원 차이의 상대적 영향")
    print("-" * 45)
    
    prices = [2000, 5000, 10000, 20000]
    for price in prices:
        relative_impact = 1000 / price * 100
        print(f"{price:6.0f}만원 | {relative_impact:5.1f}% (차량 가격 대비)")
    
    print("\n💡 개선 방향:")
    print("1. 차량 가격의 일정 비율을 기준으로 설정")
    print("2. 상대적 TCO 영향 고려")
    print("3. NREL 연구 결과와의 일치성 확보")
    print("4. 실제 소비자 행동 데이터 기반 검증")

if __name__ == "__main__":
    # 기본 로지스틱 함수 테스트
    current_func = test_logistic_function()
    
    # 차량 가격 영향 분석
    vehicle_scenarios = analyze_vehicle_price_impact()
    
    # 개선된 로지스틱 함수 테스트
    improved_func = improved_logistic_function()
    
    # NREL 연구와의 비교
    adjusted_func = analyze_nrel_comparison()
    
    # 로지스틱 메커니즘 상세 설명
    explain_logistic_mechanism()
    
    # 1000만원 기준 분석
    explain_1000_basis()
    
    print("\n" + "="*60)
    print("📋 결론:")
    print("="*60)
    print("1. 현재 로지스틱 함수는 TCO 차이에 따른 BEV 선택 확률을 계산")
    print("2. TCO 차이가 증가할수록 BEV 선택 확률이 감소하는 형태")
    print("3. NREL 연구의 2-3% 변화와 비교하여 조정 필요")
    print("4. 기본 로지스틱 곡선 위에서 TCO 변화에 따른 이동 발생")
    print("5. NREL 연구의 정확한 수치 확인이 필요함")
    print("6. ⚠️ 1000만원 기준은 임의 설정된 값으로 개선 필요")
    print("7. 🚗 차량 가격에 따른 상대적 영향 고려 필요")
    print("8. 🔧 개선된 모델: 차량 가격의 10%를 임계값으로 사용") 