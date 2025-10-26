"""
PostgreSQL database manager implementation.

Equivalent to C++ database/postgres_manager.h/cpp
"""

from typing import Optional
import psycopg2
import psycopg2.extras
from psycopg2 import sql

from database_module.core.database_base import DatabaseBase, DatabaseResult
from database_module.core.database_types import DatabaseType


class PostgresManager(DatabaseBase):
    """
    PostgreSQL database operations manager.

    Equivalent to C++ database::postgres_manager class.

    This class provides PostgreSQL-specific implementation of database operations
    using psycopg2 driver.
    """

    def __init__(self):
        """Initialize PostgreSQL manager."""
        self._connection: Optional[psycopg2.extensions.connection] = None
        self._cursor: Optional[psycopg2.extensions.cursor] = None

    def __del__(self):
        """Destructor - ensure connection is closed."""
        self.disconnect()

    def database_type(self) -> DatabaseType:
        """Return PostgreSQL database type."""
        return DatabaseType.POSTGRES

    def connect(self, connect_string: str) -> bool:
        """
        Connect to PostgreSQL database.

        Args:
            connect_string: PostgreSQL connection string
                          Format: "host=localhost port=5432 dbname=test user=user password=pass"

        Returns:
            True if connected successfully.
        """
        try:
            self._connection = psycopg2.connect(connect_string)
            self._cursor = self._connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            return True
        except (Exception, psycopg2.Error) as error:
            print(f"Error connecting to PostgreSQL: {error}")
            return False

    def create_query(self, query_string: str) -> bool:
        """
        Execute DDL query (CREATE, DROP, ALTER).

        Args:
            query_string: DDL SQL statement

        Returns:
            True if executed successfully.
        """
        if not self._connection or not self._cursor:
            return False

        try:
            self._cursor.execute(query_string)
            self._connection.commit()
            return True
        except (Exception, psycopg2.Error) as error:
            print(f"Error executing query: {error}")
            self._connection.rollback()
            return False

    def insert_query(self, query_string: str) -> int:
        """
        Execute INSERT query.

        Args:
            query_string: SQL INSERT statement

        Returns:
            Number of rows inserted (rowcount).
        """
        if not self._connection or not self._cursor:
            return 0

        try:
            self._cursor.execute(query_string)
            self._connection.commit()
            return self._cursor.rowcount if self._cursor.rowcount else 0
        except (Exception, psycopg2.Error) as error:
            print(f"Error inserting data: {error}")
            self._connection.rollback()
            return 0

    def update_query(self, query_string: str) -> int:
        """
        Execute UPDATE query.

        Args:
            query_string: SQL UPDATE statement

        Returns:
            Number of rows updated.
        """
        if not self._connection or not self._cursor:
            return 0

        try:
            self._cursor.execute(query_string)
            self._connection.commit()
            return self._cursor.rowcount if self._cursor.rowcount else 0
        except (Exception, psycopg2.Error) as error:
            print(f"Error updating data: {error}")
            self._connection.rollback()
            return 0

    def delete_query(self, query_string: str) -> int:
        """
        Execute DELETE query.

        Args:
            query_string: SQL DELETE statement

        Returns:
            Number of rows deleted.
        """
        if not self._connection or not self._cursor:
            return 0

        try:
            self._cursor.execute(query_string)
            self._connection.commit()
            return self._cursor.rowcount if self._cursor.rowcount else 0
        except (Exception, psycopg2.Error) as error:
            print(f"Error deleting data: {error}")
            self._connection.rollback()
            return 0

    def select_query(self, query_string: str) -> DatabaseResult:
        """
        Execute SELECT query and retrieve results.

        Args:
            query_string: SQL SELECT statement

        Returns:
            List of rows as dictionaries (column_name: value).
        """
        if not self._connection or not self._cursor:
            return []

        try:
            self._cursor.execute(query_string)
            rows = self._cursor.fetchall()

            # Convert RealDictRow to regular dict
            return [dict(row) for row in rows] if rows else []
        except (Exception, psycopg2.Error) as error:
            print(f"Error selecting data: {error}")
            return []

    def execute_query(self, query_string: str) -> bool:
        """
        Execute general SQL query.

        Args:
            query_string: SQL statement to execute

        Returns:
            True if executed successfully.
        """
        if not self._connection or not self._cursor:
            return False

        try:
            self._cursor.execute(query_string)
            self._connection.commit()
            return True
        except (Exception, psycopg2.Error) as error:
            print(f"Error executing query: {error}")
            self._connection.rollback()
            return False

    def disconnect(self) -> bool:
        """
        Disconnect from PostgreSQL database.

        Returns:
            True if disconnected successfully.
        """
        try:
            if self._cursor:
                self._cursor.close()
                self._cursor = None
            if self._connection:
                self._connection.close()
                self._connection = None
            return True
        except (Exception, psycopg2.Error) as error:
            print(f"Error disconnecting: {error}")
            return False

    # Additional PostgreSQL-specific methods

    def begin_transaction(self) -> bool:
        """Begin a transaction explicitly."""
        if not self._connection:
            return False
        try:
            # psycopg2 auto-begins transactions, but we can reset isolation level if needed
            return True
        except Exception as error:
            print(f"Error beginning transaction: {error}")
            return False

    def commit_transaction(self) -> bool:
        """Commit current transaction."""
        if not self._connection:
            return False
        try:
            self._connection.commit()
            return True
        except Exception as error:
            print(f"Error committing transaction: {error}")
            return False

    def rollback_transaction(self) -> bool:
        """Rollback current transaction."""
        if not self._connection:
            return False
        try:
            self._connection.rollback()
            return True
        except Exception as error:
            print(f"Error rolling back transaction: {error}")
            return False
