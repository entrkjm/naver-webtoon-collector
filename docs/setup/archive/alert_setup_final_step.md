# Alert Policy 최종 단계 - Notifications and name

> **현재 단계**: 알림 채널 설정 및 이름 입력

---

## ✅ 현재 상태 확인

### 이미 설정된 항목

- ✅ **Notification Channels**: "Pipeline Alert Email 2 and Pipeline Alert Email 1"
  - 두 이메일 채널이 이미 선택되어 있습니다!
  - 추가 작업 불필요

---

## 📝 설정할 항목

### 1. Alert policy name (필수)

**"Alert policy name"** 입력란에 다음을 입력:

```
Pipeline Function Execution Failure
```

---

## 🔧 선택사항 (건너뛰어도 됨)

### Notification subject line
- 비워두거나 원하는 제목 입력
- 예: "파이프라인 실행 실패 알림"

### Notify on incident closure
- 체크하지 않아도 됨 (선택사항)
- 체크하면 문제가 해결되었을 때도 알림을 받습니다

### Documentation
- 비워두거나 추가 설명 입력 (선택사항)
- 예: "Cloud Function 'pipeline-function' 실행 중 오류 발생 시 알림"

### Policy Severity Level
- "No severity"로 두거나 원하는 심각도 선택 (선택사항)

---

## ✅ 최종 단계

### 설정 완료 후

1. **"Alert policy name"**에 `Pipeline Function Execution Failure` 입력
2. 하단의 **"Create Policy"** 버튼 클릭

---

## 🎯 요약

**현재 화면에서 해야 할 일:**

1. ✅ Notification Channels: 이미 선택됨 (확인만)
2. **Alert policy name 입력**: `Pipeline Function Execution Failure`
3. **"Create Policy"** 클릭

**선택사항 (건너뛰어도 됨):**
- Notification subject line
- Notify on incident closure
- Documentation
- Policy Severity Level

---

## 🚀 다음 Alert Policy

첫 번째 Alert Policy 생성 완료 후:

1. 다시 **"CREATE POLICY"** 클릭
2. 같은 과정 반복:
   - Metric: Cloud Scheduler Job → Job failed execution count
   - Filter: `job_id = naver-webtoon-weekly-collection`
   - Threshold: `0`
   - 알림 채널: 동일하게 선택
   - Alert name: `Pipeline Scheduler Job Failure`

---

## 💡 팁

- Notification Channels는 이미 선택되어 있으니 그대로 두면 됩니다
- Alert policy name만 입력하고 바로 "Create Policy"를 클릭해도 됩니다
- 나머지는 모두 선택사항입니다

