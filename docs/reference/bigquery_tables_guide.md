# BigQuery 테이블 가이드

이 문서는 네이버 웹툰 수집 파이프라인의 BigQuery 테이블 구조와 사용 방법을 설명합니다.

## 핵심 테이블 (확인해야 할 테이블)

### 1. `dim_webtoon` - 웹툰 마스터 테이블

**용도**: 웹툰의 기본 정보를 저장하는 마스터 테이블

**스키마**:
- `webtoon_id` (STRING, PRIMARY KEY): 웹툰 고유 ID
- `title` (STRING): 웹툰 제목
- `author` (STRING): 작가명
- `genre` (STRING): 장르
- `tags` (ARRAY<STRING>): 태그 리스트
- `created_at` (TIMESTAMP): 레코드 생성 시각
- `updated_at` (TIMESTAMP): 레코드 수정 시각

**확인 방법**:
```sql
-- 전체 웹툰 수 확인
SELECT COUNT(*) AS total_webtoons
FROM `naver-webtoon-collector.naver_webtoon.dim_webtoon`;

-- 최근 업데이트된 웹툰 확인
SELECT webtoon_id, title, author, genre, updated_at
FROM `naver-webtoon-collector.naver_webtoon.dim_webtoon`
ORDER BY updated_at DESC
LIMIT 10;
```

**현재 상태**: 737개 웹툰

---

### 2. `fact_weekly_chart` - 주간 차트 히스토리 테이블 ⭐ **가장 중요**

**용도**: 주간 차트 순위 히스토리를 저장하는 팩트 테이블

**스키마**:
- `chart_date` (DATE, PARTITION KEY): 수집 날짜
- `webtoon_id` (STRING, FOREIGN KEY): 웹툰 ID → dim_webtoon 참조
- `rank` (INTEGER): 주간 차트 순위
- `collected_at` (TIMESTAMP): 데이터 수집 시각
- `weekday` (STRING): 요일 정보
- `year` (INTEGER): 연도
- `month` (INTEGER): 월
- `week` (INTEGER): 해당 월의 몇 번째 주
- `view_count` (INTEGER): 조회수

**확인 방법**:
```sql
-- 최근 수집된 차트 데이터 확인
SELECT 
  chart_date,
  COUNT(DISTINCT webtoon_id) AS webtoon_count,
  COUNT(*) AS total_records
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
GROUP BY chart_date
ORDER BY chart_date DESC
LIMIT 10;

-- 특정 날짜의 상위 10개 웹툰 확인
SELECT 
  w.title,
  w.author,
  c.rank,
  c.view_count
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart` c
JOIN `naver-webtoon-collector.naver_webtoon.dim_webtoon` w
  ON c.webtoon_id = w.webtoon_id
WHERE c.chart_date = '2025-12-28'
ORDER BY c.rank
LIMIT 10;
```

**현재 상태**: 
- 총 1,540개 레코드
- 2개 날짜 (2025-12-27, 2025-12-28)
- 각 날짜당 770개 레코드 (737개 고유 웹툰)

---

### 3. `fact_webtoon_stats` - 웹툰 상세 정보 히스토리

**용도**: 웹툰 상세 정보(관심 수, 완결 여부 등) 히스토리

**스키마**:
- `webtoon_id` (STRING, FOREIGN KEY): 웹툰 ID
- `collected_at` (TIMESTAMP, PARTITION KEY): 데이터 수집 시각
- `favorite_count` (INTEGER): 관심 수
- `favorite_count_source` (STRING): 데이터 소스 (api/html)
- `finished` (BOOLEAN): 완결 여부
- `rest` (BOOLEAN): 휴재 여부
- `total_episode_count` (INTEGER): 총 에피소드 수
- `year` (INTEGER): 연도
- `month` (INTEGER): 월
- `week` (INTEGER): 해당 월의 몇 번째 주

**확인 방법**:
```sql
-- 웹툰 상세 정보 확인
SELECT 
  w.title,
  s.favorite_count,
  s.finished,
  s.collected_at
FROM `naver-webtoon-collector.naver_webtoon.fact_webtoon_stats` s
JOIN `naver-webtoon-collector.naver_webtoon.dim_webtoon` w
  ON s.webtoon_id = w.webtoon_id
ORDER BY s.collected_at DESC
LIMIT 10;
```

**현재 상태**: 4개 레코드 (거의 없음 - 웹툰 상세 정보 수집이 아직 구현되지 않음)

---

## 임시 테이블 (무시해도 됨)

### `*_temp_*` 테이블들

**용도**: BigQuery 업로드 시 MERGE 작업을 위한 임시 테이블

**특징**:
- MERGE 작업 후 자동으로 삭제되어야 함
- 하지만 일부 테이블이 남아있을 수 있음
- 데이터가 없거나 중복된 데이터일 수 있음

**정리 방법**:
```bash
# 임시 테이블 정리 스크립트 실행
./scripts/cleanup_temp_tables.sh
```

또는 수동으로:
```sql
-- 임시 테이블 목록 확인
SELECT table_id
FROM `naver-webtoon-collector.naver_webtoon.__TABLES__`
WHERE table_id LIKE '%temp%';

-- 임시 테이블 삭제 (예시)
DROP TABLE IF EXISTS `naver-webtoon-collector.naver_webtoon.dim_webtoon_temp_20251228103248`;
```

---

## Cloud Scheduler 실행 확인

### 실행 이력 확인

```bash
# Cloud Scheduler 실행 로그 확인
gcloud logging read "resource.type=cloud_scheduler_job AND resource.labels.job_id=naver-webtoon-weekly-collection" \
  --limit=10 \
  --format="table(timestamp,severity,jsonPayload.status.code)"
```

### 데이터 수집 확인

```sql
-- 최근 수집된 데이터 확인
SELECT 
  chart_date,
  COUNT(*) AS record_count,
  COUNT(DISTINCT webtoon_id) AS webtoon_count
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
GROUP BY chart_date
ORDER BY chart_date DESC;
```

**현재 상태**: 
- Cloud Scheduler가 정상 실행됨 (2025-12-28)
- 데이터가 BigQuery에 정상 반영됨
- 2개 날짜의 데이터 수집 완료 (2025-12-27, 2025-12-28)

---

## 주요 쿼리 예시

### 1. 주간 차트 순위 변동 추이

```sql
SELECT 
  chart_date,
  w.title,
  c.rank,
  LAG(c.rank) OVER (PARTITION BY c.webtoon_id ORDER BY chart_date) AS prev_rank,
  c.rank - LAG(c.rank) OVER (PARTITION BY c.webtoon_id ORDER BY chart_date) AS rank_change
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart` c
JOIN `naver-webtoon-collector.naver_webtoon.dim_webtoon` w
  ON c.webtoon_id = w.webtoon_id
WHERE c.chart_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 4 WEEK)
ORDER BY chart_date DESC, c.rank
LIMIT 100;
```

### 2. 장르별 웹툰 수

```sql
SELECT 
  genre,
  COUNT(*) AS webtoon_count
FROM `naver-webtoon-collector.naver_webtoon.dim_webtoon`
WHERE genre IS NOT NULL
GROUP BY genre
ORDER BY webtoon_count DESC;
```

### 3. 상위 랭킹 웹툰 추적

```sql
SELECT 
  w.title,
  w.author,
  c.chart_date,
  c.rank,
  c.view_count
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart` c
JOIN `naver-webtoon-collector.naver_webtoon.dim_webtoon` w
  ON c.webtoon_id = w.webtoon_id
WHERE c.rank <= 10
ORDER BY c.chart_date DESC, c.rank;
```

---

## 요약

**확인해야 할 테이블**:
1. ⭐ **`fact_weekly_chart`** - 주간 차트 데이터 (가장 중요)
2. `dim_webtoon` - 웹툰 마스터 정보
3. `fact_webtoon_stats` - 웹툰 상세 정보 (현재 거의 없음)

**무시해도 되는 테이블**:
- `*_temp_*` 테이블들 (임시 테이블, 정리 필요)

**현재 상태**:
- ✅ Cloud Scheduler 정상 실행
- ✅ BigQuery에 데이터 정상 반영
- ✅ 2개 날짜의 데이터 수집 완료

