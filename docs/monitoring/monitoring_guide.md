# 로깅 및 모니터링 가이드

이 문서는 네이버 웹툰 수집 파이프라인의 로깅 및 모니터링 방법을 설명합니다.

## 목차

1. [Cloud Logging](#cloud-logging)
2. [Cloud Monitoring](#cloud-monitoring)
3. [에러 알림 설정](#에러-알림-설정)
4. [로그 확인 방법](#로그-확인-방법)
5. [모니터링 메트릭](#모니터링-메트릭)

---

## Cloud Logging

Cloud Functions는 자동으로 Cloud Logging에 로그를 기록합니다.

### 로그 확인 방법

#### 1. Cloud Console에서 확인

1. [Cloud Logging 콘솔](https://console.cloud.google.com/logs) 접속
2. 리소스 타입: `Cloud Function` 선택
3. 함수명: `pipeline_function` 필터링
4. 로그 레벨: `ERROR`, `WARNING`, `INFO` 등 필터링 가능

#### 2. gcloud CLI로 확인

```bash
# 최근 50개 로그 확인
gcloud functions logs read pipeline_function \
  --gen2 \
  --region=asia-northeast3 \
  --limit=50

# 에러 로그만 확인
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=pipeline_function AND severity>=ERROR" \
  --limit=50 \
  --format=json
```

#### 3. 로그 쿼리 예시

```bash
# 특정 날짜의 로그 확인
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=pipeline_function AND timestamp>=\"2025-12-28T00:00:00Z\"" \
  --limit=100

# "ERROR" 키워드가 포함된 로그
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=pipeline_function AND textPayload=~\"ERROR\"" \
  --limit=50
```

---

## Cloud Monitoring

Cloud Monitoring을 통해 파이프라인의 성능과 상태를 모니터링할 수 있습니다.

### 주요 메트릭

1. **Cloud Functions 실행 횟수**
   - 메트릭: `cloudfunctions.googleapis.com/function/execution_count`
   - 목적: 파이프라인 실행 빈도 확인

2. **Cloud Functions 실행 시간**
   - 메트릭: `cloudfunctions.googleapis.com/function/execution_times`
   - 목적: 파이프라인 성능 모니터링

3. **Cloud Functions 에러율**
   - 메트릭: `cloudfunctions.googleapis.com/function/execution_count` (severity=ERROR)
   - 목적: 파이프라인 실패율 모니터링

4. **Cloud Scheduler 작업 상태**
   - 메트릭: `cloudscheduler.googleapis.com/job/execution_count`
   - 목적: 스케줄러 실행 상태 확인

5. **BigQuery 작업 수**
   - 메트릭: `bigquery.googleapis.com/job/num_in_flight`
   - 목적: BigQuery 작업 모니터링

6. **GCS 작업 수**
   - 메트릭: `storage.googleapis.com/api/request_count`
   - 목적: GCS 업로드 모니터링

### 대시보드 생성

Cloud Console에서 대시보드를 생성하여 주요 메트릭을 한눈에 확인할 수 있습니다.

1. [Cloud Monitoring 대시보드](https://console.cloud.google.com/monitoring/dashboards?project=naver-webtoon-collector) 접속
2. "CREATE DASHBOARD" 클릭
3. 다음 위젯 추가:
   - Cloud Functions 실행 횟수 (Line Chart)
   - Cloud Functions 실행 시간 (Line Chart)
   - Cloud Functions 에러율 (Line Chart)
   - Cloud Scheduler 작업 상태 (Line Chart)

---

## 에러 알림 설정

### Cloud Monitoring 알림 정책 생성

#### 1. Cloud Console에서 생성

1. [Cloud Monitoring 알림 정책](https://console.cloud.google.com/monitoring/alerting?project=naver-webtoon-collector) 접속
2. "CREATE POLICY" 클릭
3. 다음 조건 추가:

**조건 1: Cloud Functions 에러율**
- 메트릭: `cloudfunctions.googleapis.com/function/execution_count`
- 필터: `resource.function_name = "pipeline_function"` AND `severity = "ERROR"`
- 임계값: `> 0` (에러가 1개 이상 발생)

**조건 2: Cloud Functions 실행 시간 초과**
- 메트릭: `cloudfunctions.googleapis.com/function/execution_times`
- 필터: `resource.function_name = "pipeline_function"`
- 임계값: `> 3300초` (55분 초과, 타임아웃 3600초 대비 여유)

**조건 3: Cloud Scheduler 작업 실패**
- 메트릭: `cloudscheduler.googleapis.com/job/execution_count`
- 필터: `resource.job_id = "naver-webtoon-weekly-collection"` AND `status = "FAILED"`
- 임계값: `> 0`

4. 알림 채널 선택 (이메일, Slack 등)
5. 알림 정책 저장

#### 2. gcloud CLI로 생성 (고급)

```bash
# 알림 채널 생성 (이메일)
gcloud alpha monitoring channels create \
  --display-name="Webtoon Pipeline Alerts" \
  --type=email \
  --channel-labels=email_address="your-email@example.com"

# 알림 정책 생성 (예시)
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Pipeline Function Errors" \
  --condition-display-name="Error Count > 0" \
  --condition-threshold-value=1 \
  --condition-threshold-duration=0s
```

---

## 로그 확인 방법

### 1. Cloud Functions 로그

```bash
# 최근 로그 확인
gcloud functions logs read pipeline_function \
  --gen2 \
  --region=asia-northeast3 \
  --limit=50

# 실시간 로그 스트리밍
gcloud functions logs tail pipeline_function \
  --gen2 \
  --region=asia-northeast3
```

### 2. Cloud Scheduler 로그

```bash
# 스케줄러 실행 로그 확인
gcloud logging read "resource.type=cloud_scheduler_job AND resource.labels.job_id=naver-webtoon-weekly-collection" \
  --limit=50 \
  --format=json
```

### 3. BigQuery 로그

```bash
# BigQuery 작업 로그 확인
gcloud logging read "resource.type=bigquery_project AND jsonPayload.jobStatus.state=ERROR" \
  --limit=50
```

### 4. GCS 로그

```bash
# GCS 작업 로그 확인
gcloud logging read "resource.type=gcs_bucket AND resource.labels.bucket_name=naver-webtoon-raw" \
  --limit=50
```

---

## 모니터링 메트릭

### 주요 KPI (Key Performance Indicators)

1. **파이프라인 실행 성공률**
   - 목표: > 95%
   - 계산: (성공한 실행 수 / 전체 실행 수) * 100

2. **평균 실행 시간**
   - 목표: < 300초 (5분)
   - 메트릭: `cloudfunctions.googleapis.com/function/execution_times`

3. **데이터 수집량**
   - 목표: 주당 약 1,500개 웹툰 데이터
   - 확인: BigQuery에서 `fact_weekly_chart` 테이블 쿼리

4. **에러 발생 빈도**
   - 목표: 주당 < 1회
   - 메트릭: `cloudfunctions.googleapis.com/function/execution_count` (severity=ERROR)

### 모니터링 쿼리 예시

#### BigQuery에서 데이터 수집량 확인

```sql
-- 주간 데이터 수집량 확인
SELECT 
  DATE_TRUNC(chart_date, WEEK) AS week,
  COUNT(DISTINCT webtoon_id) AS webtoon_count,
  COUNT(*) AS total_records
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
GROUP BY week
ORDER BY week DESC
LIMIT 10;
```

#### Cloud Functions 실행 통계

```bash
# 최근 7일간 실행 통계
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=pipeline_function AND timestamp>=\"$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)\"" \
  --format="table(timestamp,severity,textPayload)" \
  --limit=1000
```

---

## 문제 해결

### 로그가 보이지 않는 경우

1. Cloud Logging API가 활성화되어 있는지 확인
2. 서비스 계정에 `logging.logWriter` 권한이 있는지 확인
3. 로그 보존 기간 확인 (기본 30일)

### 알림이 오지 않는 경우

1. 알림 채널이 올바르게 설정되어 있는지 확인
2. 알림 정책의 임계값이 적절한지 확인
3. 알림 채널의 이메일 주소 확인 (스팸 폴더 확인)

### 성능 문제 진단

1. Cloud Functions 실행 시간 로그 확인
2. BigQuery 쿼리 실행 시간 확인
3. GCS 업로드 속도 확인
4. 네트워크 지연 확인

---

## 참고 자료

- [Cloud Logging 문서](https://cloud.google.com/logging/docs)
- [Cloud Monitoring 문서](https://cloud.google.com/monitoring/docs)
- [Cloud Functions 모니터링](https://cloud.google.com/functions/docs/monitoring)
- [알림 정책 가이드](https://cloud.google.com/monitoring/alerts)

