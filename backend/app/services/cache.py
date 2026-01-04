# app/services/cache.py

import time
from typing import Dict, Any, Optional
from app.core.config import settings


class SimpleCache:
    """
    Simple in-memory cache.
    Designed to be easily replaced by Redis / Memcached later.
    """

    def __init__(self):
        self._cache: Dict[str, tuple[Any, float]] = {}
        self.hits: int = 0
        self.misses: int = 0

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if not entry:
            self.misses += 1
            return None

        value, timestamp = entry
        if time.time() - timestamp > settings.CACHE_TTL:
            del self._cache[key]
            self.misses += 1
            return None

        self.hits += 1
        return value

    def set(self, key: str, value: Any) -> None:
        # Basic eviction strategy
        if len(self._cache) > 1_000:
            oldest_keys = sorted(
                self._cache.items(),
                key=lambda item: item[1][1]
            )[:200]

            for k, _ in oldest_keys:
                del self._cache[k]

        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        self._cache.clear()

    def stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total else 0.0

        return {
            "size": len(self._cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%",
        }
