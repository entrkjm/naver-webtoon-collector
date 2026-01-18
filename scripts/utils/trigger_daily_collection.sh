#!/bin/bash
# 매일 수집 수동 트리거 스크립트
#
# 주 1회 기본 스케줄 외에 필요시 매일 수집을 실행하는 스크립트입니다.
# Cloud Function에 daily_collection=true 파라미터를 전달합니다.

set -e

# 날짜 파라미터 (선택적, 기본값: 오늘)
COLLECTION_DATE=${1:-$(date +%Y-%m-%d)}

# Cloud Function URL (환경 변수 또는 기본값)
FUNCTION_URL=${FUNCTION_URL:-"https://pipeline-function-vod3sdldea-du.a.run.app"}

echo "=================================================================================="
echo "매일 수집 수동 트리거"
echo "=================================================================================="
echo ""
echo "수집 날짜: ${COLLECTION_DATE}"
echo "Cloud Function URL: ${FUNCTION_URL}"
echo ""

# 확인 요청
read -p "매일 수집을 실행하시겠습니까? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "취소되었습니다."
    exit 0
fi

# Cloud Function 호출
echo "Cloud Function 호출 중..."
echo ""

RESPONSE=$(curl -X POST "${FUNCTION_URL}" \
    -H "Content-Type: application/json" \
    -d "{
        \"date\": \"${COLLECTION_DATE}\",
        \"sort_types\": [\"popular\", \"view\"],
        \"daily_collection\": true
    }" \
    -w "\nHTTP_STATUS:%{http_code}" \
    -s)

HTTP_STATUS=$(echo "${RESPONSE}" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "${RESPONSE}" | sed '/HTTP_STATUS/d')

echo "응답 상태: ${HTTP_STATUS}"
echo ""
echo "응답 내용:"
echo "${BODY}" | jq . 2>/dev/null || echo "${BODY}"

if [ "${HTTP_STATUS}" == "200" ]; then
    echo ""
    echo "✅ 매일 수집 트리거 성공!"
else
    echo ""
    echo "❌ 매일 수집 트리거 실패 (HTTP ${HTTP_STATUS})"
    exit 1
fi

echo ""
echo "다음 명령어로 수집 상태를 확인하세요:"
echo "  ./scripts/utils/check_date_collection.sh ${COLLECTION_DATE}"
