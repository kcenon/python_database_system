"""
SQL query builder implementation.

Equivalent to C++ database/query_builder.h/cpp
"""

from enum import IntEnum
from typing import List, Dict, Optional, Union, Any
from database_module.core.database_base import DatabaseValue


class JoinType(IntEnum):
    """
    SQL JOIN types.

    Equivalent to C++ join_type enum.
    """
    INNER = 0
    LEFT = 1
    RIGHT = 2
    FULL_OUTER = 3
    CROSS = 4

    def to_sql(self) -> str:
        """Convert to SQL string."""
        mapping = {
            JoinType.INNER: "INNER JOIN",
            JoinType.LEFT: "LEFT JOIN",
            JoinType.RIGHT: "RIGHT JOIN",
            JoinType.FULL_OUTER: "FULL OUTER JOIN",
            JoinType.CROSS: "CROSS JOIN",
        }
        return mapping[self]


class SortOrder(IntEnum):
    """
    SQL sort order.

    Equivalent to C++ sort_order enum.
    """
    ASC = 0
    DESC = 1

    def to_sql(self) -> str:
        """Convert to SQL string."""
        return "ASC" if self == SortOrder.ASC else "DESC"


class QueryCondition:
    """
    Represents a WHERE condition in a query.

    Equivalent to C++ query_condition class.
    """

    def __init__(
        self,
        field: Optional[str] = None,
        operator: Optional[str] = None,
        value: Optional[DatabaseValue] = None,
        raw_condition: Optional[str] = None,
    ):
        """
        Initialize query condition.

        Args:
            field: Field name
            operator: Comparison operator (=, !=, >, <, >=, <=, LIKE, IN)
            value: Value to compare
            raw_condition: Raw SQL condition string
        """
        self.field = field
        self.operator = operator
        self.value = value
        self.raw_condition = raw_condition
        self.sub_conditions: List[QueryCondition] = []
        self.logical_operator: Optional[str] = None

    def to_sql(self) -> str:
        """Convert condition to SQL string."""
        if self.raw_condition:
            return self.raw_condition

        if self.sub_conditions:
            conditions = [cond.to_sql() for cond in self.sub_conditions]
            joined = f" {self.logical_operator} ".join(conditions)
            return f"({joined})"

        # Format value
        if self.value is None:
            formatted_value = "NULL"
        elif isinstance(self.value, str):
            # Escape single quotes
            escaped = self.value.replace("'", "''")
            formatted_value = f"'{escaped}'"
        elif isinstance(self.value, bool):
            formatted_value = "TRUE" if self.value else "FALSE"
        else:
            formatted_value = str(self.value)

        return f"{self.field} {self.operator} {formatted_value}"

    def __and__(self, other: "QueryCondition") -> "QueryCondition":
        """Combine conditions with AND."""
        combined = QueryCondition()
        combined.sub_conditions = [self, other]
        combined.logical_operator = "AND"
        return combined

    def __or__(self, other: "QueryCondition") -> "QueryCondition":
        """Combine conditions with OR."""
        combined = QueryCondition()
        combined.sub_conditions = [self, other]
        combined.logical_operator = "OR"
        return combined


class QueryBuilder:
    """
    SQL query builder for constructing queries programmatically.

    Equivalent to C++ sql_query_builder class.

    This builder is NOT thread-safe. Each thread should use its own instance.

    Warning:
        Avoid using raw methods with user input to prevent SQL injection.
        Use parameterized methods instead.
    """

    def __init__(self):
        """Initialize query builder."""
        self._query_type: Optional[str] = None
        self._select_columns: List[str] = []
        self._from_table: Optional[str] = None
        self._where_conditions: List[QueryCondition] = []
        self._joins: List[str] = []
        self._group_by_columns: List[str] = []
        self._having_clause: Optional[str] = None
        self._order_by_clauses: List[str] = []
        self._limit_count: Optional[int] = None
        self._offset_count: Optional[int] = None

        # For INSERT/UPDATE
        self._target_table: Optional[str] = None
        self._set_data: Dict[str, DatabaseValue] = {}
        self._insert_rows: List[Dict[str, DatabaseValue]] = []

    # SELECT operations

    def select(self, columns: Union[str, List[str]]) -> "QueryBuilder":
        """
        Add SELECT columns.

        Args:
            columns: Single column or list of columns to select.
                    Use "*" to select all columns.

        Returns:
            Self for chaining.
        """
        self._query_type = "SELECT"
        if isinstance(columns, str):
            self._select_columns.append(columns)
        else:
            self._select_columns.extend(columns)
        return self

    def from_table(self, table: str) -> "QueryBuilder":
        """
        Set FROM table.

        Args:
            table: Table name

        Returns:
            Self for chaining.
        """
        self._from_table = table
        return self

    # WHERE conditions

    def where(
        self,
        field: str,
        operator: str,
        value: DatabaseValue,
    ) -> "QueryBuilder":
        """
        Add WHERE condition.

        Args:
            field: Field name
            operator: Comparison operator (=, !=, >, <, >=, <=, LIKE, IN)
            value: Value to compare

        Returns:
            Self for chaining.
        """
        condition = QueryCondition(field, operator, value)
        self._where_conditions.append(condition)
        return self

    def where_condition(self, condition: QueryCondition) -> "QueryBuilder":
        """
        Add WHERE condition object.

        Args:
            condition: QueryCondition instance

        Returns:
            Self for chaining.
        """
        self._where_conditions.append(condition)
        return self

    def where_raw(self, raw_where: str) -> "QueryBuilder":
        """
        Add raw WHERE clause (use with caution).

        Args:
            raw_where: Raw SQL WHERE condition

        Returns:
            Self for chaining.
        """
        condition = QueryCondition(raw_condition=raw_where)
        self._where_conditions.append(condition)
        return self

    # JOIN operations

    def join(
        self,
        table: str,
        condition: str,
        join_type: JoinType = JoinType.INNER,
    ) -> "QueryBuilder":
        """
        Add JOIN clause.

        Args:
            table: Table to join
            condition: JOIN condition (e.g., "users.id = orders.user_id")
            join_type: Type of join (INNER, LEFT, RIGHT, etc.)

        Returns:
            Self for chaining.
        """
        join_str = f"{join_type.to_sql()} {table} ON {condition}"
        self._joins.append(join_str)
        return self

    def left_join(self, table: str, condition: str) -> "QueryBuilder":
        """Add LEFT JOIN clause."""
        return self.join(table, condition, JoinType.LEFT)

    def right_join(self, table: str, condition: str) -> "QueryBuilder":
        """Add RIGHT JOIN clause."""
        return self.join(table, condition, JoinType.RIGHT)

    # GROUP BY and HAVING

    def group_by(self, columns: Union[str, List[str]]) -> "QueryBuilder":
        """
        Add GROUP BY columns.

        Args:
            columns: Single column or list of columns

        Returns:
            Self for chaining.
        """
        if isinstance(columns, str):
            self._group_by_columns.append(columns)
        else:
            self._group_by_columns.extend(columns)
        return self

    def having(self, condition: str) -> "QueryBuilder":
        """
        Add HAVING clause.

        Args:
            condition: HAVING condition

        Returns:
            Self for chaining.
        """
        self._having_clause = condition
        return self

    # ORDER BY

    def order_by(
        self, column: str, order: SortOrder = SortOrder.ASC
    ) -> "QueryBuilder":
        """
        Add ORDER BY clause.

        Args:
            column: Column to sort by
            order: Sort order (ASC or DESC)

        Returns:
            Self for chaining.
        """
        order_str = f"{column} {order.to_sql()}"
        self._order_by_clauses.append(order_str)
        return self

    # LIMIT and OFFSET

    def limit(self, count: int) -> "QueryBuilder":
        """
        Set LIMIT.

        Args:
            count: Maximum number of rows to return

        Returns:
            Self for chaining.
        """
        self._limit_count = count
        return self

    def offset(self, count: int) -> "QueryBuilder":
        """
        Set OFFSET.

        Args:
            count: Number of rows to skip

        Returns:
            Self for chaining.
        """
        self._offset_count = count
        return self

    # INSERT operations

    def insert_into(self, table: str) -> "QueryBuilder":
        """
        Start INSERT query.

        Args:
            table: Table to insert into

        Returns:
            Self for chaining.
        """
        self._query_type = "INSERT"
        self._target_table = table
        return self

    def values(
        self, data: Union[Dict[str, DatabaseValue], List[Dict[str, DatabaseValue]]]
    ) -> "QueryBuilder":
        """
        Set values for INSERT.

        Args:
            data: Single row dict or list of row dicts

        Returns:
            Self for chaining.
        """
        if isinstance(data, dict):
            self._insert_rows.append(data)
        else:
            self._insert_rows.extend(data)
        return self

    # UPDATE operations

    def update(self, table: str) -> "QueryBuilder":
        """
        Start UPDATE query.

        Args:
            table: Table to update

        Returns:
            Self for chaining.
        """
        self._query_type = "UPDATE"
        self._target_table = table
        return self

    def set(
        self, field_or_data: Union[str, Dict[str, DatabaseValue]], value: Optional[DatabaseValue] = None
    ) -> "QueryBuilder":
        """
        Set field values for UPDATE.

        Args:
            field_or_data: Field name or dict of field-value pairs
            value: Value to set (if field_or_data is a field name)

        Returns:
            Self for chaining.
        """
        if isinstance(field_or_data, str):
            self._set_data[field_or_data] = value
        else:
            self._set_data.update(field_or_data)
        return self

    # DELETE operations

    def delete_from(self, table: str) -> "QueryBuilder":
        """
        Start DELETE query.

        Args:
            table: Table to delete from

        Returns:
            Self for chaining.
        """
        self._query_type = "DELETE"
        self._target_table = table
        return self

    # Build query

    def build(self) -> str:
        """
        Build final SQL query string.

        Returns:
            SQL query string.
        """
        if self._query_type == "SELECT":
            return self._build_select()
        elif self._query_type == "INSERT":
            return self._build_insert()
        elif self._query_type == "UPDATE":
            return self._build_update()
        elif self._query_type == "DELETE":
            return self._build_delete()
        else:
            raise ValueError("No query type set")

    def _build_select(self) -> str:
        """Build SELECT query."""
        parts = []

        # SELECT columns
        columns = ", ".join(self._select_columns) if self._select_columns else "*"
        parts.append(f"SELECT {columns}")

        # FROM table
        if self._from_table:
            parts.append(f"FROM {self._from_table}")

        # JOINs
        for join in self._joins:
            parts.append(join)

        # WHERE
        if self._where_conditions:
            where_clauses = [cond.to_sql() for cond in self._where_conditions]
            parts.append(f"WHERE {' AND '.join(where_clauses)}")

        # GROUP BY
        if self._group_by_columns:
            parts.append(f"GROUP BY {', '.join(self._group_by_columns)}")

        # HAVING
        if self._having_clause:
            parts.append(f"HAVING {self._having_clause}")

        # ORDER BY
        if self._order_by_clauses:
            parts.append(f"ORDER BY {', '.join(self._order_by_clauses)}")

        # LIMIT
        if self._limit_count is not None:
            parts.append(f"LIMIT {self._limit_count}")

        # OFFSET
        if self._offset_count is not None:
            parts.append(f"OFFSET {self._offset_count}")

        return " ".join(parts)

    def _build_insert(self) -> str:
        """Build INSERT query."""
        if not self._insert_rows:
            raise ValueError("No values specified for INSERT")

        first_row = self._insert_rows[0]
        columns = list(first_row.keys())
        columns_str = ", ".join(columns)

        # Build values
        values_lists = []
        for row in self._insert_rows:
            values = [self._format_value(row.get(col)) for col in columns]
            values_lists.append(f"({', '.join(values)})")

        values_str = ", ".join(values_lists)

        return f"INSERT INTO {self._target_table} ({columns_str}) VALUES {values_str}"

    def _build_update(self) -> str:
        """Build UPDATE query."""
        if not self._set_data:
            raise ValueError("No SET data specified for UPDATE")

        # SET clause
        set_clauses = [
            f"{field} = {self._format_value(value)}"
            for field, value in self._set_data.items()
        ]
        set_str = ", ".join(set_clauses)

        parts = [f"UPDATE {self._target_table}", f"SET {set_str}"]

        # WHERE
        if self._where_conditions:
            where_clauses = [cond.to_sql() for cond in self._where_conditions]
            parts.append(f"WHERE {' AND '.join(where_clauses)}")

        return " ".join(parts)

    def _build_delete(self) -> str:
        """Build DELETE query."""
        parts = [f"DELETE FROM {self._target_table}"]

        # WHERE
        if self._where_conditions:
            where_clauses = [cond.to_sql() for cond in self._where_conditions]
            parts.append(f"WHERE {' AND '.join(where_clauses)}")

        return " ".join(parts)

    def _format_value(self, value: DatabaseValue) -> str:
        """Format value for SQL."""
        if value is None:
            return "NULL"
        elif isinstance(value, str):
            # Escape single quotes
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        else:
            return str(value)

    # Reset builder

    def reset(self) -> None:
        """Reset builder to initial state."""
        self._query_type = None
        self._select_columns = []
        self._from_table = None
        self._where_conditions = []
        self._joins = []
        self._group_by_columns = []
        self._having_clause = None
        self._order_by_clauses = []
        self._limit_count = None
        self._offset_count = None
        self._target_table = None
        self._set_data = {}
        self._insert_rows = []
