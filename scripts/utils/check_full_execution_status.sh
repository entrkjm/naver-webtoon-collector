#!/bin/bash
# 전체 실행 상태 확인 스크립트

echo "=== 전체 실행 상태 확인 ==="
echo ""

# 최근 로그 확인
echo "1. 최근 실행 로그:"
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=pipeline-function" \
  --limit=50 \
  --format="value(timestamp,textPayload)" \
  --order=desc 2>&1 | grep -E "(시작|완료|진행|수집|업로드|error|ERROR|실패|성공|배치)" | head -20

echo ""
echo "2. BigQuery 데이터 확인:"
bq query --use_legacy_sql=false --format=csv "
SELECT 
  chart_date,
  COUNT(*) AS record_count,
  MAX(collected_at) AS last_collected
FROM \`naver-webtoon-collector.naver_webtoon.fact_weekly_chart\`
WHERE chart_date = '2025-12-28'
GROUP BY chart_date
" 2>&1 | tail -3

echo ""
echo "3. dim_webtoon 업데이트 확인:"
bq query --use_legacy_sql=false --format=csv "
SELECT 
  COUNT(*) AS total_records,
  COUNTIF(genre IS NOT NULL) AS genre_count,
  COUNTIF(ARRAY_LENGTH(tags) > 0) AS tags_count,
  MAX(updated_at) AS last_updated
FROM \`naver-webtoon-collector.naver_webtoon.dim_webtoon\`
" 2>&1 | tail -2

echo ""
echo "진행 상황을 계속 확인하려면:"
echo "  watch -n 10 ./scripts/check_full_execution_status.sh"

