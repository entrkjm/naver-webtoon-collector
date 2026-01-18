# weekday_rank 수집 현황 확인 결과

## 확인 결과

### ❌ weekday_rank는 기존에 수집되지 않았음

1. **로컬 CSV 파일 확인**:
   - 파일: `data/processed/fact_weekly_chart/2025-12-21_popular.csv`
   - 컬럼 목록: `chart_date, webtoon_id, rank, collected_at, weekday, year, month, week, view_count`
   - **`weekday_rank` 컬럼 없음**

2. **BigQuery 스키마 확인**:
   - 테이블: `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
   - **`weekday_rank` 컬럼 없음** (에러: "Unrecognized name: weekday_rank")

3. **코드 확인**:
   - `src/parse_api.py`: 방금 추가됨 (이전에는 없었음)
   - `src/models.py`: 방금 추가됨
   - `src/transform.py`: 방금 추가됨

### 결론

**기존 코드에는 `weekday_rank` 수집 로직이 없었고, 실제로도 수집되지 않았습니다.**

현재 코드에 추가한 것은 **새로운 기능**이며, 다음 작업이 필요합니다:

1. ✅ BigQuery 스키마에 `weekday_rank` 컬럼 추가
2. ✅ 기존 데이터 마이그레이션 (요일별 순위 재계산)
3. ✅ 이후 수집부터 `weekday_rank` 저장

---

## 수정 작업 내역

### 1. 코드 수정 (완료)
- `src/parse_api.py`: `weekday_rank=idx` 파라미터 추가
- `src/models.py`: `weekday_rank` 필드 추가
- `src/transform.py`: `weekday_rank` 저장 로직 추가
- `src/upload_bigquery.py`: MERGE 쿼리에 `weekday_rank` 추가

### 2. BigQuery 스키마 수정 (필요)
- `scripts/setup/add_weekday_rank_column.sql` 실행 필요

### 3. 기존 데이터 마이그레이션 (필요)
- 기존 데이터의 `weekday_rank` 재계산 및 업데이트
