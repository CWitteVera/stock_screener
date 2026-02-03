"""
Utility helper functions
"""

import pandas as pd
from typing import List, Dict, Any
from datetime import datetime

def format_currency(value: float) -> str:
    """Format a value as currency"""
    return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    """Format a value as percentage"""
    return f"{value:.1f}%"

def calculate_shares_for_trade(price: float, capital: float) -> int:
    """Calculate number of shares that can be bought with given capital"""
    if price <= 0:
        return 0
    shares = int(capital / price)
    return shares

def calculate_position_value(shares: int, price: float) -> float:
    """Calculate total position value"""
    return shares * price

def get_star_rating(score: float) -> str:
    """Convert numeric score (0-100) to star rating"""
    if score >= 90:
        return "⭐⭐⭐⭐⭐"
    elif score >= 80:
        return "⭐⭐⭐⭐"
    elif score >= 70:
        return "⭐⭐⭐"
    elif score >= 60:
        return "⭐⭐"
    else:
        return "⭐"

def get_confidence_bar(confidence: float) -> str:
    """Convert confidence percentage to visual bar"""
    filled = int(confidence / 10)
    empty = 10 - filled
    return "●" * filled + "○" * empty

def format_timeframe_days(days: int) -> str:
    """Format days into readable timeframe"""
    if days == 1:
        return "1 day"
    return f"{days} days"

def get_rank_emoji(rank: int) -> str:
    """Get emoji for rank"""
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    else:
        return "  "

def get_tier_emoji(tier: int) -> str:
    """Get emoji for tier"""
    if tier == 1:
        return "🔥"
    elif tier == 2:
        return "⚠️"
    else:
        return "🛑"

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers"""
    if denominator == 0:
        return default
    return numerator / denominator
