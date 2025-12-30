"""
Cloud Functions 진입점: 네이버 웹툰 주간 차트 수집 파이프라인

이 함수는 HTTP 트리거로 실행되며, 전체 ELT 파이프라인을 실행합니다.
- Extract: 네이버 웹툰 API에서 데이터 수집
- Load Raw: GCS에 JSON 원본 저장
- Transform: 데이터 파싱 및 정규화
- Load Refined: BigQuery에 정제된 데이터 저장
"""

import json
import logging
import os
from datetime import date
from typing import Optional

import functions_framework

# 프로젝트 루트를 Python 경로에 추가
import sys
from pathlib import Path

# Cloud Functions에서는 /workspace가 루트
# 로컬 테스트 시에는 상대 경로 사용
if os.path.exists('/workspace'):
    project_root = Path('/workspace')
    sys.path.insert(0, str(project_root))
else:
    # 로컬 테스트용: functions/pipeline_function에서 src로 접근
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    # src 디렉토리도 경로에 추가
    src_path = project_root / 'src'
    if src_path.exists():
        sys.path.insert(0, str(src_path))

from src.extract import extract_webtoon_chart, try_api_endpoints
from src.parse import parse_html_file
from src.parse_api import parse_api_response
from src.transform import transform_and_save, load_dim_webtoon
from src.extract_webtoon_detail import extract_webtoon_detail
from src.transform_webtoon_stats import transform_and_save_webtoon_stats
from src.upload_gcs import upload_chart_data_to_gcs, upload_webtoon_detail_to_gcs
from src.upload_bigquery import (
    upload_dim_webtoon,
    upload_fact_weekly_chart,
    upload_fact_webtoon_stats,
    get_bigquery_client,
)
from src.utils import setup_logging

# 환경 변수
GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'naver-webtoon-raw')
BIGQUERY_PROJECT_ID = os.getenv('BIGQUERY_PROJECT_ID', 'naver-webtoon-collector')
BIGQUERY_DATASET_ID = os.getenv('BIGQUERY_DATASET_ID', 'naver_webtoon')

# 로깅 설정
setup_logging()
logger = logging.getLogger(__name__)


@functions_framework.http
def main(request):
    """
    Cloud Functions HTTP 트리거 진입점
    
    Args:
        request: Flask Request 객체
    
    Returns:
        HTTP 응답 (JSON)
    """
    try:
        # 요청 본문 파싱
        request_json = request.get_json(silent=True)
        if request_json is None:
            request_json = {}
        
        # 파라미터 추출
        chart_date_str = request_json.get('date')
        if chart_date_str:
            try:
                chart_date = date.fromisoformat(chart_date_str)
            except ValueError:
                logger.error(f"잘못된 날짜 형식: {chart_date_str}")
                return {'error': f'Invalid date format: {chart_date_str}'}, 400
        else:
            chart_date = date.today()
        
        sort_types = request_json.get('sort_types', ['popular', 'view'])
        limit = request_json.get('limit')  # 테스트용 제한
        delete_existing = request_json.get('delete_existing', False)  # 기존 데이터 삭제 여부
        
        # 기존 데이터 삭제 (요청 시)
        if delete_existing:
            logger.info(f"\n{'='*60}")
            logger.info(f"기존 데이터 삭제 시작: date={chart_date}")
            logger.info(f"{'='*60}")
            
            try:
                from google.cloud import bigquery
                client = get_bigquery_client()
                
                # fact_weekly_chart에서 해당 날짜 데이터 삭제
                delete_query = f"""
                DELETE FROM `{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET_ID}.fact_weekly_chart`
                WHERE chart_date = '{chart_date}'
                """
                query_job = client.query(delete_query)
                query_job.result()
                deleted_count = query_job.num_dml_affected_rows if hasattr(query_job, 'num_dml_affected_rows') else 0
                logger.info(f"✅ fact_weekly_chart에서 {deleted_count}개 레코드 삭제됨")
                
                # GCS에서 해당 날짜 데이터 삭제
                from google.cloud import storage
                storage_client = storage.Client(project=BIGQUERY_PROJECT_ID)
                bucket = storage_client.bucket(GCS_BUCKET_NAME)
                
                # 날짜별 경로 삭제
                date_prefix = f"raw_html/{chart_date}/"
                blobs = bucket.list_blobs(prefix=date_prefix)
                deleted_blobs = 0
                for blob in blobs:
                    blob.delete()
                    deleted_blobs += 1
                
                if deleted_blobs > 0:
                    logger.info(f"✅ GCS에서 {deleted_blobs}개 파일 삭제됨")
                else:
                    logger.info("GCS에 해당 날짜 데이터가 없습니다.")
                
                logger.info(f"✅ 기존 데이터 삭제 완료")
            except Exception as e:
                logger.error(f"기존 데이터 삭제 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()
                # 삭제 실패해도 계속 진행
        
        logger.info(f"파이프라인 실행 시작: date={chart_date}, sort_types={sort_types}")
        
        all_success = True
        
        # 각 정렬 타입별로 수집
        for sort_type in sort_types:
            sort_name = sort_type if sort_type else "default"
            logger.info(f"\n{'='*60}")
            logger.info(f"정렬 타입: {sort_name}")
            logger.info(f"{'='*60}")
            
            try:
                # Step 1: Extract (API에서 데이터 수집)
                logger.info(f"데이터 수집 시작... (정렬: {sort_name})")
                api_data = try_api_endpoints(sort_type=sort_type)
                
                if api_data is None:
                    logger.error(f"데이터 수집 실패 (정렬: {sort_name})")
                    all_success = False
                    continue
                
                # Step 2: Load Raw (GCS에 JSON 원본 저장)
                logger.info("GCS에 원본 데이터 저장 중...")
                # 임시 파일에 저장 후 GCS 업로드
                from tempfile import NamedTemporaryFile
                import json as json_module
                
                with NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_file:
                    json_module.dump(api_data, tmp_file, ensure_ascii=False, indent=2)
                    tmp_path = Path(tmp_file.name)
                
                try:
                    gcs_success = upload_chart_data_to_gcs(
                        chart_date,
                        sort_type=sort_type,
                        json_file_path=tmp_path,
                        dry_run=False
                    )
                    if not gcs_success:
                        logger.warning(f"GCS 업로드 실패 (정렬: {sort_name}), 계속 진행...")
                finally:
                    # 임시 파일 삭제
                    if tmp_path.exists():
                        tmp_path.unlink()
                
                # Step 3: Parse (데이터 파싱)
                logger.info("데이터 파싱 시작...")
                parsed_data = parse_api_response(api_data)
                
                if len(parsed_data) == 0:
                    logger.error("파싱된 데이터가 없습니다.")
                    all_success = False
                    continue
                
                logger.info(f"파싱 완료: {len(parsed_data)}개 웹툰 데이터")
                
                # Step 4: Transform & Load Refined (BigQuery에 직접 저장)
                # transform_and_save를 사용하여 로컬 파일에 저장 후 BigQuery 업로드
                logger.info("데이터 변환 및 저장 시작...")
                
                # 임시 디렉토리 사용 (Cloud Functions의 /tmp 사용)
                import tempfile
                temp_dir = Path(tempfile.gettempdir()) / 'webtoon_pipeline'
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                # 환경 변수 설정 (로컬 파일 저장 경로)
                os.environ['DATA_DIR'] = str(temp_dir)
                
                # transform_and_save 실행 (로컬 파일에 저장)
                success = transform_and_save(parsed_data, chart_date, sort_type=sort_type)
                
                if success:
                    # 저장된 JSONL 파일을 BigQuery에 업로드
                    from src.utils import get_dim_webtoon_jsonl_path, get_chart_jsonl_path
                    
                    # dim_webtoon 업로드
                    dim_jsonl_path = get_dim_webtoon_jsonl_path()
                    if dim_jsonl_path.exists():
                        logger.info(f"dim_webtoon.jsonl 파일 발견, BigQuery 업로드 시작: {dim_jsonl_path}")
                        try:
                            upload_success = upload_dim_webtoon(jsonl_path=dim_jsonl_path, dry_run=False)
                            if upload_success:
                                logger.info("dim_webtoon BigQuery 업로드 성공")
                            else:
                                logger.error("dim_webtoon BigQuery 업로드 실패")
                        except Exception as e:
                            logger.error(f"dim_webtoon BigQuery 업로드 중 오류 발생: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        logger.warning(f"dim_webtoon.jsonl 파일이 존재하지 않습니다: {dim_jsonl_path}")
                    
                    # fact_weekly_chart 업로드
                    fact_jsonl_path = get_chart_jsonl_path(chart_date, sort_type)
                    if fact_jsonl_path.exists():
                        logger.info(f"fact_weekly_chart.jsonl 파일 발견, BigQuery 업로드 시작: {fact_jsonl_path}")
                        try:
                            upload_success = upload_fact_weekly_chart(
                                chart_date=chart_date,
                                sort_type=sort_type,
                                jsonl_path=fact_jsonl_path,
                                dry_run=False
                            )
                            if upload_success:
                                logger.info("fact_weekly_chart BigQuery 업로드 성공")
                            else:
                                logger.error("fact_weekly_chart BigQuery 업로드 실패")
                        except Exception as e:
                            logger.error(f"fact_weekly_chart BigQuery 업로드 중 오류 발생: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        logger.warning(f"fact_weekly_chart.jsonl 파일이 존재하지 않습니다: {fact_jsonl_path}")
                else:
                    logger.error(f"데이터 변환 및 저장 실패 (정렬: {sort_name})")
                    all_success = False
                    continue
                
                logger.info(f"✅ 정렬 타입 '{sort_name}' 수집 완료!")
                
            except Exception as e:
                logger.error(f"정렬 타입 '{sort_name}' 처리 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()
                all_success = False
        
        # 웹툰 상세 정보 수집 (genre, tags 정보 수집) - 필수 실행
        logger.info("\n" + "="*60)
        logger.info("웹툰 상세 정보 수집 시작... (genre, tags 수집)")
        logger.info("="*60)
        
        try:
            # dim_webtoon에서 모든 웹툰 ID 가져오기
            from src.transform import load_dim_webtoon
            dim_df = load_dim_webtoon()
            
            if len(dim_df) == 0:
                logger.warning("수집할 웹툰이 없습니다. 차트 수집을 먼저 실행하세요.")
            else:
                webtoon_ids = dim_df['webtoon_id'].astype(str).unique().tolist()
                
                # limit 파라미터 적용 (테스트용)
                if limit is not None and limit > 0:
                    webtoon_ids = webtoon_ids[:limit]
                    logger.info(f"제한 모드: {limit}개 웹툰만 상세 정보 수집합니다.")
                
                logger.info(f"총 {len(webtoon_ids)}개 웹툰의 상세 정보 수집 시작...")
                logger.info(f"예상 소요 시간: 약 {len(webtoon_ids) * 2 / 60:.1f}분 (각 웹툰당 약 2초)")
                
                detail_data_list = []
                batch_size = 10  # Rate limiting 배치 크기
                batch_delay = 5  # Rate limiting 배치 간 대기 시간 (초)
                save_batch_size = 100  # 저장 배치 크기 (100개마다 저장 및 업로드)
                
                from src.transform import merge_dim_webtoon, save_dim_webtoon, load_dim_webtoon
                from src.models import create_dim_webtoon_record
                
                # dim_webtoon 로드 (배치 저장 시 사용)
                dim_df = load_dim_webtoon()
                dim_df['webtoon_id'] = dim_df['webtoon_id'].astype(str)
                dim_webtoon_ids = set(dim_df['webtoon_id'])
                
                for i, webtoon_id in enumerate(webtoon_ids, 1):
                    try:
                        # 웹툰 상세 정보 수집
                        detail_data = extract_webtoon_detail(webtoon_id, use_html_fallback=True)
                        
                        if detail_data:
                            detail_data_list.append(detail_data)
                            if i % 10 == 0:
                                logger.info(f"[{i}/{len(webtoon_ids)}] 웹툰 상세 정보 수집 진행 중... (성공: {len(detail_data_list)}개)")
                        else:
                            logger.warning(f"[{i}/{len(webtoon_ids)}] 웹툰 상세 정보 수집 실패: {webtoon_id}")
                        
                        # Rate limiting: 각 요청 간 1.5초 대기
                        import time
                        time.sleep(1.5)
                        
                        # Rate limiting 배치 처리: 10개마다 긴 대기
                        if i % batch_size == 0 and i < len(webtoon_ids):
                            logger.info(f"Rate limiting 배치 완료: {i}/{len(webtoon_ids)}개 처리됨. {batch_delay}초 대기...")
                            time.sleep(batch_delay)
                        
                        # 저장 배치 처리: 100개마다 저장 및 BigQuery 업로드
                        if len(detail_data_list) >= save_batch_size and i % save_batch_size == 0:
                            logger.info(f"\n{'='*60}")
                            logger.info(f"배치 저장 시작: {len(detail_data_list)}개 데이터 저장 및 업로드")
                            logger.info(f"{'='*60}")
                            
                            # 현재 배치 데이터 추출
                            batch_data = detail_data_list[:save_batch_size]
                            detail_data_list = detail_data_list[save_batch_size:]  # 남은 데이터는 다음 배치에서 처리
                            
                            # fact_webtoon_stats 저장
                            try:
                                stats_success = transform_and_save_webtoon_stats(batch_data, dim_webtoon_ids)
                                if stats_success:
                                    logger.info(f"✅ fact_webtoon_stats 배치 저장 완료: {len(batch_data)}개")
                                    
                                    # fact_webtoon_stats를 BigQuery에 업로드
                                    from src.utils import get_webtoon_stats_jsonl_path
                                    stats_jsonl_path = get_webtoon_stats_jsonl_path()
                                    if stats_jsonl_path.exists():
                                        logger.info("fact_webtoon_stats를 BigQuery에 업로드 중...")
                                        try:
                                            upload_success = upload_fact_webtoon_stats(jsonl_path=stats_jsonl_path, dry_run=False)
                                            if upload_success:
                                                logger.info(f"✅ fact_webtoon_stats BigQuery 업로드 성공 ({len(batch_data)}개)")
                                            else:
                                                logger.error("fact_webtoon_stats BigQuery 업로드 실패")
                                        except Exception as e:
                                            logger.error(f"fact_webtoon_stats BigQuery 업로드 중 오류 발생: {e}")
                                            import traceback
                                            traceback.print_exc()
                                else:
                                    logger.error("fact_webtoon_stats 배치 저장 실패")
                            except Exception as e:
                                logger.error(f"fact_webtoon_stats 배치 저장 중 오류 발생: {e}")
                                import traceback
                                traceback.print_exc()
                            
                            # dim_webtoon 업데이트 (genre, tags 정보 추가)
                            logger.info("dim_webtoon 배치 업데이트 중 (genre, tags 정보 추가)...")
                            update_records = []
                            
                            for detail_data in batch_data:
                                webtoon_id = str(detail_data.get('webtoon_id')) if detail_data.get('webtoon_id') else None
                                genre = detail_data.get('genre')
                                tags = detail_data.get('tags')
                                
                                if webtoon_id and webtoon_id in dim_webtoon_ids:
                                    # 기존 레코드 찾기
                                    existing = dim_df[dim_df['webtoon_id'] == webtoon_id]
                                    if len(existing) > 0:
                                        # genre나 tags가 있으면 업데이트
                                        if genre or tags:
                                            existing_record = existing.iloc[0].to_dict()
                                            
                                            # 기존 tags 처리
                                            existing_tags = existing_record.get('tags')
                                            if isinstance(existing_tags, str):
                                                existing_tags = [t.strip() for t in existing_tags.split('|') if t.strip()] if existing_tags else []
                                            elif not isinstance(existing_tags, list):
                                                existing_tags = []
                                            
                                            # 새 tags와 병합 (중복 제거)
                                            new_tags = tags if tags else []
                                            if isinstance(new_tags, list):
                                                combined_tags = list(set(existing_tags + new_tags))
                                            else:
                                                combined_tags = existing_tags
                                            
                                            # 업데이트 레코드 생성
                                            update_record = create_dim_webtoon_record(
                                                webtoon_id=webtoon_id,
                                                title=existing_record.get('title', ''),
                                                author=existing_record.get('author'),
                                                genre=genre if genre else existing_record.get('genre'),
                                                tags=combined_tags if combined_tags else None,
                                            )
                                            update_records.append(update_record)
                            
                            if len(update_records) > 0:
                                dim_df = merge_dim_webtoon(dim_df, update_records)
                                save_dim_webtoon(dim_df)
                                logger.info(f"✅ dim_webtoon 배치 업데이트 완료: {len(update_records)}개 레코드 업데이트됨")
                                
                                # 업데이트된 dim_webtoon을 BigQuery에 업로드
                                from src.utils import get_dim_webtoon_jsonl_path
                                dim_jsonl_path = get_dim_webtoon_jsonl_path()
                                if dim_jsonl_path.exists():
                                    logger.info("업데이트된 dim_webtoon을 BigQuery에 업로드 중...")
                                    try:
                                        upload_success = upload_dim_webtoon(jsonl_path=dim_jsonl_path, dry_run=False)
                                        if upload_success:
                                            logger.info(f"✅ dim_webtoon BigQuery 업로드 성공 ({len(update_records)}개 업데이트)")
                                        else:
                                            logger.error("dim_webtoon BigQuery 업로드 실패")
                                    except Exception as e:
                                        logger.error(f"dim_webtoon BigQuery 업로드 중 오류 발생: {e}")
                                        import traceback
                                        traceback.print_exc()
                            
                            logger.info(f"✅ 배치 저장 완료: {i}/{len(webtoon_ids)}개 처리됨")
                            logger.info(f"{'='*60}\n")
                            
                    except Exception as e:
                        logger.error(f"웹툰 상세 정보 수집 실패 (webtoon_id={webtoon_id}): {e}")
                        continue
                
                # 남은 데이터 처리 (마지막 배치)
                if len(detail_data_list) > 0:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"마지막 배치 저장 시작: {len(detail_data_list)}개 데이터 저장 및 업로드")
                    logger.info(f"{'='*60}")
                    
                    # fact_webtoon_stats 저장
                    try:
                        stats_success = transform_and_save_webtoon_stats(detail_data_list, dim_webtoon_ids)
                        if stats_success:
                            logger.info(f"✅ fact_webtoon_stats 마지막 배치 저장 완료: {len(detail_data_list)}개")
                            
                            # fact_webtoon_stats를 BigQuery에 업로드
                            from src.utils import get_webtoon_stats_jsonl_path
                            stats_jsonl_path = get_webtoon_stats_jsonl_path()
                            if stats_jsonl_path.exists():
                                logger.info("fact_webtoon_stats를 BigQuery에 업로드 중...")
                                try:
                                    upload_success = upload_fact_webtoon_stats(jsonl_path=stats_jsonl_path, dry_run=False)
                                    if upload_success:
                                        logger.info(f"✅ fact_webtoon_stats BigQuery 업로드 성공 ({len(detail_data_list)}개)")
                                    else:
                                        logger.error("fact_webtoon_stats BigQuery 업로드 실패")
                                except Exception as e:
                                    logger.error(f"fact_webtoon_stats BigQuery 업로드 중 오류 발생: {e}")
                                    import traceback
                                    traceback.print_exc()
                        else:
                            logger.error("fact_webtoon_stats 마지막 배치 저장 실패")
                    except Exception as e:
                        logger.error(f"fact_webtoon_stats 마지막 배치 저장 중 오류 발생: {e}")
                        import traceback
                        traceback.print_exc()
                    
                    # dim_webtoon 업데이트 (genre, tags 정보 추가)
                    logger.info("dim_webtoon 마지막 배치 업데이트 중 (genre, tags 정보 추가)...")
                    update_records = []
                    
                    for detail_data in detail_data_list:
                        webtoon_id = str(detail_data.get('webtoon_id')) if detail_data.get('webtoon_id') else None
                        genre = detail_data.get('genre')
                        tags = detail_data.get('tags')
                        
                        if webtoon_id and webtoon_id in dim_webtoon_ids:
                            # 기존 레코드 찾기
                            existing = dim_df[dim_df['webtoon_id'] == webtoon_id]
                            if len(existing) > 0:
                                # genre나 tags가 있으면 업데이트
                                if genre or tags:
                                    existing_record = existing.iloc[0].to_dict()
                                    
                                    # 기존 tags 처리
                                    existing_tags = existing_record.get('tags')
                                    if isinstance(existing_tags, str):
                                        existing_tags = [t.strip() for t in existing_tags.split('|') if t.strip()] if existing_tags else []
                                    elif not isinstance(existing_tags, list):
                                        existing_tags = []
                                    
                                    # 새 tags와 병합 (중복 제거)
                                    new_tags = tags if tags else []
                                    if isinstance(new_tags, list):
                                        combined_tags = list(set(existing_tags + new_tags))
                                    else:
                                        combined_tags = existing_tags
                                    
                                    # 업데이트 레코드 생성
                                    update_record = create_dim_webtoon_record(
                                        webtoon_id=webtoon_id,
                                        title=existing_record.get('title', ''),
                                        author=existing_record.get('author'),
                                        genre=genre if genre else existing_record.get('genre'),
                                        tags=combined_tags if combined_tags else None,
                                    )
                                    update_records.append(update_record)
                    
                    if len(update_records) > 0:
                        dim_df = merge_dim_webtoon(dim_df, update_records)
                        save_dim_webtoon(dim_df)
                        logger.info(f"✅ dim_webtoon 마지막 배치 업데이트 완료: {len(update_records)}개 레코드 업데이트됨")
                        
                        # 업데이트된 dim_webtoon을 BigQuery에 업로드
                        from src.utils import get_dim_webtoon_jsonl_path
                        dim_jsonl_path = get_dim_webtoon_jsonl_path()
                        if dim_jsonl_path.exists():
                            logger.info("업데이트된 dim_webtoon을 BigQuery에 업로드 중...")
                            try:
                                upload_success = upload_dim_webtoon(jsonl_path=dim_jsonl_path, dry_run=False)
                                if upload_success:
                                    logger.info(f"✅ dim_webtoon BigQuery 업로드 성공 ({len(update_records)}개 업데이트)")
                                else:
                                    logger.error("dim_webtoon BigQuery 업로드 실패")
                            except Exception as e:
                                logger.error(f"dim_webtoon BigQuery 업로드 중 오류 발생: {e}")
                                import traceback
                                traceback.print_exc()
                    else:
                        logger.warning(f"dim_webtoon 업데이트할 레코드가 없습니다. (genre/tags가 있는 detail_data: {sum(1 for d in detail_data_list if d.get('genre') or d.get('tags'))}개)")
                    
                    logger.info(f"✅ 마지막 배치 저장 완료")
                    logger.info(f"{'='*60}\n")
                else:
                    logger.warning("수집된 웹툰 상세 정보가 없습니다.")
        except Exception as e:
            logger.error(f"웹툰 상세 정보 수집 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            all_success = False
        
        if all_success:
            logger.info("🎉 파이프라인 실행 완료!")
            return {'status': 'success', 'date': str(chart_date)}, 200
        else:
            logger.error("❌ 파이프라인 실행 중 일부 오류 발생")
            return {'status': 'partial_failure', 'date': str(chart_date)}, 500
            
    except Exception as e:
        logger.error(f"파이프라인 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}, 500

