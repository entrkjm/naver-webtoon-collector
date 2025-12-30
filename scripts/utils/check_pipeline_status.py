#!/usr/bin/env python3
"""
파이프라인 실행 상태 확인 스크립트

최근 실행된 파이프라인의 로그를 확인하고 완료 여부를 체크합니다.
"""

import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import get_logs_dir


def find_latest_log() -> Path:
    """가장 최근 로그 파일을 찾습니다."""
    logs_dir = get_logs_dir()
    log_files = sorted(logs_dir.glob("pipeline_*.log"), reverse=True)
    
    if not log_files:
        return None
    
    return log_files[0]


def check_pipeline_status(log_file: Path) -> dict:
    """로그 파일을 분석하여 파이프라인 상태를 확인합니다."""
    if not log_file or not log_file.exists():
        return {
            'status': 'not_found',
            'message': '로그 파일을 찾을 수 없습니다.'
        }
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return {
                'status': 'running',
                'message': '로그 파일이 비어있습니다. 실행 중일 수 있습니다.'
            }
        
        # 마지막 몇 줄 확인
        last_lines = lines[-20:] if len(lines) >= 20 else lines
        last_text = ''.join(last_lines)
        
        # 완료 메시지 확인
        if '🎉 모든 정렬 타입 수집 완료!' in last_text:
            return {
                'status': 'completed',
                'message': '✅ 파이프라인 실행 완료',
                'last_lines': last_lines[-5:]
            }
        elif '❌' in last_text or 'ERROR' in last_text or '실패' in last_text:
            return {
                'status': 'error',
                'message': '❌ 파이프라인 실행 중 오류 발생',
                'last_lines': last_lines[-10:]
            }
        else:
            return {
                'status': 'running',
                'message': '⏳ 파이프라인 실행 중...',
                'last_lines': last_lines[-5:]
            }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': f'로그 파일 읽기 실패: {e}'
        }


def main():
    print("="*80)
    print("파이프라인 실행 상태 확인")
    print("="*80)
    
    log_file = find_latest_log()
    
    if not log_file:
        print("\n❌ 로그 파일을 찾을 수 없습니다.")
        print("파이프라인을 먼저 실행하세요.")
        return
    
    print(f"\n📄 로그 파일: {log_file}")
    print(f"📅 수정 시간: {datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    
    status = check_pipeline_status(log_file)
    
    print(f"\n{status['message']}")
    
    if 'last_lines' in status:
        print("\n최근 로그 (마지막 5줄):")
        print("-" * 80)
        for line in status['last_lines']:
            print(line.rstrip())
    
    print("\n" + "="*80)
    print("전체 로그 보기:")
    print(f"  tail -f {log_file}")
    print("="*80)


if __name__ == "__main__":
    main()



