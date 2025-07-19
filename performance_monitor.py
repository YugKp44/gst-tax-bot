# performance_monitor.py - Monitor and log performance metrics

import time
import logging
from typing import Dict, List, Optional
from functools import wraps
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor performance metrics for the GST Tax Bot"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.query_times: deque = deque(maxlen=max_history)
        self.query_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.cache_stats = {'hits': 0, 'misses': 0}
        self.intent_stats = defaultdict(int)
        
    def record_query_time(self, duration: float, intent_type: str = 'unknown'):
        """Record query processing time"""
        self.query_times.append(duration)
        self.intent_stats[intent_type] += 1
        
    def record_cache_hit(self):
        """Record cache hit"""
        self.cache_stats['hits'] += 1
        
    def record_cache_miss(self):
        """Record cache miss"""
        self.cache_stats['misses'] += 1
        
    def record_error(self, error_type: str):
        """Record error occurrence"""
        self.error_counts[error_type] += 1
        
    def get_stats(self) -> Dict:
        """Get current performance statistics"""
        total_queries = len(self.query_times)
        
        if total_queries == 0:
            return {
                'total_queries': 0,
                'avg_response_time': 0,
                'cache_hit_rate': 0,
                'error_rate': 0
            }
            
        avg_time = sum(self.query_times) / total_queries
        total_cache_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        cache_hit_rate = (self.cache_stats['hits'] / total_cache_requests * 100) if total_cache_requests > 0 else 0
        total_errors = sum(self.error_counts.values())
        error_rate = (total_errors / (total_queries + total_errors) * 100) if total_queries > 0 else 0
        
        return {
            'total_queries': total_queries,
            'avg_response_time': round(avg_time, 3),
            'cache_hit_rate': round(cache_hit_rate, 2),
            'error_rate': round(error_rate, 2),
            'intent_distribution': dict(self.intent_stats),
            'recent_response_times': list(self.query_times)[-10:],  # Last 10 response times
        }
        
    def log_performance_summary(self):
        """Log performance summary"""
        stats = self.get_stats()
        logger.info(f"Performance Summary: {stats}")

# Global performance monitor
perf_monitor = PerformanceMonitor()

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Extract intent if available
            intent_type = 'unknown'
            if hasattr(result, '__len__') and len(result) > 0:
                if isinstance(result, (list, tuple)) and len(result) > 0:
                    if isinstance(result[0], dict) and 'intent' in result[0]:
                        intent_type = result[0]['intent']
            
            perf_monitor.record_query_time(duration, intent_type)
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            perf_monitor.record_query_time(duration, 'error')
            perf_monitor.record_error(type(e).__name__)
            raise
    return wrapper
