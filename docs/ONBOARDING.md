# 프로젝트 온보딩 가이드

> **목적**: 새로운 AI 어시스턴트나 개발자가 이 프로젝트를 빠르게 이해하고 작업을 이어갈 수 있도록 하는 가이드

---

## 🎯 프로젝트 개요

**네이버 웹툰 주간 차트 수집 파이프라인** - 매주 네이버 웹툰 주간 차트 데이터를 수집하여 BigQuery에 저장하는 ELT 파이프라인

### 핵심 목표
- 매주 네이버 웹툰 주간 차트 데이터 수집 및 저장
- HTML 원본 보존 (GCS) + 정제된 데이터 저장 (BigQuery) 이중 구조
- GCP Always Free 범위 내에서 운영
- 확장 가능한 데이터 모델 설계

---

## 📋 현재 상태 (2025-12-31)

### 완료된 작업
- ✅ 로컬 파이프라인 구현 완료
- ✅ GCP 인프라 구축 완료
- ✅ Cloud Functions 배포 완료
- ✅ Cloud Scheduler 설정 완료 (매주 월요일 오전 9시 자동 실행)
- ✅ 데이터 검증 함수 배포 완료
- ✅ Alert Policy 설정 완료
- ✅ GitHub Actions CI/CD 구축 완료
- ✅ 파이프라인 최종 테스트 완료

### 현재 배포된 리소스
- **GCP 프로젝트**: `naver-webtoon-collector`
- **리전**: `asia-northeast3`
- **Cloud Functions**:
  - `pipeline-function` (Gen2, Python 3.11)
  - `data-validation-function` (Gen2, Python 3.11)
- **Cloud Scheduler**:
  - `naver-webtoon-weekly-collection` (매주 월요일 오전 9시)
  - `data-validation-scheduler` (매주 월요일 오전 10시)
- **BigQuery**:
  - 데이터셋: `naver_webtoon`
  - 테이블: `dim_webtoon`, `fact_weekly_chart`, `fact_webtoon_stats`
- **GCS**:
  - 버킷: `naver-webtoon-raw`
  - 경로: `raw_html/YYYY-MM-DD/sort_{sort_type}/webtoon_chart.json`
- **알림 채널**: 
  - `entrkjm@vaiv.kr`
  - `entrkjm@gmail.com`

---

## 🏗️ 아키텍처

### ELT 파이프라인 구조

```
네이버 웹툰 API
    ↓
[Extract] → API 응답 수집
    ↓
[Load Raw] → GCS에 JSON 원본 저장
    ↓
[Transform] → 데이터 파싱 및 정규화
    ↓
[Load Refined] → BigQuery에 정제된 데이터 저장
```

### 인프라 구성

```
Cloud Scheduler (매주 월요일 오전 9시)
    ↓
Cloud Functions (pipeline-function)
    ├── Extract: 네이버 웹툰 API 호출
    ├── Load Raw: GCS에 원본 저장
    ├── Transform: 데이터 파싱
    └── Load Refined: BigQuery에 저장
         ↓
    BigQuery (dim_webtoon, fact_weekly_chart)
    
Cloud Scheduler (매주 월요일 오전 10시)
    ↓
Cloud Functions (data-validation-function)
    └── 데이터 품질 검증 및 알림
```

### 데이터 모델

**dim_webtoon** (마스터 테이블)
- `webtoon_id` (PK): 웹툰 고유 ID
- `title`, `author`, `genre`, `tags`
- `created_at`, `updated_at`

**fact_weekly_chart** (히스토리 테이블) ⭐ **가장 중요**
- `chart_date` (Partition Key): 수집 날짜
- `webtoon_id` (FK): 웹툰 ID
- `rank`: 주간 차트 순위
- `weekday`, `year`, `month`, `week`, `view_count`

**fact_webtoon_stats** (상세 정보 히스토리)
- `webtoon_id` (FK): 웹툰 ID
- `collected_at` (Partition Key): 수집 시각
- `favorite_count`, `finished`, `rest`, `total_episode_count`

---

## 📁 프로젝트 구조

```
naver_webtoon/
├── src/                    # 핵심 로직
│   ├── extract.py         # API 수집
│   ├── parse_api.py       # API 응답 파싱
│   ├── transform.py       # 데이터 변환
│   ├── upload_bigquery.py # BigQuery 업로드
│   ├── upload_gcs.py      # GCS 업로드
│   └── utils.py           # 유틸리티
├── functions/             # Cloud Functions
│   ├── pipeline_function/ # 메인 파이프라인
│   └── data_validation_function/ # 데이터 검증
├── scripts/               # 배포/설정 스크립트
│   ├── setup/            # GCP 설정 스크립트
│   ├── monitoring/       # 모니터링 스크립트
│   └── data_management/ # 데이터 관리 스크립트
├── docs/                  # 문서
│   ├── setup/            # 설정 가이드
│   ├── monitoring/       # 모니터링 가이드
│   ├── data_management/ # 데이터 관리 가이드
│   └── reference/        # 참고 문서
├── .github/workflows/     # GitHub Actions CI/CD
├── README.md             # 프로젝트 개요
├── STATUS.md             # 현재 작업 상태
├── PROGRESS.md           # 전체 진행 상황
└── .cursorrules          # 프로젝트 규칙
```

---

## 🔑 핵심 원칙

### 1. 멱등성 보장 (필수)
- 수집 날짜(Partition)를 기준으로 중복 체크
- 같은 날짜에 여러 번 실행되어도 데이터 중복 방지
- MERGE 문 사용 (BigQuery)

### 2. ELT 아키텍처
- **Extract & Load Raw**: 원본 데이터 보존 (GCS)
- **Transform & Load Refined**: 정제된 데이터 저장 (BigQuery)

### 3. GCP Always Free 범위 내 운영
- Cloud Functions: 200만 요청/월
- BigQuery: 10GB 저장, 1TB 쿼리/월
- GCS: 5GB 저장

### 4. 자동화
- Cloud Scheduler를 통한 주 1회 자동 실행
- GitHub Actions를 통한 자동 배포

---

## 🚀 빠른 시작

### 1. 프로젝트 이해하기
1. [`README.md`](../README.md) 읽기 - 프로젝트 개요
2. [`.cursorrules`](../.cursorrules) 읽기 - 핵심 원칙
3. [`STATUS.md`](../STATUS.md) 읽기 - 현재 상태
4. [`docs/reference/bigquery_schema.md`](reference/bigquery_schema.md) 읽기 - 데이터 모델

### 2. 현재 배포 상태 확인
```bash
# Cloud Functions 확인
gcloud functions list --gen2 --region=asia-northeast3

# Cloud Scheduler 확인
gcloud scheduler jobs list --location=asia-northeast3

# BigQuery 데이터 확인
bq query --use_legacy_sql=false \
    "SELECT COUNT(*) as count, MAX(chart_date) as latest_date 
     FROM \`naver-webtoon-collector.naver_webtoon.fact_weekly_chart\`"
```

### 3. 로그 확인
```bash
# 파이프라인 함수 로그
gcloud functions logs read pipeline-function --gen2 --region=asia-northeast3 --limit=50

# 데이터 검증 함수 로그
gcloud functions logs read data-validation-function --gen2 --region=asia-northeast3 --limit=50
```

---

## 📚 필수 문서

### 시작하기
- [`README.md`](../README.md) - 프로젝트 개요
- [`.cursorrules`](../.cursorrules) - 프로젝트 규칙
- [`STATUS.md`](../STATUS.md) - 현재 상태

### 아키텍처 및 데이터 모델
- [`docs/reference/bigquery_schema.md`](reference/bigquery_schema.md) - BigQuery 스키마
- [`docs/reference/bigquery_tables_guide.md`](reference/bigquery_tables_guide.md) - 테이블 가이드

### 운영 가이드
- [`docs/monitoring/monitoring_guide.md`](monitoring/monitoring_guide.md) - 모니터링 가이드
- [`docs/data_management/data_validation_guide.md`](data_management/data_validation_guide.md) - 데이터 검증 가이드
- [`docs/setup/alert_setup_complete_guide.md`](setup/alert_setup_complete_guide.md) - Alert Policy 설정

### 다음 단계
- [`docs/NEXT_STEPS.md`](NEXT_STEPS.md) - 다음 단계 가이드

---

## ⚠️ 주의사항

### 1. 멱등성 보장
- 같은 날짜에 여러 번 실행되어도 데이터가 중복되지 않도록 처리
- MERGE 문 사용 필수

### 2. 비용 관리
- GCP Always Free 범위 내에서 운영
- BigQuery 쿼리 비용 주의
- GCS 저장 용량 모니터링

### 3. Rate Limiting
- 네이버 웹툰 API 호출 시 Rate Limiting 준수
- 배치 처리 시 적절한 딜레이 추가

### 4. 에러 핸들링
- 모든 외부 호출에 에러 핸들링 필수
- 실패 시 명확한 로그 메시지 기록
- Alert Policy를 통한 자동 알림

---

## 🔧 트러블슈팅

### 파이프라인 실행 실패
1. Cloud Functions 로그 확인
2. Alert Policy 알림 확인
3. BigQuery 데이터 확인
4. GCS 원본 데이터 확인

### 데이터 검증 실패
1. 데이터 검증 함수 로그 확인
2. 임계값 설정 확인 (`MIN_EXPECTED_RECORDS`)
3. BigQuery 데이터 품질 확인

### 배포 실패
1. GitHub Actions 로그 확인
2. GCP 권한 확인
3. 서비스 계정 키 확인

---

## 📞 연락처 및 리소스

### GCP 리소스
- **프로젝트 ID**: `naver-webtoon-collector`
- **리전**: `asia-northeast3`
- **서비스 계정**: `webtoon-collector@naver-webtoon-collector.iam.gserviceaccount.com`

### GitHub
- **저장소**: `entrkjm/naver-webtoon-collector`
- **CI/CD**: GitHub Actions (`.github/workflows/deploy.yml`)

---

## 💡 작업 시작 전 체크리스트

- [ ] `README.md` 읽기
- [ ] `.cursorrules` 읽기
- [ ] `STATUS.md` 읽기
- [ ] 현재 배포 상태 확인
- [ ] BigQuery 데이터 확인
- [ ] 로그 확인
- [ ] 관련 문서 확인

---

## 🎯 다음 작업 시 참고

1. **현재 상태 확인**: `STATUS.md` 확인
2. **다음 단계 확인**: `docs/NEXT_STEPS.md` 확인
3. **프로젝트 규칙 준수**: `.cursorrules` 확인
4. **문서 업데이트**: 작업 완료 후 `STATUS.md`, `PROGRESS.md` 업데이트

---

**마지막 업데이트**: 2025-12-31

