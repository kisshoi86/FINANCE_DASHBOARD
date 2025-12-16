# F&F 재무 실적 대시보드

Snowflake 데이터를 활용한 실시간 F&F 재무 실적 대시보드입니다.

## 📋 주요 기능

- **전체 요약**: 주요 재무 지표 카드 및 비교 차트
- **손익계산서**: 연도별 손익계산서 비교 및 트렌드 분석
- **재무상태표**: 자산/부채/자본 구성 비율 및 상세 내역
- **분석**: 주요 재무 비율 분석 (영업이익률, 순이익률 등)
- **Snowflake 연결**: 실시간 데이터베이스 연결 및 쿼리 실행

## 🚀 빠른 시작

### 로컬 실행

1. **패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **환경 변수 설정** (PowerShell)
   ```powershell
   $env:SNOWFLAKE_ACCOUNT="cixxjbf-wp67697"
   $env:SNOWFLAKE_USER="songahreum"
   $env:SNOWFLAKE_PASSWORD="Fnfsnowflake2025!"
   $env:SNOWFLAKE_WAREHOUSE="DEV_WH"
   $env:SNOWFLAKE_DATABASE="FNF"
   $env:SNOWFLAKE_SCHEMA="SAP_FNF"
   $env:SNOWFLAKE_ROLE="PU_SQL_SAP"
   ```

3. **대시보드 실행**
   ```bash
   streamlit run dashboard.py
   ```
   
   또는 배치 파일 실행:
   ```powershell
   .\run_dashboard.bat
   ```

### 클라우드 배포

자세한 배포 가이드는 [DEPLOY.md](DEPLOY.md)를 참고하세요.

**Streamlit Cloud 배포 (권장)**:
1. GitHub 저장소에 코드 푸시
2. https://share.streamlit.io 접속
3. GitHub 저장소 연결
4. 환경 변수 설정
5. 배포 완료!

## 📁 프로젝트 구조

```
finance_dashboard/
├── dashboard.py              # 메인 대시보드 애플리케이션
├── snowflake_connector.py    # Snowflake 연결 모듈
├── requirements.txt          # Python 패키지 의존성
├── .streamlit/
│   └── config.toml          # Streamlit 설정
├── DEPLOY.md                # 배포 가이드
└── README.md                # 이 파일
```

## 🔧 설정

### 환경 변수

Snowflake 연결을 위한 필수 환경 변수:

- `SNOWFLAKE_ACCOUNT`: Snowflake 계정 이름
- `SNOWFLAKE_USER`: 사용자 이름
- `SNOWFLAKE_PASSWORD`: 비밀번호
- `SNOWFLAKE_WAREHOUSE`: 웨어하우스 이름 (기본값: DEV_WH)
- `SNOWFLAKE_DATABASE`: 데이터베이스 이름 (기본값: FNF)
- `SNOWFLAKE_SCHEMA`: 스키마 이름 (기본값: SAP_FNF)
- `SNOWFLAKE_ROLE`: 역할 이름 (기본값: PU_SQL_SAP)

### Streamlit 설정

`.streamlit/config.toml`에서 테마 및 서버 설정을 변경할 수 있습니다.

## 📚 문서

- [대시보드 사용 가이드](DASHBOARD_README.md)
- [배포 가이드](DEPLOY.md)
- [환경 변수 설정 가이드](환경변수_설정_가이드.md)
- [GitHub 배포 가이드](GITHUB_DEPLOY_GUIDE.md)

## 🔐 보안 주의사항

- **절대 코드에 비밀번호를 하드코딩하지 마세요**
- 환경 변수나 Streamlit Secrets를 사용하세요
- `.env` 파일은 `.gitignore`에 추가되어 있습니다
- 프로덕션 환경에서는 더 안전한 인증 방법(키 페어, OAuth 등)을 사용하세요

## 🐛 문제 해결

### 연결 오류
- 환경 변수가 올바르게 설정되었는지 확인
- Snowflake 계정 정보가 정확한지 확인
- 네트워크 연결 상태 확인

### 데이터가 표시되지 않음
- `dashboard.py`의 쿼리가 실제 테이블 구조와 일치하는지 확인
- 사이드바의 "테이블 목록 조회"로 테이블 존재 여부 확인
- 쿼리 실행 시 오류 메시지 확인

### 패키지 설치 오류
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 📝 라이선스

이 프로젝트는 F&F 내부 사용을 위한 것입니다.

## 👥 작성자

F&F 개발팀
