"""
Risk calculation and position sizing
"""

from typing import Tuple
from config.settings import CAPITAL_PER_TRADE, MAX_LOSS_PERCENT, MIN_RISK_REWARD_RATIO

def calculate_stop_loss(entry_price: float, max_loss_percent: float = MAX_LOSS_PERCENT) -> float:
    """
    Calculate stop loss price
    """
    return entry_price * (1 - max_loss_percent / 100)

def calculate_target_price(entry_price: float, target_return_percent: float) -> float:
    """
    Calculate target price
    """
    return entry_price * (1 + target_return_percent / 100)

def calculate_position_size(entry_price: float, capital: float = CAPITAL_PER_TRADE) -> Tuple[int, float]:
    """
    Calculate number of shares and actual position value
    Returns: (shares, position_value)
    """
    if entry_price <= 0:
        return 0, 0.0
    
    shares = int(capital / entry_price)
    position_value = shares * entry_price
    
    return shares, position_value

def calculate_risk_reward(entry_price: float, target_price: float, stop_price: float) -> float:
    """
    Calculate risk/reward ratio
    """
    potential_gain = target_price - entry_price
    potential_loss = entry_price - stop_price
    
    if potential_loss <= 0:
        return 0.0
    
    return potential_gain / potential_loss

def calculate_profit_loss(entry_price: float, target_price: float, 
                         stop_price: float, shares: int) -> Tuple[float, float]:
    """
    Calculate potential profit and maximum loss in dollars
    Returns: (target_profit, max_loss)
    """
    target_profit = (target_price - entry_price) * shares
    max_loss = (entry_price - stop_price) * shares
    
    return target_profit, max_loss

def validate_trade_risk(entry_price: float, target_price: float, 
                        stop_price: float) -> Tuple[bool, str]:
    """
    Validate if trade meets risk management criteria
    Returns: (is_valid, reason)
    """
    
    # Check risk/reward ratio
    rr_ratio = calculate_risk_reward(entry_price, target_price, stop_price)
    
    if rr_ratio < MIN_RISK_REWARD_RATIO:
        return False, f"Risk/Reward ratio {rr_ratio:.2f} is below minimum {MIN_RISK_REWARD_RATIO}"
    
    # Check stop loss is reasonable
    stop_loss_pct = ((entry_price - stop_price) / entry_price) * 100
    if stop_loss_pct > MAX_LOSS_PERCENT * 1.2:  # Allow 20% buffer
        return False, f"Stop loss {stop_loss_pct:.1f}% exceeds maximum {MAX_LOSS_PERCENT}%"
    
    return True, "Trade passes risk criteria"

def calculate_adjusted_stop_loss(entry_price: float, support_levels: list, 
                                 max_loss_percent: float = MAX_LOSS_PERCENT) -> float:
    """
    Calculate stop loss considering support levels
    Places stop just below nearest support, but not exceeding max loss
    """
    default_stop = calculate_stop_loss(entry_price, max_loss_percent)
    
    if not support_levels:
        return default_stop
    
    # Find nearest support below entry
    valid_supports = [s for s in support_levels if s < entry_price]
    
    if not valid_supports:
        return default_stop
    
    nearest_support = max(valid_supports)
    
    # Place stop 1% below support
    adjusted_stop = nearest_support * 0.99
    
    # Don't exceed max loss
    if adjusted_stop < default_stop:
        return default_stop
    
    return adjusted_stop
