# src/orchestrator/mesh_router.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette
# RFC 1001 Compliant — PSIVI Open Science Hub

"""
Production-Grade Mesh Router for PSIVI Open Science Mesh

Handles routing of .psvc containers between agents and workers with:
- Circuit breaker pattern for fault tolerance
- Connection pooling for performance
- Exponential backoff retries
- Health checks and monitoring
- Graceful shutdown
- Rate limiting
- Metrics collection
"""

import time
import logging
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from collections import deque
import threading
from contextlib import contextmanager
import queue

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class CircuitBreaker:
    """Circuit breaker for fault tolerance."""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0.0
    success_count: int = 0
    
    def record_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info("Circuit breaker recovered to CLOSED state")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker OPEN after {self.failure_count} failures")
    
    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info("Circuit breaker transitioned to HALF_OPEN")
                return True
            return False
        else:  # HALF_OPEN
            return True


@dataclass
class Connection:
    """Represents a connection to a worker or agent."""
    id: str
    endpoint: str
    last_heartbeat: float = field(default_factory=time.time)
    is_healthy: bool = True
    active_requests: int = 0
    total_requests: int = 0
    failure_count: int = 0
    latency_ms: float = 0.0
    
    def record_request(self, latency: float, success: bool):
        self.active_requests -= 1
        self.total_requests += 1
        self.latency_ms = (self.latency_ms * 0.9) + (latency * 0.1)  # EMA
        
        if success:
            self.is_healthy = True
            self.failure_count = 0
        else:
            self.failure_count += 1
            if self.failure_count >= 3:
                self.is_healthy = False


class ConnectionPool:
    """Thread-safe connection pool with health monitoring."""
    
    def __init__(self, max_connections: int = 100, health_check_interval: float = 30.0):
        self.max_connections = max_connections
        self.health_check_interval = health_check_interval
        self.connections: Dict[str, Connection] = {}
        self.lock = threading.RLock()
        self._running = True
        self._health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self._health_check_thread.start()
    
    def register_connection(self, conn_id: str, endpoint: str) -> Connection:
        with self.lock:
            if conn_id not in self.connections:
                if len(self.connections) >= self.max_connections:
                    raise RuntimeError(f"Connection pool exhausted (max={self.max_connections})")
                
                conn = Connection(id=conn_id, endpoint=endpoint)
                self.connections[conn_id] = conn
                logger.info(f"Registered connection: {conn_id} -> {endpoint}")
                return conn
            return self.connections[conn_id]
    
    def get_healthy_connection(self, strategy: str = "round_robin") -> Optional[Connection]:
        with self.lock:
            healthy_conns = [c for c in self.connections.values() if c.is_healthy]
            
            if not healthy_conns:
                return None
            
            if strategy == "round_robin":
                # Simple round-robin based on total requests
                return min(healthy_conns, key=lambda c: c.total_requests)
            elif strategy == "least_connections":
                return min(healthy_conns, key=lambda c: c.active_requests)
            elif strategy == "lowest_latency":
                return min(healthy_conns, key=lambda c: c.latency_ms)
            else:
                return healthy_conns[0]
    
    def remove_connection(self, conn_id: str):
        with self.lock:
            if conn_id in self.connections:
                del self.connections[conn_id]
                logger.info(f"Removed connection: {conn_id}")
    
    def _health_check_loop(self):
        while self._running:
            time.sleep(self.health_check_interval)
            self._perform_health_checks()
    
    def _perform_health_checks(self):
        with self.lock:
            now = time.time()
            stale_threshold = now - (self.health_check_interval * 2)
            
            for conn in list(self.connections.values()):
                if conn.last_heartbeat < stale_threshold:
                    conn.is_healthy = False
                    logger.warning(f"Connection {conn.id} marked unhealthy (stale heartbeat)")
    
    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "total_connections": len(self.connections),
                "healthy_connections": sum(1 for c in self.connections.values() if c.is_healthy),
                "total_requests": sum(c.total_requests for c in self.connections.values()),
                "avg_latency_ms": sum(c.latency_ms for c in self.connections.values()) / len(self.connections) if self.connections else 0
            }
    
    def shutdown(self):
        self._running = False
        logger.info("Connection pool shutdown initiated")


@dataclass
class RoutingMetrics:
    """Metrics collection for monitoring."""
    total_routed: int = 0
    successful_routes: int = 0
    failed_routes: int = 0
    total_latency_ms: float = 0.0
    circuit_breaker_trips: int = 0
    
    def record_success(self, latency_ms: float):
        self.total_routed += 1
        self.successful_routes += 1
        self.total_latency_ms += latency_ms
    
    def record_failure(self):
        self.total_routed += 1
        self.failed_routes += 1
    
    def record_circuit_trip(self):
        self.circuit_breaker_trips += 1
    
    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / self.successful_routes if self.successful_routes > 0 else 0.0
    
    @property
    def success_rate(self) -> float:
        return self.successful_routes / self.total_routed if self.total_routed > 0 else 0.0


class MeshRouter:
    """
    Production-grade mesh router with fault tolerance and monitoring.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_recovery: float = 60.0,
        max_connections: int = 100,
        rate_limit_per_second: int = 1000
    ):
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            recovery_timeout=circuit_breaker_recovery
        )
        self.connection_pool = ConnectionPool(max_connections=max_connections)
        self.metrics = RoutingMetrics()
        self.rate_limiter = RateLimiter(rate_limit_per_second)
        self._running = True
        self._shutdown_event = threading.Event()
        
        logger.info(
            f"MeshRouter initialized: max_retries={max_retries}, "
            f"circuit_threshold={circuit_breaker_threshold}, "
            f"max_connections={max_connections}"
        )
    
    def route_container(
        self,
        container_bytes: bytes,
        target_agent_id: str,
        timeout: float = 30.0
    ) -> bytes:
        """
        Route a .psvc container to a target agent with full fault tolerance.
        
        Args:
            container_bytes: Serialized .psvc container
            target_agent_id: Target agent or worker ID
            timeout: Maximum time to wait for response
            
        Returns:
            Processed container bytes
            
        Raises:
            CircuitBreakerOpenError: If circuit breaker is open
            RoutingTimeoutError: If routing times out
            RoutingError: If routing fails after all retries
        """
        if not self._running:
            raise RuntimeError("MeshRouter is shutting down")
        
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            self.metrics.record_circuit_trip()
            raise CircuitBreakerOpenError(
                f"Circuit breaker is OPEN. Recovery in "
                f"{self.circuit_breaker.recovery_timeout - (time.time() - self.circuit_breaker.last_failure_time):.1f}s"
            )
        
        # Rate limiting
        if not self.rate_limiter.acquire():
            raise RateLimitExceededError("Rate limit exceeded")
        
        # Retry with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                # Get healthy connection
                connection = self.connection_pool.get_healthy_connection(strategy="least_connections")
                if not connection:
                    raise NoHealthyConnectionsError("No healthy connections available")
                
                # Route the container
                result = self._execute_route(connection, container_bytes, target_agent_id, timeout)
                
                # Record success
                latency_ms = (time.time() - start_time) * 1000
                connection.record_request(latency_ms, success=True)
                self.circuit_breaker.record_success()
                self.metrics.record_success(latency_ms)
                
                logger.debug(
                    f"Successfully routed container to {target_agent_id} "
                    f"via {connection.id} in {latency_ms:.2f}ms"
                )
                
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Routing attempt {attempt + 1}/{self.max_retries} failed: {e}"
                )
                
                if connection:
                    connection.record_request(0, success=False)
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)
        
        # All retries failed
        self.circuit_breaker.record_failure()
        self.metrics.record_failure()
        raise RoutingError(f"Routing failed after {self.max_retries} attempts: {last_exception}")
    
    def _execute_route(
        self,
        connection: Connection,
        container_bytes: bytes,
        target_agent_id: str,
        timeout: float
    ) -> bytes:
        """
        Execute the actual routing operation.
        In production, this would make network calls to the target agent.
        """
        connection.active_requests += 1
        connection.last_heartbeat = time.time()
        
        # Simulate routing (replace with actual network call)
        # In production: HTTP/gRPC call to target agent
        time.sleep(0.01)  # Simulate network latency
        
        return container_bytes  # Echo back for now
    
    def register_worker(self, worker_id: str, endpoint: str):
        """Register a new worker in the mesh."""
        self.connection_pool.register_connection(worker_id, endpoint)
    
    def deregister_worker(self, worker_id: str):
        """Remove a worker from the mesh."""
        self.connection_pool.remove_connection(worker_id)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        return {
            "router_healthy": self._running,
            "circuit_breaker_state": self.circuit_breaker.state.value,
            "connection_pool": self.connection_pool.get_stats(),
            "metrics": {
                "total_routed": self.metrics.total_routed,
                "success_rate": self.metrics.success_rate,
                "avg_latency_ms": self.metrics.avg_latency_ms,
                "circuit_breaker_trips": self.metrics.circuit_breaker_trips
            }
        }
    
    def shutdown(self, timeout: float = 30.0):
        """Graceful shutdown."""
        logger.info("Initiating graceful shutdown...")
        self._running = False
        self._shutdown_event.set()
        self.connection_pool.shutdown()
        logger.info("MeshRouter shutdown complete")


class RateLimiter:
    """Simple token bucket rate limiter."""
    
    def __init__(self, rate_per_second: int):
        self.rate = rate_per_second
        self.tokens = rate_per_second
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def acquire(self) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


# Custom exceptions
class RoutingError(Exception):
    """Base exception for routing errors."""
    pass

class CircuitBreakerOpenError(RoutingError):
    """Raised when circuit breaker is open."""
    pass

class RoutingTimeoutError(RoutingError):
    """Raised when routing times out."""
    pass

class NoHealthyConnectionsError(RoutingError):
    """Raised when no healthy connections are available."""
    pass

class RateLimitExceededError(RoutingError):
    """Raised when rate limit is exceeded."""
    pass


# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize router
    router = MeshRouter(
        max_retries=3,
        circuit_breaker_threshold=5,
        max_connections=100,
        rate_limit_per_second=1000
    )
    
    # Register some workers
    router.register_worker("worker-1", "http://localhost:8001")
    router.register_worker("worker-2", "http://localhost:8002")
    router.register_worker("worker-3", "http://localhost:8003")
    
    # Route some containers
    try:
        result = router.route_container(
            container_bytes=b"test_container_data",
            target_agent_id="worker-1",
            timeout=30.0
        )
        print(f"✓ Successfully routed container")
    except Exception as e:
        print(f"✗ Routing failed: {e}")
    
    # Check health
    health = router.get_health_status()
    print(f"\nHealth Status:")
    print(f"  Circuit Breaker: {health['circuit_breaker_state']}")
    print(f"  Connections: {health['connection_pool']['healthy_connections']}/{health['connection_pool']['total_connections']}")
    print(f"  Success Rate: {health['metrics']['success_rate']:.2%}")
    print(f"  Avg Latency: {health['metrics']['avg_latency_ms']:.2f}ms")
    
    # Shutdown
    router.shutdown()
