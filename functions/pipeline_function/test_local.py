#!/usr/bin/env python3
"""
로컬 테스트 스크립트: Cloud Functions를 로컬에서 테스트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from main import main
from flask import Flask, Request

# Flask Request 객체 생성 (테스트용)
app = Flask(__name__)

# 테스트 요청 생성
class TestRequest:
    def get_json(self, silent=True):
        return {
            'date': '2025-12-27',
            'sort_types': ['popular'],
        }

if __name__ == "__main__":
    print("=== Cloud Functions 로컬 테스트 ===\n")
    
    request = TestRequest()
    result, status_code = main(request)
    
    print(f"\n상태 코드: {status_code}")
    print(f"결과: {result}")
    
    if status_code == 200:
        print("\n✅ 테스트 성공!")
    else:
        print("\n❌ 테스트 실패!")

