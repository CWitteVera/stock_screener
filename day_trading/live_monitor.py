"""
Live position monitoring for day trades - checks every 15 minutes
"""

import json
import yfinance as yf
from datetime import datetime, time, timedelta
from typing import List, Dict, Optional
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.day_trade_opportunity import DayTradeOpportunity
from config.settings import DAY_TRADE_CHECK_INTERVAL, DAY_TRADE_FORCE_EXIT_TIME


class MonitoredTrade:
    """Represents a trade being monitored (executed or educational)"""
    
    def __init__(self, opportunity: DayTradeOpportunity, executed: bool = False):
        self.opportunity = opportunity
        self.executed = executed  # True if real trade, False if monitor-only
        self.entry_time = datetime.now()
        self.entry_price = opportunity.entry_price
        self.target_price = opportunity.target_price
        self.stop_price = opportunity.stop_price
        self.current_price = opportunity.current_price
        self.current_pnl = 0.0
        self.current_pnl_pct = 0.0
        self.status = "MONITORING"  # MONITORING, TARGET_HIT, STOP_HIT, FORCE_EXIT
        self.exit_time = None
        self.exit_price = None
        self.checks = []  # List of check timestamps and prices
        
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON storage"""
        return {
            'symbol': self.opportunity.symbol,
            'name': self.opportunity.name,
            'sector': self.opportunity.sector,
            'setup_type': self.opportunity.setup_type,
            'executed': self.executed,
            'entry_time': self.entry_time.isoformat(),
            'entry_price': self.entry_price,
            'target_price': self.target_price,
            'stop_price': self.stop_price,
            'shares': self.opportunity.shares,
            'position_value': self.opportunity.position_value,
            'current_price': self.current_price,
            'current_pnl': self.current_pnl,
            'current_pnl_pct': self.current_pnl_pct,
            'status': self.status,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'exit_price': self.exit_price,
            'estimated_return_pct': self.opportunity.estimated_return_pct,
            'confidence': self.opportunity.confidence,
            'catalyst': self.opportunity.catalyst,
            'checks': self.checks,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MonitoredTrade':
        """Create from dictionary"""
        # Create a minimal opportunity object
        opp = DayTradeOpportunity(
            symbol=data['symbol'],
            name=data['name'],
            current_price=data['current_price'],
            sector=data['sector'],
            entry_price=data['entry_price'],
            target_price=data['target_price'],
            stop_price=data['stop_price'],
            estimated_return_pct=data['estimated_return_pct'],
            estimated_return_dollars=0,
            estimated_time_minutes=0,
            confidence=data['confidence'],
            shares=data['shares'],
            position_value=data['position_value'],
            setup_type=data['setup_type'],
            catalyst=data['catalyst'],
        )
        
        trade = cls(opp, data['executed'])
        trade.entry_time = datetime.fromisoformat(data['entry_time'])
        trade.current_price = data['current_price']
        trade.current_pnl = data['current_pnl']
        trade.current_pnl_pct = data['current_pnl_pct']
        trade.status = data['status']
        trade.exit_time = datetime.fromisoformat(data['exit_time']) if data['exit_time'] else None
        trade.exit_price = data['exit_price']
        trade.checks = data.get('checks', [])
        
        return trade


class LiveMonitor:
    """
    Monitor day trade positions every 15 minutes
    Track both executed and educational (monitor-only) trades
    """
    
    def __init__(self, check_interval: int = DAY_TRADE_CHECK_INTERVAL):
        self.check_interval = check_interval  # minutes
        self.monitored_trades: List[MonitoredTrade] = []
        
        # Use relative path from script location
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_file = os.path.join(base_dir, 'data', 'day_trading', 'monitored_trades.json')
        self._load_trades()
        
        # Parse force exit time
        force_exit_parts = DAY_TRADE_FORCE_EXIT_TIME.split(":")
        self.force_exit_time = time(int(force_exit_parts[0]), int(force_exit_parts[1]))
    
    def add_trade(self, opportunity: DayTradeOpportunity, executed: bool = False):
        """Add a trade to monitoring"""
        trade = MonitoredTrade(opportunity, executed)
        self.monitored_trades.append(trade)
        self._save_trades()
        
        mode = "EXECUTED" if executed else "MONITOR-ONLY (Educational)"
        print(f"\n✅ Added to monitoring: {opportunity.symbol} - {mode}")
        print(f"   Entry: ${opportunity.entry_price:.2f} | Target: ${opportunity.target_price:.2f} | Stop: ${opportunity.stop_price:.2f}")
        print(f"   Shares: {opportunity.shares} (${opportunity.position_value:.2f})")
    
    def check_positions(self):
        """Check all monitored positions"""
        print("\n" + "=" * 80)
        print(f"POSITION CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        if not self.monitored_trades:
            print("\n📭 No positions currently monitored")
            return
        
        active_trades = [t for t in self.monitored_trades if t.status == "MONITORING"]
        
        if not active_trades:
            print("\n📭 No active positions (all closed)")
            self._print_closed_summary()
            return
        
        print(f"\n📊 Monitoring {len(active_trades)} active position(s):\n")
        
        for trade in active_trades:
            self._check_single_position(trade)
        
        self._save_trades()
        
        # Print summary
        self._print_monitoring_summary()
    
    def _check_single_position(self, trade: MonitoredTrade):
        """Check a single position and update status"""
        symbol = trade.opportunity.symbol
        
        try:
            # Get current price
            ticker = yf.Ticker(symbol)
            current_price = ticker.info.get('currentPrice', ticker.info.get('regularMarketPrice', 0))
            
            if current_price == 0:
                print(f"⚠️  {symbol}: Unable to get current price")
                return
            
            # Update price and P&L
            trade.current_price = current_price
            price_diff = current_price - trade.entry_price
            trade.current_pnl = price_diff * trade.opportunity.shares
            trade.current_pnl_pct = (price_diff / trade.entry_price) * 100
            
            # Record this check
            trade.checks.append({
                'time': datetime.now().isoformat(),
                'price': current_price,
                'pnl': trade.current_pnl,
                'pnl_pct': trade.current_pnl_pct,
            })
            
            # Check exit conditions
            exit_reason = None
            
            # 1. Target hit
            if current_price >= trade.target_price:
                trade.status = "TARGET_HIT"
                trade.exit_time = datetime.now()
                trade.exit_price = current_price
                exit_reason = "🎯 TARGET HIT"
            
            # 2. Stop hit
            elif current_price <= trade.stop_price:
                trade.status = "STOP_HIT"
                trade.exit_time = datetime.now()
                trade.exit_price = current_price
                exit_reason = "🛑 STOP LOSS"
            
            # 3. Force exit time
            elif datetime.now().time() >= self.force_exit_time:
                trade.status = "FORCE_EXIT"
                trade.exit_time = datetime.now()
                trade.exit_price = current_price
                exit_reason = "⏰ FORCE EXIT (3:45 PM)"
            
            # Print status
            mode_indicator = "💰" if trade.executed else "📚"
            status_emoji = "📈" if trade.current_pnl >= 0 else "📉"
            
            print(f"{mode_indicator} {symbol} - {trade.opportunity.name}")
            print(f"   Entry: ${trade.entry_price:.2f} → Current: ${current_price:.2f}")
            print(f"   Target: ${trade.target_price:.2f} | Stop: ${trade.stop_price:.2f}")
            print(f"   {status_emoji} P&L: ${trade.current_pnl:+.2f} ({trade.current_pnl_pct:+.2f}%)")
            print(f"   Time in trade: {self._time_in_trade(trade)}")
            
            if exit_reason:
                print(f"   ⚠️  {exit_reason}")
                print(f"   Final P&L: ${trade.current_pnl:+.2f} ({trade.current_pnl_pct:+.2f}%)")
            else:
                # Check if approaching force exit
                minutes_to_exit = self._minutes_until_force_exit()
                if minutes_to_exit is not None and minutes_to_exit <= 30:
                    print(f"   ⚠️  WARNING: Force exit in {minutes_to_exit} minutes!")
            
            print()
            
        except Exception as e:
            print(f"❌ Error checking {symbol}: {e}\n")
    
    def get_active_trades(self) -> List[MonitoredTrade]:
        """Get list of currently active trades"""
        return [t for t in self.monitored_trades if t.status == "MONITORING"]
    
    def get_closed_trades(self) -> List[MonitoredTrade]:
        """Get list of closed trades"""
        return [t for t in self.monitored_trades if t.status != "MONITORING"]
    
    def get_todays_trades(self) -> List[MonitoredTrade]:
        """Get trades from today"""
        today = datetime.now().date()
        return [t for t in self.monitored_trades if t.entry_time.date() == today]
    
    def _time_in_trade(self, trade: MonitoredTrade) -> str:
        """Calculate time in trade"""
        delta = datetime.now() - trade.entry_time
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    
    def _minutes_until_force_exit(self) -> Optional[int]:
        """Calculate minutes until force exit time"""
        now = datetime.now()
        force_exit_dt = datetime.combine(now.date(), self.force_exit_time)
        
        if now >= force_exit_dt:
            return 0
        
        delta = force_exit_dt - now
        return int(delta.total_seconds() / 60)
    
    def _print_monitoring_summary(self):
        """Print summary of all monitored trades"""
        active = self.get_active_trades()
        closed = self.get_closed_trades()
        
        print("\n" + "-" * 80)
        print("MONITORING SUMMARY")
        print("-" * 80)
        
        # Active trades
        if active:
            total_pnl = sum(t.current_pnl for t in active)
            print(f"\n📊 Active Positions: {len(active)}")
            print(f"   Total P&L: ${total_pnl:+.2f}")
        
        # Today's closed trades
        todays_closed = [t for t in closed if t.entry_time.date() == datetime.now().date()]
        if todays_closed:
            total_pnl = sum(t.current_pnl for t in todays_closed)
            wins = len([t for t in todays_closed if t.current_pnl > 0])
            print(f"\n✅ Today's Closed: {len(todays_closed)} ({wins} wins)")
            print(f"   Total P&L: ${total_pnl:+.2f}")
    
    def _print_closed_summary(self):
        """Print summary of closed trades"""
        closed = self.get_todays_trades()
        if closed:
            print("\n📋 Today's Closed Trades:\n")
            for trade in closed:
                mode = "💰 EXECUTED" if trade.executed else "📚 MONITORED"
                print(f"{mode} {trade.opportunity.symbol}: {trade.status}")
                print(f"   Entry: ${trade.entry_price:.2f} → Exit: ${trade.exit_price:.2f}")
                print(f"   P&L: ${trade.current_pnl:+.2f} ({trade.current_pnl_pct:+.2f}%)")
                print()
    
    def _save_trades(self):
        """Save monitored trades to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            data = {
                'last_updated': datetime.now().isoformat(),
                'trades': [t.to_dict() for t in self.monitored_trades],
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Error saving trades: {e}")
    
    def _load_trades(self):
        """Load monitored trades from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    
                self.monitored_trades = [
                    MonitoredTrade.from_dict(t) for t in data.get('trades', [])
                ]
                
                # Filter out old trades (older than 1 day if closed)
                one_day_ago = datetime.now() - timedelta(days=1)
                self.monitored_trades = [
                    t for t in self.monitored_trades
                    if t.status == "MONITORING" or t.entry_time > one_day_ago
                ]
                
        except Exception as e:
            print(f"⚠️  Error loading trades: {e}")
            self.monitored_trades = []
    
    def clear_old_trades(self, days: int = 7):
        """Clear trades older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        original_count = len(self.monitored_trades)
        
        self.monitored_trades = [
            t for t in self.monitored_trades
            if t.entry_time > cutoff or t.status == "MONITORING"
        ]
        
        removed = original_count - len(self.monitored_trades)
        if removed > 0:
            print(f"🗑️  Removed {removed} old trade(s)")
            self._save_trades()


if __name__ == "__main__":
    # Test the monitor
    monitor = LiveMonitor()
    monitor.check_positions()
