"""
Simple file-based caching system
"""

import os
import pickle
import time
from pathlib import Path
from typing import Any, Optional
from config.settings import CACHE_DURATION_HOURS

class Cache:
    """Simple file-based cache for stock data"""
    
    def __init__(self, cache_dir: str = None):
        if cache_dir is None:
            base_dir = Path(__file__).parent.parent
            cache_dir = os.path.join(base_dir, 'data', 'cache')
        
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if it exists and hasn't expired"""
        cache_file = self._get_cache_file(key)
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            # Check if cache has expired
            timestamp = data.get('timestamp', 0)
            age_hours = (time.time() - timestamp) / 3600
            
            if age_hours > CACHE_DURATION_HOURS:
                # Cache expired, remove it
                os.remove(cache_file)
                return None
            
            return data.get('value')
        except Exception as e:
            print(f"Error reading cache for {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any):
        """Cache a value with current timestamp"""
        cache_file = self._get_cache_file(key)
        
        try:
            data = {
                'timestamp': time.time(),
                'value': value
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Error writing cache for {key}: {str(e)}")
    
    def clear(self, key: str = None):
        """Clear cache for a specific key or all cache"""
        if key:
            cache_file = self._get_cache_file(key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
        else:
            # Clear all cache
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    
    def _get_cache_file(self, key: str) -> str:
        """Get the cache file path for a key"""
        # Sanitize key for filename
        safe_key = key.replace('/', '_').replace('\\', '_')
        return os.path.join(self.cache_dir, f"{safe_key}.cache")
