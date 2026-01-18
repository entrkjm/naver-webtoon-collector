"""
Extract 모듈: 네이버 웹툰 페이지 HTML 수집

이 모듈은 네이버 웹툰 주간 차트 페이지의 HTML을 수집하여
로컬 파일 시스템에 저장합니다 (GCS 대체).

주의: 
1. 먼저 API 엔드포인트를 찾아서 requests로 직접 호출 시도
2. API를 찾을 수 없으면 모바일 버전 HTML 수집 시도
3. 그래도 안 되면 Selenium 사용 (Cloud Functions에서는 비권장)
"""

import logging
import time
from datetime import date
from pathlib import Path
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.utils import get_raw_html_dir, setup_logging

logger = logging.getLogger(__name__)

# 네이버 웹툰 주간 차트 URL
NAVER_WEBTOON_CHART_URL = "https://comic.naver.com/webtoon"
NAVER_WEBTOON_MOBILE_URL = "https://m.comic.naver.com/webtoon/weekday"

# 정렬 방식
SORT_POPULAR = "user"     # 인기순 (API에서는 "user" 사용)
SORT_VIEW = "view"        # 조회순

# API 엔드포인트 (브라우저 네트워크 요청 분석 결과)
# 실제 API: https://comic.naver.com/api/webtoon/titlelist/weekday?order={view|user}
WEBTOON_API_ENDPOINTS = [
    {
        "url": "https://comic.naver.com/api/webtoon/titlelist/weekday",
        "params": {"order": "view"},
        "sort_type": "view"
    },
    {
        "url": "https://comic.naver.com/api/webtoon/titlelist/weekday",
        "params": {"order": "user"},
        "sort_type": "popular"  # 사용자에게는 "popular"로 표시
    },
]


def create_session() -> requests.Session:
    """
    재시도 로직이 포함된 requests 세션을 생성합니다.
    브라우저 동작을 흉내내기 위해 필요한 헤더를 설정합니다.
    
    Returns:
        설정된 requests.Session 객체
    """
    session = requests.Session()
    
    # 브라우저 동작 흉내내기: 실제 브라우저가 보내는 헤더 설정
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',  # API 요청이므로 JSON Accept
        'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://comic.naver.com/webtoon',  # API 요청 시 필수
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'DNT': '1',
    })
    
    # 재시도 전략 설정
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def try_api_endpoints(sort_type: Optional[str] = None) -> Optional[dict]:
    """
    알려진 API 엔드포인트를 시도하여 데이터를 가져옵니다.
    
    Args:
        sort_type: 정렬 방식 ("popular" 또는 "view"), None이면 모든 정렬 시도
    
    Returns:
        JSON 데이터 (실패 시 None)
    """
    if not WEBTOON_API_ENDPOINTS:
        logger.info("API 엔드포인트가 설정되지 않았습니다.")
        return None
    
    session = create_session()
    
    # 정렬 타입 필터링
    # sort_type이 "popular"면 "user"로 매핑 (API에서는 "user" 사용)
    endpoints_to_try = WEBTOON_API_ENDPOINTS
    if sort_type:
        if sort_type == "popular":
            # API에서는 "popular"가 아니라 "user"를 사용
            endpoints_to_try = [ep for ep in WEBTOON_API_ENDPOINTS if ep.get("sort_type") == "popular"]
        else:
            endpoints_to_try = [ep for ep in WEBTOON_API_ENDPOINTS if ep.get("sort_type") == sort_type]
    
    for endpoint_config in endpoints_to_try:
        try:
            url = endpoint_config.get("url")
            params = endpoint_config.get("params", {})
            sort_type_name = endpoint_config.get("sort_type", "unknown")
            
            logger.info(f"API 엔드포인트 시도: {url} (정렬: {sort_type_name}, order={params.get('order')})")
            
            # 요청 전 딜레이 (과도한 요청 방지)
            time.sleep(1)
            
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # JSON 응답 확인
            try:
                data = response.json()
                logger.info(f"✅ API에서 데이터 수집 성공: {len(str(data))} bytes (정렬: {sort_type_name})")
                
                # 정렬 타입 정보 추가
                if isinstance(data, dict):
                    data["_sort_type"] = sort_type_name
                    data["_api_url"] = url
                    data["_api_params"] = params
                
                return data
            except ValueError as e:
                logger.warning(f"JSON 파싱 실패: {url}, 오류: {e}")
                logger.debug(f"응답 내용: {response.text[:500]}")
                continue
                
        except requests.RequestException as e:
            logger.warning(f"API 엔드포인트 실패: {endpoint_config}, 오류: {e}")
            continue
        except Exception as e:
            logger.error(f"예상치 못한 오류: {endpoint_config}, 오류: {e}")
            continue
    
    return None


def fetch_webtoon_chart_html(url: Optional[str] = None, use_mobile: bool = True, sort_type: Optional[str] = None, chart_date: Optional[date] = None) -> Optional[str]:
    """
    네이버 웹툰 주간 차트 페이지의 HTML을 수집합니다.
    
    우선순위:
    1. API 엔드포인트 시도 (정렬 파라미터 포함)
    2. 모바일 버전 HTML 수집 (더 단순할 수 있음)
    3. 데스크톱 버전 HTML 수집
    
    Args:
        url: 웹툰 차트 URL (None이면 기본 URL 사용)
        use_mobile: 모바일 버전 사용 여부
        sort_type: 정렬 방식 ("popular" 또는 "view"), None이면 기본값
    
    Returns:
        HTML 문자열 (실패 시 None)
    """
    # 1. API 엔드포인트 시도 (정렬 파라미터 포함)
    api_data = try_api_endpoints(sort_type=sort_type)
    if api_data:
        # API 데이터를 JSON 파일로 저장 (GCS 업로드용)
        import json
        if chart_date is None:
            chart_date = date.today()
        json_path = save_json_to_file(api_data, chart_date, sort_type=sort_type)
        
        # HTML 형식으로도 저장 (파싱용, 기존 로직 유지)
        sort_info = f"<!-- Sort Type: {api_data.get('_sort_type', 'unknown')} -->\n"
        html = f"{sort_info}<!-- API Response -->\n<script type='application/json' id='webtoon-data'>{json.dumps(api_data, ensure_ascii=False)}</script>"
        return html
    
    # 2. HTML 수집
    if url is None:
        url = NAVER_WEBTOON_MOBILE_URL if use_mobile else NAVER_WEBTOON_CHART_URL
    
    logger.info(f"웹툰 차트 페이지 수집 시작: {url}")
    
    try:
        session = create_session()
        
        # 모바일 버전인 경우 User-Agent 변경
        if use_mobile:
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
            })
        
        # 정렬 파라미터 추가 (URL에 쿼리 파라미터로)
        params = {}
        if sort_type:
            params['sort'] = sort_type
        
        # 요청 전 딜레이 (과도한 요청 방지)
        time.sleep(1)
        
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        html = response.text
        logger.info(f"HTML 수집 성공: {len(html)} bytes")
        return html
        
    except Exception as e:
        logger.error(f"HTML 수집 실패: {e}")
        return None


def save_json_to_file(json_data: dict, chart_date: date, filename: Optional[str] = None, sort_type: Optional[str] = None) -> Optional[Path]:
    """
    API 응답 JSON을 로컬 파일로 저장합니다.
    
    Args:
        json_data: 저장할 JSON 데이터
        chart_date: 수집 날짜
        filename: 저장할 파일명 (None이면 정렬 타입에 따라 자동 생성)
        sort_type: 정렬 방식 ("popular" 또는 "view")
    
    Returns:
        저장된 파일의 Path 객체 (실패 시 None)
    """
    save_dir = get_raw_html_dir(chart_date)
    
    # 파일명 생성 (정렬 타입 포함)
    if filename is None:
        if sort_type:
            filename = f"webtoon_chart_{sort_type}.json"
        else:
            filename = "webtoon_chart.json"
    
    file_path = save_dir / filename
    
    try:
        import json
        file_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding='utf-8')
        logger.info(f"JSON 저장 완료: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"JSON 저장 실패: {file_path}, 오류: {e}")
        return None


def save_html_to_file(html: str, chart_date: date, filename: Optional[str] = None, sort_type: Optional[str] = None) -> Path:
    """
    수집한 HTML을 로컬 파일로 저장합니다.
    
    Args:
        html: 저장할 HTML 문자열
        chart_date: 수집 날짜
        filename: 저장할 파일명 (None이면 정렬 타입에 따라 자동 생성)
        sort_type: 정렬 방식 ("popular" 또는 "view")
    
    Returns:
        저장된 파일의 Path 객체
    """
    save_dir = get_raw_html_dir(chart_date)
    
    # 파일명 생성 (정렬 타입 포함)
    if filename is None:
        if sort_type:
            filename = f"webtoon_chart_{sort_type}.html"
        else:
            filename = "webtoon_chart.html"
    
    file_path = save_dir / filename
    
    try:
        file_path.write_text(html, encoding='utf-8')
        logger.info(f"HTML 저장 완료: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"HTML 저장 실패: {file_path}, 오류: {e}")
        raise


def extract_webtoon_chart(chart_date: Optional[date] = None, url: Optional[str] = None, use_mobile: bool = True, sort_type: Optional[str] = None) -> Optional[Path]:
    """
    네이버 웹툰 주간 차트를 수집하여 로컬에 저장합니다.
    
    Args:
        chart_date: 수집 날짜 (None이면 오늘 날짜 사용)
        url: 웹툰 차트 URL (None이면 기본 URL 사용)
        use_mobile: 모바일 버전 사용 여부
        sort_type: 정렬 방식 ("popular" 또는 "view"), None이면 기본값
    
    Returns:
        저장된 HTML 파일의 Path 객체 (실패 시 None)
    """
    if chart_date is None:
        chart_date = date.today()
    
    try:
        # HTML 수집 (모바일 버전 우선 시도, 정렬 파라미터 포함)
        html = fetch_webtoon_chart_html(url, use_mobile=use_mobile, sort_type=sort_type, chart_date=chart_date)
        
        if html is None:
            logger.error("HTML 수집 실패")
            return None
        
        # 파일로 저장 (정렬 타입 포함)
        file_path = save_html_to_file(html, chart_date, sort_type=sort_type)
        
        logger.info(f"웹툰 차트 수집 완료: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"웹툰 차트 수집 중 오류 발생: {e}")
        return None


if __name__ == "__main__":
    # 테스트 실행
    setup_logging()
    result = extract_webtoon_chart()
    if result:
        print(f"수집 완료: {result}")
    else:
        print("수집 실패")
