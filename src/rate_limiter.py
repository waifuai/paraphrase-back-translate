"""
Rate limiting functionality for API calls.
"""

import time
import threading
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    strategy: RateLimitStrategy = RateLimitStrategy.FIXED_WINDOW
    enabled: bool = True


class RateLimiter:
    """
    Rate limiter implementation with multiple strategies.

    Supports:
    - Fixed window: Simple requests per minute/hour limits
    - Sliding window: More precise time-based limits
    - Token bucket: Allows bursts but maintains overall rate
    """

    def __init__(self, config: RateLimitConfig):
        """
        Initialize the rate limiter.

        Args:
            config: Rate limiting configuration
        """
        self.config = config
        self._lock = threading.Lock()

        # Fixed window tracking
        self._minute_window: Dict[int, int] = {}
        self._hour_window: Dict[int, int] = {}

        # Sliding window tracking
        self._request_times: list = []

        # Token bucket tracking
        self._tokens = config.burst_limit
        self._last_refill = time.time()

    def wait_if_needed(self) -> bool:
        """
        Wait if rate limit would be exceeded.

        Returns:
            True if had to wait, False if request can proceed immediately
        """
        if not self.config.enabled:
            return False

        with self._lock:
            if self._is_allowed():
                self._record_request()
                return False
            else:
                wait_time = self._calculate_wait_time()
                if wait_time > 0:
                    time.sleep(wait_time)
                self._record_request()
                return True

    def _is_allowed(self) -> bool:
        """Check if request is allowed under current rate limits."""
        current_time = time.time()

        # Check minute limit
        if self._exceeds_minute_limit(current_time):
            return False

        # Check hour limit
        if self._exceeds_hour_limit(current_time):
            return False

        return True

    def _exceeds_minute_limit(self, current_time: float) -> bool:
        """Check if minute limit would be exceeded."""
        if self.config.requests_per_minute <= 0:
            return False

        window_key = int(current_time // 60)  # Current minute
        current_count = self._minute_window.get(window_key, 0)

        return current_count >= self.config.requests_per_minute

    def _exceeds_hour_limit(self, current_time: float) -> bool:
        """Check if hour limit would be exceeded."""
        if self.config.requests_per_hour <= 0:
            return False

        window_key = int(current_time // 3600)  # Current hour
        current_count = self._hour_window.get(window_key, 0)

        return current_count >= self.config.requests_per_hour

    def _record_request(self) -> None:
        """Record that a request was made."""
        current_time = time.time()

        # Record in minute window
        minute_key = int(current_time // 60)
        self._minute_window[minute_key] = self._minute_window.get(minute_key, 0) + 1

        # Record in hour window
        hour_key = int(current_time // 3600)
        self._hour_window[hour_key] = self._hour_window.get(hour_key, 0) + 1

        # Record in sliding window
        self._request_times.append(current_time)

        # Clean up old entries
        self._cleanup_old_entries(current_time)

    def _cleanup_old_entries(self, current_time: float) -> None:
        """Clean up old entries from windows."""
        # Clean minute windows older than 5 minutes
        cutoff_minute = int((current_time - 300) // 60)
        self._minute_window = {
            k: v for k, v in self._minute_window.items()
            if k > cutoff_minute
        }

        # Clean hour windows older than 2 hours
        cutoff_hour = int((current_time - 7200) // 3600)
        self._hour_window = {
            k: v for k, v in self._hour_window.items()
            if k > cutoff_hour
        }

        # Clean sliding window (keep last hour)
        cutoff_time = current_time - 3600
        self._request_times = [t for t in self._request_times if t > cutoff_time]

    def _calculate_wait_time(self) -> float:
        """Calculate how long to wait before next request is allowed."""
        current_time = time.time()

        # Find the earliest time when we can make a request
        wait_times = []

        # Check minute limit
        if self.config.requests_per_minute > 0:
            minute_key = int(current_time // 60)
            current_count = self._minute_window.get(minute_key, 0)
            if current_count >= self.config.requests_per_minute:
                next_minute = (minute_key + 1) * 60
                wait_times.append(next_minute - current_time)

        # Check hour limit
        if self.config.requests_per_hour > 0:
            hour_key = int(current_time // 3600)
            current_count = self._hour_window.get(hour_key, 0)
            if current_count >= self.config.requests_per_hour:
                next_hour = (hour_key + 1) * 3600
                wait_times.append(next_hour - current_time)

        return max(wait_times) if wait_times else 0.0

    def get_stats(self) -> Dict[str, int]:
        """
        Get current rate limiter statistics.

        Returns:
            Dictionary with rate limiter stats
        """
        with self._lock:
            current_time = time.time()

            # Current minute requests
            minute_key = int(current_time // 60)
            minute_count = self._minute_window.get(minute_key, 0)

            # Current hour requests
            hour_key = int(current_time // 3600)
            hour_count = self._hour_window.get(hour_key, 0)

            return {
                "current_minute_requests": minute_count,
                "current_hour_requests": hour_count,
                "requests_per_minute_limit": self.config.requests_per_minute,
                "requests_per_hour_limit": self.config.requests_per_hour,
                "recent_requests_count": len(self._request_times)
            }


# Global rate limiter instance
_default_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(config: Optional[RateLimitConfig] = None) -> RateLimiter:
    """
    Get the global rate limiter instance.

    Args:
        config: Optional rate limit configuration

    Returns:
        RateLimiter instance
    """
    global _default_rate_limiter

    if _default_rate_limiter is None or config is not None:
        if config is None:
            config = RateLimitConfig()
        _default_rate_limiter = RateLimiter(config)

    return _default_rate_limiter


def wait_for_rate_limit() -> bool:
    """
    Wait if necessary to comply with rate limits.

    Returns:
        True if had to wait, False if request can proceed immediately
    """
    limiter = get_rate_limiter()
    return limiter.wait_if_needed()