# Rank 편향 문제 및 해결 방안

## 문제 분석

### 현재 상황

1. **Rank 저장 방식**: `rank` 필드가 **통합 순위(global rank)**로 저장됨
   - 모든 요일의 웹툰을 합쳐서 1, 2, 3, ... 순위로 매김
   - 예: FRIDAY 1위 = 전체 1위, MONDAY 1위 = 전체 112위

2. **편향 문제**: 수집 시점의 요일에 따라 순위가 달라짐
   - 월요일에 수집 → 월요일 웹툰이 상위권
   - 금요일에 수집 → 금요일 웹툰이 상위권
   - 현재는 주 1회(월요일 자정) 수집 → 월요일 웹툰 편향

3. **데이터 예시**:
   ```
   2026-01-11 (일요일 수집):
   - FRIDAY 1위: 전체 1위 (광마회귀)
   - MONDAY 1위: 전체 112위 (만남어플 중독)
   
   2026-01-05 (월요일 수집):
   - MONDAY 1위: 전체 1위 (만남어플 중독)
   - FRIDAY 1위: 전체 646위 (광마회귀)
   ```

### 근본 원인

**코드 위치**: `src/parse_api.py` 92-105줄

```python
# 각 요일별로 순위를 매기고 데이터 추출
global_rank = 1
for weekday, items in weekday_groups.items():
    for idx, item in enumerate(items, start=1):
        webtoon_data = extract_webtoon_from_api_item(
            item, 
            rank=global_rank,  # ❌ 전체 순위로 저장
            weekday=weekday
        )
```

- `global_rank`는 모든 요일을 통합한 전체 순위
- 요일별 순위(`idx`)는 계산하지만 저장하지 않음

---

## 해결 방안

### 방안 1: 요일별 순위 컬럼 추가 (권장)

**BigQuery 스키마 수정**:
- `rank`: 통합 순위 유지 (기존 호환성)
- `weekday_rank`: 요일별 순위 추가 (새 컬럼)

**장점**:
- 기존 데이터와 호환
- 통합 순위와 요일별 순위 모두 활용 가능
- 집계 시 요일별 순위로 정확한 분석 가능

**단점**:
- 스키마 변경 필요
- 기존 데이터 마이그레이션 필요

### 방안 2: 수집 주기 변경 (필수)

**현재**: 주 1회 (매주 월요일 자정)
**변경**: 매일 수집

**이유**:
- 매일 수집해야 모든 요일의 정확한 순위를 얻을 수 있음
- 요일별 편향을 제거하고 일년간 평균/중위 순위 계산 가능

**스케줄 변경**:
```bash
# 현재: 0 0 * * 1 (매주 월요일 00:00 KST)
# 변경: 0 0 * * * (매일 00:00 KST)
```

### 방안 3: 집계 쿼리 (나중에 사용)

일년간 평균/중위 순위 계산:

```sql
-- 평균 순위로 집계
SELECT 
  webtoon_id,
  AVG(weekday_rank) AS avg_rank,
  PERCENTILE_CONT(weekday_rank, 0.5) OVER () AS median_rank,
  COUNT(*) AS collection_count
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
WHERE chart_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
GROUP BY webtoon_id
ORDER BY avg_rank ASC
```

---

## 구현 계획

### 1단계: 요일별 순위 컬럼 추가

1. **BigQuery 스키마 수정**
   - `weekday_rank` 컬럼 추가 (INTEGER, NULLABLE)
   - 기존 `rank`는 통합 순위로 유지

2. **코드 수정**
   - `parse_api.py`: 요일별 순위(`idx`) 저장
   - `models.py`: `weekday_rank` 필드 추가
   - `transform.py`: 요일별 순위 저장 로직 추가

3. **기존 데이터 마이그레이션**
   - 기존 데이터는 `weekday_rank = NULL`로 유지
   - 또는 BigQuery에서 `ROW_NUMBER()`로 재계산

### 2단계: 수집 주기 변경

1. **Cloud Scheduler 수정**
   - 스케줄: `0 0 * * 1` → `0 0 * * *` (매일 자정)
   - 또는 매일 오전 9시: `0 9 * * *`

2. **비용 고려**
   - 현재: 주 1회 = 월 4-5회
   - 변경: 매일 = 월 30-31회
   - Cloud Functions: 200만 요청/월 한도 내 (충분함)
   - BigQuery: 저장 용량 증가 (하지만 Always Free 범위 내)

### 3단계: 집계 쿼리 작성

1. **일년간 평균 순위**
2. **일년간 중위 순위**
3. **요일별 평균 순위**

---

## 즉시 조치 사항

### 1. 요일별 순위 컬럼 추가

**BigQuery 스키마 수정**:
```sql
ALTER TABLE `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
ADD COLUMN weekday_rank INTEGER;

-- 기존 데이터 마이그레이션 (요일별 순위 재계산)
UPDATE `naver-webtoon-collector.naver_webtoon.fact_weekly_chart` f
SET weekday_rank = (
  SELECT rn
  FROM (
    SELECT 
      webtoon_id,
      ROW_NUMBER() OVER (PARTITION BY chart_date, weekday ORDER BY rank) AS rn
    FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
    WHERE chart_date = f.chart_date AND weekday = f.weekday
  )
  WHERE webtoon_id = f.webtoon_id
)
WHERE weekday_rank IS NULL;
```

### 2. 코드 수정

**`src/parse_api.py` 수정**:
```python
# 각 요일별로 순위를 매기고 데이터 추출
for weekday, items in weekday_groups.items():
    for idx, item in enumerate(items, start=1):
        webtoon_data = extract_webtoon_from_api_item(
            item, 
            rank=global_rank,  # 통합 순위
            weekday=weekday,
            weekday_rank=idx   # ✅ 요일별 순위 추가
        )
```

### 3. 수집 주기 변경

**Cloud Scheduler 수정**:
```bash
# 기존 작업 삭제 후 재생성
gcloud scheduler jobs delete kakao-webtoon-weekly-collection \
  --location=asia-northeast3

# 매일 자정 실행으로 변경
gcloud scheduler jobs create http kakao-webtoon-daily-collection \
  --location=asia-northeast3 \
  --schedule="0 0 * * *" \
  --time-zone="Asia/Seoul" \
  --uri="https://pipeline-function-vod3sdldea-du.a.run.app" \
  --http-method=POST \
  --message-body='{"sort_types": ["popular", "view"]}'
```

---

## 참고사항

### 비용 영향

- **Cloud Functions**: 월 30-31회 실행 (한도: 200만 회/월) ✅ 충분
- **BigQuery**: 저장 용량 증가 (하지만 Always Free 범위 내)
- **GCS**: 원본 데이터 저장 용량 증가 (5GB 한도 내)

### 데이터 품질

- **현재**: 주 1회 수집 → 요일별 편향 있음
- **변경 후**: 매일 수집 → 정확한 요일별 순위, 일년간 평균/중위 순위 계산 가능

---

## 결론

1. ✅ **요일별 순위 컬럼 추가**: 정확한 요일별 순위 저장
2. ✅ **수집 주기 변경**: 매일 수집으로 편향 제거
3. ✅ **집계 쿼리**: 일년간 평균/중위 순위로 정확한 분석

이렇게 수정하면 정확한 웹툰 순위 분석이 가능합니다.
