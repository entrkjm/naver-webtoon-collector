# 파이프라인 실패 알림 설정 가이드

파이프라인이 실패하거나 데이터 수집이 제대로 되지 않을 때 알림을 받을 수 있도록 설정하는 방법입니다.

## 개요

이 알림 시스템은 다음 상황을 감지합니다:

1. **Cloud Function 실행 실패**: 파이프라인 Cloud Function이 오류로 종료된 경우
2. **Cloud Scheduler 작업 실패**: 스케줄러가 작업을 실행하지 못한 경우
3. **데이터 수집 실패**: 예상보다 적은 데이터가 수집되었거나 데이터가 없는 경우

## 설정 단계

### 1. 알림 채널 설정

먼저 알림을 받을 이메일 주소를 설정합니다:

```bash
export NOTIFICATION_CHANNEL_EMAIL="your-email@example.com"
```

### 2. Alert Policy 설정

Cloud Monitoring Alert Policy를 생성합니다:

```bash
cd scripts
./setup_alert_policies.sh
```

이 스크립트는 다음 Alert Policy를 생성합니다:
- **Pipeline Function Execution Failure**: Cloud Function 실행 실패 감지
- **Pipeline Scheduler Job Failure**: Cloud Scheduler 작업 실패 감지

### 3. 데이터 검증 Cloud Function 배포

데이터 수집 상태를 주기적으로 확인하는 Cloud Function을 배포합니다:

```bash
cd functions/data_validation_function
./deploy.sh
```

이 함수는 다음을 확인합니다:
- `fact_weekly_chart` 테이블에 예상 레코드 수 이상의 데이터가 있는지
- `fact_webtoon_stats` 테이블에 예상 레코드 수 이상의 데이터가 있는지
- 최근 48시간 이내에 데이터가 수집되었는지

### 4. 데이터 검증 Scheduler 설정

데이터 검증 함수를 주기적으로 실행하는 Scheduler를 설정합니다:

```bash
cd scripts
./setup_data_validation_scheduler.sh
```

기본적으로 매주 월요일 오전 10시에 실행됩니다. 스케줄을 변경하려면 `SCHEDULE` 환경 변수를 설정하세요:

```bash
export SCHEDULE="0 10 * * 1"  # 매주 월요일 오전 10시
./setup_data_validation_scheduler.sh
```

## 알림 동작 방식

### 1. Cloud Function/Scheduler 실패 알림

- Cloud Monitoring이 자동으로 실패를 감지
- Alert Policy가 트리거되면 설정된 이메일로 알림 전송
- 알림은 1시간에 최대 1회로 제한됨 (중복 알림 방지)

### 2. 데이터 수집 실패 알림

- 데이터 검증 Cloud Function이 주기적으로 실행
- 예상 레코드 수보다 적거나 데이터가 없으면:
  - Cloud Logging에 ERROR 레벨 로그 기록
  - Cloud Monitoring Alert Policy가 자동으로 감지하여 알림 전송

## 수동 테스트

### 데이터 검증 함수 테스트

```bash
# 함수 URL 가져오기
FUNCTION_URL=$(gcloud functions describe data-validation-function \
    --gen2 \
    --region=asia-northeast3 \
    --format="value(serviceConfig.uri)")

# 수동 실행
curl -X POST "$FUNCTION_URL" \
    -H "Content-Type: application/json" \
    -d '{"date": "2025-12-28"}'
```

### Alert Policy 확인

```bash
# Alert Policy 목록 확인
gcloud alpha monitoring policies list

# 알림 채널 확인
gcloud alpha monitoring channels list
```

## 알림 메시지 예시

### Cloud Function 실패 알림

```
제목: Pipeline Function Execution Failure

내용:
Cloud Function 'pipeline-function' 실행 중 오류가 발생했습니다.
시간: 2025-12-28 16:00:00
```

### 데이터 수집 실패 알림

```
제목: 파이프라인 데이터 수집 실패 - 2025-12-28

내용:
날짜: 2025-12-28

오류:
- fact_weekly_chart: 예상 레코드 수(700)보다 적습니다. 실제: 0개
- fact_webtoon_stats: 2025-12-28 데이터가 없습니다.
```

## 설정 확인

### 모든 Alert Policy 확인

```bash
gcloud alpha monitoring policies list \
    --filter="displayName:pipeline OR displayName:Pipeline"
```

### 데이터 검증 Scheduler 확인

```bash
gcloud scheduler jobs describe data-validation-scheduler \
    --location=asia-northeast3
```

### 최근 알림 확인

```bash
# Cloud Console에서 확인:
# https://console.cloud.google.com/monitoring/alerting?project=naver-webtoon-collector
```

## 문제 해결

### 알림이 오지 않는 경우

1. **알림 채널 확인**
   ```bash
   gcloud alpha monitoring channels list
   ```

2. **Alert Policy 상태 확인**
   ```bash
   gcloud alpha monitoring policies list
   ```

3. **Cloud Logging 확인**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit=50
   ```

### 데이터 검증 함수가 실행되지 않는 경우

1. **Scheduler 상태 확인**
   ```bash
   gcloud scheduler jobs describe data-validation-scheduler --location=asia-northeast3
   ```

2. **수동 실행 테스트**
   ```bash
   gcloud scheduler jobs run data-validation-scheduler --location=asia-northeast3
   ```

3. **함수 로그 확인**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=data-validation-function" --limit=50
   ```

## 비용 고려사항

- Cloud Monitoring Alert Policy: Always Free 범위 내
- 데이터 검증 Cloud Function: 주 1회 실행 시 약 $0.0001/월 (무료 범위 내)
- Cloud Scheduler: 3개 작업까지 무료

## 참고

- [Cloud Monitoring 문서](https://cloud.google.com/monitoring/docs)
- [Cloud Scheduler 문서](https://cloud.google.com/scheduler/docs)
- [Alert Policy 설정 가이드](https://cloud.google.com/monitoring/alerts)

