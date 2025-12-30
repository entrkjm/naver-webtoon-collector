"""
API 응답 파싱 모듈

네이버 웹툰 API의 JSON 응답을 파싱합니다.
HTML 파싱과 별도로 관리합니다.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def parse_api_response(api_data: dict) -> List[Dict[str, any]]:
    """
    API JSON 응답을 파싱하여 웹툰 차트 데이터 리스트로 변환합니다.
    
    실제 API 응답 구조에 따라 이 함수를 수정해야 할 수 있습니다.
    
    Args:
        api_data: API에서 받은 JSON 데이터
    
    Returns:
        웹툰 차트 데이터 리스트
        각 항목은 {'rank': int, 'title': str, 'webtoon_id': str, ...} 형식
    """
    chart_data = []
    
    try:
        # API 응답 구조 확인 (실제 구조에 맞게 수정 필요)
        # 예상 구조:
        # {
        #   "result": {
        #     "titleList": [
        #       {"titleId": "123456", "titleName": "웹툰 제목", ...}
        #     ]
        #   }
        # }
        
        # 네이버 웹툰 API 실제 구조: titleListMap (요일별 분류)
        webtoon_list = []
        
        if isinstance(api_data, dict):
            # titleListMap에서 모든 요일의 웹툰을 합침 (요일 정보 포함)
            title_list_map = api_data.get("titleListMap", {})
            
            if title_list_map:
                # 모든 요일의 웹툰을 하나의 리스트로 합침 (요일 정보 포함)
                for day_key, day_webtoons in title_list_map.items():
                    if isinstance(day_webtoons, list):
                        # 각 웹툰에 요일 정보 추가
                        for webtoon in day_webtoons:
                            if isinstance(webtoon, dict):
                                webtoon['_weekday'] = day_key  # 요일 정보 임시 저장
                        webtoon_list.extend(day_webtoons)
                        logger.debug(f"요일 {day_key}: {len(day_webtoons)}개 웹툰")
                
                logger.info(f"API 응답에서 총 {len(webtoon_list)}개 웹툰 발견 (모든 요일 합계)")
            else:
                # 대체 구조 시도
                if "result" in api_data and isinstance(api_data["result"], dict):
                    if "titleList" in api_data["result"]:
                        webtoon_list = api_data["result"]["titleList"]
                    elif "list" in api_data["result"]:
                        webtoon_list = api_data["result"]["list"]
                elif "titleList" in api_data:
                    webtoon_list = api_data["titleList"]
                elif isinstance(api_data.get("data"), list):
                    webtoon_list = api_data["data"]
        
        # 구조 3: 리스트 자체
        elif isinstance(api_data, list):
            webtoon_list = api_data
        
        if not webtoon_list:
            logger.warning("API 응답에서 웹툰 리스트를 찾을 수 없습니다.")
            logger.debug(f"API 응답 구조: {list(api_data.keys()) if isinstance(api_data, dict) else '리스트'}")
            return []
        
        logger.info(f"파싱할 웹툰 총 {len(webtoon_list)}개")
        
        # 각 웹툰 데이터 추출 (요일별로 순위 재계산)
        # 요일별로 그룹화하여 각 요일 내에서 순위 계산
        weekday_groups = {}
        for item in webtoon_list:
            if isinstance(item, dict):
                weekday = item.get('_weekday', 'UNKNOWN')
                if weekday not in weekday_groups:
                    weekday_groups[weekday] = []
                weekday_groups[weekday].append(item)
        
        # 각 요일별로 순위를 매기고 데이터 추출
        global_rank = 1
        for weekday, items in weekday_groups.items():
            for idx, item in enumerate(items, start=1):
                try:
                    # 요일별 순위와 전체 순위 모두 저장
                    webtoon_data = extract_webtoon_from_api_item(
                        item, 
                        rank=global_rank,  # 전체 순위
                        weekday=weekday   # 요일 정보
                    )
                    if webtoon_data:
                        chart_data.append(webtoon_data)
                        global_rank += 1
                except Exception as e:
                    logger.warning(f"항목 파싱 실패 (요일: {weekday}, 순위: {global_rank}): {e}")
                    continue
        
        logger.info(f"API 파싱 완료: {len(chart_data)}개 웹툰 데이터 추출")
        return chart_data
        
    except Exception as e:
        logger.error(f"API 응답 파싱 실패: {e}")
        import traceback
        traceback.print_exc()
        return []


def extract_webtoon_from_api_item(item: dict, rank: int, weekday: Optional[str] = None) -> Optional[Dict[str, any]]:
    """
    API 응답의 개별 웹툰 항목에서 데이터를 추출합니다.
    
    실제 API 응답 구조에 따라 이 함수를 수정해야 합니다.
    
    Args:
        item: API 응답의 개별 웹툰 항목 (딕셔너리)
        rank: 순위
        weekday: 요일 정보 (예: "MONDAY", "FRIDAY")
    
    Returns:
        웹툰 데이터 딕셔너리 (실패 시 None)
    """
    try:
        # API 응답 필드명 확인 (실제 구조에 맞게 수정 필요)
        # 예상 필드명:
        # - titleId 또는 title_id 또는 id
        # - titleName 또는 title 또는 name
        # - author 또는 writer 또는 authorName
        
        webtoon_id = None
        title = None
        author = None
        
        # 네이버 웹툰 API 실제 필드명 사용
        # titleId: 숫자 또는 문자열
        webtoon_id = item.get('titleId')
        if webtoon_id is not None:
            webtoon_id = str(webtoon_id)
        else:
            logger.warning(f"순위 {rank}: 웹툰 ID를 찾을 수 없습니다")
            return None
        
        # titleName: 제목
        title = item.get('titleName')
        if not title:
            # 대체 필드명 시도
            for field in ['title', 'name', 'webtoonTitle']:
                if field in item:
                    title = str(item[field])
                    break
        
        if not title:
            logger.warning(f"순위 {rank}: 제목을 찾을 수 없습니다")
            return None
        
        # author: 작가 (선택적)
        author = item.get('author')
        if author:
            author = str(author)
        
        # 추가 필드 (실제 API에서 제공하는 정보)
        # viewCount: 조회수 (조회순 정렬에 사용)
        view_count = item.get('viewCount')
        if view_count is not None:
            try:
                view_count = int(view_count)
            except (ValueError, TypeError):
                view_count = None
        
        # starScore: 별점 (현재는 저장하지 않음)
        star_score = item.get('starScore')
        
        # 결과 딕셔너리 생성
        data = {
            'rank': rank,
            'title': str(title),
            'webtoon_id': webtoon_id,
        }
        
        # 선택적 필드 추가
        if author:
            data['author'] = author
        
        # 요일 정보 추가
        if weekday:
            data['weekday'] = weekday
        
        # view_count 추가 (0이 아닌 경우만 저장하거나, 모두 저장)
        if view_count is not None:
            data['view_count'] = view_count
        
        return data
        
    except Exception as e:
        logger.error(f"데이터 추출 실패 (순위 {rank}): {e}")
        return None

