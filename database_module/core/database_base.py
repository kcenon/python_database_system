"""
Database base abstract class module.

Equivalent to C++ database/database_base.h
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Union, Optional, Any

# Type aliases matching C++ database types
DatabaseValue = Union[str, int, float, bool, None]
DatabaseRow = Dict[str, DatabaseValue]
DatabaseResult = List[DatabaseRow]


class DatabaseBase(ABC):
    """
    Abstract base class for database operations.

    Equivalent to C++ database::database_base class.

    This class serves as an interface for database operations such as
    connecting, querying, and disconnecting. Derived classes must implement
    all abstract methods for specific database systems.
    """

    @abstractmethod
    def database_type(self) -> "DatabaseType":
        """
        Get the specific type of the database.

        Returns:
            Database type enum value.
        """
        pass

    @abstractmethod
    def connect(self, connect_string: str) -> bool:
        """
        Establish connection to database.

        Args:
            connect_string: Connection details (host, port, user, password, database)

        Returns:
            True if connection successful, False otherwise.
        """
        pass

    @abstractmethod
    def create_query(self, query_string: str) -> bool:
        """
        Create/prepare a database query.

        Args:
            query_string: SQL query to prepare

        Returns:
            True if query prepared successfully, False otherwise.
        """
        pass

    @abstractmethod
    def insert_query(self, query_string: str) -> int:
        """
        Execute INSERT query.

        Args:
            query_string: SQL INSERT statement

        Returns:
            Number of rows inserted.
        """
        pass

    @abstractmethod
    def update_query(self, query_string: str) -> int:
        """
        Execute UPDATE query.

        Args:
            query_string: SQL UPDATE statement

        Returns:
            Number of rows updated.
        """
        pass

    @abstractmethod
    def delete_query(self, query_string: str) -> int:
        """
        Execute DELETE query.

        Args:
            query_string: SQL DELETE statement

        Returns:
            Number of rows deleted.
        """
        pass

    @abstractmethod
    def select_query(self, query_string: str) -> DatabaseResult:
        """
        Execute SELECT query and retrieve results.

        Args:
            query_string: SQL SELECT statement

        Returns:
            List of rows as dictionaries. Empty list if query fails.
        """
        pass

    @abstractmethod
    def execute_query(self, query_string: str) -> bool:
        """
        Execute general SQL query (DDL, DML).

        Args:
            query_string: SQL query to execute

        Returns:
            True if executed successfully, False otherwise.
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Terminate database connection.

        Returns:
            True if disconnected successfully, False otherwise.
        """
        pass
