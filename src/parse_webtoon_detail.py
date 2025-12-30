"""
Parse Webtoon Detail 모듈: 웹툰 상세 정보 파싱

이 모듈은 API 응답과 HTML에서 웹툰 상세 정보를 파싱합니다.
"""

import logging
import re
from typing import Optional, Dict, Any

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def parse_api_response(api_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    API 응답에서 웹툰 상세 정보를 파싱합니다.
    
    Args:
        api_data: API 응답 데이터
    
    Returns:
        파싱된 웹툰 상세 정보 딕셔너리
    """
    result = {
        'favorite_count': api_data.get('favoriteCount'),
        'finished': api_data.get('finished'),
        'rest': api_data.get('rest'),
    }
    
    # genre 추출: gfpAdCustomParam.genreTypes 배열에서 첫 번째 값
    genre = None
    if 'gfpAdCustomParam' in api_data and isinstance(api_data['gfpAdCustomParam'], dict):
        genre_types = api_data['gfpAdCustomParam'].get('genreTypes', [])
        if genre_types and len(genre_types) > 0:
            genre = genre_types[0]  # 첫 번째 장르만 저장
    
    result['genre'] = genre
    
    # tags 추출: curationTagList에서 tagName 추출
    tags = []
    if 'curationTagList' in api_data and isinstance(api_data['curationTagList'], list):
        for tag_item in api_data['curationTagList']:
            if isinstance(tag_item, dict) and 'tagName' in tag_item:
                tags.append(tag_item['tagName'])
    
    result['tags'] = tags if tags else None
    
    return result


def parse_favorite_count_from_html(html: str) -> Optional[int]:
    """
    HTML에서 관심 수를 파싱합니다.
    
    여러 방법을 시도합니다:
    1. 클래스명 패턴 매칭 (EpisodeListUser__count로 시작)
    2. 텍스트 패턴 매칭 (큰 숫자 찾기)
    3. "관심" 텍스트 주변에서 찾기
    
    Args:
        html: HTML 문자열
    
    Returns:
        관심 수 (정수), 찾지 못하면 None
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 방법 1: 클래스명 패턴 매칭
        # EpisodeListUser__count로 시작하는 모든 클래스 찾기
        interest_elements = soup.find_all('span', class_=re.compile(r'EpisodeListUser__count'))
        
        for elem in interest_elements:
            text = elem.get_text(strip=True)
            try:
                # 쉼표 제거 후 정수 변환
                favorite_count = int(text.replace(',', ''))
                # 관심 수는 보통 큰 숫자 (10만 이상)
                if favorite_count > 10000:
                    logger.debug(f"HTML에서 관심 수 파싱 성공 (클래스명): {favorite_count:,}")
                    return favorite_count
            except ValueError:
                continue
        
        # 방법 2: 텍스트 패턴 매칭 (큰 숫자 찾기)
        number_pattern = re.compile(r'\d{1,3}(?:,\d{3})*')
        all_spans = soup.find_all('span')
        
        for span in all_spans:
            text = span.get_text(strip=True)
            if number_pattern.match(text):
                try:
                    number = int(text.replace(',', ''))
                    # 관심 수는 보통 큰 숫자 (10만 이상)
                    if number > 100000:
                        logger.debug(f"HTML에서 관심 수 파싱 성공 (텍스트 패턴): {number:,}")
                        return number
                except ValueError:
                    continue
        
        # 방법 3: "관심" 텍스트 주변에서 찾기
        interest_keywords = ['관심', '찜', 'favorite']
        
        for keyword in interest_keywords:
            # 텍스트에 키워드가 포함된 요소 찾기
            elements = soup.find_all(string=re.compile(keyword, re.I))
            for elem in elements[:5]:  # 최대 5개만 확인
                parent = elem.parent
                if parent:
                    # 부모나 형제 요소에서 숫자 찾기
                    # 같은 부모 내의 모든 span 찾기
                    siblings = parent.find_all('span')
                    for sibling in siblings:
                        text = sibling.get_text(strip=True)
                        if re.match(r'^\d{1,3}(?:,\d{3})*$', text):
                            try:
                                number = int(text.replace(',', ''))
                                if number > 10000:
                                    logger.debug(f"HTML에서 관심 수 파싱 성공 ('{keyword}' 주변): {number:,}")
                                    return number
                            except ValueError:
                                continue
        
        logger.debug("HTML에서 관심 수를 찾지 못했습니다")
        return None
        
    except Exception as e:
        logger.error(f"HTML 파싱 실패: {e}")
        return None


def parse_webtoon_detail(api_data: Optional[Dict[str, Any]] = None, html: Optional[str] = None) -> Dict[str, Any]:
    """
    API 응답 또는 HTML에서 웹툰 상세 정보를 파싱합니다.
    
    Args:
        api_data: API 응답 데이터 (우선)
        html: HTML 문자열 (API 실패 시 사용)
    
    Returns:
        파싱된 웹툰 상세 정보 딕셔너리
    """
    result = {
        'favorite_count': None,
        'favorite_count_source': None,
        'finished': None,
        'rest': None,
        'genre': None,
        'tags': None,
    }
    
    # 1. API 응답 파싱 (우선)
    if api_data:
        parsed = parse_api_response(api_data)
        result.update(parsed)
        if result['favorite_count'] is not None:
            result['favorite_count_source'] = 'api'
    
    # 2. HTML 파싱 (API에서 찾지 못한 경우)
    if result['favorite_count'] is None and html:
        favorite_count = parse_favorite_count_from_html(html)
        if favorite_count is not None:
            result['favorite_count'] = favorite_count
            result['favorite_count_source'] = 'html'
    
    return result

