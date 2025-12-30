# Setup 가이드

GCP 리소스 설정 및 초기화 가이드입니다.

---

## 📚 주요 가이드

### Alert Policy 설정

- **[alert_setup_complete_guide.md](./alert_setup_complete_guide.md)** ⭐ **메인 가이드**
  - Alert Policy 설정 완전 가이드
  - 실제 Cloud Console 화면 기준 단계별 설명
  - Cloud Function 실행 실패 및 Cloud Scheduler 작업 실패 감지 설정

- **[alert_setup_status.md](./alert_setup_status.md)** - 알림 설정 완료 상태 확인
  - 알림 채널 생성 상태
  - Alert Policy 설정 상태
  - 다음 단계 안내

---

## 📁 디렉토리 구조

```
docs/setup/
├── alert_setup_complete_guide.md  # 메인 가이드 (이것을 사용하세요!)
├── archive/                        # 아카이브된 가이드들
│   ├── alert_setup_manual.md
│   ├── alert_setup_guide.md
│   ├── alert_setup_simple_guide.md
│   └── ... (기타 중간 단계 가이드들)
└── README.md                       # 이 파일
```

---

## 🚀 빠른 시작

### Alert Policy 설정

1. [alert_setup_complete_guide.md](./alert_setup_complete_guide.md) 열기
2. 단계별로 따라하기
3. 두 개의 Alert Policy 생성:
   - Pipeline Function Execution Failure
   - Pipeline Scheduler Job Failure

---

## 📝 참고

- **메인 가이드**: `alert_setup_complete_guide.md`만 사용하시면 됩니다
- **아카이브**: 이전 버전이나 중간 단계 가이드는 `archive/` 폴더에 있습니다
- 필요시 아카이브에서 참고할 수 있습니다

---

## 🔗 관련 문서

- [Monitoring Guide](../monitoring/monitoring_guide.md) - 모니터링 전체 가이드
- [Alert Notification Guide](../monitoring/alert_notification_guide.md) - 알림 확인 방법

