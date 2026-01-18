#!/bin/bash
# Cloud Scheduler 수집 주기를 매일로 변경하는 스크립트

set -e

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ 프로젝트가 설정되지 않았습니다."
    echo "먼저 다음 명령어를 실행하세요:"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

# 현재 작업 이름 확인 (kakao 또는 naver)
CURRENT_JOB=$(gcloud scheduler jobs list --location=asia-northeast3 --format="value(name)" 2>/dev/null | grep -E "(naver|kakao).*weekly.*collection" | head -1)

if [ -z "$CURRENT_JOB" ]; then
    echo "❌ 기존 weekly-collection 작업을 찾을 수 없습니다."
    exit 1
fi

JOB_NAME=$(basename "$CURRENT_JOB")
REGION="asia-northeast3"

# 기존 작업 정보 확인
echo "=== 기존 작업 정보 ==="
gcloud scheduler jobs describe "$JOB_NAME" --location="$REGION" --format="table(name,schedule,timeZone,state)" 2>/dev/null

echo ""
echo "⚠️  주의: 수집 주기를 매일로 변경합니다."
echo "   기존: 주 1회 (매주 월요일)"
echo "   변경: 매일 (매일 자정)"
echo ""
read -p "계속하시겠습니까? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "취소되었습니다."
    exit 1
fi

# 기존 작업 삭제
echo "기존 작업 삭제 중..."
gcloud scheduler jobs delete "$JOB_NAME" --location="$REGION" --quiet 2>/dev/null || true

# Cloud Function URL 가져오기
FUNCTION_URL=$(gcloud scheduler jobs describe "$JOB_NAME" --location="$REGION" --format="value(httpTarget.uri)" 2>/dev/null || echo "https://pipeline-function-vod3sdldea-du.a.run.app")

# 새로운 작업 이름 (daily로 변경)
NEW_JOB_NAME="${JOB_NAME/weekly/daily}"

# 매일 자정 실행으로 변경
echo "새로운 작업 생성 중 (매일 자정)..."
gcloud scheduler jobs create http "$NEW_JOB_NAME" \
    --location="$REGION" \
    --schedule="0 0 * * *" \
    --uri="$FUNCTION_URL" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{"sort_types": ["popular", "view"]}' \
    --time-zone="Asia/Seoul" \
    --description="네이버 웹툰 주간 차트 수집 (매일 자정)" \
    --attempt-deadline=600s

echo ""
echo "✅ Cloud Scheduler 작업 생성 완료!"
echo ""
echo "작업 정보:"
gcloud scheduler jobs describe "$NEW_JOB_NAME" --location="$REGION" --format="table(name,schedule,timeZone,state,nextRunTime)" 2>/dev/null

echo ""
echo "다음 실행 시간:"
gcloud scheduler jobs describe "$NEW_JOB_NAME" --location="$REGION" --format="value(scheduleTime)" 2>/dev/null

echo ""
echo "⚠️  비용 참고:"
echo "   - 기존: 주 1회 = 월 4-5회"
echo "   - 변경: 매일 = 월 30-31회"
echo "   - Cloud Functions 한도: 200만 회/월 (충분함)"
