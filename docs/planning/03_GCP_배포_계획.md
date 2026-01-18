# GCP 배포 계획

> **작성일**: 2025-12-21  
> **목표**: 로컬에서 동작하는 파이프라인을 GCP에서 자동 실행되도록 구축

---

## 📋 배포 전 체크리스트

### 현재 상태
- ✅ 로컬 파이프라인 완전 동작 확인
- ✅ 데이터 모델 설계 완료 (dim_webtoon, fact_weekly_chart, fact_webtoon_stats)
- ✅ 멱등성 보장 로직 구현 완료
- ✅ 웹툰 상세 정보 수집 기능 포함

### 필요한 준비사항
- [ ] GCP 프로젝트 생성 또는 기존 프로젝트 확인
- [ ] gcloud CLI 설치 및 인증
- [ ] 결제 계정 연결 (Always Free 사용을 위해 필요)
- [ ] GitHub 저장소 준비 (CI/CD용)

---

## 🎯 Phase 2 단계별 작업

### 2.1 GCP 프로젝트 설정 (우선순위: 최우선)

**목표**: GCP 환경 준비

**작업 내용**:
1. GCP 프로젝트 생성/확인
   ```bash
   gcloud projects list
   # 또는 새 프로젝트 생성
   gcloud projects create PROJECT_ID --name="네이버 웹툰 수집기"
   ```

2. 필요한 API 활성화
   - Cloud Functions API
   - Cloud Scheduler API
   - BigQuery API
   - Cloud Storage API
   - Cloud Build API (CI/CD용)

3. 서비스 계정 생성 및 권한 설정
   - Cloud Functions 실행용 서비스 계정
   - BigQuery, GCS 접근 권한 부여

4. 로컬 인증 설정
   ```bash
   gcloud auth login
   gcloud config set project PROJECT_ID
   ```

**검증**:
- [ ] `gcloud projects list`로 프로젝트 확인
- [ ] API 활성화 상태 확인
- [ ] 서비스 계정 생성 확인

**산출물**:
- GCP 프로젝트 ID
- 서비스 계정 이메일
- API 활성화 확인 스크립트

---

### 2.2 BigQuery 데이터 모델 구축

**목표**: 데이터 저장소 스키마 생성

**작업 내용**:
1. BigQuery 데이터셋 생성
   - 데이터셋명: `naver_webtoon` (또는 사용자 지정)

2. 테이블 생성 (3개)
   - `dim_webtoon`: 웹툰 마스터 테이블
   - `fact_weekly_chart`: 주간 차트 히스토리 (파티션: chart_date)
   - `fact_webtoon_stats`: 웹툰 상세 정보 히스토리 (파티션: collected_at)

3. 스키마 정의 파일 작성
   - `scripts/setup_bigquery.sql` 생성

4. 샘플 데이터로 검증

**스키마 특징**:
- `fact_weekly_chart`: `chart_date` 기준 파티션
- `fact_webtoon_stats`: `collected_at` 기준 파티션
- Foreign Key 관계: `webtoon_id` → `dim_webtoon.webtoon_id`

**검증**:
- [ ] 데이터셋 생성 확인
- [ ] 테이블 생성 확인
- [ ] 파티션 설정 확인
- [ ] 샘플 데이터 INSERT/SELECT 테스트

**산출물**:
- `scripts/setup_bigquery.sql`
- 테이블 생성 스크립트
- 스키마 문서

---

### 2.3 GCS 버킷 생성 및 테스트

**목표**: HTML 원본 저장소 구축

**작업 내용**:
1. GCS 버킷 생성
   - 버킷명: `naver-webtoon-raw` (또는 사용자 지정)
   - 리전: `asia-northeast3` (서울, Always Free 지원)

2. 버킷 권한 설정
   - Cloud Functions 서비스 계정에 읽기/쓰기 권한

3. 파일명 규칙 정의
   - `raw_html/YYYY-MM-DD/sort_{sort_type}/webtoon_chart.json` (API 응답)
   - `raw_html/YYYY-MM-DD/webtoon_detail/{webtoon_id}.json` (웹툰 상세 정보)

4. 로컬에서 업로드/다운로드 테스트

**검증**:
- [ ] 버킷 생성 및 접근 가능 여부
- [ ] 파일 업로드/다운로드 테스트
- [ ] 파일명 규칙 준수 확인

**산출물**:
- GCS 버킷 설정 문서
- 파일 업로드 테스트 스크립트

---

### 2.4 Cloud Functions 구현

**목표**: 파이프라인을 Cloud Functions로 포팅

**아키텍처 결정**:
현재 `run_pipeline.py`가 통합 파이프라인으로 구현되어 있으므로, **하나의 통합 함수**로 구현합니다.

**작업 내용**:
1. Cloud Functions 디렉토리 구조 생성
   ```
   functions/
   └── pipeline_function/
       ├── main.py          # Cloud Functions 진입점
       ├── requirements.txt # 의존성
       └── src/             # 로컬 src 모듈 복사/적응
   ```

2. 로컬 코드를 Cloud Functions로 포팅
   - `run_pipeline.py` 로직을 `main.py`로 이동
   - 파일 시스템 → GCS로 변경
   - CSV 저장 → BigQuery로 변경
   - 환경 변수 설정 (버킷명, 프로젝트 ID, 데이터셋명 등)

3. GCS 클라이언트 연동
   - HTML/JSON 원본 저장
   - 기존 파일 읽기 (멱등성 체크용)

4. BigQuery 클라이언트 연동
   - `dim_webtoon` 테이블에 INSERT/UPDATE
   - `fact_weekly_chart` 테이블에 INSERT (중복 체크)
   - `fact_webtoon_stats` 테이블에 INSERT (중복 체크)

5. HTTP 트리거 설정
   - Cloud Scheduler에서 호출 가능하도록

6. 로컬 테스트 (Functions Framework)
   ```bash
   functions-framework --target=main --port=8080
   ```

7. 배포
   ```bash
   gcloud functions deploy pipeline_function \
     --runtime python39 \
     --trigger-http \
     --entry-point main \
     --timeout 540s \
     --memory 512MB
   ```

**환경 변수**:
- `GCS_BUCKET_NAME`: GCS 버킷명
- `BIGQUERY_PROJECT_ID`: BigQuery 프로젝트 ID
- `BIGQUERY_DATASET_ID`: BigQuery 데이터셋 ID
- `NAVER_WEBTOON_API_BASE_URL`: API 베이스 URL (선택사항)

**검증**:
- [ ] 로컬 Functions Framework 테스트
- [ ] Cloud Functions 배포 성공
- [ ] 수동 HTTP 트리거 테스트
- [ ] GCS에 파일 저장 확인
- [ ] BigQuery에 데이터 적재 확인
- [ ] 멱등성 동작 확인 (같은 날짜 재실행)

**산출물**:
- `functions/pipeline_function/main.py`
- `functions/pipeline_function/requirements.txt`
- 배포 스크립트
- 테스트 결과

---

### 2.5 Cloud Scheduler 설정

**목표**: 주 1회 자동 실행

**작업 내용**:
1. Cloud Scheduler 작업 생성
   - 작업명: `naver-webtoon-weekly-collection`
   - 스케줄: 매주 월요일 오전 9시 (KST)
   - 타겟: Cloud Functions HTTP 트리거 URL
   - HTTP 메서드: POST
   - 페이로드: `{"date": "AUTO"}` (또는 빈 페이로드)

2. 인증 설정
   - Cloud Functions에 인증 없이 접근 가능하도록 설정
   - 또는 서비스 계정 인증 설정

3. 수동 실행 테스트
   ```bash
   gcloud scheduler jobs run naver-webtoon-weekly-collection
   ```

**검증**:
- [ ] 스케줄러 작업 생성 확인
- [ ] 수동 실행 테스트 성공
- [ ] 스케줄 설정 확인 (다음 실행 시간 확인)

**산출물**:
- Cloud Scheduler 설정 문서
- 스케줄 설정 스크립트

---

### 2.6 GitHub Actions CI/CD 구축

**목표**: 코드 배포 자동화

**작업 내용**:
1. GitHub Actions 워크플로우 파일 생성
   - `.github/workflows/deploy.yml`

2. GCP 인증 설정
   - 옵션 1: 서비스 계정 키를 GitHub Secrets에 저장
   - 옵션 2: Workload Identity 연동 (권장, 더 안전)

3. 배포 워크플로우 구성
   - `main` 브랜치에 푸시 시 자동 배포
   - Cloud Functions 배포
   - BigQuery 스키마 변경 시 자동 적용 (선택사항)

4. 테스트 워크플로우 구성 (선택사항)
   - PR 시 테스트 실행

**검증**:
- [ ] GitHub에 푸시 시 자동 배포 확인
- [ ] 배포 로그 확인
- [ ] 배포 후 함수 동작 확인

**산출물**:
- `.github/workflows/deploy.yml`
- CI/CD 문서

---

## 🔄 배포 순서

1. **2.1 GCP 프로젝트 설정** ← **먼저 시작**
2. **2.2 BigQuery 데이터 모델 구축**
3. **2.3 GCS 버킷 생성 및 테스트**
4. **2.4 Cloud Functions 구현**
5. **2.5 Cloud Scheduler 설정**
6. **2.6 GitHub Actions CI/CD 구축**

---

## 📝 주요 고려사항

### Always Free 제약사항
- **Cloud Functions**: 200만 요청/월, 400,000GB-초/월
- **BigQuery**: 10GB 저장, 1TB 쿼리/월
- **GCS**: 5GB 저장, 5,000 Class A 작업/월
- **Cloud Scheduler**: 3개 작업 무료

### 비용 최적화
- Cloud Functions 타임아웃: 최소 필요 시간으로 설정
- BigQuery 파티션 활용으로 쿼리 비용 절감
- GCS 스토리지 클래스: Standard (Always Free 범위 내)

### 보안
- 서비스 계정 최소 권한 원칙
- 환경 변수로 민감 정보 관리
- GitHub Secrets로 인증 정보 관리

---

## 🚀 빠른 시작 가이드

### 1단계: GCP 프로젝트 설정
```bash
# 프로젝트 확인/생성
gcloud projects list
gcloud config set project PROJECT_ID

# API 활성화
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2단계: BigQuery 스키마 생성
```bash
# 데이터셋 생성
bq mk --dataset PROJECT_ID:naver_webtoon

# 테이블 생성 (SQL 파일 실행)
bq query --use_legacy_sql=false < scripts/setup_bigquery.sql
```

### 3단계: GCS 버킷 생성
```bash
# 버킷 생성
gsutil mb -p PROJECT_ID -c STANDARD -l asia-northeast3 gs://naver-webtoon-raw
```

### 4단계: Cloud Functions 배포
```bash
cd functions/pipeline_function
gcloud functions deploy pipeline_function \
  --runtime python39 \
  --trigger-http \
  --entry-point main \
  --timeout 540s \
  --memory 512MB \
  --set-env-vars GCS_BUCKET_NAME=naver-webtoon-raw,BIGQUERY_PROJECT_ID=PROJECT_ID,BIGQUERY_DATASET_ID=naver_webtoon
```

### 5단계: Cloud Scheduler 설정
```bash
gcloud scheduler jobs create http naver-webtoon-weekly-collection \
  --schedule="0 9 * * 1" \
  --time-zone="Asia/Seoul" \
  --uri="https://REGION-PROJECT_ID.cloudfunctions.net/pipeline_function" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{}'
```

---

## 📚 참고 문서

- [Cloud Functions Python 가이드](https://cloud.google.com/functions/docs/writing)
- [BigQuery 파티션 테이블](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [GCS Python 클라이언트](https://cloud.google.com/storage/docs/reference/libraries)
- [Cloud Scheduler 가이드](https://cloud.google.com/scheduler/docs)

---

## ✅ 완료 체크리스트

- [ ] 2.1 GCP 프로젝트 설정 완료
- [ ] 2.2 BigQuery 데이터 모델 구축 완료
- [ ] 2.3 GCS 버킷 생성 및 테스트 완료
- [ ] 2.4 Cloud Functions 구현 완료
- [ ] 2.5 Cloud Scheduler 설정 완료
- [ ] 2.6 GitHub Actions CI/CD 구축 완료
- [ ] 전체 파이프라인 자동 실행 확인
- [ ] 비용 모니터링 설정


