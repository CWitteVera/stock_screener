"""
Enhanced dashboard components for dual dashboard (Swing + Day Trading)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import List, Optional
import json

from models.capital_account import CapitalAccount
from models.trade import Trade
from models.day_trade_opportunity import DayTradeOpportunity
from ledger.trading_ledger import TradingLedger
from day_trading.day_screener import DayScreener
from config.settings import (
    CAPITAL_PER_TRADE, PRIMARY_RETURN_TARGET, FALLBACK_RETURN_TARGET,
    DAY_TRADE_MIN_RETURN, DAY_TRADE_TARGET_RETURN, DAY_TRADE_MIN_CONFIDENCE
)
from utils.helpers import format_currency, format_percentage


def render_capital_sidebar(capital_account: CapitalAccount):
    """
    Render capital account display in sidebar
    
    Args:
        capital_account: CapitalAccount instance
    """
    st.sidebar.markdown("---")
    st.sidebar.header("💰 Capital Account")
    
    # Current capital
    st.sidebar.metric(
        "Current Capital",
        format_currency(capital_account.current_capital),
        delta=format_currency(capital_account.current_capital - capital_account.starting_capital)
    )
    
    # Progress to $7k goal
    goal_amount = 7000.0
    progress_pct = (capital_account.current_capital / goal_amount) * 100
    st.sidebar.progress(min(progress_pct / 100, 1.0))
    st.sidebar.caption(f"Progress to $7k: {progress_pct:.1f}%")
    
    # Next paycheck
    if capital_account.next_paycheck_date:
        days_to_paycheck = (capital_account.next_paycheck_date - date.today()).days
        st.sidebar.info(f"💵 Next paycheck in {days_to_paycheck} days\n\n${capital_account.paycheck_amount:.2f}")
    
    # Trading stats
    with st.sidebar.expander("📊 Trading Stats"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Trades", capital_account.total_trades)
            st.metric("Win Rate", f"{capital_account.get_win_rate():.1f}%")
        with col2:
            st.metric("Total Profit", format_currency(capital_account.total_profit))
            st.metric("Return", f"{capital_account.get_total_return_pct():.1f}%")
    
    # Time to goal
    goal_projection = capital_account.time_to_goal(goal_amount)
    
    if not goal_projection.get('goal_reached'):
        with st.sidebar.expander("🎯 Time to $7k Goal"):
            if 'current_performance' in goal_projection:
                days = goal_projection['current_performance']['days']
                target_date = goal_projection['current_performance']['date']
                st.info(f"**Current Pace:** {days} days\n\n{target_date.strftime('%B %d, %Y')}")
            
            if 'optimistic' in goal_projection:
                days = goal_projection['optimistic']['days']
                st.success(f"**Best Case:** {days} days")
            
            if 'pessimistic' in goal_projection:
                days = goal_projection['pessimistic']['days']
                st.warning(f"**Conservative:** {days} days")


def render_dual_opportunities(swing_trades: List[Trade], day_opportunities: List[DayTradeOpportunity], 
                              capital_account: CapitalAccount, execute_day_trades: bool = False):
    """
    Render dual dashboard with Swing + Day trading opportunities
    
    Args:
        swing_trades: List of swing trade opportunities
        day_opportunities: List of day trade opportunities
        capital_account: CapitalAccount for checking PDT eligibility
        execute_day_trades: Whether to execute or just monitor day trades
    """
    
    # Two columns: Swing (left) + Day (right)
    col_swing, col_day = st.columns(2)
    
    # LEFT COLUMN: SWING TRADES
    with col_swing:
        st.header("📊 Swing Trades")
        st.caption(f"Target: {PRIMARY_RETURN_TARGET}%+ in 5-10 days")
        
        if swing_trades:
            render_swing_opportunities_compact(swing_trades)
        else:
            st.info("No swing opportunities found.\nWait for better market conditions.")
    
    # RIGHT COLUMN: DAY TRADES
    with col_day:
        st.header("⚡ Day Trade Monitor")
        st.caption(f"Target: {DAY_TRADE_TARGET_RETURN}%+ intraday")
        
        # Check if can execute day trades
        can_execute = capital_account.current_capital >= 7000.0
        
        if not can_execute and execute_day_trades:
            st.warning("⚠️ MONITOR ONLY - Need $7k for execution\n\nCapital requirement not met for Pattern Day Trading.")
            execute_day_trades = False
        
        if not can_execute:
            st.info("📊 **MONITOR MODE**\n\nTracking opportunities until $7k threshold reached.")
        
        if day_opportunities:
            render_day_opportunities_compact(day_opportunities, execute_day_trades)
        else:
            st.info("No day trade setups found.\nCheck again at market open.")


def render_swing_opportunities_compact(trades: List[Trade]):
    """
    Render swing trade opportunities in compact format
    
    Args:
        trades: List of Trade objects
    """
    
    for i, trade in enumerate(trades[:5], 1):  # Show top 5
        with st.container():
            # Header row
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**#{i} {trade.symbol}** - {trade.name[:30]}")
            with col2:
                st.metric("Return", format_percentage(trade.estimated_return), label_visibility="collapsed")
            with col3:
                st.metric("Conf", f"{trade.confidence:.0f}%", label_visibility="collapsed")
            
            # Details row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.caption(f"Entry: {format_currency(trade.entry_price)}")
            with col2:
                st.caption(f"Target: {format_currency(trade.target_price)}")
            with col3:
                st.caption(f"Stop: {format_currency(trade.stop_price)}")
            with col4:
                st.caption(f"Days: {trade.days_to_target}")
            
            # Score bar
            score_pct = trade.score / 100
            st.progress(score_pct)
            st.caption(f"Score: {trade.score:.0f}/100")
            
            st.markdown("---")


def render_day_opportunities_compact(opportunities: List[DayTradeOpportunity], execute_mode: bool = False):
    """
    Render day trade opportunities in compact format
    
    Args:
        opportunities: List of DayTradeOpportunity objects
        execute_mode: Whether in execute or monitor mode
    """
    
    mode_badge = "🔴 EXECUTE" if execute_mode else "🟢 MONITOR"
    st.caption(mode_badge)
    
    for i, opp in enumerate(opportunities[:5], 1):  # Show top 5
        with st.container():
            # Header row
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**#{i} {opp.symbol}**")
            with col2:
                st.metric("Return", format_percentage(opp.estimated_return_pct), label_visibility="collapsed")
            with col3:
                st.metric("Conf", f"{opp.confidence:.0f}%", label_visibility="collapsed")
            
            # Details row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.caption(f"Entry: {format_currency(opp.entry_price)}")
            with col2:
                st.caption(f"Target: {format_currency(opp.target_price)}")
            with col3:
                st.caption(f"Stop: {format_currency(opp.stop_price)}")
            with col4:
                st.caption("Intraday")
            
            # Score bar
            score_pct = opp.overall_score / 100
            st.progress(score_pct)
            st.caption(f"Score: {opp.overall_score:.0f}/100")
            
            st.markdown("---")


def render_ledger_tab(ledger: TradingLedger):
    """
    Render trading ledger with metrics and accuracy analysis
    
    Args:
        ledger: TradingLedger instance
    """
    
    st.header("📚 Trading Ledger")
    
    if not ledger.entries:
        st.info("No trades recorded yet. Start tracking trades to see ledger data.")
        return
    
    # Calculate metrics
    from ledger.performance_metrics import (
        get_win_rate, get_profit_loss_summary, get_avg_profit_per_trade
    )
    from ledger.accuracy_calculator import get_overall_accuracy
    
    # Build comprehensive metrics
    metrics = {
        'total_trades': len([e for e in ledger.entries if e.exit_date is not None]),
        'win_rate': get_win_rate(ledger.entries),
        'avg_profit_per_trade': get_avg_profit_per_trade(ledger.entries)
    }
    
    # Add profit loss summary
    pl_summary = get_profit_loss_summary(ledger.entries)
    metrics.update(pl_summary)
    
    # Add prediction accuracy
    try:
        accuracy = get_overall_accuracy(ledger.entries)
        metrics['prediction_accuracy'] = accuracy.get('return_accuracy', 0.0)
        metrics['confidence_calibration'] = get_win_rate(ledger.entries)  # Use win rate as proxy
        metrics['roi_accuracy'] = accuracy.get('return_accuracy', 0.0)
    except Exception as e:
        metrics['prediction_accuracy'] = 0.0
        metrics['confidence_calibration'] = 0.0
        metrics['roi_accuracy'] = 0.0
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", metrics.get('total_trades', 0))
    with col2:
        st.metric("Win Rate", f"{metrics.get('win_rate', 0):.1f}%")
    with col3:
        # Use total return percentage from P&L summary
        total_return = metrics.get('total_return_pct', 0)
        st.metric("Total Return", f"{total_return:.1f}%")
    with col4:
        st.metric("Avg per Trade", format_currency(metrics.get('avg_profit_per_trade', 0)))
    
    # Accuracy & Calibration row
    st.markdown("---")
    st.subheader("🎯 Prediction Accuracy")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        accuracy = metrics.get('prediction_accuracy', 0)
        st.metric("Prediction Accuracy", f"{accuracy:.1f}%")
        st.caption("How often predicted outcomes match reality")
    
    with col2:
        calibration = metrics.get('confidence_calibration', 0)
        st.metric("Confidence Calibration", f"{calibration:.1f}%")
        st.caption("How well confidence scores predict success")
    
    with col3:
        roi_accuracy = metrics.get('roi_accuracy', 0)
        st.metric("ROI Accuracy", f"{roi_accuracy:.1f}%")
        st.caption("How close actual returns match predictions")
    
    # Ledger table
    st.markdown("---")
    st.subheader("📊 Trade History")
    
    # Convert entries to dataframe
    df_data = []
    for entry in ledger.entries:
        df_data.append({
            'Date': entry.entry_date.strftime('%Y-%m-%d') if entry.entry_date else 'N/A',
            'Type': entry.trade_type,
            'Symbol': entry.symbol,
            'Entry': format_currency(entry.predicted_entry),
            'Target': format_currency(entry.predicted_target),
            'Stop': format_currency(entry.predicted_stop),
            'Pred Return': format_percentage(entry.predicted_return_pct),
            'Confidence': f"{entry.predicted_confidence}%",
            'Executed': '✅' if entry.executed else '📊',
            'Status': entry.status or 'OPEN'
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Export buttons
    st.markdown("---")
    st.subheader("💾 Export Ledger")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export CSV", use_container_width=True):
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"trading_ledger_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📋 Export JSON", use_container_width=True):
            json_data = json.dumps([entry.to_dict() for entry in ledger.entries], indent=2)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_data,
                file_name=f"trading_ledger_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("📊 Export Metrics", use_container_width=True):
            metrics_json = json.dumps(metrics, indent=2)
            st.download_button(
                label="⬇️ Download Metrics",
                data=metrics_json,
                file_name=f"ledger_metrics_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )


def render_debug_tab(scan_results: Optional[dict] = None):
    """
    Render debug and analysis tab with filtering visualization
    
    Args:
        scan_results: Optional dict with scan results and debug info
    """
    
    st.header("🔧 Debug & Analysis")
    
    # Tab sections
    tab1, tab2 = st.tabs(["🔍 Filtering Pipeline", "📊 Stock Analyzer"])
    
    with tab1:
        render_filtering_pipeline(scan_results)
    
    with tab2:
        render_stock_analyzer()


def render_filtering_pipeline(scan_results: Optional[dict] = None):
    """
    Render filtering pipeline visualization
    
    Args:
        scan_results: Optional scan results with debug info
    """
    
    st.subheader("🔍 Filtering Pipeline Visualization")
    
    if not scan_results or 'filter_stats' not in scan_results:
        st.info("Run a scan to see filtering pipeline statistics.")
        return
    
    filter_stats = scan_results.get('filter_stats', {})
    
    # Funnel visualization
    st.markdown("### Screening Funnel")
    
    stages = [
        ('Initial Universe', filter_stats.get('initial_count', 0)),
        ('After Price Filter', filter_stats.get('after_price', 0)),
        ('After Volume Filter', filter_stats.get('after_volume', 0)),
        ('After Technical Filter', filter_stats.get('after_technical', 0)),
        ('Final Opportunities', filter_stats.get('final_count', 0))
    ]
    
    for stage_name, count in stages:
        pct = 100 if filter_stats.get('initial_count', 0) == 0 else \
              (count / filter_stats.get('initial_count', 1)) * 100
        
        st.markdown(f"**{stage_name}:** {count} stocks ({pct:.1f}%)")
        st.progress(pct / 100)
        st.markdown("")
    
    # Filter rejection reasons
    if 'rejection_reasons' in filter_stats:
        st.markdown("### Top Rejection Reasons")
        
        reasons = filter_stats['rejection_reasons']
        for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
            st.markdown(f"- **{reason}:** {count} stocks")


def render_stock_analyzer():
    """
    Individual stock analyzer tool
    """
    
    st.subheader("📊 Individual Stock Analyzer")
    st.caption("Analyze why a specific stock passed or failed filters")
    
    symbol = st.text_input("Enter stock symbol:", placeholder="e.g., NVDA", key="debug_symbol")
    
    col1, col2 = st.columns(2)
    
    with col1:
        analyze_swing = st.button("🔍 Analyze for Swing Trade", use_container_width=True)
    
    with col2:
        analyze_day = st.button("⚡ Analyze for Day Trade", use_container_width=True)
    
    if analyze_swing and symbol:
        with st.spinner(f"Analyzing {symbol} for swing trading..."):
            analyze_individual_stock_swing(symbol)
    
    if analyze_day and symbol:
        with st.spinner(f"Analyzing {symbol} for day trading..."):
            analyze_individual_stock_day(symbol)


def analyze_individual_stock_swing(symbol: str):
    """
    Analyze individual stock for swing trading with detailed breakdown
    
    Args:
        symbol: Stock ticker symbol
    """
    
    try:
        from core.screener import AdaptiveScreener
        
        screener = AdaptiveScreener()
        
        # Try to analyze the stock
        st.markdown(f"### Analysis for {symbol}")
        
        # Fetch and display basic info
        from config.api_config import DataFetcher
        fetcher = DataFetcher()
        stock_data = fetcher.get_stock_data(symbol)
        
        if not stock_data:
            st.error(f"❌ Could not fetch data for {symbol}")
            return
        
        st.success(f"✅ Data fetched successfully")
        
        # Display basic metrics
        info = stock_data.get('info', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            st.metric("Price", format_currency(price))
        
        with col2:
            volume = info.get('volume', 0)
            st.metric("Volume", f"{volume:,.0f}")
        
        with col3:
            market_cap = info.get('marketCap', 0)
            st.metric("Market Cap", f"${market_cap/1e9:.1f}B")
        
        with col4:
            sector = info.get('sector', 'Unknown')
            st.metric("Sector", sector)
        
        # Run through filters
        st.markdown("### Filter Results")
        
        from config.settings import MIN_PRICE, MAX_PRICE, MIN_VOLUME
        
        # Price filter
        if MIN_PRICE <= price <= MAX_PRICE:
            st.success(f"✅ Price Filter: ${price:.2f} (Range: ${MIN_PRICE}-${MAX_PRICE})")
        else:
            st.error(f"❌ Price Filter: ${price:.2f} (Range: ${MIN_PRICE}-${MAX_PRICE})")
        
        # Volume filter
        if volume >= MIN_VOLUME:
            st.success(f"✅ Volume Filter: {volume:,.0f} (Min: {MIN_VOLUME:,.0f})")
        else:
            st.error(f"❌ Volume Filter: {volume:,.0f} (Min: {MIN_VOLUME:,.0f})")
        
        st.info("💡 Use the main scanner to see full technical analysis and scoring.")
        
    except Exception as e:
        st.error(f"❌ Error analyzing {symbol}: {str(e)}")


def analyze_individual_stock_day(symbol: str):
    """
    Analyze individual stock for day trading with detailed breakdown
    
    Args:
        symbol: Stock ticker symbol
    """
    
    try:
        from day_trading.day_screener import DayScreener
        
        screener = DayScreener()
        
        st.markdown(f"### Day Trade Analysis for {symbol}")
        
        # Analyze stock
        result = screener.analyze_stock(symbol, "Technology")
        
        if result:
            st.success(f"✅ {symbol} passes day trading filters!")
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Overall Score", f"{result.overall_score:.0f}%")
            with col2:
                st.metric("Confidence", f"{result.confidence:.0f}%")
            with col3:
                st.metric("Est. Return", format_percentage(result.estimated_return_pct))
            with col4:
                st.metric("Entry", format_currency(result.entry_price))
            
            # Strategy breakdown
            st.markdown("### Strategy Components")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Momentum", f"{result.momentum_score:.0f}/100")
            with col2:
                st.metric("Volatility", f"{result.volatility_score:.0f}/100")
            with col3:
                st.metric("Volume", f"{result.volume_score:.0f}/100")
            
        else:
            st.warning(f"⚠️ {symbol} does not meet day trading criteria")
            st.info("Stock may have failed confidence threshold or filter requirements.")
        
    except Exception as e:
        st.error(f"❌ Error analyzing {symbol}: {str(e)}")
