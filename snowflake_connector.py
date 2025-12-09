"""
Snowflake 데이터베이스 연결 및 데이터 조회 모듈
F&F 실적 데이터를 Snowflake에서 조회하는 기능을 제공합니다.
"""

import os
import pandas as pd
import snowflake.connector
from snowflake.connector import DictCursor
from typing import Optional, Dict, List
import streamlit as st


class SnowflakeConnector:
    """Snowflake 데이터베이스 연결 및 쿼리 실행 클래스"""
    
    def __init__(self):
        """환경 변수에서 Snowflake 연결 정보를 읽어옵니다."""
        self.account = os.getenv('SNOWFLAKE_ACCOUNT')
        self.user = os.getenv('SNOWFLAKE_USER')
        self.password = os.getenv('SNOWFLAKE_PASSWORD')
        self.warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'DEV_WH')
        self.database = os.getenv('SNOWFLAKE_DATABASE', 'FNF')
        self.schema = os.getenv('SNOWFLAKE_SCHEMA', 'SAP_FNF')
        self.role = os.getenv('SNOWFLAKE_ROLE', 'PU_SQL_SAP')
        self._connection = None
    
    def connect(self):
        """Snowflake에 연결합니다."""
        # 필수 환경 변수 검증
        if not self.account:
            raise ConnectionError("SNOWFLAKE_ACCOUNT 환경 변수가 설정되지 않았습니다.")
        if not self.user:
            raise ConnectionError("SNOWFLAKE_USER 환경 변수가 설정되지 않았습니다.")
        if not self.password:
            raise ConnectionError("SNOWFLAKE_PASSWORD 환경 변수가 설정되지 않았습니다.")
        
        try:
            if self._connection is None or self._connection.is_closed():
                # account에서 .snowflakecomputing.com 제거 (있는 경우)
                account_clean = self.account.replace('.snowflakecomputing.com', '').replace('https://', '').replace('http://', '')
                
                self._connection = snowflake.connector.connect(
                    user=self.user,
                    password=self.password,
                    account=account_clean,
                    warehouse=self.warehouse,
                    database=self.database,
                    schema=self.schema,
                    role=self.role
                )
            return self._connection
        except Exception as e:
            raise ConnectionError(f"Snowflake 연결 실패: {str(e)}")
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """SQL 쿼리를 실행하고 결과를 DataFrame으로 반환합니다."""
        try:
            conn = self.connect()
            cursor = conn.cursor(DictCursor)
            cursor.execute(query)
            
            # 결과를 DataFrame으로 변환
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            
            cursor.close()
            
            if rows:
                df = pd.DataFrame(rows)
                return df
            else:
                return pd.DataFrame(columns=columns)
        except Exception as e:
            raise Exception(f"쿼리 실행 실패: {str(e)}")
    
    def get_tables(self) -> List[Dict]:
        """현재 스키마의 테이블 목록을 반환합니다."""
        query = f"""
            SELECT TABLE_NAME, TABLE_TYPE, CREATED, LAST_ALTERED
            FROM {self.database}.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{self.schema}'
            ORDER BY TABLE_NAME
        """
        return self.execute_query(query).to_dict('records')
    
    def get_table_columns(self, table_name: str) -> pd.DataFrame:
        """테이블의 컬럼 정보를 반환합니다."""
        query = f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                COMMENT
            FROM {self.database}.INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{self.schema}' AND TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """
        return self.execute_query(query)
    
    def test_connection(self) -> Dict:
        """연결을 테스트하고 현재 설정 정보를 반환합니다."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION(), CURRENT_USER(), CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_ROLE()")
            result = cursor.fetchone()
            cursor.close()
            
            return {
                "status": "success",
                "version": result[0],
                "user": result[1],
                "database": result[2],
                "schema": result[3],
                "role": result[4]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def close(self):
        """연결을 닫습니다."""
        if self._connection and not self._connection.is_closed():
            self._connection.close()
            self._connection = None


@st.cache_resource
def get_snowflake_connector():
    """Streamlit 캐시를 사용한 Snowflake 연결자 반환"""
    return SnowflakeConnector()


def format_currency(value: float, unit: str = "원") -> str:
    """금액을 한국어 형식으로 포맷팅합니다."""
    if value is None or pd.isna(value):
        return "0"
    
    abs_value = abs(value)
    
    if abs_value >= 1000000000000:  # 조
        return f"{value/1000000000000:.2f}조 {unit}"
    elif abs_value >= 100000000:  # 억
        return f"{value/100000000:.2f}억 {unit}"
    elif abs_value >= 10000:  # 만
        return f"{value/10000:.2f}만 {unit}"
    else:
        return f"{value:,.0f} {unit}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """퍼센트를 포맷팅합니다."""
    if value is None or pd.isna(value):
        return "0%"
    return f"{value:.{decimals}f}%"

