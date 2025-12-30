# GCP 배포 준비사항 설정 가이드

> **목표**: GCP 배포를 위한 필수 준비사항 설정

---

## 📋 체크리스트

### 1. GCP 계정 및 프로젝트
- [ ] Google Cloud Platform 계정 생성/확인
- [ ] GCP 프로젝트 생성 또는 기존 프로젝트 확인
- [ ] 결제 계정 연결 (Always Free 사용을 위해 필요)

### 2. gcloud CLI 설치 및 인증
- [ ] gcloud CLI 설치
- [ ] gcloud 인증 설정
- [ ] 프로젝트 설정

### 3. GitHub 저장소
- [ ] GitHub 저장소 생성 또는 확인
- [ ] 로컬 저장소와 연결

---

## 1️⃣ GCP 계정 및 프로젝트 설정

### 1.1 Google Cloud Platform 계정 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. Google 계정으로 로그인
3. 무료 체험 계정 생성 (필요시)

### 1.2 GCP 프로젝트 생성

**옵션 A: 웹 콘솔에서 생성**
1. [GCP 콘솔](https://console.cloud.google.com/) 접속
2. 상단 프로젝트 선택 드롭다운 클릭
3. "새 프로젝트" 클릭
4. 프로젝트 정보 입력:
   - 프로젝트 이름: `네이버 웹툰 수집기` (또는 원하는 이름)
   - 프로젝트 ID: 자동 생성 또는 직접 입력 (예: `naver-webtoon-collector`)
5. "만들기" 클릭

**옵션 B: gcloud CLI로 생성 (CLI 설치 후)**
```bash
gcloud projects create naver-webtoon-collector \
  --name="네이버 웹툰 수집기"
```

### 1.3 결제 계정 연결

⚠️ **중요**: Always Free 티어를 사용하려면 결제 계정이 필요합니다.
- 결제 계정이 없으면 Always Free 티어를 사용할 수 없습니다.
- 하지만 실제로 비용이 발생하지 않도록 Always Free 범위 내에서만 사용합니다.

1. [결제 계정 설정](https://console.cloud.google.com/billing) 접속
2. 결제 계정 생성 또는 기존 계정 연결
3. 프로젝트에 결제 계정 연결

---

## 2️⃣ gcloud CLI 설치 및 인증

### 2.1 gcloud CLI 설치 (macOS)

**방법 1: Homebrew 사용 (권장)**
```bash
# Homebrew가 설치되어 있지 않다면 먼저 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# gcloud CLI 설치
brew install --cask google-cloud-sdk
```

**방법 2: 공식 설치 스크립트**
```bash
# 설치 스크립트 다운로드 및 실행
curl https://sdk.cloud.google.com | bash

# PATH에 추가 (zsh 사용 시)
echo 'export PATH="$HOME/google-cloud-sdk/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**방법 3: 수동 설치**
1. [gcloud CLI 다운로드 페이지](https://cloud.google.com/sdk/docs/install) 접속
2. macOS용 설치 파일 다운로드
3. 설치 파일 실행

### 2.2 gcloud 초기화 및 인증

```bash
# gcloud 초기화
gcloud init

# 또는 단계별로 진행
# 1. 로그인
gcloud auth login

# 2. 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID

# 3. 기본 리전 설정 (서울)
gcloud config set compute/region asia-northeast3

# 4. 기본 영역 설정
gcloud config set compute/zone asia-northeast3-a
```

### 2.3 설치 확인

```bash
# 버전 확인
gcloud --version

# 현재 설정 확인
gcloud config list

# 프로젝트 목록 확인
gcloud projects list
```

---

## 3️⃣ GitHub 저장소 설정

### 3.1 GitHub 저장소 생성

1. [GitHub](https://github.com) 접속 및 로그인
2. 우측 상단 "+" 버튼 클릭 → "New repository"
3. 저장소 정보 입력:
   - Repository name: `naver_webtoon` (또는 원하는 이름)
   - Description: "네이버 웹툰 주간 차트 수집 파이프라인"
   - Public 또는 Private 선택
   - **"Initialize this repository with a README" 체크 해제** (이미 로컬에 파일이 있으므로)
4. "Create repository" 클릭

### 3.2 로컬 저장소와 연결

```bash
cd /Users/jongminkim/Documents/projects/naver_webtoon

# Git 저장소 초기화 (아직 안 했다면)
git init

# .gitignore 확인 (이미 있음)
cat .gitignore

# 원격 저장소 추가
git remote add origin https://github.com/YOUR_USERNAME/naver_webtoon.git

# 또는 SSH 사용 시
# git remote add origin git@github.com:YOUR_USERNAME/naver_webtoon.git

# 현재 상태 확인
git status

# 첫 커밋 (선택사항)
git add .
git commit -m "Initial commit: 로컬 파이프라인 구현 완료"

# 원격 저장소에 푸시
git branch -M main
git push -u origin main
```

---

## 4️⃣ 필요한 API 활성화

gcloud CLI가 설치되고 인증이 완료되면 다음 스크립트를 실행하세요:

```bash
# 프로젝트 ID 설정 (실제 프로젝트 ID로 변경)
export PROJECT_ID="your-project-id"

# 필요한 API 활성화
gcloud services enable cloudfunctions.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudscheduler.googleapis.com --project=$PROJECT_ID
gcloud services enable bigquery.googleapis.com --project=$PROJECT_ID
gcloud services enable storage.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID  # Cloud Functions Gen2용
```

---

## 5️⃣ 서비스 계정 생성

Cloud Functions가 BigQuery와 GCS에 접근할 수 있도록 서비스 계정을 생성합니다:

```bash
# 프로젝트 ID 설정
export PROJECT_ID="your-project-id"

# 서비스 계정 생성
gcloud iam service-accounts create webtoon-collector \
  --display-name="네이버 웹툰 수집기 서비스 계정" \
  --project=$PROJECT_ID

# 서비스 계정 이메일 확인
export SERVICE_ACCOUNT_EMAIL="webtoon-collector@${PROJECT_ID}.iam.gserviceaccount.com"

# 권한 부여
# BigQuery 데이터 편집자
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/bigquery.dataEditor"

# BigQuery 작업 사용자
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/bigquery.jobUser"

# Cloud Storage 객체 관리자
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/storage.objectAdmin"

# Cloud Functions 실행 권한
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/cloudfunctions.invoker"
```

---

## ✅ 준비사항 확인 스크립트

다음 스크립트를 실행하여 준비사항이 모두 완료되었는지 확인하세요:

```bash
#!/bin/bash
# scripts/check_prerequisites.sh

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
if gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "   ✅ 인증됨"
    gcloud auth list --filter=status:ACTIVE --format="value(account)"
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
if git remote -v &> /dev/null; then
    echo "   ✅ 원격 저장소 연결됨"
    git remote -v
else
    echo "   ⚠️  원격 저장소가 연결되지 않았습니다."
    echo "   (선택사항이지만 CI/CD를 위해 권장됩니다)"
fi
echo ""

# 5. API 활성화 확인
if [ -n "$PROJECT_ID" ]; then
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
fi
echo ""

echo "=== 확인 완료 ==="
```

---

## 🚀 다음 단계

준비사항이 모두 완료되면 다음 단계로 진행하세요:

1. **BigQuery 스키마 구축** (`scripts/setup_bigquery.sql` 생성 및 실행)
2. **GCS 버킷 생성**
3. **Cloud Functions 구현**

---

## 📚 참고 링크

- [gcloud CLI 설치 가이드](https://cloud.google.com/sdk/docs/install)
- [GCP 프로젝트 생성](https://console.cloud.google.com/projectcreate)
- [결제 계정 설정](https://console.cloud.google.com/billing)
- [GitHub 저장소 생성](https://github.com/new)

