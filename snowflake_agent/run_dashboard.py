#!/usr/bin/env python3
"""
Simple script to run the Arbiter Data Inflection Dashboard.
Hardcoded parameters: edit the values below as needed.
"""

from arbiter_agent import SnowflakeCardSpendAgent

# Hardcoded parameters - edit these as needed
# exclude tickers with bad quality
EXCLUDE_TICKERS = ['OPTU', 'CHDN','97950', 'LNC', 'NSIT', 'CONN', 'TTAN', 'TRVG', 'TMP', 'SDC',
                   'NWC', 'LVS', 'HQY', 'FTD', 'FTCH', 'CABO', 'BHF', 'ASAP', 'GTLB', 'FTDR', 'SPWR',
                   'SSB', 'DXLG', 'L', 'TRI', 'DFRG', 'MUL', 'BHLB', 'ACGL', 'TDUP', 'ZGN', 'SIMP', 'HBAN',
                   'IMBI', 'SASR', 'SLF', 'AROW', 'OSCR', 'MTB', 'CURO', 'RAD', 'CRMT', 'HIBB', 'WISE',
                   'PRTY', 'SNV', 'OPK', 'PRPL', 'NCR', 'HOOD', 'JOAN', 'ANGI', 'BOO', 'BIG', 'BCOR', 'CNXN',
                   'CSSE', 'FWONA', 'RTWIQ', 'ALRM', 'CRWD', '' ]  # List of tickers to exclude
OUTPUT_FILE = 'arbiter_dashboard.html'  # Output HTML file path

def main():
    """Run the dashboard generation."""
    print("🚀 Starting Arbiter Data YoY % Inflection Dashboard generation...")
    
    agent = SnowflakeCardSpendAgent()
    
    try:
        # Generate the dashboard with hardcoded parameters
        agent.generate_dashboard(
            output_path=OUTPUT_FILE,
            exclude_tickers=EXCLUDE_TICKERS
        )
        
        print(f"✅ Dashboard generated successfully: {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {str(e)}")
    
    finally:
        # Note: Agent session is managed internally
        pass

if __name__ == "__main__":
    main()