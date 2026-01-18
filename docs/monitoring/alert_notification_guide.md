# 알림 수신 설정 가이드

## 현재 알림 시스템 구조

알림은 **두 가지 방식**으로 전송됩니다:

### 1. Cloud Monitoring Alert Policy (자동 감지)

**작동 방식**:
1. Cloud Logging에 ERROR 레벨 로그가 기록됨
2. Alert Policy가 이를 감지
3. 설정된 이메일 주소로 알림 전송

**감지하는 상황**:
- Cloud Function 실행 실패 (ERROR 로그 발생)
- Cloud Scheduler 작업 실패
- 데이터 검증 함수에서 ERROR 로그 기록

**알림 수신처**: `NOTIFICATION_CHANNEL_EMAIL` 환경 변수로 설정한 이메일 주소

### 2. 데이터 검증 함수 직접 알림 (현재 미구현)

**현재 상태**: 
- `send_alert` 함수가 있지만 실제 이메일 전송은 TODO 상태
- 현재는 Cloud Logging에 ERROR 로그만 기록
- Alert Policy가 이 로그를 감지하여 알림 전송

**향후 개선**:
- SendGrid, Mailgun 등 이메일 서비스 연동
- 또는 Cloud Monitoring API를 통한 직접 알림 전송

---

## 알림 설정 방법

### 1단계: 이메일 주소 설정

```bash
export NOTIFICATION_CHANNEL_EMAIL="your-email@example.com"
```

### 2단계: Alert Policy 설정

```bash
cd scripts
./setup_alert_policies.sh
```

이 스크립트는:
1. 이메일 알림 채널 생성
2. Cloud Function 실행 실패 Alert Policy 생성
3. Cloud Scheduler 작업 실패 Alert Policy 생성

### 3단계: 데이터 검증 함수 배포

```bash
cd functions/data_validation_function
./deploy.sh
```

배포 시 `NOTIFICATION_CHANNEL_EMAIL` 환경 변수가 설정되어 있으면 함수에 전달됩니다.

---

## 알림 수신 확인

### 현재 설정된 알림 채널 확인

```bash
gcloud alpha monitoring channels list
```

### 현재 설정된 Alert Policy 확인

```bash
gcloud alpha monitoring policies list
```

### 알림 채널 상세 정보 확인

```bash
# 특정 채널 정보 확인
gcloud alpha monitoring channels describe CHANNEL_ID
```

---

## 알림이 오는 경우

### 1. Cloud Function 실행 실패

**조건**: `pipeline-function` Cloud Function에서 ERROR 레벨 로그 발생

**알림 내용**:
```
제목: Pipeline Function Execution Failure

내용:
Cloud Function 'pipeline-function' 실행 중 오류가 발생했습니다.
```

**수신처**: `NOTIFICATION_CHANNEL_EMAIL`로 설정한 이메일

### 2. Cloud Scheduler 작업 실패

**조건**: `naver-webtoon-weekly-collection` 스케줄러 작업 실패

**알림 내용**:
```
제목: Pipeline Scheduler Job Failure

내용:
Cloud Scheduler 작업 'naver-webtoon-weekly-collection'이 실패했습니다.
```

**수신처**: `NOTIFICATION_CHANNEL_EMAIL`로 설정한 이메일

### 3. 데이터 수집 실패

**조건**: 데이터 검증 함수가 ERROR 로그 기록

**알림 내용**:
```
제목: 파이프라인 데이터 수집 실패 - 2025-12-28

내용:
날짜: 2025-12-28

오류:
- fact_weekly_chart: 예상 레코드 수(500)보다 적습니다. 실제: 150개
- fact_webtoon_stats: 2025-12-28 데이터가 없습니다.
```

**수신처**: `NOTIFICATION_CHANNEL_EMAIL`로 설정한 이메일

---

## 알림이 오지 않는 경우 확인

### 1. 알림 채널이 설정되지 않았는지 확인

```bash
gcloud alpha monitoring channels list
```

채널이 없으면 `setup_alert_policies.sh`를 실행하세요.

### 2. Alert Policy가 생성되지 않았는지 확인

```bash
gcloud alpha monitoring policies list
```

Policy가 없으면 `setup_alert_policies.sh`를 실행하세요.

### 3. 이메일 주소 확인

```bash
# 알림 채널의 이메일 주소 확인
gcloud alpha monitoring channels describe CHANNEL_ID --format="value(labels.email_address)"
```

### 4. 스팸 폴더 확인

GCP 알림 이메일이 스팸 폴더로 이동했을 수 있습니다.

### 5. Alert Policy 상태 확인

```bash
# Alert Policy 상세 정보 확인
gcloud alpha monitoring policies describe POLICY_ID
```

---

## 알림 테스트

### 수동으로 알림 테스트

1. **데이터 검증 함수 수동 실행**:
```bash
# 함수 URL 가져오기
FUNCTION_URL=$(gcloud functions describe data-validation-function \
    --gen2 \
    --region=asia-northeast3 \
    --format="value(serviceConfig.uri)")

# 테스트 실행 (실패 시나리오)
curl -X POST "$FUNCTION_URL" \
    -H "Content-Type: application/json" \
    -d '{"date": "1999-01-01"}'  # 존재하지 않는 날짜
```

2. **Cloud Function에 ERROR 로그 강제 기록**:
```bash
# Cloud Function 로그에 ERROR 기록
gcloud logging write test-error-log \
    "테스트 에러 메시지" \
    --severity=ERROR \
    --resource-type=cloud_run_revision \
    --resource-labels.service_name=pipeline-function
```

---

## 알림 수신처 변경

### 기존 알림 채널 수정

```bash
# 알림 채널 ID 확인
CHANNEL_ID=$(gcloud alpha monitoring channels list \
    --filter="displayName:Pipeline Alert Email" \
    --format="value(name)" \
    --limit=1)

# 알림 채널 삭제
gcloud alpha monitoring channels delete "$CHANNEL_ID"

# 새 이메일로 알림 채널 재생성
export NOTIFICATION_CHANNEL_EMAIL="new-email@example.com"
cd scripts
./setup_alert_policies.sh
```

### 여러 이메일로 알림 받기

```bash
# 여러 알림 채널 생성
gcloud alpha monitoring channels create \
    --display-name="Pipeline Alert Email 1" \
    --type=email \
    --channel-labels=email_address="email1@example.com"

gcloud alpha monitoring channels create \
    --display-name="Pipeline Alert Email 2" \
    --type=email \
    --channel-labels=email_address="email2@example.com"

# Alert Policy에 여러 채널 추가 (수동으로 Cloud Console에서)
```

---

## 현재 상태 확인

### 알림 채널 확인

```bash
gcloud alpha monitoring channels list \
    --filter="displayName:Pipeline Alert Email" \
    --format="table(displayName,labels.email_address)"
```

### Alert Policy 확인

```bash
gcloud alpha monitoring policies list \
    --filter="displayName:pipeline OR displayName:Pipeline" \
    --format="table(displayName,notificationChannels)"
```

---

## 참고

- 알림은 **1시간에 최대 1회**로 제한됩니다 (중복 알림 방지)
- 알림 이메일은 GCP에서 자동으로 전송됩니다
- 이메일 주소는 Cloud Monitoring 알림 채널에 저장됩니다
- Alert Policy는 Cloud Logging의 ERROR 레벨 로그를 감지합니다

