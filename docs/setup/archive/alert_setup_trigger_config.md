# Alert Policy Trigger 설정 가이드

> **Configure alert trigger** 단계 설정 방법

---

## 🎯 Cloud Function 실행 실패 감지 설정

### 현재 화면에서 설정할 값

#### 1. Condition Type
- ✅ **"Threshold"** 선택 (이미 선택되어 있을 수 있음)
  - "Condition triggers if a time series rises above or falls below a value for a specific duration window"

#### 2. Alert trigger
- ✅ **"Any time series violates"** 선택 (이미 선택되어 있을 수 있음)

#### 3. Threshold position
- ✅ **"Above threshold"** 선택 (이미 선택되어 있을 수 있음)

#### 4. Threshold value
- **입력란에 `0` 입력**
  - 현재 `/s` (초당)로 표시되어 있지만, 숫자 `0`을 입력하면 됩니다
  - 의미: ERROR 로그가 1개라도 발생하면 알림

#### 5. Advanced Options (선택사항)
- **Duration**: `1 minute` 선택 (기본값일 수 있음)
- **Evaluation window**: `1 minute` 선택

#### 6. Condition name
- 이미 `Cloud Function - Log entries`로 설정되어 있음
- 그대로 두거나 원하는 이름으로 변경 가능

---

## ✅ 설정 요약

**최종 설정값:**
- Condition Type: **Threshold**
- Alert trigger: **Any time series violates**
- Threshold position: **Above threshold**
- Threshold value: **0**
- Duration: **1 minute** (Advanced Options에서)

**의미:**
- ERROR 로그가 1분 동안 1개라도 발생하면 알림 전송

---

## 📝 다음 단계

설정 완료 후:

1. **"Save"** 또는 **"Next"** 버튼 클릭
2. 왼쪽 메뉴에서 **"Notifications and name"** 클릭
3. 알림 채널 추가
4. Alert name 입력
5. **"Create Policy"** 클릭

---

## 💡 참고

### Threshold value = 0의 의미

- `0`을 입력하면: ERROR 로그가 1개라도 발생하면 알림
- `1` 이상을 입력하면: 해당 개수 이상의 ERROR 로그가 발생해야 알림

**권장**: `0` (ERROR가 하나라도 발생하면 즉시 알림)

### Duration

- `1 minute`: 1분 동안 조건을 만족하면 알림
- 너무 짧으면: 잦은 알림 (노이즈)
- 너무 길면: 알림이 늦게 옴

**권장**: `1 minute` (빠른 알림)

---

## 🔄 다른 Condition Type 설명

### Metric absence
- 메트릭에 데이터가 없을 때 알림
- 이 경우에는 사용하지 않음

### Forecast preview
- 미래에 임계값을 넘을 것으로 예측될 때 알림
- 이 경우에는 사용하지 않음

**결론**: **Threshold**를 사용하세요!

