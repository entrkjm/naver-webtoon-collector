# GitHub 저장소 설정 가이드

> **목적**: 로컬 프로젝트를 GitHub에 업로드하고 CI/CD를 설정

---

## 📋 단계별 가이드

### 1단계: Git 사용자 정보 설정 (필요시)

```bash
# 전역 설정 (모든 저장소에 적용)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 또는 이 프로젝트에만 적용
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

---

### 2단계: 초기 커밋

```bash
# 모든 파일 추가
git add .

# 초기 커밋
git commit -m "Initial commit: 네이버 웹툰 주간 차트 수집 파이프라인"
```

---

### 3단계: GitHub 저장소 생성

#### 방법 1: GitHub 웹사이트에서 생성 (권장)

1. **GitHub 접속**: https://github.com
2. **새 저장소 생성**:
   - 우측 상단 **+** 버튼 → **New repository** 클릭
   - **Repository name**: `naver-webtoon-collector` (또는 원하는 이름)
   - **Description**: `네이버 웹툰 주간 차트 수집 파이프라인`
   - **Visibility**: Private 또는 Public 선택
   - **Initialize this repository with**: 체크하지 않음 (이미 로컬에 코드가 있음)
   - **Create repository** 클릭

3. **저장소 URL 확인**: 생성 후 표시되는 URL 복사
   - 예: `https://github.com/your-username/naver-webtoon-collector.git`

#### 방법 2: GitHub CLI 사용 (선택사항)

```bash
# GitHub CLI 설치 확인
gh --version

# 로그인
gh auth login

# 저장소 생성
gh repo create naver-webtoon-collector \
    --private \
    --description "네이버 웹툰 주간 차트 수집 파이프라인" \
    --source=. \
    --remote=origin \
    --push
```

---

### 4단계: 원격 저장소 연결 및 푸시

```bash
# 원격 저장소 추가 (GitHub에서 생성한 URL 사용)
git remote add origin https://github.com/your-username/naver-webtoon-collector.git

# 또는 SSH 사용
git remote add origin git@github.com:your-username/naver-webtoon-collector.git

# 원격 저장소 확인
git remote -v

# main 브랜치로 이름 변경 (필요시)
git branch -M main

# 코드 푸시
git push -u origin main
```

---

### 5단계: GitHub Secrets 설정

저장소가 생성되면 GitHub Secrets를 설정해야 합니다:

1. **GitHub 저장소 페이지 접속**
2. **Settings** → **Secrets and variables** → **Actions** 클릭
3. **New repository secret** 클릭
4. **필수 Secrets 등록**:
   - `GCP_SA_KEY`: GCP 서비스 계정 키 JSON 전체 내용
   - `NOTIFICATION_CHANNEL_EMAIL` (선택): `entrkjm@vaiv.kr,entrkjm@gmail.com`

자세한 내용은 [`github_actions_setup.md`](./github_actions_setup.md) 참고

---

## ✅ 확인 사항

### 저장소 상태 확인

```bash
# 원격 저장소 확인
git remote -v

# 브랜치 확인
git branch -a

# 최근 커밋 확인
git log --oneline -5
```

### GitHub Actions 활성화 확인

1. GitHub 저장소 → **Actions** 탭
2. 워크플로우 파일이 보이는지 확인
3. 첫 번째 푸시 후 자동 실행 여부 확인

---

## 🔧 문제 해결

### 인증 오류

**증상**: `git push` 시 인증 요청

**해결 방법**:
- Personal Access Token 사용 (HTTPS)
- SSH 키 설정 (SSH)
- GitHub CLI 사용

### 푸시 거부

**증상**: `Permission denied` 또는 `403 Forbidden`

**해결 방법**:
1. 저장소 접근 권한 확인
2. 인증 정보 확인
3. Personal Access Token 재생성

---

## 📚 다음 단계

GitHub 저장소 설정이 완료되면:

1. ✅ GitHub Secrets 설정
2. ✅ GitHub Actions 테스트
3. ✅ 자동 배포 확인

자세한 내용은 [`github_actions_setup.md`](./github_actions_setup.md) 참고

