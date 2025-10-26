"""
Database manager singleton module.

Equivalent to C++ database/database_manager.h/cpp
"""

import threading
from typing import Optional, Dict
from database_module.core.database_base import DatabaseBase, DatabaseResult
from database_module.core.database_types import DatabaseType
from database_module.pool.connection_pool import (
    ConnectionPool,
    ConnectionPoolConfig,
    ConnectionStats,
)


class DatabaseManager:
    """
    Singleton database manager.

    Equivalent to C++ database::database_manager class.

    Manages database connections and operations with singleton pattern.
    """

    _instance: Optional["DatabaseManager"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls):
        """Singleton implementation using __new__."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize database manager (called once)."""
        if self._initialized:
            return

        self._database: Optional[DatabaseBase] = None
        self._connected: bool = False
        self._current_type: DatabaseType = DatabaseType.NONE
        self._connection_pools: Dict[DatabaseType, ConnectionPool] = {}
        self._pool_lock = threading.Lock()
        self._initialized = True

    @classmethod
    def handle(cls) -> "DatabaseManager":
        """
        Get singleton instance.

        Returns:
            DatabaseManager singleton instance.
        """
        return cls()

    def set_mode(self, database_type: DatabaseType) -> bool:
        """
        Set database type.

        Args:
            database_type: Database type to set

        Returns:
            True if database type set successfully.
        """
        from database_module.backends.postgres.postgres_manager import PostgresManager

        if database_type == DatabaseType.POSTGRES:
            self._database = PostgresManager()
            self._current_type = database_type
            return True
        # Add other database types here (MySQL, SQLite, etc.)
        return False

    def database_type(self) -> DatabaseType:
        """Get current database type."""
        return self._current_type

    def connect(self, connect_string: str) -> bool:
        """
        Connect to database.

        Args:
            connect_string: Connection string

        Returns:
            True if connected successfully.
        """
        if not self._database:
            return False

        self._connected = self._database.connect(connect_string)
        return self._connected

    def create_query(self, query_string: str) -> bool:
        """Execute DDL query."""
        return self._database.create_query(query_string) if self._database else False

    def insert_query(self, query_string: str) -> int:
        """Execute INSERT query."""
        return self._database.insert_query(query_string) if self._database else 0

    def update_query(self, query_string: str) -> int:
        """Execute UPDATE query."""
        return self._database.update_query(query_string) if self._database else 0

    def delete_query(self, query_string: str) -> int:
        """Execute DELETE query."""
        return self._database.delete_query(query_string) if self._database else 0

    def select_query(self, query_string: str) -> DatabaseResult:
        """Execute SELECT query."""
        return self._database.select_query(query_string) if self._database else []

    def execute_query(self, query_string: str) -> bool:
        """Execute general SQL query."""
        return self._database.execute_query(query_string) if self._database else False

    def disconnect(self) -> bool:
        """
        Disconnect from database.

        Returns:
            True if disconnected successfully.
        """
        if self._database:
            self._connected = False
            return self._database.disconnect()
        return False

    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._connected

    def create_connection_pool(
        self, db_type: DatabaseType, config: ConnectionPoolConfig
    ) -> bool:
        """
        Create a connection pool for the specified database type.

        Args:
            db_type: The database type to create a pool for
            config: Connection pool configuration parameters

        Returns:
            True if the pool was created successfully, False otherwise
        """
        with self._pool_lock:
            if db_type in self._connection_pools:
                # Pool already exists
                return False

            # Create connection factory function based on database type
            def create_connection():
                from database_module.backends.postgres.postgres_manager import (
                    PostgresManager,
                )

                if db_type == DatabaseType.POSTGRES:
                    manager = PostgresManager()
                    if manager.connect(config.connection_string):
                        return manager
                # Add other database types here
                return None

            pool = ConnectionPool(config, create_connection)
            self._connection_pools[db_type] = pool
            return True

    def get_connection_pool(self, db_type: DatabaseType) -> Optional[ConnectionPool]:
        """
        Get the connection pool for the specified database type.

        Args:
            db_type: The database type to get a pool for

        Returns:
            ConnectionPool if found, None otherwise
        """
        with self._pool_lock:
            return self._connection_pools.get(db_type)

    def get_pool_stats(self) -> Dict[DatabaseType, ConnectionStats]:
        """
        Get connection pool statistics for all active pools.

        Returns:
            Dict mapping database type to connection statistics
        """
        stats = {}
        with self._pool_lock:
            for db_type, pool in self._connection_pools.items():
                stats[db_type] = pool.get_stats()
        return stats

    def create_query_builder(self, db_type: Optional[DatabaseType] = None):
        """
        Create a query builder for the current or specified database type.

        Args:
            db_type: Optional database type. If None, uses current database type.

        Returns:
            QueryBuilder configured for the specified database
        """
        from database_module.query.query_builder import QueryBuilder

        target_type = db_type if db_type is not None else self._current_type
        return QueryBuilder()
