"""
F&F 실적 대시보드 HTML 생성기
Streamlit 대시보드와 유사한 레이아웃의 HTML 파일을 생성합니다.
"""

import json
from datetime import datetime
from pathlib import Path


def format_currency(value, unit="원"):
    """금액을 한국어 형식으로 포맷팅"""
    if value is None:
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


def generate_metric_card(item):
    """재무 지표 카드 HTML 생성"""
    name = item.get('항목', '')
    value = item.get('값', 0)
    unit = item.get('단위', '')
    change = item.get('변동률', None)
    
    formatted_value = format_currency(value, unit) if unit == "원" else f"{value:,.1f} {unit}"
    
    change_html = ""
    if change is not None:
        change_class = "positive-change" if change >= 0 else "negative-change"
        change_icon = "↑" if change >= 0 else "↓"
        change_html = f'<div class="metric-change {change_class}">{change_icon} {abs(change):.1f}% 전년 대비</div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{name}</div>
        <div class="metric-value">{formatted_value}</div>
        {change_html}
    </div>
    """


def generate_summary_tab(data):
    """전체 요약 탭 HTML 생성"""
    summary_data = data.get('summary', [])
    
    if not summary_data:
        return "<p>요약 데이터가 없습니다.</p>"
    
    # 주요 지표 카드
    cards_html = ""
    for item in summary_data[:6]:
        cards_html += generate_metric_card(item)
    
    # 차트 데이터 준비
    chart_labels = [item.get('항목', '') for item in summary_data]
    chart_values = [item.get('값', 0) for item in summary_data]
    chart_changes = [item.get('변동률', 0) for item in summary_data]
    
    # 테이블 생성
    table_rows = ""
    for item in summary_data:
        name = item.get('항목', '')
        value = item.get('값', 0)
        unit = item.get('단위', '')
        change = item.get('변동률', None)
        
        formatted_value = format_currency(value, unit) if unit == "원" else f"{value:,.1f} {unit}"
        change_str = f"{change:+.1f}%" if change is not None else "-"
        change_class = "positive-change" if (change is not None and change >= 0) else "negative-change"
        
        table_rows += f"""
        <tr>
            <td>{name}</td>
            <td>{formatted_value}</td>
            <td class="{change_class}">{change_str}</td>
        </tr>
        """
    
    return f"""
    <div class="tab-content active" id="summary-tab">
        <h2>주요 재무 지표</h2>
        <div class="metrics-grid">
            {cards_html}
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <h3>주요 지표 비교</h3>
                <canvas id="summaryChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>변동률</h3>
                <canvas id="changeChart"></canvas>
            </div>
        </div>
        
        <h2>상세 내역</h2>
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>항목</th>
                        <th>값</th>
                        <th>변동률</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </div>
    """


def generate_income_statement_tab(data):
    """손익계산서 탭 HTML 생성"""
    income_data = data.get('income_statement', [])
    
    if not income_data:
        return "<p>손익계산서 데이터가 없습니다.</p>"
    
    # 연도 추출
    years = []
    for item in income_data:
        for key in item.keys():
            if key != '항목' and '년' in str(key):
                if key not in years:
                    years.append(key)
    years = sorted(years, reverse=True)
    
    # 테이블 생성
    table_rows = ""
    for item in income_data:
        name = item.get('항목', '')
        table_rows += "<tr>"
        table_rows += f"<td>{name}</td>"
        for year in years:
            value = item.get(year, 0)
            formatted_value = format_currency(value, '원')
            table_rows += f"<td>{formatted_value}</td>"
        table_rows += "</tr>"
    
    # 차트 데이터 준비
    chart_data = {}
    for item in income_data:
        name = item.get('항목', '')
        chart_data[name] = [item.get(year, 0) for year in years]
    
    # 주요 항목 트렌드 데이터
    main_items = ['매출액', '영업이익', '순이익']
    trend_data = {item: chart_data.get(item, []) for item in main_items if item in chart_data}
    
    return f"""
    <div class="tab-content" id="income-tab">
        <h2>손익계산서</h2>
        
        <div class="charts-section">
            <div class="chart-container">
                <h3>연도별 비교</h3>
                <canvas id="incomeChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>주요 항목 트렌드</h3>
                <canvas id="incomeTrendChart"></canvas>
            </div>
        </div>
        
        <h2>상세 내역</h2>
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>항목</th>
                        {' '.join([f'<th>{year}</th>' for year in years])}
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </div>
    """


def generate_balance_sheet_tab(data):
    """재무상태표 탭 HTML 생성"""
    balance_data = data.get('balance_sheet', [])
    
    if not balance_data:
        return "<p>재무상태표 데이터가 없습니다.</p>"
    
    # 분류별 집계
    categories = {}
    for item in balance_data:
        category = item.get('분류', '기타')
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    # 분류별 총액 계산
    category_totals = {}
    for category, items in categories.items():
        category_totals[category] = sum([item.get('값', 0) for item in items])
    
    # 테이블 생성
    table_rows = ""
    for item in balance_data:
        name = item.get('항목', '')
        value = item.get('값', 0)
        category = item.get('분류', '')
        formatted_value = format_currency(value, '원')
        table_rows += f"""
        <tr>
            <td>{name}</td>
            <td>{formatted_value}</td>
            <td>{category}</td>
        </tr>
        """
    
    return f"""
    <div class="tab-content" id="balance-tab">
        <h2>재무상태표</h2>
        
        <div class="balance-overview">
            {''.join([f'''
            <div class="balance-item">
                <h3>{category}</h3>
                <div class="balance-value">{format_currency(total, '원')}</div>
            </div>
            ''' for category, total in category_totals.items()])}
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <h3>분류별 구성</h3>
                <canvas id="balancePieChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>분류별 금액</h3>
                <canvas id="balanceBarChart"></canvas>
            </div>
        </div>
        
        <h2>상세 내역</h2>
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>항목</th>
                        <th>금액</th>
                        <th>분류</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </div>
    """


def generate_html(data, output_file='dashboard_preview.html'):
    """전체 HTML 대시보드 생성"""
    
    summary_tab = generate_summary_tab(data)
    income_tab = generate_income_statement_tab(data)
    balance_tab = generate_balance_sheet_tab(data)
    
    # 차트 데이터 준비
    summary_data = data.get('summary', [])
    income_data = data.get('income_statement', [])
    balance_data = data.get('balance_sheet', [])
    
    # Chart.js 데이터
    summary_labels = json.dumps([item.get('항목', '') for item in summary_data], ensure_ascii=False)
    summary_values = json.dumps([item.get('값', 0) for item in summary_data], ensure_ascii=False)
    summary_changes = json.dumps([item.get('변동률', 0) for item in summary_data], ensure_ascii=False)
    
    # 손익계산서 차트 데이터
    years = []
    for item in income_data:
        for key in item.keys():
            if key != '항목' and '년' in str(key):
                if key not in years:
                    years.append(key)
    years = sorted(years, reverse=True)
    years_json = json.dumps(years, ensure_ascii=False)
    
    # 손익계산서 전체 데이터셋
    income_all_datasets = []
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22']
    for idx, item in enumerate(income_data):
        item_name = item.get('항목', '')
        values = [item.get(year, 0) for year in years]
        income_all_datasets.append({
            'label': item_name,
            'data': values,
            'borderColor': colors[idx % len(colors)],
            'backgroundColor': colors[idx % len(colors)] + '40'
        })
    income_all_datasets_json = json.dumps(income_all_datasets, ensure_ascii=False)
    
    # 트렌드 차트용 (주요 항목만)
    income_datasets = []
    main_items = ['매출액', '영업이익', '순이익']
    trend_colors = ['#3498db', '#2ecc71', '#e74c3c']
    for idx, item_name in enumerate(main_items):
        item_data = next((item for item in income_data if item.get('항목') == item_name), None)
        if item_data:
            values = [item_data.get(year, 0) for year in years]
            income_datasets.append({
                'label': item_name,
                'data': values,
                'borderColor': trend_colors[idx % len(trend_colors)],
                'backgroundColor': trend_colors[idx % len(trend_colors)] + '40'
            })
    income_datasets_json = json.dumps(income_datasets, ensure_ascii=False)
    
    # 재무상태표 차트 데이터
    categories = {}
    for item in balance_data:
        category = item.get('분류', '기타')
        if category not in categories:
            categories[category] = 0
        categories[category] += item.get('값', 0)
    
    balance_labels = json.dumps(list(categories.keys()), ensure_ascii=False)
    balance_values = json.dumps(list(categories.values()), ensure_ascii=False)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>F&F 실적 대시보드 미리보기</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .main-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            color: white;
            text-align: center;
        }}
        
        .main-header h1 {{
            font-size: 2.5em;
            margin-bottom: 0.5rem;
        }}
        
        .main-header p {{
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
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        
        .metric-label {{
            font-size: 0.9rem;
            color: #6c757d;
            margin-bottom: 0.5rem;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 0.5rem;
        }}
        
        .metric-change {{
            font-size: 0.9rem;
        }}
        
        .positive-change {{
            color: #2ecc71;
        }}
        
        .negative-change {{
            color: #e74c3c;
        }}
        
        .charts-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }}
        
        .chart-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }}
        
        .chart-container h3 {{
            margin-bottom: 15px;
            color: #495057;
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
            
            .charts-section {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="main-header">
            <h1>📊 F&F 실적 대시보드</h1>
            <p>실시간 재무 실적 모니터링</p>
            <p style="font-size: 0.9em; margin-top: 10px;">생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
        </div>
        
        <div class="tabs">
            <button class="tab-button active" onclick="showTab('summary')">📈 전체 요약</button>
            <button class="tab-button" onclick="showTab('income')">💰 손익계산서</button>
            <button class="tab-button" onclick="showTab('balance')">🏦 재무상태표</button>
        </div>
        
        {summary_tab}
        {income_tab}
        {balance_tab}
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
            document.getElementById(tabName + '-tab').classList.add('active');
            
            // 차트 재생성
            initCharts();
        }}
        
        function initCharts() {{
            // 전체 요약 차트
            const summaryCtx = document.getElementById('summaryChart');
            if (summaryCtx && !summaryCtx.chart) {{
                summaryCtx.chart = new Chart(summaryCtx, {{
                    type: 'bar',
                    data: {{
                        labels: {summary_labels},
                        datasets: [{{
                            label: '값',
                            data: {summary_values},
                            backgroundColor: 'rgba(102, 126, 234, 0.6)',
                            borderColor: 'rgba(102, 126, 234, 1)',
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}
            
            // 변동률 차트
            const changeCtx = document.getElementById('changeChart');
            if (changeCtx && !changeCtx.chart) {{
                changeCtx.chart = new Chart(changeCtx, {{
                    type: 'bar',
                    data: {{
                        labels: {summary_labels},
                        datasets: [{{
                            label: '변동률 (%)',
                            data: {summary_changes},
                            backgroundColor: function(context) {{
                                const value = context.parsed.y;
                                return value >= 0 ? 'rgba(46, 204, 113, 0.6)' : 'rgba(231, 76, 60, 0.6)';
                            }},
                            borderColor: function(context) {{
                                const value = context.parsed.y;
                                return value >= 0 ? 'rgba(46, 204, 113, 1)' : 'rgba(231, 76, 60, 1)';
                            }},
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}
            
            // 손익계산서 차트
            const incomeCtx = document.getElementById('incomeChart');
            if (incomeCtx && !incomeCtx.chart) {{
                incomeCtx.chart = new Chart(incomeCtx, {{
                    type: 'bar',
                    data: {{
                        labels: {years_json},
                        datasets: {income_all_datasets_json}
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}
            
            // 손익계산서 트렌드 차트
            const trendCtx = document.getElementById('incomeTrendChart');
            if (trendCtx && !trendCtx.chart) {{
                trendCtx.chart = new Chart(trendCtx, {{
                    type: 'line',
                    data: {{
                        labels: {years_json},
                        datasets: {income_datasets_json}
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}
            
            // 재무상태표 파이 차트
            const pieCtx = document.getElementById('balancePieChart');
            if (pieCtx && !pieCtx.chart) {{
                pieCtx.chart = new Chart(pieCtx, {{
                    type: 'pie',
                    data: {{
                        labels: {balance_labels},
                        datasets: [{{
                            data: {balance_values},
                            backgroundColor: [
                                'rgba(102, 126, 234, 0.6)',
                                'rgba(46, 204, 113, 0.6)',
                                'rgba(231, 76, 60, 0.6)',
                                'rgba(243, 156, 18, 0.6)',
                                'rgba(155, 89, 182, 0.6)'
                            ],
                            borderColor: [
                                'rgba(102, 126, 234, 1)',
                                'rgba(46, 204, 113, 1)',
                                'rgba(231, 76, 60, 1)',
                                'rgba(243, 156, 18, 1)',
                                'rgba(155, 89, 182, 1)'
                            ],
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: false
                            }}
                        }}
                    }}
                }});
            }}
            
            // 재무상태표 바 차트
            const barCtx = document.getElementById('balanceBarChart');
            if (barCtx && !barCtx.chart) {{
                barCtx.chart = new Chart(barCtx, {{
                    type: 'bar',
                    data: {{
                        labels: {balance_labels},
                        datasets: [{{
                            label: '금액',
                            data: {balance_values},
                            backgroundColor: 'rgba(102, 126, 234, 0.6)',
                            borderColor: 'rgba(102, 126, 234, 1)',
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}
        }}
        
        // 페이지 로드 시 차트 초기화
        document.addEventListener('DOMContentLoaded', function() {{
            initCharts();
        }});
    </script>
</body>
</html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 대시보드 HTML 파일이 생성되었습니다: {output_file}")
    return output_file


if __name__ == "__main__":
    # 샘플 데이터 로드
    data_file = 'sample_data.json'
    
    if Path(data_file).exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        generate_html(data, 'dashboard_preview.html')
        print("\n📂 브라우저에서 dashboard_preview.html 파일을 열어 확인하세요!")
    else:
        print(f"❌ 오류: {data_file} 파일을 찾을 수 없습니다.")

