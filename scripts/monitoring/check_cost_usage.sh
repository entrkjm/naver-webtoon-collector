#!/bin/bash
# GCP 비용 및 사용량 확인 스크립트

set -e

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ 프로젝트가 설정되지 않았습니다."
    exit 1
fi

echo "=== GCP 비용 및 사용량 확인 ==="
echo "프로젝트: $PROJECT_ID"
echo ""

# BigQuery 저장 용량 확인
echo "📊 BigQuery 저장 용량:"
bq query --use_legacy_sql=false --format=prettyjson "
SELECT 
  dataset_id,
  table_id,
  ROUND(size_bytes / 1024 / 1024, 2) AS size_mb
FROM \`${PROJECT_ID}.naver_webtoon.__TABLES__\`
ORDER BY size_mb DESC
" 2>/dev/null || echo "  ⚠️  BigQuery 데이터셋이 없거나 접근 권한이 없습니다."

echo ""

# GCS 버킷 크기 확인
echo "📦 Cloud Storage 버킷 크기:"
gsutil du -sh gs://naver-webtoon-raw 2>/dev/null || echo "  ⚠️  GCS 버킷이 없거나 접근 권한이 없습니다."

echo ""

# GCS 파일 수 확인
echo "📁 Cloud Storage 파일 수:"
gsutil ls -l gs://naver-webtoon-raw/** 2>/dev/null | wc -l | xargs echo "  파일 수:"

echo ""

# Cloud Functions 실행 횟수 확인 (최근 30일)
echo "⚡ Cloud Functions 실행 횟수 (최근 30일):"
# macOS와 Linux 호환성을 위한 날짜 계산
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    DATE_30_DAYS_AGO=$(date -u -v-30d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-30d +%Y-%m-%dT%H:%M:%SZ)
else
    # Linux
    DATE_30_DAYS_AGO=$(date -u -d '30 days ago' +%Y-%m-%dT%H:%M:%SZ)
fi
EXECUTION_COUNT=$(gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=pipeline_function AND timestamp>=\"${DATE_30_DAYS_AGO}\"" \
  --format="value(timestamp)" \
  --limit=10000 2>/dev/null | wc -l | xargs)
echo "  실행 횟수: $EXECUTION_COUNT"

echo ""

# Always Free 범위 확인
echo "✅ Always Free 범위 확인:"
echo ""
echo "BigQuery:"
echo "  - 저장 한도: 10GB/월"
echo "  - 쿼리 한도: 1TB/월"
echo ""
echo "Cloud Storage:"
echo "  - 저장 한도: 5GB/월"
echo "  - Class A 작업 한도: 5,000회/월"
echo ""
echo "Cloud Functions:"
echo "  - 요청 한도: 200만 회/월"
echo "  - 컴퓨팅 한도: 400,000GB-초/월"
echo ""
echo "Cloud Scheduler:"
echo "  - 작업 한도: 3개 무료"
echo ""

echo "📈 상세 사용량은 Cloud Console에서 확인하세요:"
echo "  https://console.cloud.google.com/billing/usage?project=$PROJECT_ID"

