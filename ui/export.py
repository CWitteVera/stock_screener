"""
Export functions for trade opportunities
"""

import pandas as pd
import csv
from typing import List
from models.trade import Trade

def export_to_fidelity_csv(trades: List[Trade], filename: str = "fidelity_trades.csv"):
    """
    Export trades to Fidelity ATP CSV format
    """
    if not trades:
        return False
    
    rows = [trade.to_fidelity_csv_row() for trade in trades]
    
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    
    return True

def export_full_analysis_csv(trades: List[Trade], filename: str = "trade_analysis.csv"):
    """
    Export full trade analysis to CSV
    """
    if not trades:
        return False
    
    rows = [trade.to_dict() for trade in trades]
    
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    
    return True

def export_to_json(trades: List[Trade], filename: str = "trades.json"):
    """
    Export trades to JSON format
    """
    import json
    
    if not trades:
        return False
    
    data = [trade.to_dict() for trade in trades]
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return True

def format_trade_summary(trade: Trade) -> str:
    """
    Format a single trade as text summary
    """
    summary = f"""
═══════════════════════════════════════════════
{trade.symbol} - {trade.name}
═══════════════════════════════════════════════

Current Price: ${trade.current_price:.2f}
Overall Score: {trade.score:.0f}/100

📈 RETURN POTENTIAL: {trade.estimated_return:.1f}% in {trade.days_to_target} days
   Confidence: {trade.confidence:.0f}%

💰 TRADE SETUP (${trade.position_value:.2f} position):
   BUY:        {trade.shares} shares @ ${trade.entry_price:.2f}
   TARGET:     ${trade.target_price:.2f} (+{trade.estimated_return:.1f}% = +${trade.target_profit:.0f} profit)
   STOP LOSS:  ${trade.stop_price:.2f} (-{((trade.entry_price - trade.stop_price) / trade.entry_price * 100):.1f}% = -${trade.max_loss:.0f} max loss)

🛡️ RISK MANAGEMENT:
   Risk/Reward: 1:{trade.risk_reward_ratio:.1f}
   
📊 TECHNICAL SIGNALS:
   MACD Score:     {trade.macd_score:.0f}/100
   RSI:            {trade.rsi:.0f if trade.rsi else 'N/A'}
   Volume Score:   {trade.volume_score:.0f}/100
   Breakout Score: {trade.breakout_score:.0f}/100
   Momentum Score: {trade.momentum_score:.0f}/100

🎯 ENTRY STRATEGY:
   {trade.entry_strategy}
"""
    
    if trade.support_levels:
        summary += f"\n📉 SUPPORT LEVELS: {', '.join(trade.support_levels)}\n"
    
    return summary

def format_results_text(result: dict) -> str:
    """
    Format full scan results as text
    """
    from datetime import datetime
    from utils.helpers import get_tier_emoji
    
    text = f"""
{'='*60}
🔍 SWING TRADE SCREENER RESULTS
Sector: {result['sector']} | Date: {datetime.now().strftime('%b %d, %Y, %I:%M %p')}
{'='*60}

📊 MARKET ASSESSMENT: {get_tier_emoji(result['tier'])} {result['mode']}
{result['recommendation']}

{'='*60}
"""
    
    if result['trades']:
        for i, trade in enumerate(result['trades'], 1):
            rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            text += f"\n{rank_emoji} RANK #{i}:"
            text += format_trade_summary(trade)
            text += "\n"
        
        # Quick reference table
        text += "\n" + "="*60 + "\n"
        text += "📋 QUICK REFERENCE TABLE:\n"
        text += "┌────────┬───────┬──────────┬─────────┬──────────┬───────┐\n"
        text += "│ Rank   │ Ticker│ Entry    │ Target  │ Stop     │ Score │\n"
        text += "├────────┼───────┼──────────┼─────────┼──────────┼───────┤\n"
        
        for i, trade in enumerate(result['trades'], 1):
            rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            text += f"│ {rank_emoji} #{i:<2} │ {trade.symbol:<5} │ ${trade.entry_price:>7.2f} │ ${trade.target_price:>6.0f} │ ${trade.stop_price:>7.0f} │ {trade.score:>5.0f} │\n"
        
        text += "└────────┴───────┴──────────┴─────────┴──────────┴───────┘\n"
        text += "\n💡 RECOMMENDATION: Pick top 1-2. Start with #1.\n"
    
    text += "\n" + "="*60 + "\n"
    text += f"Scan completed in {result['scan_time']:.1f} seconds\n"
    
    return text
