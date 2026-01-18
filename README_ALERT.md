# 파이프라인 실패 알림 기능

파이프라인이 실패하거나 데이터 수집이 제대로 되지 않을 때 알림을 받을 수 있는 기능입니다.

## 빠른 시작

### 1단계: 알림 이메일 설정

```bash
export NOTIFICATION_CHANNEL_EMAIL="your-email@example.com"
```

### 2단계: Alert Policy 설정

```bash
cd scripts
./setup_alert_policies.sh
```

### 3단계: 데이터 검증 함수 배포

```bash
cd functions/data_validation_function
./deploy.sh
```

### 4단계: 데이터 검증 Scheduler 설정

```bash
cd scripts
./setup_data_validation_scheduler.sh
```

## 알림이 감지하는 상황

1. **Cloud Function 실행 실패**: 파이프라인 함수가 오류로 종료
2. **Cloud Scheduler 작업 실패**: 스케줄러가 작업 실행 실패
3. **데이터 수집 실패**: 예상보다 적은 데이터 또는 데이터 없음

## 상세 가이드

자세한 설정 방법은 [docs/alert_setup_guide.md](docs/alert_setup_guide.md)를 참고하세요.

