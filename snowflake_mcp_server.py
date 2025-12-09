#!/usr/bin/env python3
"""
Snowflake MCP Server
Model Context Protocol 서버를 통해 Snowflake 데이터베이스에 연결합니다.
"""

import os
import sys
import json
import asyncio
from typing import Any, Sequence
import snowflake.connector
from snowflake.connector import DictCursor

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: mcp 패키지가 설치되지 않았습니다. 'pip install mcp'를 실행하세요.", file=sys.stderr)
    sys.exit(1)


# 전역 연결 변수
_connection = None


def get_connection():
    """Snowflake 연결 생성"""
    global _connection
    if _connection is None or _connection.is_closed():
        try:
            _connection = snowflake.connector.connect(
                user=os.getenv('SNOWFLAKE_USER'),
                password=os.getenv('SNOWFLAKE_PASSWORD'),
                account=os.getenv('SNOWFLAKE_ACCOUNT'),
                warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'DEV_WH'),
                database=os.getenv('SNOWFLAKE_DATABASE', 'FNF'),
                schema=os.getenv('SNOWFLAKE_SCHEMA', 'SAP_FNF'),
                role=os.getenv('SNOWFLAKE_ROLE', 'PU_SQL_SAP')
            )
        except Exception as e:
            raise ConnectionError(f"Snowflake 연결 실패: {str(e)}")
    return _connection


# MCP 서버 생성
server = Server("snowflake-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """사용 가능한 도구 목록 반환"""
    return [
        Tool(
            name="execute_query",
            description="Snowflake SQL 쿼리를 실행하고 결과를 반환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "실행할 SQL 쿼리"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_tables",
            description="현재 데이터베이스와 스키마의 테이블 목록을 반환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "데이터베이스 이름 (선택사항, 기본값: 환경변수 값)"
                    },
                    "schema": {
                        "type": "string",
                        "description": "스키마 이름 (선택사항, 기본값: 환경변수 값)"
                    }
                }
            }
        ),
        Tool(
            name="describe_table",
            description="테이블의 구조(컬럼 정보)를 반환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "테이블 이름"
                    },
                    "database": {
                        "type": "string",
                        "description": "데이터베이스 이름 (선택사항)"
                    },
                    "schema": {
                        "type": "string",
                        "description": "스키마 이름 (선택사항)"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="test_connection",
            description="Snowflake 연결을 테스트합니다.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """도구 호출 처리"""
    try:
        if name == "test_connection":
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION(), CURRENT_USER(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
            result = cursor.fetchone()
            cursor.close()
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "message": "연결 성공",
                    "version": result[0],
                    "user": result[1],
                    "database": result[2],
                    "schema": result[3]
                }, ensure_ascii=False, indent=2)
            )]
        
        elif name == "execute_query":
            query = arguments.get("query")
            if not query:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "쿼리가 제공되지 않았습니다."}, ensure_ascii=False)
                )]
            
            conn = get_connection()
            cursor = conn.cursor(DictCursor)
            cursor.execute(query)
            
            # 결과 가져오기
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            
            result = {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows)
            }
            
            cursor.close()
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2, default=str)
            )]
        
        elif name == "list_tables":
            database = arguments.get("database") or os.getenv('SNOWFLAKE_DATABASE', 'FNF')
            schema = arguments.get("schema") or os.getenv('SNOWFLAKE_SCHEMA', 'SAP_FNF')
            
            conn = get_connection()
            cursor = conn.cursor(DictCursor)
            cursor.execute(f"""
                SELECT TABLE_NAME, TABLE_TYPE, CREATED, LAST_ALTERED
                FROM {database}.INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = '{schema}'
                ORDER BY TABLE_NAME
            """)
            tables = cursor.fetchall()
            cursor.close()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "database": database,
                    "schema": schema,
                    "tables": tables,
                    "count": len(tables)
                }, ensure_ascii=False, indent=2, default=str)
            )]
        
        elif name == "describe_table":
            table_name = arguments.get("table_name")
            database = arguments.get("database") or os.getenv('SNOWFLAKE_DATABASE', 'FNF')
            schema = arguments.get("schema") or os.getenv('SNOWFLAKE_SCHEMA', 'SAP_FNF')
            
            conn = get_connection()
            cursor = conn.cursor(DictCursor)
            cursor.execute(f"""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    COMMENT
                FROM {database}.INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """)
            columns = cursor.fetchall()
            cursor.close()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "table": f"{database}.{schema}.{table_name}",
                    "columns": columns,
                    "column_count": len(columns)
                }, ensure_ascii=False, indent=2, default=str)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"알 수 없는 도구: {name}"}, ensure_ascii=False)
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, ensure_ascii=False)
        )]


async def run_server():
    """서버 실행"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """메인 함수"""
    # 환경 변수 확인
    required_vars = ['SNOWFLAKE_ACCOUNT', 'SNOWFLAKE_USER', 'SNOWFLAKE_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: 다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}", file=sys.stderr)
        sys.exit(1)
    
    asyncio.run(run_server())


if __name__ == "__main__":
    main()

