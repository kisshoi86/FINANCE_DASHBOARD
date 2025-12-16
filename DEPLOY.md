# Finance Dashboard 배포 가이드

## 🚀 Streamlit Cloud 배포 (권장)

Streamlit Cloud를 사용하면 무료로 대시보드를 배포할 수 있습니다.

### 1단계: GitHub 저장소 준비

#### 1.1 Git 저장소 초기화 (아직 안 했다면)

```powershell
# finance_dashboard 폴더에서 실행
git init
git branch -M main
```

#### 1.2 GitHub 저장소 생성

1. https://github.com 접속
2. 로그인 (kisshoi86 계정)
3. 우측 상단 `+` 버튼 > "New repository" 클릭
4. 저장소 설정:
   - **Repository name**: `FINANCE_DASHBOARD`
   - **Description**: "F&F 재무 실적 대시보드"
   - **Visibility**: Public 또는 Private 선택
   - ❌ Add a README file 체크하지 않기
   - ❌ Add .gitignore 체크하지 않기
   - ❌ Choose a license 체크하지 않기
5. "Create repository" 클릭

#### 1.3 로컬 코드를 GitHub에 푸시

```powershell
# 원격 저장소 추가
git remote add origin https://github.com/kisshoi86/FINANCE_DASHBOARD.git

# 파일 추가
git add .

# 커밋
git commit -m "Initial commit: Finance Dashboard"

# 푸시
git push -u origin main
```

### 2단계: Streamlit Cloud 배포

#### 2.1 Streamlit Cloud 접속

1. https://share.streamlit.io 접속
2. GitHub 계정으로 로그인 (kisshoi86 계정)

#### 2.2 새 앱 배포

1. "New app" 버튼 클릭
2. **Repository**: `kisshoi86/FINANCE_DASHBOARD` 선택
3. **Branch**: `main` 선택
4. **Main file path**: `dashboard.py` 입력
5. **App URL** (선택사항): 원하는 URL 입력

#### 2.3 환경 변수 설정

"Advanced settings" 또는 "Secrets" 섹션에서 다음 환경 변수 추가:

```
SNOWFLAKE_ACCOUNT=cixxjbf-wp67697
SNOWFLAKE_USER=songahreum
SNOWFLAKE_PASSWORD=Fnfsnowflake2025!
SNOWFLAKE_WAREHOUSE=DEV_WH
SNOWFLAKE_DATABASE=FNF
SNOWFLAKE_SCHEMA=SAP_FNF
SNOWFLAKE_ROLE=PU_SQL_SAP
```

#### 2.4 배포 시작

"Deploy!" 버튼 클릭하면 배포가 시작됩니다.

### 3단계: 배포 확인

- 배포 완료 후 제공되는 URL로 대시보드 접속
- 대시보드가 정상적으로 작동하는지 확인
- 사이드바에서 "Snowflake 연결 테스트" 버튼으로 연결 확인

## 🔄 업데이트 배포

코드를 수정한 후 다시 배포하려면:

```powershell
git add .
git commit -m "Update: 설명"
git push origin main
```

Streamlit Cloud는 자동으로 변경사항을 감지하여 재배포합니다.

## 🛠️ 문제 해결

### 배포 실패 시

1. **의존성 오류**: `requirements.txt`에 모든 패키지가 포함되어 있는지 확인
2. **환경 변수 오류**: Streamlit Cloud의 Secrets에서 환경 변수가 올바르게 설정되었는지 확인
3. **파일 경로 오류**: `dashboard.py`의 경로가 올바른지 확인

### Snowflake 연결 오류

1. 환경 변수가 올바르게 설정되었는지 확인
2. Snowflake 계정의 네트워크 정책에서 Streamlit Cloud IP 허용 여부 확인
3. 대시보드의 사이드바에서 "환경 변수 확인"으로 설정 상태 확인

## 📝 참고사항

- Streamlit Cloud는 무료 플랜에서도 사용 가능합니다
- 환경 변수는 Streamlit Cloud의 Secrets에 안전하게 저장됩니다
- 배포된 앱은 공개 URL로 접근 가능합니다 (Private 저장소여도 앱은 공개)
- 코드를 업데이트하면 자동으로 재배포됩니다

