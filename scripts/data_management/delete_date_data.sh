#!/bin/bash
# 특정 날짜의 데이터를 삭제하는 스크립트

set -e

# 날짜 파라미터 확인
DATE=${1:-$(date +%Y-%m-%d)}

if [ -z "$DATE" ]; then
    echo "❌ 날짜를 지정해주세요."
    echo "사용법: $0 YYYY-MM-DD"
    exit 1
fi

PROJECT_ID="naver-webtoon-collector"
DATASET_ID="naver_webtoon"

echo "=== ${DATE} 날짜 데이터 삭제 ==="
echo ""

# BigQuery에서 해당 날짜 데이터 삭제
echo "1. BigQuery 데이터 삭제 중..."
echo "   - fact_weekly_chart (chart_date = ${DATE})"
bq query --use_legacy_sql=false --quiet --format=none "
DELETE FROM \`${PROJECT_ID}.${DATASET_ID}.fact_weekly_chart\`
WHERE chart_date = '${DATE}'
" 2>&1 | grep -v "Waiting on" || true

echo "   ✅ BigQuery 데이터 삭제 완료"
echo ""

# GCS에서 해당 날짜 데이터 삭제
echo "2. GCS 데이터 삭제 중..."
BUCKET_NAME="naver-webtoon-raw"
GCS_PATH="gs://${BUCKET_NAME}/raw_html/${DATE}/"

echo "   - GCS 경로: ${GCS_PATH}"
gsutil -m rm -r "${GCS_PATH}" 2>&1 | grep -v "Removing" || echo "   (해당 경로에 데이터가 없거나 이미 삭제됨)"

echo "   ✅ GCS 데이터 삭제 완료"
echo ""

echo "✅ ${DATE} 날짜 데이터 삭제 완료!"
echo ""
echo "다음 명령어로 파이프라인을 실행하세요:"
echo "  curl -X POST \"https://pipeline-function-l3loqwy2ea-du.a.run.app\" \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"date\": \"${DATE}\", \"sort_types\": [\"popular\", \"view\"]}'"

