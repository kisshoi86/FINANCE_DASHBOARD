@echo off
chcp 65001 >nul
echo === Finance Dashboard GitHub Push ===
echo.

REM 현재 디렉토리 확인
echo Current directory:
cd
echo.

REM Git 초기화 확인
if not exist ".git" (
    echo Initializing Git repository...
    git init
    git branch -M main
    echo [OK] Git initialized
) else (
    echo [OK] Git repository exists
)

REM 원격 저장소 확인
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo.
    echo No remote repository configured.
    echo Enter GitHub repository URL:
    echo Example: https://github.com/kisshoi86/FINANCE_DASHBOARD.git
    set /p REPO_URL=
    if not "!REPO_URL!"=="" (
        git remote add origin !REPO_URL!
        echo [OK] Remote added
    ) else (
        echo Skipped. Set manually with:
        echo   git remote add origin https://github.com/kisshoi86/FINANCE_DASHBOARD.git
        pause
        exit /b
    )
) else (
    for /f "tokens=*" %%i in ('git remote get-url origin') do set REMOTE_URL=%%i
    echo [OK] Remote: !REMOTE_URL!
)

REM 파일 추가
echo.
echo Staging files...
git add .

REM 커밋
echo.
set /p COMMIT_MSG="Enter commit message (or press Enter for default): "
if "!COMMIT_MSG!"=="" set COMMIT_MSG=Initial commit: Finance Dashboard

echo Committing...
git commit -m "!COMMIT_MSG!"

REM 푸시
echo.
set /p PUSH_CONFIRM="Push to GitHub? (Y/N): "
if /i "!PUSH_CONFIRM!"=="Y" (
    echo Pushing...
    git push -u origin main
    
    if errorlevel 1 (
        echo.
        echo Push failed. You may need to authenticate.
        echo.
    ) else (
        echo.
        echo [OK] Push completed!
        echo.
        echo Next steps:
        echo 1. Go to https://share.streamlit.io
        echo 2. Connect your GitHub repository
        echo 3. Set main file to: dashboard.py
        echo 4. Add environment variables in Secrets
        echo.
    )
) else (
    echo Skipped push. Run manually:
    echo   git push -u origin main
)

echo.
echo Done!
pause

