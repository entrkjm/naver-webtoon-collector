# 알림 설정 수동 가이드 (Cloud Console)

> **간단 버전**: 빠르게 설정하고 싶다면 이 문서를 참고하세요.  
> **상세 버전**: 단계별로 자세히 알고 싶다면 [`alert_setup_step_by_step.md`](./alert_setup_step_by_step.md)를 참고하세요.

gcloud CLI로 Alert Policy 생성이 복잡하므로, Cloud Console을 통한 수동 설정 가이드를 제공합니다.

## 알림 채널 생성 완료

다음 두 개의 알림 채널이 이미 생성되었습니다:
- **entrkjm@vaiv.kr**: `projects/naver-webtoon-collector/notificationChannels/4064953618660246281`
- **entrkjm@gmail.com**: `projects/naver-webtoon-collector/notificationChannels/14681047802946022682`

## Alert Policy 수동 생성

### 1. Cloud Console 접속

1. [Cloud Monitoring Alerting 페이지](https://console.cloud.google.com/monitoring/alerting?project=naver-webtoon-collector) 접속
2. "CREATE POLICY" 클릭

### 2. Alert Policy 1: Cloud Function 실행 실패

**조건 설정**:
- **Resource type**: Cloud Run Revision
- **Metric**: Log entries
- **Filter**: 
  ```
  resource.type="cloud_run_revision"
  resource.labels.service_name="pipeline-function"
  severity="ERROR"
  ```
- **Condition**: Any time series violates
- **Threshold**: > 0
- **Duration**: 1 minute

**알림 채널**:
- ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
- ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)

**정책 이름**: `Pipeline Function Execution Failure`

### 3. Alert Policy 2: Cloud Scheduler 작업 실패

**조건 설정**:
- **Resource type**: Cloud Scheduler Job
- **Metric**: Job failed execution count
- **Filter**: 
  ```
  resource.type="cloud_scheduler_job"
  resource.labels.job_id="naver-webtoon-weekly-collection"
  ```
- **Condition**: Any time series violates
- **Threshold**: > 0
- **Duration**: 1 minute

**알림 채널**:
- ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
- ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)

**정책 이름**: `Pipeline Scheduler Job Failure`

### 4. Alert Policy 3: 데이터 검증 실패 (선택사항)

데이터 검증 함수가 ERROR 로그를 기록하면 자동으로 감지됩니다.

**조건 설정**:
- **Resource type**: Cloud Run Revision
- **Metric**: Log entries
- **Filter**: 
  ```
  resource.type="cloud_run_revision"
  resource.labels.service_name="data-validation-function"
  severity="ERROR"
  textPayload=~"파이프라인 데이터 수집 실패"
  ```
- **Condition**: Any time series violates
- **Threshold**: > 0
- **Duration**: 1 minute

**알림 채널**:
- ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
- ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)

**정책 이름**: `Pipeline Data Collection Failure`

## 알림 테스트

### 수동 테스트

1. **Cloud Function에 테스트 ERROR 로그 기록**:
```bash
gcloud logging write test-error-log \
    "테스트 에러 메시지" \
    --severity=ERROR \
    --resource-type=cloud_run_revision \
    --resource-labels.service_name=pipeline-function
```

2. **Alert Policy가 트리거되는지 확인** (약 1-2분 소요)

3. **이메일 확인**:
   - entrkjm@vaiv.kr
   - entrkjm@gmail.com

## 현재 설정된 알림 채널 확인

```bash
gcloud alpha monitoring channels list \
    --format="table(displayName,labels.email_address,name)"
```

## 참고

- 알림은 두 이메일 주소로 동시에 전송됩니다
- 알림은 실패 발생 시 즉시 전송됩니다
- 중복 알림 방지를 위해 Cloud Monitoring이 자동으로 관리합니다

