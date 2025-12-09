"""
F&F 실적 대시보드
Snowflake 데이터를 활용한 실시간 재무 실적 대시보드
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# pyarrow 확인 및 설정
try:
    import pyarrow
    HAS_PYARROW = True
except ImportError:
    HAS_PYARROW = False
    # pyarrow가 없어도 작동하도록 설정
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning, message='.*pyarrow.*')

from snowflake_connector import get_snowflake_connector, format_currency, format_percentage

# 페이지 설정
st.set_page_config(
    page_title="F&F 실적 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# shadcn/ui 디자인 시스템 적용
st.markdown("""
<style>
    /* shadcn/ui Color Palette - CSS Variables */
    :root {
        --background: 0 0% 100%;
        --foreground: 222.2 84% 4.9%;
        --card: 0 0% 100%;
        --card-foreground: 222.2 84% 4.9%;
        --popover: 0 0% 100%;
        --popover-foreground: 222.2 84% 4.9%;
        --primary: 221.2 83.2% 53.3%;
        --primary-foreground: 210 40% 98%;
        --secondary: 210 40% 96.1%;
        --secondary-foreground: 222.2 47.4% 11.2%;
        --muted: 210 40% 96.1%;
        --muted-foreground: 215.4 16.3% 46.9%;
        --accent: 210 40% 96.1%;
        --accent-foreground: 222.2 47.4% 11.2%;
        --destructive: 0 84.2% 60.2%;
        --destructive-foreground: 210 40% 98%;
        --border: 214.3 31.8% 91.4%;
        --input: 214.3 31.8% 91.4%;
        --ring: 221.2 83.2% 53.3%;
        --radius: 0.5rem;
    }
    
    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Header Styles - shadcn inspired */
    .main-header {
        background: hsl(var(--card));
        border: 1px solid hsl(var(--border));
        padding: 2rem;
        border-radius: calc(var(--radius) + 4px);
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-header h1 {
        color: hsl(var(--foreground));
        font-size: 2rem;
        font-weight: 600;
        letter-spacing: -0.025em;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: hsl(var(--muted-foreground));
        font-size: 0.875rem;
    }
    
    /* Metric Card - shadcn Card style */
    .metric-card {
        background: hsl(var(--card));
        border: 1px solid hsl(var(--border));
        padding: 1.5rem;
        border-radius: var(--radius);
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        transition: all 0.2s ease-in-out;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        border-color: hsl(var(--ring));
    }
    
    .metric-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: hsl(var(--muted-foreground));
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: hsl(var(--foreground));
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    
    .metric-change {
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .positive-change {
        color: hsl(142.1 76.2% 36.3%);
    }
    
    .negative-change {
        color: hsl(var(--destructive));
    }
    
    /* Streamlit Component Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: hsl(var(--muted));
        border-radius: var(--radius);
        padding: 0.25rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: calc(var(--radius) - 2px);
        padding: 0.5rem 1rem;
        font-weight: 500;
        color: hsl(var(--muted-foreground));
        transition: all 0.2s;
    }
    
    .stTabs [aria-selected="true"] {
        background: hsl(var(--card));
        color: hsl(var(--foreground));
        box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    }
    
    /* Sidebar Styles */
    [data-testid="stSidebar"] {
        background: hsl(var(--card));
        border-right: 1px solid hsl(var(--border));
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: hsl(var(--primary));
        color: hsl(var(--primary-foreground));
        border: none;
        border-radius: var(--radius);
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
        width: 100%;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: hsl(var(--primary) / 0.9);
        box-shadow: 0 2px 4px 0 rgb(0 0 0 / 0.1);
    }
    
    /* Dataframe Styles */
    .stDataFrame {
        border: 1px solid hsl(var(--border));
        border-radius: var(--radius);
        overflow: hidden;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid hsl(var(--border));
        margin: 1.5rem 0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: hsl(var(--foreground));
        font-weight: 600;
        letter-spacing: -0.025em;
    }
    
    h2 {
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        font-size: 1.25rem;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* Info/Warning/Error Messages */
    .stAlert {
        border: 1px solid hsl(var(--border));
        border-radius: var(--radius);
    }
    
    /* Plotly Chart Container */
    .js-plotly-plot {
        border: 1px solid hsl(var(--border));
        border-radius: var(--radius);
        padding: 1rem;
        background: hsl(var(--card));
    }
    
    /* Text Input */
    .stTextArea textarea {
        border: 1px solid hsl(var(--input));
        border-radius: var(--radius);
        padding: 0.5rem;
        font-size: 0.875rem;
    }
    
    .stTextArea textarea:focus {
        outline: none;
        border-color: hsl(var(--ring));
        box-shadow: 0 0 0 2px hsl(var(--ring) / 0.2);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: hsl(var(--muted));
        border-radius: var(--radius);
        padding: 0.75rem;
        font-weight: 500;
    }
    
    /* Metric Display */
    [data-testid="stMetricValue"] {
        color: hsl(var(--foreground));
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: hsl(var(--muted-foreground));
        font-weight: 500;
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: hsl(var(--secondary));
        color: hsl(var(--secondary-foreground));
        border: 1px solid hsl(var(--border));
        border-radius: var(--radius);
        font-weight: 500;
    }
    
    .stDownloadButton > button:hover {
        background: hsl(var(--secondary) / 0.8);
    }
</style>
""", unsafe_allow_html=True)


def load_financial_summary(connector):
    """주요 재무 지표 요약 데이터 로드"""
    # 실제 테이블 구조에 맞게 쿼리를 수정해야 합니다
    # 예시 쿼리 (실제 테이블명과 컬럼명에 맞게 수정 필요)
    query = """
    -- 주요 재무 지표 조회 쿼리
    -- 실제 테이블 구조에 맞게 수정이 필요합니다
    SELECT 
        '매출액' as "항목",
        1000000000000 as "값",
        '원' as "단위",
        5.2 as "변동률"
    UNION ALL
    SELECT 
        '영업이익',
        150000000000,
        '원',
        8.3
    UNION ALL
    SELECT 
        '순이익',
        120000000000,
        '원',
        6.1
    UNION ALL
    SELECT 
        '총자산',
        5000000000000,
        '원',
        3.5
    UNION ALL
    SELECT 
        '부채비율',
        45.2,
        '%',
        -2.1
    UNION ALL
    SELECT 
        'ROE',
        12.5,
        '%',
        1.2
    """
    
    try:
        return connector.execute_query(query)
    except Exception as e:
        st.error(f"데이터 로드 오류: {str(e)}")
        return None


def load_income_statement(connector, years=3):
    """손익계산서 데이터 로드"""
    # 실제 테이블 구조에 맞게 쿼리를 수정해야 합니다
    query = """
    -- 손익계산서 데이터 조회 쿼리
    -- 실제 테이블 구조에 맞게 수정이 필요합니다
    SELECT 
        '매출액' as "항목",
        2024 as "연도",
        1000000000000 as "금액"
    UNION ALL
    SELECT '매출액', 2023, 950000000000
    UNION ALL
    SELECT '매출액', 2022, 900000000000
    UNION ALL
    SELECT '매출원가', 2024, 600000000000
    UNION ALL
    SELECT '매출원가', 2023, 570000000000
    UNION ALL
    SELECT '매출원가', 2022, 540000000000
    UNION ALL
    SELECT '영업이익', 2024, 150000000000
    UNION ALL
    SELECT '영업이익', 2023, 140000000000
    UNION ALL
    SELECT '영업이익', 2022, 130000000000
    UNION ALL
    SELECT '순이익', 2024, 120000000000
    UNION ALL
    SELECT '순이익', 2023, 113000000000
    UNION ALL
    SELECT '순이익', 2022, 105000000000
    """
    
    try:
        return connector.execute_query(query)
    except Exception as e:
        st.error(f"손익계산서 데이터 로드 오류: {str(e)}")
        return None


def load_balance_sheet(connector):
    """재무상태표 데이터 로드"""
    # 실제 테이블 구조에 맞게 쿼리를 수정해야 합니다
    query = """
    -- 재무상태표 데이터 조회 쿼리
    -- 실제 테이블 구조에 맞게 수정이 필요합니다
    SELECT 
        '현금 및 현금성자산' as "항목",
        500000000000 as "값",
        '유동자산' as "분류"
    UNION ALL
    SELECT '매출채권', 300000000000, '유동자산'
    UNION ALL
    SELECT '재고자산', 200000000000, '유동자산'
    UNION ALL
    SELECT '유형자산', 3000000000000, '비유동자산'
    UNION ALL
    SELECT '단기차입금', 200000000000, '유동부채'
    UNION ALL
    SELECT '장기차입금', 1800000000000, '비유동부채'
    UNION ALL
    SELECT '자본금', 500000000000, '자본'
    UNION ALL
    SELECT '이익잉여금', 2150000000000, '자본'
    """
    
    try:
        return connector.execute_query(query)
    except Exception as e:
        st.error(f"재무상태표 데이터 로드 오류: {str(e)}")
        return None


def create_metric_card(label, value, unit="", change=None, change_label=""):
    """재무 지표 카드 생성 - shadcn 스타일"""
    change_html = ""
    if change is not None:
        change_class = "positive-change" if change >= 0 else "negative-change"
        change_icon = "↑" if change >= 0 else "↓"
        change_html = f'<div class="metric-change {change_class}">{change_icon} {abs(change):.1f}% {change_label}</div>'
    
    formatted_value = format_currency(value, unit) if unit == "원" else f"{value:,.1f} {unit}"
    
    card_html = f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{formatted_value}</div>
        {change_html}
    </div>
    """
    return card_html


def main():
    # 헤더 - shadcn 스타일
    st.markdown("""
    <div class="main-header">
        <h1>F&F 실적 대시보드</h1>
        <p>실시간 재무 실적 모니터링</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바 - 연결 설정 및 테이블 탐색 (shadcn 스타일)
    with st.sidebar:
        st.markdown("### ⚙️ 설정")
        
        # 환경 변수 상태 확인
        env_status = {
            "SNOWFLAKE_ACCOUNT": os.getenv('SNOWFLAKE_ACCOUNT'),
            "SNOWFLAKE_USER": os.getenv('SNOWFLAKE_USER'),
            "SNOWFLAKE_PASSWORD": "설정됨" if os.getenv('SNOWFLAKE_PASSWORD') else "미설정",
            "SNOWFLAKE_WAREHOUSE": os.getenv('SNOWFLAKE_WAREHOUSE', 'DEV_WH'),
            "SNOWFLAKE_DATABASE": os.getenv('SNOWFLAKE_DATABASE', 'FNF'),
            "SNOWFLAKE_SCHEMA": os.getenv('SNOWFLAKE_SCHEMA', 'SAP_FNF'),
            "SNOWFLAKE_ROLE": os.getenv('SNOWFLAKE_ROLE', 'PU_SQL_SAP')
        }
        
        with st.expander("🔍 환경 변수 확인", expanded=False):
            for key, value in env_status.items():
                if value:
                    st.text(f"{key}: {value}")
                else:
                    st.error(f"{key}: ❌ 미설정")
        
        # 연결 테스트
        if st.button("🔌 Snowflake 연결 테스트", use_container_width=True):
            try:
                connector = get_snowflake_connector()
                result = connector.test_connection()
                if result["status"] == "success":
                    st.success("✅ 연결 성공!")
                    st.json(result)
                else:
                    st.error(f"❌ 연결 실패: {result.get('message', 'Unknown error')}")
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ 연결 실패: {error_msg}")
                if "환경 변수가 설정되지 않았습니다" in error_msg:
                    st.info("💡 사이드바의 '환경 변수 확인'을 열어 설정 상태를 확인하세요.")
        
        st.divider()
        
        # 테이블 탐색
        st.markdown("### 📋 테이블 탐색")
        if st.button("테이블 목록 조회", use_container_width=True):
            try:
                connector = get_snowflake_connector()
                tables = connector.get_tables()
                if tables:
                    st.success(f"✅ {len(tables)}개의 테이블을 찾았습니다")
                    for table in tables:
                        with st.expander(table['TABLE_NAME']):
                            st.write(f"**타입:** {table['TABLE_TYPE']}")
                            st.write(f"**생성일:** {table.get('CREATED', 'N/A')}")
                            # 컬럼 정보 조회
                            if st.button(f"{table['TABLE_NAME']} 컬럼 보기", key=f"cols_{table['TABLE_NAME']}"):
                                cols = connector.get_table_columns(table['TABLE_NAME'])
                                st.dataframe(cols)
                else:
                    st.info("테이블이 없습니다")
            except Exception as e:
                st.error(f"오류: {str(e)}")
        
        st.divider()
        
        # 커스텀 쿼리 실행
        st.markdown("### 🔍 커스텀 쿼리")
        custom_query = st.text_area("SQL 쿼리 입력", height=150, label_visibility="collapsed", placeholder="SELECT * FROM ...")
        if st.button("쿼리 실행", use_container_width=True):
            if custom_query:
                try:
                    connector = get_snowflake_connector()
                    df = connector.execute_query(custom_query)
                    st.dataframe(df)
                    st.download_button(
                        label="📥 CSV 다운로드",
                        data=df.to_csv(index=False).encode('utf-8-sig'),
                        file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"쿼리 실행 오류: {str(e)}")
    
    # 메인 대시보드
    try:
        # Snowflake 연결 시도
        try:
            connector = get_snowflake_connector()
            # 연결 테스트
            test_result = connector.test_connection()
            if test_result["status"] != "success":
                raise ConnectionError(test_result.get("message", "연결 실패"))
        except (ConnectionError, Exception) as conn_error:
            st.warning("⚠️ **Snowflake 연결 실패**")
            st.info(f"""
            **오류 내용:** {str(conn_error)}
            
            **해결 방법:**
            1. 사이드바의 "환경 변수 확인"을 열어 설정 상태를 확인하세요
            2. PowerShell에서 다음 명령어로 환경 변수를 설정하세요:
            
            ```powershell
            $env:SNOWFLAKE_ACCOUNT="cixxjbf-wp67697"
            $env:SNOWFLAKE_USER="songahreum"
            $env:SNOWFLAKE_PASSWORD="Fnfsnowflake2025!"
            $env:SNOWFLAKE_WAREHOUSE="DEV_WH"
            $env:SNOWFLAKE_DATABASE="FNF"
            $env:SNOWFLAKE_SCHEMA="SAP_FNF"
            $env:SNOWFLAKE_ROLE="PU_SQL_SAP"
            ```
            
            3. 환경 변수 설정 후 브라우저를 새로고침하세요
            4. 또는 `setup_env.ps1` 스크립트를 실행하세요
            """)
            st.stop()
        
        # 탭 생성
        tab1, tab2, tab3, tab4 = st.tabs(["전체 요약", "손익계산서", "재무상태표", "분석"])
        
        # 탭 1: 전체 요약
        with tab1:
            st.markdown("## 주요 재무 지표")
            
            summary_data = load_financial_summary(connector)
            
            # 디버깅: 데이터 확인
            if summary_data is None:
                st.error("❌ 데이터를 불러올 수 없습니다 (None 반환)")
            elif summary_data.empty:
                st.warning("⚠️ 데이터가 비어있습니다")
            elif len(summary_data) == 0:
                st.warning("⚠️ 데이터 행이 없습니다")
            else:
                st.success(f"✅ {len(summary_data)}개의 데이터 로드 완료")
            
            if summary_data is not None and not summary_data.empty and len(summary_data) > 0:
                # 주요 지표 카드
                cols = st.columns(3)
                for idx, row in summary_data.head(6).iterrows():
                    with cols[idx % 3]:
                        change = row.get('변동률', None)
                        change_label = "전년 대비" if change is not None else ""
                        st.markdown(
                            create_metric_card(
                                row['항목'],
                                row['값'],
                                row.get('단위', ''),
                                change,
                                change_label
                            ),
                            unsafe_allow_html=True
                        )
                
                st.divider()
                
                # 차트
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("주요 지표 비교")
                    # shadcn primary color: hsl(221.2 83.2% 53.3%)
                    fig = px.bar(
                        summary_data,
                        x='항목',
                        y='값',
                        color='항목',
                        color_discrete_sequence=['hsl(221.2, 83.2%, 53.3%)', 'hsl(221.2, 83.2%, 60%)', 'hsl(221.2, 83.2%, 65%)'],
                        title="주요 재무 지표"
                    )
                    fig.update_layout(
                        showlegend=False, 
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family='system-ui, -apple-system, sans-serif')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("### 변동률")
                    # shadcn destructive (red) and success (green) colors
                    fig = px.bar(
                        summary_data,
                        x='항목',
                        y='변동률',
                        color='변동률',
                        color_continuous_scale=['hsl(0, 84.2%, 60.2%)', 'hsl(142.1, 76.2%, 36.3%)'],
                        title="전년 대비 변동률 (%)"
                    )
                    fig.update_layout(
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family='system-ui, -apple-system, sans-serif')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # 상세 테이블
                st.subheader("상세 내역")
                st.dataframe(summary_data, use_container_width=True)
            else:
                st.info("데이터를 불러올 수 없습니다. Snowflake 연결 및 쿼리를 확인하세요.")
        
        # 탭 2: 손익계산서
        with tab2:
            st.markdown("## 손익계산서")
            
            income_data = load_income_statement(connector)
            
            if income_data is not None and not income_data.empty:
                # 연도별 비교 차트
                st.markdown("### 연도별 비교")
                
                # 피벗 테이블 생성
                pivot_data = income_data.pivot(index='항목', columns='연도', values='금액').reset_index()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # shadcn color palette
                    fig = px.bar(
                        income_data,
                        x='항목',
                        y='금액',
                        color='연도',
                        barmode='group',
                        color_discrete_sequence=[
                            'hsl(221.2, 83.2%, 53.3%)',
                            'hsl(221.2, 83.2%, 60%)',
                            'hsl(221.2, 83.2%, 65%)'
                        ],
                        title="연도별 손익계산서 비교"
                    )
                    fig.update_layout(
                        height=500,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family='system-ui, -apple-system, sans-serif')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # 주요 항목 트렌드
                    main_items = ['매출액', '영업이익', '순이익']
                    trend_data = income_data[income_data['항목'].isin(main_items)]
                    
                    fig = px.line(
                        trend_data,
                        x='연도',
                        y='금액',
                        color='항목',
                        markers=True,
                        color_discrete_sequence=[
                            'hsl(221.2, 83.2%, 53.3%)',
                            'hsl(142.1, 76.2%, 36.3%)',
                            'hsl(0, 84.2%, 60.2%)'
                        ],
                        title="주요 항목 트렌드"
                    )
                    fig.update_layout(
                        height=500,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family='system-ui, -apple-system, sans-serif')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # 상세 테이블
                st.markdown("### 상세 내역")
                st.dataframe(pivot_data, use_container_width=True)
            else:
                st.info("손익계산서 데이터를 불러올 수 없습니다.")
        
        # 탭 3: 재무상태표
        with tab3:
            st.markdown("## 재무상태표")
            
            balance_data = load_balance_sheet(connector)
            
            if balance_data is not None and not balance_data.empty:
                # 자산/부채/자본 요약
                summary_by_category = balance_data.groupby('분류')['값'].sum().reset_index()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 분류별 구성")
                    # shadcn color palette for pie chart
                    fig = px.pie(
                        summary_by_category,
                        values='값',
                        names='분류',
                        color_discrete_sequence=[
                            'hsl(221.2, 83.2%, 53.3%)',
                            'hsl(142.1, 76.2%, 36.3%)',
                            'hsl(0, 84.2%, 60.2%)',
                            'hsl(38, 92%, 50%)',
                            'hsl(280, 70%, 50%)'
                        ],
                        title="자산/부채/자본 구성"
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family='system-ui, -apple-system, sans-serif')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("### 분류별 금액")
                    fig = px.bar(
                        summary_by_category,
                        x='분류',
                        y='값',
                        color='분류',
                        color_discrete_sequence=[
                            'hsl(221.2, 83.2%, 53.3%)',
                            'hsl(142.1, 76.2%, 36.3%)',
                            'hsl(0, 84.2%, 60.2%)',
                            'hsl(38, 92%, 50%)',
                            'hsl(280, 70%, 50%)'
                        ],
                        title="분류별 총액"
                    )
                    fig.update_layout(
                        showlegend=False, 
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family='system-ui, -apple-system, sans-serif')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # 상세 테이블
                st.markdown("### 상세 내역")
                st.dataframe(balance_data, use_container_width=True)
            else:
                st.info("재무상태표 데이터를 불러올 수 없습니다.")
        
        # 탭 4: 분석
        with tab4:
            st.markdown("## 재무 분석")
            
            st.markdown("### 📌 분석 지표")
            
            summary_data = load_financial_summary(connector)
            income_data = load_income_statement(connector)
            
            if summary_data is not None and income_data is not None:
                # 주요 비율 계산
                metrics_cols = st.columns(4)
                
                # 매출액 대비 영업이익률
                if not income_data.empty:
                    revenue_2024 = income_data[(income_data['항목'] == '매출액') & (income_data['연도'] == 2024)]['금액'].values
                    operating_2024 = income_data[(income_data['항목'] == '영업이익') & (income_data['연도'] == 2024)]['금액'].values
                    
                    if len(revenue_2024) > 0 and len(operating_2024) > 0 and revenue_2024[0] > 0:
                        operating_margin = (operating_2024[0] / revenue_2024[0]) * 100
                        with metrics_cols[0]:
                            st.metric("영업이익률", f"{operating_margin:.2f}%")
                    
                    # 순이익률
                    net_2024 = income_data[(income_data['항목'] == '순이익') & (income_data['연도'] == 2024)]['금액'].values
                    if len(net_2024) > 0 and revenue_2024[0] > 0:
                        net_margin = (net_2024[0] / revenue_2024[0]) * 100
                        with metrics_cols[1]:
                            st.metric("순이익률", f"{net_margin:.2f}%")
                
                st.info("💡 **참고:** 실제 Snowflake 테이블 구조에 맞게 쿼리를 수정해야 합니다. 현재는 샘플 데이터를 사용하고 있습니다.")
            else:
                st.warning("분석을 위한 데이터를 불러올 수 없습니다.")
    
    except ImportError as import_error:
        if 'pyarrow' in str(import_error):
            # pyarrow는 선택적 패키지이므로 경고만 표시하고 계속 진행
            st.sidebar.warning("ℹ️ pyarrow가 설치되지 않았습니다 (선택사항)")
        else:
            st.error(f"모듈 import 오류: {str(import_error)}")
            st.stop()
    except Exception as e:
        error_msg = str(e)
        # pyarrow 관련 오류는 무시 (이미 설치되어 있음)
        if 'pyarrow' in error_msg.lower():
            pass  # pyarrow는 이미 설치되어 있으므로 무시
        else:
            st.error(f"대시보드 로드 오류: {str(e)}")
            st.info("Snowflake 연결 정보를 확인하세요. 환경 변수가 설정되어 있는지 확인해주세요.")


if __name__ == "__main__":
    main()

