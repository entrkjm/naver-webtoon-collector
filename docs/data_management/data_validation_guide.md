# 데이터 검증 가이드

이 문서는 네이버 웹툰 수집 파이프라인의 데이터 검증 방법을 설명합니다.

## 목차

1. [데이터 품질 검증](#데이터-품질-검증)
2. [일관성 검증](#일관성-검증)
3. [검증 리포트 생성](#검증-리포트-생성)
4. [자동화된 검증](#자동화된-검증)

---

## 데이터 품질 검증

### 1. 중복 레코드 확인

#### dim_webtoon 중복 확인
```sql
SELECT 
    webtoon_id,
    COUNT(*) AS count
FROM `naver-webtoon-collector.naver_webtoon.dim_webtoon`
GROUP BY webtoon_id
HAVING COUNT(*) > 1
```

**예상 결과**: 0개 (중복 없어야 함)

#### fact_weekly_chart 중복 확인
```sql
SELECT 
    chart_date,
    webtoon_id,
    weekday,
    COUNT(*) AS count
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
GROUP BY chart_date, webtoon_id, weekday
HAVING COUNT(*) > 1
```

**예상 결과**: 0개 (중복 없어야 함)

### 2. Foreign Key 관계 확인

#### fact_weekly_chart의 webtoon_id가 dim_webtoon에 존재하는지 확인
```sql
SELECT 
    f.webtoon_id,
    COUNT(*) AS orphan_count
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart` f
LEFT JOIN `naver-webtoon-collector.naver_webtoon.dim_webtoon` d
    ON f.webtoon_id = d.webtoon_id
WHERE d.webtoon_id IS NULL
GROUP BY f.webtoon_id
```

**예상 결과**: 0개 (모든 webtoon_id가 dim_webtoon에 존재해야 함)

### 3. 필수 필드 누락 확인

#### dim_webtoon 필수 필드 확인
```sql
SELECT 
    COUNT(*) AS missing_count
FROM `naver-webtoon-collector.naver_webtoon.dim_webtoon`
WHERE webtoon_id IS NULL OR title IS NULL
```

**예상 결과**: 0개

#### fact_weekly_chart 필수 필드 확인
```sql
SELECT 
    COUNT(*) AS missing_count
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
WHERE chart_date IS NULL OR webtoon_id IS NULL OR rank IS NULL
```

**예상 결과**: 0개

### 4. 데이터 타입 검증

#### rank가 양수인지 확인
```sql
SELECT 
    COUNT(*) AS invalid_count
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
WHERE rank <= 0
```

**예상 결과**: 0개

#### chart_date가 유효한 날짜인지 확인
```sql
SELECT 
    COUNT(*) AS invalid_count
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
WHERE chart_date < '2020-01-01' OR chart_date > CURRENT_DATE()
```

**예상 결과**: 0개 (또는 예상 범위 내)

---

## 일관성 검증

### 1. 주간 데이터 수집 확인

#### 최근 4주간 데이터 수집 현황
```sql
SELECT 
    chart_date,
    COUNT(DISTINCT webtoon_id) AS webtoon_count,
    COUNT(*) AS total_records
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
WHERE chart_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 28 DAY)
GROUP BY chart_date
ORDER BY chart_date DESC
```

**예상 결과**: 주당 약 1,500개 웹툰 데이터

### 2. 데이터 증가 추이 확인

#### 월별 데이터 수집 추이
```sql
SELECT 
    DATE_TRUNC(chart_date, MONTH) AS month,
    COUNT(DISTINCT webtoon_id) AS webtoon_count,
    COUNT(*) AS total_records
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
GROUP BY month
ORDER BY month DESC
```

### 3. 웹툰 수 일관성 확인

#### 주간 웹툰 수 변동 확인
```sql
SELECT 
    chart_date,
    COUNT(DISTINCT webtoon_id) AS webtoon_count
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
GROUP BY chart_date
ORDER BY chart_date DESC
LIMIT 10
```

**예상 결과**: 주간 웹툰 수가 크게 변동하지 않아야 함 (약 1,500개 ± 100개)

---

## 검증 리포트 생성

### 스크립트 사용

```bash
# 데이터 품질 검증 실행
python scripts/validate_data_quality.py
```

### 검증 항목

1. ✅ dim_webtoon 중복 레코드 확인
2. ✅ fact_weekly_chart 중복 레코드 확인
3. ✅ Foreign Key 관계 확인
4. ✅ 필수 필드 누락 확인
5. ✅ 데이터 일관성 확인

### 리포트 예시

```
============================================================
데이터 품질 검증 리포트
============================================================
✅ dim_webtoon 중복 레코드 없음
✅ fact_weekly_chart 중복 레코드 없음
✅ Foreign Key 관계 정상
✅ dim_webtoon 필수 필드 모두 존재
✅ fact_weekly_chart 필수 필드 모두 존재
최근 4주간 데이터 수집 현황:
  - 2025-12-28: 770개 웹툰, 770개 레코드
  - 2025-12-27: 770개 웹툰, 770개 레코드
평균 웹툰 수: 770개
============================================================
✅ 모든 검증 통과
============================================================
```

---

## 자동화된 검증

### Cloud Scheduler를 통한 주기적 검증

주 1회 데이터 검증을 자동으로 실행할 수 있습니다:

```bash
# Cloud Scheduler 작업 생성 (예시)
gcloud scheduler jobs create http data-validation-job \
  --location=asia-northeast3 \
  --schedule="0 10 * * 1" \
  --uri="https://YOUR_CLOUD_FUNCTION_URL" \
  --http-method=POST \
  --message-body='{"action": "validate"}'
```

### 알림 설정

검증 실패 시 알림을 받도록 설정:

1. Cloud Monitoring 알림 정책 생성
2. 검증 스크립트 실행 결과 모니터링
3. 실패 시 이메일/Slack 알림

---

## 문제 해결

### 중복 레코드 발견 시

1. 중복 원인 확인 (멱등성 로직 문제)
2. 중복 레코드 삭제:
   ```sql
   DELETE FROM `naver-webtoon-collector.naver_webtoon.dim_webtoon`
   WHERE webtoon_id IN (
       SELECT webtoon_id
       FROM (
           SELECT webtoon_id, ROW_NUMBER() OVER (PARTITION BY webtoon_id ORDER BY updated_at DESC) AS rn
           FROM `naver-webtoon-collector.naver_webtoon.dim_webtoon`
       )
       WHERE rn > 1
   )
   ```

### Foreign Key 위반 발견 시

1. 누락된 webtoon_id 확인
2. dim_webtoon에 레코드 추가 또는 fact_weekly_chart에서 삭제

### 데이터 일관성 문제 발견 시

1. 수집 파이프라인 로그 확인
2. 특정 날짜의 데이터 재수집
3. 데이터 수집 로직 점검

---

## 참고 자료

- [BigQuery 데이터 품질 가이드](https://cloud.google.com/bigquery/docs/data-quality)
- [데이터 검증 모범 사례](https://cloud.google.com/architecture/data-validation)

