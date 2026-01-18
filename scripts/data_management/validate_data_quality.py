#!/usr/bin/env python3
"""
데이터 품질 검증 스크립트

BigQuery의 데이터 품질을 검증합니다:
- 중복 레코드 확인
- Foreign Key 관계 확인
- 필수 필드 누락 확인
- 데이터 일관성 확인
"""

import sys
from pathlib import Path
from datetime import date, datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from src.utils import setup_logging
import logging

logger = logging.getLogger(__name__)

# BigQuery 설정
PROJECT_ID = "naver-webtoon-collector"
DATASET_ID = "naver_webtoon"


def get_bigquery_client():
    """BigQuery 클라이언트를 생성합니다."""
    return bigquery.Client(project=PROJECT_ID)


def check_dim_webtoon_duplicates(client):
    """dim_webtoon 테이블의 중복 레코드를 확인합니다."""
    logger.info("dim_webtoon 중복 레코드 확인 중...")
    
    query = f"""
    SELECT 
        webtoon_id,
        COUNT(*) AS count
    FROM `{PROJECT_ID}.{DATASET_ID}.dim_webtoon`
    GROUP BY webtoon_id
    HAVING COUNT(*) > 1
    """
    
    results = client.query(query).result()
    duplicates = list(results)
    
    if len(duplicates) > 0:
        logger.warning(f"⚠️  dim_webtoon 중복 레코드 발견: {len(duplicates)}개")
        for row in duplicates:
            logger.warning(f"  - webtoon_id: {row.webtoon_id}, 중복 수: {row.count}")
        return False
    else:
        logger.info("✅ dim_webtoon 중복 레코드 없음")
        return True


def check_fact_weekly_chart_duplicates(client, chart_date: date = None):
    """fact_weekly_chart 테이블의 중복 레코드를 확인합니다."""
    logger.info("fact_weekly_chart 중복 레코드 확인 중...")
    
    date_filter = ""
    if chart_date:
        date_filter = f"AND chart_date = '{chart_date}'"
    
    query = f"""
    SELECT 
        chart_date,
        webtoon_id,
        weekday,
        COUNT(*) AS count
    FROM `{PROJECT_ID}.{DATASET_ID}.fact_weekly_chart`
    WHERE 1=1 {date_filter}
    GROUP BY chart_date, webtoon_id, weekday
    HAVING COUNT(*) > 1
    """
    
    results = client.query(query).result()
    duplicates = list(results)
    
    if len(duplicates) > 0:
        logger.warning(f"⚠️  fact_weekly_chart 중복 레코드 발견: {len(duplicates)}개")
        for row in duplicates[:10]:  # 최대 10개만 출력
            logger.warning(f"  - chart_date: {row.chart_date}, webtoon_id: {row.webtoon_id}, weekday: {row.weekday}, 중복 수: {row.count}")
        return False
    else:
        logger.info("✅ fact_weekly_chart 중복 레코드 없음")
        return True


def check_foreign_key_relationships(client):
    """Foreign Key 관계를 확인합니다."""
    logger.info("Foreign Key 관계 확인 중...")
    
    query = f"""
    SELECT 
        f.webtoon_id,
        COUNT(*) AS orphan_count
    FROM `{PROJECT_ID}.{DATASET_ID}.fact_weekly_chart` f
    LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.dim_webtoon` d
        ON f.webtoon_id = d.webtoon_id
    WHERE d.webtoon_id IS NULL
    GROUP BY f.webtoon_id
    """
    
    results = client.query(query).result()
    orphans = list(results)
    
    if len(orphans) > 0:
        logger.warning(f"⚠️  Foreign Key 위반 발견: {len(orphans)}개 webtoon_id가 dim_webtoon에 없음")
        for row in orphans[:10]:  # 최대 10개만 출력
            logger.warning(f"  - webtoon_id: {row.webtoon_id}, 레코드 수: {row.orphan_count}")
        return False
    else:
        logger.info("✅ Foreign Key 관계 정상")
        return True


def check_missing_required_fields(client):
    """필수 필드 누락을 확인합니다."""
    logger.info("필수 필드 누락 확인 중...")
    
    # dim_webtoon 필수 필드 확인
    query = f"""
    SELECT 
        COUNT(*) AS missing_count
    FROM `{PROJECT_ID}.{DATASET_ID}.dim_webtoon`
    WHERE webtoon_id IS NULL OR title IS NULL
    """
    
    results = client.query(query).result()
    missing = list(results)[0]
    
    if missing.missing_count > 0:
        logger.warning(f"⚠️  dim_webtoon 필수 필드 누락: {missing.missing_count}개")
        return False
    else:
        logger.info("✅ dim_webtoon 필수 필드 모두 존재")
    
    # fact_weekly_chart 필수 필드 확인
    query = f"""
    SELECT 
        COUNT(*) AS missing_count
    FROM `{PROJECT_ID}.{DATASET_ID}.fact_weekly_chart`
    WHERE chart_date IS NULL OR webtoon_id IS NULL OR rank IS NULL
    """
    
    results = client.query(query).result()
    missing = list(results)[0]
    
    if missing.missing_count > 0:
        logger.warning(f"⚠️  fact_weekly_chart 필수 필드 누락: {missing.missing_count}개")
        return False
    else:
        logger.info("✅ fact_weekly_chart 필수 필드 모두 존재")
    
    return True


def check_data_consistency(client):
    """데이터 일관성을 확인합니다."""
    logger.info("데이터 일관성 확인 중...")
    
    # 최근 4주간 데이터 수집 확인
    query = f"""
    SELECT 
        chart_date,
        COUNT(DISTINCT webtoon_id) AS webtoon_count,
        COUNT(*) AS total_records
    FROM `{PROJECT_ID}.{DATASET_ID}.fact_weekly_chart`
    WHERE chart_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 28 DAY)
    GROUP BY chart_date
    ORDER BY chart_date DESC
    """
    
    results = client.query(query).result()
    weekly_data = list(results)
    
    if len(weekly_data) == 0:
        logger.warning("⚠️  최근 4주간 데이터가 없습니다.")
        return False
    
    logger.info(f"최근 {len(weekly_data)}주간 데이터 수집 현황:")
    for row in weekly_data:
        logger.info(f"  - {row.chart_date}: {row.webtoon_count}개 웹툰, {row.total_records}개 레코드")
    
    # 평균 웹툰 수 확인 (일관성 체크)
    avg_webtoon_count = sum(row.webtoon_count for row in weekly_data) / len(weekly_data)
    logger.info(f"평균 웹툰 수: {avg_webtoon_count:.0f}개")
    
    return True


def generate_validation_report(client):
    """검증 리포트를 생성합니다."""
    logger.info("\n" + "="*60)
    logger.info("데이터 품질 검증 리포트")
    logger.info("="*60)
    
    all_passed = True
    
    # 1. 중복 레코드 확인
    if not check_dim_webtoon_duplicates(client):
        all_passed = False
    
    if not check_fact_weekly_chart_duplicates(client):
        all_passed = False
    
    # 2. Foreign Key 관계 확인
    if not check_foreign_key_relationships(client):
        all_passed = False
    
    # 3. 필수 필드 누락 확인
    if not check_missing_required_fields(client):
        all_passed = False
    
    # 4. 데이터 일관성 확인
    if not check_data_consistency(client):
        all_passed = False
    
    logger.info("\n" + "="*60)
    if all_passed:
        logger.info("✅ 모든 검증 통과")
    else:
        logger.warning("⚠️  일부 검증 실패 - 위의 경고를 확인하세요")
    logger.info("="*60)
    
    return all_passed


if __name__ == "__main__":
    setup_logging(level=logging.INFO)
    
    try:
        client = get_bigquery_client()
        success = generate_validation_report(client)
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ 검증 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

