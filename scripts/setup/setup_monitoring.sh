#!/bin/bash
# Cloud Monitoring 및 알림 설정 스크립트

set -e

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ 프로젝트가 설정되지 않았습니다."
    echo "먼저 다음 명령어를 실행하세요:"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

FUNCTION_NAME="pipeline_function"
REGION="asia-northeast3"
NOTIFICATION_CHANNEL_EMAIL="${NOTIFICATION_CHANNEL_EMAIL:-}"

echo "=== Cloud Monitoring 설정 ==="
echo "프로젝트: $PROJECT_ID"
echo "함수명: $FUNCTION_NAME"
echo ""

# Cloud Monitoring API 활성화
echo "Cloud Monitoring API 활성화 중..."
gcloud services enable monitoring.googleapis.com --project="$PROJECT_ID" 2>/dev/null || true

# 알림 채널 생성 (이메일이 제공된 경우)
if [ -n "$NOTIFICATION_CHANNEL_EMAIL" ]; then
    echo "알림 채널 생성 중 (이메일: $NOTIFICATION_CHANNEL_EMAIL)..."
    NOTIFICATION_CHANNEL_ID=$(gcloud alpha monitoring channels create \
        --display-name="Webtoon Pipeline Alerts" \
        --type=email \
        --channel-labels=email_address="$NOTIFICATION_CHANNEL_EMAIL" \
        --format="value(name)" 2>/dev/null || echo "")
    
    if [ -n "$NOTIFICATION_CHANNEL_ID" ]; then
        echo "✅ 알림 채널 생성 완료: $NOTIFICATION_CHANNEL_ID"
    else
        echo "⚠️  알림 채널 생성 실패 (이미 존재할 수 있음)"
    fi
fi

echo ""
echo "✅ Cloud Monitoring 설정 완료!"
echo ""
echo "다음 단계:"
echo "1. Cloud Console에서 모니터링 대시보드 확인:"
echo "   https://console.cloud.google.com/monitoring?project=$PROJECT_ID"
echo ""
echo "2. Cloud Functions 로그 확인:"
echo "   gcloud functions logs read $FUNCTION_NAME --gen2 --region=$REGION --limit=50"
echo ""
echo "3. Cloud Logging에서 로그 확인:"
echo "   https://console.cloud.google.com/logs?project=$PROJECT_ID"
echo ""
echo "4. 알림 정책은 Cloud Console에서 수동으로 설정하세요:"
echo "   - Cloud Functions 에러율 > 0"
echo "   - Cloud Functions 실행 시간 > 3300초 (55분 초과, 타임아웃 3600초 대비)"
echo "   - Cloud Scheduler 작업 실패"

