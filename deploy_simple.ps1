# Finance Dashboard GitHub Deploy Script (Simple Version)
# This script helps deploy the dashboard to GitHub

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=== Finance Dashboard GitHub Deploy ===" -ForegroundColor Cyan
Write-Host ""

# Check if .git exists
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    git branch -M main
    Write-Host "[OK] Git initialized" -ForegroundColor Green
} else {
    Write-Host "[OK] Git repository exists" -ForegroundColor Green
}

# Check remote
$hasRemote = $false
try {
    $null = git remote get-url origin 2>$null
    if ($LASTEXITCODE -eq 0) {
        $hasRemote = $true
        $remoteUrl = git remote get-url origin
        Write-Host "[OK] Remote: $remoteUrl" -ForegroundColor Green
    }
} catch {
    $hasRemote = $false
}

if (-not $hasRemote) {
    Write-Host ""
    Write-Host "No remote repository configured." -ForegroundColor Yellow
    Write-Host "Enter GitHub repository URL:" -ForegroundColor Yellow
    Write-Host "Example: https://github.com/kisshoi86/FINANCE_DASHBOARD.git" -ForegroundColor Gray
    $repoUrl = Read-Host
    if ($repoUrl) {
        git remote add origin $repoUrl
        Write-Host "[OK] Remote added" -ForegroundColor Green
    } else {
        Write-Host "Skipped. Set manually later with:" -ForegroundColor Yellow
        Write-Host "  git remote add origin https://github.com/kisshoi86/FINANCE_DASHBOARD.git" -ForegroundColor White
        exit
    }
}

# Stage and commit
Write-Host ""
Write-Host "Staging files..." -ForegroundColor Yellow
git add .

Write-Host "Enter commit message (or press Enter for default):" -ForegroundColor Yellow
$commitMsg = Read-Host
if (-not $commitMsg) {
    $commitMsg = "Initial commit: Finance Dashboard"
}

Write-Host "Committing..." -ForegroundColor Yellow
git commit -m $commitMsg

if ($LASTEXITCODE -ne 0) {
    Write-Host "No changes to commit" -ForegroundColor Yellow
}

# Push
Write-Host ""
Write-Host "Push to GitHub? (Y/N):" -ForegroundColor Yellow
$pushConfirm = Read-Host

if ($pushConfirm -eq "Y" -or $pushConfirm -eq "y") {
    Write-Host "Pushing..." -ForegroundColor Yellow
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Push completed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next: Deploy to Streamlit Cloud" -ForegroundColor Cyan
        Write-Host "1. Go to https://share.streamlit.io" -ForegroundColor White
        Write-Host "2. Connect your GitHub repository" -ForegroundColor White
        Write-Host "3. Set main file to: dashboard.py" -ForegroundColor White
        Write-Host "4. Add environment variables in Secrets" -ForegroundColor White
    } else {
        Write-Host "Push failed. Check authentication." -ForegroundColor Red
    }
} else {
    Write-Host "Skipped push. Run manually:" -ForegroundColor Yellow
    Write-Host "  git push -u origin main" -ForegroundColor White
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

