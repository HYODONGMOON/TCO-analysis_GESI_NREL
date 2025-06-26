#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCO 분석 실행 스크립트
5년 소유기간 기준 올바른 TCO 계산 적용
기존 사용자 입력 데이터 보존 기능
"""

import os
import sys
from create_tco_template import create_tco_template
from tco_analysis import ImprovedTCOAnalyzer

def main():
    """TCO 분석 전체 실행"""
    
    print("🚀 TCO 분석 시스템을 시작합니다!")
    print("=" * 60)
    print("📋 5년 소유기간 기준 올바른 TCO 계산이 적용됩니다")
    print("🔒 기존 사용자 입력 데이터는 자동으로 보존됩니다")
    print("=" * 60)
    
    # 1. Excel 템플릿 파일 확인 및 생성
    template_file = 'TCO_분석_입력템플릿.xlsx'
    
    if os.path.exists(template_file):
        print(f"\n✅ 기존 템플릿 파일을 발견했습니다: {template_file}")
        
        # 기존 데이터 확인
        try:
            import pandas as pd
            existing_df = pd.read_excel(template_file, sheet_name='차량분류')
            print(f"📊 기존 데이터: {len(existing_df)}개 차량 분류 조합")
            
            # 사용자 입력 데이터인지 확인 (랜덤값이 아닌 실제 데이터인지)
            sample_data = existing_df[['구매비용_만원', '차량대수']].head(3)
            print("📋 데이터 샘플:")
            print(sample_data)
            
        except Exception as e:
            print(f"⚠️  기존 데이터 확인 중 오류: {e}")
        
        while True:
            choice = input("\n새로운 템플릿을 생성하시겠습니까? (y/n): ").lower().strip()
            if choice in ['y', 'yes', '예']:
                print("\n📝 새로운 템플릿을 생성합니다...")
                print("⚠️  기존 사용자 입력 데이터는 백업으로 보존됩니다.")
                try:
                    create_tco_template()
                    print("✅ 새로운 템플릿이 생성되었습니다.")
                except Exception as e:
                    print(f"❌ 템플릿 생성 중 오류 발생: {e}")
                    return
                break
            elif choice in ['n', 'no', '아니오']:
                print("\n📂 기존 템플릿을 사용합니다.")
                break
            else:
                print("❌ 잘못된 입력입니다. 'y' 또는 'n'을 입력해주세요.")
    else:
        print(f"\n📝 템플릿 파일이 없습니다. 새로 생성합니다...")
        try:
            create_tco_template()
            print("✅ 템플릿이 성공적으로 생성되었습니다.")
        except Exception as e:
            print(f"❌ 템플릿 생성 중 오류 발생: {e}")
            return
    
    # 2. TCO 분석 실행
    print("\n" + "=" * 60)
    print("📊 TCO 분석을 시작합니다...")
    print("=" * 60)
    
    try:
        # TCO 분석기 생성 및 실행
        analyzer = ImprovedTCOAnalyzer(template_file)
        results = analyzer.run_complete_analysis()
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📋 분석 완료 - 생성된 파일들:")
        print("=" * 60)
        
        generated_files = [
            ('TCO_분석_입력템플릿.xlsx', '입력 데이터 템플릿'),
            ('TCO_분석_결과.png', '분석 결과 시각화'),
            ('tco_analysis.py', 'TCO 분석 코드'),
            ('create_tco_template.py', '템플릿 생성 코드'),
            ('run_tco_analysis.py', '실행 스크립트')
        ]
        
        for filename, description in generated_files:
            if os.path.exists(filename):
                size = os.path.getsize(filename) / 1024  # KB
                print(f"✅ {filename:<30} ({size:.1f}KB) - {description}")
            else:
                print(f"❌ {filename:<30} - 파일이 없습니다")
        
        # 백업 파일 확인
        backup_files = [f for f in os.listdir('.') if f.startswith('TCO_분석_입력템플릿_backup_')]
        if backup_files:
            print(f"\n📦 백업 파일들:")
            for backup in sorted(backup_files, reverse=True)[:3]:  # 최근 3개만 표시
                size = os.path.getsize(backup) / 1024
                print(f"   📄 {backup} ({size:.1f}KB)")
        
        print("\n" + "=" * 60)
        print("🎯 다음 단계 안내:")
        print("=" * 60)
        print("1. 📊 'TCO_분석_결과.png' 파일에서 분석 결과 확인")
        print("2. 📝 'TCO_분석_입력템플릿.xlsx' 파일에 실제 데이터 입력")
        print("3. 🔄 실제 데이터로 재분석 수행")
        print("4. 📈 필요시 추가 시나리오 분석 실행")
        
        print("\n💡 주요 분석 내용:")
        print("   • 5년 소유기간 기준 총소유비용 계산")
        print("   • ICE vs BEV 경제성 비교")
        print("   • 연도별 TCO 변화 추이 분석")
        print("   • ICE 지원 제거 시나리오 분석")
        print("   • 소비자 선택 모델 분석")
        
        print("\n🔒 데이터 보존 안내:")
        print("   • 사용자가 입력한 데이터는 자동으로 보존됩니다")
        print("   • 템플릿 재생성 시 백업 파일이 자동 생성됩니다")
        print("   • 기존 데이터는 새로운 분석에 반영됩니다")
        
        print("\n🎉 TCO 분석이 성공적으로 완료되었습니다!")
        
    except Exception as e:
        print(f"\n❌ TCO 분석 중 오류 발생: {e}")
        print("💡 다음 사항을 확인해주세요:")
        print("   • Excel 파일이 올바르게 생성되었는지 확인")
        print("   • 필요한 패키지들이 설치되었는지 확인")
        print("   • 파일 권한 및 경로 확인")
        return
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")
        print("💡 관리자에게 문의하거나 로그를 확인해주세요.") 