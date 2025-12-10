-- F&F 실적 대시보드용 샘플 쿼리
-- 실제 테이블 구조에 맞게 수정하여 dashboard.py에 적용하세요

-- ============================================
-- 1. 주요 재무 지표 요약 (load_financial_summary)
-- ============================================

-- 예시 1: 단일 테이블에서 주요 지표 조회
SELECT 
    지표명 as 항목,
    금액 as 값,
    단위,
    변동률
FROM FNF.SAP_FNF.재무지표마스터
WHERE 기준일자 = CURRENT_DATE()
ORDER BY 표시순서;

-- 예시 2: 여러 테이블에서 집계하여 지표 생성
SELECT 
    '매출액' as 항목,
    SUM(매출금액) as 값,
    '원' as 단위,
    ((SUM(매출금액) - LAG(SUM(매출금액)) OVER (ORDER BY 기준일자)) / LAG(SUM(매출금액)) OVER (ORDER BY 기준일자) * 100) as 변동률
FROM FNF.SAP_FNF.매출테이블
WHERE 기준일자 = CURRENT_DATE()
GROUP BY 기준일자;

-- ============================================
-- 2. 손익계산서 (load_income_statement)
-- ============================================

-- 예시 1: 연도별 손익계산서 데이터
SELECT 
    계정과목코드 as 항목코드,
    계정과목명 as 항목,
    연도,
    금액
FROM FNF.SAP_FNF.손익계산서
WHERE 연도 >= YEAR(CURRENT_DATE()) - 2
ORDER BY 연도 DESC, 계정과목코드;

-- 예시 2: 계층 구조가 있는 경우
SELECT 
    계정과목명 as 항목,
    연도,
    SUM(금액) as 금액
FROM FNF.SAP_FNF.손익계산서상세
WHERE 연도 >= YEAR(CURRENT_DATE()) - 2
    AND 계정레벨 = 1  -- 최상위 레벨만
GROUP BY 계정과목명, 연도
ORDER BY 연도 DESC, 계정과목명;

-- ============================================
-- 3. 재무상태표 (load_balance_sheet)
-- ============================================

-- 예시 1: 기준일자별 재무상태표
SELECT 
    계정과목명 as 항목,
    금액 as 값,
    CASE 
        WHEN 계정구분 = 'A' THEN '자산'
        WHEN 계정구분 = 'L' THEN '부채'
        WHEN 계정구분 = 'E' THEN '자본'
        ELSE '기타'
    END as 분류
FROM FNF.SAP_FNF.재무상태표
WHERE 기준일자 = CURRENT_DATE()
ORDER BY 계정구분, 계정과목코드;

-- 예시 2: 분류별 집계
SELECT 
    계정과목명 as 항목,
    SUM(금액) as 값,
    대분류 as 분류
FROM FNF.SAP_FNF.재무상태표상세
WHERE 기준일자 = CURRENT_DATE()
GROUP BY 계정과목명, 대분류
ORDER BY 대분류, 계정과목명;

-- ============================================
-- 4. 추가 분석 쿼리 예시
-- ============================================

-- 월별 매출 추이
SELECT 
    TO_CHAR(매출일자, 'YYYY-MM') as 월,
    SUM(매출금액) as 매출액
FROM FNF.SAP_FNF.매출테이블
WHERE 매출일자 >= DATEADD(MONTH, -12, CURRENT_DATE())
GROUP BY TO_CHAR(매출일자, 'YYYY-MM')
ORDER BY 월;

-- 부서별 실적
SELECT 
    부서코드,
    부서명,
    SUM(매출금액) as 매출액,
    SUM(영업이익) as 영업이익
FROM FNF.SAP_FNF.부서별실적
WHERE 기준연도 = YEAR(CURRENT_DATE())
GROUP BY 부서코드, 부서명
ORDER BY 매출액 DESC;

-- 제품별 매출 Top 10
SELECT 
    제품코드,
    제품명,
    SUM(매출금액) as 매출액,
    SUM(판매수량) as 판매수량
FROM FNF.SAP_FNF.제품별매출
WHERE 기준연도 = YEAR(CURRENT_DATE())
GROUP BY 제품코드, 제품명
ORDER BY 매출액 DESC
LIMIT 10;

-- ============================================
-- 5. 테이블 구조 확인 쿼리
-- ============================================

-- 모든 테이블 목록
SELECT 
    TABLE_NAME,
    TABLE_TYPE,
    CREATED,
    LAST_ALTERED
FROM FNF.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SAP_FNF'
ORDER BY TABLE_NAME;

-- 특정 테이블의 컬럼 정보
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COMMENT
FROM FNF.INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'SAP_FNF' 
    AND TABLE_NAME = '테이블명'
ORDER BY ORDINAL_POSITION;

-- 테이블의 샘플 데이터 확인 (최대 10개)
SELECT *
FROM FNF.SAP_FNF.테이블명
LIMIT 10;








