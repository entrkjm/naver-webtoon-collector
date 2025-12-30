# 네이버 웹툰 정렬 API 분석 가이드

## 목표
'인기순'과 '조회순' 정렬을 위한 API 엔드포인트 찾기

## 분석 방법

### 1단계: 브라우저에서 네트워크 요청 확인

1. Chrome 브라우저에서 `https://comic.naver.com/webtoon` 접속
2. 개발자 도구 열기 (F12)
3. **Network** 탭 열기
4. 필터 설정:
   - **XHR** 또는 **Fetch** 선택 (API 요청만 보기)
   - 또는 **All** 선택 후 필터에 `webtoon`, `list`, `rank` 등 입력

### 2단계: 정렬 버튼 클릭 시 요청 확인

1. 페이지가 로드되면 초기 요청 확인 (인기순 기본값)
2. **'조회순' 버튼 클릭**
3. Network 탭에서 새로 발생한 요청 확인

### 3단계: API 정보 기록

찾은 API 요청의 다음 정보를 기록하세요:

#### 인기순 API
```
URL: https://...
Method: GET/POST
Query Parameters 또는 Body:
  - sort=? (예: sort=popular, sort=view 등)
  - week=? (요일)
  - page=?
Headers:
  - User-Agent: ...
  - Cookie: ... (필요시)
  - Referer: ...
Response 형식: JSON/HTML
```

#### 조회순 API
```
URL: https://... (인기순과 같은 URL인지 확인)
Method: GET/POST
Query Parameters 또는 Body:
  - sort=? (다른 값인지 확인)
  - ...
```

### 4단계: 예상되는 패턴

네이버 웹툰의 경우 다음과 같은 패턴일 수 있습니다:

**옵션 1: URL 파라미터**
```
https://comic.naver.com/webtoon/list?sort=popular  (인기순)
https://comic.naver.com/webtoon/list?sort=view     (조회순)
```

**옵션 2: 별도 API 엔드포인트**
```
https://comic.naver.com/api/webtoon/popular
https://comic.naver.com/api/webtoon/view
```

**옵션 3: POST 요청 (Body에 파라미터)**
```
POST https://comic.naver.com/api/webtoon/list
Body: {"sort": "popular"} 또는 {"sort": "view"}
```

### 5단계: 모바일 버전도 확인

모바일 버전(`https://m.comic.naver.com/webtoon/weekday`)에서도 정렬 기능이 있는지 확인해보세요.
모바일 API가 더 단순할 수 있습니다.

## 찾은 정보를 코드에 반영

API를 찾으면 `src/extract.py`의 `WEBTOON_API_ENDPOINTS`에 추가하고,
정렬 파라미터를 전달하는 함수를 구현합니다.

