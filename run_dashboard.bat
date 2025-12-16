@echo off
REM F&F 실적 대시보드 실행 스크립트

echo ====================================
echo F&F 실적 대시보드 시작 중...
echo ====================================

REM 환경 변수 설정 (필요한 경우 여기에 추가)
REM set SNOWFLAKE_ACCOUNT=cixxjbf-wp67697
REM set SNOWFLAKE_USER=your_username
REM set SNOWFLAKE_PASSWORD=your_password

REM Streamlit 대시보드 실행
streamlit run dashboard.py

pause












