# PySimDB

[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://github.com/shayanheidari01/pysimdb/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)

**PySimDB** is a lightweight, JSON-based database library for Python that provides a simple yet powerful interface for storing and querying structured data. It offers features similar to SQLite but with a pure Python implementation and JSON storage.

## Features

- **Schema Validation**: Enforce data types and required fields
- **CRUD Operations**: Create, Read, Update, Delete records
- **Query Builder**: Flexible querying with WHERE, ORDER BY, LIMIT, OFFSET
- **Joins**: Join related data from multiple tables
- **Transactions**: Atomic operations with rollback support
- **Indexing**: Secondary indexes for improved query performance
- **Lightweight**: Pure Python implementation with minimal dependencies
- **High Performance**: Uses pysimdjson for fast JSON parsing

## Installation

```bash
pip install pysimdb
```

## Quick Start

```python
from pysimdb import JsonDatabase, TableSchema

# Initialize database
db = JsonDatabase("data")

# Define a schema
user_schema = TableSchema({
    "id": int,
    "name": str,
    "age": int,
    "email": str
}, primary_key="id")

# Create table
db.create_table("users", user_schema)

# Insert data
user = {"id": 1, "name": "John Doe", "age": 30, "email": "john@example.com"}
db.insert("users", user)

# Query data
users = db.query("users").where("age", ">", 25).all()
print(users)
```

## Performance

PySimDB uses `pysimdjson` for high-performance JSON parsing, which significantly improves read performance compared to the standard library's [json](file://c:\Users\ASUS\Desktop\json%20db\data\posts.json) module.

## Detailed Documentation

### 1. Database Initialization

```python
from pysimdb import JsonDatabase

# Initialize with default path ("data")
db = JsonDatabase()

# Initialize with custom path
db = JsonDatabase("my_database")
```

### 2. Schema Definition

Define table schemas with data types and primary keys:

```python
from pysimdb import TableSchema

# Define a schema with primary key
user_schema = TableSchema({
    "id": int,
    "name": str,
    "age": int,
    "email": str
}, primary_key="id")

# Create table with schema
db.create_table("users", user_schema)
```

### 3. CRUD Operations

#### Create (Insert)

```python
# Insert a single record
user = {"id": 1, "name": "John Doe", "age": 30, "email": "john@example.com"}
db.insert("users", user)

# Handle duplicates
db.insert("users", user, if_exists="ignore")    # Ignore if exists
db.insert("users", user, if_exists="replace")   # Replace if exists
```

#### Read (Select)

```python
# Select all records
all_users = db.select("users")

# Query with conditions using QueryBuilder
users = db.query("users").where("age", ">", 25).all()

# Select specific columns
users = db.query("users").select("name", "age").all()
```

#### Update

```python
# Update records matching conditions
db.update("users", {"id": 1}, {"age": 31})
```

#### Delete

```python
# Delete records matching conditions
db.delete("users", {"id": 1})
```

### 4. Query Builder

The QueryBuilder provides a flexible way to query data:

```python
# Basic query
users = db.query("users").all()

# WHERE conditions
users = db.query("users").where("age", ">", 25).all()
users = db.query("users").where("name", "=", "John").all()

# ORDER BY
users = db.query("users").order_by("age").all()          # Ascending
users = db.query("users").order_by("age", desc=True).all()  # Descending

# LIMIT and OFFSET
users = db.query("users").limit(10).offset(20).all()

# SELECT specific columns
users = db.query("users").select("name", "age").all()

# Chaining operations
users = (
    db.query("users")
    .where("age", ">", 25)
    .order_by("age")
    .limit(5)
    .select("name", "age")
    .all()
)
```

### 5. Joins

Join data from multiple tables:

```python
# Join tables
results = (
    db.query("posts")
    .join("users", "user_id", "id")  # (other_table, base_field, other_field)
    .select("title", "name")
    .all()
)
```

### 6. Transactions

Perform atomic operations with rollback support:

```python
def transfer_operation():
    # Deduct from one account
    db.update("accounts", {"id": 1}, {"balance": 900})
    # Add to another account
    db.update("accounts", {"id": 2}, {"balance": 1100})
    # Insert transaction record
    db.insert("transactions", {
        "id": 1,
        "from_account": 1,
        "to_account": 2,
        "amount": 100
    })

# Execute transaction (automatically rolls back on exception)
db.transaction(transfer_operation)
```

### 7. Indexing

Create secondary indexes for improved query performance:

```python
# Create index on a field
db.create_index("users", "age")

# List indexes
indexes = db.list_indexes("users")

# Drop index
db.drop_index("users", "age")
```

### 8. Table Management

```python
# Create table
db.create_table("users", user_schema)

# Drop table
db.drop_table("users")
```

## API Reference

### JsonDatabase

#### `__init__(path="data")`
Initialize the database with a storage path.

#### `create_table(table, schema)`
Create a new table with the specified schema.

#### `drop_table(table)`
Remove a table and all its data.

#### `insert(table, record, if_exists="error")`
Insert a record into a table.
- `if_exists`: "error" (default), "ignore", or "replace"

#### `select(table)`
Select all records from a table.

#### `query(table)`
Create a QueryBuilder for the specified table.

#### `update(table, where, updates)`
Update records matching the where conditions.

#### `delete(table, where)`
Delete records matching the where conditions.

#### `create_index(table, field)`
Create a secondary index on a field.

#### `drop_index(table, field)`
Drop a secondary index.

#### `list_indexes(table)`
List all indexes for a table.

#### `transaction(func)`
Execute a function within a transaction.

### TableSchema

#### `__init__(fields, primary_key=None)`
Define a table schema with field types and optional primary key.

#### `validate(record)`
Validate a record against the schema.

### QueryBuilder

#### `select(*columns)`
Select specific columns.

#### `where(field, op, value)`
Add a WHERE condition.
- `op`: "=", "!=", "<", ">", "<=", ">=", "in"

#### `order_by(field, desc=False)`
Order results by a field.

#### `limit(n)`
Limit the number of results.

#### `offset(n)`
Skip the first n results.

#### `join(other_table, base_field, other_field)`
Join with another table.

#### `all()`
Execute the query and return all results.

#### `first()`
Execute the query and return the first result.

## Error Handling

The library raises specific exceptions for different error conditions:

- `SchemaError`: Raised when schema validation fails
- `ValueError`: Raised for various validation errors
- Other standard Python exceptions for file I/O, etc.

```python
from pysimdb import SchemaError

try:
    db.insert("users", {"id": 1, "name": "John"})  # Missing 'age' field
except SchemaError as e:
    print(f"Schema validation error: {e}")
```

## Performance Considerations

1. **Indexing**: Use secondary indexes for frequently queried fields
2. **Batch Operations**: For bulk inserts, use transactions
3. **Query Optimization**: Use WHERE clauses to limit result sets
4. **Memory Usage**: Large datasets are loaded into memory
5. **JSON Parsing**: Uses pysimdjson for high-performance JSON parsing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## GitHub Repository

[https://github.com/shayanheidari01/pysimdb](https://github.com/shayanheidari01/pysimdb)