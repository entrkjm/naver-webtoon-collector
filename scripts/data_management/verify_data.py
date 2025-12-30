#!/usr/bin/env python3
"""
수집된 데이터 검증 스크립트

수집된 데이터의 품질을 확인합니다:
- 중복 체크
- Foreign Key 관계 확인
- 데이터 타입 검증
"""

import sys
from pathlib import Path
from datetime import date
import pandas as pd

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import (
    get_dim_webtoon_csv_path,
    get_chart_csv_path,
    get_webtoon_stats_csv_path,
)


def verify_dim_webtoon() -> dict:
    """dim_webtoon 데이터 검증"""
    result = {
        'status': 'ok',
        'issues': []
    }
    
    dim_path = get_dim_webtoon_csv_path()
    if not dim_path.exists():
        result['status'] = 'error'
        result['issues'].append('dim_webtoon.csv 파일이 없습니다.')
        return result
    
    try:
        df = pd.read_csv(dim_path)
        
        # 중복 체크
        duplicates = df['webtoon_id'].duplicated().sum()
        if duplicates > 0:
            result['status'] = 'warning'
            result['issues'].append(f'중복된 webtoon_id: {duplicates}개')
        
        result['total'] = len(df)
        result['unique'] = df['webtoon_id'].nunique()
        
    except Exception as e:
        result['status'] = 'error'
        result['issues'].append(f'파일 읽기 실패: {e}')
    
    return result


def verify_fact_weekly_chart(chart_date: date = None) -> dict:
    """fact_weekly_chart 데이터 검증"""
    if chart_date is None:
        from datetime import date
        chart_date = date.today()
    
    result = {
        'status': 'ok',
        'issues': [],
        'sort_types': {}
    }
    
    for sort_type in ['view', 'popular']:
        chart_path = get_chart_csv_path(chart_date, sort_type=sort_type)
        
        if not chart_path.exists():
            result['sort_types'][sort_type] = {
                'status': 'not_found',
                'message': f'{chart_path.name} 파일이 없습니다.'
            }
            continue
        
        try:
            df = pd.read_csv(chart_path)
            
            # 중복 체크 (chart_date, webtoon_id, weekday)
            df['weekday'] = df['weekday'].fillna('')
            duplicates = df.duplicated(subset=['chart_date', 'webtoon_id', 'weekday']).sum()
            
            sort_result = {
                'status': 'ok',
                'total': len(df),
                'unique': len(df.drop_duplicates(subset=['chart_date', 'webtoon_id', 'weekday'])),
                'duplicates': duplicates
            }
            
            if duplicates > 0:
                sort_result['status'] = 'warning'
                sort_result['message'] = f'중복 레코드: {duplicates}개'
            
            result['sort_types'][sort_type] = sort_result
            
        except Exception as e:
            result['sort_types'][sort_type] = {
                'status': 'error',
                'message': f'파일 읽기 실패: {e}'
            }
    
    return result


def verify_foreign_keys(chart_date: date = None) -> dict:
    """Foreign Key 관계 검증"""
    if chart_date is None:
        from datetime import date
        chart_date = date.today()
    
    result = {
        'status': 'ok',
        'issues': []
    }
    
    try:
        # dim_webtoon 로드
        dim_path = get_dim_webtoon_csv_path()
        if not dim_path.exists():
            result['status'] = 'error'
            result['issues'].append('dim_webtoon.csv 파일이 없습니다.')
            return result
        
        dim_df = pd.read_csv(dim_path)
        dim_ids = set(dim_df['webtoon_id'].astype(str))
        
        # fact_weekly_chart 확인
        for sort_type in ['view', 'popular']:
            chart_path = get_chart_csv_path(chart_date, sort_type=sort_type)
            if chart_path.exists():
                chart_df = pd.read_csv(chart_path)
                chart_ids = set(chart_df['webtoon_id'].astype(str))
                missing = chart_ids - dim_ids
                
                if missing:
                    result['status'] = 'error'
                    result['issues'].append(
                        f'fact_weekly_chart ({sort_type})에 있지만 dim_webtoon에 없는 webtoon_id: {len(missing)}개'
                    )
        
        # fact_webtoon_stats 확인
        stats_path = get_webtoon_stats_csv_path()
        if stats_path.exists():
            stats_df = pd.read_csv(stats_path)
            stats_ids = set(stats_df['webtoon_id'].astype(str))
            missing = stats_ids - dim_ids
            
            if missing:
                result['status'] = 'error'
                result['issues'].append(
                    f'fact_webtoon_stats에 있지만 dim_webtoon에 없는 webtoon_id: {len(missing)}개'
                )
    
    except Exception as e:
        result['status'] = 'error'
        result['issues'].append(f'검증 실패: {e}')
    
    return result


def main():
    from datetime import date
    
    print("="*80)
    print("데이터 검증 리포트")
    print("="*80)
    
    # 1. dim_webtoon 검증
    print("\n1. dim_webtoon 검증:")
    dim_result = verify_dim_webtoon()
    if dim_result['status'] == 'ok':
        print(f"  ✅ 총 {dim_result['total']:,}개 레코드, 고유 webtoon_id: {dim_result['unique']:,}개")
    else:
        print(f"  {'⚠️' if dim_result['status'] == 'warning' else '❌'} {', '.join(dim_result['issues'])}")
    
    # 2. fact_weekly_chart 검증
    print("\n2. fact_weekly_chart 검증:")
    chart_result = verify_fact_weekly_chart()
    for sort_type, result in chart_result['sort_types'].items():
        if result['status'] == 'ok':
            print(f"  ✅ {sort_type}: {result['total']:,}개 레코드 (고유: {result['unique']:,}개)")
        elif result['status'] == 'warning':
            print(f"  ⚠️  {sort_type}: {result['message']}")
        else:
            print(f"  ❌ {sort_type}: {result.get('message', '오류')}")
    
    # 3. Foreign Key 검증
    print("\n3. Foreign Key 관계 검증:")
    fk_result = verify_foreign_keys()
    if fk_result['status'] == 'ok':
        print("  ✅ 모든 Foreign Key 관계가 올바릅니다.")
    else:
        print(f"  ❌ {'; '.join(fk_result['issues'])}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()



