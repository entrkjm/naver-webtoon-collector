#!/bin/bash
# 모든 기존 데이터 삭제 스크립트
# 
# 주의: 이 스크립트는 fact_weekly_chart 테이블의 모든 데이터를 삭제합니다.
# weekday_rank 컬럼이 없고 요일별 편향이 있는 기존 데이터를 정리하기 위한 스크립트입니다.

set -e

PROJECT_ID="naver-webtoon-collector"
DATASET_ID="naver_webtoon"
BUCKET_NAME="naver-webtoon-raw"

echo "=" * 80
echo "기존 데이터 전체 삭제"
echo "=" * 80
echo ""
echo "⚠️  주의: 이 작업은 되돌릴 수 없습니다!"
echo ""
echo "삭제 대상:"
echo "  - BigQuery: fact_weekly_chart 테이블의 모든 데이터"
echo "  - GCS: raw_html/ 디렉토리의 모든 파일"
echo ""

# 기존 데이터 확인
echo "1. 기존 데이터 확인 중..."
echo "----------------------------------------------------------------------------------"

RECORD_COUNT=$(bq query --use_legacy_sql=false --format=csv --quiet "
SELECT COUNT(*) as cnt
FROM \`${PROJECT_ID}.${DATASET_ID}.fact_weekly_chart\`
" | tail -n +2)

echo "BigQuery 레코드 수: ${RECORD_COUNT}개"

DATE_RANGE=$(bq query --use_legacy_sql=false --format=csv --quiet "
SELECT 
  MIN(chart_date) as min_date,
  MAX(chart_date) as max_date
FROM \`${PROJECT_ID}.${DATASET_ID}.fact_weekly_chart\`
" | tail -n +2)

echo "날짜 범위: ${DATE_RANGE}"
echo ""

# GCS 파일 확인
echo "GCS 파일 확인 중..."
GCS_FILES=$(gsutil ls "gs://${BUCKET_NAME}/raw_html/" 2>/dev/null | wc -l || echo "0")
echo "GCS 파일 수: ${GCS_FILES}개"
echo ""

# 확인 요청
echo "=================================================================================="
read -p "정말로 모든 기존 데이터를 삭제하시겠습니까? (yes 입력): " -r
echo ""

if [[ ! $REPLY == "yes" ]]; then
    echo "취소되었습니다."
    exit 0
fi

# BigQuery 데이터 삭제
echo "2. BigQuery 데이터 삭제 중..."
echo "----------------------------------------------------------------------------------"

bq query --use_legacy_sql=false --quiet --format=none "
DELETE FROM \`${PROJECT_ID}.${DATASET_ID}.fact_weekly_chart\`
WHERE TRUE
" 2>&1 | grep -v "Waiting on" || true

echo "✅ BigQuery 데이터 삭제 완료"
echo ""

# GCS 데이터 삭제
echo "3. GCS 데이터 삭제 중..."
echo "----------------------------------------------------------------------------------"

GCS_PATH="gs://${BUCKET_NAME}/raw_html/"
if gsutil ls "${GCS_PATH}" >/dev/null 2>&1; then
    gsutil -m rm -r "${GCS_PATH}*" 2>&1 | grep -v "Removing" || true
    echo "✅ GCS 데이터 삭제 완료"
else
    echo "GCS에 데이터가 없거나 이미 삭제되었습니다."
fi
echo ""

# 삭제 확인
echo "4. 삭제 확인 중..."
echo "----------------------------------------------------------------------------------"

REMAINING_COUNT=$(bq query --use_legacy_sql=false --format=csv --quiet "
SELECT COUNT(*) as cnt
FROM \`${PROJECT_ID}.${DATASET_ID}.fact_weekly_chart\`
" | tail -n +2)

if [ "${REMAINING_COUNT}" == "0" ]; then
    echo "✅ BigQuery: 모든 데이터 삭제 확인 (남은 레코드: 0개)"
else
    echo "⚠️  BigQuery: ${REMAINING_COUNT}개 레코드가 남아있습니다."
fi

echo ""
echo "=================================================================================="
echo "✅ 기존 데이터 삭제 완료!"
echo "=================================================================================="
echo ""
echo "다음 단계:"
echo "  1. BigQuery 스키마에 weekday_rank 컬럼 추가"
echo "  2. 새로운 수집 시작"
