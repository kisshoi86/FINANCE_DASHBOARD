# Finance Dashboard GitHub Deploy Script
# UTF-8 Encoding

# 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=== Finance Dashboard GitHub Deploy Script ===" -ForegroundColor Cyan
Write-Host ""

# 현재 디렉토리 확인
$currentDir = Get-Location
Write-Host "Current directory: $currentDir" -ForegroundColor Yellow

# Git 저장소 확인
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    if ($LASTEXITCODE -eq 0) {
        git branch -M main
        Write-Host "[OK] Git repository initialized" -ForegroundColor Green
    }
} else {
    Write-Host "[OK] Git repository already exists" -ForegroundColor Green
}

# 원격 저장소 확인
try {
    $remoteUrl = git remote get-url origin 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Remote repository: $remoteUrl" -ForegroundColor Green
    } else {
        throw "No remote"
    }
} catch {
    Write-Host ""
    Write-Host "Remote repository is not configured." -ForegroundColor Yellow
    Write-Host "Enter GitHub repository URL (e.g., https://github.com/kisshoi86/FINANCE_DASHBOARD.git):" -ForegroundColor Yellow
    $repoUrl = Read-Host
    if ($repoUrl) {
        git remote add origin $repoUrl
        Write-Host "[OK] Remote repository added" -ForegroundColor Green
    } else {
        Write-Host "Repository URL not entered. Please set it manually later:" -ForegroundColor Red
        Write-Host "  git remote add origin https://github.com/kisshoi86/FINANCE_DASHBOARD.git" -ForegroundColor Yellow
    }
}

# 변경사항 확인
Write-Host ""
Write-Host "Checking changes..." -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "Staging files..." -ForegroundColor Yellow
git add .

# 커밋 메시지 입력
Write-Host ""
Write-Host "Enter commit message (press Enter for default):" -ForegroundColor Yellow
$commitMsg = Read-Host
if (-not $commitMsg) {
    $commitMsg = "Update: Finance Dashboard deployment"
}

Write-Host "Committing..." -ForegroundColor Yellow
git commit -m $commitMsg

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Commit completed" -ForegroundColor Green
} else {
    Write-Host "No changes to commit or an error occurred." -ForegroundColor Yellow
}

# 푸시 여부 확인
Write-Host ""
Write-Host "Push to remote repository? (Y/N):" -ForegroundColor Yellow
$pushConfirm = Read-Host

if ($pushConfirm -eq "Y" -or $pushConfirm -eq "y") {
    Write-Host "Pushing..." -ForegroundColor Yellow
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Push completed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Go to Streamlit Cloud: https://share.streamlit.io" -ForegroundColor White
        Write-Host "2. Connect GitHub repository" -ForegroundColor White
        Write-Host "3. Set Main file: dashboard.py" -ForegroundColor White
        Write-Host "4. Configure environment variables in Secrets" -ForegroundColor White
        Write-Host "5. Deploy!" -ForegroundColor White
    } else {
        Write-Host "Error occurred during push." -ForegroundColor Red
        Write-Host "GitHub authentication may be required." -ForegroundColor Yellow
    }
} else {
    Write-Host "Skipping push." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To push manually later:" -ForegroundColor Cyan
    Write-Host "  git push -u origin main" -ForegroundColor White
}

Write-Host ""
Write-Host "Script execution completed!" -ForegroundColor Green
