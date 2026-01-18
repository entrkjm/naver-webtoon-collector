# Monitoring 가이드

모니터링, 알림, 비용 관리 가이드입니다.

---

## 📚 주요 가이드

### 알림 및 모니터링

- **[alert_notification_guide.md](./alert_notification_guide.md)** - 알림 수신 설정 및 확인 가이드
  - 알림이 어디로 오는지
  - 알림 확인 방법
  - 알림 테스트 방법

- **[monitoring_guide.md](./monitoring_guide.md)** - Cloud Logging 및 Cloud Monitoring 사용 가이드
  - 로그 확인 방법
  - 메트릭 확인 방법
  - Alert Policy 관리

- **[cost_monitoring_guide.md](./cost_monitoring_guide.md)** - GCP 비용 모니터링 가이드
  - 비용 확인 방법
  - Always Free 티어 관리
  - 비용 최적화 팁

---

## 🚀 빠른 시작

### 로그 확인

```bash
# Cloud Function 로그 확인
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=pipeline-function" --limit=50
```

### 메트릭 확인

[Cloud Monitoring 대시보드](https://console.cloud.google.com/monitoring/dashboards?project=naver-webtoon-collector)에서 확인

### 알림 확인

[Alerting 페이지](https://console.cloud.google.com/monitoring/alerting?project=naver-webtoon-collector)에서 Alert Policy 확인

---

## 🔗 관련 문서

- [Setup Guide](../setup/alert_setup_complete_guide.md) - Alert Policy 설정 가이드
- [Data Management Guide](../data_management/data_validation_guide.md) - 데이터 검증 가이드

