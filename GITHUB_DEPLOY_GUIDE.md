# GitHub 저장소 생성 및 배포 가이드

## 문제 상황
- 에러: `Repository not found`
- 원인: GitHub에 `FINANCE_DASHBOARD` 저장소가 아직 생성되지 않음

## 해결 방법

### 1단계: GitHub에서 새 저장소 생성

1. **GitHub 웹사이트 접속**
   - https://github.com 접속
   - 로그인 (kisshoi86 계정)

2. **새 저장소 생성**
   - 우측 상단의 `+` 버튼 클릭
   - "New repository" 선택

3. **저장소 설정**
   - **Repository name**: `FINANCE_DASHBOARD`
   - **Description**: (선택사항) "F&F 재무 실적 대시보드"
   - **Visibility**: 
     - Public (공개) 또는 Private (비공개) 선택
   - **중요**: 아래 옵션들은 체크하지 마세요
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license
   - (이미 로컬에 파일이 있으므로)

4. **"Create repository" 버튼 클릭**

### 2단계: 로컬 저장소와 연결

저장소 생성 후, GitHub에서 제공하는 명령어를 사용하거나 아래 명령어를 실행:

```powershell
# 현재 디렉토리 확인
cd "C:\Users\AC1160\OneDrive - F&F\바탕 화면\finance_dashboard"

# 원격 저장소 URL 확인 (이미 설정되어 있어야 함)
git remote -v

# 만약 URL이 다르다면 수정
git remote set-url origin https://github.com/kisshoi86/FINANCE_DASHBOARD.git
```

### 3단계: 파일 커밋 및 푸시

```powershell
# 현재 상태 확인
git status

# 모든 파일 추가
git add .

# 커밋 (처음이면)
git commit -m "Initial commit: Finance Dashboard project"

# 또는 이미 커밋이 있다면
git commit -m "Build test completed and ready for deployment"

# 원격 저장소로 푸시
git push -u origin master

# 또는 main 브랜치를 사용한다면
git push -u origin main
```

### 4단계: 브랜치 이름 확인 및 변경 (필요시)

```powershell
# 현재 브랜치 확인
git branch

# main 브랜치로 변경하려면
git branch -M main
git push -u origin main
```

## 대안: GitHub CLI 사용 (선택사항)

GitHub CLI가 설치되어 있다면:

```powershell
# GitHub CLI로 저장소 생성
gh repo create FINANCE_DASHBOARD --public --source=. --remote=origin --push
```

## 문제 해결

### 문제 1: 인증 오류
```powershell
# GitHub Personal Access Token 필요
# Settings > Developer settings > Personal access tokens > Tokens (classic)
# 생성 후 비밀번호 대신 토큰 사용
```

### 문제 2: 저장소 이름이 이미 존재
- 다른 이름 사용 (예: `finance-dashboard`, `fnf-dashboard`)
- 또는 기존 저장소 삭제 후 재생성

### 문제 3: 권한 오류
- GitHub 계정에 저장소 생성 권한 확인
- Organization이 있다면 권한 확인

## 배포 플랫폼 연결 (Vercel/Netlify)

저장소 생성 후:

1. **Vercel**
   - https://vercel.com 접속
   - "Import Git Repository" 클릭
   - `kisshoi86/FINANCE_DASHBOARD` 선택
   - 배포 설정 후 Deploy

2. **Netlify**
   - https://netlify.com 접속
   - "Add new site" > "Import an existing project"
   - GitHub 연결 후 저장소 선택

## 다음 단계

1. ✅ GitHub 저장소 생성
2. ✅ 로컬 파일 푸시
3. ✅ 배포 플랫폼 연결
4. ✅ 환경 변수 설정 (필요시)
5. ✅ 배포 완료 확인





