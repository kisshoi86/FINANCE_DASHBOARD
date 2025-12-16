# F&F 실적 대시보드 사용 가이드

Snowflake 데이터를 활용한 실시간 F&F 재무 실적 대시보드입니다.

## 🚀 빠른 시작

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

Windows PowerShell에서:
```powershell
$env:SNOWFLAKE_ACCOUNT="cixxjbf-wp67697"
$env:SNOWFLAKE_USER="songahreum"
$env:SNOWFLAKE_PASSWORD="Fnfsnowflake2025!"
$env:SNOWFLAKE_WAREHOUSE="DEV_WH"
$env:SNOWFLAKE_DATABASE="FNF"
$env:SNOWFLAKE_SCHEMA="SAP_FNF"
$env:SNOWFLAKE_ROLE="PU_SQL_SAP"
```

또는 `.env` 파일을 생성하고 `python-dotenv` 패키지를 사용할 수도 있습니다.

### 3. 대시보드 실행

```bash
streamlit run dashboard.py
```

또는 Windows에서:
```bash
run_dashboard.bat
```

브라우저가 자동으로 열리며 대시보드가 표시됩니다. (기본 주소: http://localhost:8501)

## 📊 대시보드 기능

### 1. 전체 요약 탭
- 주요 재무 지표 카드 (매출액, 영업이익, 순이익 등)
- 지표별 비교 차트
- 전년 대비 변동률 시각화
- 상세 지표 테이블

### 2. 손익계산서 탭
- 연도별 손익계산서 비교
- 주요 항목 트렌드 분석
- 상세 손익계산서 테이블

### 3. 재무상태표 탭
- 자산/부채/자본 구성 비율
- 분류별 금액 비교
- 상세 재무상태표 테이블

### 4. 분석 탭
- 주요 재무 비율 분석
- 영업이익률, 순이익률 등

### 5. 사이드바 기능
- **Snowflake 연결 테스트**: 현재 연결 상태 확인
- **테이블 탐색**: 데이터베이스의 테이블 목록 및 구조 확인
- **커스텀 쿼리**: 직접 SQL 쿼리를 실행하고 결과 확인

## 🔧 Snowflake 쿼리 커스터마이징

현재 대시보드는 샘플 데이터를 사용하고 있습니다. 실제 Snowflake 테이블에 맞게 쿼리를 수정해야 합니다.

### 수정이 필요한 파일: `dashboard.py`

#### 1. `load_financial_summary()` 함수
```python
def load_financial_summary(connector):
    query = """
    -- 실제 테이블명과 컬럼명으로 수정
    SELECT 
        항목명 as 항목,
        금액 as 값,
        단위,
        변동률
    FROM FNF.SAP_FNF.재무지표테이블
    WHERE 기준일자 = CURRENT_DATE()
    """
    return connector.execute_query(query)
```

#### 2. `load_income_statement()` 함수
```python
def load_income_statement(connector, years=3):
    query = """
    -- 실제 테이블명과 컬럼명으로 수정
    SELECT 
        계정과목 as 항목,
        연도,
        금액
    FROM FNF.SAP_FNF.손익계산서테이블
    WHERE 연도 >= YEAR(CURRENT_DATE()) - :years
    ORDER BY 연도 DESC, 계정과목
    """
    return connector.execute_query(query)
```

#### 3. `load_balance_sheet()` 함수
```python
def load_balance_sheet(connector):
    query = """
    -- 실제 테이블명과 컬럼명으로 수정
    SELECT 
        계정과목 as 항목,
        금액 as 값,
        분류
    FROM FNF.SAP_FNF.재무상태표테이블
    WHERE 기준일자 = CURRENT_DATE()
    ORDER BY 분류, 계정과목
    """
    return connector.execute_query(query)
```

## 📋 실제 테이블 구조 확인 방법

1. 대시보드를 실행합니다
2. 사이드바에서 "테이블 목록 조회" 버튼을 클릭합니다
3. 각 테이블의 "컬럼 보기" 버튼을 클릭하여 구조를 확인합니다
4. 확인한 테이블명과 컬럼명을 사용하여 쿼리를 수정합니다

## 🔐 보안 주의사항

- **절대 코드에 비밀번호를 하드코딩하지 마세요**
- 환경 변수나 `.env` 파일을 사용하세요
- `.env` 파일은 `.gitignore`에 추가하세요
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

## 📝 추가 기능 개발

대시보드를 확장하려면:

1. **새로운 데이터 소스 추가**: `snowflake_connector.py`에 새로운 쿼리 함수 추가
2. **새로운 시각화 추가**: `dashboard.py`에 Plotly 차트 추가
3. **필터링 기능**: Streamlit의 `st.selectbox`, `st.date_input` 등 사용
4. **데이터 내보내기**: `st.download_button`으로 Excel/PDF 내보내기 기능 추가

## 📞 지원

문제가 발생하거나 질문이 있으시면:
1. 사이드바의 "커스텀 쿼리" 기능으로 직접 SQL을 테스트해보세요
2. Snowflake 연결 로그를 확인하세요
3. Streamlit의 오류 메시지를 확인하세요












