# TCO Analysis for GESI & NREL

**ICE vs BEV 총소유비용(Total Cost of Ownership) 분석 모델**

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## 🎯 프로젝트 개요

이 프로젝트는 **내연기관차(ICE)**와 **전기차(BEV)**의 총소유비용을 비교하고, ICE에 대한 직간접 지원 제거 시 소비자 선택 변화를 분석하는 종합적인 도구입니다.

### 주요 목적
- 차량 분류별 상세한 TCO 분석
- ICE 지원 정책 제거 시나리오 분석
- 소비자 선택 행동 예측 모델링
- 정책 결정을 위한 데이터 기반 인사이트 제공

## 🚀 주요 기능

### 📊 차량 분류별 TCO 분석
- **대분류**: 승용차 / 승합차 / 화물차
- **중분류**: 자가용 / 상용차
- **소분류**: 소형 / 중형 / 대형
- **차량유형**: ICE / BEV

### 💰 비용 구성요소 분석
- 구매비용
- 연료비 (연료비/전기비)
- 유지보수비
- 세금 및 보험료
- 감가상각비
- 정부 보조금

### 🔄 시나리오 분석
- ICE 직간접 지원 제거 전후 비교
- BEV 경쟁력 변화 분석
- 정책 영향도 평가

### 🤖 소비자 선택 모델
- 로지스틱 회귀 기반 선택 확률 예측
- TCO 변화에 따른 BEV 선택률 시뮬레이션
- 특성 중요도 분석

### 📈 시각화
- 차량유형별 TCO 비교 차트
- 비용 구성요소 분석 그래프
- 시나리오 분석 결과
- BEV 선택 확률 곡선

## 📁 파일 구조

```
📁 TCO-analysis_GESI_NREL/
├── 📄 create_tco_template.py      # 엑셀 템플릿 생성 스크립트
├── 📄 tco_analysis.py             # 메인 TCO 분석 엔진
├── 📄 run_tco_analysis.py         # 통합 실행 스크립트
├── 📊 TCO_분석_입력템플릿.xlsx     # 데이터 입력 템플릿
├── 📈 TCO_분석_결과.png           # 분석 결과 시각화
├── 📄 README.md                   # 프로젝트 가이드 (이 파일)
├── 📄 README_TCO분석.md           # 상세 기술 문서
└── 📄 requirements.txt            # 필요 패키지 목록
```

## 🛠 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/HYODONGMOON/TCO-analysis_GESI_NREL.git
cd TCO-analysis_GESI_NREL
```

### 2. 필요 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 빠른 시작 (통합 실행)
```bash
python run_tco_analysis.py
```

### 4. 단계별 실행
```bash
# 1단계: 엑셀 템플릿 생성
python create_tco_template.py

# 2단계: TCO 분석 실행
python tco_analysis.py
```

## 📊 분석 결과 예시

### 현재 상황 분석
```
📊 현재 상황:
   • ICE 평균 TCO: 7,407만원
   • BEV 평균 TCO: 7,898만원
   • BEV가 ICE보다 492만원 비쌈
```

### ICE 지원 제거 시나리오
```
🔄 ICE 지원 제거 시:
   • ICE TCO 증가: 123만원
   • BEV 경쟁력 개선: 123만원
```

### 정책 시사점
```
💡 정책 시사점:
   • ICE 직간접 지원 제거 시 BEV 경쟁력 크게 향상
   • 총소유비용이 소비자 선택에 핵심적 영향
   • 차량 분류별 맞춤형 정책 필요
```

## 📈 시각화 결과

분석 실행 후 `TCO_분석_결과.png` 파일에서 다음 차트들을 확인할 수 있습니다:

1. **차량유형별 평균 TCO 비교**
2. **비용 구성요소별 ICE vs BEV 비교**
3. **시나리오 분석: 조정 전후 TCO**
4. **TCO 차이에 따른 BEV 선택 확률**

## 🔧 사용자 정의

### 실제 데이터 사용
1. `TCO_분석_입력템플릿.xlsx` 파일 열기
2. **차량분류** 시트에서 실제 데이터로 수정
3. **지원제거시나리오** 시트에서 정책 시나리오 조정
4. `python tco_analysis.py` 재실행

### 분석 모델 확장
- 더 많은 차량 분류 추가
- 새로운 비용 항목 포함
- 다양한 정책 시나리오 테스트
- 지역별/시간별 분석

## 🎯 활용 분야

### 정책 입안자
- 전기차 보조금 정책 효과 분석
- ICE 지원 정책 개선 방안 도출
- 탄소 중립 정책 영향 평가

### 연구기관
- TCO 기반 시장 전망 분석
- 소비자 행동 패턴 연구
- 정책 시뮬레이션 및 모델링

### 산업계
- 전기차 시장 진입 전략 수립
- 가격 경쟁력 분석
- 시장 점유율 예측

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 연락처

- **개발자**: HYODONGMOON
- **이메일**: [이메일 주소]
- **프로젝트 링크**: [https://github.com/HYODONGMOON/TCO-analysis_GESI_NREL](https://github.com/HYODONGMOON/TCO-analysis_GESI_NREL)

## 🙏 감사의 글

- **GESI (Green Energy Strategy Institute)** - 연구 지원
- **NREL (National Renewable Energy Laboratory)** - 기술 협력
- **T3CO** - 기초 프레임워크 제공

---

**⭐ 이 프로젝트가 유용하다면 Star를 눌러주세요!**

## 📚 추가 문서

- [상세 기술 문서](README_TCO분석.md)
- [API 문서](docs/api.md) (예정)
- [사용 사례](docs/examples.md) (예정)

---
**최종 업데이트**: 2025-06-19  
**버전**: 1.0.0 