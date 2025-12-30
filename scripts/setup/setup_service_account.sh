#!/bin/bash
# GCP 서비스 계정 생성 및 권한 설정 스크립트

set -e

# 프로젝트 ID 확인
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ 프로젝트가 설정되지 않았습니다."
    echo "먼저 다음 명령어를 실행하세요:"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

SERVICE_ACCOUNT_NAME="webtoon-collector"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "=== GCP 서비스 계정 생성 및 권한 설정 ==="
echo "프로젝트: $PROJECT_ID"
echo "서비스 계정: $SERVICE_ACCOUNT_NAME"
echo ""

# 서비스 계정이 이미 존재하는지 확인
if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
    echo "⚠️  서비스 계정이 이미 존재합니다: $SERVICE_ACCOUNT_EMAIL"
    read -p "계속하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    # 서비스 계정 생성
    echo "서비스 계정 생성 중..."
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --display-name="네이버 웹툰 수집기 서비스 계정" \
        --project="$PROJECT_ID"
    echo "✅ 서비스 계정 생성 완료"
fi

echo ""
echo "권한 부여 중..."

# BigQuery 데이터 편집자
echo "  - BigQuery 데이터 편집자 권한 부여..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/bigquery.dataEditor" \
    --quiet

# BigQuery 작업 사용자
echo "  - BigQuery 작업 사용자 권한 부여..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/bigquery.jobUser" \
    --quiet

# Cloud Storage 객체 관리자
echo "  - Cloud Storage 객체 관리자 권한 부여..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/storage.objectAdmin" \
    --quiet

# Cloud Functions 실행 권한
echo "  - Cloud Functions 실행 권한 부여..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/cloudfunctions.invoker" \
    --quiet

# Cloud Functions 개발자 (함수 배포 및 관리용)
echo "  - Cloud Functions 개발자 권한 부여..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/cloudfunctions.developer" \
    --quiet

echo ""
echo "✅ 서비스 계정 설정 완료!"
echo ""
echo "서비스 계정 정보:"
echo "  이메일: $SERVICE_ACCOUNT_EMAIL"
echo "  프로젝트: $PROJECT_ID"
echo ""
echo "부여된 권한:"
echo "  - BigQuery 데이터 편집자"
echo "  - BigQuery 작업 사용자"
echo "  - Cloud Storage 객체 관리자"
echo "  - Cloud Functions 실행 권한"
echo "  - Cloud Functions 개발자"

