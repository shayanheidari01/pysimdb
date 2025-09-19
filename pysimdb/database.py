import os
import pysimdb

class JsonDatabase:
    """
    JSON Database with CRUD, schema validation, and transaction support.
    """

    def __init__(self, path="data"):
        self.storage = pysimdb.JsonStorage(path)
        self.schemas = {}  # table_name -> TableSchema
        self.indexes = {}  # table_name -> dict of records by primary key
        # secondary indexes: table -> field -> {value: set(primary_key)}
        self.secondary_indexes = {}
        # metadata of which fields are indexed for a table
        self.indexes_meta = {}

    def create_table(self, table, schema: "pysimdb.TableSchema"):
        self.schemas[table] = schema
        self.storage.create_table(table)
        self._rebuild_index(table)

    def drop_table(self, table: str):
        """Remove table file and clear schema/index in memory."""
        file = os.path.join(self.storage.base_path, f"{table}.json")
        try:
            if os.path.exists(file):
                os.remove(file)
        except OSError:
            pass
        self.schemas.pop(table, None)
        self.indexes.pop(table, None)
        self.secondary_indexes.pop(table, None)
        self.indexes_meta.pop(table, None)

    def insert(self, table, record: dict, if_exists: str = "error"):
        schema = self.schemas.get(table)
        if schema:
            schema.validate(record)
        # ensure index reflects file state
        self._rebuild_index(table)
        self.indexes.setdefault(table, {})
        pk = schema.primary_key if schema else None

        data = self.storage.load(table)

        if pk:
            if pk not in record:
                raise ValueError(f"Primary key '{pk}' is required for table '{table}'")
            exists = record[pk] in self.indexes.get(table, {})
            if exists:
                if if_exists == "error":
                    raise ValueError(
                        f"Duplicate primary key '{pk}'={record[pk]} in table '{table}'"
                    )
                if if_exists == "ignore":
                    return
                if if_exists == "replace":
                    # replace existing record in-place
                    for i, row in enumerate(data):
                        if row.get(pk) == record[pk]:
                            data[i] = record
                            break
                    self.storage.save(table, data)
                    self._rebuild_index(table)
                    return

        # append new record
        data.append(record)
        self.storage.save(table, data)
        # refresh index
        self._rebuild_index(table)
        # update secondary indexes (map values to primary keys)
        schema = self.schemas.get(table)
        if schema and schema.primary_key and table in self.secondary_indexes:
            pk = schema.primary_key
            pk_val = record.get(pk)
            if pk_val is not None:
                for field, idx in self.secondary_indexes.get(table, {}).items():
                    if field in record:
                        val = record[field]
                        idx.setdefault(val, set()).add(pk_val)

    def select(self, table):
        # return rows in file order; callers can still rely on indexes if needed
        return self.storage.load(table)
        
    def query(self, table):
        """Create a new query builder for the specified table."""
        from .query_builder import QueryBuilder
        return QueryBuilder(self, table)

    def update(self, table, where: dict, updates: dict):
        data = self.storage.load(table)
        schema = self.schemas.get(table)
        changed = False
        for row in data:
            if all(row.get(k) == v for k, v in where.items()):
                # track old values for indexed fields
                old_vals = {}
                if schema and schema.primary_key and table in self.secondary_indexes:
                    for field in self.secondary_indexes.get(table, {}):
                        old_vals[field] = row.get(field)
                row.update(updates)
                # update secondary indexes if necessary
                if schema and schema.primary_key and table in self.secondary_indexes:
                    pk = row.get(schema.primary_key)
                    for field, idx in self.secondary_indexes.get(table, {}).items():
                        old = old_vals.get(field)
                        new = row.get(field)
                        if old != new:
                            if old in idx and pk in idx[old]:
                                idx[old].discard(pk)
                                if not idx[old]:
                                    idx.pop(old, None)
                            if new is not None:
                                idx.setdefault(new, set()).add(pk)
                changed = True
        if changed:
            self.storage.save(table, data)
            self._rebuild_index(table)

    def delete(self, table, where: dict):
        data = self.storage.load(table)
        new_data = []
        removed_pks = []
        schema = self.schemas.get(table)
        for row in data:
            if not all(row.get(k) == v for k, v in where.items()):
                new_data.append(row)
            else:
                if schema and schema.primary_key:
                    removed_pks.append(row.get(schema.primary_key))
        if len(new_data) != len(data):
            self.storage.save(table, new_data)
            # remove pks from secondary indexes
            if schema and schema.primary_key and table in self.secondary_indexes:
                for field, idx in self.secondary_indexes.get(table, {}).items():
                    for pk in removed_pks:
                        # need to find which value mapped to this pk
                        # iterate values and remove pk where present
                        to_remove = []
                        for val, pks in list(idx.items()):
                            if pk in pks:
                                pks.discard(pk)
                                if not pks:
                                    to_remove.append(val)
                        for val in to_remove:
                            idx.pop(val, None)
            self._rebuild_index(table)

    # -- Secondary index API --
    def create_index(self, table: str, field: str):
        """Create a secondary index on `field` for `table`. Requires table to have a primary key."""
        schema = self.schemas.get(table)
        if not schema or not schema.primary_key:
            raise ValueError("create_index requires table with a primary key")
        self._rebuild_index(table)
        pk_index = self.indexes.get(table, {})
        idx = {}
        for pk, row in pk_index.items():
            val = row.get(field)
            if val is not None:
                idx.setdefault(val, set()).add(pk)
        self.secondary_indexes.setdefault(table, {})[field] = idx
        self.indexes_meta.setdefault(table, set()).add(field)

    def drop_index(self, table: str, field: str):
        if table in self.secondary_indexes:
            self.secondary_indexes[table].pop(field, None)
        if table in self.indexes_meta:
            self.indexes_meta[table].discard(field)

    def list_indexes(self, table: str):
        return list(self.indexes_meta.get(table, []))

    def get_rows_by_index(self, table: str, field: str, value):
        # ensure index exists
        if table not in self.secondary_indexes or field not in self.secondary_indexes.get(table, {}):
            # attempt to create index on the fly
            self.create_index(table, field)
        pk_set = self.secondary_indexes.get(table, {}).get(field, {}).get(value, set())
        # ensure pk index is up-to-date
        self._rebuild_index(table)
        pk_index = self.indexes.get(table, {})
        return [pk_index[pk] for pk in pk_set if pk in pk_index]

    def transaction(self, func):
        backup = {}
        for table_file in os.listdir(self.storage.base_path):
            if table_file.endswith(".json"):
                file_path = os.path.join(self.storage.base_path, table_file)
                with open(file_path, "rb") as f:
                    backup[table_file] = f.read()
        try:
            func()
        except Exception as e:
            for file, content in backup.items():
                with open(os.path.join(self.storage.base_path, file), "wb") as f:
                    f.write(content)
            raise e

    def _rebuild_index(self, table):
        schema = self.schemas.get(table)
        data = self.storage.load(table)
        if schema and schema.primary_key:
            self.indexes[table] = {row[schema.primary_key]: row for row in data}
        else:
            self.indexes[table] = {i: row for i, row in enumerate(data)}
