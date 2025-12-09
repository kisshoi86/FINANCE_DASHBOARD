# Node.js 버전 확인 및 재설치 가이드

## 현재 시스템 상태

### 확인된 버전 정보
- **Node.js 버전**: v24.11.1
- **npm 버전**: 11.6.2
- **설치 경로**: `C:\Program Files\nodejs`

## Node.js 버전 확인 방법

### 1. 기본 명령어로 확인

```powershell
# Node.js 버전 확인
node --version
# 또는
node -v

# npm 버전 확인
npm --version
# 또는
npm -v

# 설치 경로 확인
where.exe node
where.exe npm
```

### 2. 상세 정보 확인

```powershell
# Node.js 상세 정보
node -p "process.versions"

# npm 설정 확인
npm config list

# npm 전역 패키지 확인
npm list -g --depth=0
```

## Node.js 재설치 방법

### 방법 1: 공식 웹사이트에서 재설치 (권장)

#### 1단계: 현재 Node.js 제거

**Windows 설정을 통한 제거:**
1. `Windows 키 + I`를 눌러 설정 열기
2. "앱" → "앱 및 기능" 선택
3. "Node.js" 검색
4. "Node.js" 선택 후 "제거" 클릭

**또는 PowerShell을 통한 제거:**
```powershell
# 관리자 권한으로 PowerShell 실행 필요
# 제거 프로그램 확인
Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like "*Node.js*"} | Select-Object Name, Version

# 수동으로 제거 프로그램 실행
# 제어판 → 프로그램 제거에서 Node.js 제거
```

#### 2단계: 수동 정리 (선택사항)

```powershell
# 관리자 권한 PowerShell에서 실행
# Node.js 설치 폴더 삭제
Remove-Item -Recurse -Force "C:\Program Files\nodejs" -ErrorAction SilentlyContinue

# npm 캐시 폴더 삭제
Remove-Item -Recurse -Force "$env:APPDATA\npm" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\npm-cache" -ErrorAction SilentlyContinue

# 환경 변수 확인 (수동으로 제거 필요할 수 있음)
[Environment]::GetEnvironmentVariable("Path", "Machine") -split ";" | Where-Object {$_ -like "*nodejs*"}
```

#### 3단계: 새 버전 다운로드 및 설치

1. **공식 웹사이트 방문**
   - https://nodejs.org/ 접속
   - 또는 https://nodejs.org/ko/ (한국어)

2. **버전 선택**
   - **LTS (Long Term Support) 버전 권장**: 안정적이고 장기 지원
   - **Current 버전**: 최신 기능 포함 (현재 v24.11.1이 최신)

3. **다운로드 및 설치**
   - Windows Installer (.msi) 다운로드
   - 다운로드한 파일 실행
   - 설치 마법사 따라하기
   - **중요**: "Add to PATH" 옵션 체크 확인

#### 4단계: 설치 확인

```powershell
# 새 PowerShell 창 열기 (환경 변수 새로고침)
node --version
npm --version

# 설치 경로 확인
where.exe node
```

### 방법 2: Node Version Manager (NVM) 사용 (고급)

NVM을 사용하면 여러 Node.js 버전을 관리할 수 있습니다.

#### 1단계: NVM for Windows 설치

1. **다운로드**
   - https://github.com/coreybutler/nvm-windows/releases
   - `nvm-setup.exe` 다운로드

2. **설치**
   - 다운로드한 파일 실행
   - 설치 마법사 따라하기

#### 2단계: NVM 사용

```powershell
# 관리자 권한 PowerShell에서 실행

# 사용 가능한 Node.js 버전 목록 확인
nvm list available

# 특정 버전 설치 (예: LTS 버전)
nvm install 20.18.0

# 설치된 버전 목록 확인
nvm list

# 특정 버전 사용
nvm use 20.18.0

# 현재 사용 중인 버전 확인
node --version
```

### 방법 3: Chocolatey를 통한 설치 (패키지 관리자)

Chocolatey가 설치되어 있는 경우:

```powershell
# 관리자 권한 PowerShell에서 실행

# Chocolatey 설치 확인
choco --version

# Node.js 제거 (이미 설치된 경우)
choco uninstall nodejs

# Node.js 재설치
choco install nodejs-lts

# 또는 최신 버전
choco install nodejs
```

## 설치 후 확인 및 설정

### 1. 기본 확인

```powershell
# 버전 확인
node --version
npm --version

# 전역 npm 패키지 확인
npm list -g --depth=0
```

### 2. npm 설정 최적화

```powershell
# npm 레지스트리 확인
npm config get registry

# npm 캐시 경로 확인
npm config get cache

# npm 로그 레벨 설정
npm config set loglevel warn

# npm 업데이트 (npm 자체 업데이트)
npm install -g npm@latest
```

### 3. 프로젝트 의존성 재설치

```powershell
# 프로젝트 디렉토리로 이동
cd "C:\Users\AC1160\OneDrive - F&F\바탕 화면\finance_dashboard\moodtracker"

# npm 캐시 정리
npm cache clean --force

# node_modules 및 package-lock.json 삭제
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item package-lock.json -ErrorAction SilentlyContinue

# 의존성 재설치
npm install

# 빌드 테스트
npm run build
```

## 문제 해결

### 문제 1: "node is not recognized" 오류

**원인**: PATH 환경 변수에 Node.js 경로가 없음

**해결 방법**:
```powershell
# 환경 변수 확인
$env:Path -split ";" | Where-Object {$_ -like "*nodejs*"}

# 수동으로 PATH에 추가 (관리자 권한 필요)
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "Machine") + ";C:\Program Files\nodejs",
    "Machine"
)

# 새 PowerShell 창 열기
```

### 문제 2: 권한 오류

**해결 방법**:
- PowerShell을 **관리자 권한**으로 실행
- 또는 npm 전역 설치 시 `--global` 대신 사용자 디렉토리에 설치

### 문제 3: 이전 버전 캐시 문제

**해결 방법**:
```powershell
# npm 캐시 완전 정리
npm cache clean --force

# 또는 캐시 폴더 직접 삭제
Remove-Item -Recurse -Force "$env:APPDATA\npm-cache" -ErrorAction SilentlyContinue
```

## 권장 사항

1. **LTS 버전 사용 권장**
   - 프로덕션 환경에서는 LTS 버전 사용
   - 현재 LTS: v20.x.x

2. **정기적인 업데이트**
   - 보안 패치 및 버그 수정을 위해 정기적으로 업데이트
   - `npm install -g npm@latest`로 npm 업데이트

3. **버전 관리**
   - 프로젝트별로 필요한 Node.js 버전 명시 (`.nvmrc` 파일 사용)
   - 팀 프로젝트에서는 동일한 버전 사용 권장

## 추가 리소스

- **Node.js 공식 사이트**: https://nodejs.org/
- **npm 공식 사이트**: https://www.npmjs.com/
- **NVM for Windows**: https://github.com/coreybutler/nvm-windows
- **Node.js 릴리스 노트**: https://nodejs.org/en/blog/release/

