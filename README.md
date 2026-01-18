# 네이버 웹툰 주간 차트 수집 파이프라인

네이버 웹툰 주간 차트 데이터를 장기적으로 추적하고 분석하기 위한 ELT 파이프라인입니다.

## 프로젝트 개요

이 프로젝트는 매주 네이버 웹툰 주간 차트 데이터를 수집하여 저장하고, 장기적인 추세 분석을 가능하게 합니다.

### 핵심 특징

- **ELT 아키텍처**: HTML 원본 보존 (GCS) + 정제된 데이터 저장 (BigQuery)
- **확장 가능한 데이터 모델**: dim_webtoon (마스터) + fact_weekly_chart (히스토리)
- **GCP Always Free 범위 내 운영**: 비용 최적화
- **자동화**: Cloud Scheduler를 통한 주 1회 자동 실행

## 프로젝트 구조

```
naver_webtoon/
├── src/                    # 핵심 로직
│   ├── extract.py         # HTML 수집
│   ├── parse.py           # HTML 파싱
│   ├── transform.py       # 데이터 변환
│   ├── models.py          # 데이터 모델 정의
│   └── utils.py           # 유틸리티 함수
├── docs/                   # 문서
│   ├── planning/          # 계획 문서
│   ├── archive/           # 아카이브 문서
│   └── *.md               # 가이드 문서
├── functions/             # Cloud Functions 코드
│   └── pipeline_function/ # 통합 파이프라인 함수
├── scripts/               # 배포/설정 스크립트
│   ├── docs/              # 스크립트 관련 문서
│   ├── *.sh               # Shell 스크립트
│   └── *.py               # Python 스크립트
├── tests/                 # 테스트 코드
├── data/                  # 로컬 테스트용 데이터 (gitignore)
├── logs/                  # 로그 파일 (gitignore)
├── PROGRESS.md            # 전체 진행 상황 추적
├── STATUS.md              # 현재 작업 상태
└── README.md              # 프로젝트 개요
```

## 시작하기

### 1. 환경 설정

```bash
# Python 3.9 이상 필요
python --version

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 로컬 테스트

```bash
# 파이프라인 실행 (구현 후)
python src/extract.py
python src/parse.py
python src/transform.py
```

## 데이터 모델

자세한 스키마 정보는 [`docs/bigquery_schema.md`](./docs/bigquery_schema.md)를 참고하세요.

### dim_webtoon (마스터 테이블)
- `webtoon_id` (STRING, PK): 웹툰 고유 ID
- `title` (STRING): 웹툰 제목
- `author` (STRING): 작가명
- `genre` (STRING): 장르
- `tags` (ARRAY<STRING>): 태그 리스트
- `created_at`, `updated_at` (TIMESTAMP): 타임스탬프

### fact_weekly_chart (히스토리 테이블) ⭐ **가장 중요**
- `chart_date` (DATE, Partition Key): 수집 날짜
- `webtoon_id` (STRING, FK): 웹툰 ID → dim_webtoon 참조
- `rank` (INTEGER): 주간 차트 순위
- `collected_at` (TIMESTAMP): 수집 시각
- `weekday`, `year`, `month`, `week`, `view_count`: 추가 정보

### fact_webtoon_stats (상세 정보 히스토리)
- `webtoon_id` (STRING, FK): 웹툰 ID
- `collected_at` (TIMESTAMP, Partition Key): 수집 시각
- `favorite_count`, `finished`, `rest`, `total_episode_count`: 상세 정보

## 진행 상황

- [`PROGRESS.md`](./PROGRESS.md): 전체 진행 상황 추적
- [`STATUS.md`](./STATUS.md): 현재 작업 상태

## 문서

### 계획 문서
- [`docs/planning/01_전체_구현_계획.md`](./docs/planning/01_전체_구현_계획.md): 상세 구현 계획
- [`docs/planning/02_로컬_테스트_계획.md`](./docs/planning/02_로컬_테스트_계획.md): 로컬 테스트 상세 계획
- [`docs/planning/03_GCP_배포_계획.md`](./docs/planning/03_GCP_배포_계획.md): GCP 배포 계획

### 가이드 문서
- [`docs/NEXT_STEPS.md`](./docs/NEXT_STEPS.md): 다음 단계 가이드 ⭐
- [`docs/reference/bigquery_schema.md`](./docs/reference/bigquery_schema.md): BigQuery 스키마 문서
- [`docs/reference/bigquery_tables_guide.md`](./docs/reference/bigquery_tables_guide.md): BigQuery 테이블 사용 가이드
- [`docs/monitoring/monitoring_guide.md`](./docs/monitoring/monitoring_guide.md): 로깅 및 모니터링 가이드
- [`docs/monitoring/cost_monitoring_guide.md`](./docs/monitoring/cost_monitoring_guide.md): 비용 모니터링 가이드
- [`docs/data_management/data_validation_guide.md`](./docs/data_management/data_validation_guide.md): 데이터 검증 가이드
- [`docs/setup/alert_setup_complete_guide.md`](./docs/setup/alert_setup_complete_guide.md): Alert Policy 설정 가이드

## 라이선스

이 프로젝트는 개인 프로젝트입니다.

