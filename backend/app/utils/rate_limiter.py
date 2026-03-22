import time
from collections import defaultdict
from typing import Dict, Tuple, List


class RateLimiter:
    """
    Simple Token Bucket rate limiter (in-memory).
    """
    def __init__(self, requests_per_minute: int = 20):
        self.requests_per_minute = requests_per_minute
        self.buckets: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.buckets[user_id] = [t for t in self.buckets[user_id] if t > minute_ago]
        
        if len(self.buckets[user_id]) < self.requests_per_minute:
            self.buckets[user_id].append(now)
            return True
            
        return False


# Global Limiter
limiter = RateLimiter(requests_per_minute=20)
