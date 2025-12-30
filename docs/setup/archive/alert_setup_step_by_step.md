# Alert Policy 설정 단계별 가이드

> **목표**: Cloud Monitoring Alert Policy를 설정하여 파이프라인 실패 시 이메일 알림을 받습니다.

---

## 📋 사전 준비

### 1. 알림 채널 확인

다음 명령어로 알림 채널이 생성되어 있는지 확인합니다:

```bash
gcloud alpha monitoring channels list \
    --format="table(displayName,labels.email_address)"
```

**예상 결과**:
- Pipeline Alert Email 1 (entrkjm@vaiv.kr)
- Pipeline Alert Email 2 (entrkjm@gmail.com)

✅ 알림 채널이 2개 있으면 준비 완료입니다.

---

## 🎯 Alert Policy 설정 (Cloud Console)

### Step 1: Cloud Monitoring 페이지 접속

1. 브라우저에서 다음 링크를 엽니다:
   ```
   https://console.cloud.google.com/monitoring/alerting?project=naver-webtoon-collector
   ```

2. 또는 수동으로 접속:
   - [Google Cloud Console](https://console.cloud.google.com/) 접속
   - 프로젝트 선택: `naver-webtoon-collector`
   - 왼쪽 메뉴에서 **"Monitoring"** → **"Alerting"** 클릭

---

### Step 2: Alert Policy 1 생성 - Cloud Function 실행 실패

#### 2-1. Alert Policy 생성 시작

1. **"CREATE POLICY"** 버튼 클릭
2. **"Select a metric"** 선택

#### 2-2. 조건 설정

**Find resource type and metric** 섹션에서:

1. **Resource type** 선택:
   - 드롭다운에서 `Cloud Run Revision` 선택

2. **Metric** 선택:
   - 검색창에 `log entries` 입력
   - `Log entries` 선택

3. **Filter** 설정:
   - **Add filter** 클릭
   - **Label**: `service_name` 선택
   - **Value**: `pipeline-function` 입력
   
   - **Add filter** 클릭 (두 번째)
   - **Label**: `severity` 선택
   - **Value**: `ERROR` 입력

4. **Filter preview** 확인:
   ```
   resource.type="cloud_run_revision"
   resource.labels.service_name="pipeline-function"
   severity="ERROR"
   ```

#### 2-3. Alert trigger 설정

1. **Condition type**: `Any time series violates` 선택
2. **Threshold**: `Any value is above` → `0` 입력
3. **Advanced Options**:
   - **Duration**: `1 minute` 선택
   - **Evaluation window**: `1 minute` 선택

#### 2-4. 알림 채널 추가

1. **Notification channels** 섹션에서:
   - **"Select notification channels"** 클릭
   - 다음 2개 채널 모두 선택:
     - ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
     - ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)
   - **"OK"** 클릭

#### 2-5. Alert Policy 이름 및 저장

1. **Alert name**: `Pipeline Function Execution Failure` 입력
2. **Documentation** (선택사항):
   ```
   Cloud Function 'pipeline-function' 실행 중 오류가 발생했습니다.
   Cloud Logging에서 ERROR 레벨 로그를 확인하세요.
   ```
3. **"CREATE POLICY"** 버튼 클릭

✅ **Alert Policy 1 생성 완료!**

---

### Step 3: Alert Policy 2 생성 - Cloud Scheduler 작업 실패

#### 3-1. Alert Policy 생성 시작

1. 다시 **"CREATE POLICY"** 버튼 클릭
2. **"Select a metric"** 선택

#### 3-2. 조건 설정

**Find resource type and metric** 섹션에서:

1. **Resource type** 선택:
   - 드롭다운에서 `Cloud Scheduler Job` 선택

2. **Metric** 선택:
   - 검색창에 `failed execution` 입력
   - `Job failed execution count` 선택

3. **Filter** 설정:
   - **Add filter** 클릭
   - **Label**: `job_id` 선택
   - **Value**: `naver-webtoon-weekly-collection` 입력

4. **Filter preview** 확인:
   ```
   resource.type="cloud_scheduler_job"
   resource.labels.job_id="naver-webtoon-weekly-collection"
   ```

#### 3-3. Alert trigger 설정

1. **Condition type**: `Any time series violates` 선택
2. **Threshold**: `Any value is above` → `0` 입력
3. **Advanced Options**:
   - **Duration**: `1 minute` 선택
   - **Evaluation window**: `1 minute` 선택

#### 3-4. 알림 채널 추가

1. **Notification channels** 섹션에서:
   - **"Select notification channels"** 클릭
   - 다음 2개 채널 모두 선택:
     - ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
     - ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)
   - **"OK"** 클릭

#### 3-5. Alert Policy 이름 및 저장

1. **Alert name**: `Pipeline Scheduler Job Failure` 입력
2. **Documentation** (선택사항):
   ```
   Cloud Scheduler 작업 'naver-webtoon-weekly-collection'이 실패했습니다.
   Cloud Scheduler에서 작업 실행 이력을 확인하세요.
   ```
3. **"CREATE POLICY"** 버튼 클릭

✅ **Alert Policy 2 생성 완료!**

---

## ✅ 설정 완료 확인

### 1. Alert Policy 목록 확인

Cloud Console에서:
- **Monitoring** → **Alerting** → **Policies** 메뉴로 이동
- 다음 2개의 Alert Policy가 보여야 합니다:
  - ✅ Pipeline Function Execution Failure
  - ✅ Pipeline Scheduler Job Failure

### 2. 명령어로 확인

```bash
gcloud alpha monitoring policies list \
    --format="table(displayName,notificationChannels)" \
    --filter="displayName:Pipeline"
```

---

## 🧪 알림 테스트

### 방법 1: Cloud Function에 테스트 ERROR 로그 기록

```bash
gcloud logging write test-error-log \
    "테스트 에러 메시지 - Alert Policy 테스트" \
    --severity=ERROR \
    --resource-type=cloud_run_revision \
    --resource-labels.service_name=pipeline-function
```

**예상 결과**:
- 약 1-2분 후 두 이메일 주소로 알림 전송
- 이메일 제목: "Pipeline Function Execution Failure"

### 방법 2: Cloud Scheduler 작업 실패 시뮬레이션

Cloud Scheduler 작업을 일시적으로 비활성화했다가 다시 활성화하면 실패 이벤트가 발생할 수 있습니다.

---

## 📧 알림 이메일 확인

알림이 오면 다음 정보가 포함됩니다:

- **제목**: Alert Policy 이름 (예: "Pipeline Function Execution Failure")
- **내용**: 
  - 발생 시간
  - 리소스 정보
  - 메트릭 값
  - Cloud Console 링크

**스팸 폴더 확인**: GCP 알림 이메일이 스팸 폴더로 이동했을 수 있습니다.

---

## 🔧 문제 해결

### 알림 채널이 보이지 않는 경우

```bash
# 알림 채널 목록 확인
gcloud alpha monitoring channels list

# 알림 채널 재생성 (필요시)
gcloud alpha monitoring channels create \
    --display-name="Pipeline Alert Email 1" \
    --type=email \
    --channel-labels=email_address="entrkjm@vaiv.kr"
```

### Alert Policy가 트리거되지 않는 경우

1. **Filter 확인**: 리소스 타입과 메트릭이 정확한지 확인
2. **로그 확인**: Cloud Logging에서 실제 ERROR 로그가 있는지 확인
3. **시간 확인**: Alert Policy는 1분 후에 트리거됩니다

### 알림이 오지 않는 경우

1. **이메일 주소 확인**: 알림 채널의 이메일 주소가 정확한지 확인
2. **스팸 폴더 확인**: 이메일이 스팸 폴더로 이동했을 수 있습니다
3. **Alert Policy 상태 확인**: Alert Policy가 "Enabled" 상태인지 확인

---

## 📝 요약

### 생성된 Alert Policy

1. **Pipeline Function Execution Failure**
   - 조건: `pipeline-function` Cloud Function에서 ERROR 로그 발생
   - 알림: entrkjm@vaiv.kr, entrkjm@gmail.com

2. **Pipeline Scheduler Job Failure**
   - 조건: `naver-webtoon-weekly-collection` 스케줄러 작업 실패
   - 알림: entrkjm@vaiv.kr, entrkjm@gmail.com

### 알림이 오는 경우

- ✅ Cloud Function 실행 실패 (ERROR 로그 발생)
- ✅ Cloud Scheduler 작업 실패
- ✅ 데이터 검증 함수에서 ERROR 로그 발생 (데이터 검증 함수 배포 후)

---

## 🔗 관련 문서

- [Alert Setup Manual](./alert_setup_manual.md) - 간단한 가이드
- [Alert Notification Guide](../monitoring/alert_notification_guide.md) - 알림 확인 방법
- [Monitoring Guide](../monitoring/monitoring_guide.md) - 모니터링 전체 가이드

---

## 💡 팁

- Alert Policy는 한 번만 설정하면 됩니다
- 알림은 1시간에 최대 1회로 제한됩니다 (중복 알림 방지)
- Alert Policy를 수정하려면 Cloud Console에서 해당 Policy를 클릭하여 편집할 수 있습니다
- 알림을 받지 않으려면 Alert Policy를 "Disabled"로 변경할 수 있습니다

