"""
API Configuration Manager
Handles data fetching from multiple sources with intelligent fallback
"""

import yfinance as yf
import os
from dotenv import load_dotenv
import requests
from typing import Dict, Any, Optional
import time

class DataFetcher:
    """
    Fetch stock data - primarily from yfinance (free)
    Optionally enhance with FMP if API key provided
    """
    
    def __init__(self):
        load_dotenv()
        self.fmp_api_key = os.getenv('FMP_API_KEY', None)
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', None)
        self.use_fmp = self.fmp_api_key is not None and self.fmp_api_key != 'your_fmp_api_key_here'
        self.fmp_calls_today = 0
        self.fmp_limit = 250
        
    def get_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch all necessary data for a stock using yfinance
        Returns None if data cannot be fetched
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data (free, unlimited)
            hist = ticker.history(period='3mo')  # 3 months of data
            
            if hist.empty:
                return None
            
            # Get current info (free)
            info = ticker.info
            
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if current_price is None and not hist.empty:
                current_price = hist['Close'].iloc[-1]
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'history': hist,
                'volume': hist['Volume'].iloc[-1],
                'avg_volume': hist['Volume'].mean(),
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'name': info.get('longName', symbol),
                'info': info
            }
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get fundamental data
        Uses FMP if available, otherwise basic yfinance info
        """
        if self.use_fmp and self.fmp_calls_today < self.fmp_limit:
            try:
                return self._get_fmp_fundamentals(symbol)
            except Exception as e:
                print(f"FMP error for {symbol}, falling back to yfinance: {str(e)}")
        
        # Fallback to yfinance
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                'earnings_date': info.get('earningsDate', None),
                'pe_ratio': info.get('trailingPE', None),
                'forward_pe': info.get('forwardPE', None),
                'analyst_target': info.get('targetMeanPrice', None),
                'recommendation': info.get('recommendationKey', None),
            }
        except Exception as e:
            print(f"Error fetching fundamentals for {symbol}: {str(e)}")
            return {}
    
    def _get_fmp_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch fundamental data from Financial Modeling Prep
        """
        self.fmp_calls_today += 1
        
        # Get key metrics
        url = f"https://financialmodelingprep.com/api/v3/key-metrics/{symbol}"
        params = {'apikey': self.fmp_api_key, 'limit': 1}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if not data:
            return {}
        
        metrics = data[0] if isinstance(data, list) else data
        
        return {
            'pe_ratio': metrics.get('peRatio'),
            'price_to_book': metrics.get('pbRatio'),
            'debt_to_equity': metrics.get('debtToEquity'),
            'roe': metrics.get('roe'),
        }
    
    def get_analyst_targets(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get analyst price targets
        Only available with FMP API
        """
        if not self.use_fmp or self.fmp_calls_today >= self.fmp_limit:
            return None
        
        try:
            self.fmp_calls_today += 1
            url = f"https://financialmodelingprep.com/api/v3/analyst-estimates/{symbol}"
            params = {'apikey': self.fmp_api_key, 'limit': 1}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data:
                return data[0] if isinstance(data, list) else data
        except Exception as e:
            print(f"Error fetching analyst targets for {symbol}: {str(e)}")
        
        return None
    
    def reset_daily_limits(self):
        """Reset daily API call counters"""
        self.fmp_calls_today = 0
