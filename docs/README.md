# Documentation

네이버 웹툰 데이터 수집 파이프라인 프로젝트의 문서 모음입니다.

## 디렉토리 구조

```
docs/
├── setup/              # 설정 및 초기화 가이드
├── monitoring/         # 모니터링 및 알림 가이드
├── data_management/    # 데이터 관리 및 검증 가이드
├── reference/          # 참고 문서 (스키마, 테이블 가이드)
├── planning/           # 프로젝트 계획 문서
└── archive/            # 아카이브 문서
```

## Setup 가이드 (`setup/`)

GCP 리소스 설정 및 초기화 가이드입니다.

- **[alert_setup_complete_guide.md](setup/alert_setup_complete_guide.md)** ⭐ **메인 가이드** - Alert Policy 설정 완전 가이드
- **[alert_setup_status.md](setup/alert_setup_status.md)** - 알림 설정 완료 상태 확인
- **[README.md](setup/README.md)** - Setup 폴더 설명

### 빠른 시작

1. [Alert Setup Complete Guide](setup/alert_setup_complete_guide.md) - Alert Policy 설정 완전 가이드
2. [Alert Setup Status](setup/README_ALERT_SETUP.md) - 알림 설정 완료 상태 확인

## Monitoring 가이드 (`monitoring/`)

모니터링, 알림, 비용 관리 가이드입니다.

- **[alert_notification_guide.md](monitoring/alert_notification_guide.md)** - 알림 수신 설정 및 확인 가이드
- **[monitoring_guide.md](monitoring/monitoring_guide.md)** - Cloud Logging 및 Cloud Monitoring 사용 가이드
- **[cost_monitoring_guide.md](monitoring/cost_monitoring_guide.md)** - GCP 비용 모니터링 가이드
- **[README.md](monitoring/README.md)** - Monitoring 폴더 설명

### 주요 내용

- Cloud Logging 로그 확인 방법
- Cloud Monitoring 메트릭 확인 방법
- Alert Policy 설정 및 관리
- 비용 모니터링 및 Always Free 티어 관리

## Data Management 가이드 (`data_management/`)

데이터 관리, 검증, 품질 관리 가이드입니다.

- **[data_validation_guide.md](data_management/data_validation_guide.md)** - 데이터 검증 절차 및 방법
- **[data_collection_failure_policy.md](data_management/data_collection_failure_policy.md)** - 데이터 수집 실패 정책 및 처리 방법
- **[threshold_guide.md](data_management/threshold_guide.md)** - 데이터 검증 임계값 설정 및 추천 가이드 (통합)
- **[README.md](data_management/README.md)** - Data Management 폴더 설명

### 주요 내용

- 데이터 품질 검증 절차
- 데이터 수집 실패 감지 및 알림
- 임계값 설정 및 조정 방법

## Reference 문서 (`reference/`)

참고용 기술 문서입니다.

- **[bigquery_schema.md](reference/bigquery_schema.md)** - BigQuery 테이블 스키마 상세 정의
- **[bigquery_tables_guide.md](reference/bigquery_tables_guide.md)** - BigQuery 테이블 가이드 및 예제 쿼리
- **[README.md](reference/README.md)** - Reference 폴더 설명

### 주요 내용

- `dim_webtoon` 테이블 스키마
- `fact_weekly_chart` 테이블 스키마
- `fact_webtoon_stats` 테이블 스키마
- 각 테이블의 용도 및 예제 쿼리

## Planning 문서 (`planning/`)

프로젝트 계획 및 설계 문서입니다.

프로젝트 초기 계획 및 설계 문서가 포함되어 있습니다.

## Archive 문서 (`archive/`)

아카이브된 문서입니다.

과거 버전의 문서나 더 이상 사용하지 않는 문서가 포함되어 있습니다.

## 문서 읽기 순서

### 초기 설정 시

1. [Alert Setup Complete Guide](setup/alert_setup_complete_guide.md) - Alert Policy 설정
2. [Monitoring Guide](monitoring/monitoring_guide.md) - 모니터링 설정
3. [Cost Monitoring Guide](monitoring/cost_monitoring_guide.md) - 비용 모니터링 설정

### 운영 중

1. [Data Validation Guide](data_management/data_validation_guide.md) - 데이터 검증 방법
2. [Alert Notification Guide](monitoring/alert_notification_guide.md) - 알림 확인 방법
3. [BigQuery Tables Guide](reference/bigquery_tables_guide.md) - 데이터 조회 방법

### 문제 해결 시

1. [Data Collection Failure Policy](data_management/data_collection_failure_policy.md) - 데이터 수집 실패 처리
2. [Threshold Guide](data_management/threshold_guide.md) - 임계값 설정 및 조정
3. [Monitoring Guide](monitoring/monitoring_guide.md) - 로그 및 메트릭 확인

## 관련 스크립트

각 문서에 해당하는 스크립트는 `scripts/` 디렉토리에 있습니다:

- Setup 문서 → `scripts/setup/`
- Monitoring 문서 → `scripts/monitoring/`
- Data Management 문서 → `scripts/data_management/`

## 업데이트 이력

문서는 프로젝트 진행에 따라 지속적으로 업데이트됩니다. 최신 정보는 각 문서의 최종 수정일을 확인하세요.

