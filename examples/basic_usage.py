"""
Database System - Basic Usage Example

This example demonstrates the basic usage of the Python database system.
Equivalent to C++ samples/basic_usage.cpp
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database_module import (
    DatabaseManager,
    DatabaseType,
)


def main():
    print("=== Database System - Basic Usage Example ===")

    # 1. Database manager creation and configuration
    print("\n1. Database Manager Setup:")

    db_manager = DatabaseManager.handle()

    # Set database type
    db_manager.set_mode(DatabaseType.POSTGRES)
    print("Database type set to: PostgreSQL")

    # Connection string (modify these values for your database)
    connection_string = "host=localhost port=5432 dbname=testdb user=testuser password=testpass"
    print("Connection string configured")

    print(
        "Note: This example demonstrates API usage. Actual database connection requires PostgreSQL server."
    )

    # 2. Connection management
    print("\n2. Connection Management:")

    print("Attempting to connect to database...")
    connected = db_manager.connect(connection_string)

    if connected:
        print("✓ Successfully connected to database")
        print("Connection status: Connected")
        print(f"Database type: {db_manager.database_type()}")

        # 3. Table operations
        print("\n3. Table Operations:")

        # Create table
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                age INTEGER CHECK (age >= 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """

        print("Creating users table...")
        table_created = db_manager.create_query(create_table_sql)
        if table_created:
            print("✓ Users table created successfully")
        else:
            print("✗ Failed to create users table")

        # 4. Data insertion
        print("\n4. Data Insertion:")

        insert_queries = [
            "INSERT INTO users (username, email, age) VALUES ('john_doe', 'john@example.com', 30)",
            "INSERT INTO users (username, email, age) VALUES ('jane_smith', 'jane@example.com', 25)",
            "INSERT INTO users (username, email, age) VALUES ('bob_wilson', 'bob@example.com', 35)",
            "INSERT INTO users (username, email, age, is_active) VALUES ('alice_brown', 'alice@example.com', 28, FALSE)",
        ]

        for query in insert_queries:
            inserted = db_manager.insert_query(query)
            if inserted > 0:
                print("✓ User inserted successfully")
            else:
                print("✗ Failed to insert user (may already exist)")

        # 5. Data selection
        print("\n5. Data Selection:")

        select_all = "SELECT id, username, email, age, is_active FROM users ORDER BY id"
        all_users = db_manager.select_query(select_all)

        if all_users:
            print(f"✓ All users retrieved ({len(all_users)} rows):")
            for row in all_users:
                print(f"  User: {row}")
        else:
            print("✗ Failed to retrieve users")

        # Select specific user
        select_user = (
            "SELECT username, email, age FROM users WHERE username = 'john_doe'"
        )
        john_data = db_manager.select_query(select_user)

        if john_data:
            print("✓ John's data retrieved:")
            for row in john_data:
                for key, value in row.items():
                    print(f"  {key}: {value}")
        else:
            print("✗ John's data not found")

        # 6. Data updates
        print("\n6. Data Updates:")

        update_query = "UPDATE users SET age = 31 WHERE username = 'john_doe'"
        updated = db_manager.update_query(update_query)

        if updated > 0:
            print("✓ John's age updated successfully")

            # Verify update
            updated_data = db_manager.select_query(
                "SELECT username, age FROM users WHERE username = 'john_doe'"
            )
            if updated_data:
                print(f"Updated data: {updated_data[0]}")
        else:
            print("✗ Failed to update John's age")

        # 7. Data deletion
        print("\n7. Data Deletion:")

        delete_query = "DELETE FROM users WHERE username LIKE 'temp_user%'"
        deleted = db_manager.delete_query(delete_query)

        if deleted > 0:
            print("✓ Temporary users deleted successfully")
        else:
            print("No temporary users to delete")

        # 8. Query Builder Example
        print("\n8. Query Builder Example:")

        from database_module.query import QueryBuilder, SortOrder

        # Build SELECT query
        builder = QueryBuilder()
        query = (
            builder.select(["username", "email", "age"])
            .from_table("users")
            .where("age", ">=", 30)
            .order_by("age", SortOrder.DESC)
            .limit(5)
            .build()
        )

        print(f"Built query: {query}")

        result = db_manager.select_query(query)
        if result:
            print(f"✓ Query executed successfully ({len(result)} rows):")
            for row in result:
                print(f"  {row}")

        # 9. Connection testing
        print("\n9. Connection Health Check:")
        print(f"Connection active: {db_manager.is_connected()}")

        # 10. Cleanup
        print("\n10. Cleanup:")

        # Optionally drop the test table (uncomment if needed)
        # drop_table = "DROP TABLE IF EXISTS users"
        # table_dropped = db_manager.execute_query(drop_table)
        # if table_dropped:
        #     print("✓ Test table dropped successfully")

        # Disconnect
        db_manager.disconnect()
        print("✓ Disconnected from database")
        print("Connection status: Disconnected")

    else:
        print("✗ Failed to connect to database")
        print("Please ensure:")
        print("  - PostgreSQL server is running")
        print("  - Database 'testdb' exists")
        print("  - User 'testuser' has appropriate permissions")
        print("  - Connection parameters are correct")

        print("\nTo test with a real database, update the connection string:")
        print(
            "  host=your_host port=5432 dbname=your_db user=your_user password=your_pass"
        )

    print("\n=== Basic Usage Example completed ===")


if __name__ == "__main__":
    main()
