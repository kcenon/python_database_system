"""
Connection pool implementation.

Equivalent to C++ database/connection_pool.h/cpp
"""

from dataclasses import dataclass, field
from typing import Optional, List
from queue import Queue, Empty
import threading
import time


@dataclass
class ConnectionPoolConfig:
    """
    Connection pool configuration.

    Equivalent to C++ connection_pool_config struct.
    """
    min_connections: int = 2
    max_connections: int = 20
    acquire_timeout_seconds: float = 5.0
    idle_timeout_seconds: float = 30.0
    health_check_interval_seconds: float = 60.0
    enable_health_checks: bool = True
    connection_string: str = ""


@dataclass
class ConnectionStats:
    """
    Connection pool statistics.

    Equivalent to C++ connection_stats struct.
    """
    total_connections: int = 0
    active_connections: int = 0
    available_connections: int = 0
    failed_acquisitions: int = 0
    successful_acquisitions: int = 0
    last_health_check: float = field(default_factory=time.time)


class ConnectionPool:
    """
    Database connection pool.

    Equivalent to C++ connection_pool_base class.

    Manages a pool of database connections for reuse.
    """

    def __init__(self, config: ConnectionPoolConfig, create_connection_func):
        """
        Initialize connection pool.

        Args:
            config: Pool configuration
            create_connection_func: Function to create new connection
        """
        self._config = config
        self._create_connection = create_connection_func
        self._available: Queue = Queue(maxsize=config.max_connections)
        self._in_use: List = []
        self._lock = threading.Lock()
        self._total_connections = 0

        # Statistics tracking
        self._stats = ConnectionStats()
        self._stats_lock = threading.Lock()

        # Pre-create minimum connections
        for _ in range(config.min_connections):
            conn = self._create_new_connection()
            if conn:
                self._available.put(conn)

    def _create_new_connection(self):
        """Create a new database connection."""
        try:
            conn = self._create_connection()
            with self._lock:
                self._total_connections += 1
            return conn
        except Exception as e:
            print(f"Failed to create connection: {e}")
            return None

    def acquire(self, timeout: Optional[float] = None) -> Optional[object]:
        """
        Acquire a connection from the pool.

        Args:
            timeout: Maximum time to wait for connection (seconds)

        Returns:
            Database connection object, or None if timeout.
        """
        timeout = timeout or self._config.acquire_timeout_seconds

        try:
            # Try to get from available pool
            conn = self._available.get(timeout=timeout)
            with self._lock:
                self._in_use.append(conn)

            # Update statistics
            with self._stats_lock:
                self._stats.successful_acquisitions += 1
                self._stats.active_connections = len(self._in_use)
                self._stats.available_connections = self._available.qsize()

            return conn
        except Empty:
            # Pool exhausted, try to create new if under max
            with self._lock:
                if self._total_connections < self._config.max_connections:
                    conn = self._create_new_connection()
                    if conn:
                        self._in_use.append(conn)

                        # Update statistics
                        with self._stats_lock:
                            self._stats.successful_acquisitions += 1
                            self._stats.active_connections = len(self._in_use)
                            self._stats.available_connections = self._available.qsize()

                        return conn

            # Failed to acquire
            with self._stats_lock:
                self._stats.failed_acquisitions += 1

            return None

    def release(self, conn: object) -> None:
        """
        Release connection back to pool.

        Args:
            conn: Connection to release
        """
        with self._lock:
            if conn in self._in_use:
                self._in_use.remove(conn)
                self._available.put(conn)

    def size(self) -> int:
        """Get total number of connections in pool."""
        return self._total_connections

    def available_count(self) -> int:
        """Get number of available connections."""
        return self._available.qsize()

    def in_use_count(self) -> int:
        """Get number of connections in use."""
        with self._lock:
            return len(self._in_use)

    def get_stats(self) -> ConnectionStats:
        """
        Get connection pool statistics.

        Returns:
            ConnectionStats object with current pool statistics.
        """
        with self._stats_lock:
            # Update current state
            self._stats.total_connections = self._total_connections
            self._stats.active_connections = len(self._in_use)
            self._stats.available_connections = self._available.qsize()
            return ConnectionStats(
                total_connections=self._stats.total_connections,
                active_connections=self._stats.active_connections,
                available_connections=self._stats.available_connections,
                failed_acquisitions=self._stats.failed_acquisitions,
                successful_acquisitions=self._stats.successful_acquisitions,
                last_health_check=self._stats.last_health_check,
            )
