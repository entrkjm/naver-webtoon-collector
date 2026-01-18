# Alert Policy 설정 - 정확한 단계 (실제 화면 기준)

> **현재 화면 기준**: Resource labels와 Metric labels가 표시된 화면

---

## 🎯 Alert Policy 1: Cloud Function 실행 실패

### 현재 화면에서 해야 할 일

화면 오른쪽에 **"Resource labels"** 섹션이 보입니다:

- `project_id`: 프로젝트 ID
- `function_name`: **이것을 사용하세요!** ← 함수 이름
- `region`: 리전

### Filter 추가 단계

#### Filter 1: function_name

1. **"Filter"** 입력 필드 클릭 (또는 "Type to filter" 입력란)
2. `function_name` 입력하거나 드롭다운에서 선택
3. **"Comparator"**: `=` 선택
4. **"Value"**: `pipeline-function` 입력
5. **"Done"** 버튼 클릭

#### Filter 2: severity

1. **"Add a filter"** 링크 클릭
2. **"Filter"** 입력 필드에 `severity` 입력
3. **"Comparator"**: `=` 선택
4. **"Value"**: `ERROR` 입력
5. **"Done"** 버튼 클릭

### 다음 단계

1. 왼쪽 메뉴에서 **"Configure trigger"** 클릭
2. **Condition type**: `Any time series violates` 선택
3. **Threshold**: `Any value is above` → `0` 입력
4. **Duration**: `1 minute` 선택

### 알림 채널 추가

1. 왼쪽 메뉴에서 **"Notifications and name"** 클릭
2. **"Notification channels"** 클릭
3. 다음 2개 채널 모두 선택:
   - ✅ Pipeline Alert Email 1 (entrkjm@vaiv.kr)
   - ✅ Pipeline Alert Email 2 (entrkjm@gmail.com)
4. **"OK"** 클릭

### 이름 입력 및 저장

1. **"Alert name"** 입력:
   ```
   Pipeline Function Execution Failure
   ```
2. 하단 **"Create Policy"** 버튼 클릭

---

## 🎯 Alert Policy 2: Cloud Scheduler 작업 실패

### Metric 선택

1. 다시 **"CREATE POLICY"** 클릭
2. **"Select a metric"** 클릭
3. **"Cloud Scheduler Job"** 클릭
4. **"Job failed execution count"** 선택
5. **"Apply"** 클릭

### Filter 추가

화면 오른쪽에 **"Resource labels"** 섹션이 나타나면:

1. **"Filter"** 입력 필드에 `job_id` 입력
2. **"Comparator"**: `=` 선택
3. **"Value"**: `naver-webtoon-weekly-collection` 입력
4. **"Done"** 버튼 클릭

### 나머지 단계

1. **"Configure trigger"** → Threshold 설정
2. **"Notifications and name"** → 알림 채널 추가
3. Alert name: `Pipeline Scheduler Job Failure`
4. **"Create Policy"** 클릭

---

## ✅ 핵심 포인트

### Cloud Function Filter

- **Filter**: `function_name` ← Resource labels에서 확인
- **Value**: `pipeline-function`
- **추가 Filter**: `severity = ERROR`

### Filter 입력 방법

1. **"Filter"** 입력 필드에 직접 입력: `function_name`
2. 또는 드롭다운에서 선택
3. **"Resource labels"** 섹션에 표시된 label 이름 사용

---

## 📝 요약

**현재 화면에서:**

1. **"Filter"** 입력 필드에 `function_name` 입력
2. **"Value"**에 `pipeline-function` 입력
3. **"Done"** 클릭
4. **"Add a filter"** 클릭하여 `severity = ERROR` 추가
5. 나머지 단계 진행

---

## 💡 참고

- `function_name`은 **Resource labels** 섹션에 표시된 label입니다
- `severity`는 **Metric labels** 또는 일반 label입니다
- Filter는 여러 개 추가할 수 있습니다

