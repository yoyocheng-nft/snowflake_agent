#!/usr/bin/env python3
"""
Simple script to run the Arbiter Data Inflection Dashboard.
Hardcoded parameters: edit the values below as needed.
"""

from arbiter_agent import SnowflakeCardSpendAgent

# Hardcoded parameters - edit these as needed

## Tickers to monitor in the TICKER MONITOR tab
## Add or remove ticker symbols as needed
MONITOR_TICKERS = ['TGT', 'PINS', 'MSFT', 'META', 'AMZN', 'HD']

## exclude tickers with bad quality or meaningless ticker
EXCLUDE_TICKERS = ['OPTU', 'CHDN','97950', 'LNC', 'NSIT', 'CONN', 'TTAN', 'TRVG', 'TMP', 'SDC', 'SAN', 'NLOK', 'SBCF', 'SMRTQ',
                   'NWC', 'LVS', 'HQY', 'FTD', 'FTCH', 'CABO', 'BHF', 'ASAP', 'GTLB', 'FTDR', 'SPWR', 'DOCN', 'THRN', 'OBNK',
                   'SSB', 'DXLG', 'L', 'TRI', 'DFRG', 'MUL', 'BHLB', 'ACGL', 'TDUP', 'ZGN', 'SIMP', 'HBAN', 'BBBY', 'LNF', 'FIS',
                   'IMBI', 'SASR', 'SLF', 'AROW', 'OSCR', 'MTB', 'CURO', 'RAD', 'CRMT', 'HIBB', 'WISE', 'CADE', 'CINE', 'CTBI',
                   'PRTY', 'SNV', 'OPK', 'PRPL', 'NCR', 'HOOD', 'JOAN', 'ANGI', 'BOO', 'BIG', 'BCOR', 'CNXN', 'LKFN', '7453',
                   'CSSE', 'FWONA', 'RTWIQ', 'ALRM', 'CRWD', 'SEM', 'WSFS', 'BARK',  'EBSB', 'TRCY', 'CNO', 'NEO', 'CNTY',
                   'AMAL', 'FRPT', 'MYGN', 'SSINQ','FMBI', 'BODY', 'OFG', 'STBA', 'HTH', 'WWE', 'MNTV', 'SFER', '1913','OWLT',
                   '']

## Output HTML file path
OUTPUT_FILE = 'arbiter_dashboard.html'

def main():
    """Run the dashboard generation."""
    print("🚀 Starting Arbiter Data YoY % Inflection Dashboard generation...")
    
    agent = SnowflakeCardSpendAgent()
    
    try:
        # Generate the dashboard with hardcoded parameters
        agent.generate_dashboard(
            output_path=OUTPUT_FILE,
            exclude_tickers=EXCLUDE_TICKERS,
            monitor_tickers=MONITOR_TICKERS
        )
        
        print(f"✅ Dashboard generated successfully: {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {str(e)}")
    
    finally:
        # Note: Agent session is managed internally
        pass

if __name__ == "__main__":
    main()