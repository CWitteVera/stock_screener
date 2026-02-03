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
from config.settings import (
    CAPITAL_PER_TRADE, PRIMARY_RETURN_TARGET, FALLBACK_RETURN_TARGET,
    MAX_LOSS_PERCENT, MAX_HOLD_DAYS
)

# Page configuration
st.set_page_config(
    page_title="Swing Trading Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application"""
    
    # Title and description
    st.title("🎯 Intelligent Swing Trading Screener")
    st.caption("Adaptive return targeting: 15% → 8% → Wait | Optimized for $1000 trades")
    
    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Mode selection
        mode = st.radio(
            "Select Mode",
            ["🔍 Scan for Trades", "💼 Monitor Position"],
            index=0
        )
        
        if mode == "🔍 Scan for Trades":
            render_scan_controls()
        else:
            render_monitor_controls()
        
        # Information section
        render_info_section()
    
    # Main content area
    if mode == "🔍 Scan for Trades":
        render_scan_mode()
    else:
        render_monitor_mode()

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

def render_monitor_controls():
    """Render position monitoring controls"""
    
    st.markdown("---")
    st.subheader("Position Monitor")
    
    st.info("Switch to the main area to monitor your positions")

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

def render_scan_mode():
    """Render scanning interface"""
    
    if st.session_state.get('scanning'):
        # Clear scanning flag
        scanning = st.session_state.scanning
        st.session_state.scanning = False
        
        # Run scan
        render_dashboard(st.session_state.scan_params)
        
    else:
        # Welcome screen
        render_welcome_screen()

def render_monitor_mode():
    """Render position monitoring interface"""
    
    render_position_monitor()

def render_welcome_screen():
    """Render welcome/info screen"""
    
    st.markdown("---")
    st.header("Welcome to the Swing Trading Screener!")
    
    st.info("👈 Select a sector and click 'Start Scan' to find swing trade opportunities!")
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Adaptive Targeting")
        st.markdown("""
        Intelligently adjusts return targets:
        - 15%+ opportunities → TRADE
        - 8-14% opportunities → CONSIDER
        - <8% opportunities → WAIT
        """)
    
    with col2:
        st.markdown("### 📊 Technical Analysis")
        st.markdown("""
        Comprehensive scoring:
        - MACD signals
        - RSI momentum
        - Volume patterns
        - Breakout detection
        - Price momentum
        """)
    
    with col3:
        st.markdown("### 💰 Risk Management")
        st.markdown("""
        Built-in protection:
        - Automatic stop loss
        - Position sizing
        - Risk/reward ratios
        - Support-based stops
        """)
    
    # Quick stats (placeholder)
    st.markdown("---")
    st.subheader("📈 Quick Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Positions", "0", help="Number of open trades")
    with col2:
        st.metric("Today's Scans", "0", help="Scans performed today")
    with col3:
        st.metric("Total Opportunities", "0", help="Trades identified today")
    with col4:
        st.metric("API Calls Used", "0", help="FMP API calls today")
    
    # Instructions
    st.markdown("---")
    st.subheader("🚀 Quick Start")
    
    st.markdown("""
    1. **Select a sector** from the sidebar (Technology, Healthcare, etc.)
    2. **Set your target return** (default: 15%)
    3. **Click "Start Scan"** to find opportunities
    4. **Review the results** and select top trades
    5. **Export to Fidelity** or your broker
    6. **Monitor positions** using the Position Monitor mode
    """)
    
    st.markdown("---")
    st.success("🆓 This screener is 100% FREE! All analysis uses yfinance (no API key required)")
    st.info("💡 Optional: Add FMP API key in .env file for enhanced fundamental data")

if __name__ == '__main__':
    main()
