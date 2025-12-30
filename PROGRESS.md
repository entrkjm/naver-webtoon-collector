# 전체 진행 상황 추적

> **마지막 업데이트**: 2025-12-29  
> **현재 Phase**: Phase 3 완료  
> **진행 상황**: Phase 1 완료, Phase 2 완료, Phase 3 완료 (로깅 및 모니터링, 비용 모니터링, 데이터 검증, Alert Policy 설정 모두 완료)  
> **최근 작업**: Alert Policy 설정 완료, 알림 시스템 테스트 완료, 루트 디렉토리 문서 업데이트

---

## 📊 전체 진행률

| Phase | 진행률 | 완료/전체 |
|-------|--------|----------|
| Phase 1: 로컬 개발 및 테스트 | 90% | 3.5/4 (2 완료, 1 완료, 1 부분 완료) |
| Phase 2: GCP 인프라 구축 | 100% | 7/7 (모두 완료) |
| Phase 3: 모니터링 및 최적화 | 100% | 4/4 (모두 완료) |
| **Alert Policy 설정** | 100% | 완료 |
| **전체** | **95%** | **15.5/15** |

---

## Phase 1: 로컬 개발 및 테스트

**목표**: 핵심 로직을 로컬에서 구현하고 검증

### 1.1 로컬 환경 설정
- [ ] Python 가상환경 설정 (사용자 작업 필요)
- [ ] 필요한 라이브러리 설치 (사용자 작업 필요)
- [x] 프로젝트 디렉토리 구조 생성
- [x] requirements.txt 작성
- [x] 기본 소스 파일 스켈레톤 생성
- [x] README.md, .gitignore 작성

**상태**: 🟡 진행 중  
**완료일**: -  
**비고**: 디렉토리 구조와 기본 파일 생성 완료. 가상환경 설정은 사용자 작업 필요.

---

### 1.2 핵심 로직 구현
- [x] **Extract 모듈** (`src/extract.py`)
  - [x] 네이버 웹툰 페이지 HTML 수집
  - [x] User-Agent 헤더 설정
  - [x] 에러 핸들링 및 재시도 로직
  - [x] HTML 로컬 저장 (날짜별 디렉토리)
- [x] **Parse 모듈** (`src/parse.py`, `src/parse_api.py`)
  - [x] HTML에서 차트 데이터 파싱
  - [x] API 응답 파싱 (우선 사용)
  - [x] 순위, 제목, 웹툰 ID 추출
  - [x] 요일 정보 추출
  - [x] HTML 구조 변경 대비 유연한 파싱 (여러 선택자 시도)
  - [x] API 기반 파싱으로 업그레이드 완료
- [x] **Transform 모듈** (`src/transform.py`)
  - [x] 파싱된 데이터를 스키마에 맞게 변환
  - [x] dim_webtoon과 fact_weekly_chart 분리 로직
  - [x] CSV 저장 (날짜별 파일 분리)
  - [x] 멱등성 보장 (중복 체크)
- [x] **웹툰 상세 정보 수집 모듈** (`src/extract_webtoon_detail.py`, `src/parse_webtoon_detail.py`, `src/transform_webtoon_stats.py`)
  - [x] API 우선, HTML 보조 수집 전략
  - [x] 관심 수(favorite_count) 수집
  - [x] 완결/휴재 상태 수집
  - [x] 전체 에피소드 수 수집
  - [x] Rate limiting 및 배치 처리
  - [x] CSV 저장 및 멱등성 보장
- [x] **통합 실행 스크립트** (`src/run_pipeline.py`)
  - [x] Extract → Parse → Transform 전체 플로우
  - [x] 웹툰 상세 정보 수집 단계 통합
- [x] **유틸리티 모듈** (`src/utils.py`)
  - [x] 날짜 처리, 파일 I/O, 로깅 설정

**상태**: 🟢 완료  
**완료일**: 2025-12-20  
**비고**: API 기반 수집으로 업그레이드 완료. 웹툰 상세 정보 수집 기능 추가 완료.

---

### 1.3 데이터 모델 설계
- [x] `dim_webtoon` 테이블 스키마 정의
  - [x] 필드: webtoon_id (PK), title, author, genre, created_at, updated_at
  - [x] 레코드 생성 함수 구현
  - [x] 검증 함수 구현
- [x] `fact_weekly_chart` 테이블 스키마 정의
  - [x] 필드: chart_date (Partition), webtoon_id (FK), rank, collected_at, weekday, year, month, week, view_count
  - [x] 레코드 생성 함수 구현
  - [x] 검증 함수 구현
- [x] `fact_webtoon_stats` 테이블 스키마 정의 (웹툰 상세 정보 히스토리)
  - [x] 필드: webtoon_id (FK), collected_at (Partition), favorite_count, favorite_count_source, finished, rest, total_episode_count, year, month, week
  - [x] 레코드 생성 함수 구현
  - [x] 검증 함수 구현
- [x] 관계형 데이터 모델 검증
  - [x] Foreign Key 관계 검증 함수 구현
- [x] 스키마 문서 작성 (`src/models.py`)

**상태**: 🟢 완료  
**완료일**: 2025-12-20  
**비고**: 데이터 모델 스키마 및 검증 로직 구현 완료. 웹툰 상세 정보 히스토리 테이블 추가 완료.

---

### 1.4 로컬 테스트
- [x] 단일 실행 테스트
  - [x] HTML 수집 성공 확인 (API 기반)
  - [x] 파싱 성공 확인 (API 응답 파싱)
  - [x] 데이터 저장 성공 확인 (CSV)
  - [x] 웹툰 상세 정보 수집 성공 확인
- [ ] 멱등성 테스트
  - [x] 같은 날짜 재실행 시 데이터 중복 없음 확인 (기본 테스트 완료)
  - [ ] 다른 날짜 실행 시 새 레코드 추가 확인
  - [ ] 웹툰 상세 정보 멱등성 테스트
- [ ] 에러 핸들링 테스트
  - [ ] 네트워크 오류 시나리오
  - [ ] API 응답 변경 시나리오
  - [ ] 파일 시스템 오류 시나리오
- [ ] 데이터 품질 검증
  - [x] dim_webtoon 중복 없음 확인 (기본 검증 완료)
  - [x] fact_weekly_chart 중복 없음 확인 (기본 검증 완료)
  - [x] Foreign Key 관계 유지 확인 (기본 검증 완료)
  - [ ] fact_webtoon_stats 데이터 품질 검증

**상태**: 🟡 진행 중  
**완료일**: -  
**비고**: 기본 기능 테스트 완료. 체계적인 테스트 시나리오 실행 필요.

**산출물**:
- [ ] 로컬에서 동작하는 완전한 파이프라인 코드
- [ ] 테스트 결과 및 검증 리포트
- [ ] 데이터 모델 스키마 문서

---

## Phase 2: GCP 인프라 단계별 구축

### 2.1 GCP 프로젝트 설정
- [x] GCP 프로젝트 생성 및 설정
  - 프로젝트 ID: `naver-webtoon-collector`
  - 프로젝트 이름: "Naver Webtoon Collector"
- [x] 필요한 API 활성화
  - [x] Cloud Functions API
  - [x] Cloud Scheduler API
  - [x] BigQuery API
  - [x] Cloud Storage API
  - [x] Cloud Build API
  - [x] Cloud Run API
- [x] 서비스 계정 생성 및 권한 설정
  - 서비스 계정: `webtoon-collector@naver-webtoon-collector.iam.gserviceaccount.com`
  - BigQuery 데이터 편집자, 작업 사용자 권한
  - Cloud Storage 객체 관리자 권한
  - Cloud Functions 실행 권한, 개발자 권한
- [x] 로컬 인증 설정 (gcloud CLI)
  - gcloud 인증 완료
  - 프로젝트 설정 완료
  - 기본 리전 설정 (asia-northeast3)

**상태**: 🟢 완료  
**완료일**: 2025-12-21  
**비고**: GCP 프로젝트 생성 및 기본 설정 완료. 결제 계정 연결 완료.

**검증 항목**:
- [ ] GCP 프로젝트 접근 가능 여부
- [ ] 필요한 API 활성화 확인

---

### 2.2 BigQuery 데이터 모델 구축
**목표**: 데이터 저장소 스키마 생성

- [x] BigQuery 데이터셋 생성
- [x] `dim_webtoon` 테이블 생성 (스키마 정의)
- [x] `fact_weekly_chart` 테이블 생성 (파티션 설정: 수집 날짜 기준)
- [x] `fact_webtoon_stats` 테이블 생성 (파티션 설정: collected_at 기준)
- [x] BigQuery 스키마 정의 파일 작성 (`scripts/setup_bigquery.sql`)
- [ ] 샘플 데이터로 스키마 검증 (다음 단계에서 진행)

**상태**: 🟢 완료  
**완료일**: 2025-12-27  
**비고**: 
- 데이터셋: `naver-webtoon-collector.naver_webtoon`
- 모든 테이블 생성 완료
- 파티션 및 클러스터링 설정 완료
- tags 필드는 REPEATED STRING (ARRAY)로 설정됨

**검증 항목**:
- [x] 테이블 생성 확인
- [x] 파티션 설정 확인
- [ ] 샘플 데이터 INSERT/SELECT 테스트 (다음 단계에서 진행)

**산출물**:
- [x] BigQuery 스키마 정의 파일 (SQL): `scripts/setup_bigquery.sql`
- [x] 테이블 생성 완료

---

### 2.3 GCS 버킷 생성 및 테스트
**목표**: HTML 원본 저장소 구축

- [x] GCS 버킷 생성
- [x] 버킷 권한 설정
- [x] 로컬에서 GCS 업로드/다운로드 테스트
- [x] 파일명 규칙 정의
- [x] 파일 업로드 테스트 스크립트 작성

**상태**: 🟢 완료  
**완료일**: 2025-12-27  
**비고**: 
- 버킷명: `gs://naver-webtoon-raw`
- 리전: `asia-northeast3`
- 스토리지 클래스: STANDARD
- 서비스 계정 권한 부여 완료 (objectAdmin)
- 업로드/다운로드 테스트 성공

**파일명 규칙**:
- 차트 데이터: `raw_html/YYYY-MM-DD/sort_{sort_type}/webtoon_chart.json`
- 웹툰 상세 정보: `raw_html/YYYY-MM-DD/webtoon_detail/{webtoon_id}.json`

**검증 항목**:
- [x] 버킷 생성 및 접근 가능 여부
- [x] 파일 업로드/다운로드 테스트
- [x] 파일명 규칙 정의 완료

**산출물**:
- [x] GCS 버킷 설정 완료
- [x] 파일 업로드 테스트 스크립트: `scripts/test_gcs_upload.sh`

---

### 2.4 BigQuery 업로드 기능 구현
**목표**: JSONL 파일을 BigQuery에 적재하는 기능 구현

- [x] `src/upload_bigquery.py` 모듈 생성
- [x] `upload_dim_webtoon` 함수 구현 (MERGE로 멱등성 보장)
- [x] `upload_fact_weekly_chart` 함수 구현 (MERGE로 멱등성 보장)
- [x] `upload_fact_webtoon_stats` 함수 구현 (MERGE로 멱등성 보장)
- [x] 테스트 스크립트 작성 (`scripts/test_bigquery_upload.py`)
- [ ] 로컬에서 실제 업로드 테스트 (다음 단계에서 진행)

**상태**: 🟢 완료  
**완료일**: 2025-12-27  
**비고**: 
- BigQuery 클라이언트 라이브러리 추가 (`google-cloud-bigquery`)
- 임시 테이블을 사용한 MERGE 방식으로 중복 방지
- 배치 업로드 지원 (1000개씩)
- tags 필드 ARRAY 변환 처리

**검증 항목**:
- [x] 모듈 생성 및 함수 구현 완료
- [ ] 로컬에서 실제 업로드 테스트

**산출물**:
- [x] `src/upload_bigquery.py`: BigQuery 업로드 모듈
- [x] `scripts/test_bigquery_upload.py`: 테스트 스크립트
- [x] `requirements.txt` 업데이트 (google-cloud-bigquery 추가)

---

### 2.5 GCS 업로드 기능 구현
**목표**: HTML/JSON 원본 파일을 GCS에 업로드하는 기능 구현

- [x] `src/upload_gcs.py` 모듈 생성
- [x] `upload_chart_data_to_gcs` 함수 구현 (차트 데이터 업로드)
- [x] `upload_webtoon_detail_to_gcs` 함수 구현 (웹툰 상세 정보 업로드)
- [x] `extract.py` 수정: API 응답을 JSON 파일로도 저장
- [x] `run_pipeline.py`에 GCS 업로드 통합 (환경 변수로 제어)
- [x] 테스트 스크립트 작성 (`scripts/test_gcs_upload_data.py`)

**상태**: 🟢 완료  
**완료일**: 2025-12-27  
**비고**: 
- GCS 클라이언트 라이브러리 사용 (`google-cloud-storage`)
- 파일명 규칙: `raw_html/YYYY-MM-DD/sort_{sort_type}/webtoon_chart.json`
- 환경 변수 `UPLOAD_TO_GCS=true`로 업로드 활성화
- API 응답을 JSON 파일로 저장하여 GCS에 업로드

**검증 항목**:
- [x] 모듈 생성 및 함수 구현 완료
- [ ] 로컬에서 실제 업로드 테스트 (다음 단계에서 진행)

**산출물**:
- [x] `src/upload_gcs.py`: GCS 업로드 모듈
- [x] `scripts/test_gcs_upload_data.py`: 테스트 스크립트
- [x] `src/extract.py` 수정: JSON 파일 저장 기능 추가
- [x] `src/run_pipeline.py` 수정: GCS 업로드 통합

---

### 2.6 Cloud Functions 구현
**목표**: 파이프라인을 Cloud Functions로 포팅

- [x] Cloud Functions 디렉토리 구조 생성 (`functions/pipeline_function/`)
- [x] `main.py` 작성 (HTTP 트리거 진입점)
- [x] `requirements.txt` 작성 (Cloud Functions용 의존성)
- [x] `deploy.sh` 배포 스크립트 작성
- [x] `README.md` 작성 (배포 및 사용 가이드)
- [x] `src/utils.py` 수정: 환경 변수 `DATA_DIR` 지원
- [ ] 로컬 Functions Framework 테스트
- [ ] Cloud Functions 배포 및 테스트

**상태**: 🟢 완료  
**완료일**: 2025-12-28  
**비고**: 
- 통합 파이프라인으로 구현 (Extract → Load Raw → Transform → Load Refined)
- GCS에 JSON 원본 저장
- BigQuery에 정제된 데이터 저장
- HTTP 트리거로 실행
- 환경 변수로 설정 관리
- 함수 URL: https://pipeline-function-l3loqwy2ea-du.a.run.app
- 배포 성공 및 수동 테스트 완료
- 타임아웃: 3600초 (1시간) - 수백 개 웹툰 수집 시 5초 sleep 고려

**검증 항목**:
- [x] 코드 작성 완료
- [x] 로컬 Functions Framework 테스트
- [x] Cloud Functions 배포 성공
- [x] 수동 HTTP 트리거 테스트
- [x] GCS에 파일 저장 확인
- [x] BigQuery에 데이터 적재 확인 (fact_weekly_chart 성공, dim_webtoon tags 타입 이슈 있음)

**산출물**:
- [x] `functions/pipeline_function/main.py`: Cloud Functions 진입점
- [x] `functions/pipeline_function/requirements.txt`: 의존성 패키지
- [x] `functions/pipeline_function/deploy.sh`: 배포 스크립트
- [x] `functions/pipeline_function/README.md`: 사용 가이드

---

### 2.7 Cloud Scheduler 설정
**목표**: 주 1회 자동 실행 스케줄 설정

- [x] Cloud Scheduler API 활성화
- [x] Cloud Scheduler 작업 생성 (`naver-webtoon-weekly-collection`)
- [x] 스케줄 설정: 매주 월요일 오전 9시 (KST)
- [x] HTTP 타겟 설정: Cloud Functions URL
- [x] 페이로드 설정: `{"sort_types": ["popular", "view"]}`
- [x] 배포 스크립트 작성 (`scripts/setup_scheduler.sh`)
- [x] 수동 실행 테스트

**상태**: 🟢 완료  
**완료일**: 2025-12-28  
**비고**: 
- 작업명: `naver-webtoon-weekly-collection`
- 스케줄: 매주 월요일 오전 9시 (KST, UTC+9)
- Cron 표현식: `0 0 * * 1` (UTC 기준)
- 타임존: `Asia/Seoul`
- 다음 실행 시간: 자동 계산됨

**검증 항목**:
- [x] 스케줄러 작업 생성 확인
- [x] 수동 실행 테스트 성공
- [x] 스케줄 설정 확인

**산출물**:
- [x] `scripts/setup_scheduler.sh`: Cloud Scheduler 설정 스크립트
- [x] Cloud Scheduler 작업 생성 완료

---

### 2.5 Cloud Functions - Transform 함수 구현
**목표**: GCS의 HTML을 파싱하여 BigQuery에 적재하는 함수 배포

- [ ] Phase 1에서 구현한 Parse/Transform 로직을 Cloud Functions로 포팅
- [ ] GCS에서 HTML 다운로드 로직 추가
- [ ] BigQuery 클라이언트 라이브러리 연동
- [ ] 멱등성 보장 로직 구현 (파티션 기반 중복 체크)
- [ ] 환경 변수 설정 (프로젝트 ID, 데이터셋명 등)
- [ ] 로컬에서 함수 테스트
- [ ] Cloud Functions 배포
- [ ] 배포 스크립트 작성

**상태**: 🔴 미시작  
**완료일**: -  
**비고**: -

**검증 항목**:
- [ ] 함수 배포 성공
- [ ] GCS에서 HTML 읽기 확인
- [ ] BigQuery 적재 확인
- [ ] 중복 실행 시 데이터 중복 방지 확인

**산출물**:
- [ ] Cloud Functions 코드 (Transform) - `functions/transform_function/`
- [ ] 배포 스크립트
- [ ] 테스트 결과

---

### 2.6 Cloud Scheduler 설정
**목표**: 주 1회 자동 실행 스케줄 설정

- [ ] Cloud Scheduler 작업 생성
- [ ] Extract 함수 호출 스케줄 설정 (예: 매주 월요일 오전 9시)
- [ ] Transform 함수 호출 스케줄 설정 (Extract 이후 약간의 지연)
- [ ] 또는 Pub/Sub를 통한 함수 체이닝 구성
- [ ] 스케줄 설정 스크립트 작성
- [ ] 수동 실행 테스트

**상태**: 🔴 미시작  
**완료일**: -  
**비고**: -

**검증 항목**:
- [ ] 스케줄러 작업 생성 확인
- [ ] 수동 실행 테스트
- [ ] 스케줄 설정 확인

**산출물**:
- [ ] Cloud Scheduler 설정 문서
- [ ] 스케줄 설정 스크립트

---

### 2.7 GitHub Actions CI/CD 구축
**목표**: 코드 배포 자동화

- [ ] GitHub Actions 워크플로우 파일 생성 (`.github/workflows/deploy.yml`)
- [ ] GCP 인증 설정 (서비스 계정 키 또는 Workload Identity)
- [ ] Cloud Functions 배포 자동화
- [ ] BigQuery 스키마 변경 시 자동 적용 (선택사항)
- [ ] CI/CD 문서 작성

**상태**: 🔴 미시작  
**완료일**: -  
**비고**: -

**검증 항목**:
- [ ] GitHub에 푸시 시 자동 배포 확인
- [ ] 배포 로그 확인

**산출물**:
- [ ] `.github/workflows/deploy.yml`
- [ ] CI/CD 문서

---

## Phase 3: 모니터링 및 최적화

### 3.1 로깅 및 모니터링
- [x] Cloud Monitoring API 활성화
- [x] Cloud Logging 확인 방법 문서화 (`docs/monitoring_guide.md`)
- [x] Cloud Monitoring 대시보드 설정 스크립트 작성
- [x] 모니터링 가이드 문서 작성
- [x] 로그 확인 스크립트 작성 (`scripts/setup_monitoring.sh`)
- [x] Cloud Monitoring 알림 정책 설정 완료

**상태**: 🟢 완료  
**완료일**: 2025-12-29  
**비고**: 
- Cloud Functions는 자동으로 Cloud Logging에 로그 기록
- 모니터링 대시보드 생성 스크립트 제공
- Alert Policy 설정 완료: "Pipeline Function Execution Failure"
- pipeline-function 및 data-validation-function ERROR 로그 감지
- 알림 채널: entrkjm@vaiv.kr, entrkjm@gmail.com

**검증 항목**:
- [x] Cloud Monitoring API 활성화 확인
- [x] Cloud Functions 로그 확인 가능
- [x] 모니터링 가이드 문서 작성 완료
- [x] Alert Policy 설정 완료
- [x] 알림 시스템 테스트 완료 (알림 수신 확인)

**산출물**:
- [x] `docs/monitoring_guide.md`: 모니터링 가이드 문서
- [x] `scripts/setup_monitoring.sh`: 모니터링 설정 스크립트
- [x] `scripts/create_monitoring_dashboard.sh`: 대시보드 생성 스크립트

---

### 3.2 비용 모니터링
- [x] GCP 사용량 대시보드 확인 방법 문서화 (`docs/cost_monitoring_guide.md`)
- [x] Always Free 범위 확인 스크립트 작성 (`scripts/check_free_tier_usage.sh`)
- [x] 비용 및 사용량 확인 스크립트 작성 (`scripts/check_cost_usage.sh`)
- [x] Always Free 범위 내 사용 확인

**상태**: 🟢 완료  
**완료일**: 2025-12-28  
**비고**: 
- Always Free 범위 내에서 운영 중
- BigQuery: 0.11MB (한도: 10GB)
- GCS: 1.22MB (한도: 5GB)
- Cloud Functions: 월 5회 실행 (한도: 200만 회)

**검증 항목**:
- [x] 비용 모니터링 가이드 문서 작성 완료
- [x] 사용량 확인 스크립트 작성 완료
- [x] Always Free 범위 확인 완료

**산출물**:
- [x] `docs/cost_monitoring_guide.md`: 비용 모니터링 가이드
- [x] `scripts/check_cost_usage.sh`: 사용량 확인 스크립트
- [x] `scripts/check_free_tier_usage.sh`: Always Free 범위 확인 스크립트

---

### 3.3 데이터 검증
- [x] 데이터 품질 검증 스크립트 작성 (`scripts/validate_data_quality.py`)
- [x] 데이터 검증 가이드 문서화 (`docs/data_validation_guide.md`)
- [x] 중복 레코드 확인 기능
- [x] Foreign Key 관계 확인 기능
- [x] 필수 필드 누락 확인 기능
- [x] 데이터 일관성 확인 기능
- [x] 검증 리포트 생성 기능
- [x] 데이터 검증 Cloud Function 배포 (`data-validation-function`)
- [x] 데이터 검증 스케줄러 설정 (매주 월요일 오전 10시)

**상태**: 🟢 완료  
**완료일**: 2025-12-29  
**비고**: 
- 모든 검증 항목 통과 확인
- 중복 레코드 없음
- Foreign Key 관계 정상
- 필수 필드 모두 존재

**검증 항목**:
- [x] 데이터 품질 검증 스크립트 작성 완료
- [x] 검증 가이드 문서 작성 완료
- [x] 실제 데이터 검증 실행 및 통과 확인

**산출물**:
- [x] `scripts/validate_data_quality.py`: 데이터 품질 검증 스크립트
- [x] `docs/data_validation_guide.md`: 데이터 검증 가이드

---

## 📝 진행 상황 업데이트 가이드

### 작업 시작 시
1. 해당 작업의 체크박스를 확인
2. 상태를 🟡 진행 중으로 변경
3. 시작일 기록

### 작업 완료 시
1. 모든 하위 체크박스 완료 표시
2. 상태를 🟢 완료로 변경
3. 완료일 기록
4. 진행률 자동 계산 및 업데이트

### 블로커 발생 시
1. 상태를 🔴 블로커로 변경
2. 비고에 블로커 내용 기록
3. 해결 방법 또는 대안 기록

### 상태 표시
- 🔴 미시작 / 블로커
- 🟡 진행 중
- 🟢 완료

---

## 🎯 다음 마일스톤

1. **Phase 1 완료**: 로컬에서 완전히 동작하는 파이프라인
2. **Phase 2.5 완료**: GCP에서 수동 실행 가능한 파이프라인
3. **Phase 2 완료**: 자동화된 파이프라인 (스케줄러 + CI/CD)
4. **Phase 3 완료**: 프로덕션 준비 완료

---

## 📌 참고 문서

### 계획 문서
- [`docs/planning/01_전체_구현_계획.md`](./docs/planning/01_전체_구현_계획.md): 상세 구현 계획
- [`docs/planning/02_로컬_테스트_계획.md`](./docs/planning/02_로컬_테스트_계획.md): 로컬 테스트 상세 계획
- [`docs/planning/03_GCP_배포_계획.md`](./docs/planning/03_GCP_배포_계획.md): GCP 배포 계획

### 가이드 문서
- [`docs/bigquery_schema.md`](./docs/bigquery_schema.md): BigQuery 스키마 문서
- [`docs/bigquery_tables_guide.md`](./docs/bigquery_tables_guide.md): BigQuery 테이블 사용 가이드
- [`docs/monitoring_guide.md`](./docs/monitoring_guide.md): 로깅 및 모니터링 가이드
- [`docs/cost_monitoring_guide.md`](./docs/cost_monitoring_guide.md): 비용 모니터링 가이드
- [`docs/data_validation_guide.md`](./docs/data_validation_guide.md): 데이터 검증 가이드

