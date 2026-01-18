# weekday_rank 최종 결정

## 문제 재검토

### 사용자 지적
- `viewCount`는 대부분 0이거나 제공되지 않음
- `starScore`로도 정렬되어 있지 않음
- API가 제공하는 리스트 순서 자체가 순위일 가능성

### 확인 결과

**API 응답 구조**:
- `viewCount`: 20개 중 1개만 값이 있음 (대부분 0)
- `starScore`: 모든 항목에 값이 있지만, 리스트 순서와 일치하지 않음

**예시 (인기순, FRIDAY)**:
```
리스트[0]: 광마회귀, starScore=9.96, viewCount=0
리스트[1]: 역대급 영지 설계사, starScore=9.98, viewCount=0
리스트[2]: 오! 나의 교주님, starScore=9.17, viewCount=0
```

→ starScore가 내림차순이 아님 (9.96 < 9.98 < 9.17)

---

## 결론

**API가 제공하는 리스트 순서 자체가 순위입니다.**

1. `viewCount`는 대부분 제공되지 않음 (0)
2. `starScore`로도 정렬되어 있지 않음
3. API가 복잡한 알고리즘(인기도, 최신 업데이트 등)으로 정렬하여 제공
4. **리스트 인덱스(idx)를 weekday_rank로 사용하는 것이 맞음**

---

## 수정 내용

### 원래 코드로 복원

**변경 전 (잘못된 수정)**:
```python
# 재정렬 시도 (잘못됨)
if sort_type == 'view':
    items = sorted(items, key=lambda x: x.get('viewCount', 0), reverse=True)
elif sort_type == 'popular':
    items = sorted(items, key=lambda x: x.get('starScore', 0), reverse=True)
```

**변경 후 (올바른 코드)**:
```python
# API 응답의 리스트 순서를 그대로 순위로 사용
for idx, item in enumerate(items, start=1):
    weekday_rank=idx  # ✅ API가 제공하는 순서 = 순위
```

---

## 최종 결정

✅ **리스트 인덱스(idx)를 weekday_rank로 사용**
- API가 제공하는 리스트 순서 = 실제 순위
- 재정렬 불필요
- 원래 코드가 맞았음
