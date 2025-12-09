# F&F 실적 대시보드 환경 변수 설정 스크립트
# PowerShell에서 실행: .\setup_env.ps1

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "F&F 실적 대시보드 환경 변수 설정" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 기존 환경 변수 확인
$currentAccount = $env:SNOWFLAKE_ACCOUNT
$currentUser = $env:SNOWFLAKE_USER

if ($currentAccount) {
    Write-Host "현재 설정된 SNOWFLAKE_ACCOUNT: $currentAccount" -ForegroundColor Yellow
}
if ($currentUser) {
    Write-Host "현재 설정된 SNOWFLAKE_USER: $currentUser" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "환경 변수를 설정하시겠습니까? (Y/N)" -ForegroundColor Green
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    # 기본값 사용 (README에서 확인한 값)
    $env:SNOWFLAKE_ACCOUNT = "cixxjbf-wp67697"
    $env:SNOWFLAKE_USER = "songahreum"
    $env:SNOWFLAKE_PASSWORD = "Fnfsnowflake2025!"
    $env:SNOWFLAKE_WAREHOUSE = "DEV_WH"
    $env:SNOWFLAKE_DATABASE = "FNF"
    $env:SNOWFLAKE_SCHEMA = "SAP_FNF"
    $env:SNOWFLAKE_ROLE = "PU_SQL_SAP"
    
    Write-Host ""
    Write-Host "✅ 환경 변수가 설정되었습니다!" -ForegroundColor Green
    Write-Host ""
    Write-Host "설정된 값:" -ForegroundColor Cyan
    Write-Host "  SNOWFLAKE_ACCOUNT: $env:SNOWFLAKE_ACCOUNT"
    Write-Host "  SNOWFLAKE_USER: $env:SNOWFLAKE_USER"
    Write-Host "  SNOWFLAKE_WAREHOUSE: $env:SNOWFLAKE_WAREHOUSE"
    Write-Host "  SNOWFLAKE_DATABASE: $env:SNOWFLAKE_DATABASE"
    Write-Host "  SNOWFLAKE_SCHEMA: $env:SNOWFLAKE_SCHEMA"
    Write-Host "  SNOWFLAKE_ROLE: $env:SNOWFLAKE_ROLE"
    Write-Host ""
    Write-Host "⚠️  주의: 이 설정은 현재 PowerShell 세션에만 유효합니다." -ForegroundColor Yellow
    Write-Host "대시보드를 실행하려면 같은 PowerShell 창에서 'streamlit run dashboard.py'를 실행하세요." -ForegroundColor Yellow
} else {
    Write-Host "설정이 취소되었습니다." -ForegroundColor Red
}

Write-Host ""
Write-Host "대시보드 실행 명령어:" -ForegroundColor Cyan
Write-Host "  streamlit run dashboard.py" -ForegroundColor White







