# Python Database System

A Python implementation of a database abstraction layer, providing a unified interface for multiple database backends. This is the Python equivalent of the C++ database_system.

## Features

- **Multiple Database Support**: PostgreSQL, MySQL, SQLite (extensible architecture)
- **Singleton Pattern**: Thread-safe database manager
- **Connection Pooling**: Efficient connection reuse and management
- **Query Builder**: Programmatic SQL query construction
- **Type Safety**: Full type hints for better IDE support
- **Clean API**: Simple and consistent interface across database types

## Architecture

```
python_database_system/
├── database_module/           # Main module
│   ├── core/                  # Core abstractions
│   │   ├── database_types.py  # Database type enumeration
│   │   ├── database_base.py   # Abstract base class
│   │   └── database_manager.py # Singleton manager
│   ├── backends/              # Database implementations
│   │   └── postgres/          # PostgreSQL backend
│   │       └── postgres_manager.py
│   ├── pool/                  # Connection pooling
│   │   └── connection_pool.py
│   └── query/                 # Query builder
│       └── query_builder.py
├── examples/                  # Usage examples
│   └── basic_usage.py
├── tests/                     # Unit tests
└── docs/                      # Documentation
```

## Installation

### Requirements

- Python 3.8+
- PostgreSQL (for PostgreSQL backend)

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from database_module import DatabaseManager, DatabaseType

# Get singleton instance
db_manager = DatabaseManager.handle()

# Configure database type
db_manager.set_mode(DatabaseType.POSTGRES)

# Connect to database
connection_string = "host=localhost port=5432 dbname=mydb user=myuser password=mypass"
if db_manager.connect(connection_string):
    print("Connected successfully")

    # Create table
    create_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) NOT NULL
        )
    """
    db_manager.create_query(create_sql)

    # Insert data
    insert_sql = "INSERT INTO users (username, email) VALUES ('john', 'john@example.com')"
    rows_inserted = db_manager.insert_query(insert_sql)

    # Select data
    select_sql = "SELECT * FROM users"
    results = db_manager.select_query(select_sql)
    for row in results:
        print(row)  # Dict with column names as keys

    # Update data
    update_sql = "UPDATE users SET email = 'newemail@example.com' WHERE username = 'john'"
    rows_updated = db_manager.update_query(update_sql)

    # Delete data
    delete_sql = "DELETE FROM users WHERE username = 'john'"
    rows_deleted = db_manager.delete_query(delete_sql)

    # Disconnect
    db_manager.disconnect()
```

### Query Builder

```python
from database_module import DatabaseManager, DatabaseType
from database_module.query import QueryBuilder, SortOrder

# Setup database
db_manager = DatabaseManager.handle()
db_manager.set_mode(DatabaseType.POSTGRES)
db_manager.connect(connection_string)

# Build SELECT query
builder = QueryBuilder()
query = (
    builder.select(["id", "username", "email"])
    .from_table("users")
    .where("age", ">=", 18)
    .order_by("username", SortOrder.ASC)
    .limit(10)
    .build()
)

# Execute query
results = db_manager.select_query(query)

# Build INSERT query
builder.reset()
query = (
    builder.insert_into("users")
    .values({
        "username": "alice",
        "email": "alice@example.com",
        "age": 25
    })
    .build()
)
db_manager.insert_query(query)

# Build UPDATE query
builder.reset()
query = (
    builder.update("users")
    .set({"email": "new@example.com"})
    .where("username", "=", "alice")
    .build()
)
db_manager.update_query(query)

# Build DELETE query
builder.reset()
query = (
    builder.delete_from("users")
    .where("age", "<", 18)
    .build()
)
db_manager.delete_query(query)
```

### Connection Pool

```python
from database_module.pool import ConnectionPool, ConnectionPoolConfig
import psycopg2

# Define connection factory
def create_connection():
    return psycopg2.connect(connection_string)

# Create pool configuration
config = ConnectionPoolConfig(
    min_connections=2,
    max_connections=10,
    connection_timeout_seconds=30,
    idle_timeout_seconds=300
)

# Create pool
pool = ConnectionPool(config, create_connection)

# Acquire connection
conn = pool.acquire(timeout=5.0)
if conn:
    # Use connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()

    # Release connection back to pool
    pool.release(conn)

# Check pool status
print(f"Total connections: {pool.size()}")
print(f"Available: {pool.available_count()}")
print(f"In use: {pool.in_use_count()}")
```

## API Reference

### DatabaseManager

**Singleton Methods:**
- `handle()` - Get singleton instance

**Configuration:**
- `set_mode(database_type: DatabaseType) -> bool` - Set database type
- `database_type() -> DatabaseType` - Get current database type

**Connection:**
- `connect(connect_string: str) -> bool` - Connect to database
- `disconnect() -> bool` - Disconnect from database
- `is_connected() -> bool` - Check connection status

**Query Operations:**
- `create_query(query_string: str) -> bool` - Execute DDL query
- `insert_query(query_string: str) -> int` - Execute INSERT query
- `update_query(query_string: str) -> int` - Execute UPDATE query
- `delete_query(query_string: str) -> int` - Execute DELETE query
- `select_query(query_string: str) -> DatabaseResult` - Execute SELECT query
- `execute_query(query_string: str) -> bool` - Execute general query

### QueryBuilder

**SELECT:**
- `select(columns: Union[str, List[str]]) -> QueryBuilder`
- `from_table(table: str) -> QueryBuilder`

**WHERE:**
- `where(field: str, operator: str, value: DatabaseValue) -> QueryBuilder`
- `where_condition(condition: QueryCondition) -> QueryBuilder`
- `where_raw(raw_where: str) -> QueryBuilder`

**JOIN:**
- `join(table: str, condition: str, join_type: JoinType) -> QueryBuilder`
- `left_join(table: str, condition: str) -> QueryBuilder`
- `right_join(table: str, condition: str) -> QueryBuilder`

**GROUP BY:**
- `group_by(columns: Union[str, List[str]]) -> QueryBuilder`
- `having(condition: str) -> QueryBuilder`

**ORDER BY:**
- `order_by(column: str, order: SortOrder) -> QueryBuilder`

**LIMIT/OFFSET:**
- `limit(count: int) -> QueryBuilder`
- `offset(count: int) -> QueryBuilder`

**INSERT:**
- `insert_into(table: str) -> QueryBuilder`
- `values(data: Union[Dict, List[Dict]]) -> QueryBuilder`

**UPDATE:**
- `update(table: str) -> QueryBuilder`
- `set(field_or_data: Union[str, Dict], value: Optional[DatabaseValue]) -> QueryBuilder`

**DELETE:**
- `delete_from(table: str) -> QueryBuilder`

**Build:**
- `build() -> str` - Build final SQL query
- `reset() -> None` - Reset builder state

### ConnectionPool

**Methods:**
- `acquire(timeout: Optional[float]) -> Optional[object]` - Get connection from pool
- `release(conn: object) -> None` - Return connection to pool
- `size() -> int` - Total connections in pool
- `available_count() -> int` - Available connections
- `in_use_count() -> int` - Connections in use

## Type System

### DatabaseType Enum
- `NONE = 0`
- `POSTGRES = 1`
- `MYSQL = 2`
- `SQLITE = 3`
- `ORACLE = 4`
- `MONGODB = 5`
- `REDIS = 6`

### JoinType Enum
- `INNER = 0`
- `LEFT = 1`
- `RIGHT = 2`
- `FULL_OUTER = 3`
- `CROSS = 4`

### SortOrder Enum
- `ASC = 0`
- `DESC = 1`

### Type Aliases
- `DatabaseValue = Union[str, int, float, bool, None]` - Single value
- `DatabaseRow = Dict[str, DatabaseValue]` - Single row
- `DatabaseResult = List[DatabaseRow]` - Query result

## Examples

See the `examples/` directory for complete working examples:

- `basic_usage.py` - Comprehensive example covering all features

Run examples:
```bash
cd examples
python basic_usage.py
```

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Comparison with C++ Version

| Feature | C++ | Python |
|---------|-----|--------|
| Singleton Pattern | `std::once_flag` | `threading.Lock` with `__new__` |
| Abstract Interface | Pure virtual | `abc.ABC` with `@abstractmethod` |
| Database Value | `std::variant` | `Union` type hint |
| Connection Pool | Template-based | Generic with type hints |
| Query Builder | Builder pattern | Builder pattern with method chaining |
| Thread Safety | `std::mutex` | `threading.Lock` |

## Thread Safety

- **DatabaseManager**: Thread-safe singleton initialization
- **QueryBuilder**: NOT thread-safe - use one instance per thread
- **ConnectionPool**: Thread-safe with internal locking

## Security Notes

- **SQL Injection**: Avoid using `where_raw()` and raw methods with user input
- **Credentials**: Never hardcode connection strings - use environment variables
- **Connection Strings**: Stored in memory - ensure proper cleanup

## Contributing

This module follows the same architecture as the C++ database_system to maintain consistency across implementations.

## License

BSD 3-Clause License

## Related Projects

- `python_logger_system` - Python logging system
- `python_container_system` - Python container utilities
- `database_system` (C++) - Original C++ implementation
