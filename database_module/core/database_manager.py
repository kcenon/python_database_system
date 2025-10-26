"""
Database manager singleton module.

Equivalent to C++ database/database_manager.h/cpp
"""

import threading
from typing import Optional, Dict
from database_module.core.database_base import DatabaseBase, DatabaseResult
from database_module.core.database_types import DatabaseType


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
