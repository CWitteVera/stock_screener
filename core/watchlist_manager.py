"""
Watchlist management system with momentum tracking
"""

import json
import os
from datetime import date, datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from models.watchlist_stock import WatchlistStock
from models.stock import Stock
from core.technical_analysis import calculate_all_indicators
from core.scoring_engine import calculate_overall_score
from core.return_estimator import estimate_return_potential


class WatchlistManager:
    """
    Manages watchlist stocks with momentum tracking and alerts
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize watchlist manager
        
        Args:
            data_path: Path to watchlist JSON file
        """
        if data_path is None:
            # Default path
            base_dir = Path(__file__).parent.parent
            data_path = base_dir / "data" / "watchlist" / "watchlist.json"
        
        self.data_path = Path(data_path)
        self.watchlist: Dict[str, WatchlistStock] = {}
        self.load()
    
    def add_stock(
        self, 
        symbol: str, 
        reason: str, 
        stock: Optional[Stock] = None,
        notes: str = ""
    ) -> Tuple[bool, str]:
        """
        Add stock to watchlist
        
        Args:
            symbol: Stock symbol
            reason: Reason for adding (IMPROVING_TREND, OVERSOLD_BOUNCE, etc.)
            stock: Optional Stock object with current data
            notes: Additional notes
            
        Returns:
            (success, message)
        """
        try:
            # Check if already exists
            if symbol in self.watchlist:
                return False, f"{symbol} is already on watchlist"
            
            # Create watchlist stock
            watchlist_stock = WatchlistStock(
                symbol=symbol,
                added_date=date.today(),
                reason=reason,
                notes=notes
            )
            
            # If stock data provided, set initial metrics
            if stock:
                watchlist_stock.initial_score = stock.overall_score or 0.0
                watchlist_stock.initial_return_potential = stock.estimated_return or 0.0
                watchlist_stock.initial_confidence = int(stock.confidence or 0)
                
                watchlist_stock.current_score = stock.overall_score or 0.0
                watchlist_stock.current_return_potential = stock.estimated_return or 0.0
                watchlist_stock.current_confidence = int(stock.confidence or 0)
            
            self.watchlist[symbol] = watchlist_stock
            self.save()
            
            return True, f"Added {symbol} to watchlist ({reason})"
            
        except Exception as e:
            return False, f"Error adding {symbol}: {str(e)}"
    
    def remove_stock(self, symbol: str, reason: str = "") -> Tuple[bool, str]:
        """
        Remove stock from watchlist
        
        Args:
            symbol: Stock symbol
            reason: Reason for removal
            
        Returns:
            (success, message)
        """
        try:
            if symbol not in self.watchlist:
                return False, f"{symbol} not found in watchlist"
            
            del self.watchlist[symbol]
            self.save()
            
            msg = f"Removed {symbol} from watchlist"
            if reason:
                msg += f" ({reason})"
            
            return True, msg
            
        except Exception as e:
            return False, f"Error removing {symbol}: {str(e)}"
    
    def update_stock_metrics(
        self, 
        symbol: str, 
        stock: Stock
    ) -> Tuple[bool, str]:
        """
        Update metrics for a watchlist stock
        
        Args:
            symbol: Stock symbol
            stock: Stock object with current data
            
        Returns:
            (success, message)
        """
        try:
            if symbol not in self.watchlist:
                return False, f"{symbol} not found in watchlist"
            
            watchlist_stock = self.watchlist[symbol]
            
            # Update metrics
            score = stock.overall_score or 0.0
            return_potential = stock.estimated_return or 0.0
            confidence = int(stock.confidence or 0)
            
            watchlist_stock.update_metrics(score, return_potential, confidence)
            
            # Estimate days to criteria
            watchlist_stock.days_until_potential = watchlist_stock.estimate_days_to_criteria()
            
            self.save()
            
            # Check if alert triggered
            if watchlist_stock.alert_triggered:
                return True, f"✓ Updated {symbol} - ALERT: Meets criteria!"
            
            return True, f"Updated {symbol} - Score: {score:.1f}, Return: {return_potential:.1f}%, Trend: {watchlist_stock.score_trend}"
            
        except Exception as e:
            return False, f"Error updating {symbol}: {str(e)}"
    
    def update_all_stocks(self, get_stock_func) -> Dict[str, str]:
        """
        Update all watchlist stocks
        
        Args:
            get_stock_func: Function to fetch stock data (symbol -> Stock)
            
        Returns:
            Dict of symbol -> status message
        """
        results = {}
        
        for symbol in list(self.watchlist.keys()):
            try:
                # Fetch current data
                stock = get_stock_func(symbol)
                
                if stock is None:
                    results[symbol] = "Error: Could not fetch data"
                    continue
                
                success, msg = self.update_stock_metrics(symbol, stock)
                results[symbol] = msg
                
            except Exception as e:
                results[symbol] = f"Error: {str(e)}"
        
        return results
    
    def get_stocks_by_trend(self, trend: str) -> List[WatchlistStock]:
        """
        Get stocks filtered by trend
        
        Args:
            trend: IMPROVING, DECLINING, or STABLE
            
        Returns:
            List of watchlist stocks
        """
        return [
            stock for stock in self.watchlist.values()
            if stock.score_trend == trend
        ]
    
    def get_alert_stocks(self) -> List[WatchlistStock]:
        """
        Get stocks with triggered alerts
        
        Returns:
            List of stocks that meet criteria
        """
        return [
            stock for stock in self.watchlist.values()
            if stock.alert_triggered
        ]
    
    def get_near_criteria_stocks(
        self, 
        min_return: float = 15.0, 
        min_confidence: int = 80,
        threshold: float = 5.0
    ) -> List[WatchlistStock]:
        """
        Get stocks near meeting criteria
        
        Args:
            min_return: Target return threshold
            min_confidence: Target confidence threshold
            threshold: How close to threshold (e.g., 5% below)
            
        Returns:
            List of stocks close to criteria
        """
        near_stocks = []
        
        for stock in self.watchlist.values():
            return_diff = min_return - stock.current_return_potential
            confidence_diff = min_confidence - stock.current_confidence
            
            # Check if within threshold
            if (0 < return_diff <= threshold) or (0 < confidence_diff <= 10):
                near_stocks.append(stock)
        
        return near_stocks
    
    def check_removal_criteria(
        self, 
        max_days: int = 30,
        declining_days: int = 5
    ) -> List[str]:
        """
        Check which stocks should be removed
        
        Args:
            max_days: Remove after this many days on watchlist
            declining_days: Remove if declining trend for this many days
            
        Returns:
            List of symbols to consider removing
        """
        to_remove = []
        
        for symbol, stock in self.watchlist.items():
            # Too long on watchlist
            if stock.days_on_watchlist > max_days:
                to_remove.append(symbol)
                continue
            
            # Declining for too long
            if stock.score_trend == "DECLINING":
                # Check if score dropped significantly
                score_change = stock.get_score_change()
                if score_change < -10:
                    to_remove.append(symbol)
        
        return to_remove
    
    def get_all_stocks(self, sort_by: str = "added_date") -> List[WatchlistStock]:
        """
        Get all watchlist stocks
        
        Args:
            sort_by: Sort field (added_date, score, return_potential, days_on_watchlist)
            
        Returns:
            Sorted list of stocks
        """
        stocks = list(self.watchlist.values())
        
        if sort_by == "score":
            stocks.sort(key=lambda s: s.current_score, reverse=True)
        elif sort_by == "return_potential":
            stocks.sort(key=lambda s: s.current_return_potential, reverse=True)
        elif sort_by == "days_on_watchlist":
            stocks.sort(key=lambda s: s.days_on_watchlist, reverse=True)
        else:  # added_date
            stocks.sort(key=lambda s: s.added_date)
        
        return stocks
    
    def get_stock(self, symbol: str) -> Optional[WatchlistStock]:
        """Get specific stock from watchlist"""
        return self.watchlist.get(symbol)
    
    def export_to_dict(self) -> Dict:
        """
        Export watchlist to dictionary
        
        Returns:
            Dict with watchlist data and metadata
        """
        return {
            'updated': datetime.now().isoformat(),
            'total_stocks': len(self.watchlist),
            'stocks': {
                symbol: stock.to_dict()
                for symbol, stock in self.watchlist.items()
            }
        }
    
    def save(self):
        """Save watchlist to JSON file"""
        try:
            # Ensure directory exists
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = self.export_to_dict()
            
            with open(self.data_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving watchlist: {e}")
    
    def load(self):
        """Load watchlist from JSON file"""
        try:
            if not self.data_path.exists():
                # Create empty file
                self.watchlist = {}
                self.save()
                return
            
            with open(self.data_path, 'r') as f:
                data = json.load(f)
            
            # Load stocks
            if 'stocks' in data:
                for symbol, stock_data in data['stocks'].items():
                    self.watchlist[symbol] = WatchlistStock.from_dict(stock_data)
            
        except Exception as e:
            print(f"Error loading watchlist: {e}")
            self.watchlist = {}
    
    def get_statistics(self) -> Dict:
        """
        Get watchlist statistics
        
        Returns:
            Dict with statistics
        """
        if not self.watchlist:
            return {
                'total': 0,
                'improving': 0,
                'declining': 0,
                'stable': 0,
                'alerts': 0,
                'avg_days': 0,
                'avg_score': 0,
            }
        
        improving = len(self.get_stocks_by_trend("IMPROVING"))
        declining = len(self.get_stocks_by_trend("DECLINING"))
        stable = len(self.get_stocks_by_trend("STABLE"))
        alerts = len(self.get_alert_stocks())
        
        avg_days = sum(s.days_on_watchlist for s in self.watchlist.values()) / len(self.watchlist)
        avg_score = sum(s.current_score for s in self.watchlist.values()) / len(self.watchlist)
        
        return {
            'total': len(self.watchlist),
            'improving': improving,
            'declining': declining,
            'stable': stable,
            'alerts': alerts,
            'avg_days': round(avg_days, 1),
            'avg_score': round(avg_score, 1),
        }
