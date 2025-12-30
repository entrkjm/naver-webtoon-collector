#!/bin/bash
# Cloud Scheduler 설정 스크립트

set -e

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ 프로젝트가 설정되지 않았습니다."
    echo "먼저 다음 명령어를 실행하세요:"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

JOB_NAME="naver-webtoon-weekly-collection"
REGION="asia-northeast3"
FUNCTION_URL="https://pipeline-function-l3loqwy2ea-du.a.run.app"

# Cloud Scheduler API 활성화
echo "Cloud Scheduler API 활성화 중..."
gcloud services enable cloudscheduler.googleapis.com --project="$PROJECT_ID" 2>/dev/null || true

# 기존 작업이 있으면 삭제
echo "기존 작업 확인 중..."
if gcloud scheduler jobs describe "$JOB_NAME" --location="$REGION" --project="$PROJECT_ID" 2>/dev/null; then
    echo "기존 작업 삭제 중..."
    gcloud scheduler jobs delete "$JOB_NAME" --location="$REGION" --project="$PROJECT_ID" --quiet
fi

# Cloud Scheduler 작업 생성
# 매주 월요일 오전 9시 (KST) = 매주 월요일 00:00 (UTC)
echo "Cloud Scheduler 작업 생성 중..."
gcloud scheduler jobs create http "$JOB_NAME" \
    --location="$REGION" \
    --schedule="0 0 * * 1" \
    --uri="$FUNCTION_URL" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{"sort_types": ["popular", "view"]}' \
    --time-zone="Asia/Seoul" \
    --description="네이버 웹툰 주간 차트 수집 (매주 월요일 오전 9시)" \
    --attempt-deadline=600s

echo ""
echo "✅ Cloud Scheduler 작업 생성 완료!"
echo ""
echo "작업 정보:"
gcloud scheduler jobs describe "$JOB_NAME" --location="$REGION" --project="$PROJECT_ID" --format="table(name,schedule,timeZone,state)"

echo ""
echo "다음 실행 시간 확인:"
gcloud scheduler jobs describe "$JOB_NAME" --location="$REGION" --project="$PROJECT_ID" --format="value(scheduleTime)"

echo ""
echo "수동 실행 테스트:"
echo "  gcloud scheduler jobs run $JOB_NAME --location=$REGION"

