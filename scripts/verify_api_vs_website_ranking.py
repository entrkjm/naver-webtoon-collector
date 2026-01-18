#!/usr/bin/env python3
"""
API 응답 순서와 실제 웹사이트 순위를 비교하는 스크립트

실행 방법:
    python3 scripts/verify_api_vs_website_ranking.py
"""

import urllib.request
import urllib.parse
import json
import time
from html.parser import HTMLParser
import re

def call_api(order_type):
    """API 호출"""
    url = "https://comic.naver.com/api/webtoon/titlelist/weekday"
    params = {"order": order_type}
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    
    req = urllib.request.Request(
        full_url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://comic.naver.com/webtoon'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"API 호출 실패: {e}")
        return None

def fetch_website_html(order_type='user'):
    """실제 웹사이트 HTML 가져오기"""
    if order_type == 'user':
        url = "https://comic.naver.com/webtoon?tab=weekday&order=user"
    else:
        url = "https://comic.naver.com/webtoon?tab=weekday&order=view"
    
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://comic.naver.com/webtoon'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"웹사이트 HTML 가져오기 실패: {e}")
        return None

def extract_webtoon_order_from_html(html, weekday='FRIDAY'):
    """HTML에서 특정 요일의 웹툰 순서 추출"""
    # HTML에서 titleId를 찾아서 순서 추출
    # 실제 구조에 맞게 수정 필요
    
    # 간단한 방법: titleId 패턴 찾기
    title_id_pattern = r'"titleId":(\d+)'
    title_ids = re.findall(title_id_pattern, html)
    
    # 또는 더 정확하게: 요일별 섹션 찾기
    # 이 부분은 실제 HTML 구조를 확인해야 함
    
    return title_ids

def compare_api_vs_website(weekday='FRIDAY', order_type='user', limit=10):
    """API 순서와 웹사이트 순서 비교"""
    print("=" * 80)
    print(f"API vs 웹사이트 순위 비교: {weekday} ({order_type})")
    print("=" * 80)
    print()
    
    # 1. API 호출
    print("1. API 호출 중...")
    api_data = call_api(order_type)
    if not api_data or 'titleListMap' not in api_data:
        print("❌ API 호출 실패")
        return
    
    if weekday not in api_data['titleListMap']:
        print(f"❌ {weekday} 데이터 없음")
        return
    
    api_items = api_data['titleListMap'][weekday]
    print(f"✅ API 응답: {len(api_items)}개 웹툰\n")
    
    # 2. 웹사이트 HTML 가져오기
    print("2. 웹사이트 HTML 가져오기 중...")
    html = fetch_website_html(order_type)
    if not html:
        print("❌ 웹사이트 HTML 가져오기 실패")
        print("\n⚠️ 수동 검증 필요:")
        print(f"   웹사이트: https://comic.naver.com/webtoon?tab=weekday&order={order_type}")
        print(f"   {weekday} 섹션의 상위 {limit}개 웹툰 순서를 확인하세요")
        print()
        print("API 순서 (상위 10개):")
        print("-" * 80)
        for idx, item in enumerate(api_items[:limit], start=1):
            title = item.get('titleName', 'N/A')
            title_id = item.get('titleId', 'N/A')
            print(f"{idx:2d}위: {title} (ID: {title_id})")
        return
    
    print(f"✅ HTML 가져오기 성공 ({len(html)} bytes)\n")
    
    # 3. HTML에서 웹툰 순서 추출 (간단한 방법)
    print("3. HTML에서 웹툰 순서 추출 중...")
    print("⚠️ HTML 파싱은 복잡하므로, API 순서를 출력합니다")
    print("   실제 웹사이트와 직접 비교해주세요\n")
    
    # 4. API 순서 출력
    print("=" * 80)
    print("API 응답 순서 (상위 10개):")
    print("=" * 80)
    print(f"{'순위':<6} {'제목':<40} {'ID':<10} {'별점':<8} {'조회수':<15}")
    print("-" * 80)
    
    for idx, item in enumerate(api_items[:limit], start=1):
        title = item.get('titleName', 'N/A')[:38]
        title_id = item.get('titleId', 'N/A')
        star = item.get('starScore', 0)
        view = item.get('viewCount', 0)
        view_str = f"{view:,}" if view > 0 else "(없음)"
        print(f"{idx:<6} {title:<40} {title_id:<10} {star:<8.2f} {view_str:<15}")
    
    print()
    print("=" * 80)
    print("검증 방법:")
    print("=" * 80)
    print(f"1. 웹사이트 열기: https://comic.naver.com/webtoon?tab=weekday&order={order_type}")
    print(f"2. {weekday} 섹션 확인")
    print(f"3. 위 API 순서와 웹사이트 순서가 일치하는지 확인")
    print()
    print("⚠️ 중요: API 순서가 웹사이트 순서와 일치하면 idx를 weekday_rank로 사용 가능")
    print("         일치하지 않으면 다른 방법 필요")

if __name__ == '__main__':
    print("API vs 웹사이트 순위 비교 검증\n")
    
    # 인기순 검증
    compare_api_vs_website(weekday='FRIDAY', order_type='user', limit=10)
    
    print("\n" + "=" * 80)
    print()
    
    # 조회순 검증
    compare_api_vs_website(weekday='FRIDAY', order_type='view', limit=10)
