"""
Extract Webtoon Detail 모듈: 웹툰 상세 정보 수집

이 모듈은 웹툰 상세 정보를 수집합니다.
- API 우선 시도 (/api/article/list/info)
- API 실패 시 HTML 파싱 시도
- Rate limiting 적용
"""

import logging
import time
from typing import Optional, Dict, Any
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from src.extract import create_session

logger = logging.getLogger(__name__)

# 웹툰 상세 정보 API 엔드포인트
WEBTOON_DETAIL_API_URL = "https://comic.naver.com/api/article/list/info"
WEBTOON_EPISODE_API_URL = "https://comic.naver.com/api/article/list"
WEBTOON_DETAIL_PAGE_URL = "https://comic.naver.com/webtoon/list"


def fetch_webtoon_detail_api(webtoon_id: str, session: Optional[requests.Session] = None) -> Optional[Dict[str, Any]]:
    """
    API를 통해 웹툰 상세 정보를 수집합니다.
    
    Args:
        webtoon_id: 웹툰 ID
        session: requests Session 객체 (없으면 새로 생성)
    
    Returns:
        API 응답 데이터 (딕셔너리), 실패 시 None
    """
    if session is None:
        session = create_session()
    
    url = f"{WEBTOON_DETAIL_API_URL}?titleId={webtoon_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8',
        'Referer': f'{WEBTOON_DETAIL_PAGE_URL}?titleId={webtoon_id}',
        'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
    }
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.debug(f"API 응답 성공: webtoon_id={webtoon_id}")
            return data
        else:
            logger.warning(f"API 응답 실패: webtoon_id={webtoon_id}, status={response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"API 호출 실패: webtoon_id={webtoon_id}, 오류: {e}")
        return None


def fetch_webtoon_detail_html(webtoon_id: str, session: Optional[requests.Session] = None) -> Optional[str]:
    """
    HTML을 통해 웹툰 상세 페이지를 수집합니다.
    
    Args:
        webtoon_id: 웹툰 ID
        session: requests Session 객체 (없으면 새로 생성)
    
    Returns:
        HTML 문자열, 실패 시 None
    """
    if session is None:
        session = create_session()
    
    url = f"{WEBTOON_DETAIL_PAGE_URL}?titleId={webtoon_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8',
        'Referer': 'https://comic.naver.com/webtoon',
    }
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.debug(f"HTML 수집 성공: webtoon_id={webtoon_id}")
            return response.text
        else:
            logger.warning(f"HTML 수집 실패: webtoon_id={webtoon_id}, status={response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"HTML 수집 실패: webtoon_id={webtoon_id}, 오류: {e}")
        return None


def fetch_webtoon_episode_count(webtoon_id: str, session: Optional[requests.Session] = None) -> Optional[int]:
    """
    API를 통해 전체 에피소드 수를 가져옵니다.
    
    Args:
        webtoon_id: 웹툰 ID
        session: requests Session 객체 (없으면 새로 생성)
    
    Returns:
        전체 에피소드 수, 실패 시 None
    """
    if session is None:
        session = create_session()
    
    url = f"{WEBTOON_EPISODE_API_URL}?titleId={webtoon_id}&page=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8',
        'Referer': f'{WEBTOON_DETAIL_PAGE_URL}?titleId={webtoon_id}',
        'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
    }
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total_count = data.get('totalCount')
            if total_count is not None:
                logger.debug(f"에피소드 수 조회 성공: webtoon_id={webtoon_id}, count={total_count}")
                return int(total_count)
        return None
            
    except Exception as e:
        logger.debug(f"에피소드 수 조회 실패: webtoon_id={webtoon_id}, 오류: {e}")
        return None


def extract_webtoon_detail(webtoon_id: str, use_html_fallback: bool = True) -> Optional[Dict[str, Any]]:
    """
    웹툰 상세 정보를 수집합니다.
    
    우선순위:
    1. API 호출 시도 (/api/article/list/info)
    2. API 실패 시 HTML 파싱 시도 (use_html_fallback=True인 경우)
    
    Args:
        webtoon_id: 웹툰 ID
        use_html_fallback: API 실패 시 HTML 파싱 시도 여부
    
    Returns:
        웹툰 상세 정보 딕셔너리, 실패 시 None
        {
            'webtoon_id': str,
            'favorite_count': int,
            'favorite_count_source': 'api' | 'html',
            'finished': bool,
            'rest': bool,
            'total_episode_count': int,
            ...
        }
    """
    session = create_session()
    result = {
        'webtoon_id': webtoon_id,
        'favorite_count': None,
        'favorite_count_source': None,
        'finished': None,
        'rest': None,
        'total_episode_count': None,
        'genre': None,
        'tags': None,
    }
    
    # 1. API 호출 시도
    api_data = fetch_webtoon_detail_api(webtoon_id, session)
    
    if api_data:
        # API에서 데이터 파싱 (parse_webtoon_detail 사용)
        from src.parse_webtoon_detail import parse_webtoon_detail
        parsed = parse_webtoon_detail(api_data=api_data)
        
        result.update(parsed)
        
        # 에피소드 수는 별도 API 호출
        episode_count = fetch_webtoon_episode_count(webtoon_id, session)
        if episode_count is not None:
            result['total_episode_count'] = episode_count
        
        logger.info(f"웹툰 상세 정보 수집 성공 (API): webtoon_id={webtoon_id}, favorite_count={result['favorite_count']}, genre={result.get('genre')}, tags={len(result.get('tags', [])) if result.get('tags') else 0}개")
        return result
    
    # 2. HTML 파싱 시도 (API 실패 시)
    if use_html_fallback:
        html = fetch_webtoon_detail_html(webtoon_id, session)
        
        if html:
            from src.parse_webtoon_detail import parse_favorite_count_from_html
            
            favorite_count = parse_favorite_count_from_html(html)
            if favorite_count is not None:
                result['favorite_count'] = favorite_count
                result['favorite_count_source'] = 'html'
                logger.info(f"웹툰 상세 정보 수집 성공 (HTML): webtoon_id={webtoon_id}, favorite_count={favorite_count}")
                return result
    
    logger.warning(f"웹툰 상세 정보 수집 실패: webtoon_id={webtoon_id}")
    return None

