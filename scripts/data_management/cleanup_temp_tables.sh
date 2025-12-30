#!/bin/bash
# BigQuery 임시 테이블 정리 스크립트

set -e

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ 프로젝트가 설정되지 않았습니다."
    exit 1
fi

DATASET_ID="naver_webtoon"

echo "=== BigQuery 임시 테이블 정리 ==="
echo "프로젝트: $PROJECT_ID"
echo "데이터셋: $DATASET_ID"
echo ""

# 임시 테이블 목록 조회
echo "임시 테이블 목록 확인 중..."
TEMP_TABLES=$(bq ls --format=json "${PROJECT_ID}:${DATASET_ID}" | \
  jq -r '.[] | select(.tableReference.tableId | contains("temp")) | .tableReference.tableId' 2>/dev/null || echo "")

if [ -z "$TEMP_TABLES" ]; then
    echo "✅ 임시 테이블이 없습니다."
    exit 0
fi

echo "다음 임시 테이블들이 발견되었습니다:"
echo "$TEMP_TABLES" | while read -r table; do
    echo "  - $table"
done

echo ""
read -p "이 테이블들을 삭제하시겠습니까? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "취소되었습니다."
    exit 0
fi

# 임시 테이블 삭제
echo "임시 테이블 삭제 중..."
echo "$TEMP_TABLES" | while read -r table; do
    echo "  삭제 중: $table"
    bq rm -f -t "${PROJECT_ID}:${DATASET_ID}.${table}" 2>/dev/null || echo "    ⚠️  삭제 실패: $table"
done

echo ""
echo "✅ 임시 테이블 정리 완료!"

