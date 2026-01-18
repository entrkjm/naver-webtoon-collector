# Alert Policy 설정 - Cloud Console UI 가이드

> **최신 UI 기준**: 2024-2025년 Cloud Console 인터페이스

Cloud Console의 실제 화면에 맞춘 단계별 가이드입니다.

---

## 🚀 시작하기

### Step 1: Cloud Monitoring 페이지 접속

1. 다음 링크로 이동:
   ```
   https://console.cloud.google.com/monitoring/alerting?project=naver-webtoon-collector
   ```

2. 또는 수동 접속:
   - [Google Cloud Console](https://console.cloud.google.com/) 접속
   - 프로젝트 선택: `naver-webtoon-collector`
   - 왼쪽 메뉴: **"Monitoring"** → **"Alerting"** → **"Policies"**

---

## 📋 Alert Policy 1: Cloud Function 실행 실패

### 방법 A: Logs-based Alert (권장)

#### 1. Alert Policy 생성 시작

1. **"CREATE POLICY"** 버튼 클릭
2. **"Select a metric"** 섹션에서:
   - **"Logs-based alert"** 또는 **"Log-based metric"** 선택
   - 또는 왼쪽 메뉴에서 **"Logs"** 탭 클릭

#### 2. Log Query 작성

**Log query** 또는 **Filter** 입력란에 다음을 입력:

```
resource.type="cloud_run_revision"
resource.labels.service_name="pipeline-function"
severity="ERROR"
```

**또는 MQL (Monitoring Query Language) 사용:**

```
fetch cloud_run_revision
| filter resource.labels.service_name == "pipeline-function"
| filter severity == "ERROR"
| group_by 1m
| every 1m
```

#### 3. Alert Condition 설정

1. **Alert trigger**: `Any log entry matches` 또는 `Any time series violates`
2. **Threshold**: `> 0` 또는 `Any value is above 0`
3. **Duration**: `1 minute`

#### 4. 알림 채널 추가

1. **"Notification channels"** 또는 **"Add notification channels"** 클릭
2. 다음 2개 채널 선택:
   - ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
   - ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)
3. **"OK"** 또는 **"Select"** 클릭

#### 5. Alert Policy 이름 및 저장

1. **Alert name** 또는 **Policy name**: `Pipeline Function Execution Failure`
2. **"CREATE POLICY"** 또는 **"SAVE"** 클릭

---

### 방법 B: Metric-based Alert

#### 1. Alert Policy 생성 시작

1. **"CREATE POLICY"** 버튼 클릭
2. **"Select a metric"** 클릭

#### 2. Metric 선택

**방법 1: 검색으로 찾기**
1. 검색창에 `logging.googleapis.com/log_entry_count` 입력
2. **"Log entry count"** 선택

**방법 2: 카테고리로 찾기**
1. **"Resource type"** 또는 **"Resource"** 드롭다운에서:
   - `Cloud Run Revision` 선택
2. **"Metric"** 드롭다운에서:
   - `Log entry count` 선택

#### 3. Filter 설정

**Filter** 섹션에서:

1. **"Add filter"** 또는 **"+"** 버튼 클릭
2. **Label**: `service_name` 선택
3. **Value**: `pipeline-function` 입력
4. **"Add filter"** 다시 클릭
5. **Label**: `severity` 선택
6. **Value**: `ERROR` 입력

**Filter preview** 확인:
```
resource.type="cloud_run_revision"
resource.labels.service_name="pipeline-function"
severity="ERROR"
```

#### 4. Alert Condition 설정

1. **Condition type**: `Any time series violates` 선택
2. **Threshold**: 
   - `Any value is above` → `0` 입력
3. **Duration**: `1 minute` 선택

#### 5. 알림 채널 추가

1. **"Notification channels"** 섹션에서:
   - **"Select notification channels"** 클릭
   - 다음 2개 채널 선택:
     - ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
     - ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)
   - **"OK"** 클릭

#### 6. Alert Policy 이름 및 저장

1. **Alert name**: `Pipeline Function Execution Failure`
2. **"CREATE POLICY"** 클릭

---

## 📋 Alert Policy 2: Cloud Scheduler 작업 실패

### 방법 A: Metric-based Alert (권장)

#### 1. Alert Policy 생성 시작

1. **"CREATE POLICY"** 버튼 클릭
2. **"Select a metric"** 클릭

#### 2. Metric 선택

**검색으로 찾기:**
1. 검색창에 `scheduler.googleapis.com/job/failed_execution_count` 입력
2. **"Job failed execution count"** 선택

**또는 카테고리로 찾기:**
1. **"Resource type"** 또는 **"Resource"** 드롭다운에서:
   - `Cloud Scheduler Job` 선택
2. **"Metric"** 드롭다운에서:
   - `Job failed execution count` 선택

#### 3. Filter 설정

**Filter** 섹션에서:

1. **"Add filter"** 또는 **"+"** 버튼 클릭
2. **Label**: `job_id` 선택
3. **Value**: `naver-webtoon-weekly-collection` 입력

**Filter preview** 확인:
```
resource.type="cloud_scheduler_job"
resource.labels.job_id="naver-webtoon-weekly-collection"
```

#### 4. Alert Condition 설정

1. **Condition type**: `Any time series violates` 선택
2. **Threshold**: 
   - `Any value is above` → `0` 입력
3. **Duration**: `1 minute` 선택

#### 5. 알림 채널 추가

1. **"Notification channels"** 섹션에서:
   - **"Select notification channels"** 클릭
   - 다음 2개 채널 선택:
     - ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
     - ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)
   - **"OK"** 클릭

#### 6. Alert Policy 이름 및 저장

1. **Alert name**: `Pipeline Scheduler Job Failure`
2. **"CREATE POLICY"** 클릭

---

## 🔍 UI가 다른 경우

### "Resource type" 항목이 없는 경우

Cloud Console UI가 업데이트되어 다음 중 하나일 수 있습니다:

#### 옵션 1: 검색창 사용

1. **"Select a metric"** 클릭
2. 상단 검색창에 직접 입력:
   - `logging.googleapis.com/log_entry_count` (Cloud Function용)
   - `scheduler.googleapis.com/job/failed_execution_count` (Scheduler용)
3. 검색 결과에서 선택

#### 옵션 2: MQL (Monitoring Query Language) 사용

1. **"CREATE POLICY"** 클릭
2. **"MQL"** 또는 **"Query"** 탭 선택
3. 다음 쿼리 입력:

**Cloud Function용:**
```
fetch cloud_run_revision
| filter resource.labels.service_name == "pipeline-function"
| filter severity == "ERROR"
| group_by 1m
| every 1m
```

**Scheduler용:**
```
fetch cloud_scheduler_job
| filter resource.labels.job_id == "naver-webtoon-weekly-collection"
| metric 'scheduler.googleapis.com/job/failed_execution_count'
| group_by 1m
| every 1m
```

#### 옵션 3: Logs-based Alert 사용

1. **"CREATE POLICY"** 클릭
2. **"Logs"** 또는 **"Log-based"** 탭 선택
3. Log query 입력 (위의 "방법 A" 참고)

---

## 🎯 핵심 포인트

### Cloud Function 실행 실패 감지

**핵심 정보:**
- **Metric**: `logging.googleapis.com/log_entry_count` 또는 Logs-based alert
- **Filter**: `service_name="pipeline-function"` AND `severity="ERROR"`
- **Threshold**: `> 0`

### Cloud Scheduler 작업 실패 감지

**핵심 정보:**
- **Metric**: `scheduler.googleapis.com/job/failed_execution_count`
- **Filter**: `job_id="naver-webtoon-weekly-collection"`
- **Threshold**: `> 0`

---

## 🧪 테스트

설정 완료 후 테스트:

```bash
# 테스트 ERROR 로그 기록
gcloud logging write test-error-log \
    "테스트 에러 메시지 - Alert Policy 테스트" \
    --severity=ERROR \
    --resource-type=cloud_run_revision \
    --resource-labels.service_name=pipeline-function
```

약 1-2분 후 이메일 알림 확인

---

## ❓ 문제 해결

### "Resource type" 항목이 보이지 않는 경우

1. **검색창 사용**: 상단 검색창에 metric 이름 직접 입력
2. **MQL 사용**: "MQL" 또는 "Query" 탭에서 쿼리 작성
3. **Logs 탭 사용**: "Logs" 또는 "Log-based" 탭에서 로그 쿼리 작성

### Metric을 찾을 수 없는 경우

1. **정확한 metric 이름 확인**:
   ```bash
   # Cloud Function 로그 메트릭
   logging.googleapis.com/log_entry_count
   
   # Scheduler 실패 메트릭
   scheduler.googleapis.com/job/failed_execution_count
   ```

2. **검색창에 전체 metric 이름 입력**

3. **API 활성화 확인**:
   - Cloud Logging API
   - Cloud Monitoring API
   - Cloud Scheduler API

---

## 📝 요약

### 생성할 Alert Policy

1. **Pipeline Function Execution Failure**
   - Metric: `logging.googleapis.com/log_entry_count` 또는 Logs-based
   - Filter: `service_name="pipeline-function"`, `severity="ERROR"`
   - 알림: entrkjm@vaiv.kr, entrkjm@gmail.com

2. **Pipeline Scheduler Job Failure**
   - Metric: `scheduler.googleapis.com/job/failed_execution_count`
   - Filter: `job_id="naver-webtoon-weekly-collection"`
   - 알림: entrkjm@vaiv.kr, entrkjm@gmail.com

---

## 🔗 관련 문서

- [Alert Setup Step by Step](./alert_setup_step_by_step.md) - 상세 가이드
- [Alert Setup Manual](./alert_setup_manual.md) - 간단 가이드

