"""
Database types enumeration module.

Equivalent to C++ database/database_types.h
"""

from enum import IntEnum
from typing import Final


class DatabaseType(IntEnum):
    """
    Enumeration of supported database types.

    Equivalent to C++ database::database_types enum.

    Attributes:
        NONE: No specific database type
        POSTGRES: PostgreSQL database
        MYSQL: MySQL/MariaDB database
        SQLITE: SQLite database
        ORACLE: Oracle database (future)
        MONGODB: MongoDB database (future)
        REDIS: Redis database (future)
    """
    NONE = 0
    POSTGRES = 1
    MYSQL = 2
    SQLITE = 3
    ORACLE = 4
    MONGODB = 5
    REDIS = 6

    def to_string(self) -> str:
        """
        Convert database type to string representation.

        Returns:
            String representation of the database type.
        """
        return self.name.lower()

    @classmethod
    def from_string(cls, value: str) -> "DatabaseType":
        """
        Convert string to database type.

        Args:
            value: String representation (case-insensitive)

        Returns:
            Corresponding DatabaseType enum value.

        Raises:
            ValueError: If string doesn't match any database type.
        """
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Unknown database type: {value}")


# Type aliases for convenience
DB_POSTGRES: Final = DatabaseType.POSTGRES
DB_MYSQL: Final = DatabaseType.MYSQL
DB_SQLITE: Final = DatabaseType.SQLITE
DB_MONGODB: Final = DatabaseType.MONGODB
DB_REDIS: Final = DatabaseType.REDIS
