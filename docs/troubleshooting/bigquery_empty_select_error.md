# BigQuery 빈 SELECT 쿼리 에러 분석

## 에러 내용

```
ERROR: Syntax error: SELECT list must not be empty at [1:9]
쿼리: SELECT  FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart` 
      WHERE chart_date = "2026-01-12" LIMIT 1000
```

## 에러 원인

**문제**: `SELECT` 뒤에 컬럼이 없음 (빈 SELECT 리스트)

**가능한 원인**:
1. **BigQuery 콘솔에서 직접 쿼리 실행 시 실수** (가장 가능성 높음)
   - 사용자가 BigQuery 콘솔에서 데이터 확인을 위해 쿼리를 작성하다가
   - `SELECT` 뒤에 컬럼을 선택하지 않고 실행
   - 에러 로그의 `principalEmail: entrkjm@gmail.com`과 `callerSuppliedUserAgent: Mozilla/5.0...`이 이를 뒷받침

2. **코드에서 생성된 쿼리** (확인 필요)
   - 현재 코드베이스에는 이런 빈 SELECT 쿼리를 생성하는 부분이 없음
   - 하지만 혹시 모를 다른 스크립트나 도구에서 생성했을 가능성

## 코드 확인 결과

### 현재 코드베이스 검색 결과

- ✅ `upload_bigquery.py`: MERGE 쿼리만 사용, 빈 SELECT 없음
- ✅ `data_validation_function`: `SELECT COUNT(*)` 등 정상 쿼리만 사용
- ✅ 다른 스크립트: 모두 정상적인 SELECT 쿼리 사용

**결론**: 코드에서 빈 SELECT 쿼리를 생성하는 부분은 **없습니다**.

## Alert가 안 온 이유

### Alert Policy 설정 확인

현재 설정된 Alert Policy:
- **Pipeline Function Execution Failure**
  - 조건: `pipeline-function`에서 `ERROR` 로그 발생
  - 리소스 타입: `Cloud Function` (Cloud Run Revision)
  - 로그 필터: `severity=ERROR` AND `function_name=pipeline-function`

### 왜 Alert가 안 왔는가?

1. **에러 로그 타입이 다름**
   - 이 에러는 **BigQuery Audit Log** (`cloudaudit.googleapis.com/data_access`)
   - Alert Policy는 **Cloud Functions 로그**만 감지
   - BigQuery 쿼리 에러는 Cloud Functions 로그가 아니므로 감지되지 않음

2. **리소스 타입이 다름**
   - 에러 로그의 `resource.type`: `bigquery_resource`
   - Alert Policy의 리소스 타입: `cloud_run_revision` (Cloud Function)
   - 리소스 타입이 일치하지 않아 감지되지 않음

3. **로그 소스가 다름**
   - 에러 로그: BigQuery 서비스에서 발생
   - Alert Policy: Cloud Functions 서비스에서 발생하는 로그만 감지

## 해결 방법

### 1. BigQuery 쿼리 에러를 감지하려면 (선택사항)

BigQuery 쿼리 에러를 감지하는 별도의 Alert Policy를 생성할 수 있습니다:

```bash
# BigQuery 쿼리 에러 감지 Alert Policy 생성 (예시)
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="BigQuery Query Error" \
    --condition-display-name="BigQuery Error" \
    --condition-threshold-value=1 \
    --condition-threshold-duration=60s \
    --condition-filter='resource.type="bigquery_resource" AND severity="ERROR"'
```

**하지만 권장하지 않음**:
- BigQuery 콘솔에서 사용자가 직접 실행한 쿼리 에러까지 감지하면 알림이 너무 많아질 수 있음
- 실제 파이프라인 에러와 구분이 어려움

### 2. 현재 Alert Policy로 충분한 이유

현재 설정된 Alert Policy는 **파이프라인 실행 실패를 감지**하는 데 충분합니다:

- ✅ Cloud Functions 실행 실패 → Alert 발생
- ✅ 파이프라인 코드에서 BigQuery 쿼리 에러 발생 → Cloud Functions ERROR 로그 → Alert 발생
- ⚠️ BigQuery 콘솔에서 사용자가 직접 실행한 쿼리 에러 → Alert 없음 (의도된 동작)

### 3. 올바른 쿼리 예시

BigQuery 콘솔에서 데이터를 확인할 때는 다음처럼 쿼리를 작성하세요:

```sql
-- ✅ 올바른 쿼리
SELECT 
  chart_date,
  COUNT(*) AS record_count,
  COUNT(DISTINCT webtoon_id) AS unique_webtoons
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
WHERE chart_date = "2026-01-12"
GROUP BY chart_date
```

```sql
-- ❌ 잘못된 쿼리 (에러 발생)
SELECT  FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart` 
WHERE chart_date = "2026-01-12" LIMIT 1000
```

## 결론

1. **에러 원인**: BigQuery 콘솔에서 사용자가 직접 실행한 쿼리에서 `SELECT` 뒤에 컬럼을 선택하지 않음
2. **Alert가 안 온 이유**: Alert Policy는 Cloud Functions 로그만 감지하며, BigQuery Audit Log는 감지하지 않음
3. **대응**: 현재 Alert Policy 설정으로 충분하며, BigQuery 콘솔에서 쿼리 실행 시 주의 필요

## 참고

- [Alert Policy 설정 가이드](../setup/alert_setup_complete_guide.md)
- [BigQuery 쿼리 가이드](../reference/bigquery_tables_guide.md)
