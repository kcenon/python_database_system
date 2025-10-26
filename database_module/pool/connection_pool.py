"""
Connection pool implementation.

Equivalent to C++ database/connection_pool.h/cpp
"""

from dataclasses import dataclass
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
    max_connections: int = 10
    connection_timeout_seconds: int = 30
    idle_timeout_seconds: int = 300
    validation_query: str = "SELECT 1"


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
        timeout = timeout or self._config.connection_timeout_seconds

        try:
            # Try to get from available pool
            conn = self._available.get(timeout=timeout)
            with self._lock:
                self._in_use.append(conn)
            return conn
        except Empty:
            # Pool exhausted, try to create new if under max
            with self._lock:
                if self._total_connections < self._config.max_connections:
                    conn = self._create_new_connection()
                    if conn:
                        self._in_use.append(conn)
                        return conn
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
