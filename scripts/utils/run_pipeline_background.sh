#!/bin/bash
# 백그라운드로 파이프라인을 실행하는 스크립트

set -e

# 프로젝트 루트로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 로그 디렉토리 생성
mkdir -p logs

# 파라미터 파싱
DATE_ARG=""
SORT_ARGS=""
HTML_ARG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --date)
            DATE_ARG="--date $2"
            shift 2
            ;;
        --sort)
            # --sort 다음의 모든 인자를 수집
            SORT_ARGS="--sort"
            shift
            while [[ $# -gt 0 ]] && [[ ! "$1" =~ ^-- ]]; do
                SORT_ARGS="$SORT_ARGS $1"
                shift
            done
            ;;
        --html)
            HTML_ARG="--html $2"
            shift 2
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            exit 1
            ;;
    esac
done

# 타임스탬프 생성
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="logs/pipeline_${TIMESTAMP}.log"
PID_FILE="logs/pipeline_${TIMESTAMP}.pid"

# 백그라운드 실행
echo "파이프라인을 백그라운드로 실행합니다..."
echo "로그 파일: $LOG_FILE"
echo "PID 파일: $PID_FILE"

nohup python3 src/run_pipeline.py $DATE_ARG $SORT_ARGS $HTML_ARG > "$LOG_FILE" 2>&1 &
PID=$!

# PID 저장
echo $PID > "$PID_FILE"

echo "✅ 파이프라인 실행 시작 (PID: $PID)"
echo ""
echo "실행 상태 확인:"
echo "  tail -f $LOG_FILE"
echo ""
echo "프로세스 확인:"
echo "  ps -p $PID"
echo ""
echo "실행 중지:"
echo "  kill $PID"

