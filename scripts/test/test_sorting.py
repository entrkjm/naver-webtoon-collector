"""
정렬 타입별 수집 테스트 스크립트

브라우저에서 네트워크 요청을 분석한 후,
실제 API 엔드포인트나 URL 파라미터를 테스트합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.extract import extract_webtoon_chart, SORT_POPULAR, SORT_VIEW
from src.utils import setup_logging
from datetime import date

setup_logging()

print("="*60)
print("정렬 타입별 수집 테스트")
print("="*60)

# 테스트할 정렬 타입들
sort_types = [
    (None, "기본값 (인기순)"),
    ("popular", "인기순"),
    ("view", "조회순"),
]

for sort_type, description in sort_types:
    print(f"\n{'='*60}")
    print(f"테스트: {description} (sort_type={sort_type})")
    print('='*60)
    
    try:
        result = extract_webtoon_chart(
            chart_date=date.today(),
            sort_type=sort_type
        )
        
        if result:
            print(f"✅ 성공: {result}")
            
            # 파일 크기 확인
            file_size = result.stat().st_size
            print(f"   파일 크기: {file_size:,} bytes")
            
            # HTML 내용 일부 확인
            content = result.read_text(encoding='utf-8')[:500]
            if 'webtoon' in content.lower() or 'titleId' in content:
                print(f"   ✅ 웹툰 데이터 포함 확인")
            else:
                print(f"   ⚠️ 웹툰 데이터가 보이지 않음")
        else:
            print(f"❌ 실패")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("테스트 완료")
print("="*60)
print("\n다음 단계:")
print("1. 브라우저에서 네트워크 요청 분석")
print("2. 찾은 API 엔드포인트를 src/extract.py의 WEBTOON_API_ENDPOINTS에 추가")
print("3. 또는 URL 파라미터가 작동하는지 확인")

