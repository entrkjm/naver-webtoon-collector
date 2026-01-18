# Alert Policy Filter Label 가이드

> **중요**: Cloud Function의 경우 label 이름이 다를 수 있습니다.

---

## 🔍 Cloud Function Filter Label 확인 방법

### 방법 1: Dropdown에서 확인

Filter 추가 화면에서:

1. **"Filter"** 드롭다운 클릭
2. 나타나는 목록에서 다음 중 하나를 찾으세요:
   - `resource.labels.service`
   - `resource.labels.function_name`
   - `resource.labels.service_name`
   - `resource.labels.region`
   - 기타 label들

### 방법 2: 실제 사용 가능한 Label

Cloud Function의 경우 일반적으로:

**가능한 Label들:**
- `resource.labels.service` ← **이것을 사용하세요!**
- `resource.labels.function_name`
- `resource.labels.region`
- `resource.labels.revision_name`

---

## ✅ 올바른 Filter 설정

### Cloud Function 실행 실패 감지

**Filter 1:**
- **Filter**: `resource.labels.service` 선택
- **Comparator**: `=` 또는 `equals`
- **Value**: `pipeline-function` 입력

**Filter 2:**
- **Filter**: `severity` 선택
- **Comparator**: `=` 또는 `equals`
- **Value**: `ERROR` 입력

---

## 🔄 대안: Log Query 사용

Filter가 복잡하면 Log Query를 직접 사용할 수도 있습니다:

1. **"View Code"** 버튼 클릭
2. 또는 MQL (Monitoring Query Language) 사용:

```
fetch cloud_function
| filter resource.labels.service == "pipeline-function"
| filter severity == "ERROR"
| group_by 1m
| every 1m
```

---

## 💡 팁

### Label 이름 확인

Filter 드롭다운을 열면 사용 가능한 모든 label이 표시됩니다. 다음을 찾아보세요:

- `resource.labels.service` ← 가장 가능성 높음
- `resource.labels.function_name`
- `resource.labels.service_name`

### Value 확인

`pipeline-function`이 정확한지 확인:

```bash
# Cloud Function 이름 확인
gcloud functions list --gen2 --region=asia-northeast3
```

---

## 📝 정리

**Filter 설정 순서:**

1. **"Add a filter"** 클릭
2. **"Filter"** 드롭다운에서 `resource.labels.service` 선택
3. **"Comparator"**: `=` 선택
4. **"Value"**: `pipeline-function` 입력
5. **"Done"** 클릭
6. 다시 **"Add a filter"** 클릭
7. **"Filter"**: `severity` 선택
8. **"Comparator"**: `=` 선택
9. **"Value"**: `ERROR` 입력
10. **"Done"** 클릭

---

## ❓ 문제 해결

### Label이 보이지 않는 경우

1. **Filter 드롭다운을 열어** 사용 가능한 label 목록 확인
2. `resource.labels.`로 시작하는 항목들을 찾아보세요
3. `service`, `function_name`, `service_name` 등을 확인

### 정확한 값 확인

Cloud Function의 정확한 이름 확인:

```bash
gcloud run services list --region=asia-northeast3
```

또는:

```bash
gcloud functions list --gen2 --region=asia-northeast3
```

