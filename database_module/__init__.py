"""
Python Database System

A Python implementation of the C++ database_system, providing unified
database access across PostgreSQL, MySQL, SQLite, and NoSQL databases.

Equivalent to C++ database_system namespace.
"""

__version__ = "1.0.0"
__author__ = "🍀☀🌕🌥 🌊"

from database_module.core.database_types import DatabaseType
from database_module.core.database_base import DatabaseBase, DatabaseValue, DatabaseRow, DatabaseResult
from database_module.core.database_manager import DatabaseManager

# Convenience exports
from database_module.backends.postgres.postgres_manager import PostgresManager
from database_module.pool.connection_pool import ConnectionPool, ConnectionPoolConfig
from database_module.query.query_builder import QueryBuilder, JoinType, SortOrder

__all__ = [
    # Core types
    "DatabaseType",
    "DatabaseBase",
    "DatabaseValue",
    "DatabaseRow",
    "DatabaseResult",
    "DatabaseManager",

    # Backends
    "PostgresManager",

    # Connection pooling
    "ConnectionPool",
    "ConnectionPoolConfig",

    # Query building
    "QueryBuilder",
    "JoinType",
    "SortOrder",
]
