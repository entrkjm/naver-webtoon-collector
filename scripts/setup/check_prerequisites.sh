#!/bin/bash
# GCP 배포 준비사항 확인 스크립트

echo "=== GCP 배포 준비사항 확인 ==="
echo ""

# 1. gcloud CLI 확인
echo "1. gcloud CLI 확인..."
if command -v gcloud &> /dev/null; then
    echo "   ✅ gcloud CLI 설치됨"
    gcloud --version | head -1
else
    echo "   ❌ gcloud CLI가 설치되어 있지 않습니다."
    echo "   설치 방법: brew install --cask google-cloud-sdk"
fi
echo ""

# 2. gcloud 인증 확인
echo "2. gcloud 인증 확인..."
if gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | grep -q .; then
    echo "   ✅ 인증됨"
    gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1
else
    echo "   ❌ 인증이 필요합니다."
    echo "   실행: gcloud auth login"
fi
echo ""

# 3. 프로젝트 설정 확인
echo "3. 프로젝트 설정 확인..."
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -n "$PROJECT_ID" ]; then
    echo "   ✅ 프로젝트 설정됨: $PROJECT_ID"
else
    echo "   ❌ 프로젝트가 설정되지 않았습니다."
    echo "   실행: gcloud config set project YOUR_PROJECT_ID"
fi
echo ""

# 4. GitHub 저장소 확인
echo "4. GitHub 저장소 확인..."
if git remote -v &> /dev/null && [ -n "$(git remote -v)" ]; then
    echo "   ✅ 원격 저장소 연결됨"
    git remote -v | head -2
else
    echo "   ⚠️  원격 저장소가 연결되지 않았습니다."
    echo "   (선택사항이지만 CI/CD를 위해 권장됩니다)"
fi
echo ""

# 5. API 활성화 확인
if [ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "" ]; then
    echo "5. 필요한 API 활성화 확인..."
    APIS=(
        "cloudfunctions.googleapis.com"
        "cloudscheduler.googleapis.com"
        "bigquery.googleapis.com"
        "storage.googleapis.com"
        "cloudbuild.googleapis.com"
    )
    
    for API in "${APIS[@]}"; do
        if gcloud services list --enabled --filter="name:$API" --format="value(name)" --project=$PROJECT_ID 2>/dev/null | grep -q "$API"; then
            echo "   ✅ $API 활성화됨"
        else
            echo "   ❌ $API 비활성화됨"
        fi
    done
else
    echo "5. API 활성화 확인 (프로젝트 설정 필요)"
fi
echo ""

echo "=== 확인 완료 ==="
echo ""
echo "다음 단계:"
echo "1. gcloud CLI 설치: brew install --cask google-cloud-sdk"
echo "2. 인증: gcloud auth login"
echo "3. 프로젝트 설정: gcloud config set project YOUR_PROJECT_ID"
echo "4. API 활성화: scripts/setup_gcp_prerequisites.md 참고"

