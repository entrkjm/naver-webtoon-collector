"""
데이터 모델 정의

이 모듈은 데이터 모델 스키마를 정의합니다.
- dim_webtoon: 웹툰 마스터 테이블 스키마
- fact_weekly_chart: 주간 차트 히스토리 테이블 스키마
- fact_webtoon_stats: 웹툰 상세 정보 히스토리 테이블 스키마
"""

from datetime import date, datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# dim_webtoon (마스터 테이블) 스키마
# ============================================================================

def create_dim_webtoon_record(
    webtoon_id: str,
    title: str,
    author: Optional[str] = None,
    genre: Optional[str] = None,
    tags: Optional[list] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    dim_webtoon 레코드를 생성합니다.
    
    Args:
        webtoon_id: 웹툰 고유 ID (필수, Primary Key)
        title: 웹툰 제목 (필수)
        author: 작가명 (선택, API에서 수집)
        genre: 장르 (선택, API에서 수집, 첫 번째 장르만 저장)
        tags: 태그 리스트 (선택, API에서 수집, REPEATED STRING)
        created_at: 레코드 생성 시각 (선택, 없으면 현재 시각)
        updated_at: 레코드 수정 시각 (선택, 없으면 현재 시각)
    
    Returns:
        dim_webtoon 레코드 딕셔너리
    
    Raises:
        ValueError: 필수 필드가 누락된 경우
    """
    if not webtoon_id:
        raise ValueError("webtoon_id는 필수 필드입니다.")
    if not title:
        raise ValueError("title은 필수 필드입니다.")
    
    now = datetime.now()
    
    # tags는 리스트로 저장 (BigQuery에서는 REPEATED STRING으로 사용)
    # CSV 저장 시에는 transform.py에서 파이프로 구분된 문자열로 변환
    tags_list = None
    if tags:
        if isinstance(tags, list):
            tags_list = [str(tag) for tag in tags if tag]  # 빈 문자열 제거
        elif isinstance(tags, str):
            # 이미 문자열인 경우 (CSV에서 로드한 경우) 리스트로 변환
            tags_list = [t.strip() for t in tags.split('|') if t.strip()]
        else:
            tags_list = [str(tags)]
    
    return {
        'webtoon_id': str(webtoon_id),
        'title': str(title),
        'author': str(author) if author else None,
        'genre': str(genre) if genre else None,
        'tags': tags_list,  # 리스트로 저장 (BigQuery REPEATED STRING용), CSV 저장 시 변환
        'created_at': created_at if created_at else now,
        'updated_at': updated_at if updated_at else now
    }


def validate_dim_webtoon_record(record: Dict[str, Any]) -> bool:
    """
    dim_webtoon 레코드의 유효성을 검증합니다.
    
    Args:
        record: 검증할 레코드
    
    Returns:
        유효하면 True, 그렇지 않으면 False
    """
    required_fields = ['webtoon_id', 'title']
    
    for field in required_fields:
        if field not in record or not record[field]:
            logger.warning(f"dim_webtoon 레코드 검증 실패: 필수 필드 '{field}' 누락")
            return False
    
    # webtoon_id는 문자열이어야 함
    if not isinstance(record['webtoon_id'], str):
        logger.warning(f"dim_webtoon 레코드 검증 실패: webtoon_id는 문자열이어야 합니다")
        return False
    
    return True


# ============================================================================
# fact_weekly_chart (히스토리 테이블) 스키마
# ============================================================================

def create_fact_weekly_chart_record(
    chart_date: date,
    webtoon_id: str,
    rank: int,
    collected_at: Optional[datetime] = None,
    weekday: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    week: Optional[int] = None,
    view_count: Optional[int] = None
) -> Dict[str, Any]:
    """
    fact_weekly_chart 레코드를 생성합니다.
    
    Args:
        chart_date: 수집 날짜 (필수, Partition Key) - 차트 기준 날짜
        webtoon_id: 웹툰 ID (필수, Foreign Key -> dim_webtoon)
        rank: 주간 차트 순위 (필수, 1 이상의 정수)
        collected_at: 데이터 수집 시각 (선택, 없으면 현재 시각)
        weekday: 요일 정보 (선택, 예: "MONDAY", "FRIDAY")
        year: 연도 (선택, collected_at에서 추출)
        month: 월 (선택, collected_at에서 추출)
        week: 해당 월의 몇 번째 주인지 (선택, collected_at에서 추출)
        view_count: 조회수 (선택, API에서 제공하는 경우)
    
    Returns:
        fact_weekly_chart 레코드 딕셔너리
    
    Raises:
        ValueError: 필수 필드가 누락되었거나 유효하지 않은 경우
    """
    if not chart_date:
        raise ValueError("chart_date는 필수 필드입니다.")
    if not webtoon_id:
        raise ValueError("webtoon_id는 필수 필드입니다.")
    if not isinstance(rank, int) or rank < 1:
        raise ValueError("rank는 1 이상의 정수여야 합니다.")
    
    now = datetime.now() if not collected_at else collected_at
    
    # collected_at에서 year, month 추출 (없으면 현재 시각에서)
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    
    # week 계산 (해당 월의 몇 번째 주인지)
    # 1일이 속한 주를 1주차로 계산
    if week is None:
        day_of_month = now.day
        # 해당 날짜가 속한 주 계산: (day - 1) // 7 + 1
        # 예: 1일~7일 = 1주차, 8일~14일 = 2주차, ...
        week = ((day_of_month - 1) // 7) + 1
    
    return {
        'chart_date': chart_date if isinstance(chart_date, date) else chart_date,
        'webtoon_id': str(webtoon_id),
        'rank': int(rank),
        'collected_at': now,
        'weekday': weekday,  # 요일 정보 (예: "MONDAY", "FRIDAY")
        'year': int(year),
        'month': int(month),
        'week': int(week),
        'view_count': int(view_count) if view_count is not None else None
    }


def validate_fact_weekly_chart_record(record: Dict[str, Any]) -> bool:
    """
    fact_weekly_chart 레코드의 유효성을 검증합니다.
    
    Args:
        record: 검증할 레코드
    
    Returns:
        유효하면 True, 그렇지 않으면 False
    """
    required_fields = ['chart_date', 'webtoon_id', 'rank']
    
    for field in required_fields:
        if field not in record:
            logger.warning(f"fact_weekly_chart 레코드 검증 실패: 필수 필드 '{field}' 누락")
            return False
    
    # chart_date는 date 타입이어야 함
    if not isinstance(record['chart_date'], (date, str)):
        logger.warning(f"fact_weekly_chart 레코드 검증 실패: chart_date는 date 타입이어야 합니다")
        return False
    
    # webtoon_id는 문자열이어야 함
    if not isinstance(record['webtoon_id'], str) or not record['webtoon_id']:
        logger.warning(f"fact_weekly_chart 레코드 검증 실패: webtoon_id는 비어있지 않은 문자열이어야 합니다")
        return False
    
    # rank는 1 이상의 정수여야 함
    if not isinstance(record['rank'], int) or record['rank'] < 1:
        logger.warning(f"fact_weekly_chart 레코드 검증 실패: rank는 1 이상의 정수여야 합니다 (현재: {record['rank']})")
        return False
    
    # year, month, week는 정수여야 함 (있는 경우)
    if 'year' in record and record['year'] is not None:
        if not isinstance(record['year'], int) or record['year'] < 2000 or record['year'] > 2100:
            logger.warning(f"fact_weekly_chart 레코드 검증 실패: year는 2000-2100 사이의 정수여야 합니다 (현재: {record['year']})")
            return False
    
    if 'month' in record and record['month'] is not None:
        if not isinstance(record['month'], int) or record['month'] < 1 or record['month'] > 12:
            logger.warning(f"fact_weekly_chart 레코드 검증 실패: month는 1-12 사이의 정수여야 합니다 (현재: {record['month']})")
            return False
    
    if 'week' in record and record['week'] is not None:
        if not isinstance(record['week'], int) or record['week'] < 1 or record['week'] > 6:
            logger.warning(f"fact_weekly_chart 레코드 검증 실패: week는 1-6 사이의 정수여야 합니다 (현재: {record['week']})")
            return False
    
    return True


# ============================================================================
# fact_webtoon_stats (웹툰 상세 정보 히스토리 테이블) 스키마
# ============================================================================

def create_fact_webtoon_stats_record(
    webtoon_id: str,
    collected_at: Optional[datetime] = None,
    favorite_count: Optional[int] = None,
    favorite_count_source: Optional[str] = None,
    finished: Optional[bool] = None,
    rest: Optional[bool] = None,
    total_episode_count: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    week: Optional[int] = None
) -> Dict[str, Any]:
    """
    fact_webtoon_stats 레코드를 생성합니다.
    
    Args:
        webtoon_id: 웹툰 ID (필수, Foreign Key -> dim_webtoon)
        collected_at: 데이터 수집 시각 (필수, Partition Key)
        favorite_count: 관심 수 (누적값)
        favorite_count_source: 관심 수 수집 소스 ("api" 또는 "html")
        finished: 완결 여부
        rest: 휴재 여부
        total_episode_count: 전체 에피소드 수
        year: 연도 (collected_at에서 추출)
        month: 월 (collected_at에서 추출)
        week: 해당 월의 몇 번째 주인지 (collected_at에서 추출)
    
    Returns:
        fact_webtoon_stats 레코드 딕셔너리
    
    Raises:
        ValueError: 필수 필드가 누락되었거나 유효하지 않은 경우
    """
    if not webtoon_id:
        raise ValueError("webtoon_id는 필수 필드입니다.")
    
    now = datetime.now() if not collected_at else collected_at
    
    # collected_at에서 year, month 추출 (없으면 현재 시각에서)
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    
    # week 계산 (해당 월의 몇 번째 주인지)
    if week is None:
        day_of_month = now.day
        week = ((day_of_month - 1) // 7) + 1
    
    return {
        'webtoon_id': str(webtoon_id),
        'collected_at': now,
        'favorite_count': int(favorite_count) if favorite_count is not None else None,
        'favorite_count_source': favorite_count_source,  # "api" 또는 "html"
        'finished': bool(finished) if finished is not None else None,
        'rest': bool(rest) if rest is not None else None,
        'total_episode_count': int(total_episode_count) if total_episode_count is not None else None,
        'year': int(year),
        'month': int(month),
        'week': int(week)
    }


def validate_fact_webtoon_stats_record(record: Dict[str, Any]) -> bool:
    """
    fact_webtoon_stats 레코드의 유효성을 검증합니다.
    
    Args:
        record: 검증할 레코드
    
    Returns:
        유효하면 True, 그렇지 않으면 False
    """
    required_fields = ['webtoon_id', 'collected_at']
    
    for field in required_fields:
        if field not in record:
            logger.warning(f"fact_webtoon_stats 레코드 검증 실패: 필수 필드 '{field}' 누락")
            return False
    
    # webtoon_id는 문자열이어야 함
    if not isinstance(record['webtoon_id'], str) or not record['webtoon_id']:
        logger.warning(f"fact_webtoon_stats 레코드 검증 실패: webtoon_id는 비어있지 않은 문자열이어야 합니다")
        return False
    
    # favorite_count_source는 "api" 또는 "html"이어야 함 (있는 경우)
    if 'favorite_count_source' in record and record['favorite_count_source']:
        if record['favorite_count_source'] not in ['api', 'html']:
            logger.warning(f"fact_webtoon_stats 레코드 검증 실패: favorite_count_source는 'api' 또는 'html'이어야 합니다")
            return False
    
    # year, month, week는 정수여야 함 (있는 경우)
    if 'year' in record and record['year'] is not None:
        if not isinstance(record['year'], int) or record['year'] < 2000 or record['year'] > 2100:
            logger.warning(f"fact_webtoon_stats 레코드 검증 실패: year는 2000-2100 사이의 정수여야 합니다")
            return False
    
    if 'month' in record and record['month'] is not None:
        if not isinstance(record['month'], int) or record['month'] < 1 or record['month'] > 12:
            logger.warning(f"fact_webtoon_stats 레코드 검증 실패: month는 1-12 사이의 정수여야 합니다")
            return False
    
    if 'week' in record and record['week'] is not None:
        if not isinstance(record['week'], int) or record['week'] < 1 or record['week'] > 6:
            logger.warning(f"fact_webtoon_stats 레코드 검증 실패: week는 1-6 사이의 정수여야 합니다")
            return False
    
    return True


# ============================================================================
# 스키마 정의 (참조용)
# ============================================================================

# dim_webtoon 스키마 정의
DIM_WEBTOON_SCHEMA = {
    'webtoon_id': str,      # Primary Key
    'title': str,
    'author': Optional[str],
    'genre': Optional[str],  # 첫 번째 장르만 저장
    'tags': Optional[list],  # REPEATED STRING (BigQuery), CSV에서는 파이프로 구분
    'created_at': datetime,
    'updated_at': datetime
}

# fact_weekly_chart 스키마 정의
FACT_WEEKLY_CHART_SCHEMA = {
    'chart_date': date,     # Partition Key - 차트 기준 날짜 (수집 날짜)
    'webtoon_id': str,      # Foreign Key -> dim_webtoon
    'rank': int,            # 주간 차트 순위
    'collected_at': datetime,  # 데이터 수집 시각 (타임스탬프)
    'weekday': Optional[str],   # 요일 정보 (예: "MONDAY", "FRIDAY")
    'year': int,            # 연도 (collected_at에서 추출)
    'month': int,           # 월 (collected_at에서 추출)
    'week': int,            # 해당 월의 몇 번째 주인지 (collected_at에서 추출)
    'view_count': Optional[int]  # 조회수 (API에서 제공하는 경우)
}

# CSV 저장 시 컬럼 순서
DIM_WEBTOON_COLUMNS = [
    'webtoon_id',
    'title',
    'author',
    'genre',
    'tags',
    'created_at',
    'updated_at'
]

FACT_WEEKLY_CHART_COLUMNS = [
    'chart_date',
    'webtoon_id',
    'rank',
    'collected_at',
    'weekday',
    'year',
    'month',
    'week',
    'view_count'
]

# fact_webtoon_stats 스키마 정의
FACT_WEBTOON_STATS_SCHEMA = {
    'webtoon_id': str,              # Foreign Key -> dim_webtoon
    'collected_at': datetime,        # Partition Key - 데이터 수집 시각
    'favorite_count': Optional[int], # 관심 수 (누적값)
    'favorite_count_source': Optional[str],  # 수집 소스 ("api" 또는 "html")
    'finished': Optional[bool],     # 완결 여부
    'rest': Optional[bool],         # 휴재 여부
    'total_episode_count': Optional[int],  # 전체 에피소드 수
    'year': int,                    # 연도 (collected_at에서 추출)
    'month': int,                   # 월 (collected_at에서 추출)
    'week': int                     # 해당 월의 몇 번째 주인지 (collected_at에서 추출)
}

FACT_WEBTOON_STATS_COLUMNS = [
    'webtoon_id',
    'collected_at',
    'favorite_count',
    'favorite_count_source',
    'finished',
    'rest',
    'total_episode_count',
    'year',
    'month',
    'week'
]


# ============================================================================
# Foreign Key 관계 검증
# ============================================================================

def validate_foreign_key(
    fact_record: Dict[str, Any],
    dim_webtoon_ids: set
) -> bool:
    """
    fact_weekly_chart 레코드의 webtoon_id가 dim_webtoon에 존재하는지 검증합니다.
    
    Args:
        fact_record: fact_weekly_chart 레코드
        dim_webtoon_ids: dim_webtoon에 존재하는 webtoon_id 집합
    
    Returns:
        Foreign Key 관계가 유효하면 True, 그렇지 않으면 False
    """
    webtoon_id = fact_record.get('webtoon_id')
    
    if not webtoon_id:
        logger.warning("Foreign Key 검증 실패: webtoon_id가 없습니다")
        return False
    
    if webtoon_id not in dim_webtoon_ids:
        logger.warning(f"Foreign Key 검증 실패: webtoon_id '{webtoon_id}'가 dim_webtoon에 존재하지 않습니다")
        return False
    
    return True
