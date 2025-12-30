#!/bin/bash
# Always Free 범위 초과 여부 확인 스크립트

set -e

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ 프로젝트가 설정되지 않았습니다."
    exit 1
fi

echo "=== Always Free 범위 확인 ==="
echo "프로젝트: $PROJECT_ID"
echo ""

WARNINGS=0

# BigQuery 저장 용량 확인
echo "📊 BigQuery 저장 용량:"
BQ_SIZE=$(bq query --use_legacy_sql=false --format=csv --max_rows=1 "
SELECT ROUND(SUM(size_bytes) / 1024 / 1024 / 1024, 2) AS size_gb
FROM \`${PROJECT_ID}.naver_webtoon.__TABLES__\`
" 2>/dev/null | tail -1 | tr -d ' ' || echo "0")

if [ -n "$BQ_SIZE" ] && [ "$BQ_SIZE" != "size_gb" ]; then
    if (( $(echo "$BQ_SIZE > 10" | bc -l) )); then
        echo "  ❌ 저장 용량 초과: ${BQ_SIZE}GB (한도: 10GB)"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "  ✅ 저장 용량: ${BQ_SIZE}GB / 10GB"
    fi
else
    echo "  ⚠️  BigQuery 데이터셋이 없거나 접근 권한이 없습니다."
fi

echo ""

# GCS 버킷 크기 확인
echo "📦 Cloud Storage 버킷 크기:"
GCS_SIZE=$(gsutil du -s gs://naver-webtoon-raw 2>/dev/null | awk '{print $1}' || echo "0")
GCS_SIZE_GB=$(echo "scale=2; $GCS_SIZE / 1024 / 1024 / 1024" | bc)

if (( $(echo "$GCS_SIZE_GB > 5" | bc -l) )); then
    echo "  ❌ 저장 용량 초과: ${GCS_SIZE_GB}GB (한도: 5GB)"
    WARNINGS=$((WARNINGS + 1))
else
    echo "  ✅ 저장 용량: ${GCS_SIZE_GB}GB / 5GB"
fi

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

if [ "$EXECUTION_COUNT" -gt 2000000 ]; then
    echo "  ❌ 요청 수 초과: $EXECUTION_COUNT (한도: 2,000,000회)"
    WARNINGS=$((WARNINGS + 1))
else
    echo "  ✅ 요청 수: $EXECUTION_COUNT / 2,000,000회"
fi

echo ""

# 결과 요약
if [ $WARNINGS -eq 0 ]; then
    echo "✅ 모든 항목이 Always Free 범위 내에 있습니다."
    exit 0
else
    echo "⚠️  $WARNINGS 개 항목이 Always Free 범위를 초과했습니다."
    echo "   상세 사용량을 확인하고 최적화를 고려하세요."
    exit 1
fi

