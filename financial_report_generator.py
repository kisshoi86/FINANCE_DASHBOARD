"""
재무실적보고서 HTML 생성기
전체요약, 손익계산서, 재무상태표를 포함한 HTML 보고서를 생성합니다.
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path


class FinancialReportGenerator:
    """재무실적보고서 HTML 생성 클래스"""
    
    def __init__(self, data_file=None, data_dict=None):
        """
        Args:
            data_file: JSON 또는 Excel 파일 경로
            data_dict: 직접 데이터 딕셔너리 전달
        """
        if data_file:
            self.data = self._load_data(data_file)
        elif data_dict:
            self.data = data_dict
        else:
            raise ValueError("data_file 또는 data_dict 중 하나를 제공해야 합니다.")
        
        self.report_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    def _load_data(self, file_path):
        """데이터 파일 로드"""
        path = Path(file_path)
        if path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif path.suffix in ['.xlsx', '.xls']:
            # Excel 파일에서 여러 시트 읽기
            excel_data = pd.read_excel(file_path, sheet_name=None)
            return {
                'summary': excel_data.get('전체요약', pd.DataFrame()).to_dict('records'),
                'income_statement': excel_data.get('손익계산서', pd.DataFrame()).to_dict('records'),
                'balance_sheet': excel_data.get('재무상태표', pd.DataFrame()).to_dict('records')
            }
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {path.suffix}")
    
    def _generate_summary_tab(self):
        """전체요약 탭 HTML 생성"""
        summary_data = self.data.get('summary', [])
        
        if not summary_data:
            return "<p>요약 데이터가 없습니다.</p>"
        
        # 주요 지표 카드 생성
        cards_html = ""
        for item in summary_data[:6]:  # 상위 6개 지표
            name = item.get('항목', item.get('name', ''))
            value = item.get('값', item.get('value', 0))
            unit = item.get('단위', item.get('unit', ''))
            change = item.get('변동률', item.get('change', 0))
            
            change_class = "positive" if change >= 0 else "negative"
            change_icon = "↑" if change >= 0 else "↓"
            
            cards_html += f"""
            <div class="metric-card">
                <div class="metric-name">{name}</div>
                <div class="metric-value">{self._format_number(value)} {unit}</div>
                <div class="metric-change {change_class}">
                    {change_icon} {abs(change):.1f}%
                </div>
            </div>
            """
        
        # 차트 데이터 준비
        chart_data = summary_data[:10]  # 상위 10개 지표
        chart_labels = [item.get('항목', item.get('name', '')) for item in chart_data]
        chart_values = [item.get('값', item.get('value', 0)) for item in chart_data]
        
        return f"""
        <div class="summary-container">
            <h2>주요 재무 지표</h2>
            <div class="metrics-grid">
                {cards_html}
            </div>
            
            <h2>주요 지표 비교</h2>
            <div class="chart-container">
                <canvas id="summaryChart"></canvas>
            </div>
            
            <h2>요약 테이블</h2>
            <div class="table-container">
                {self._generate_table(summary_data)}
            </div>
        </div>
        """
    
    def _generate_income_statement_tab(self):
        """손익계산서 탭 HTML 생성"""
        income_data = self.data.get('income_statement', [])
        
        if not income_data:
            return "<p>손익계산서 데이터가 없습니다.</p>"
        
        # 연도별 데이터 추출
        years = self._extract_years(income_data)
        
        # 차트 데이터 준비
        chart_html = self._generate_comparison_chart(income_data, years, "손익계산서")
        
        return f"""
        <div class="income-statement-container">
            <h2>손익계산서</h2>
            {chart_html}
            
            <h2>상세 내역</h2>
            <div class="table-container">
                {self._generate_table(income_data)}
            </div>
            
            <h2>트렌드 분석</h2>
            <div class="chart-container">
                <canvas id="incomeTrendChart"></canvas>
            </div>
        </div>
        """
    
    def _generate_balance_sheet_tab(self):
        """재무상태표 탭 HTML 생성"""
        balance_data = self.data.get('balance_sheet', [])
        
        if not balance_data:
            return "<p>재무상태표 데이터가 없습니다.</p>"
        
        # 자산/부채/자본 분류
        assets = [item for item in balance_data if '자산' in str(item.get('항목', item.get('name', '')))]
        liabilities = [item for item in balance_data if '부채' in str(item.get('항목', item.get('name', '')))]
        equity = [item for item in balance_data if '자본' in str(item.get('항목', item.get('name', '')))]
        
        # 차트 데이터 준비
        chart_html = self._generate_balance_chart(assets, liabilities, equity)
        
        return f"""
        <div class="balance-sheet-container">
            <h2>재무상태표</h2>
            {chart_html}
            
            <h2>상세 내역</h2>
            <div class="table-container">
                {self._generate_table(balance_data)}
            </div>
            
            <h2>구성 비율</h2>
            <div class="chart-container">
                <canvas id="balancePieChart"></canvas>
            </div>
        </div>
        """
    
    def _extract_years(self, data):
        """데이터에서 연도 추출"""
        years = set()
        for item in data:
            for key in item.keys():
                if isinstance(key, str) and key.replace('년', '').replace(' ', '').isdigit():
                    years.add(key)
                elif isinstance(key, (int, float)) or (isinstance(key, str) and key.isdigit()):
                    years.add(str(key))
        return sorted(list(years), reverse=True)[:5]  # 최근 5년
    
    def _generate_table(self, data):
        """데이터를 HTML 테이블로 변환"""
        if not data:
            return "<p>데이터가 없습니다.</p>"
        
        # 헤더 생성
        headers = list(data[0].keys())
        header_html = "<thead><tr>" + "".join([f"<th>{h}</th>" for h in headers]) + "</tr></thead>"
        
        # 바디 생성
        body_html = "<tbody>"
        for row in data:
            body_html += "<tr>"
            for header in headers:
                value = row.get(header, '')
                if isinstance(value, (int, float)):
                    value = self._format_number(value)
                body_html += f"<td>{value}</td>"
            body_html += "</tr>"
        body_html += "</tbody>"
        
        return f"<table class='data-table'>{header_html}{body_html}</table>"
    
    def _generate_comparison_chart(self, data, years, title):
        """비교 차트 생성"""
        if not years:
            return ""
        
        chart_data = {}
        for item in data:
            name = item.get('항목', item.get('name', ''))
            chart_data[name] = []
            for year in years:
                value = item.get(year, item.get(str(year), 0))
                if isinstance(value, str):
                    value = value.replace(',', '').replace('원', '').strip()
                    try:
                        value = float(value)
                    except:
                        value = 0
                chart_data[name].append(value)
        
        # Chart.js 데이터 형식으로 변환
        datasets = []
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
        for i, (name, values) in enumerate(chart_data.items()):
            datasets.append({
                'label': name,
                'data': values,
                'borderColor': colors[i % len(colors)],
                'backgroundColor': colors[i % len(colors)] + '40'
            })
        
        datasets_json = json.dumps(datasets, ensure_ascii=False)
        years_json = json.dumps(years, ensure_ascii=False)
        
        return f"""
        <div class="chart-container">
            <canvas id="{title}Chart"></canvas>
            <script>
                const ctx = document.getElementById('{title}Chart').getContext('2d');
                new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: {years_json},
                        datasets: {datasets_json}
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: true,
                                text: '{title}'
                            }},
                            legend: {{
                                display: true
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            </script>
        </div>
        """
    
    def _generate_balance_chart(self, assets, liabilities, equity):
        """재무상태표 차트 생성"""
        total_assets = sum([item.get('값', item.get('value', 0)) for item in assets])
        total_liabilities = sum([item.get('값', item.get('value', 0)) for item in liabilities])
        total_equity = sum([item.get('값', item.get('value', 0)) for item in equity])
        
        return f"""
        <div class="balance-overview">
            <div class="balance-item">
                <h3>총 자산</h3>
                <div class="balance-value">{self._format_number(total_assets)}</div>
            </div>
            <div class="balance-item">
                <h3>총 부채</h3>
                <div class="balance-value">{self._format_number(total_liabilities)}</div>
            </div>
            <div class="balance-item">
                <h3>총 자본</h3>
                <div class="balance-value">{self._format_number(total_equity)}</div>
            </div>
        </div>
        """
    
    def _format_number(self, value):
        """숫자 포맷팅"""
        if isinstance(value, str):
            try:
                value = float(value.replace(',', '').replace('원', '').strip())
            except:
                return value
        
        if abs(value) >= 1000000000000:  # 조
            return f"{value/1000000000000:.2f}조"
        elif abs(value) >= 100000000:  # 억
            return f"{value/100000000:.2f}억"
        elif abs(value) >= 10000:  # 만
            return f"{value/10000:.2f}만"
        else:
            return f"{value:,.0f}"
    
    def generate_html(self, output_file='financial_report.html'):
        """전체 HTML 보고서 생성"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>재무실적보고서</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .tabs {{
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .tab-button {{
            flex: 1;
            padding: 20px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 600;
            color: #6c757d;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }}
        
        .tab-button:hover {{
            background: #e9ecef;
            color: #495057;
        }}
        
        .tab-button.active {{
            color: #667eea;
            border-bottom-color: #667eea;
            background: white;
        }}
        
        .tab-content {{
            display: none;
            padding: 30px;
            animation: fadeIn 0.5s;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-name {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        
        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .metric-change {{
            font-size: 0.9em;
        }}
        
        .metric-change.positive {{
            color: #2ecc71;
        }}
        
        .metric-change.negative {{
            color: #e74c3c;
        }}
        
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .table-container {{
            overflow-x: auto;
            margin: 30px 0;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .data-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        .data-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .data-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .balance-overview {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .balance-item {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        
        .balance-item h3 {{
            color: #6c757d;
            margin-bottom: 10px;
            font-size: 1em;
        }}
        
        .balance-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #495057;
        }}
        
        h2 {{
            color: #495057;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        @media (max-width: 768px) {{
            .tabs {{
                flex-direction: column;
            }}
            
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>재무실적보고서</h1>
            <p>보고서 작성일: {self.report_date}</p>
        </div>
        
        <div class="tabs">
            <button class="tab-button active" onclick="showTab('summary')">전체요약</button>
            <button class="tab-button" onclick="showTab('income')">손익계산서</button>
            <button class="tab-button" onclick="showTab('balance')">재무상태표</button>
        </div>
        
        <div id="summary" class="tab-content active">
            {self._generate_summary_tab()}
        </div>
        
        <div id="income" class="tab-content">
            {self._generate_income_statement_tab()}
        </div>
        
        <div id="balance" class="tab-content">
            {self._generate_balance_sheet_tab()}
        </div>
    </div>
    
    <script>
        function showTab(tabName) {{
            // 모든 탭 버튼과 콘텐츠 숨기기
            document.querySelectorAll('.tab-button').forEach(btn => {{
                btn.classList.remove('active');
            }});
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            
            // 선택된 탭 활성화
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }}
        
        // 차트 초기화 (데이터가 있는 경우)
        document.addEventListener('DOMContentLoaded', function() {{
            // 여기에 추가 차트 초기화 코드를 넣을 수 있습니다
        }});
    </script>
</body>
</html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"보고서가 생성되었습니다: {output_file}")
        return output_file


if __name__ == "__main__":
    # 샘플 데이터 예시
    sample_data = {
        'summary': [
            {'항목': '매출액', '값': 1000000000000, '단위': '원', '변동률': 5.2},
            {'항목': '영업이익', '값': 150000000000, '단위': '원', '변동률': 8.3},
            {'항목': '순이익', '값': 120000000000, '단위': '원', '변동률': 6.1},
            {'항목': '총자산', '값': 5000000000000, '단위': '원', '변동률': 3.5},
            {'항목': '부채비율', '값': 45.2, '단위': '%', '변동률': -2.1},
            {'항목': 'ROE', '값': 12.5, '단위': '%', '변동률': 1.2}
        ],
        'income_statement': [
            {'항목': '매출액', '2024년': 1000000000000, '2023년': 950000000000, '2022년': 900000000000},
            {'항목': '매출원가', '2024년': 600000000000, '2023년': 570000000000, '2022년': 540000000000},
            {'항목': '판매비와관리비', '2024년': 250000000000, '2023년': 240000000000, '2022년': 230000000000},
            {'항목': '영업이익', '2024년': 150000000000, '2023년': 140000000000, '2022년': 130000000000},
            {'항목': '순이익', '2024년': 120000000000, '2023년': 113000000000, '2022년': 105000000000}
        ],
        'balance_sheet': [
            {'항목': '현금 및 현금성자산', '값': 500000000000},
            {'항목': '매출채권', '값': 300000000000},
            {'항목': '재고자산', '값': 200000000000},
            {'항목': '유형자산', '값': 4000000000000},
            {'항목': '단기차입금', '값': 200000000000},
            {'항목': '매입채무', '값': 150000000000},
            {'항목': '장기차입금', '값': 1800000000000},
            {'항목': '자본금', '값': 500000000000},
            {'항목': '이익잉여금', '값': 2150000000000}
        ]
    }
    
    # 보고서 생성
    generator = FinancialReportGenerator(data_dict=sample_data)
    generator.generate_html('financial_report.html')










