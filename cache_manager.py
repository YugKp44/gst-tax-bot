# cache_manager.py - Simple caching for improved performance

import hashlib
import json
from typing import Any, Optional, Dict
from collections import OrderedDict
import time

class SimpleCache:
    """Simple in-memory cache with LRU eviction"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
    
    def _generate_key(self, query: str, k: int = 3) -> str:
        """Generate a cache key from query and parameters"""
        key_data = f"{query.lower().strip()}_{k}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, query: str, k: int = 3) -> Optional[Any]:
        """Get cached results for a query"""
        key = self._generate_key(query, k)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if entry has expired
        if time.time() - entry['timestamp'] > self.ttl:
            del self.cache[key]
            return None
        
        # Move to end (mark as recently used)
        self.cache.move_to_end(key)
        return entry['data']
    
    def put(self, query: str, data: Any, k: int = 3) -> None:
        """Cache results for a query"""
        key = self._generate_key(query, k)
        
        # Remove oldest entry if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            self.cache.popitem(last=False)
        
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        self.cache.move_to_end(key)
    
    def clear(self) -> None:
        """Clear all cached entries"""
        self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)
    
    def hit_rate_info(self) -> Dict[str, int]:
        """Get cache statistics (would need to be implemented with counters)"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size
        }

# Global cache instance
query_cache = SimpleCache(max_size=1000, ttl=3600)  # 1 hour TTL
