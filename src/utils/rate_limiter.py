"""Rate limiting for API calls."""

import time
from threading import Lock
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Simple token bucket rate limiter."""

    def __init__(self, calls: int, period: float):
        """Initialize rate limiter.

        Args:
            calls: Number of calls allowed
            period: Time period in seconds
        """
        self.calls = calls
        self.period = period
        self.allowance = calls
        self.last_check = time.time()
        self.lock = Lock()

    def wait(self):
        """Wait if rate limit is exceeded."""
        with self.lock:
            current = time.time()
            time_passed = current - self.last_check
            self.last_check = current

            # Add tokens based on time passed
            self.allowance += time_passed * (self.calls / self.period)

            if self.allowance > self.calls:
                self.allowance = self.calls

            if self.allowance < 1.0:
                # Calculate sleep time
                sleep_time = (1.0 - self.allowance) * (self.period / self.calls)
                logger.debug(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
                self.allowance = 0.0
            else:
                self.allowance -= 1.0
