"""
Main adaptive screener with intelligent tiering
"""

import time
from typing import List, Dict, Optional
from config.api_config import DataFetcher
from config.sectors import load_watchlist, get_sector_watchlist_path
from config.settings import (
    MIN_PRICE, MAX_PRICE, MIN_VOLUME, MIN_MARKET_CAP, MIN_VOLATILITY,
    TIER_1_MIN_RETURN, TIER_1_MIN_CONFIDENCE, TIER_2_MIN_RETURN, TIER_2_MIN_CONFIDENCE,
    CAPITAL_PER_TRADE, MAX_LOSS_PERCENT, MAX_HOLD_DAYS
)
from models.stock import Stock
from models.trade import Trade
from models.position import Position
from core.technical_analysis import calculate_all_indicators, calculate_volatility_percent, find_support_resistance
from core.scoring_engine import calculate_overall_score
from core.return_estimator import estimate_return_potential
from core.risk_calculator import (
    calculate_stop_loss, calculate_target_price, calculate_position_size,
    calculate_risk_reward, calculate_profit_loss, calculate_adjusted_stop_loss
)
from utils.cache import Cache
from utils.logger import logger
from utils.helpers import calculate_shares_for_trade
from datetime import date

class AdaptiveScreener:
    """
    Intelligent screener with adaptive return targeting
    15% → 8% → wait
    """
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.cache = Cache()
    
    def scan_sector(self, sector_name: str, min_return: float = TIER_1_MIN_RETURN) -> Dict:
        """
        Scan a sector for swing trade opportunities
        Returns results with tier classification
        """
        logger.info(f"Starting scan of {sector_name} sector")
        
        # Load watchlist
        watchlist_path = get_sector_watchlist_path(sector_name)
        symbols = load_watchlist(watchlist_path)
        
        if not symbols:
            logger.error(f"No symbols found in watchlist for {sector_name}")
            return self._empty_result()
        
        logger.info(f"Loaded {len(symbols)} symbols from {sector_name} watchlist")
        
        return self._scan_symbols(symbols, sector_name, min_return)
    
    def scan_watchlist(self, watchlist_path: str, min_return: float = TIER_1_MIN_RETURN) -> Dict:
        """
        Scan a custom watchlist
        """
        logger.info(f"Scanning custom watchlist: {watchlist_path}")
        
        symbols = load_watchlist(watchlist_path)
        
        if not symbols:
            logger.error(f"No symbols found in watchlist")
            return self._empty_result()
        
        return self._scan_symbols(symbols, "Custom", min_return)
    
    def _scan_symbols(self, symbols: List[str], sector_name: str, min_return: float) -> Dict:
        """
        Core scanning logic
        """
        start_time = time.time()
        
        # Stage 1: Fetch and pre-filter
        logger.info(f"Stage 1: Fetching data for {len(symbols)} symbols...")
        candidates = self._fetch_and_filter(symbols)
        logger.info(f"Stage 1 complete: {len(candidates)} candidates passed basic filters")
        
        if not candidates:
            return self._create_result([], 3, sector_name)
        
        # Stage 2: Technical analysis and scoring
        logger.info(f"Stage 2: Analyzing technical indicators...")
        scored_stocks = self._analyze_and_score(candidates)
        logger.info(f"Stage 2 complete: {len(scored_stocks)} stocks scored")
        
        if not scored_stocks:
            return self._create_result([], 3, sector_name)
        
        # Stage 3: Estimate return potential
        logger.info(f"Stage 3: Estimating return potential...")
        estimated_stocks = self._estimate_returns(scored_stocks)
        
        # Stage 4: Adaptive tiering
        logger.info(f"Stage 4: Categorizing opportunities...")
        result = self._categorize_and_rank(estimated_stocks, sector_name)
        
        elapsed = time.time() - start_time
        logger.info(f"Scan complete in {elapsed:.1f} seconds")
        result['scan_time'] = elapsed
        
        return result
    
    def _fetch_and_filter(self, symbols: List[str]) -> List[Stock]:
        """
        Stage 1: Fetch data and apply basic filters
        """
        candidates = []
        
        for symbol in symbols:
            try:
                # Try cache first
                cached = self.cache.get(f"stock_{symbol}")
                if cached:
                    stock_data = cached
                else:
                    stock_data = self.data_fetcher.get_stock_data(symbol)
                    if stock_data:
                        self.cache.set(f"stock_{symbol}", stock_data)
                
                if not stock_data:
                    continue
                
                # Create Stock object
                stock = Stock(
                    symbol=stock_data['symbol'],
                    name=stock_data['name'],
                    current_price=stock_data['current_price'],
                    sector=stock_data['sector'],
                    market_cap=stock_data['market_cap'],
                    volume=stock_data['volume'],
                    avg_volume=stock_data['avg_volume'],
                    history=stock_data['history'],
                    info=stock_data['info']
                )
                
                # Apply basic filters
                if not stock.passes_basic_filters(MIN_PRICE, MAX_PRICE, MIN_VOLUME, MIN_MARKET_CAP):
                    continue
                
                # Check volatility
                df = calculate_all_indicators(stock.history)
                volatility = calculate_volatility_percent(df)
                
                if volatility < MIN_VOLATILITY:
                    continue
                
                # Check not in downtrend
                if 'SMA_50' in df.columns:
                    sma_50 = df['SMA_50'].iloc[-1]
                    if not pd.isna(sma_50) and stock.current_price < sma_50:
                        continue
                
                candidates.append(stock)
                
            except Exception as e:
                logger.warning(f"Error processing {symbol}: {str(e)}")
                continue
        
        return candidates
    
    def _analyze_and_score(self, stocks: List[Stock]) -> List[Stock]:
        """
        Stage 2: Calculate technical indicators and score stocks
        """
        scored = []
        
        for stock in stocks:
            try:
                # Calculate all indicators
                df = calculate_all_indicators(stock.history)
                
                # Get latest values
                if 'RSI' in df.columns:
                    stock.rsi = df['RSI'].iloc[-1]
                if 'MACD' in df.columns:
                    stock.macd = df['MACD'].iloc[-1]
                    stock.macd_signal = df['MACD_signal'].iloc[-1]
                    stock.macd_histogram = df['MACD_hist'].iloc[-1]
                if 'SMA_20' in df.columns:
                    stock.sma_20 = df['SMA_20'].iloc[-1]
                if 'SMA_50' in df.columns:
                    stock.sma_50 = df['SMA_50'].iloc[-1]
                if 'ATR' in df.columns:
                    stock.atr = df['ATR'].iloc[-1]
                
                # Calculate scores
                stock_data = {
                    'symbol': stock.symbol,
                    'current_price': stock.current_price
                }
                
                scores = calculate_overall_score(stock_data, df)
                stock.macd_score = scores['macd_score']
                stock.rsi_score = scores['rsi_score']
                stock.volume_score = scores['volume_score']
                stock.breakout_score = scores['breakout_score']
                stock.momentum_score = scores['momentum_score']
                stock.overall_score = scores['overall_score']
                
                # Update history with indicators
                stock.history = df
                
                scored.append(stock)
                
            except Exception as e:
                logger.warning(f"Error scoring {stock.symbol}: {str(e)}")
                continue
        
        return scored
    
    def _estimate_returns(self, stocks: List[Stock]) -> List[Stock]:
        """
        Stage 3: Estimate return potential for each stock
        """
        estimated = []
        
        for stock in stocks:
            try:
                stock_data = {
                    'symbol': stock.symbol,
                    'current_price': stock.current_price
                }
                
                est_return, confidence, days = estimate_return_potential(stock_data, stock.history)
                
                stock.estimated_return = est_return
                stock.confidence = confidence
                stock.days_to_target = days
                
                estimated.append(stock)
                
            except Exception as e:
                logger.warning(f"Error estimating returns for {stock.symbol}: {str(e)}")
                continue
        
        return estimated
    
    def _categorize_and_rank(self, stocks: List[Stock], sector_name: str) -> Dict:
        """
        Stage 4: Categorize into tiers and rank
        """
        # Filter and sort
        tier_1_stocks = [
            s for s in stocks
            if s.estimated_return >= TIER_1_MIN_RETURN and s.confidence >= TIER_1_MIN_CONFIDENCE
        ]
        
        tier_2_stocks = [
            s for s in stocks
            if TIER_2_MIN_RETURN <= s.estimated_return < TIER_1_MIN_RETURN 
            and s.confidence >= TIER_2_MIN_CONFIDENCE
        ]
        
        # Sort by overall score
        tier_1_stocks.sort(key=lambda x: x.overall_score, reverse=True)
        tier_2_stocks.sort(key=lambda x: x.overall_score, reverse=True)
        
        # Determine tier
        if len(tier_1_stocks) >= 3:
            tier = 1
            top_stocks = tier_1_stocks[:5]
        elif len(tier_2_stocks) >= 3:
            tier = 2
            top_stocks = tier_2_stocks[:5]
        else:
            tier = 3
            top_stocks = []
        
        return self._create_result(top_stocks, tier, sector_name)
    
    def _create_result(self, stocks: List[Stock], tier: int, sector_name: str) -> Dict:
        """
        Create result dictionary with tier information
        """
        # Convert stocks to trades
        trades = []
        for stock in stocks:
            trade = self._create_trade_from_stock(stock)
            if trade:
                trades.append(trade)
        
        # Tier-specific messaging
        if tier == 1:
            mode = "AGGRESSIVE OPPORTUNITIES"
            recommendation = f"🔥 {len(trades)} high-confidence trades with 15%+ potential found. TRADE NOW!"
            risk_level = "HIGH"
        elif tier == 2:
            mode = "MODERATE OPPORTUNITIES"
            recommendation = f"⚠️ {len(trades)} moderate trades with 8-14% potential. Consider smaller positions or wait for better setups."
            risk_level = "MEDIUM"
        else:
            mode = "WEAK MARKET CONDITIONS"
            recommendation = "🛑 No stocks meet 8%+ return criteria. HOLD CASH - Wait for better opportunities."
            risk_level = "LOW"
        
        return {
            'tier': tier,
            'mode': mode,
            'recommendation': recommendation,
            'risk_level': risk_level,
            'sector': sector_name,
            'trades': trades,
            'scan_time': 0,
            'timestamp': date.today().isoformat()
        }
    
    def _create_trade_from_stock(self, stock: Stock) -> Optional[Trade]:
        """
        Convert Stock to Trade opportunity
        """
        try:
            entry_price = stock.current_price
            target_price = calculate_target_price(entry_price, stock.estimated_return)
            stop_price = calculate_stop_loss(entry_price, MAX_LOSS_PERCENT)
            
            # Get support levels for better stop placement
            levels = find_support_resistance(stock.history)
            support_levels = levels.get('support_levels', [])
            
            # Adjust stop loss based on support
            if support_levels:
                adjusted_stop = calculate_adjusted_stop_loss(entry_price, support_levels, MAX_LOSS_PERCENT)
                stop_price = max(stop_price, adjusted_stop)  # Use whichever is higher (less risk)
            
            # Calculate position
            shares, position_value = calculate_position_size(entry_price, CAPITAL_PER_TRADE)
            
            if shares == 0:
                return None
            
            # Calculate P&L
            target_profit, max_loss = calculate_profit_loss(entry_price, target_price, stop_price, shares)
            risk_reward = calculate_risk_reward(entry_price, target_price, stop_price)
            
            # Entry strategy
            entry_range_low = entry_price * 0.99
            entry_range_high = entry_price * 1.03
            entry_strategy = f"Best: Market open or pullback to ${entry_range_low:.2f}-${entry_price:.2f}. Avoid chasing above ${entry_range_high:.2f}"
            
            trade = Trade(
                symbol=stock.symbol,
                name=stock.name,
                entry_price=entry_price,
                target_price=target_price,
                stop_price=stop_price,
                estimated_return=stock.estimated_return,
                confidence=stock.confidence,
                days_to_target=stock.days_to_target,
                score=stock.overall_score,
                sector=stock.sector,
                shares=shares,
                position_value=position_value,
                target_profit=target_profit,
                max_loss=max_loss,
                risk_reward_ratio=risk_reward,
                current_price=stock.current_price,
                rsi=stock.rsi,
                macd_score=stock.macd_score,
                volume_score=stock.volume_score,
                breakout_score=stock.breakout_score,
                momentum_score=stock.momentum_score,
                entry_strategy=entry_strategy,
                support_levels=[f"${s:.2f}" for s in support_levels[:3]]
            )
            
            return trade
            
        except Exception as e:
            logger.error(f"Error creating trade for {stock.symbol}: {str(e)}")
            return None
    
    def monitor_position(self, symbol: str):
        """
        Monitor an active position
        """
        position = Position.load(symbol)
        
        if not position:
            logger.error(f"No active position found for {symbol}")
            return None
        
        # Get current data
        stock_data = self.data_fetcher.get_stock_data(symbol)
        
        if not stock_data:
            logger.error(f"Could not fetch data for {symbol}")
            return None
        
        # Calculate indicators
        df = calculate_all_indicators(stock_data['history'])
        
        # Technical data
        technical_data = {
            'above_20ma': stock_data['current_price'] > df['SMA_20'].iloc[-1] if 'SMA_20' in df.columns else None,
            'rsi': df['RSI'].iloc[-1] if 'RSI' in df.columns else None,
            'macd_bullish': df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1] if 'MACD' in df.columns else None,
            'volume_above_avg': stock_data['volume'] > stock_data['avg_volume']
        }
        
        # Update position
        position.update(stock_data['current_price'], technical_data)
        position.save()
        
        return position
    
    def _empty_result(self):
        """Return empty result for errors"""
        return self._create_result([], 3, "Unknown")


# Import pandas for the NA checks
import pandas as pd
