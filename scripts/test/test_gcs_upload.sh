#!/bin/bash
# GCS 버킷 업로드/다운로드 테스트 스크립트

set -e

BUCKET_NAME="naver-webtoon-raw"
PROJECT_ID="naver-webtoon-collector"

echo "=== GCS 버킷 테스트 ==="
echo "버킷: gs://${BUCKET_NAME}"
echo "프로젝트: ${PROJECT_ID}"
echo ""

# 버킷 존재 확인
echo "1. 버킷 존재 확인..."
if gsutil ls -b "gs://${BUCKET_NAME}" &>/dev/null; then
    echo "✅ 버킷 존재 확인: gs://${BUCKET_NAME}"
else
    echo "❌ 버킷이 존재하지 않습니다: gs://${BUCKET_NAME}"
    exit 1
fi

# 테스트 파일 생성
TEST_FILE="/tmp/gcs_test_$(date +%Y%m%d_%H%M%S).json"
echo "2. 테스트 파일 생성..."
cat > "${TEST_FILE}" <<EOF
{
  "test": "GCS 업로드 테스트",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project": "${PROJECT_ID}"
}
EOF
echo "✅ 테스트 파일 생성: ${TEST_FILE}"

# 업로드 테스트
GCS_PATH="gs://${BUCKET_NAME}/test/upload_test.json"
echo "3. 파일 업로드 테스트..."
gsutil cp "${TEST_FILE}" "${GCS_PATH}"
echo "✅ 파일 업로드 완료: ${GCS_PATH}"

# 다운로드 테스트
DOWNLOAD_FILE="/tmp/gcs_download_test.json"
echo "4. 파일 다운로드 테스트..."
gsutil cp "${GCS_PATH}" "${DOWNLOAD_FILE}"
echo "✅ 파일 다운로드 완료: ${DOWNLOAD_FILE}"

# 내용 비교
echo "5. 파일 내용 검증..."
if diff -q "${TEST_FILE}" "${DOWNLOAD_FILE}" &>/dev/null; then
    echo "✅ 파일 내용 일치 확인"
else
    echo "❌ 파일 내용이 일치하지 않습니다"
    exit 1
fi

# 정리
echo "6. 테스트 파일 정리..."
gsutil rm "${GCS_PATH}"
rm -f "${TEST_FILE}" "${DOWNLOAD_FILE}"
echo "✅ 테스트 파일 정리 완료"

echo ""
echo "✅ 모든 테스트 통과!"

