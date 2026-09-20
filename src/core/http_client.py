# src/core/http_client.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

"""
Production HTTP client with circuit breaker, retries, rate limiting, and metrics.
Used by all agents for external API calls.
"""

import time
import logging
import threading
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def can_execute(self) -> bool:
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            elif self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker: OPEN -> HALF_OPEN")
                    return True
                return False
            else:  # HALF_OPEN
                return True

    def record_success(self):
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info("Circuit breaker: HALF_OPEN -> CLOSED")

    def record_failure(self):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker: -> OPEN (failures={self.failure_count})")


@dataclass
class RateLimiter:
    rate_per_second: float
    tokens: float = 0.0
    last_update: float = field(default_factory=time.time)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def acquire(self, timeout: float = 5.0) -> bool:
        with self._lock:
            deadline = time.time() + timeout
            while time.time() < deadline:
                now = time.time()
                elapsed = now - self.last_update
                self.tokens = min(self.rate_per_second, self.tokens + elapsed * self.rate_per_second)
                self.last_update = now

                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return True
                time.sleep(0.01)
            return False


@dataclass
class HTTPMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def record_success(self, latency_ms: float):
        with self._lock:
            self.total_requests += 1
            self.successful_requests += 1
            self.total_latency_ms += latency_ms

    def record_failure(self):
        with self._lock:
            self.total_requests += 1
            self.failed_requests += 1

    @property
    def avg_latency_ms(self) -> float:
        with self._lock:
            return self.total_latency_ms / self.successful_requests if self.successful_requests > 0 else 0.0

    @property
    def success_rate(self) -> float:
        with self._lock:
            return self.successful_requests / self.total_requests if self.total_requests > 0 else 0.0

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "total": self.total_requests,
                "success": self.successful_requests,
                "failed": self.failed_requests,
                "avg_latency_ms": self.avg_latency_ms,
                "success_rate": self.success_rate
            }


class ProductionHTTPClient:
    """
    Production-grade HTTP client with:
    - Automatic retries with exponential backoff
    - Circuit breaker for fault tolerance
    - Rate limiting to respect API quotas
    - Connection pooling
    - Metrics collection
    - Timeout enforcement
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        rate_limit_per_second: float = 10.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_recovery: float = 60.0,
        headers: Optional[Dict[str, str]] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = headers or {}

        # Session with connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Circuit breaker and rate limiter
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            recovery_timeout=circuit_breaker_recovery
        )
        self.rate_limiter = RateLimiter(rate_per_second=rate_limit_per_second)
        self.metrics = HTTPMetrics()

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a GET request with full production safeguards."""
        return self._request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request with full production safeguards."""
        return self._request("POST", endpoint, json=json, **kwargs)

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            raise RuntimeError(f"Circuit breaker OPEN for {self.base_url}")

        # Rate limiting
        if not self.rate_limiter.acquire():
            raise RuntimeError(f"Rate limit exceeded for {self.base_url}")

        start_time = time.time()
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()

            latency_ms = (time.time() - start_time) * 1000
            self.circuit_breaker.record_success()
            self.metrics.record_success(latency_ms)

            logger.debug(f"{method} {url} -> {response.status_code} ({latency_ms:.2f}ms)")
            return response.json()

        except requests.exceptions.RequestException as e:
            self.circuit_breaker.record_failure()
            self.metrics.record_failure()
            logger.error(f"{method} {url} failed: {e}")
            raise

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "base_url": self.base_url,
            "circuit_state": self.circuit_breaker.state.value,
            "metrics": self.metrics.get_stats()
        }
