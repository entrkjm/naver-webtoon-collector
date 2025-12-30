"""
파이프라인 통합 실행 스크립트

Extract → Parse → Transform 전체 플로우를 실행합니다.
"""

import argparse
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Optional

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.extract import extract_webtoon_chart
from src.parse import parse_html_file
from src.transform import transform_and_save, load_dim_webtoon
from src.extract_webtoon_detail import extract_webtoon_detail
from src.transform_webtoon_stats import transform_and_save_webtoon_stats
from src.utils import setup_logging, get_log_file_path

logger = None


def run_pipeline(chart_date: date = None, html_file: Path = None, sort_types: list = None, limit: Optional[int] = None) -> bool:
    """
    전체 파이프라인을 실행합니다.
    
    Args:
        chart_date: 수집 날짜 (None이면 오늘 날짜)
        html_file: 이미 수집된 HTML 파일 경로 (None이면 새로 수집)
        sort_types: 정렬 방식 리스트 (["popular", "view"] 등), None이면 기본값만
        limit: 테스트용 웹툰 수 제한 (None이면 전체 수집)
    
    Returns:
        성공 여부
    """
    global logger
    # 로그 파일 경로 생성
    log_file = get_log_file_path("pipeline")
    setup_logging(log_file=log_file)
    logger = logging.getLogger(__name__)
    logger.info(f"로그 파일: {log_file}")
    
    if sort_types is None:
        sort_types = [None]  # 기본값만
    
    if chart_date is None:
        chart_date = date.today()
    
    try:
        all_success = True
        
        # 각 정렬 타입별로 수집
        for sort_type in sort_types:
            sort_name = sort_type if sort_type else "default"
            logger.info(f"\n{'='*60}")
            logger.info(f"정렬 타입: {sort_name}")
            logger.info(f"{'='*60}")
            
            try:
                # Step 1: Extract (HTML 수집)
                if html_file:
                    logger.info(f"기존 HTML 파일 사용: {html_file}")
                    html_path = html_file
                else:
                    logger.info(f"HTML 수집 시작... (정렬: {sort_name})")
                    html_path = extract_webtoon_chart(chart_date, sort_type=sort_type)
                    if html_path is None:
                        logger.error(f"HTML 수집 실패 (정렬: {sort_name})")
                        all_success = False
                        continue
                
                # Step 2: Parse (HTML 파싱)
                logger.info("HTML 파싱 시작...")
                parsed_data = parse_html_file(html_path)
                if len(parsed_data) == 0:
                    logger.error("파싱된 데이터가 없습니다. HTML 구조를 확인하세요.")
                    all_success = False
                    continue
                
                logger.info(f"파싱 완료: {len(parsed_data)}개 웹툰 데이터")
                
                # Step 3: Transform (데이터 변환 및 저장)
                # 정렬 타입별로 별도 파일로 저장하거나, 하나의 파일에 통합
                logger.info("데이터 변환 및 저장 시작...")
                success = transform_and_save(parsed_data, chart_date, sort_type=sort_type)
                
                if success:
                    logger.info(f"✅ 정렬 타입 '{sort_name}' 수집 완료!")
                    
                    # Step 4: GCS 업로드 (선택적, 환경 변수로 제어)
                    if os.getenv('UPLOAD_TO_GCS', 'false').lower() == 'true':
                        logger.info("GCS 업로드 시작...")
                        from src.upload_gcs import upload_chart_data_to_gcs
                        gcs_success = upload_chart_data_to_gcs(chart_date, sort_type=sort_type)
                        if gcs_success:
                            logger.info(f"✅ GCS 업로드 완료 (정렬: {sort_name})")
                        else:
                            logger.warning(f"⚠️ GCS 업로드 실패 (정렬: {sort_name}), 계속 진행...")
                else:
                    logger.error(f"❌ 정렬 타입 '{sort_name}' 데이터 변환 및 저장 실패")
                    all_success = False
                    
            except Exception as e:
                logger.error(f"정렬 타입 '{sort_name}' 처리 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()
                all_success = False
        
        # Step 4: 웹툰 상세 정보 수집 (모든 정렬 타입 수집 완료 후)
        logger.info("\n" + "="*60)
        logger.info("웹툰 상세 정보 수집 시작...")
        logger.info("="*60)
        
        try:
            # dim_webtoon에서 모든 웹툰 ID 가져오기
            dim_df = load_dim_webtoon()
            if len(dim_df) == 0:
                logger.warning("수집할 웹툰이 없습니다. 차트 수집을 먼저 실행하세요.")
            else:
                webtoon_ids = dim_df['webtoon_id'].astype(str).unique().tolist()
                
                # 테스트용 제한
                if limit is not None and limit > 0:
                    webtoon_ids = webtoon_ids[:limit]
                    logger.info(f"테스트 모드: {limit}개 웹툰만 수집합니다.")
                
                logger.info(f"총 {len(webtoon_ids)}개 웹툰의 상세 정보 수집 시작...")
                
                detail_data_list = []
                batch_size = 10
                batch_delay = 10  # 배치 간 대기 시간 (초)
                
                for i, webtoon_id in enumerate(webtoon_ids, 1):
                    try:
                        # 웹툰 상세 정보 수집
                        detail_data = extract_webtoon_detail(webtoon_id, use_html_fallback=True)
                        
                        if detail_data:
                            detail_data_list.append(detail_data)
                            logger.debug(f"[{i}/{len(webtoon_ids)}] 웹툰 상세 정보 수집: {webtoon_id}")
                        else:
                            logger.warning(f"[{i}/{len(webtoon_ids)}] 웹툰 상세 정보 수집 실패: {webtoon_id}")
                        
                        # Rate limiting: 각 요청 간 1-2초 대기
                        import time
                        time.sleep(1.5)
                        
                        # 배치 처리: 10개마다 긴 대기
                        if i % batch_size == 0:
                            logger.info(f"배치 완료: {i}/{len(webtoon_ids)}개 처리됨. {batch_delay}초 대기...")
                            time.sleep(batch_delay)
                            
                    except Exception as e:
                        logger.error(f"웹툰 상세 정보 수집 실패 (webtoon_id={webtoon_id}): {e}")
                        continue
                
                # 수집된 데이터 저장
                if len(detail_data_list) > 0:
                    dim_webtoon_ids = set(dim_df['webtoon_id'].astype(str))
                    
                    # fact_webtoon_stats 저장
                    success = transform_and_save_webtoon_stats(detail_data_list, dim_webtoon_ids)
                    
                    if success:
                        logger.info(f"✅ 웹툰 상세 정보 수집 완료: {len(detail_data_list)}개")
                        
                        # dim_webtoon 업데이트 (genre, tags 정보 추가)
                        logger.info("dim_webtoon 업데이트 중 (genre, tags 정보 추가)...")
                        from src.transform import merge_dim_webtoon, save_dim_webtoon
                        from src.models import create_dim_webtoon_record, validate_dim_webtoon_record
                        
                        dim_df = load_dim_webtoon()
                        # webtoon_id를 문자열로 변환하여 비교
                        dim_df['webtoon_id'] = dim_df['webtoon_id'].astype(str)
                        update_records = []
                        
                        for detail_data in detail_data_list:
                            webtoon_id = str(detail_data.get('webtoon_id')) if detail_data.get('webtoon_id') else None
                            genre = detail_data.get('genre')
                            tags = detail_data.get('tags')
                            
                            logger.debug(f"업데이트 체크: webtoon_id={webtoon_id}, genre={genre}, tags={tags}")
                            
                            if webtoon_id and webtoon_id in dim_webtoon_ids:
                                # 기존 레코드 찾기
                                existing = dim_df[dim_df['webtoon_id'] == webtoon_id]
                                if len(existing) > 0:
                                    # genre나 tags가 있으면 업데이트
                                    if genre or tags:
                                        # 기존 정보 유지하면서 genre, tags만 업데이트
                                        existing_record = existing.iloc[0].to_dict()
                                        
                                        # 기존 tags는 이미 리스트로 변환되어 있음 (load_dim_webtoon_csv에서 처리)
                                        existing_tags = existing_record.get('tags')
                                        
                                        update_record = create_dim_webtoon_record(
                                            webtoon_id=existing_record['webtoon_id'],
                                            title=existing_record['title'],
                                            author=existing_record.get('author'),
                                            genre=genre if genre else existing_record.get('genre'),
                                            tags=tags if tags else existing_tags,
                                        )
                                        if validate_dim_webtoon_record(update_record):
                                            update_records.append(update_record)
                                            logger.debug(f"업데이트 레코드 추가: webtoon_id={webtoon_id}, genre={genre}, tags={len(tags) if tags else 0}개")
                                        else:
                                            logger.warning(f"업데이트 레코드 검증 실패: webtoon_id={webtoon_id}")
                                else:
                                    logger.warning(f"기존 레코드를 찾을 수 없음: webtoon_id={webtoon_id}")
                            else:
                                logger.warning(f"webtoon_id가 dim_webtoon_ids에 없음: webtoon_id={webtoon_id}, dim_webtoon_ids에 있음: {webtoon_id in dim_webtoon_ids if webtoon_id else False}")
                        
                        if len(update_records) > 0:
                            updated_df = merge_dim_webtoon(dim_df, update_records)
                            save_dim_webtoon(updated_df)
                            logger.info(f"dim_webtoon 업데이트 완료: {len(update_records)}개 레코드 업데이트됨")
                        else:
                            logger.warning(f"dim_webtoon 업데이트할 레코드가 없습니다. (genre/tags가 있는 detail_data: {sum(1 for d in detail_data_list if d.get('genre') or d.get('tags'))}개)")
                    else:
                        logger.error("❌ 웹툰 상세 정보 저장 실패")
                        all_success = False
                else:
                    logger.warning("수집된 웹툰 상세 정보가 없습니다.")
                    
        except Exception as e:
            logger.error(f"웹툰 상세 정보 수집 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            all_success = False
        
        if all_success:
            logger.info("\n🎉 모든 정렬 타입 수집 완료!")
            return True
        else:
            logger.error("\n⚠️ 일부 정렬 타입 수집 실패")
            return False
            
    except Exception as e:
        logger.error(f"파이프라인 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='네이버 웹툰 주간 차트 수집 파이프라인')
    parser.add_argument(
        '--date',
        type=str,
        help='수집 날짜 (YYYY-MM-DD 형식, 기본값: 오늘)'
    )
    parser.add_argument(
        '--html',
        type=str,
        help='이미 수집된 HTML 파일 경로 (지정 시 새로 수집하지 않음)'
    )
    parser.add_argument(
        '--sort',
        type=str,
        nargs='+',
        choices=['popular', 'view'],
        help='정렬 방식 (popular: 인기순, view: 조회순). 여러 개 지정 가능 (예: --sort popular view)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='테스트용 웹툰 수 제한 (상세 정보 수집 시에만 적용, None이면 전체 수집)'
    )
    
    args = parser.parse_args()
    
    # 날짜 파싱
    chart_date = None
    if args.date:
        try:
            chart_date = date.fromisoformat(args.date)
        except ValueError:
            print(f"잘못된 날짜 형식: {args.date} (YYYY-MM-DD 형식 사용)")
            sys.exit(1)
    
    # HTML 파일 경로
    html_file = None
    if args.html:
        html_file = Path(args.html)
        if not html_file.exists():
            print(f"HTML 파일을 찾을 수 없습니다: {html_file}")
            sys.exit(1)
    
    # 정렬 타입 설정
    sort_types = args.sort if args.sort else None
    
    # 파이프라인 실행
    success = run_pipeline(
        chart_date=chart_date,
        html_file=html_file,
        sort_types=sort_types,
        limit=args.limit
    )
    sys.exit(0 if success else 1)

