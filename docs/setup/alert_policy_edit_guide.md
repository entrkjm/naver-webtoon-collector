# Alert Policy 수정 가이드

> **목적**: 기존 Alert Policy에 `data-validation-function`도 감지하도록 추가

---

## 현재 상황

- ✅ Alert Policy 생성 완료: "Pipeline Function Execution Failure"
- ✅ 현재 감지: `pipeline-function`의 ERROR 로그만 감지
- ⚠️ 추가 필요: `data-validation-function`의 ERROR 로그도 감지

---

## 수정 방법

### 방법 1: Alert Condition 추가 (권장)

기존 Alert Policy에 새로운 Alert Condition을 추가합니다.

#### 1단계: Alert Policy 편집

1. [Cloud Monitoring Alerting 페이지](https://console.cloud.google.com/monitoring/alerting?project=naver-webtoon-collector) 접속
2. **"Policies"** 탭 클릭
3. **"Pipeline Function Execution Failure"** Alert Policy 찾기
4. Alert Policy 이름 클릭하여 편집 모드 진입

#### 2단계: Alert Condition 추가

1. **"+ Add alert condition"** 또는 **"Add condition"** 버튼 클릭
2. **"Select a metric"** 클릭
3. 왼쪽 리소스 목록에서 **"Cloud Function"** 클릭
4. **"Log entry count"** 선택
5. **"Apply"** 버튼 클릭

#### 3단계: Filter 추가

화면 오른쪽에 **"Resource labels"** 섹션이 나타나면:

**Filter 1: function_name**
- **Filter**: `function_name`
- **Comparator**: `=`
- **Value**: `data-validation-function`
- **"Done"** 클릭

**Filter 2: severity**
- **"Add a filter"** 클릭
- **Filter**: `severity`
- **Comparator**: `=`
- **Value**: `ERROR`
- **"Done"** 클릭

#### 4단계: Alert Condition 설정

1. **"Configure trigger"** 클릭
2. **Threshold value**: `0` 입력
3. **Duration**: `1 minute` 선택

#### 5단계: 저장

1. **"SAVE"** 또는 **"UPDATE POLICY"** 버튼 클릭

✅ **완료!** 이제 두 함수 모두 감지합니다.

---

### 방법 2: Filter를 OR 조건으로 수정 (고급)

> **참고**: Cloud Monitoring UI에서는 OR 조건을 직접 설정하기 어려울 수 있습니다. 방법 1을 권장합니다.

만약 MQL을 사용할 수 있다면:

1. Alert Policy 편집 모드에서 **"MQL"** 탭 클릭
2. 다음 쿼리 입력:

```mql
fetch cloud_function
| filter resource.label.function_name == 'pipeline-function' OR resource.label.function_name == 'data-validation-function'
| filter severity == 'ERROR'
| group_by 1m, [value_log_entry_count_aggregate: aggregate(value.log_entry_count)]
| every 1m
| condition value_log_entry_count_aggregate > 0
```

---

## 수정 후 확인

### Alert Policy 확인

```bash
gcloud alpha monitoring policies list \
    --format="table(displayName,conditions)" \
    --filter="displayName:Pipeline Function"
```

### 테스트

데이터 검증 함수에서 ERROR 로그를 발생시켜 알림이 오는지 확인:

```bash
# 데이터 검증 함수 수동 실행 (데이터가 없는 날짜로)
curl -X POST "https://data-validation-function-xxx.run.app" \
  -H "Content-Type: application/json" \
  -d '{"date": "2099-01-01"}'
```

약 1-2분 후 이메일 알림 확인

---

## 최종 결과

수정 후 Alert Policy는 다음을 감지합니다:

1. ✅ `pipeline-function`의 ERROR 로그
2. ✅ `data-validation-function`의 ERROR 로그

두 함수 중 하나라도 ERROR 로그를 발생시키면 알림이 전송됩니다.

---

## 문제 해결

### "Add condition" 버튼이 보이지 않는 경우

- Alert Policy를 편집 모드로 전환했는지 확인
- 또는 Alert Policy를 삭제하고 새로 생성 (두 함수 모두 포함)

### Filter가 작동하지 않는 경우

- `function_name` 대신 `service_name` 또는 `service`를 시도
- MQL 탭을 사용하여 직접 쿼리 작성

---

## 참고

- 두 함수 모두 Cloud Function이므로 같은 Alert Policy에서 감지 가능
- 각 함수는 별도의 Alert Condition으로 설정되므로 독립적으로 작동
- 하나의 Alert Policy에 여러 Condition이 있으면, 하나라도 조건을 만족하면 알림 전송

