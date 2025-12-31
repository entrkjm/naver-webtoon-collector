#!/bin/bash
# GitHub Actions 배포 권한 수정 스크립트

set -e

PROJECT_ID="naver-webtoon-collector"
SERVICE_ACCOUNT_EMAIL="webtoon-collector@${PROJECT_ID}.iam.gserviceaccount.com"

echo "=== GitHub Actions 배포 권한 수정 ==="
echo "프로젝트: $PROJECT_ID"
echo "서비스 계정: $SERVICE_ACCOUNT_EMAIL"
echo ""

# 현재 프로젝트 확인
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo "⚠️  현재 프로젝트가 다릅니다: $CURRENT_PROJECT"
    echo "프로젝트를 변경합니다..."
    gcloud config set project "$PROJECT_ID"
fi

echo "1. 서비스 계정이 자신을 사용할 수 있도록 권한 부여..."
gcloud iam service-accounts add-iam-policy-binding "$SERVICE_ACCOUNT_EMAIL" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/iam.serviceAccountUser" \
    --project="$PROJECT_ID" \
    --quiet

echo ""
echo "2. Cloud Build 서비스 계정에 권한 부여..."
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo "   Cloud Build 서비스 계정: $CLOUD_BUILD_SA"

# Cloud Build 서비스 계정에 serviceAccountUser 역할 부여
gcloud iam service-accounts add-iam-policy-binding "$SERVICE_ACCOUNT_EMAIL" \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/iam.serviceAccountUser" \
    --project="$PROJECT_ID" \
    --quiet

# Cloud Build 서비스 계정에 Cloud Functions Developer 역할 부여
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/cloudfunctions.developer" \
    --quiet

# Cloud Build 서비스 계정에 Service Account User 역할 부여 (프로젝트 레벨)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/iam.serviceAccountUser" \
    --quiet

echo ""
echo "✅ 권한 설정 완료!"
echo ""
echo "설정된 권한:"
echo "  - $SERVICE_ACCOUNT_EMAIL → 자신에게 serviceAccountUser 역할"
echo "  - $CLOUD_BUILD_SA → $SERVICE_ACCOUNT_EMAIL에 serviceAccountUser 역할"
echo "  - $CLOUD_BUILD_SA → 프로젝트에 cloudfunctions.developer 역할"
echo "  - $CLOUD_BUILD_SA → 프로젝트에 serviceAccountUser 역할"

