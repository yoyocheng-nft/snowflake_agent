# snowflake_agent

# Arbiter Data YoY % Inflection Dashboard

A Python agent that reads pre-transformed card spend data from Snowflake and generates an interactive HTML dashboard with trend analysis, summary metrics, and year-over-year comparisons.

## Features

✨ **Data Reading**: Fetches pre-transformed card spend data from Snowflake tables  
� **Interactive Dashboard**: Creates beautiful HTML dashboards with:
  - Summary cards highlighting top gainers, decliners, and inflection points
  - Trend indicators (Accelerating/Decelerating/Unchanged)
  - Color-coded cells based on performance
  - Clickable tickers with Chart.js time-series charts
  - Dark fintech theme with modern styling

🚀 **On-Demand Execution**: Run anytime with customizable parameters  
🎯 **Ticker Management**: 
  - Exclude unwanted tickers from main analysis
  - Dedicated Ticker Monitor tab with year-over-year comparisons
  
📈 **Visual Analytics**: 
  - Interactive charts showing 14-day moving averages over time
  - Multi-year comparison views for selected tickers
  - 12-week historical trend analysis

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Snowflake Connection

The agent uses RSA key authentication with the following files:

- `credentials_sf.json`: Connection parameters
- `rsa_key.p8`: Private key file

**credentials_sf.json structure:**
```json
{
    "account": "YOUR_ACCOUNT",
    "user": "YOUR_USER",
    "role": "ACCOUNTADMIN",
    "warehouse": "YOUR_WAREHOUSE",
    "database": "YOUR_DATABASE",
    "schema": "YOUR_SCHEMA"
}
```

### 3. Verify Data Source

The agent reads from table: `AGENT.ARBITER.TRANSFORM`

**Expected columns:**
- `DATE`: Date column
- `TICKER`: Stock ticker symbol
- `EXCHANGE`: Exchange identifier
- `MOVING_AVG_14_DAY`: Pre-calculated 14-day moving average
- `YOY_PCT_CHANGE`: Pre-calculated year-over-year percentage change

## Usage

### Quick Start (Recommended)

```bash
python run_dashboard.py
```

This runs the dashboard generation with pre-configured settings and generates `arbiter_dashboard.html`.

### Programmatic Usage

```python
from arbiter_agent import SnowflakeCardSpendAgent

# Create agent instance
agent = SnowflakeCardSpendAgent()

# Generate dashboard with custom settings
agent.generate_dashboard(
    output_path="my_dashboard.html",
    exclude_tickers=['AAPL', 'GOOGL'],  # Optional: exclude from main table
    monitor_tickers=['TGT', 'MSFT', 'AMZN']  # Optional: tickers for Monitor tab
)
```

### Advanced Usage

```python
from arbiter_agent import SnowflakeCardSpendAgent

agent = SnowflakeCardSpendAgent()

# Fetch raw data (last 90 days by default)
df = agent.fetch_data(days_back=90)

# Fetch monitor data for specific year range
monitor_data = agent.fetch_monitor_data(tickers=['TGT', 'MSFT', 'AMZN'])

# Create dashboard with both exclusions and monitor tickers
agent.generate_dashboard(
    output_path="custom_dashboard.html",
    exclude_tickers=['TICKER1', 'TICKER2'],
    monitor_tickers=['MSFT', 'AAPL', 'GOOG']
)
```

## Architecture

### Core Components

1. **SnowflakeCardSpendAgent Class**
   - Manages Snowflake connection via Snowpark
   - Handles data fetching and processing
   - Generates interactive HTML dashboards

2. **Data Flow**
   - `fetch_data()`: Retrieves last 90 days of pre-transformed data from Snowflake
   - `fetch_monitor_data()`: Retrieves data for specified tickers from Jan 1 of (current year - 1) to now
   - `generate_dashboard()`: Creates HTML with summary metrics, interactive tables, and charts

### Data Processing Logic

**Summary Metrics Calculation**:
- Top 10 tickers with highest YoY increase
- Top 10 tickers with highest YoY decline
- Tickers that flipped from negative to positive YoY
- Tickers that flipped from positive to negative YoY

**Trend Analysis**:
- Compares latest vs previous date YoY values
- Classifies as: Accelerating, Decelerating, or Unchanged (±1% threshold)
- Color codes: Green (positive), Red (negative), Blue (unchanged)

**Ticker Monitor Tab**:
- Year-over-year comparison charts for selected tickers
- Shows current year vs previous year on same day-of-year axis
- 14-day moving average visualization

**Dashboard Features**:
- **Summary Cards**: Quick overview of key metrics and inflection points
- **Interactive Table**: Click ticker names to view 14-day MA time series
- **Monitor Tab**: Dedicated view for year-over-year comparisons
- **Color Coding**: Visual indicators for performance trends
- **Responsive Design**: Modern dark theme optimized for financial data
- **Chart.js Integration**: Professional time-series visualization

## Dashboard Output

The generated HTML dashboard includes two main tabs:

### Summary Tab
Contains key metrics and comprehensive data table.

**Summary Cards**:
- Top 10 tickers with highest YoY increase
- Top 10 tickers with highest YoY decline
- Tickers that flipped from negative to positive YoY
- Tickers that flipped from positive to negative YoY

**Main Data Table**:
- **Columns**: TICKER, EXCHANGE, Date values (12 weeks back), Trend
- **Rows**: Sorted by latest YoY % (descending)
- **Color Coding**:
  - 🟢 Green: Positive YoY accelerating
  - 🔴 Red: Negative YoY accelerating
  - 🔵 Blue: Unchanged (±1% threshold)
  - Light colors: Decelerating trends

**Interactive Features**:
- **Clickable Tickers**: Opens modal with Chart.js line chart
- **Time Series Charts**: Shows 14-day moving average over time
- **Modal Interface**: Clean popup for detailed views

### Ticker Monitor Tab
Dedicated view for year-over-year comparison of selected tickers.

**Features**:
- Side-by-side line charts for current and previous year
- Day-of-year alignment for accurate seasonal comparison
- 14-day moving average visualization
- Responsive grid layout

## Configuration

### Customize Date Range

```python
# Change data lookback period
df = agent.fetch_data(days_back=180)  # 6 months instead of 3
```

### Customize Tickers

Edit `run_dashboard.py` to customize ticker lists:

```python
# Tickers to exclude from main summary table
EXCLUDE_TICKERS = ['AAPL', 'MSFT', 'TSLA']

# Tickers to monitor in the dedicated Ticker Monitor tab
MONITOR_TICKERS = ['TGT', 'PINS', 'MSFT', 'META', 'AMZN', 'HD']
```

Or customize programmatically:

```python
agent.generate_dashboard(
    exclude_tickers=['AAPL', 'TSLA'],
    monitor_tickers=['MSFT', 'GOOGL', 'AMZN']
)
```

### Change Output Location

```python
agent.generate_dashboard(output_path="/path/to/custom/dashboard.html")
```

## File Structure

```
snowflake_agent/
├── arbiter_agent.py            # Main agent class
├── run_dashboard.py            # Execution script with configuration
├── snowpark_utils.py           # Snowflake connection utilities
├── credentials_sf.json         # Connection parameters (not in repo)
├── rsa_key.p8                  # Private key for auth (not in repo)
├── snowpark_connection_test.py # Connection testing utility
├── requirements.txt            # Python dependencies
├── arbiter_dashboard.html      # Generated dashboard output
└── README.md                   # This file
```

## Dependencies

- snowflake-snowpark-python
- pandas
- cryptography
- chart.js (via CDN in generated HTML)

## Troubleshooting

### Connection Issues
- **RSA Key Error**: Ensure `rsa_key.p8` exists and has correct permissions
- **Authentication Failed**: Verify credentials in `credentials_sf.json`
- **Warehouse Not Found**: Check warehouse name and availability

### Data Issues
- **Empty Results**: Verify source table `AGENT.ARBITER.TRANSFORM` has data
- **Missing Columns**: Check column names match expected schema
- **Date Range**: Ensure data exists for requested date range

### Dashboard Issues
- **No Charts**: Check browser console for JavaScript errors
- **Styling Problems**: Ensure modern browser with CSS Grid support
- **Large Files**: Reduce date range if dashboard becomes too large

## Examples

See `examples.py` for comprehensive usage examples including:
- Basic pipeline execution
- Custom date ranges
- Different output configurations
- Error handling patterns

## Support

For issues:
1. Run `python snowpark_connection_test.py` to verify Snowflake connection
2. Check data exists in source table with correct schema
3. Review error messages and logs
4. Verify all dependencies are installed

## Future Enhancements

- [ ] Add data validation and quality checks
- [ ] Implement incremental loading
- [ ] Add email notifications for significant changes
- [ ] Create REST API wrapper
- [ ] Add more chart types and analytics
- [ ] Support multiple data sources
