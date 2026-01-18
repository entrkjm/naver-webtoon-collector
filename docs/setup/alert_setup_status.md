# 알림 설정 완료 상태

## ✅ 완료된 작업

### 알림 채널 생성 완료

다음 두 개의 이메일 주소로 알림을 받을 수 있도록 알림 채널이 생성되었습니다:

1. **entrkjm@vaiv.kr**
   - 채널 ID: `projects/naver-webtoon-collector/notificationChannels/4064953618660246281`

2. **entrkjm@gmail.com**
   - 채널 ID: `projects/naver-webtoon-collector/notificationChannels/14681047802946022682`

## ⚠️ 다음 단계: Alert Policy 생성

Alert Policy는 Cloud Console에서 수동으로 생성해야 합니다.

### 빠른 설정 가이드

1. [Cloud Monitoring Alerting 페이지](https://console.cloud.google.com/monitoring/alerting?project=naver-webtoon-collector) 접속
2. "CREATE POLICY" 클릭
3. 다음 3개의 Alert Policy 생성:
   - **Pipeline Function Execution Failure**: Cloud Function 실행 실패 감지
   - **Pipeline Scheduler Job Failure**: Cloud Scheduler 작업 실패 감지
   - **Pipeline Data Collection Failure**: 데이터 수집 실패 감지 (선택사항)

### 상세 가이드

자세한 설정 방법은 [docs/alert_setup_manual.md](docs/alert_setup_manual.md)를 참고하세요.

## 알림이 오는 경우

다음 상황에서 두 이메일 주소로 알림이 전송됩니다:

1. **Cloud Function 실행 실패**
2. **Cloud Scheduler 작업 실패**
3. **데이터 수집 실패** (데이터 검증 함수 배포 후)

## 알림 채널 확인

```bash
gcloud alpha monitoring channels list \
    --format="table(displayName,labels.email_address)"
```

