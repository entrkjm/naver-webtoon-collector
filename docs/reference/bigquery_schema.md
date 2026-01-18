# BigQuery 스키마 문서

이 문서는 네이버 웹툰 수집 파이프라인의 BigQuery 데이터 모델 스키마를 설명합니다.

## 데이터셋 정보

- **프로젝트 ID**: `naver-webtoon-collector`
- **데이터셋 ID**: `naver_webtoon`
- **리전**: `asia-northeast3`
- **전체 경로**: `naver-webtoon-collector.naver_webtoon`

---

## 테이블 목록

### 1. `dim_webtoon` - 웹툰 마스터 테이블

**용도**: 웹툰의 기본 정보를 저장하는 마스터 테이블

**특징**:
- `webtoon_id`는 PRIMARY KEY 역할 (고유해야 함)
- Clustering: `webtoon_id`
- MERGE 작업으로 업데이트 지원

**스키마**:

| 컬럼명 | 타입 | 모드 | 설명 |
|--------|------|------|------|
| `webtoon_id` | STRING | REQUIRED | 웹툰 고유 ID (Primary Key) |
| `title` | STRING | REQUIRED | 웹툰 제목 |
| `author` | STRING | NULLABLE | 작가명 |
| `genre` | STRING | NULLABLE | 장르 |
| `tags` | ARRAY<STRING> | REPEATED | 태그 리스트 (배열) |
| `created_at` | TIMESTAMP | REQUIRED | 레코드 생성 시각 |
| `updated_at` | TIMESTAMP | REQUIRED | 레코드 수정 시각 |

**제약 조건**:
- `webtoon_id`는 고유해야 함 (애플리케이션 레벨에서 보장)
- MERGE 작업으로 중복 방지 및 업데이트 처리

**현재 상태**:
- 레코드 수: 737개
- 저장 용량: 약 0.05MB

---

### 2. `fact_weekly_chart` - 주간 차트 히스토리 테이블 ⭐ **가장 중요**

**용도**: 주간 차트 순위 히스토리를 저장하는 팩트 테이블

**특징**:
- Partitioning: `chart_date` (DATE 기준)
- Clustering: `webtoon_id`, `chart_date`
- 주 1회 데이터 수집

**스키마**:

| 컬럼명 | 타입 | 모드 | 설명 |
|--------|------|------|------|
| `chart_date` | DATE | REQUIRED | 수집 날짜 (Partition Key) |
| `webtoon_id` | STRING | REQUIRED | 웹툰 ID (Foreign Key → dim_webtoon) |
| `rank` | INTEGER | REQUIRED | 주간 차트 순위 (1 이상) |
| `collected_at` | TIMESTAMP | REQUIRED | 데이터 수집 시각 |
| `weekday` | STRING | NULLABLE | 요일 정보 (예: "MONDAY", "FRIDAY") |
| `year` | INTEGER | REQUIRED | 연도 |
| `month` | INTEGER | REQUIRED | 월 |
| `week` | INTEGER | REQUIRED | 해당 월의 몇 번째 주 |
| `view_count` | INTEGER | NULLABLE | 조회수 |

**제약 조건**:
- `(chart_date, webtoon_id, weekday)` 조합은 고유해야 함
- `webtoon_id`는 `dim_webtoon.webtoon_id`에 존재해야 함 (Foreign Key)
- MERGE 작업으로 중복 방지

**현재 상태**:
- 레코드 수: 1,540개
- 파티션 수: 3개
- 저장 용량: 약 0.11MB
- 수집 날짜: 2025-12-27, 2025-12-28

---

### 3. `fact_webtoon_stats` - 웹툰 상세 정보 히스토리 테이블

**용도**: 웹툰 상세 정보(관심 수, 완결 여부 등) 히스토리

**특징**:
- Partitioning: `collected_at` (TIMESTAMP 기준, DATE로 변환)
- Clustering: `webtoon_id`, `collected_at`
- 웹툰 상세 정보 수집 시 데이터 저장

**스키마**:

| 컬럼명 | 타입 | 모드 | 설명 |
|--------|------|------|------|
| `webtoon_id` | STRING | REQUIRED | 웹툰 ID (Foreign Key → dim_webtoon) |
| `collected_at` | TIMESTAMP | REQUIRED | 데이터 수집 시각 (Partition Key) |
| `favorite_count` | INTEGER | NULLABLE | 관심 수 |
| `favorite_count_source` | STRING | NULLABLE | 데이터 소스 ("api" 또는 "html") |
| `finished` | BOOLEAN | NULLABLE | 완결 여부 |
| `rest` | BOOLEAN | NULLABLE | 휴재 여부 |
| `total_episode_count` | INTEGER | NULLABLE | 총 에피소드 수 |
| `year` | INTEGER | REQUIRED | 연도 |
| `month` | INTEGER | REQUIRED | 월 |
| `week` | INTEGER | REQUIRED | 해당 월의 몇 번째 주 |

**제약 조건**:
- `(webtoon_id, collected_at)` 조합은 고유해야 함
- `webtoon_id`는 `dim_webtoon.webtoon_id`에 존재해야 함 (Foreign Key)
- MERGE 작업으로 중복 방지

**현재 상태**:
- 레코드 수: 4개 (거의 없음 - 웹툰 상세 정보 수집 미구현)
- 파티션 수: 1개
- 저장 용량: 약 0.0MB

---

## 테이블 관계도

```
dim_webtoon (마스터)
    │
    ├─── fact_weekly_chart (차트 히스토리)
    │    └─── webtoon_id (FK)
    │
    └─── fact_webtoon_stats (상세 정보 히스토리)
         └─── webtoon_id (FK)
```

---

## 파티션 및 클러스터링 전략

### 파티션 전략

1. **fact_weekly_chart**: `chart_date` 기준 파티션
   - 날짜별로 파티션이 분리되어 쿼리 성능 향상
   - 오래된 파티션 삭제 용이

2. **fact_webtoon_stats**: `collected_at` 기준 파티션 (DATE 변환)
   - 수집 시각 기준으로 파티션 분리
   - 시간 기반 쿼리 최적화

### 클러스터링 전략

1. **dim_webtoon**: `webtoon_id` 클러스터링
   - 웹툰 ID 기준 조회 최적화

2. **fact_weekly_chart**: `webtoon_id`, `chart_date` 클러스터링
   - 웹툰별, 날짜별 조회 최적화

3. **fact_webtoon_stats**: `webtoon_id`, `collected_at` 클러스터링
   - 웹툰별, 시간별 조회 최적화

---

## 데이터 타입 설명

### STRING
- 텍스트 데이터
- 예: `webtoon_id`, `title`, `author`

### INTEGER
- 정수 데이터
- 예: `rank`, `view_count`, `year`, `month`, `week`

### DATE
- 날짜 데이터 (YYYY-MM-DD 형식)
- 예: `chart_date`

### TIMESTAMP
- 날짜 및 시간 데이터 (타임존 포함)
- 예: `created_at`, `updated_at`, `collected_at`

### BOOLEAN
- 참/거짓 값
- 예: `finished`, `rest`

### ARRAY<STRING>
- 문자열 배열 (REPEATED)
- 예: `tags` - 여러 태그를 배열로 저장

---

## 제약 조건 및 규칙

### Primary Key (애플리케이션 레벨)

- **dim_webtoon**: `webtoon_id` (고유)
- **fact_weekly_chart**: `(chart_date, webtoon_id, weekday)` (고유)
- **fact_webtoon_stats**: `(webtoon_id, collected_at)` (고유)

### Foreign Key (애플리케이션 레벨)

- **fact_weekly_chart.webtoon_id** → `dim_webtoon.webtoon_id`
- **fact_webtoon_stats.webtoon_id** → `dim_webtoon.webtoon_id`

### 데이터 무결성

- MERGE 작업으로 중복 방지
- 애플리케이션 레벨에서 Foreign Key 검증
- 데이터 검증 스크립트로 주기적 확인

---

## 스키마 생성 방법

### 1. 데이터셋 생성

```bash
bq mk --dataset --location=asia-northeast3 naver-webtoon-collector:naver_webtoon
```

### 2. 테이블 생성

```bash
# SQL 파일 실행
bq query --use_legacy_sql=false < scripts/setup_bigquery.sql
```

또는 BigQuery 콘솔에서 `scripts/setup_bigquery.sql` 파일의 내용을 직접 실행

---

## 스키마 변경 이력

### 2025-12-27
- 초기 스키마 생성
- `dim_webtoon`, `fact_weekly_chart`, `fact_webtoon_stats` 테이블 생성

### 2025-12-28
- `dim_webtoon`에 `author`, `genre`, `tags` 필드 추가
- `tags` 필드를 ARRAY<STRING> 타입으로 정의

---

## 참고 자료

- [BigQuery 데이터 타입](https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types)
- [파티션 및 클러스터링](https://cloud.google.com/bigquery/docs/clustered-tables)
- [MERGE 문](https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax#merge_statement)

