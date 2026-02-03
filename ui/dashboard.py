"""
Streamlit dashboard components
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from models.trade import Trade
from ui.charts import create_price_chart, create_macd_chart, create_score_radar_chart
from ui.export import export_to_fidelity_csv, export_full_analysis_csv, export_to_json
from utils.helpers import (
    format_currency, format_percentage, get_star_rating, 
    get_confidence_bar, get_rank_emoji
)

def render_dashboard(scan_params):
    """
    Main dashboard rendering function
    """
    from core.screener import AdaptiveScreener
    
    # Show progress
    with st.spinner(f"🔍 Scanning {scan_params['sector']} sector..."):
        screener = AdaptiveScreener()
        results = screener.scan_sector(
            scan_params['sector'],
            scan_params['min_return']
        )
    
    # Display results
    render_results(results, scan_params)

def render_results(results, scan_params):
    """
    Render scan results
    """
    
    # Market assessment header
    tier = results['tier']
    mode = results['mode']
    recommendation = results['recommendation']
    
    st.markdown("---")
    st.header("📊 Market Assessment")
    
    # Color-code by tier
    if tier == 1:
        st.success(f"🔥 **{mode}**")
        st.markdown(f"### {recommendation}")
    elif tier == 2:
        st.warning(f"⚠️ **{mode}**")
        st.markdown(f"### {recommendation}")
    else:
        st.error(f"🛑 **{mode}**")
        st.markdown(f"### {recommendation}")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tier", f"Tier {tier}")
    with col2:
        st.metric("Opportunities", len(results['trades']))
    with col3:
        st.metric("Risk Level", results['risk_level'])
    with col4:
        st.metric("Scan Time", f"{results['scan_time']:.1f}s")
    
    st.markdown("---")
    
    # Trade opportunities
    if results['trades']:
        render_trade_opportunities(results['trades'])
    else:
        st.info("💡 No trade opportunities found. Consider waiting for better market conditions.")

def render_trade_opportunities(trades):
    """
    Render list of trade opportunities
    """
    
    st.header(f"🎯 Top {len(trades)} Trade Opportunities")
    
    # Quick reference table
    with st.expander("📋 Quick Reference Table", expanded=True):
        render_quick_table(trades)
    
    # Detailed cards
    st.markdown("---")
    st.subheader("📈 Detailed Analysis")
    
    for i, trade in enumerate(trades, 1):
        render_trade_card(trade, i)
        st.markdown("---")
    
    # Export options
    render_export_section(trades)

def render_quick_table(trades):
    """
    Render quick reference table
    """
    
    data = []
    for i, trade in enumerate(trades, 1):
        data.append({
            'Rank': f"{get_rank_emoji(i)} #{i}",
            'Symbol': trade.symbol,
            'Entry': format_currency(trade.entry_price),
            'Target': format_currency(trade.target_price),
            'Stop': format_currency(trade.stop_price),
            'Return': format_percentage(trade.estimated_return),
            'Confidence': f"{trade.confidence:.0f}%",
            'Score': f"{trade.score:.0f}/100"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.caption("💡 Recommendation: Pick top 1-2 trades. Start with #1.")

def render_trade_card(trade, rank):
    """
    Render detailed trade opportunity card
    """
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"## {get_rank_emoji(rank)} #{rank}: {trade.symbol} - {trade.name}")
    with col2:
        st.markdown(f"### {get_star_rating(trade.score)}")
        st.caption(f"Score: {trade.score:.0f}/100")
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Price", format_currency(trade.current_price))
    with col2:
        st.metric("Return Potential", format_percentage(trade.estimated_return))
    with col3:
        st.metric("Confidence", f"{trade.confidence:.0f}%")
    with col4:
        st.metric("Days to Target", f"{trade.days_to_target} days")
    
    # Trade setup
    st.markdown("### 💰 Trade Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Position Size:** {trade.shares} shares @ {format_currency(trade.entry_price)}  
        **Position Value:** {format_currency(trade.position_value)}  
        **Target Price:** {format_currency(trade.target_price)} (+{format_percentage(trade.estimated_return)})  
        **Stop Loss:** {format_currency(trade.stop_price)} (-{format_percentage((trade.entry_price - trade.stop_price) / trade.entry_price * 100)})
        """)
    
    with col2:
        st.markdown(f"""
        **Target Profit:** {format_currency(trade.target_profit)} 💰  
        **Max Loss:** {format_currency(trade.max_loss)} 🛡️  
        **Risk/Reward:** 1:{trade.risk_reward_ratio:.1f}  
        **Sector:** {trade.sector}
        """)
    
    # Confidence bar
    st.markdown(f"**Confidence:** {get_confidence_bar(trade.confidence)} {trade.confidence:.0f}%")
    
    # Technical signals
    st.markdown("### 📊 Technical Signals")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("MACD", f"{trade.macd_score:.0f}/100")
    with col2:
        st.metric("RSI", f"{trade.rsi:.0f}" if trade.rsi else "N/A")
    with col3:
        st.metric("Volume", f"{trade.volume_score:.0f}/100")
    with col4:
        st.metric("Breakout", f"{trade.breakout_score:.0f}/100")
    with col5:
        st.metric("Momentum", f"{trade.momentum_score:.0f}/100")
    
    # Entry strategy
    with st.expander("🎯 Entry Strategy & Support Levels"):
        st.info(trade.entry_strategy)
        
        if trade.support_levels:
            st.markdown("**Support Levels:**")
            st.markdown(", ".join(trade.support_levels))
    
    # Charts
    with st.expander("📈 View Charts"):
        render_trade_charts(trade)

def render_trade_charts(trade):
    """
    Render charts for a trade
    """
    
    # Need to fetch data again for charts
    from config.api_config import DataFetcher
    from core.technical_analysis import calculate_all_indicators
    
    fetcher = DataFetcher()
    stock_data = fetcher.get_stock_data(trade.symbol)
    
    if stock_data:
        df = calculate_all_indicators(stock_data['history'])
        
        # Price chart
        price_chart = create_price_chart(
            df, 
            trade.symbol,
            trade.entry_price,
            trade.target_price,
            trade.stop_price
        )
        st.plotly_chart(price_chart, use_container_width=True)
        
        # Radar chart
        radar_chart = create_score_radar_chart(trade)
        st.plotly_chart(radar_chart, use_container_width=True)
    else:
        st.error("Could not load chart data")

def render_export_section(trades):
    """
    Render export options
    """
    
    st.markdown("---")
    st.header("💾 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Export Fidelity CSV", use_container_width=True):
            if export_to_fidelity_csv(trades, "fidelity_trades.csv"):
                st.success("✅ Exported to fidelity_trades.csv")
    
    with col2:
        if st.button("📊 Export Full Analysis CSV", use_container_width=True):
            if export_full_analysis_csv(trades, "trade_analysis.csv"):
                st.success("✅ Exported to trade_analysis.csv")
    
    with col3:
        if st.button("📋 Export JSON", use_container_width=True):
            if export_to_json(trades, "trades.json"):
                st.success("✅ Exported to trades.json")

def render_position_monitor():
    """
    Render position monitoring interface
    """
    
    st.header("💼 Position Monitor")
    
    symbol = st.text_input("Enter symbol to monitor:", placeholder="e.g., NVDA")
    
    if st.button("📊 Check Position"):
        if symbol:
            from core.screener import AdaptiveScreener
            screener = AdaptiveScreener()
            
            with st.spinner(f"Loading position for {symbol}..."):
                position = screener.monitor_position(symbol)
            
            if position:
                render_position_status(position)
            else:
                st.warning(f"No active position found for {symbol}")
        else:
            st.error("Please enter a symbol")

def render_position_status(position):
    """
    Render position status
    """
    
    st.markdown("---")
    st.subheader(f"Position: {position.symbol} - {position.name}")
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Entry Price", format_currency(position.entry_price))
    with col2:
        st.metric("Current Price", format_currency(position.current_price))
    with col3:
        st.metric("P&L", 
                 format_currency(position.unrealized_pnl),
                 format_percentage(position.unrealized_pnl_percent))
    with col4:
        st.metric("Days Held", f"{position.days_held}/{position.max_hold_days}")
    
    # Progress bar
    progress = position.get_progress_percent() / 100
    st.progress(min(max(progress, 0), 1))
    st.caption(f"Progress to target: {position.get_progress_percent():.0f}%")
    
    # Status
    if position.should_exit():
        st.error(f"⚠️ EXIT SIGNAL: {position.status}")
    else:
        st.success(f"✅ {position.status} - Thesis intact")
    
    # Technical signals
    st.markdown("### 📈 Current Signals")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"{'✅' if position.above_20ma else '❌'} {'Above' if position.above_20ma else 'Below'} 20-MA")
    with col2:
        st.markdown(f"{'✅' if position.rsi and 40 <= position.rsi <= 70 else '⚠️'} RSI: {position.rsi:.0f if position.rsi else 'N/A'}")
    with col3:
        st.markdown(f"{'✅' if position.volume_above_avg else '⚠️'} Volume {'Above' if position.volume_above_avg else 'Below'} Avg")
    with col4:
        st.markdown(f"{'✅' if position.macd_bullish else '❌'} MACD {'Bullish' if position.macd_bullish else 'Bearish'}")
