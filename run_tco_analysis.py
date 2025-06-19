#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCO 분석 통합 실행 스크립트
엑셀 템플릿 생성부터 분석까지 한 번에 실행
"""

import os
import sys
from create_tco_template import create_tco_template
from tco_analysis import TCOAnalyzer

def main():
    """메인 실행 함수"""
    print("="*60)
    print("        TCO (Total Cost of Ownership) 분석 도구")
    print("="*60)
    print("이 도구는 ICE vs BEV 총소유비용 비교 및 소비자 선택 분석을 수행합니다.")
    print()
    
    # 엑셀 템플릿 존재 확인
    template_file = "TCO_분석_입력템플릿.xlsx"
    
    if not os.path.exists(template_file):
        print("📊 엑셀 템플릿이 없습니다. 새로 생성하겠습니다...")
        try:
            create_tco_template()
            print("✅ 엑셀 템플릿 생성 완료!")
        except Exception as e:
            print(f"❌ 엑셀 템플릿 생성 실패: {e}")
            return
    else:
        print("📊 기존 엑셀 템플릿을 사용합니다.")
        
        # 새로 생성할지 묻기
        while True:
            choice = input("새로운 템플릿을 생성하시겠습니까? (y/n): ").lower().strip()
            if choice in ['y', 'yes', '예']:
                try:
                    create_tco_template()
                    print("✅ 새 엑셀 템플릿 생성 완료!")
                    break
                except Exception as e:
                    print(f"❌ 엑셀 템플릿 생성 실패: {e}")
                    return
            elif choice in ['n', 'no', '아니오']:
                print("기존 템플릿을 사용합니다.")
                break
            else:
                print("y 또는 n을 입력해주세요.")
    
    print()
    print("🚀 TCO 분석을 시작합니다...")
    print("-" * 60)
    
    try:
        # TCO 분석 실행
        analyzer = TCOAnalyzer(template_file)
        analyzer.run_full_analysis()
        
        print()
        print("="*60)
        print("✅ TCO 분석이 완료되었습니다!")
        print()
        print("📋 생성된 파일들:")
        
        files_to_check = [
            ("📊 엑셀 템플릿", template_file),
            ("📈 분석 결과 이미지", "TCO_분석_결과.png"),
            ("📄 사용법 가이드", "README_TCO분석.md")
        ]
        
        for desc, filename in files_to_check:
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                if size > 1024*1024:
                    size_str = f"{size/(1024*1024):.1f}MB"
                elif size > 1024:
                    size_str = f"{size/1024:.1f}KB"
                else:
                    size_str = f"{size}B"
                print(f"   {desc}: {filename} ({size_str})")
            else:
                print(f"   {desc}: {filename} (생성되지 않음)")
        
        print()
        print("💡 다음 단계:")
        print("   1. TCO_분석_입력템플릿.xlsx 파일에서 실제 데이터로 수정")
        print("   2. python tco_analysis.py 명령으로 재분석")
        print("   3. TCO_분석_결과.png에서 시각화 결과 확인")
        print()
        
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {e}")
        print("자세한 오류 정보:")
        import traceback
        traceback.print_exc()
        return
    
    print("="*60)
    print("감사합니다! 🎉")

if __name__ == "__main__":
    main() 