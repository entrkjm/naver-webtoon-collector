# 두 번째 Alert Policy 생성 가이드

> **목표**: Cloud Scheduler 작업 실패 감지

---

## 🎯 Alert Policy 2: Cloud Scheduler 작업 실패

### 1단계: Alert Policy 생성 시작

1. **"CREATE POLICY"** 버튼 클릭 (또는 페이지 상단의 "+" 버튼)

### 2단계: Metric 선택

1. **"Select a metric"** 클릭
2. 왼쪽 리소스 목록에서 **"Cloud Scheduler Job"** 클릭
3. 나타나는 메트릭 목록에서 **"Job failed execution count"** 선택
4. **"Apply"** 버튼 클릭

### 3단계: Filter 추가

화면 오른쪽에 **"Resource labels"** 섹션이 나타나면:

1. **"Filter"** 입력 필드에 `job_id` 입력
2. **"Comparator"**: `=` 선택
3. **"Value"**: `naver-webtoon-weekly-collection` 입력
4. **"Done"** 버튼 클릭

### 4단계: Alert Condition 설정

1. 왼쪽 메뉴에서 **"Configure trigger"** 클릭
2. **Condition type**: `Threshold` (이미 선택됨)
3. **Alert trigger**: `Any time series violates` (이미 선택됨)
4. **Threshold position**: `Above threshold` (이미 선택됨)
5. **Threshold value**: `0` 입력
6. **Advanced Options** → **Duration**: `1 minute` 선택

### 5단계: 알림 채널 추가

1. 왼쪽 메뉴에서 **"Notifications and name"** 클릭
2. **"Notification Channels"** 클릭
3. 다음 2개 채널 모두 선택:
   - ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
   - ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)
4. **"OK"** 클릭

### 6단계: 이름 입력 및 저장

1. **"Alert policy name"** 입력란에:
   ```
   Pipeline Scheduler Job Failure
   ```
2. 하단의 **"Create Policy"** 버튼 클릭

✅ **두 번째 Alert Policy 완료!**

---

## ✅ 완료 확인

### 생성된 Alert Policy 확인

1. **"Policies"** 페이지로 이동
2. 다음 2개의 Alert Policy가 보여야 합니다:
   - ✅ Pipeline Function Execution Failure
   - ✅ Pipeline Scheduler Job Failure

### 명령어로 확인

```bash
gcloud alpha monitoring policies list \
    --format="table(displayName,notificationChannels)" \
    --filter="displayName:Pipeline"
```

---

## 🧪 테스트

### Alert Policy 테스트

설정이 제대로 되었는지 테스트:

```bash
# Cloud Function에 테스트 ERROR 로그 기록
gcloud logging write test-error-log \
    "테스트 에러 메시지 - Alert Policy 테스트" \
    --severity=ERROR \
    --resource-type=cloud_run_revision \
    --resource-labels.service_name=pipeline-function
```

**예상 결과**:
- 약 1-2분 후 두 이메일 주소로 알림 전송
- 이메일 제목: "Pipeline Function Execution Failure"

---

## 📝 요약

### 생성 완료된 Alert Policy

1. ✅ **Pipeline Function Execution Failure**
   - 조건: `pipeline-function`에서 ERROR 로그 발생
   - 알림: entrkjm@vaiv.kr, entrkjm@gmail.com

2. ⏳ **Pipeline Scheduler Job Failure** (생성 중)
   - 조건: `naver-webtoon-weekly-collection` 작업 실패
   - 알림: entrkjm@vaiv.kr, entrkjm@gmail.com

---

## 🎉 완료 후

두 번째 Alert Policy도 생성 완료하면:

1. ✅ Alert Policy 설정 완료
2. 🧪 테스트로 알림 동작 확인
3. 📊 프로젝트 완료 체크리스트 업데이트

---

## 💡 팁

- 첫 번째와 거의 동일한 과정입니다
- Metric만 "Cloud Scheduler Job"으로 변경
- Filter는 `job_id`만 추가하면 됩니다
- 알림 채널은 동일하게 선택

