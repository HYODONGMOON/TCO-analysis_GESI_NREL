#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BEV Selection Probability Calculation Explanation
실증 연구 기반 BEV 선택 확률 계산 과정 상세 분석
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def explain_bev_probability_calculation():
    """BEV 선택 확률 계산 과정을 자세히 설명"""
    
    print("="*80)
    print("🔍 BEV Selection Probability Calculation Explanation")
    print("="*80)
    
    # 실증 연구 기반 매개변수 (PDF 3페이지 기준)
    empirical_parameters = {
        'ev_price_elasticity': -2.5,
        'base_preference': 0.175,  # 17.5% 기본 선호도
        'market_share_effect': 0.15  # 15% 시장 점유율 효과
    }
    
    print(f"📊 Empirical Research Parameters:")
    print(f"   • EV Price Elasticity: {empirical_parameters['ev_price_elasticity']}")
    print(f"   • Base Preference: {empirical_parameters['base_preference']:.1%}")
    print(f"   • Market Share Effect: {empirical_parameters['market_share_effect']:.1%}")
    
    # CASPER vs CASPER EV 사례 분석
    print(f"\n🚗 CASPER vs CASPER EV Detailed Analysis:")
    
    # CASPER 데이터
    casper_ice_tco = 3020  # 만원
    casper_bev_tco = 2951  # 만원
    casper_ice_price = 1700  # 만원
    casper_bev_price = 2280  # 만원
    
    tco_diff = casper_bev_tco - casper_ice_tco  # -69만원 (BEV가 저렴)
    avg_price = (casper_ice_price + casper_bev_price) / 2  # 1990만원
    current_market_share = 0.05  # 5% (현재 BEV 시장 점유율)
    
    print(f"   • ICE TCO: {casper_ice_tco:,} KRW")
    print(f"   • BEV TCO: {casper_bev_tco:,} KRW")
    print(f"   • TCO Difference: {tco_diff:+,} KRW (BEV {'cheaper' if tco_diff < 0 else 'more expensive'})")
    print(f"   • Average Price: {avg_price:,} KRW")
    print(f"   • Current BEV Market Share: {current_market_share:.1%}")
    
    # 각 구성요소 계산
    print(f"\n🧮 Probability Calculation Components:")
    
    # 1. 기본 선호도 (Base Preference)
    base_effect = empirical_parameters['base_preference']
    print(f"   1. Base Preference: {base_effect:.1%}")
    print(f"      → 소비자들이 BEV에 대해 가지고 있는 기본적인 선호도")
    print(f"      → 환경 친화성, 신기술 선호, 정부 정책 등 TCO 외 요인")
    
    # 2. TCO 효과 (TCO Effect)
    relative_tco_impact = tco_diff / avg_price
    tco_effect = (empirical_parameters['ev_price_elasticity'] * 
                 relative_tco_impact * 
                 current_market_share * 
                 (1 - current_market_share))
    
    print(f"   2. TCO Effect: {tco_effect:.1%}")
    print(f"      → Relative TCO Impact: {relative_tco_impact:.1%}")
    print(f"      → Formula: {empirical_parameters['ev_price_elasticity']} × {relative_tco_impact:.3f} × {current_market_share} × {1-current_market_share}")
    print(f"      → TCO 차이가 가격 대비 얼마나 중요한지 반영")
    
    # 3. 시장 점유율 효과 (Market Share Effect)
    market_share_effect = empirical_parameters['market_share_effect'] * (1 - current_market_share)
    print(f"   3. Market Share Effect: {market_share_effect:.1%}")
    print(f"      → Formula: {empirical_parameters['market_share_effect']} × {1-current_market_share}")
    print(f"      → 현재 BEV 시장 점유율이 낮을수록 성장 잠재력이 높음")
    
    # 4. 최종 확률
    total_probability = base_effect + tco_effect + market_share_effect
    print(f"\n📈 Final BEV Selection Probability:")
    print(f"   = {base_effect:.1%} + {tco_effect:.1%} + {market_share_effect:.1%}")
    print(f"   = {total_probability:.1%}")
    
    print(f"\n💡 Why not 50% even though BEV TCO is lower?")
    print(f"   1. Base Preference (17.5%): 기본적으로 BEV를 선호하는 소비자 비율")
    print(f"   2. TCO Effect ({tco_effect:.1%}): TCO 차이로 인한 추가 선택")
    print(f"   3. Market Share Effect ({market_share_effect:.1%}): 시장 점유율 성장 잠재력")
    print(f"   4. Other Factors: 충전 인프라, 주행거리, 충전 시간 등 TCO 외 요인들")
    
    # 다른 시나리오와 비교
    print(f"\n🔄 Comparison with Different Scenarios:")
    
    scenarios = [
        ("Current (BEV cheaper by 69 KRW)", -69, 1990),
        ("Same TCO", 0, 1990),
        ("BEV more expensive by 500 KRW", 500, 1990),
        ("BEV more expensive by 1000 KRW", 1000, 1990)
    ]
    
    for scenario_name, tco_diff_scenario, avg_price_scenario in scenarios:
        relative_impact = tco_diff_scenario / avg_price_scenario
        tco_effect_scenario = (empirical_parameters['ev_price_elasticity'] * 
                              relative_impact * 
                              current_market_share * 
                              (1 - current_market_share))
        total_prob_scenario = base_effect + tco_effect_scenario + market_share_effect
        
        print(f"   • {scenario_name}: {total_prob_scenario:.1%}")
    
    # 시각화
    create_probability_visualization()
    
    return total_probability

def create_probability_visualization():
    """확률 계산 과정을 시각화"""
    
    # TCO 차이에 따른 BEV 선택 확률 변화
    tco_differences = np.linspace(-1000, 1000, 100)  # -1000만원 ~ +1000만원
    avg_price = 1990  # 만원
    current_market_share = 0.05
    
    empirical_parameters = {
        'ev_price_elasticity': -2.5,
        'base_preference': 0.175,
        'market_share_effect': 0.15
    }
    
    probabilities = []
    for tco_diff in tco_differences:
        relative_impact = tco_diff / avg_price
        tco_effect = (empirical_parameters['ev_price_elasticity'] * 
                     relative_impact * 
                     current_market_share * 
                     (1 - current_market_share))
        total_prob = empirical_parameters['base_preference'] + tco_effect + empirical_parameters['market_share_effect'] * (1 - current_market_share)
        probabilities.append(np.clip(total_prob, 0, 1))
    
    plt.figure(figsize=(12, 8))
    
    # 1. TCO 차이별 BEV 선택 확률
    plt.subplot(2, 2, 1)
    plt.plot(tco_differences, probabilities, 'b-', linewidth=2)
    plt.axvline(x=-69, color='red', linestyle='--', alpha=0.7, label='CASPER EV (-69 KRW)')
    plt.axhline(y=0.5, color='green', linestyle='--', alpha=0.7, label='50% Baseline')
    plt.xlabel('TCO Difference (BEV - ICE, KRW)')
    plt.ylabel('BEV Selection Probability')
    plt.title('BEV Selection Probability vs TCO Difference')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 2. 구성요소 분해
    plt.subplot(2, 2, 2)
    components = ['Base\nPreference', 'TCO\nEffect', 'Market Share\nEffect']
    values = [0.175, -0.004, 0.143]  # CASPER EV 사례
    colors = ['lightblue', 'lightgreen', 'lightcoral']
    
    bars = plt.bar(components, values, color=colors, alpha=0.7)
    plt.ylabel('Contribution to Probability')
    plt.title('Probability Components (CASPER EV)')
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # 값 표시
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005, 
                f'{value:.3f}', ha='center', va='bottom')
    
    # 3. 시장 점유율에 따른 변화
    plt.subplot(2, 2, 3)
    market_shares = np.linspace(0.01, 0.3, 50)
    tco_diff = -69  # CASPER EV 사례
    
    market_probabilities = []
    for ms in market_shares:
        relative_impact = tco_diff / 1990
        tco_effect = (-2.5 * relative_impact * ms * (1 - ms))
        total_prob = 0.175 + tco_effect + 0.15 * (1 - ms)
        market_probabilities.append(np.clip(total_prob, 0, 1))
    
    plt.plot(market_shares * 100, market_probabilities, 'purple', linewidth=2)
    plt.axvline(x=5, color='red', linestyle='--', alpha=0.7, label='Current (5%)')
    plt.xlabel('Current BEV Market Share (%)')
    plt.ylabel('BEV Selection Probability')
    plt.title('Probability vs Market Share')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 4. 가격 탄력성에 따른 변화
    plt.subplot(2, 2, 4)
    elasticities = np.linspace(-5, 0, 50)
    tco_diff = -69  # CASPER EV 사례
    
    elasticity_probabilities = []
    for elasticity in elasticities:
        relative_impact = tco_diff / 1990
        tco_effect = (elasticity * relative_impact * 0.05 * 0.95)
        total_prob = 0.175 + tco_effect + 0.143
        elasticity_probabilities.append(np.clip(total_prob, 0, 1))
    
    plt.plot(elasticities, elasticity_probabilities, 'orange', linewidth=2)
    plt.axvline(x=-2.5, color='red', linestyle='--', alpha=0.7, label='Empirical (-2.5)')
    plt.xlabel('EV Price Elasticity')
    plt.ylabel('BEV Selection Probability')
    plt.title('Probability vs Price Elasticity')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('BEV_Probability_Explanation.png', dpi=300, bbox_inches='tight')
    print("✅ BEV probability explanation visualization saved as 'BEV_Probability_Explanation.png'")
    
    return plt.gcf()

if __name__ == "__main__":
    probability = explain_bev_probability_calculation()
    print(f"\n🎯 Key Insight: BEV Selection Probability = {probability:.1%}")
    print("   This means 32% of consumers are expected to choose BEV")
    print("   even though BEV has lower TCO, due to various factors beyond TCO.") 