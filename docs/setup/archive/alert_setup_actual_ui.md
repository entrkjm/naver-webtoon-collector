# Alert Policy 설정 - 실제 화면 기준 가이드

> **실제 Cloud Console UI 기준** (2024-2025)

---

## 📋 Alert Policy 1: Cloud Function 실행 실패

### Step 1: Metric 선택

현재 화면에서:

1. **왼쪽 리소스 목록**에서 **"Cloud Function"** 클릭
   - "1 metric >" 표시가 있는 항목
   - ⚠️ "Cloud Run Revision"도 가능하지만, "Cloud Function"이 더 직관적입니다

2. 또는 검색창에 다음을 입력:
   ```
   logging.googleapis.com/log_entry_count
   ```

3. **"Cloud Function"** 클릭하면 해당 리소스의 메트릭 목록이 표시됩니다

### Step 2: Metric 선택

1. **"Cloud Function"** 클릭 후 나타나는 메트릭 목록에서:
   - **"Log entry count"** 또는 **"logging.googleapis.com/log_entry_count"** 선택

2. **"Apply"** 버튼 클릭 (현재는 회색이지만 선택하면 활성화됨)

### Step 3: Filter 설정

Metric 선택 후 화면이 변경되면:

1. **"Add filter"** 또는 **"+"** 버튼 클릭

2. 첫 번째 필터:
   - **Label**: `service_name` 선택
   - **Value**: `pipeline-function` 입력

3. 두 번째 필터 추가:
   - **"Add filter"** 다시 클릭
   - **Label**: `severity` 선택
   - **Value**: `ERROR` 입력

### Step 4: Alert Condition 설정

1. **"Configure trigger"** 섹션에서:
   - **Condition type**: `Any time series violates` 선택
   - **Threshold**: `Any value is above` → `0` 입력
   - **Duration**: `1 minute` 선택

### Step 5: 알림 채널 추가

1. **"Notifications and name"** 섹션으로 이동

2. **"Notification channels"** 또는 **"Add notification channels"** 클릭

3. 다음 2개 채널 선택:
   - ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
   - ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)

4. **"OK"** 또는 **"Select"** 클릭

### Step 6: Alert Policy 이름 및 저장

1. **"Alert name"** 또는 **"Policy name"** 입력:
   ```
   Pipeline Function Execution Failure
   ```

2. 하단의 **"Create Policy"** 버튼 클릭

---

## 📋 Alert Policy 2: Cloud Scheduler 작업 실패

### Step 1: Metric 선택

1. 다시 **"CREATE POLICY"** 버튼 클릭

2. **"Select a metric"** 클릭

3. **왼쪽 리소스 목록**에서 **"Cloud Scheduler Job"** 클릭
   - "1 metric >" 표시가 있는 항목

4. 또는 검색창에 다음을 입력:
   ```
   scheduler.googleapis.com/job/failed_execution_count
   ```

### Step 2: Metric 선택

1. **"Cloud Scheduler Job"** 클릭 후 나타나는 메트릭 목록에서:
   - **"Job failed execution count"** 또는 **"scheduler.googleapis.com/job/failed_execution_count"** 선택

2. **"Apply"** 버튼 클릭

### Step 3: Filter 설정

1. **"Add filter"** 또는 **"+"** 버튼 클릭

2. 필터 추가:
   - **Label**: `job_id` 선택
   - **Value**: `naver-webtoon-weekly-collection` 입력

### Step 4: Alert Condition 설정

1. **"Configure trigger"** 섹션에서:
   - **Condition type**: `Any time series violates` 선택
   - **Threshold**: `Any value is above` → `0` 입력
   - **Duration**: `1 minute` 선택

### Step 5: 알림 채널 추가

1. **"Notifications and name"** 섹션으로 이동

2. **"Notification channels"** 클릭

3. 다음 2개 채널 선택:
   - ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
   - ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)

4. **"OK"** 클릭

### Step 6: Alert Policy 이름 및 저장

1. **"Alert name"** 입력:
   ```
   Pipeline Scheduler Job Failure
   ```

2. 하단의 **"Create Policy"** 버튼 클릭

---

## 🎯 핵심 단계 요약

### 현재 화면에서 해야 할 일:

1. **왼쪽 리소스 목록**에서:
   - Cloud Function용: **"Cloud Function"** 클릭 (또는 "Cloud Run Revision"도 가능)
   - Scheduler용: **"Cloud Scheduler Job"** 클릭

2. **메트릭 선택**:
   - Cloud Function → "Log entry count" 선택
   - Cloud Scheduler Job → "Job failed execution count" 선택

3. **"Apply"** 버튼 클릭

4. 이후 Filter, Condition, 알림 채널 설정

---

## 💡 팁

### 검색창 사용

검색창에 직접 입력해도 됩니다:
- `logging.googleapis.com/log_entry_count` (Cloud Function용)
- `scheduler.googleapis.com/job/failed_execution_count` (Scheduler용)

### "Apply" 버튼이 활성화되지 않는 경우

1. Metric을 선택했는지 확인
2. "Selection preview" 섹션에 선택한 metric이 표시되는지 확인

---

## ✅ 완료 확인

설정 완료 후:

1. **"Policies"** 페이지로 이동
2. 다음 2개의 Alert Policy가 보여야 합니다:
   - ✅ Pipeline Function Execution Failure
   - ✅ Pipeline Scheduler Job Failure

---

## 🧪 테스트

설정 완료 후 테스트:

```bash
gcloud logging write test-error-log \
    "테스트 에러 메시지" \
    --severity=ERROR \
    --resource-type=cloud_run_revision \
    --resource-labels.service_name=pipeline-function
```

약 1-2분 후 이메일 알림 확인

