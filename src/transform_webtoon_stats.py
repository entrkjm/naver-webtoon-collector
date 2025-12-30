"""
Transform Webtoon Stats 모듈: 웹툰 상세 정보 변환 및 저장

이 모듈은 웹툰 상세 정보를 스키마에 맞게 변환하고 CSV로 저장합니다.
- fact_webtoon_stats (히스토리 테이블) 데이터 생성 및 저장
- 멱등성 보장 (중복 체크)
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from src.models import (
    create_fact_webtoon_stats_record,
    validate_fact_webtoon_stats_record,
    validate_foreign_key,
    FACT_WEBTOON_STATS_COLUMNS,
)
from src.utils import (
    get_webtoon_stats_csv_path,
    get_webtoon_stats_jsonl_path,
    get_data_format,
    format_datetime,
    parse_datetime,
)

logger = logging.getLogger(__name__)


def serialize_for_json(obj):
    """
    JSON 직렬화를 위한 헬퍼 함수.
    datetime, date 객체를 문자열로 변환합니다.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def load_fact_webtoon_stats_jsonl() -> pd.DataFrame:
    """
    fact_webtoon_stats JSONL 파일을 로드합니다. 파일이 없으면 빈 DataFrame 반환.
    
    Returns:
        fact_webtoon_stats DataFrame
    """
    file_path = get_webtoon_stats_jsonl_path()
    
    if not file_path.exists():
        logger.info("fact_webtoon_stats.jsonl 파일이 없습니다. 새로 생성합니다.")
        return pd.DataFrame(columns=FACT_WEBTOON_STATS_COLUMNS)
    
    try:
        records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    # datetime 문자열을 datetime 객체로 변환
                    if 'collected_at' in record and record['collected_at']:
                        record['collected_at'] = datetime.fromisoformat(record['collected_at'].replace('Z', '+00:00'))
                    records.append(record)
        
        if len(records) == 0:
            return pd.DataFrame(columns=FACT_WEBTOON_STATS_COLUMNS)
        
        df = pd.DataFrame(records)
        logger.info(f"fact_webtoon_stats.jsonl 로드 완료: {len(df)}개 레코드")
        return df
    except Exception as e:
        logger.error(f"fact_webtoon_stats.jsonl 로드 실패: {e}")
        return pd.DataFrame(columns=FACT_WEBTOON_STATS_COLUMNS)


def load_fact_webtoon_stats() -> pd.DataFrame:
    """
    fact_webtoon_stats 파일을 로드합니다 (JSONL 또는 CSV).
    DATA_FORMAT 환경 변수에 따라 형식을 결정합니다.
    
    Returns:
        fact_webtoon_stats DataFrame
    """
    data_format = get_data_format()
    if data_format == 'jsonl':
        return load_fact_webtoon_stats_jsonl()
    else:
        return load_fact_webtoon_stats_csv()


def load_fact_webtoon_stats_csv() -> pd.DataFrame:
    """
    fact_webtoon_stats CSV 파일을 로드합니다. 파일이 없으면 빈 DataFrame 반환.
    
    Returns:
        fact_webtoon_stats DataFrame
    """
    file_path = get_webtoon_stats_csv_path()
    
    if not file_path.exists():
        logger.info("fact_webtoon_stats.csv 파일이 없습니다. 새로 생성합니다.")
        return pd.DataFrame(columns=FACT_WEBTOON_STATS_COLUMNS)
    
    try:
        df = pd.read_csv(file_path)
        # collected_at을 datetime 타입으로 변환
        if 'collected_at' in df.columns:
            df['collected_at'] = pd.to_datetime(df['collected_at'])
        logger.info(f"fact_webtoon_stats.csv 로드 완료: {len(df)}개 레코드")
        return df
    except Exception as e:
        logger.error(f"fact_webtoon_stats.csv 로드 실패: {e}")
        return pd.DataFrame(columns=FACT_WEBTOON_STATS_COLUMNS)


def save_fact_webtoon_stats_jsonl(df: pd.DataFrame) -> None:
    """
    fact_webtoon_stats DataFrame을 JSONL 파일로 저장합니다.
    
    Args:
        df: 저장할 DataFrame
    """
    file_path = get_webtoon_stats_jsonl_path()
    
    try:
        # 컬럼 순서 보장
        df = df[FACT_WEBTOON_STATS_COLUMNS].copy() if all(col in df.columns for col in FACT_WEBTOON_STATS_COLUMNS) else df.copy()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for _, row in df.iterrows():
                record = row.to_dict()
                # datetime을 ISO 형식 문자열로 변환
                if 'collected_at' in record and pd.notna(record['collected_at']):
                    if isinstance(record['collected_at'], pd.Timestamp):
                        record['collected_at'] = record['collected_at'].isoformat()
                # None을 null로 변환 및 total_episode_count를 정수로 변환
                def convert_value(key, val):
                    if isinstance(val, list):
                        return val  # 리스트는 그대로
                    if pd.isna(val):
                        return None
                    # total_episode_count는 정수로 변환 (float -> int)
                    if key == 'total_episode_count' and val is not None:
                        try:
                            if isinstance(val, float):
                                return int(val)
                            elif isinstance(val, str):
                                return int(float(val)) if val.strip() not in ('', 'None', 'null') else None
                            elif isinstance(val, int):
                                return val
                            else:
                                return int(val)
                        except (ValueError, TypeError):
                            return None
                    return val
                record = {k: convert_value(k, v) for k, v in record.items()}
                f.write(json.dumps(record, ensure_ascii=False, default=serialize_for_json) + '\n')
        
        logger.info(f"fact_webtoon_stats.jsonl 저장 완료: {len(df)}개 레코드")
    except Exception as e:
        logger.error(f"fact_webtoon_stats.jsonl 저장 실패: {e}")
        raise


def save_fact_webtoon_stats_csv(df: pd.DataFrame) -> None:
    """
    fact_webtoon_stats DataFrame을 CSV 파일로 저장합니다.
    
    Args:
        df: 저장할 DataFrame
    """
    file_path = get_webtoon_stats_csv_path()
    
    try:
        # 컬럼 순서 보장
        df = df[FACT_WEBTOON_STATS_COLUMNS] if all(col in df.columns for col in FACT_WEBTOON_STATS_COLUMNS) else df
        df.to_csv(file_path, index=False, encoding='utf-8')
        logger.info(f"fact_webtoon_stats.csv 저장 완료: {len(df)}개 레코드")
    except Exception as e:
        logger.error(f"fact_webtoon_stats.csv 저장 실패: {e}")
        raise


def save_fact_webtoon_stats(df: pd.DataFrame) -> None:
    """
    fact_webtoon_stats DataFrame을 저장합니다 (JSONL 또는 CSV).
    DATA_FORMAT 환경 변수에 따라 형식을 결정합니다.
    
    Args:
        df: 저장할 DataFrame
    """
    data_format = get_data_format()
    if data_format == 'jsonl':
        save_fact_webtoon_stats_jsonl(df)
    else:
        save_fact_webtoon_stats_csv(df)


def transform_detail_data_to_model(
    detail_data: Dict[str, any]
) -> Optional[Dict]:
    """
    웹툰 상세 정보를 모델 스키마에 맞게 변환합니다.
    
    Args:
        detail_data: 웹툰 상세 정보 딕셔너리
    
    Returns:
        fact_webtoon_stats 레코드 (실패 시 None)
    """
    try:
        webtoon_id = detail_data.get('webtoon_id')
        if not webtoon_id:
            logger.warning("webtoon_id가 없습니다")
            return None
        
        # fact_webtoon_stats 레코드 생성
        # total_episode_count를 정수로 변환
        total_episode_count = detail_data.get('total_episode_count')
        if total_episode_count is not None:
            try:
                if isinstance(total_episode_count, float):
                    total_episode_count = int(total_episode_count)
                elif isinstance(total_episode_count, str):
                    total_episode_count = int(float(total_episode_count))
                else:
                    total_episode_count = int(total_episode_count)
            except (ValueError, TypeError):
                total_episode_count = None
        
        record = create_fact_webtoon_stats_record(
            webtoon_id=webtoon_id,
            favorite_count=detail_data.get('favorite_count'),
            favorite_count_source=detail_data.get('favorite_count_source'),
            finished=detail_data.get('finished'),
            rest=detail_data.get('rest'),
            total_episode_count=total_episode_count,
        )
        
        if validate_fact_webtoon_stats_record(record):
            return record
        else:
            logger.warning(f"fact_webtoon_stats 레코드 검증 실패: {detail_data}")
            return None
            
    except Exception as e:
        logger.error(f"데이터 변환 실패: {detail_data}, 오류: {e}")
        return None


def merge_fact_webtoon_stats(
    existing_df: pd.DataFrame,
    new_records: List[Dict]
) -> pd.DataFrame:
    """
    새로운 fact_webtoon_stats 레코드를 기존 데이터와 병합합니다.
    같은 시각의 중복 레코드는 제거합니다 (멱등성 보장).
    
    Args:
        existing_df: 기존 fact_webtoon_stats DataFrame
        new_records: 새로운 레코드 리스트
    
    Returns:
        병합된 DataFrame
    """
    if len(new_records) == 0:
        return existing_df
    
    new_df = pd.DataFrame(new_records)
    
    # collected_at을 datetime으로 변환
    if 'collected_at' in new_df.columns:
        new_df['collected_at'] = pd.to_datetime(new_df['collected_at'])
    
    # 기존 레코드가 있으면 중복 체크
    if len(existing_df) > 0:
        # 같은 (webtoon_id, collected_at) 조합 집합
        existing_keys = set(
            zip(
                existing_df['webtoon_id'].astype(str),
                existing_df['collected_at'].astype(str)
            )
        )
        
        # 중복되지 않은 레코드만 필터링
        new_df['key'] = list(zip(
            new_df['webtoon_id'].astype(str),
            new_df['collected_at'].astype(str)
        ))
        new_df_filtered = new_df[~new_df['key'].isin(existing_keys)]
        new_df_filtered = new_df_filtered.drop(columns=['key'])
        
        if len(new_df_filtered) > 0:
            logger.info(f"중복 제거: {len(new_df) - len(new_df_filtered)}개 중복 레코드 제거됨")
            return pd.concat([existing_df, new_df_filtered], ignore_index=True)
        else:
            logger.info(f"모든 레코드가 중복입니다. 데이터 변경 없음.")
            return existing_df
    else:
        # 기존 레코드가 없으면 그대로 추가
        return new_df


def transform_and_save_webtoon_stats(
    detail_data_list: List[Dict[str, any]],
    dim_webtoon_ids: set
) -> bool:
    """
    웹툰 상세 정보를 변환하여 CSV로 저장합니다.
    멱등성을 보장합니다.
    
    Args:
        detail_data_list: 웹툰 상세 정보 리스트
        dim_webtoon_ids: dim_webtoon에 존재하는 webtoon_id 집합
    
    Returns:
        성공 여부
    """
    try:
        # 1. 데이터 변환
        records = []
        for detail_data in detail_data_list:
            record = transform_detail_data_to_model(detail_data)
            if record:
                # Foreign Key 검증
                if validate_foreign_key(record, dim_webtoon_ids):
                    records.append(record)
                else:
                    logger.warning(f"Foreign Key 검증 실패: webtoon_id={record.get('webtoon_id')}")
        
        if len(records) == 0:
            logger.warning("변환된 레코드가 없습니다.")
            return False
        
        # 2. 기존 데이터 로드
        existing_df = load_fact_webtoon_stats()
        
        # 3. 병합
        merged_df = merge_fact_webtoon_stats(existing_df, records)
        
        # 4. 저장
        save_fact_webtoon_stats(merged_df)
        
        logger.info(f"웹툰 상세 정보 저장 완료: {len(records)}개 레코드 추가됨")
        return True
        
    except Exception as e:
        logger.error(f"웹툰 상세 정보 저장 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

