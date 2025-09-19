class QueryBuilder:
    """Query builder with where, join, order_by, limit, projection.

    Optimizations:
    - records equality filters and attempts to use the database's secondary
      index API (`get_rows_by_index`) for fast lookups when available.
    """

    def __init__(self, db, table):
        self.db = db
        self.base_table = table
        self.select_columns = None
        self.conditions = []
        # capture equality filters for index usage: field -> value
        self.eq_filters = {}
        self._order_by = None
        self._order_desc = False
        self._limit = None
        self._offset = 0
        self.join_table = None
        self.join_field_base = None
        self.join_field_other = None

    def select(self, *columns):
        self.select_columns = columns
        return self

    def where(self, field, op, value):
        def cond(row):
            v = row.get(field)
            if op == "=":
                return v == value
            if op == "!=":
                return v != value
            if op == "<":
                return v < value
            if op == ">":
                return v > value
            if op == "<=":
                return v <= value
            if op == ">=":
                return v >= value
            if op == "in":
                return v in value
            return False

        self.conditions.append(cond)
        if op == "=":
            # record equality to potentially use indexes later
            self.eq_filters[field] = value
        return self

    def order_by(self, field, desc=False):
        self._order_by = field
        self._order_desc = desc
        return self

    def limit(self, n):
        self._limit = n
        return self

    def offset(self, n):
        self._offset = n
        return self

    def join(self, other_table, base_field, other_field):
        self.join_table = other_table
        self.join_field_base = base_field
        self.join_field_other = other_field
        return self

    def all(self):
        # if we have an equality filter on an indexed field, attempt index lookup
        rows = None
        if self.eq_filters:
            for field, val in self.eq_filters.items():
                try:
                    rows = list(self.db.get_rows_by_index(self.base_table, field, val))
                    break
                except Exception:
                    rows = None

        if rows is None:
            rows = list(self.db.select(self.base_table))

        # apply the remaining filters
        for cond in self.conditions:
            rows = [r for r in rows if cond(r)]

        # join
        if self.join_table:
            other_rows = list(self.db.select(self.join_table))
            joined = []
            for r in rows:
                for o in other_rows:
                    if r.get(self.join_field_base) == o.get(self.join_field_other):
                        merged = {**r, **o}
                        joined.append(merged)
            rows = joined

        # apply order_by
        if self._order_by:
            rows = sorted(rows, key=lambda x: x.get(self._order_by, None), reverse=self._order_desc)

        # apply offset and limit
        if self._offset:
            rows = rows[self._offset:]
        if self._limit is not None:
            rows = rows[:self._limit]

        # apply projection
        if self.select_columns:
            rows = [{k: row[k] for k in self.select_columns if k in row} for row in rows]

        return rows

        # order/offset/limit/projection
        if self._order_by:
            rows.sort(key=lambda r: r.get(self._order_by), reverse=self._order_desc)
        if self._offset:
            rows = rows[self._offset:]
        if self._limit is not None:
            rows = rows[:self._limit]
        if self.select_columns:
            rows = [{col: r.get(col) for col in self.select_columns} for r in rows]
        return rows

    def first(self):
        res = self.limit(1).all()
        return res[0] if res else None
