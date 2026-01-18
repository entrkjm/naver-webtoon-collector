# Reference 문서

참고용 기술 문서입니다.

---

## 📚 주요 문서

### BigQuery

- **[bigquery_schema.md](./bigquery_schema.md)** - BigQuery 테이블 스키마 상세 정의
  - `dim_webtoon` 테이블 스키마
  - `fact_weekly_chart` 테이블 스키마
  - `fact_webtoon_stats` 테이블 스키마
  - 데이터 타입, 모드, 설명

- **[bigquery_tables_guide.md](./bigquery_tables_guide.md)** - BigQuery 테이블 가이드 및 예제 쿼리
  - 각 테이블의 용도
  - 예제 쿼리
  - 데이터 조회 방법

---

## 🚀 빠른 시작

### 스키마 확인

```bash
# 테이블 스키마 확인
bq show --schema --format=prettyjson naver-webtoon-collector:naver_webtoon.dim_webtoon
```

### 데이터 조회

```sql
-- 최근 수집된 데이터 확인
SELECT 
    COUNT(*) as total_records,
    MAX(chart_date) as latest_date
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
```

---

## 🔗 관련 문서

- [Data Management Guide](../data_management/data_validation_guide.md) - 데이터 검증 가이드
- [Setup Guide](../setup/alert_setup_complete_guide.md) - 설정 가이드

