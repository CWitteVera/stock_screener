#!/usr/bin/env python3
"""
Swing Trading Screener - Streamlit GUI
Main entry point for the web application
"""

import streamlit as st
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ui.dashboard import render_dashboard, render_position_monitor
from ui.enhanced_dashboard import (
    render_capital_sidebar, render_dual_opportunities, 
    render_ledger_tab, render_debug_tab
)
from config.settings import (
    CAPITAL_PER_TRADE, PRIMARY_RETURN_TARGET, FALLBACK_RETURN_TARGET,
    MAX_LOSS_PERCENT, MAX_HOLD_DAYS
)
from models.capital_account import CapitalAccount
from ledger.trading_ledger import TradingLedger
from day_trading.day_screener import DayScreener

# Page configuration
st.set_page_config(
    page_title="Swing Trading Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for capital account and ledger
if 'capital_account' not in st.session_state:
    st.session_state.capital_account = CapitalAccount()
    
if 'ledger' not in st.session_state:
    st.session_state.ledger = TradingLedger()

def main():
    """Main application"""
    
    # Title and description
    st.title("🎯 Intelligent Trading Screener")
    st.caption("Dual Dashboard: Swing Trading (15%+) & Day Trading (2%+) | Adaptive Strategy")
    
    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Capital account display
        render_capital_sidebar(st.session_state.capital_account)
        
        st.markdown("---")
        
        # Mode checkboxes (new enhanced mode)
        st.subheader("Trading Modes")
        
        enable_swing = st.checkbox("📊 Swing Trading", value=True, 
                                   help="Scan for 15%+ swing trades (5-10 days)")
        
        enable_day_monitor = st.checkbox("⚡ Day Trade Monitor", value=False,
                                        help="Monitor 2%+ intraday opportunities")
        
        # Execute day trades only if capital >= $7k
        can_execute_day = st.session_state.capital_account.current_capital >= 7000.0
        
        if can_execute_day:
            execute_day_trades = st.checkbox("🔴 Execute Day Trades", value=False,
                                            help="Execute day trades (requires $7k+)")
        else:
            execute_day_trades = False
            if enable_day_monitor:
                st.info("📊 Monitor-only mode\n\nNeed $7k to execute")
        
        st.markdown("---")
        
        # Tab mode selection
        view_mode = st.radio(
            "Select View",
            ["📊 Today's Opportunities", "💼 Active Positions", "📚 Trading Ledger", "🔧 Debug & Analysis"],
            index=0
        )
        
        # Store in session state
        st.session_state.enable_swing = enable_swing
        st.session_state.enable_day_monitor = enable_day_monitor
        st.session_state.execute_day_trades = execute_day_trades
        
        # Scan controls (only for opportunities view)
        if view_mode == "📊 Today's Opportunities":
            render_scan_controls()
        
        # Information section
        render_info_section()
    
    # Main content area - tabbed interface
    if view_mode == "📊 Today's Opportunities":
        render_opportunities_tab()
    elif view_mode == "💼 Active Positions":
        render_monitor_mode()
    elif view_mode == "📚 Trading Ledger":
        render_ledger_tab(st.session_state.ledger)
    else:  # Debug & Analysis
        scan_results = st.session_state.get('last_scan_results', None)
        render_debug_tab(scan_results)

def render_scan_controls():
    """Render scan configuration controls"""
    
    st.markdown("---")
    st.subheader("Scan Settings")
    
    sector = st.selectbox(
        "Select Sector",
        ["Technology", "Healthcare", "Energy", "Financials", "Consumer", "Communications"],
        index=0,
        help="Choose sector to scan for opportunities"
    )
    
    min_return = st.slider(
        "Minimum Return Target (%)",
        min_value=5,
        max_value=20,
        value=int(PRIMARY_RETURN_TARGET),
        step=1,
        help="Primary target return percentage"
    )
    
    max_loss = st.slider(
        "Max Loss Per Trade (%)",
        min_value=5,
        max_value=15,
        value=int(MAX_LOSS_PERCENT),
        step=1,
        help="Stop loss percentage"
    )
    
    # Store in session state
    if st.button("🔍 Start Scan", type="primary", use_container_width=True):
        st.session_state.scanning = True
        st.session_state.scan_params = {
            'sector': sector,
            'min_return': float(min_return),
            'max_loss': float(max_loss)
        }
        st.rerun()

def render_opportunities_tab():
    """Render opportunities tab with dual dashboard"""
    
    if st.session_state.get('scanning'):
        # Clear scanning flag
        st.session_state.scanning = False
        
        # Run scans based on enabled modes
        swing_trades = []
        day_opportunities = []
        
        if st.session_state.enable_swing:
            with st.spinner(f"🔍 Scanning swing opportunities..."):
                from core.screener import AdaptiveScreener
                screener = AdaptiveScreener()
                results = screener.scan_sector(
                    st.session_state.scan_params['sector'],
                    st.session_state.scan_params['min_return']
                )
                swing_trades = results.get('trades', [])
                st.session_state.last_scan_results = results
        
        if st.session_state.enable_day_monitor:
            with st.spinner(f"⚡ Scanning day trade opportunities..."):
                day_screener = DayScreener()
                # Scan sector for day trades
                from config.sectors import SECTOR_TICKERS
                sector_tickers = SECTOR_TICKERS.get(st.session_state.scan_params['sector'], [])
                
                for symbol in sector_tickers[:10]:  # Limit to first 10 for performance
                    try:
                        opp = day_screener.analyze_stock(symbol, st.session_state.scan_params['sector'])
                        if opp:
                            day_opportunities.append(opp)
                    except:
                        pass
                
                day_opportunities.sort(key=lambda x: x.overall_score, reverse=True)
        
        # Render dual dashboard
        if st.session_state.enable_swing or st.session_state.enable_day_monitor:
            render_dual_opportunities(
                swing_trades, 
                day_opportunities,
                st.session_state.capital_account,
                st.session_state.execute_day_trades
            )
        else:
            st.warning("⚠️ Enable at least one trading mode in the sidebar to scan for opportunities.")
    
    else:
        # Welcome screen
        render_welcome_screen()

def render_info_section():
    """Render information section in sidebar"""
    
    st.markdown("---")
    st.subheader("ℹ️ Information")
    
    with st.expander("Trading Parameters"):
        st.markdown(f"""
        - **Capital per trade:** ${CAPITAL_PER_TRADE:,}
        - **Primary target:** {PRIMARY_RETURN_TARGET}% in 5-10 days
        - **Fallback target:** {FALLBACK_RETURN_TARGET}%
        - **Stop loss:** -{MAX_LOSS_PERCENT}%
        - **Max hold time:** {MAX_HOLD_DAYS} days
        """)
    
    with st.expander("Tier System"):
        st.markdown("""
        **🔥 Tier 1 - Aggressive (15%+)**  
        High-confidence trades with 15%+ potential.
        Risk: HIGH | Action: TRADE NOW
        
        **⚠️ Tier 2 - Moderate (8-14%)**  
        Moderate opportunities with 8-14% potential.
        Risk: MEDIUM | Action: Consider smaller positions
        
        **🛑 Tier 3 - Wait (<8%)**  
        Weak conditions, below 8% potential.
        Risk: LOW | Action: HOLD CASH
        """)
    
    with st.expander("Data Sources"):
        st.markdown("""
        **Primary:** yfinance (FREE, unlimited)
        - All technical indicators calculated from yfinance data
        - RSI, MACD, Moving Averages, Volume analysis
        
        **Optional:** Financial Modeling Prep
        - Enhanced fundamentals (if API key provided)
        - Screener works 100% FREE without FMP key
        """)
    
    st.markdown("---")
    st.caption("Made with ❤️ for swing traders")

def render_monitor_mode():
    """Render position monitoring interface"""
    
    render_position_monitor()

def render_welcome_screen():
    """Render welcome/info screen"""
    
    st.markdown("---")
    st.header("Welcome to the Intelligent Trading Screener!")
    
    st.info("👈 Enable trading modes and click 'Start Scan' to find opportunities!")
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Swing Trading")
        st.markdown("""
        Medium-term opportunities:
        - 15%+ return targets
        - 5-10 day timeframe
        - Technical + fundamental
        - Position sizing
        """)
    
    with col2:
        st.markdown("### ⚡ Day Trading")
        st.markdown("""
        Intraday opportunities:
        - 2-5% intraday moves
        - High confidence (85%+)
        - Monitor-only until $7k
        - Pre-market scanner
        """)
    
    with col3:
        st.markdown("### 💰 Capital Tracking")
        st.markdown("""
        Built-in account management:
        - Track progress to $7k
        - Paycheck integration
        - Win rate tracking
        - Time to PDT goal
        """)
    
    # Quick stats from capital account
    st.markdown("---")
    st.subheader("📈 Your Stats")
    
    capital = st.session_state.capital_account
    ledger = st.session_state.ledger
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Capital", f"${capital.current_capital:,.2f}")
    with col2:
        st.metric("Total Trades", capital.total_trades)
    with col3:
        st.metric("Win Rate", f"{capital.get_win_rate():.1f}%")
    with col4:
        st.metric("Ledger Entries", len(ledger.entries))
    
    # Instructions
    st.markdown("---")
    st.subheader("🚀 Quick Start")
    
    st.markdown("""
    1. **Enable trading modes** in sidebar (Swing and/or Day Trading)
    2. **Select a sector** to scan
    3. **Click "Start Scan"** to find opportunities
    4. **Review dual dashboard** with both swing and day trades
    5. **Track in ledger** to monitor accuracy
    6. **Export trades** to your broker
    """)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("🆓 100% FREE - Uses yfinance (no API key required)")
    
    with col2:
        st.info("📊 Track to $7k to unlock day trade execution")

if __name__ == '__main__':
    main()
