# Scripts 디렉토리

이 디렉토리에는 네이버 웹툰 데이터 수집 파이프라인을 위한 다양한 유틸리티 스크립트가 포함되어 있습니다.

## 디렉토리 구조

```
scripts/
├── setup/              # GCP 설정 및 초기화 스크립트
├── test/               # 테스트 스크립트
├── monitoring/         # 모니터링 및 비용 확인 스크립트
├── data_management/    # 데이터 관리 및 검증 스크립트
└── utils/              # 유틸리티 스크립트
```

## Setup 스크립트 (`setup/`)

GCP 리소스 설정 및 초기화를 위한 스크립트입니다.

### 필수 설정 (순서대로 실행)

1. **check_prerequisites.sh** - 사전 요구사항 확인
   ```bash
   ./scripts/setup/check_prerequisites.sh
   ```

2. **setup_gcp_apis.sh** - 필요한 GCP API 활성화
   ```bash
   ./scripts/setup/setup_gcp_apis.sh
   ```

3. **setup_service_account.sh** - 서비스 계정 생성 및 권한 설정
   ```bash
   ./scripts/setup/setup_service_account.sh
   ```

4. **setup_bigquery.sql** - BigQuery 데이터셋 및 테이블 생성
   ```bash
   bq query --use_legacy_sql=false < scripts/setup/setup_bigquery.sql
   ```

### 선택적 설정

5. **setup_scheduler.sh** - Cloud Scheduler 작업 생성
   ```bash
   ./scripts/setup/setup_scheduler.sh
   ```

6. **setup_alert_policies.sh** - Cloud Monitoring Alert Policy 설정
   ```bash
   export NOTIFICATION_CHANNEL_EMAILS="email1@example.com,email2@example.com"
   ./scripts/setup/setup_alert_policies.sh
   ```

7. **setup_data_validation_scheduler.sh** - 데이터 검증 스케줄러 설정
   ```bash
   ./scripts/setup/setup_data_validation_scheduler.sh
   ```

8. **setup_monitoring.sh** - Cloud Monitoring 설정
   ```bash
   ./scripts/setup/setup_monitoring.sh
   ```

## Test 스크립트 (`test/`)

각 컴포넌트의 기능을 테스트하는 스크립트입니다.

- **test_gcs_upload.sh** - GCS 업로드 기능 테스트
- **test_gcs_upload_data.py** - GCS 데이터 업로드 테스트
- **test_bigquery_upload.py** - BigQuery 업로드 기능 테스트
- **test_sorting.py** - 정렬 옵션 테스트
- **test_mobile_api.py** - 모바일 API 테스트

## Monitoring 스크립트 (`monitoring/`)

모니터링 및 비용 관리 스크립트입니다.

- **check_cost_usage.sh** - 현재 GCP 리소스 사용량 확인
- **check_free_tier_usage.sh** - Always Free 티어 사용량 확인
- **create_monitoring_dashboard.sh** - Cloud Monitoring 대시보드 생성

## Data Management 스크립트 (`data_management/`)

데이터 관리 및 검증 스크립트입니다.

- **validate_data_quality.py** - 데이터 품질 검증
- **verify_data.py** - 데이터 무결성 검증
- **delete_date_data.sh** - 특정 날짜 데이터 삭제
- **cleanup_temp_tables.sh** - BigQuery 임시 테이블 정리

## Utils 스크립트 (`utils/`)

일반 유틸리티 스크립트입니다.

- **check_pipeline_status.py** - 파이프라인 실행 상태 확인
- **run_pipeline_background.sh** - 백그라운드에서 파이프라인 실행
- **check_full_execution_status.sh** - 전체 실행 상태 확인
- **analyze_html_structure.py** - HTML 구조 분석

## 사용 예시

### 초기 설정

```bash
# 1. 사전 요구사항 확인
./scripts/setup/check_prerequisites.sh

# 2. GCP API 활성화
./scripts/setup/setup_gcp_apis.sh

# 3. 서비스 계정 설정
./scripts/setup/setup_service_account.sh

# 4. BigQuery 설정
bq query --use_legacy_sql=false < scripts/setup/setup_bigquery.sql

# 5. 스케줄러 설정
./scripts/setup/setup_scheduler.sh
```

### 데이터 관리

```bash
# 데이터 품질 검증
python scripts/data_management/validate_data_quality.py

# 특정 날짜 데이터 삭제
./scripts/data_management/delete_date_data.sh 2025-12-28

# 임시 테이블 정리
./scripts/data_management/cleanup_temp_tables.sh
```

### 모니터링

```bash
# 비용 사용량 확인
./scripts/monitoring/check_cost_usage.sh

# 무료 티어 사용량 확인
./scripts/monitoring/check_free_tier_usage.sh
```

## 참고 문서

- [Setup 가이드](../docs/setup/)
- [Monitoring 가이드](../docs/monitoring/)
- [Data Management 가이드](../docs/data_management/)
