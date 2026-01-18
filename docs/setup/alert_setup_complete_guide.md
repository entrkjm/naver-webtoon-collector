# Alert Policy 설정 완전 가이드

> **최종 통합 가이드**: 실제 Cloud Console 화면 기준 단계별 가이드

---

## 📋 목차

1. [사전 준비](#사전-준비)
2. [Alert Policy 1: Cloud Function 실행 실패](#alert-policy-1-cloud-function-실행-실패)
3. [Alert Policy 2: Cloud Scheduler 작업 실패](#alert-policy-2-cloud-scheduler-작업-실패)
4. [완료 확인](#완료-확인)
5. [테스트](#테스트)

---

## 사전 준비

### 알림 채널 확인

다음 명령어로 알림 채널이 생성되어 있는지 확인:

```bash
gcloud alpha monitoring channels list \
    --format="table(displayName,labels.email_address)"
```

**예상 결과**:
- Pipeline Alert Email 1 (entrkjm@vaiv.kr)
- Pipeline Alert Email 2 (entrkjm@gmail.com)

✅ 알림 채널이 2개 있으면 준비 완료입니다.

---

## Alert Policy 1: Cloud Function 실행 실패

### 1단계: Alert Policy 생성 시작

1. [Cloud Monitoring Alerting 페이지](https://console.cloud.google.com/monitoring/alerting?project=naver-webtoon-collector) 접속
2. **"CREATE POLICY"** 버튼 클릭

### 2단계: Metric 선택

1. **"Select a metric"** 클릭
2. 왼쪽 리소스 목록에서 **"Cloud Function"** 클릭
3. 나타나는 메트릭 목록에서 **"Log entry count"** 선택
4. **"Apply"** 버튼 클릭

### 3단계: Filter 추가

화면 오른쪽에 **"Resource labels"** 섹션이 나타나면:

#### Filter 1: function_name

1. **"Filter"** 입력 필드에 `function_name` 입력
2. **"Comparator"**: `=` 선택
3. **"Value"**: `pipeline-function` 입력
4. **"Done"** 버튼 클릭

#### Filter 2: severity

1. **"Add a filter"** 링크 클릭
2. **"Filter"** 입력 필드에 `severity` 입력
3. **"Comparator"**: `=` 선택
4. **"Value"**: `ERROR` 입력
5. **"Done"** 버튼 클릭

### 4단계: Alert Condition 설정

1. 왼쪽 메뉴에서 **"Configure trigger"** 클릭
2. **Condition type**: `Threshold` (이미 선택됨)
3. **Alert trigger**: `Any time series violates` (이미 선택됨)
4. **Threshold position**: `Above threshold` (이미 선택됨)
5. **Threshold value**: `0` 입력 ← 중요!
6. **Advanced Options** 클릭:
   - **Duration**: `1 minute` 선택

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
   Pipeline Function Execution Failure
   ```
2. 하단의 **"Create Policy"** 버튼 클릭

✅ **첫 번째 Alert Policy 완료!**

---

## Alert Policy 2: Cloud Scheduler 작업 실패 (선택사항)

> **⚠️ 중요 결정**: 웹 검색 결과에 따르면, **Cloud Scheduler 자체에 대한 Alert Policy는 선택사항**입니다.
>
> **이유**:
> 1. Cloud Scheduler는 단순히 Cloud Function을 호출하는 역할만 수행
> 2. 실제 작업의 성공 여부는 호출된 Cloud Function에서 결정됨
> 3. Cloud Function 실행 실패 Alert Policy만으로도 충분히 파이프라인 실패를 감지 가능
> 4. Cloud Scheduler가 Function을 호출하지 못하는 경우는 매우 드뭄
>
> **권장사항**: 
> - ✅ **Cloud Function 실행 실패 Alert Policy만 사용** (이미 생성 완료)
> - ⚠️ Cloud Scheduler Alert Policy는 기술적 제약으로 생성이 어려움 (로그 필터링 제한)
> - 💡 **결론: Cloud Function Alert Policy만으로 충분합니다!**
>
> 아래는 Cloud Scheduler Alert Policy를 생성하고 싶은 경우를 위한 가이드입니다.

### 1단계: Alert Policy 생성 시작

1. 다시 **"CREATE POLICY"** 버튼 클릭

### 2단계: Builder 모드에서 설정

1. **"Builder"** 탭이 선택되어 있는지 확인
2. **"Select a metric"** 클릭

### 3단계: Metric 선택

1. 왼쪽 리소스 목록에서 **"Cloud Scheduler Job"** 클릭
2. **"Logs-based metrics"** 카테고리 클릭
3. **"Log entries"** 선택
4. **"Apply"** 버튼 클릭

### 4단계: Filter 추가

화면 오른쪽에 **"Resource labels"** 섹션이 나타나면:

#### Filter 1: job_id

1. **"Filter"** 입력 필드에 `job_id` 입력
2. **"Comparator"**: `=` 선택
3. **"Value"**: `naver-webtoon-weekly-collection` 입력
4. **"Done"** 버튼 클릭

#### Filter 2: HTTP 상태 코드로 실패 감지 (선택사항)

> **참고**: Builder 모드에서는 `jsonPayload.status` 필드를 직접 필터링할 수 없을 수 있습니다.

**옵션 A: HTTP 상태 코드로 필터링 (시도해보기)**

1. **"Add a filter"** 링크 클릭
2. **"Filter"** 입력 필드에 `httpRequest.status` 입력
3. **"Comparator"**: `>=` 선택
4. **"Value"**: `400` 입력 (400 이상은 에러)
5. **"Done"** 버튼 클릭

> **주의**: 이 방법은 HTTP 에러만 감지합니다. 타임아웃 등 다른 실패는 감지하지 못할 수 있습니다.

**옵션 B: Filter 없이 진행 (권장)**

> **현실적인 제약**: Cloud Monitoring의 로그 기반 메트릭에서는 `jsonPayload` 필드를 직접 필터링하기 어렵습니다.

**대안**: 
- `job_id` 필터만 사용하여 해당 Job의 모든 로그를 감지
- 하지만 이렇게 하면 정상 실행 시에도 알림이 갈 수 있습니다
- **더 나은 방법**: Cloud Function 실행 실패 Alert Policy만 사용 (이미 생성 완료)
  - Cloud Scheduler가 Cloud Function을 호출하므로, Function 실패 시 알림을 받으면 Scheduler 실패도 간접적으로 감지 가능

**또는**: Cloud Scheduler Job 실패 감지는 건너뛰고, Cloud Function 실행 실패 Alert Policy만 사용하는 것을 권장합니다.

### 5단계: Alert Condition 설정

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

## 완료 확인

### Cloud Console에서 확인

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

## 테스트

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

### 생성된 Alert Policy

1. **Pipeline Function Execution Failure** ✅ (생성 완료)
   - 조건: `pipeline-function`에서 ERROR 로그 발생
   - 알림: entrkjm@vaiv.kr, entrkjm@gmail.com
   - **이것만으로도 충분합니다!**

2. **Pipeline Scheduler Job Failure** ⚠️ (선택사항, 기술적 제약으로 생성 어려움)
   - 조건: `naver-webtoon-weekly-collection` 작업 실패
   - 알림: entrkjm@vaiv.kr, entrkjm@gmail.com
   - **참고**: Cloud Function Alert Policy만으로도 Scheduler 실패를 간접적으로 감지 가능

### 알림이 오는 경우

- ✅ Cloud Function 실행 실패 (ERROR 로그 발생)
- ✅ Cloud Scheduler 작업 실패
- ✅ 데이터 검증 함수에서 ERROR 로그 발생

---

## 💡 주요 포인트

### Filter Label

- Cloud Function: `function_name` (Resource labels에서 확인)
- Cloud Scheduler: `job_id` (Resource labels에서 확인)

### Threshold

- `0` 입력: ERROR 로그가 1개라도 발생하면 알림
- Duration: `1 minute` 권장

### 알림 채널

- 두 이메일 채널 모두 선택 필수
- entrkjm@vaiv.kr
- entrkjm@gmail.com

---

## 🔗 관련 문서

- [Alert Notification Guide](../monitoring/alert_notification_guide.md) - 알림 확인 방법
- [Monitoring Guide](../monitoring/monitoring_guide.md) - 모니터링 전체 가이드

