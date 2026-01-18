# weekday_rank 검증 필요사항

## ⚠️ 중요: 검증 필요

**`idx` (리스트 인덱스)가 실제 순위와 일치하는지 확인이 필요합니다.**

현재 코드는 API 응답의 리스트 순서를 그대로 사용하여 `weekday_rank`를 계산하고 있지만, **이게 실제 순위와 일치하는지 검증되지 않았습니다.**

---

## 검증 방법

### 1. API 응답 순서 확인

**조회순 (order=view)**:
- API 응답의 리스트 순서가 `viewCount` 내림차순인지 확인
- 리스트[0]의 viewCount >= 리스트[1]의 viewCount >= ... 이어야 함

**인기순 (order=user)**:
- API 응답의 리스트 순서가 `starScore` 내림차순인지 확인
- 리스트[0]의 starScore >= 리스트[1]의 starScore >= ... 이어야 함

### 2. 검증 스크립트 실행

```bash
# 가상환경 활성화 후
python3 scripts/verify_api_ranking_order.py
```

이 스크립트는:
1. API를 호출하여 실제 응답 확인
2. 각 요일별 리스트의 정렬 순서 검증
3. viewCount 또는 starScore로 정렬 순서 확인

---

## 만약 순서가 일치하지 않으면?

### 대안 1: viewCount/starScore로 재정렬

```python
# parse_api.py 수정
for weekday, items in weekday_groups.items():
    # 조회순인 경우: viewCount로 재정렬
    if sort_type == 'view':
        items = sorted(items, key=lambda x: x.get('viewCount', 0), reverse=True)
    # 인기순인 경우: starScore로 재정렬
    elif sort_type == 'popular':
        items = sorted(items, key=lambda x: x.get('starScore', 0), reverse=True)
    
    for idx, item in enumerate(items, start=1):
        # ...
```

### 대안 2: API 응답에 순위 필드가 있는지 확인

API 응답에 `rank` 필드나 다른 순위 정보가 있는지 확인 필요.

---

## 현재 코드 가정

현재 코드는 다음을 가정하고 있습니다:

1. **API 응답의 리스트 순서 = 실제 순위**
2. 리스트[0] = 1위, 리스트[1] = 2위, ...
3. `enumerate(items, start=1)`의 `idx`가 실제 순위와 일치

**이 가정이 맞는지 검증이 필요합니다.**

---

## 즉시 조치

1. ✅ 검증 스크립트 작성 완료 (`scripts/verify_api_ranking_order.py`)
2. ⚠️ **검증 스크립트 실행 필요** (가상환경에서)
3. ⚠️ 검증 결과에 따라 코드 수정 필요

---

## 참고

- API 엔드포인트: `https://comic.naver.com/api/webtoon/titlelist/weekday?order={view|user}`
- 조회순: `order=view` → viewCount 내림차순
- 인기순: `order=user` → starScore 내림차순 (추정)
