# 재무실적보고서 HTML 생성기

Python을 사용하여 재무실적보고서를 HTML 형태로 생성하는 도구입니다.

## 기능

- **전체요약**: 주요 재무 지표를 카드 형태로 표시하고 요약 테이블 제공
- **손익계산서**: 연도별 손익계산서 데이터를 비교 차트와 테이블로 시각화
- **재무상태표**: 자산, 부채, 자본을 구분하여 표시하고 구성 비율 차트 제공

## 설치

```bash
pip install -r requirements.txt
```

## 사용 방법

### 1. JSON 파일 사용

```python
from financial_report_generator import FinancialReportGenerator

# JSON 파일에서 데이터 로드
generator = FinancialReportGenerator(data_file='sample_data.json')
generator.generate_html('financial_report.html')
```

### 2. Excel 파일 사용

Excel 파일은 다음 시트를 포함해야 합니다:
- `전체요약`
- `손익계산서`
- `재무상태표`

```python
from financial_report_generator import FinancialReportGenerator

# Excel 파일에서 데이터 로드
generator = FinancialReportGenerator(data_file='financial_data.xlsx')
generator.generate_html('financial_report.html')
```

### 3. 직접 데이터 딕셔너리 전달

```python
from financial_report_generator import FinancialReportGenerator

data = {
    'summary': [
        {'항목': '매출액', '값': 1000000000000, '단위': '원', '변동률': 5.2},
        # ... 더 많은 데이터
    ],
    'income_statement': [
        {'항목': '매출액', '2024년': 1000000000000, '2023년': 950000000000},
        # ... 더 많은 데이터
    ],
    'balance_sheet': [
        {'항목': '현금 및 현금성자산', '값': 500000000000},
        # ... 더 많은 데이터
    ]
}

generator = FinancialReportGenerator(data_dict=data)
generator.generate_html('financial_report.html')
```

## 필요한 데이터 구조

### 전체요약 (summary)

각 항목은 다음 필드를 포함해야 합니다:
- `항목` 또는 `name`: 지표 이름
- `값` 또는 `value`: 지표 값 (숫자)
- `단위` 또는 `unit`: 단위 (예: "원", "%")
- `변동률` 또는 `change`: 전년 대비 변동률 (선택사항)

예시:
```json
{
  "항목": "매출액",
  "값": 1000000000000,
  "단위": "원",
  "변동률": 5.2
}
```

### 손익계산서 (income_statement)

각 항목은 다음 필드를 포함해야 합니다:
- `항목` 또는 `name`: 계정 항목 이름
- 연도별 값: `2024년`, `2023년`, `2022년` 등 (또는 숫자로 `2024`, `2023` 등)

예시:
```json
{
  "항목": "매출액",
  "2024년": 1000000000000,
  "2023년": 950000000000,
  "2022년": 900000000000
}
```

### 재무상태표 (balance_sheet)

각 항목은 다음 필드를 포함해야 합니다:
- `항목` 또는 `name`: 계정 항목 이름
- `값` 또는 `value`: 계정 항목의 금액
- `분류` 또는 `category`: 자산/부채/자본 분류 (선택사항)

예시:
```json
{
  "항목": "현금 및 현금성자산",
  "값": 500000000000,
  "분류": "유동자산"
}
```

## 샘플 데이터

`sample_data.json` 파일에 샘플 데이터가 포함되어 있습니다. 이를 참고하여 자신의 데이터를 준비하세요.

## 실행 예시

```bash
python financial_report_generator.py
```

이 명령어는 샘플 데이터를 사용하여 `financial_report.html` 파일을 생성합니다.

## 출력

생성된 HTML 파일은 다음 기능을 포함합니다:
- 반응형 디자인 (모바일/태블릿/데스크톱 지원)
- 인터랙티브 탭 네비게이션
- Chart.js를 사용한 데이터 시각화
- 깔끔하고 전문적인 디자인

생성된 HTML 파일을 웹 브라우저에서 열어 확인할 수 있습니다.

## Snowflake MCP 연결

이 프로젝트는 Snowflake 데이터베이스를 Model Context Protocol (MCP)를 통해 연결할 수 있는 기능을 제공합니다.

### 설정 방법

1. **필요한 패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **Claude Desktop 설정 파일 업데이트**
   
   `claude_desktop_config.json` 파일이 이미 설정되어 있습니다. 파일 위치:
   ```
   C:\Users\AC1160\AppData\Roaming\Claude\claude_desktop_config.json
   ```
   
   설정 내용:
   ```json
   {
     "mcpServers": {
       "snowflake": {
         "command": "python",
         "args": [
           "C:\\Users\\AC1160\\OneDrive - F&F\\바탕 화면\\finance_dashboard\\snowflake_mcp_server.py"
         ],
         "env": {
           "SNOWFLAKE_ACCOUNT": "cixxjbf-wp67697",
           "SNOWFLAKE_USER": "songahreum",
           "SNOWFLAKE_PASSWORD": "Fnfsnowflake2025!",
           "SNOWFLAKE_WAREHOUSE": "DEV_WH",
           "SNOWFLAKE_DATABASE": "FNF",
           "SNOWFLAKE_SCHEMA": "SAP_FNF",
           "SNOWFLAKE_ROLE": "PU_SQL_SAP"
         }
       }
     }
   }
   ```

3. **Claude Desktop 재시작**
   
   설정 파일을 변경한 후 Claude Desktop을 재시작하면 Snowflake MCP 서버가 자동으로 연결됩니다.

### 사용 가능한 도구

MCP 서버를 통해 다음 도구들을 사용할 수 있습니다:

- **test_connection**: Snowflake 연결 테스트
- **execute_query**: SQL 쿼리 실행
- **list_tables**: 테이블 목록 조회
- **describe_table**: 테이블 구조 조회

### 테스트

MCP 서버가 제대로 작동하는지 테스트하려면:

```bash
python snowflake_mcp_server.py
```

서버가 정상적으로 시작되면 Claude Desktop에서 Snowflake 데이터베이스에 접근할 수 있습니다.

## 📊 F&F 실적 대시보드

Snowflake 데이터를 활용한 실시간 재무 실적 대시보드를 제공합니다.

### 대시보드 실행

1. **환경 변수 설정** (PowerShell)
   ```powershell
   .\setup_env.ps1
   ```
   또는 수동으로:
   ```powershell
   $env:SNOWFLAKE_ACCOUNT="cixxjbf-wp67697"
   $env:SNOWFLAKE_USER="songahreum"
   $env:SNOWFLAKE_PASSWORD="Fnfsnowflake2025!"
   $env:SNOWFLAKE_WAREHOUSE="DEV_WH"
   $env:SNOWFLAKE_DATABASE="FNF"
   $env:SNOWFLAKE_SCHEMA="SAP_FNF"
   $env:SNOWFLAKE_ROLE="PU_SQL_SAP"
   ```

2. **대시보드 실행**
   ```bash
   streamlit run dashboard.py
   ```
   또는 Windows에서:
   ```bash
   run_dashboard.bat
   ```

3. **브라우저에서 확인**
   - 자동으로 브라우저가 열립니다 (http://localhost:8501)
   - 또는 수동으로 브라우저에서 해당 주소로 접속

### 대시보드 기능

- **전체 요약**: 주요 재무 지표 카드 및 비교 차트
- **손익계산서**: 연도별 손익계산서 비교 및 트렌드 분석
- **재무상태표**: 자산/부채/자본 구성 비율 시각화
- **분석**: 주요 재무 비율 분석
- **테이블 탐색**: Snowflake 테이블 구조 확인
- **커스텀 쿼리**: 직접 SQL 쿼리 실행 및 결과 확인

### 중요: 쿼리 커스터마이징 필요

현재 대시보드는 샘플 데이터를 사용하고 있습니다. 실제 Snowflake 테이블에 맞게 `dashboard.py` 파일의 쿼리를 수정해야 합니다.

자세한 내용은 `DASHBOARD_README.md` 파일을 참조하세요.




