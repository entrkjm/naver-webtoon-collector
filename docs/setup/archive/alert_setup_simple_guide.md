# Alert Policy 설정 - 간단한 순서 가이드

> **목표**: 파이프라인 실패 시 이메일 알림 받기

---

## 🎯 Alert Policy 1: Cloud Function 실행 실패

### 1단계: Alert Policy 생성 시작

1. [Cloud Monitoring Alerting 페이지](https://console.cloud.google.com/monitoring/alerting?project=naver-webtoon-collector) 접속
2. **"CREATE POLICY"** 버튼 클릭

### 2단계: Metric 선택

1. **"Select a metric"** 클릭
2. 왼쪽 리소스 목록에서 **"Cloud Function"** 클릭
3. 나타나는 메트릭 목록에서 **"Log entry count"** 선택
4. **"Apply"** 버튼 클릭

### 3단계: Filter 추가

1. **"Add filter"** 또는 **"+"** 버튼 클릭
2. 첫 번째 필터:
   - **Label**: `service_name` 선택
   - **Value**: `pipeline-function` 입력
3. **"Add filter"** 다시 클릭
4. 두 번째 필터:
   - **Label**: `severity` 선택
   - **Value**: `ERROR` 입력

### 4단계: Alert Condition 설정

1. **"Configure trigger"** 섹션에서:
   - **Condition type**: `Any time series violates` 선택
   - **Threshold**: `Any value is above` → `0` 입력
   - **Duration**: `1 minute` 선택

### 5단계: 알림 채널 추가

1. 왼쪽 메뉴에서 **"Notifications and name"** 클릭
2. **"Notification channels"** 또는 **"Add notification channels"** 클릭
3. 다음 2개 채널 모두 선택:
   - ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
   - ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)
4. **"OK"** 또는 **"Select"** 클릭

### 6단계: 이름 입력 및 저장

1. **"Alert name"** 또는 **"Policy name"** 입력란에:
   ```
   Pipeline Function Execution Failure
   ```
2. 하단의 **"Create Policy"** 버튼 클릭

✅ **첫 번째 Alert Policy 완료!**

---

## 🎯 Alert Policy 2: Cloud Scheduler 작업 실패

### 1단계: Alert Policy 생성 시작

1. 다시 **"CREATE POLICY"** 버튼 클릭

### 2단계: Metric 선택

1. **"Select a metric"** 클릭
2. 왼쪽 리소스 목록에서 **"Cloud Scheduler Job"** 클릭
3. 나타나는 메트릭 목록에서 **"Job failed execution count"** 선택
4. **"Apply"** 버튼 클릭

### 3단계: Filter 추가

1. **"Add filter"** 또는 **"+"** 버튼 클릭
2. 필터:
   - **Label**: `job_id` 선택
   - **Value**: `naver-webtoon-weekly-collection` 입력

### 4단계: Alert Condition 설정

1. **"Configure trigger"** 섹션에서:
   - **Condition type**: `Any time series violates` 선택
   - **Threshold**: `Any value is above` → `0` 입력
   - **Duration**: `1 minute` 선택

### 5단계: 알림 채널 추가

1. 왼쪽 메뉴에서 **"Notifications and name"** 클릭
2. **"Notification channels"** 클릭
3. 다음 2개 채널 모두 선택:
   - ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
   - ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)
4. **"OK"** 클릭

### 6단계: 이름 입력 및 저장

1. **"Alert name"** 입력란에:
   ```
   Pipeline Scheduler Job Failure
   ```
2. 하단의 **"Create Policy"** 버튼 클릭

✅ **두 번째 Alert Policy 완료!**

---

## ✅ 완료 확인

### 확인 방법

1. **"Policies"** 페이지로 이동
2. 다음 2개의 Alert Policy가 보여야 합니다:
   - ✅ Pipeline Function Execution Failure
   - ✅ Pipeline Scheduler Job Failure

### 명령어로 확인

```bash
gcloud alpha monitoring policies list \
    --format="table(displayName)" \
    --filter="displayName:Pipeline"
```

---

## 🧪 테스트

설정이 제대로 되었는지 테스트:

```bash
# 테스트 ERROR 로그 기록
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

### 생성한 Alert Policy

1. **Pipeline Function Execution Failure**
   - 조건: `pipeline-function`에서 ERROR 로그 발생
   - 알림: entrkjm@vaiv.kr, entrkjm@gmail.com

2. **Pipeline Scheduler Job Failure**
   - 조건: `naver-webtoon-weekly-collection` 작업 실패
   - 알림: entrkjm@vaiv.kr, entrkjm@gmail.com

### 알림이 오는 경우

- ✅ Cloud Function 실행 실패 (ERROR 로그 발생)
- ✅ Cloud Scheduler 작업 실패
- ✅ 데이터 검증 함수에서 ERROR 로그 발생

---

## 💡 팁

- 각 단계를 차근차근 진행하세요
- "Apply" 버튼이 회색이면 metric을 선택했는지 확인하세요
- 알림 채널은 두 개 모두 선택해야 합니다
- 설정 완료 후 테스트로 확인하세요

