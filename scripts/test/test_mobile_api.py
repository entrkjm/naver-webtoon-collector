"""
모바일 API 테스트 스크립트

네이버 웹툰 모바일 버전의 API를 테스트합니다.
"""

import requests
import json
from pathlib import Path

# 모바일 User-Agent
MOBILE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9',
}

# 시도해볼 API 엔드포인트들
POSSIBLE_ENDPOINTS = [
    "https://m.comic.naver.com/webtoon/weekday",
    "https://comic.naver.com/api/webtoon/weekday",
    "https://comic.naver.com/api/webtoon/list",
    "https://comic.naver.com/webtoon/weekday.nhn",
    "https://comic.naver.com/webtoon/list.nhn",
]

def test_endpoint(url):
    """API 엔드포인트를 테스트합니다."""
    print(f"\n{'='*60}")
    print(f"테스트: {url}")
    print('='*60)
    
    try:
        response = requests.get(url, headers=MOBILE_HEADERS, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"Content Length: {len(response.text)} bytes")
        
        # JSON인지 확인
        try:
            data = response.json()
            print(f"✅ JSON 응답 성공!")
            print(f"데이터 구조: {type(data)}")
            if isinstance(data, dict):
                print(f"키 목록: {list(data.keys())[:10]}")
            elif isinstance(data, list):
                print(f"리스트 길이: {len(data)}")
                if len(data) > 0:
                    print(f"첫 번째 항목: {json.dumps(data[0], ensure_ascii=False, indent=2)[:200]}")
            return True, data
        except json.JSONDecodeError:
            # HTML인 경우
            if 'webtoon' in response.text.lower() or 'comic' in response.text.lower():
                print("⚠️ HTML 응답 (웹툰 관련 키워드 포함)")
                # HTML에서 JSON 데이터 찾기
                import re
                json_pattern = r'\{[^{}]*"webtoon"[^{}]*\}'
                matches = re.findall(json_pattern, response.text[:5000])
                if matches:
                    print(f"✅ HTML 내 JSON 데이터 발견: {len(matches)}개")
                    return True, matches
            else:
                print("❌ JSON이 아닌 응답")
            return False, None
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False, None


if __name__ == "__main__":
    print("네이버 웹툰 API 엔드포인트 테스트 시작\n")
    
    results = []
    for endpoint in POSSIBLE_ENDPOINTS:
        success, data = test_endpoint(endpoint)
        results.append((endpoint, success, data))
    
    print("\n\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    for url, success, data in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{status}: {url}")
    
    # 성공한 엔드포인트 저장
    successful = [(url, data) for url, success, data in results if success]
    if successful:
        print(f"\n✅ {len(successful)}개 엔드포인트에서 데이터 발견!")
        for url, data in successful:
            output_file = Path(f"scripts/api_response_{url.split('/')[-1]}.json")
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"  저장됨: {output_file}")
            except:
                print(f"  데이터 저장 실패: {url}")

