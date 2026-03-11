"""
Snowflake Data Agent for Card Spend Analysis
Reads card spend data, performs transformations (14-day MA, YoY), 
and generates an HTML dashboard
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
from snowflake.snowpark import Session
from cryptography.hazmat.primitives import serialization
import warnings

warnings.filterwarnings('ignore')



class SnowflakeCardSpendAgent:
    """Agent for fetching transformed data and producing a weekly YoY dashboard."""

    def __init__(self, config_path: Optional[str] = None):
        # rely on shared utility to create a session using rsa_key.p8 and credentials_sf.json
        from snowpark_utils import get_session

        self.session = get_session(json_path=config_path or "credentials_sf.json")
        # use the table specified by the user
        self.source_table = "AGENT.ARBITER.TRANSFORM"

    def fetch_data(self, days_back: int = 90) -> pd.DataFrame:
        """Pull the most recent *days_back* of records from the source table."""
        print(f"\n📖 querying {self.source_table} for last {days_back} days")
        sql = (
            f"SELECT * FROM {self.source_table} "
            f"WHERE DATE >= CURRENT_DATE() - {days_back}"
        )
        snowpark_df = self.session.sql(sql)
        # collect rows and convert to pandas locally
        rows = snowpark_df.collect()
        df = pd.DataFrame([r.asDict() for r in rows])
        if not df.empty:
            df['DATE'] = pd.to_datetime(df['DATE'])
        print(f"  rows: {len(df):,}, columns: {list(df.columns)}")
        return df

    def _weekly_yoy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate the YOY percent‑change column to weekly frequency."""
        # week-ending date (Monday) to bucket the data
        df['WEEK_END'] = df['DATE'] - pd.to_timedelta(df['DATE'].dt.weekday, unit='d')
        weekly = (
            df.groupby(['WEEK_END', 'TICKER', 'EXCHANGE'])['YOY_PCT_CHANGE']
              .mean()
              .reset_index()
        )
        return weekly

    def generate_dashboard(self, output_path: str = "yoY_dashboard.html", exclude_tickers: list[str] | None = None) -> str:
        """Fetch, transform and write an HTML table.

        Args:
            output_path: file to write
            exclude_tickers: optional list of TICKER values to omit from display
        """
        df = self.fetch_data()
        # drop unwanted tickers early
        if exclude_tickers:
            df = df[~df['TICKER'].isin(exclude_tickers)]
        weekly = self._weekly_yoy(df)

        # determine which weekly dates to show (past 3 months on 7‑day spacing)
        latest = weekly['WEEK_END'].max()
        dates = [latest - pd.Timedelta(days=7 * i) for i in range(12, -1, -1)]
        dates = [d for d in dates if d in weekly['WEEK_END'].unique()]

        # pivot the table using the already‑computed YOY percentage
        pivot = weekly.pivot_table(
            index=['TICKER', 'EXCHANGE'],
            columns='WEEK_END',
            values='YOY_PCT_CHANGE'
        )
        pivot = pivot.reindex(columns=dates)

        # sort by latest YoY descending
        pivot = pivot.sort_values(by=dates[-1], ascending=False, na_position='last')

        # compute trend column with color coding for positive/negative + accelerating/decelerating
        def label_trend(row):
            vals = row.dropna().values
            if len(vals) < 2:
                return ('', '#666')
            current, prev = vals[-1], vals[-2]
            abs_diff = abs(current - prev)
            
            if abs_diff <= 3:
                return ('Unchanged', '#2196f3')  # blue for unchanged
            
            abs_trend = abs(current) - abs(prev)
            is_accelerating = abs_trend > 0
            
            # Determine color based on sign and trend direction
            if current >= 0:  # Positive YoY
                color = '#4caf50' if is_accelerating else '#9fd99f'  # bright green or light green
            else:  # Negative YoY
                color = '#e74c3c' if is_accelerating else '#f5a9a9'  # bright red or light red
            
            tag = 'Accelerating' if is_accelerating else 'Decelerating'
            return (tag, color)

        trends = pivot.apply(label_trend, axis=1)
        pivot['Trend'], pivot['TrendColor'] = zip(*trends)

        # prepare chart data for each ticker
        chart_data = {}
        for ticker in df['TICKER'].unique():
            ticker_df = df[df['TICKER'] == ticker][['DATE', 'MOVING_AVG_14_DAY']].sort_values('DATE')
            chart_data[ticker] = [{'x': d.isoformat(), 'y': float(v) if pd.notna(v) else None} for d, v in zip(ticker_df['DATE'], ticker_df['MOVING_AVG_14_DAY'])]

        # build html with fintech dark-mode styling
        css = """
            body {
                margin:0; padding:0; background:#0f1929; color:#c5cae9;
                font-family:'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                font-weight: bold;
            }
            .container {
                max-width:1600px; margin:40px auto; padding:45px;
                background:#1a2635; border-radius:12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                border: 1px solid #2a3d52;
            }
            h1 { 
                margin:0; font-size:2.2em; font-weight:700; 
                color:#ffffff; letter-spacing:-0.5px;
            }
            .subheader { 
                margin-top:8px; color:#90a4ae; font-size:0.95em; 
                font-weight:400;
            }
            table { 
                width:100%; border-collapse:collapse; color:#e0e0e0; 
                margin-top:30px;
            }
            th { 
                background:#0d1b2a; color:#b0bec5; padding:16px 12px;
                text-align:left; font-weight:700; font-size:0.85em;
                border-bottom:2px solid #2a3d52;
                text-transform:uppercase; letter-spacing:0.5px;
            }
            td { 
                padding:14px 12px; border-bottom:1px solid #263340;
                font-size:0.89em; font-weight: bold;
            }
            tr:nth-child(even){background:#161f2e;} 
            tr:hover{background:#1f2c3d; transition:background 0.2s;}
            .numeric{ 
                text-align:right; font-family:'Courier New', monospace; 
                font-weight: bold;
            }
            .ticker-cell { cursor: pointer; color: #4fc3f7; }
            .ticker-cell:hover { text-decoration: underline; }
            .modal {
                display: none; position: fixed; z-index: 1; left: 0; top: 0;
                width: 100%; height: 100%; background-color: rgba(0,0,0,0.7);
            }
            .modal-content {
                background-color: #1a2635; margin: 10% auto; padding: 20px;
                border: 1px solid #2a3d52; border-radius: 12px; width: 80%; max-width: 800px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            .close {
                color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer;
            }
            .close:hover { color: #fff; }
        """
        html = [
            '<html><head><meta charset="utf-8">',
            '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>',
            '<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>',
            '<style>', css, '</style></head><body>',
            '<div class="container">',
            '<h1>Arbiter Data YoY % Inflection Dashboard</h1>',
            f'<div class="subheader">Latest date: {weekly["WEEK_END"].max().date()}</div>',
            '<table><thead><tr><th>TICKER</th><th>EXCHANGE</th>'
        ]
        for d in dates:
            html.append(f'<th>{d.date()}</th>')
        html.append('<th>Trend</th></tr></thead><tbody>')

        for idx, row in pivot.iterrows():
            ticker, exch = idx
            html.append(f'<tr><td class="ticker-cell" data-ticker="{ticker}">{ticker}</td><td>{exch}</td>')
            for d in dates:
                val = row.get(d, '')
                if pd.notna(val):
                    html.append(f'<td class="numeric">{val:.2f}</td>')
                else:
                    html.append('<td></td>')
            tag, color = row['Trend'], row['TrendColor']
            html.append(f'<td style="color:{color}" class="trend-cell">{tag}</td></tr>')

        html.append('</tbody></table>')
        html.append('<div id="chartModal" class="modal"><div class="modal-content"><span class="close">&times;</span><canvas id="chartCanvas"></canvas></div></div>')
        html.append('<script>')
        html.append(f'const chartData = {json.dumps(chart_data)};')
        html.append('''
        let chart = null;
        document.querySelectorAll('.ticker-cell').forEach(cell => {
            cell.addEventListener('click', function() {
                const ticker = this.getAttribute('data-ticker');
                showChart(ticker);
            });
        });
        document.querySelector('.close').addEventListener('click', closeModal);
        window.addEventListener('click', function(event) {
            const modal = document.getElementById('chartModal');
            if (event.target == modal) {
                closeModal();
            }
        });
        function showChart(ticker) {
            const modal = document.getElementById('chartModal');
            const ctx = document.getElementById('chartCanvas').getContext('2d');
            if (chart) chart.destroy();
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: `${ticker} Moving Avg 14-Day`,
                        data: chartData[ticker],
                        borderColor: '#4fc3f7',
                        backgroundColor: 'rgba(79, 195, 247, 0.1)',
                        fill: true
                    }]
                },
                options: {
                    plugins: {
                        title: {
                            display: true,
                            text: `${ticker} Moving Avg 14-Day Card Spend`
                        }
                    },
                    scales: {
                        x: { type: 'time', time: { unit: 'day' } },
                        y: { beginAtZero: false }
                    }
                }
            });
            modal.style.display = 'block';
        }
        function closeModal() {
            document.getElementById('chartModal').style.display = 'none';
            if (chart) chart.destroy();
        }
        ''')
        html.append('</script></div></body></html>')
        html_content = ''.join(html)

        with open(output_path, 'w') as f:
            f.write(html_content)
        print(f"Dashboard written to {output_path}")
        return output_path
    

