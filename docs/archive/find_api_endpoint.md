# 네이버 웹툰 API 엔드포인트 찾기 가이드

## 방법: 브라우저 개발자 도구 사용

### 1단계: 브라우저에서 페이지 열기
1. Chrome 또는 Firefox 브라우저 열기
2. `https://comic.naver.com/webtoon` 접속
3. 개발자 도구 열기 (F12 또는 Cmd+Option+I)

### 2단계: Network 탭에서 API 요청 찾기
1. 개발자 도구에서 **Network** 탭 클릭
2. 필터 설정:
   - **XHR** 또는 **Fetch** 선택 (API 요청만 보기)
   - 또는 **JS** 선택 (JavaScript 파일 확인)
3. 페이지 새로고침 (F5)
4. 네트워크 요청 목록 확인

### 3단계: 차트 데이터를 가져오는 API 찾기
다음과 같은 요청을 찾아보세요:

**예상되는 API 패턴:**
- URL에 `webtoon`, `chart`, `rank`, `list`, `weekday` 같은 키워드 포함
- 응답이 JSON 형식
- 요청 메서드: GET 또는 POST

**확인할 사항:**
1. **Request URL**: API 엔드포인트 주소
2. **Request Headers**: 필요한 헤더 (Authorization, Cookie 등)
3. **Response**: 실제 데이터 구조

### 4단계: API 정보 기록
찾은 API 정보를 아래 형식으로 기록하세요:

```
API 엔드포인트: https://...
요청 메서드: GET/POST
필요한 헤더:
  - User-Agent: ...
  - Cookie: ... (필요시)
  - Referer: ... (필요시)
응답 형식: JSON
응답 예시:
{
  "data": [...]
}
```

### 5단계: Python으로 테스트
```python
import requests

url = "찾은_API_엔드포인트"
headers = {
    "User-Agent": "Mozilla/5.0 ...",
    # 필요한 다른 헤더들
}

response = requests.get(url, headers=headers)
data = response.json()
print(data)
```

## 대안: 모바일 API 확인
네이버 웹툰 모바일 버전(`https://m.comic.naver.com/webtoon/weekday`)도 확인해보세요.
모바일 API가 더 단순할 수 있습니다.

