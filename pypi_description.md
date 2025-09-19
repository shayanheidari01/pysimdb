# PySimDB

A lightweight, JSON-based database library for Python that provides a simple yet powerful interface for storing and querying structured data.

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

## License

This project is licensed under the GNU General Public License v3.0.