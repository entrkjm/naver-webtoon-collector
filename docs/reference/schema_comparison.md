# 원본 데이터 vs BigQuery 테이블 스키마 비교

이 문서는 네이버 웹툰 API에서 수집되는 원본 데이터와 최종적으로 BigQuery에 저장되는 테이블 스키마를 비교합니다.

---

## 1. 차트 데이터 (주간 차트 API)

### 원본 API 응답 구조

**API 엔드포인트**: `https://comic.naver.com/api/webtoon/titlelist/weekday?order={view|user}`

**응답 구조**:
```json
{
  "titleListMap": {
    "MONDAY": [
      {
        "titleId": "123456",        // 웹툰 ID
        "titleName": "웹툰 제목",     // 제목
        "author": "작가명",          // 작가 (선택적)
        "viewCount": 1234567,       // 조회수 (조회순 정렬 시)
        "starScore": 9.8            // 별점 (저장하지 않음)
      },
      ...
    ],
    "TUESDAY": [...],
    ...
  }
}
```

### 원본 필드 → 파싱 후 필드 매핑

| 원본 API 필드 | 파싱 후 필드 | 설명 | 저장 여부 |
|--------------|-------------|------|----------|
| `titleId` | `webtoon_id` | 웹툰 고유 ID | ✅ 저장 |
| `titleName` | `title` | 웹툰 제목 | ✅ 저장 |
| `author` | `author` | 작가명 | ✅ 저장 (선택적) |
| `viewCount` | `view_count` | 조회수 | ✅ 저장 (조회순 정렬 시) |
| `starScore` | - | 별점 | ❌ 저장하지 않음 |
| `_weekday` | `weekday` | 요일 정보 (MONDAY, TUESDAY 등) | ✅ 저장 |
| - | `rank` | 순위 (리스트 인덱스 기반 계산) | ✅ 저장 |

### 최종 BigQuery 테이블: `fact_weekly_chart`

| BigQuery 컬럼 | 타입 | 원본 필드 | 변환 로직 | 비고 |
|--------------|------|----------|----------|------|
| `chart_date` | DATE | - | 수집 날짜 (현재 날짜) | Partition Key |
| `webtoon_id` | STRING | `titleId` | 문자열 변환 | Foreign Key → dim_webtoon |
| `rank` | INTEGER | - | 리스트 인덱스 기반 계산 | 1부터 시작 |
| `collected_at` | TIMESTAMP | - | 현재 시각 | 자동 생성 |
| `weekday` | STRING | `_weekday` | titleListMap의 키 | NULLABLE |
| `year` | INTEGER | - | `collected_at`에서 추출 | 자동 계산 |
| `month` | INTEGER | - | `collected_at`에서 추출 | 자동 계산 |
| `week` | INTEGER | - | `collected_at`에서 추출 (월의 몇 번째 주) | 자동 계산 |
| `view_count` | INTEGER | `viewCount` | 정수 변환 | NULLABLE |

**변환 과정**:
1. API 응답에서 `titleListMap` 추출
2. 각 요일별로 그룹화하여 순위 계산
3. `extract_webtoon_from_api_item()` 함수로 필드 추출
4. `create_fact_weekly_chart_record()` 함수로 스키마에 맞게 변환
5. BigQuery에 MERGE 작업으로 저장

---

## 2. 웹툰 마스터 데이터 (차트 API + 상세 정보 API)

### 원본 데이터 소스

#### 2-1. 차트 API에서 수집되는 필드

| 원본 API 필드 | 파싱 후 필드 | 설명 |
|--------------|-------------|------|
| `titleId` | `webtoon_id` | 웹툰 고유 ID |
| `titleName` | `title` | 웹툰 제목 |
| `author` | `author` | 작가명 (선택적) |

#### 2-2. 상세 정보 API에서 수집되는 필드

**API 엔드포인트**: `https://comic.naver.com/api/article/list/info?titleId={webtoon_id}`

**응답 구조**:
```json
{
  "favoriteCount": 123456,          // 관심 수
  "finished": false,                // 완결 여부
  "rest": false,                    // 휴재 여부
  "gfpAdCustomParam": {
    "genreTypes": ["로맨스", "판타지"]  // 장르 리스트
  },
  "curationTagList": [
    {"tagName": "로맨스"},           // 태그 리스트
    {"tagName": "판타지"}
  ]
}
```

| 원본 API 필드 | 파싱 후 필드 | 설명 | 변환 로직 |
|--------------|-------------|------|----------|
| `favoriteCount` | `favorite_count` | 관심 수 | 정수 변환 |
| `finished` | `finished` | 완결 여부 | 불린 변환 |
| `rest` | `rest` | 휴재 여부 | 불린 변환 |
| `gfpAdCustomParam.genreTypes[0]` | `genre` | 장르 (첫 번째만) | 배열의 첫 번째 값 |
| `curationTagList[].tagName` | `tags` | 태그 리스트 | 배열로 변환 |

### 최종 BigQuery 테이블: `dim_webtoon`

| BigQuery 컬럼 | 타입 | 원본 필드 | 변환 로직 | 비고 |
|--------------|------|----------|----------|------|
| `webtoon_id` | STRING | `titleId` (차트 API) | 문자열 변환 | Primary Key |
| `title` | STRING | `titleName` (차트 API) | 문자열 변환 | 필수 필드 |
| `author` | STRING | `author` (차트 API) | 문자열 변환 | NULLABLE |
| `genre` | STRING | `gfpAdCustomParam.genreTypes[0]` (상세 API) | 배열의 첫 번째 값 | NULLABLE |
| `tags` | ARRAY<STRING> | `curationTagList[].tagName` (상세 API) | 배열로 변환 | REPEATED, NULLABLE |
| `created_at` | TIMESTAMP | - | 현재 시각 | 자동 생성 |
| `updated_at` | TIMESTAMP | - | 현재 시각 | 자동 생성 |

**변환 과정**:
1. 차트 API에서 `webtoon_id`, `title`, `author` 수집
2. 상세 정보 API에서 `genre`, `tags` 수집 (별도 API 호출)
3. `create_dim_webtoon_record()` 함수로 스키마에 맞게 변환
4. BigQuery에 MERGE 작업으로 저장 (중복 방지 및 업데이트)

**참고**:
- `genre`는 상세 정보 API의 `genreTypes` 배열에서 첫 번째 값만 저장
- `tags`는 `curationTagList` 배열의 모든 `tagName`을 추출하여 ARRAY<STRING>으로 저장
- `author`는 차트 API에서 수집되지만, 항상 제공되지 않을 수 있음

---

## 3. 웹툰 상세 정보 히스토리 데이터

### 원본 API 응답 구조

**API 엔드포인트 1**: `https://comic.naver.com/api/article/list/info?titleId={webtoon_id}`
**API 엔드포인트 2**: `https://comic.naver.com/api/article/list?titleId={webtoon_id}&page=1` (에피소드 수)

**응답 구조**:
```json
{
  "favoriteCount": 123456,          // 관심 수
  "finished": false,                // 완결 여부
  "rest": false,                    // 휴재 여부
  "totalCount": 100                 // 전체 에피소드 수 (별도 API)
}
```

### 원본 필드 → 파싱 후 필드 매핑

| 원본 API 필드 | 파싱 후 필드 | 설명 | 저장 여부 |
|--------------|-------------|------|----------|
| `favoriteCount` | `favorite_count` | 관심 수 | ✅ 저장 |
| `finished` | `finished` | 완결 여부 | ✅ 저장 |
| `rest` | `rest` | 휴재 여부 | ✅ 저장 |
| `totalCount` | `total_episode_count` | 전체 에피소드 수 | ✅ 저장 (별도 API) |
| - | `favorite_count_source` | 데이터 소스 ("api" 또는 "html") | ✅ 저장 |

**HTML 파싱 대체**:
- API 실패 시 HTML에서 `favorite_count` 파싱 시도
- HTML 파싱 성공 시 `favorite_count_source = "html"`

### 최종 BigQuery 테이블: `fact_webtoon_stats`

| BigQuery 컬럼 | 타입 | 원본 필드 | 변환 로직 | 비고 |
|--------------|------|----------|----------|------|
| `webtoon_id` | STRING | - | 웹툰 ID (파라미터) | Foreign Key → dim_webtoon |
| `collected_at` | TIMESTAMP | - | 현재 시각 | Partition Key |
| `favorite_count` | INTEGER | `favoriteCount` (API) 또는 HTML 파싱 | 정수 변환 | NULLABLE |
| `favorite_count_source` | STRING | - | "api" 또는 "html" | NULLABLE |
| `finished` | BOOLEAN | `finished` (API) | 불린 변환 | NULLABLE |
| `rest` | BOOLEAN | `rest` (API) | 불린 변환 | NULLABLE |
| `total_episode_count` | INTEGER | `totalCount` (별도 API) | 정수 변환 | NULLABLE |
| `year` | INTEGER | - | `collected_at`에서 추출 | 자동 계산 |
| `month` | INTEGER | - | `collected_at`에서 추출 | 자동 계산 |
| `week` | INTEGER | - | `collected_at`에서 추출 (월의 몇 번째 주) | 자동 계산 |

**변환 과정**:
1. 상세 정보 API 호출 (`/api/article/list/info`)
2. 에피소드 수 API 호출 (`/api/article/list?page=1`)
3. API 실패 시 HTML 파싱 시도 (관심 수만)
4. `create_fact_webtoon_stats_record()` 함수로 스키마에 맞게 변환
5. BigQuery에 MERGE 작업으로 저장

---

## 4. 필드 변환 요약

### 추가되는 필드 (원본에 없음)

| 필드 | 설명 | 생성 방법 |
|------|------|----------|
| `chart_date` | 수집 날짜 | 현재 날짜 |
| `collected_at` | 수집 시각 | 현재 시각 |
| `rank` | 순위 | 리스트 인덱스 기반 계산 |
| `year`, `month`, `week` | 시간 정보 | `collected_at`에서 추출 |
| `favorite_count_source` | 데이터 소스 | "api" 또는 "html" |
| `created_at`, `updated_at` | 타임스탬프 | 현재 시각 |

### 제거되는 필드 (원본에 있지만 저장하지 않음)

| 원본 필드 | 설명 | 제거 이유 |
|----------|------|----------|
| `starScore` | 별점 | 현재 사용하지 않음 (향후 확장 가능) |

### 변환되는 필드

| 원본 필드 | 최종 필드 | 변환 로직 |
|----------|----------|----------|
| `titleId` | `webtoon_id` | 문자열 변환 |
| `titleName` | `title` | 문자열 변환 |
| `viewCount` | `view_count` | 정수 변환 |
| `favoriteCount` | `favorite_count` | 정수 변환 |
| `genreTypes[0]` | `genre` | 배열의 첫 번째 값만 |
| `curationTagList[].tagName` | `tags` | 배열로 변환 (ARRAY<STRING>) |

---

## 5. 데이터 흐름 다이어그램

```
[차트 API]
  ↓
titleId, titleName, author, viewCount, _weekday
  ↓
[parse_api.py]
  ↓
webtoon_id, title, author, view_count, weekday, rank
  ↓
[transform.py]
  ↓
┌─────────────────────┬──────────────────────────┐
│  dim_webtoon        │  fact_weekly_chart       │
│  - webtoon_id       │  - chart_date            │
│  - title            │  - webtoon_id            │
│  - author           │  - rank                  │
│  - genre (나중에)   │  - weekday               │
│  - tags (나중에)    │  - view_count            │
│                     │  - year, month, week     │
└─────────────────────┴──────────────────────────┘

[상세 정보 API]
  ↓
favoriteCount, finished, rest, genreTypes, curationTagList, totalCount
  ↓
[parse_webtoon_detail.py]
  ↓
favorite_count, finished, rest, genre, tags, total_episode_count
  ↓
[transform.py / transform_webtoon_stats.py]
  ↓
┌─────────────────────┬──────────────────────────┐
│  dim_webtoon        │  fact_webtoon_stats      │
│  (업데이트)         │  - webtoon_id            │
│  - genre 추가       │  - favorite_count        │
│  - tags 추가        │  - finished              │
│                     │  - rest                  │
│                     │  - total_episode_count   │
│                     │  - year, month, week     │
└─────────────────────┴──────────────────────────┘
```

---

## 6. 주요 변환 로직

### 6-1. 순위 계산 (`rank`)

```python
# parse_api.py의 extract_webtoon_from_api_item()
# 요일별로 그룹화하여 각 요일 내에서 순위 계산
global_rank = 1
for weekday, items in weekday_groups.items():
    for idx, item in enumerate(items, start=1):
        webtoon_data = extract_webtoon_from_api_item(
            item, 
            rank=global_rank,  # 전체 순위
            weekday=weekday
        )
        global_rank += 1
```

### 6-2. 장르 추출 (`genre`)

```python
# parse_webtoon_detail.py의 parse_api_response()
genre = None
if 'gfpAdCustomParam' in api_data:
    genre_types = api_data['gfpAdCustomParam'].get('genreTypes', [])
    if genre_types and len(genre_types) > 0:
        genre = genre_types[0]  # 첫 번째 장르만 저장
```

### 6-3. 태그 추출 (`tags`)

```python
# parse_webtoon_detail.py의 parse_api_response()
tags = []
if 'curationTagList' in api_data:
    for tag_item in api_data['curationTagList']:
        if 'tagName' in tag_item:
            tags.append(tag_item['tagName'])
```

### 6-4. 시간 정보 계산 (`year`, `month`, `week`)

```python
# models.py의 create_fact_weekly_chart_record()
year = now.year
month = now.month
# 해당 월의 몇 번째 주인지 계산: (day - 1) // 7 + 1
week = ((now.day - 1) // 7) + 1
```

---

## 7. 참고사항

### 데이터 수집 순서

1. **차트 데이터 수집** (차트 API)
   - `dim_webtoon` 생성 (webtoon_id, title, author)
   - `fact_weekly_chart` 생성

2. **상세 정보 수집** (상세 정보 API)
   - `dim_webtoon` 업데이트 (genre, tags 추가)
   - `fact_webtoon_stats` 생성

### 멱등성 보장

- **dim_webtoon**: `webtoon_id` 기준 MERGE (중복 방지 및 업데이트)
- **fact_weekly_chart**: `(chart_date, webtoon_id, weekday)` 기준 MERGE
- **fact_webtoon_stats**: `(webtoon_id, collected_at)` 기준 MERGE

### NULL 처리

- 원본 API에서 제공하지 않는 필드는 NULL로 저장
- `author`, `genre`, `tags` 등은 선택적 필드 (NULLABLE)
- `view_count`는 조회순 정렬 시에만 제공됨

---

## 8. 관련 파일

- **원본 데이터 수집**: `src/extract.py`, `src/extract_webtoon_detail.py`
- **데이터 파싱**: `src/parse_api.py`, `src/parse_webtoon_detail.py`
- **데이터 변환**: `src/transform.py`, `src/transform_webtoon_stats.py`
- **데이터 모델**: `src/models.py`
- **BigQuery 업로드**: `src/upload_bigquery.py`
- **스키마 문서**: `docs/reference/bigquery_schema.md`

