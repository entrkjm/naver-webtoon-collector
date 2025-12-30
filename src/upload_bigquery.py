"""
BigQuery 업로드 모듈

JSONL 파일을 BigQuery에 적재하는 기능을 제공합니다.
- dim_webtoon 업로드 (MERGE로 멱등성 보장)
- fact_weekly_chart 업로드 (MERGE로 멱등성 보장)
- fact_webtoon_stats 업로드 (MERGE로 멱등성 보장)
"""

import json
import logging
import os
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional

from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.auth import default as default_auth
import subprocess

from src.utils import (
    get_dim_webtoon_jsonl_path,
    get_webtoon_stats_jsonl_path,
    get_chart_jsonl_path,
    setup_logging,
)

logger = logging.getLogger(__name__)


# BigQuery 설정 (환경 변수 또는 기본값)
BIGQUERY_PROJECT_ID = os.getenv('BIGQUERY_PROJECT_ID', 'naver-webtoon-collector')
BIGQUERY_DATASET_ID = os.getenv('BIGQUERY_DATASET_ID', 'naver_webtoon')


def get_bigquery_client() -> bigquery.Client:
    """
    BigQuery 클라이언트를 생성합니다.
    ADC가 없으면 gcloud 인증을 사용합니다.
    
    Returns:
        BigQuery 클라이언트 객체
    """
    try:
        # 먼저 ADC 시도
        credentials, project = default_auth()
        return bigquery.Client(project=BIGQUERY_PROJECT_ID, credentials=credentials)
    except Exception as e:
        logger.warning(f"ADC 인증 실패, gcloud 인증 사용 시도: {e}")
        # gcloud 인증 사용: gcloud auth print-access-token으로 토큰 가져오기
        try:
            result = subprocess.run(
                ['gcloud', 'auth', 'print-access-token'],
                capture_output=True,
                text=True,
                check=True
            )
            token = result.stdout.strip()
            
            # AccessTokenCredentials 사용
            from google.auth import credentials
            from google.oauth2 import credentials as oauth2_credentials
            
            # 토큰으로 임시 credentials 생성
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            
            # gcloud의 기본 인증 정보 사용 (더 간단한 방법)
            # gcloud config get-value account로 계정 확인
            account_result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'account'],
                capture_output=True,
                text=True,
                check=True
            )
            account = account_result.stdout.strip()
            logger.info(f"gcloud 계정 사용: {account}")
            
            # 프로젝트만 지정하고 gcloud 인증 사용
            # BigQuery 클라이언트가 자동으로 gcloud 인증을 찾도록 함
            return bigquery.Client(project=BIGQUERY_PROJECT_ID)
        except Exception as e2:
            logger.error(f"gcloud 인증도 실패: {e2}")
            raise Exception("BigQuery 인증 실패. 'gcloud auth application-default login'을 실행하세요.")


def load_jsonl_file(file_path: Path) -> List[Dict]:
    """
    JSONL 파일을 읽어서 레코드 리스트로 반환합니다.
    
    Args:
        file_path: JSONL 파일 경로
    
    Returns:
        레코드 리스트
    """
    if not file_path.exists():
        logger.warning(f"파일이 존재하지 않습니다: {file_path}")
        return []
    
    records = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        record = json.loads(line)
                        records.append(record)
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON 파싱 오류 (라인 {line_num}): {e}")
                        continue
    except Exception as e:
        logger.error(f"파일 읽기 오류: {e}")
        return []
    
    logger.info(f"JSONL 파일 로드 완료: {len(records)}개 레코드 ({file_path})")
    return records


def upload_dim_webtoon(jsonl_path: Optional[Path] = None, dry_run: bool = False) -> bool:
    """
    dim_webtoon JSONL 파일을 BigQuery에 업로드합니다.
    
    Args:
        jsonl_path: JSONL 파일 경로 (None이면 기본 경로 사용)
        dry_run: True이면 실제 업로드하지 않고 검증만 수행
    
    Returns:
        성공 여부
    """
    if jsonl_path is None:
        jsonl_path = get_dim_webtoon_jsonl_path()
    
    records = load_jsonl_file(jsonl_path)
    if len(records) == 0:
        logger.warning("업로드할 레코드가 없습니다.")
        return True
    
    if dry_run:
        logger.info(f"[DRY RUN] dim_webtoon 업로드 예정: {len(records)}개 레코드")
        return True
    
    try:
        client = get_bigquery_client()
        table_id = f"{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET_ID}.dim_webtoon"
        
        # 데이터 변환 및 정규화
        for record in records:
            # webtoon_id를 문자열로 보장
            if 'webtoon_id' in record:
                record['webtoon_id'] = str(record['webtoon_id'])
            
            # tags를 ARRAY로 변환 (이미 리스트면 그대로 사용)
            if 'tags' in record and record['tags']:
                if isinstance(record['tags'], str):
                    # 파이프로 구분된 문자열을 리스트로 변환
                    record['tags'] = [t.strip() for t in record['tags'].split('|') if t.strip()]
                elif not isinstance(record['tags'], list):
                    record['tags'] = []
            else:
                record['tags'] = None
            
            # datetime 객체를 ISO 형식 문자열로 변환 (BigQuery load_table_from_json은 문자열을 받음)
            if 'created_at' in record and record['created_at']:
                if isinstance(record['created_at'], datetime):
                    record['created_at'] = record['created_at'].isoformat()
                elif isinstance(record['created_at'], str):
                    # 이미 문자열이면 그대로 사용
                    pass
            if 'updated_at' in record and record['updated_at']:
                if isinstance(record['updated_at'], datetime):
                    record['updated_at'] = record['updated_at'].isoformat()
                elif isinstance(record['updated_at'], str):
                    # 이미 문자열이면 그대로 사용
                    pass
        
        # 임시 테이블에 먼저 업로드
        temp_table_id = f"{table_id}_temp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 스키마 정의 (tags를 REPEATED STRING으로 명시)
        schema = [
            bigquery.SchemaField("webtoon_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("author", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("genre", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("tags", "STRING", mode="REPEATED"),  # REPEATED STRING
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        # 배치로 업로드 (한 번에 최대 1000개씩)
        batch_size = 1000
        total_uploaded = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            job = client.load_table_from_json(
                batch,
                temp_table_id,
                job_config=bigquery.LoadJobConfig(
                    schema=schema,
                    write_disposition=bigquery.WriteDisposition.WRITE_APPEND if i > 0 else bigquery.WriteDisposition.WRITE_TRUNCATE,
                    create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
                    ignore_unknown_values=False,
                )
            )
            
            job.result()  # 작업 완료 대기
            total_uploaded += len(batch)
            logger.info(f"dim_webtoon 임시 테이블 업로드 진행: {total_uploaded}/{len(records)}")
        
        # MERGE 문으로 중복 제거 및 업데이트 (tags는 이미 ARRAY<STRING>으로 로드됨)
        # 임시 테이블에서 중복 제거 (webtoon_id 기준으로 최신 레코드만 선택)
        merge_query = f"""
        MERGE `{table_id}` AS target
        USING (
            SELECT 
                CAST(webtoon_id AS STRING) AS webtoon_id,
                title,
                author,
                genre,
                tags,
                CAST(created_at AS TIMESTAMP) AS created_at,
                CAST(updated_at AS TIMESTAMP) AS updated_at
            FROM (
                SELECT 
                    *,
                    ROW_NUMBER() OVER (PARTITION BY CAST(webtoon_id AS STRING) ORDER BY CAST(updated_at AS TIMESTAMP) DESC) AS rn
                FROM `{temp_table_id}`
            )
            WHERE rn = 1
        ) AS source
        ON target.webtoon_id = source.webtoon_id
        WHEN MATCHED THEN
            UPDATE SET
                title = source.title,
                author = source.author,
                genre = source.genre,
                tags = source.tags,
                updated_at = source.updated_at
        WHEN NOT MATCHED THEN
            INSERT (webtoon_id, title, author, genre, tags, created_at, updated_at)
            VALUES (source.webtoon_id, source.title, source.author, source.genre, source.tags, source.created_at, source.updated_at)
        """
        
        client.query(merge_query).result()
        logger.info(f"✅ dim_webtoon MERGE 완료")
        
        # 임시 테이블 삭제
        client.delete_table(temp_table_id, not_found_ok=True)
        
        logger.info(f"✅ dim_webtoon 업로드 완료: {total_uploaded}개 레코드")
        return True
        
    except Exception as e:
        logger.error(f"❌ dim_webtoon 업로드 실패: {e}")
        return False


def upload_fact_weekly_chart(
    chart_date: date,
    sort_type: Optional[str] = None,
    jsonl_path: Optional[Path] = None,
    dry_run: bool = False
) -> bool:
    """
    fact_weekly_chart JSONL 파일을 BigQuery에 업로드합니다.
    
    Args:
        chart_date: 차트 날짜
        sort_type: 정렬 방식 (None이면 기본값)
        jsonl_path: JSONL 파일 경로 (None이면 기본 경로 사용)
        dry_run: True이면 실제 업로드하지 않고 검증만 수행
    
    Returns:
        성공 여부
    """
    if jsonl_path is None:
        jsonl_path = get_chart_jsonl_path(chart_date, sort_type)
    
    records = load_jsonl_file(jsonl_path)
    if len(records) == 0:
        logger.warning(f"업로드할 레코드가 없습니다: {jsonl_path}")
        return True
    
    if dry_run:
        logger.info(f"[DRY RUN] fact_weekly_chart 업로드 예정: {len(records)}개 레코드")
        return True
    
    try:
        client = get_bigquery_client()
        table_id = f"{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET_ID}.fact_weekly_chart"
        
        # 데이터 변환 및 정규화
        for record in records:
            # webtoon_id를 문자열로 보장
            if 'webtoon_id' in record:
                record['webtoon_id'] = str(record['webtoon_id'])
            
            # datetime 객체를 문자열로 변환 (BigQuery는 문자열을 받아서 자동 변환)
            if 'chart_date' in record and record['chart_date']:
                if isinstance(record['chart_date'], date):
                    record['chart_date'] = record['chart_date'].isoformat()
                elif isinstance(record['chart_date'], datetime):
                    record['chart_date'] = record['chart_date'].date().isoformat()
                # 문자열이면 그대로 사용
            if 'collected_at' in record and record['collected_at']:
                if isinstance(record['collected_at'], datetime):
                    record['collected_at'] = record['collected_at'].isoformat()
                # 문자열이면 그대로 사용
        
        # 임시 테이블에 먼저 업로드
        temp_table_id = f"{table_id}_temp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        batch_size = 1000
        total_uploaded = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            job = client.load_table_from_json(
                batch,
                temp_table_id,
                job_config=bigquery.LoadJobConfig(
                    write_disposition=bigquery.WriteDisposition.WRITE_APPEND if i > 0 else bigquery.WriteDisposition.WRITE_TRUNCATE,
                    create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
                    ignore_unknown_values=False,
                )
            )
            
            job.result()
            total_uploaded += len(batch)
            logger.info(f"fact_weekly_chart 임시 테이블 업로드 진행: {total_uploaded}/{len(records)}")
        
        # MERGE 실행 (webtoon_id를 STRING으로 명시적 변환)
        merge_query = f"""
        MERGE `{table_id}` AS target
        USING (
            SELECT 
                CAST(chart_date AS DATE) AS chart_date,
                CAST(webtoon_id AS STRING) AS webtoon_id,
                rank,
                CAST(collected_at AS TIMESTAMP) AS collected_at,
                weekday,
                year,
                month,
                week,
                view_count
            FROM `{temp_table_id}`
        ) AS source
        ON target.chart_date = source.chart_date 
            AND target.webtoon_id = source.webtoon_id 
            AND COALESCE(target.weekday, '') = COALESCE(source.weekday, '')
        WHEN NOT MATCHED THEN
            INSERT (chart_date, webtoon_id, rank, collected_at, weekday, year, month, week, view_count)
            VALUES (source.chart_date, source.webtoon_id, source.rank, source.collected_at, source.weekday, source.year, source.month, source.week, source.view_count)
        """
        
        client.query(merge_query).result()
        client.delete_table(temp_table_id, not_found_ok=True)
        
        logger.info(f"✅ fact_weekly_chart 업로드 완료: {total_uploaded}개 레코드")
        return True
        
    except Exception as e:
        logger.error(f"❌ fact_weekly_chart 업로드 실패: {e}")
        return False


def upload_fact_webtoon_stats(
    jsonl_path: Optional[Path] = None,
    dry_run: bool = False
) -> bool:
    """
    fact_webtoon_stats JSONL 파일을 BigQuery에 업로드합니다.
    
    Args:
        jsonl_path: JSONL 파일 경로 (None이면 기본 경로 사용)
        dry_run: True이면 실제 업로드하지 않고 검증만 수행
    
    Returns:
        성공 여부
    """
    if jsonl_path is None:
        jsonl_path = get_webtoon_stats_jsonl_path()
    
    records = load_jsonl_file(jsonl_path)
    if len(records) == 0:
        logger.warning("업로드할 레코드가 없습니다.")
        return True
    
    if dry_run:
        logger.info(f"[DRY RUN] fact_webtoon_stats 업로드 예정: {len(records)}개 레코드")
        return True
    
    try:
        client = get_bigquery_client()
        table_id = f"{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET_ID}.fact_webtoon_stats"
        
        # 데이터 변환 및 정규화
        for record in records:
            # webtoon_id를 문자열로 보장
            if 'webtoon_id' in record:
                record['webtoon_id'] = str(record['webtoon_id'])
            
            # datetime 객체를 문자열로 변환
            if 'collected_at' in record and record['collected_at']:
                if isinstance(record['collected_at'], datetime):
                    record['collected_at'] = record['collected_at'].isoformat()
                # 문자열이면 그대로 사용
            
            # total_episode_count를 정수로 변환 (FLOAT64 -> INT64)
            # JSON에서 로드할 때 float로 읽힐 수 있으므로 명시적으로 변환
            if 'total_episode_count' in record:
                if record['total_episode_count'] is not None:
                    try:
                        # float, int, str 모두 처리
                        if isinstance(record['total_episode_count'], float):
                            record['total_episode_count'] = int(record['total_episode_count'])
                        elif isinstance(record['total_episode_count'], str):
                            # 빈 문자열이나 "None" 문자열 처리
                            if record['total_episode_count'].strip() in ('', 'None', 'null'):
                                record['total_episode_count'] = None
                            else:
                                record['total_episode_count'] = int(float(record['total_episode_count']))
                        elif isinstance(record['total_episode_count'], int):
                            # 이미 int면 그대로 사용
                            pass
                        else:
                            # 다른 타입이면 int로 변환 시도
                            record['total_episode_count'] = int(record['total_episode_count'])
                    except (ValueError, TypeError) as e:
                        logger.warning(f"total_episode_count 변환 실패: {record.get('total_episode_count')}, 오류: {e}")
                        record['total_episode_count'] = None
                else:
                    # None이면 그대로 유지
                    record['total_episode_count'] = None
        
        # 임시 테이블에 먼저 업로드 (스키마 명시)
        temp_table_id = f"{table_id}_temp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        batch_size = 1000
        total_uploaded = 0
        
        # 스키마 정의 (total_episode_count를 INT64로 명시)
        schema = [
            bigquery.SchemaField("webtoon_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("collected_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("favorite_count", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("favorite_count_source", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("finished", "BOOLEAN", mode="NULLABLE"),
            bigquery.SchemaField("rest", "BOOLEAN", mode="NULLABLE"),
            bigquery.SchemaField("total_episode_count", "INTEGER", mode="NULLABLE"),  # INT64로 명시
            bigquery.SchemaField("year", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("month", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("week", "INTEGER", mode="REQUIRED"),
        ]
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            # 배치 데이터에서 total_episode_count를 다시 한 번 확인 및 변환
            for record in batch:
                if 'total_episode_count' in record and record['total_episode_count'] is not None:
                    try:
                        if isinstance(record['total_episode_count'], float):
                            record['total_episode_count'] = int(record['total_episode_count'])
                        elif isinstance(record['total_episode_count'], str):
                            if record['total_episode_count'].strip() not in ('', 'None', 'null'):
                                record['total_episode_count'] = int(float(record['total_episode_count']))
                            else:
                                record['total_episode_count'] = None
                    except (ValueError, TypeError):
                        record['total_episode_count'] = None
            
            job = client.load_table_from_json(
                batch,
                temp_table_id,
                job_config=bigquery.LoadJobConfig(
                    write_disposition=bigquery.WriteDisposition.WRITE_APPEND if i > 0 else bigquery.WriteDisposition.WRITE_TRUNCATE,
                    create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
                    ignore_unknown_values=False,
                    schema=schema,  # 스키마 명시
                    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                )
            )
            
            job.result()
            total_uploaded += len(batch)
            logger.info(f"fact_webtoon_stats 임시 테이블 업로드 진행: {total_uploaded}/{len(records)}")
        
        # MERGE 실행 (webtoon_id를 STRING으로, total_episode_count를 INT64로 명시적 변환)
        # SAFE_CAST를 사용하여 FLOAT64 -> INT64 변환 시도
        merge_query = f"""
        MERGE `{table_id}` AS target
        USING (
            SELECT 
                CAST(webtoon_id AS STRING) AS webtoon_id,
                CAST(collected_at AS TIMESTAMP) AS collected_at,
                favorite_count,
                favorite_count_source,
                finished,
                rest,
                SAFE_CAST(total_episode_count AS INT64) AS total_episode_count,
                year,
                month,
                week
            FROM `{temp_table_id}`
            WHERE SAFE_CAST(total_episode_count AS INT64) IS NOT NULL OR total_episode_count IS NULL
        ) AS source
        ON target.webtoon_id = source.webtoon_id 
            AND target.collected_at = source.collected_at
        WHEN NOT MATCHED THEN
            INSERT (webtoon_id, collected_at, favorite_count, favorite_count_source, finished, rest, total_episode_count, year, month, week)
            VALUES (source.webtoon_id, source.collected_at, source.favorite_count, source.favorite_count_source, source.finished, source.rest, source.total_episode_count, source.year, source.month, source.week)
        """
        
        client.query(merge_query).result()
        client.delete_table(temp_table_id, not_found_ok=True)
        
        logger.info(f"✅ fact_webtoon_stats 업로드 완료: {total_uploaded}개 레코드")
        return True
        
    except Exception as e:
        logger.error(f"❌ fact_webtoon_stats 업로드 실패: {e}")
        return False

