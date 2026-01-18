# weekday_rank 필드 설명

## 핵심 답변

**`weekday_rank`는 네이버 웹툰 API에서 제공하지 않습니다.**

우리가 **각 요일 그룹 내에서 리스트 인덱스로 계산**해야 하는 필드입니다.

---

## 네이버 웹툰 API 응답 구조

### API 엔드포인트
```
https://comic.naver.com/api/webtoon/titlelist/weekday?order={view|user}
```

### API 응답 구조
```json
{
  "titleListMap": {
    "MONDAY": [
      {
        "titleId": "123456",
        "titleName": "웹툰 제목 1",
        "author": "작가명",
        "viewCount": 1234567
        // ⚠️ 여기에 순위 정보 없음!
      },
      {
        "titleId": "789012",
        "titleName": "웹툰 제목 2",
        "author": "작가명",
        "viewCount": 987654
        // ⚠️ 여기에 순위 정보 없음!
      },
      ...
    ],
    "TUESDAY": [
      {
        "titleId": "345678",
        "titleName": "웹툰 제목 3",
        ...
      },
      ...
    ],
    ...
  }
}
```

### API가 제공하는 정보
- ✅ `titleId`: 웹툰 ID
- ✅ `titleName`: 제목
- ✅ `author`: 작가명
- ✅ `viewCount`: 조회수
- ❌ **순위 정보 없음** (전체 순위도, 요일별 순위도 없음)

---

## weekday_rank 계산 방법

### 현재 코드 로직 (`parse_api.py`)

```python
# 1. API 응답에서 요일별로 그룹화
weekday_groups = {}
for item in webtoon_list:
    weekday = item.get('_weekday', 'UNKNOWN')
    if weekday not in weekday_groups:
        weekday_groups[weekday] = []
    weekday_groups[weekday].append(item)

# 2. 각 요일 그룹 내에서 순위 계산
global_rank = 1  # 전체 통합 순위
for weekday, items in weekday_groups.items():
    for idx, item in enumerate(items, start=1):  # ⭐ idx가 weekday_rank!
        webtoon_data = extract_webtoon_from_api_item(
            item, 
            rank=global_rank,      # 전체 통합 순위 (1, 2, 3, ...)
            weekday=weekday,       # 요일 정보 (MONDAY, TUESDAY, ...)
            weekday_rank=idx       # ⭐ 요일별 순위 (각 요일 내에서 1, 2, 3, ...)
        )
        global_rank += 1
```

### 예시

**API 응답**:
```json
{
  "titleListMap": {
    "MONDAY": [
      {"titleId": "111", "titleName": "월요일 웹툰 1"},
      {"titleId": "222", "titleName": "월요일 웹툰 2"},
      {"titleId": "333", "titleName": "월요일 웹툰 3"}
    ],
    "FRIDAY": [
      {"titleId": "444", "titleName": "금요일 웹툰 1"},
      {"titleId": "555", "titleName": "금요일 웹툰 2"}
    ]
  }
}
```

**계산 결과**:
| webtoon_id | weekday | rank (전체) | weekday_rank (요일별) |
|------------|---------|-------------|---------------------|
| 111 | MONDAY | 1 | 1 |
| 222 | MONDAY | 2 | 2 |
| 333 | MONDAY | 3 | 3 |
| 444 | FRIDAY | 4 | 1 |
| 555 | FRIDAY | 5 | 2 |

---

## 왜 weekday_rank가 필요한가?

### 문제 상황
- `rank`는 **전체 통합 순위** (모든 요일 합쳐서 1, 2, 3, ...)
- 수집 시점의 요일에 따라 편향됨
  - 월요일에 수집 → 월요일 웹툰이 상위권
  - 금요일에 수집 → 금요일 웹툰이 상위권

### 해결 방법
- `weekday_rank`는 **각 요일 내에서의 순위** (MONDAY 1위, 2위, 3위, ...)
- 요일별로 정확한 순위 비교 가능
- 일년간 평균/중위 순위 계산 가능

---

## 결론

1. **API는 순위 정보를 제공하지 않음**
2. **우리가 리스트 인덱스로 계산해야 함**
3. **`weekday_rank`는 각 요일 그룹 내에서 `enumerate(items, start=1)`로 계산**
4. **기존 코드에는 이 계산 로직이 있었지만, 저장하지 않았음**

---

## 다음 단계

1. ✅ BigQuery 스키마에 `weekday_rank` 컬럼 추가
2. ✅ 기존 데이터 마이그레이션 (요일별 순위 재계산)
3. ✅ 이후 수집부터 `weekday_rank` 저장
