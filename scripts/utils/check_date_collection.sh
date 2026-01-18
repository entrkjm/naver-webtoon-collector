#!/bin/bash
# 특정 날짜의 데이터 수집 상태 확인 스크립트

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
FUNCTION_NAME="pipeline-function"

echo "=== ${DATE} 데이터 수집 상태 확인 ==="
echo ""

# 1. Cloud Functions 실행 로그 확인
echo "1. Cloud Functions 실행 로그 확인:"
echo "   날짜: ${DATE}"
echo ""

# 해당 날짜의 로그 확인 (UTC 기준으로 하루 범위)
DATE_START="${DATE}T00:00:00Z"
DATE_END="${DATE}T23:59:59Z"

LOG_COUNT=$(gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=${FUNCTION_NAME} AND timestamp>=\"${DATE_START}\" AND timestamp<=\"${DATE_END}\"" \
  --format="value(timestamp)" \
  --limit=1 2>/dev/null | wc -l | xargs)

if [ "$LOG_COUNT" -gt 0 ]; then
    echo "   ✅ Cloud Functions 실행 로그 발견"
    echo ""
    echo "   최근 실행 로그:"
    gcloud logging read \
      "resource.type=cloud_run_revision AND resource.labels.service_name=${FUNCTION_NAME} AND timestamp>=\"${DATE_START}\" AND timestamp<=\"${DATE_END}\"" \
      --limit=5 \
      --format="table(timestamp,severity,textPayload)" \
      --order=desc 2>/dev/null | head -10
else
    echo "   ⚠️  Cloud Functions 실행 로그 없음"
fi

echo ""
echo ""

# 2. BigQuery fact_weekly_chart 데이터 확인
echo "2. BigQuery fact_weekly_chart 데이터 확인:"
echo "   날짜: ${DATE}"
echo ""

CHART_RESULT=$(bq query --use_legacy_sql=false --format=csv --quiet "
SELECT 
  chart_date,
  COUNT(*) AS record_count,
  COUNT(DISTINCT webtoon_id) AS unique_webtoons,
  COUNT(DISTINCT weekday) AS unique_weekdays,
  COUNT(DISTINCT CASE WHEN sort_type = 'popular' THEN 1 END) AS popular_count,
  COUNT(DISTINCT CASE WHEN sort_type = 'view' THEN 1 END) AS view_count,
  MAX(collected_at) AS last_collected
FROM \`${PROJECT_ID}.${DATASET_ID}.fact_weekly_chart\`
WHERE chart_date = '${DATE}'
GROUP BY chart_date
" 2>&1)

if echo "$CHART_RESULT" | grep -q "record_count"; then
    echo "$CHART_RESULT" | tail -n +2 | while IFS=',' read -r date count unique weekdays popular view last_collected; do
        echo "   ✅ 데이터 발견:"
        echo "      - 레코드 수: ${count}"
        echo "      - 고유 웹툰 수: ${unique}"
        echo "      - 고유 요일 수: ${weekdays}"
        echo "      - 마지막 수집 시각: ${last_collected}"
    done
else
    echo "   ❌ 데이터 없음"
fi

echo ""
echo ""

# 3. BigQuery dim_webtoon 업데이트 확인
echo "3. BigQuery dim_webtoon 업데이트 확인:"
echo ""

DIM_RESULT=$(bq query --use_legacy_sql=false --format=csv --quiet "
SELECT 
  COUNT(*) AS total_records,
  COUNTIF(genre IS NOT NULL) AS genre_count,
  COUNTIF(ARRAY_LENGTH(tags) > 0) AS tags_count,
  MAX(updated_at) AS last_updated
FROM \`${PROJECT_ID}.${DATASET_ID}.dim_webtoon\`
" 2>&1)

if echo "$DIM_RESULT" | grep -q "total_records"; then
    echo "$DIM_RESULT" | tail -n +2 | while IFS=',' read -r total genre tags updated; do
        echo "   ✅ dim_webtoon 상태:"
        echo "      - 전체 레코드 수: ${total}"
        echo "      - genre 정보 있는 레코드: ${genre}"
        echo "      - tags 정보 있는 레코드: ${tags}"
        echo "      - 마지막 업데이트: ${updated}"
    done
else
    echo "   ⚠️  dim_webtoon 데이터 확인 실패"
fi

echo ""
echo ""

# 4. BigQuery fact_webtoon_stats 데이터 확인
echo "4. BigQuery fact_webtoon_stats 데이터 확인:"
echo "   수집 날짜: ${DATE}"
echo ""

STATS_RESULT=$(bq query --use_legacy_sql=false --format=csv --quiet "
SELECT 
  COUNT(*) AS total_records,
  COUNT(DISTINCT webtoon_id) AS unique_webtoons,
  COUNTIF(favorite_count IS NOT NULL) AS favorite_count_count,
  COUNTIF(finished IS NOT NULL) AS finished_count,
  COUNTIF(rest IS NOT NULL) AS rest_count,
  COUNTIF(total_episode_count IS NOT NULL) AS episode_count,
  MAX(collected_at) AS last_collected
FROM \`${PROJECT_ID}.${DATASET_ID}.fact_webtoon_stats\`
WHERE DATE(collected_at) = '${DATE}'
" 2>&1)

if echo "$STATS_RESULT" | grep -q "total_records"; then
    echo "$STATS_RESULT" | tail -n +2 | while IFS=',' read -r total unique favorite finished rest episode last_collected; do
        if [ "$total" -gt 0 ]; then
            echo "   ✅ 데이터 발견:"
            echo "      - 레코드 수: ${total}"
            echo "      - 고유 웹툰 수: ${unique}"
            echo "      - favorite_count 있는 레코드: ${favorite}"
            echo "      - finished 정보 있는 레코드: ${finished}"
            echo "      - rest 정보 있는 레코드: ${rest}"
            echo "      - total_episode_count 있는 레코드: ${episode}"
            echo "      - 마지막 수집 시각: ${last_collected}"
        else
            echo "   ⚠️  데이터 없음 (웹툰 상세 정보 수집이 실행되지 않았거나 실패)"
        fi
    done
else
    echo "   ⚠️  fact_webtoon_stats 데이터 확인 실패"
fi

echo ""
echo ""

# 5. GCS 원본 데이터 확인
echo "5. GCS 원본 데이터 확인:"
echo "   날짜: ${DATE}"
echo ""

BUCKET_NAME="naver-webtoon-raw"
GCS_PATH="gs://${BUCKET_NAME}/raw_html/${DATE}/"

GCS_FILES=$(gsutil ls "${GCS_PATH}" 2>/dev/null | wc -l | xargs)

if [ "$GCS_FILES" -gt 0 ]; then
    echo "   ✅ GCS 원본 데이터 발견:"
    echo "      - 경로: ${GCS_PATH}"
    echo "      - 파일 수: ${GCS_FILES}"
    echo ""
    echo "   파일 목록:"
    gsutil ls "${GCS_PATH}" 2>/dev/null | head -10 | sed 's/^/      /'
else
    echo "   ⚠️  GCS 원본 데이터 없음"
fi

echo ""
echo ""

# 6. 요약
echo "=== 요약 ==="
echo ""

# fact_weekly_chart 데이터 확인
CHART_COUNT=$(echo "$CHART_RESULT" | tail -n +2 | cut -d',' -f2 2>/dev/null | head -1 | tr -d ' ' || echo "0")

if [ "$CHART_COUNT" -gt 0 ]; then
    echo "✅ fact_weekly_chart: ${CHART_COUNT}개 레코드 수집됨"
else
    echo "❌ fact_weekly_chart: 데이터 없음"
fi

# fact_webtoon_stats 데이터 확인
STATS_COUNT=$(echo "$STATS_RESULT" | tail -n +2 | cut -d',' -f1 2>/dev/null | head -1 | tr -d ' ' || echo "0")

if [ "$STATS_COUNT" -gt 0 ]; then
    echo "✅ fact_webtoon_stats: ${STATS_COUNT}개 레코드 수집됨"
else
    echo "⚠️  fact_webtoon_stats: 데이터 없음 (웹툰 상세 정보 수집 미실행 또는 실패)"
fi

# GCS 데이터 확인
if [ "$GCS_FILES" -gt 0 ]; then
    echo "✅ GCS 원본 데이터: ${GCS_FILES}개 파일 저장됨"
else
    echo "⚠️  GCS 원본 데이터: 파일 없음"
fi

echo ""
echo "확인 완료!"
