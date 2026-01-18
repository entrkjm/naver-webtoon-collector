#!/usr/bin/env python3
"""
API 응답의 리스트 순서가 실제 순위와 일치하는지 검증하는 스크립트

실행 방법:
    python3 scripts/verify_api_ranking_order.py
"""

import sys
import json
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.extract import try_api_endpoints, create_session
import requests
import time

def verify_ranking_order(api_data: dict, sort_type: str) -> dict:
    """
    API 응답의 리스트 순서가 실제 순위와 일치하는지 검증
    
    Args:
        api_data: API 응답 데이터
        sort_type: 정렬 타입 ("view" 또는 "popular")
    
    Returns:
        검증 결과 딕셔너리
    """
    results = {
        'sort_type': sort_type,
        'weekdays_verified': {},
        'overall_valid': True
    }
    
    if 'titleListMap' not in api_data:
        results['error'] = "titleListMap을 찾을 수 없습니다."
        return results
    
    title_list_map = api_data.get('titleListMap', {})
    
    for weekday, items in title_list_map.items():
        if not items or len(items) < 2:
            continue
        
        weekday_result = {
            'total_count': len(items),
            'is_valid': True,
            'issues': []
        }
        
        # order=view인 경우: viewCount로 내림차순 정렬되어야 함
        if sort_type == 'view':
            view_counts = [item.get('viewCount', 0) for item in items]
            
            # 내림차순 확인
            is_descending = True
            for i in range(len(view_counts) - 1):
                if view_counts[i] < view_counts[i + 1]:
                    is_descending = False
                    weekday_result['issues'].append(
                        f"인덱스 {i}와 {i+1}에서 조회수 순서 위반: "
                        f"{view_counts[i]:,} < {view_counts[i+1]:,}"
                    )
                    break
            
            weekday_result['is_valid'] = is_descending
            weekday_result['check_type'] = 'viewCount 내림차순'
            weekday_result['first_5_view_counts'] = view_counts[:5]
            
        # order=user (popular)인 경우: starScore나 다른 필드로 정렬
        elif sort_type == 'popular':
            star_scores = [item.get('starScore', 0) for item in items]
            view_counts = [item.get('viewCount', 0) for item in items]
            
            # 별점 내림차순 확인
            is_star_descending = True
            for i in range(len(star_scores) - 1):
                if star_scores[i] < star_scores[i + 1]:
                    is_star_descending = False
                    weekday_result['issues'].append(
                        f"인덱스 {i}와 {i+1}에서 별점 순서 위반: "
                        f"{star_scores[i]} < {star_scores[i+1]}"
                    )
                    break
            
            weekday_result['is_valid'] = is_star_descending
            weekday_result['check_type'] = 'starScore 내림차순'
            weekday_result['first_5_star_scores'] = star_scores[:5]
            weekday_result['first_5_view_counts'] = view_counts[:5]
        
        if not weekday_result['is_valid']:
            results['overall_valid'] = False
        
        results['weekdays_verified'][weekday] = weekday_result
    
    return results


def main():
    print("=" * 80)
    print("API 응답 리스트 순서 검증")
    print("=" * 80)
    print()
    
    # 조회순 검증
    print("1. 조회순 (order=view) 검증 중...")
    print("-" * 80)
    time.sleep(1)
    
    view_data = try_api_endpoints(sort_type='view')
    if view_data:
        view_results = verify_ranking_order(view_data, 'view')
        
        print(f"정렬 타입: {view_results['sort_type']}")
        print(f"전체 유효성: {'✅ 유효' if view_results['overall_valid'] else '❌ 무효'}")
        print()
        
        for weekday, result in view_results['weekdays_verified'].items():
            status = "✅" if result['is_valid'] else "❌"
            print(f"{status} {weekday}: {result['total_count']}개 웹툰")
            print(f"   검증 방식: {result['check_type']}")
            if result['first_5_view_counts']:
                print(f"   처음 5개 조회수: {result['first_5_view_counts']}")
            if result['issues']:
                print(f"   ⚠️ 문제점:")
                for issue in result['issues'][:3]:  # 처음 3개만
                    print(f"      - {issue}")
            print()
    else:
        print("❌ 조회순 API 호출 실패")
        print()
    
    # 인기순 검증
    print("2. 인기순 (order=user) 검증 중...")
    print("-" * 80)
    time.sleep(1)
    
    popular_data = try_api_endpoints(sort_type='popular')
    if popular_data:
        popular_results = verify_ranking_order(popular_data, 'popular')
        
        print(f"정렬 타입: {popular_results['sort_type']}")
        print(f"전체 유효성: {'✅ 유효' if popular_results['overall_valid'] else '❌ 무효'}")
        print()
        
        for weekday, result in popular_results['weekdays_verified'].items():
            status = "✅" if result['is_valid'] else "❌"
            print(f"{status} {weekday}: {result['total_count']}개 웹툰")
            print(f"   검증 방식: {result['check_type']}")
            if result.get('first_5_star_scores'):
                print(f"   처음 5개 별점: {result['first_5_star_scores']}")
            if result.get('first_5_view_counts'):
                print(f"   처음 5개 조회수: {result['first_5_view_counts']}")
            if result['issues']:
                print(f"   ⚠️ 문제점:")
                for issue in result['issues'][:3]:  # 처음 3개만
                    print(f"      - {issue}")
            print()
    else:
        print("❌ 인기순 API 호출 실패")
        print()
    
    # 결론
    print("=" * 80)
    print("결론")
    print("=" * 80)
    
    if view_data and popular_data:
        view_valid = verify_ranking_order(view_data, 'view')['overall_valid']
        popular_valid = verify_ranking_order(popular_data, 'popular')['overall_valid']
        
        if view_valid and popular_valid:
            print("✅ API 응답의 리스트 순서가 실제 순위와 일치합니다.")
            print("   → idx (리스트 인덱스)를 weekday_rank로 사용 가능")
        else:
            print("❌ API 응답의 리스트 순서가 실제 순위와 일치하지 않습니다.")
            print("   → idx를 weekday_rank로 사용하면 안 됨")
            print("   → viewCount나 starScore로 재정렬 필요")
    else:
        print("⚠️ API 호출 실패로 검증 불가")


if __name__ == '__main__':
    main()
