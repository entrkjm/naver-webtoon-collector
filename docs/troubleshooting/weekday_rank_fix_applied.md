# weekday_rank 수정 완료

## 문제 발견

검증 결과, **API 응답의 리스트 순서가 실제 순위와 일치하지 않습니다.**

### 검증 결과
- ❌ 조회순 (`order=view`): viewCount가 내림차순이 아님
- ❌ 인기순 (`order=user`): starScore가 내림차순이 아님

### 예시
```
MONDAY 조회순:
  리스트[0]: viewCount = 0
  리스트[1]: viewCount = 0
  리스트[7]: viewCount = 0
  리스트[8]: viewCount = 257,694,256  ← 순서 위반!
```

---

## 수정 내용

### `src/parse_api.py` 수정

**변경 전**:
```python
for weekday, items in weekday_groups.items():
    for idx, item in enumerate(items, start=1):  # ❌ 원본 순서 그대로 사용
        weekday_rank=idx
```

**변경 후**:
```python
# 정렬 타입 확인
sort_type = api_data.get('_sort_type', 'popular')

for weekday, items in weekday_groups.items():
    # ✅ 정렬 타입에 따라 재정렬
    if sort_type == 'view':
        items = sorted(items, key=lambda x: x.get('viewCount', 0), reverse=True)
    elif sort_type == 'popular':
        items = sorted(items, key=lambda x: x.get('starScore', 0), reverse=True)
    
    # 재정렬 후 순위 계산
    for idx, item in enumerate(items, start=1):
        weekday_rank=idx  # ✅ 올바른 순위
```

---

## 검증 방법

### 수정 전
- 리스트 인덱스를 그대로 순위로 사용
- 잘못된 순위 저장

### 수정 후
- viewCount 또는 starScore로 재정렬 후 순위 계산
- 올바른 순위 저장

---

## 영향 범위

1. ✅ **새로 수집되는 데이터**: 올바른 `weekday_rank` 저장
2. ⚠️ **기존 데이터**: 마이그레이션 필요 (재정렬 후 재계산)

---

## 다음 단계

1. ✅ 코드 수정 완료
2. ⚠️ **기존 데이터 마이그레이션**: BigQuery에서 재정렬 후 `weekday_rank` 재계산
3. ⚠️ **테스트**: 실제 수집 후 검증
