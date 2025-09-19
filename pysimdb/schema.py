class SchemaError(Exception):
    pass

class TableSchema:
    """Manage table schema and validate records."""

    def __init__(self, fields: dict, primary_key: str = None):
        self.fields = fields
        self.primary_key = primary_key
        if primary_key and primary_key not in fields:
            raise ValueError(f"Primary key '{primary_key}' must be a field in schema")

    def validate(self, record: dict):
        for field, ftype in self.fields.items():
            if field not in record:
                raise SchemaError(f"Missing field '{field}'")
            if not isinstance(record[field], ftype):
                raise SchemaError(f"Field '{field}' must be of type {ftype.__name__}")
        if self.primary_key and self.primary_key not in record:
            raise SchemaError(f"Missing primary key '{self.primary_key}'")
