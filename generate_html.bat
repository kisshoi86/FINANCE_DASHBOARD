@echo off
chcp 65001 >nul
echo 대시보드 HTML 생성 중...
python generate_dashboard_html.py
if %errorlevel% == 0 (
    echo.
    echo ✅ HTML 파일이 생성되었습니다!
    echo 📂 dashboard_preview.html 파일을 브라우저에서 열어보세요.
    pause
) else (
    echo.
    echo ❌ 오류가 발생했습니다.
    pause
)












