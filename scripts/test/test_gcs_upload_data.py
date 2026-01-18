#!/usr/bin/env python3
"""
GCS 업로드 테스트 스크립트

로컬에 저장된 JSON 파일을 GCS에 업로드하는 기능을 테스트합니다.
"""

import sys
from pathlib import Path
from datetime import date

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.upload_gcs import (
    upload_chart_data_to_gcs,
    upload_all_chart_data_for_date,
)
from src.utils import setup_logging, get_raw_html_dir

if __name__ == "__main__":
    setup_logging()
    
    print("=== GCS 업로드 테스트 ===\n")
    
    # 최근 날짜의 JSON 파일 찾기
    raw_dir = get_raw_html_dir()
    date_dirs = sorted([d for d in raw_dir.iterdir() if d.is_dir()], reverse=True)
    
    if not date_dirs:
        print("❌ 업로드할 JSON 파일이 없습니다.")
        print("먼저 파이프라인을 실행하여 데이터를 수집하세요.")
        sys.exit(1)
    
    # 가장 최근 날짜 선택
    latest_date_dir = date_dirs[0]
    date_str = latest_date_dir.name
    
    try:
        chart_date = date.fromisoformat(date_str)
    except ValueError:
        print(f"❌ 날짜 파싱 실패: {date_str}")
        sys.exit(1)
    
    print(f"테스트 날짜: {chart_date}\n")
    
    # 1. 개별 파일 업로드 테스트
    print("1. 개별 차트 데이터 업로드 테스트...")
    for sort_type in ["popular", "view"]:
        json_file = latest_date_dir / f"webtoon_chart_{sort_type}.json"
        if json_file.exists():
            print(f"  - {sort_type} 업로드 중...")
            success = upload_chart_data_to_gcs(chart_date, sort_type=sort_type, dry_run=False)
            if success:
                print(f"  ✅ {sort_type} 업로드 성공\n")
            else:
                print(f"  ❌ {sort_type} 업로드 실패\n")
        else:
            print(f"  ⚠️  {sort_type} JSON 파일이 없습니다: {json_file}\n")
    
    # 2. 전체 업로드 테스트
    print("2. 전체 차트 데이터 업로드 테스트...")
    success = upload_all_chart_data_for_date(chart_date, dry_run=False)
    if success:
        print("✅ 전체 업로드 성공\n")
    else:
        print("❌ 전체 업로드 실패\n")
    
    print("=== 테스트 완료 ===")

