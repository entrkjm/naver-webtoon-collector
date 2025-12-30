#!/usr/bin/env python3
"""
BigQuery 업로드 테스트 스크립트

로컬 JSONL 파일을 BigQuery에 업로드하는 기능을 테스트합니다.
"""

import sys
from pathlib import Path
from datetime import date

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.upload_bigquery import (
    upload_dim_webtoon,
    upload_fact_weekly_chart,
    upload_fact_webtoon_stats,
)
from src.utils import setup_logging

if __name__ == "__main__":
    setup_logging()
    
    print("=== BigQuery 업로드 테스트 ===\n")
    
    # 1. dim_webtoon 업로드 테스트
    print("1. dim_webtoon 업로드 테스트...")
    success = upload_dim_webtoon(dry_run=False)
    if success:
        print("✅ dim_webtoon 업로드 성공\n")
    else:
        print("❌ dim_webtoon 업로드 실패\n")
        sys.exit(1)
    
    # 2. fact_weekly_chart 업로드 테스트 (최근 날짜)
    print("2. fact_weekly_chart 업로드 테스트...")
    # 최근 JSONL 파일 찾기
    from src.utils import get_processed_dir
    chart_dir = get_processed_dir() / 'fact_weekly_chart'
    if chart_dir.exists():
        jsonl_files = sorted(chart_dir.glob('*.jsonl'), reverse=True)
        if jsonl_files:
            # 파일명에서 날짜 추출 (예: 2025-12-27_popular.jsonl)
            filename = jsonl_files[0].stem
            date_str = filename.split('_')[0]
            try:
                chart_date = date.fromisoformat(date_str)
                sort_type = filename.split('_')[1] if '_' in filename else None
                success = upload_fact_weekly_chart(
                    chart_date=chart_date,
                    sort_type=sort_type,
                    dry_run=False
                )
                if success:
                    print(f"✅ fact_weekly_chart 업로드 성공 ({chart_date})\n")
                else:
                    print(f"❌ fact_weekly_chart 업로드 실패\n")
            except Exception as e:
                print(f"⚠️  날짜 파싱 오류: {e}\n")
        else:
            print("⚠️  fact_weekly_chart JSONL 파일이 없습니다.\n")
    else:
        print("⚠️  fact_weekly_chart 디렉토리가 없습니다.\n")
    
    # 3. fact_webtoon_stats 업로드 테스트
    print("3. fact_webtoon_stats 업로드 테스트...")
    success = upload_fact_webtoon_stats(dry_run=False)
    if success:
        print("✅ fact_webtoon_stats 업로드 성공\n")
    else:
        print("❌ fact_webtoon_stats 업로드 실패\n")
    
    print("=== 테스트 완료 ===")

