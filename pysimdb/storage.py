import os
import json
import shutil
import tempfile
from threading import Lock
try:
    import simdjson
    parser = simdjson.Parser()
except Exception:
    parser = None

lock = Lock()

class JsonStorage:
    """Manage JSON files for database tables."""

    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def _file_path(self, table: str) -> str:
        return os.path.join(self.base_path, f"{table}.json")

    def load(self, table: str) -> list:
        file = self._file_path(table)
        if not os.path.exists(file):
            return []
        with open(file, "rb") as f:
            raw = f.read().strip()
            if not raw:
                return []
            try:
                if parser:
                    data = parser.parse(raw)
                    return [dict(row) for row in data]
                # fallback to Python json
                return json.loads(raw.decode("utf-8"))
            except ValueError:
                return []

    def save(self, table: str, data: list):
        file = self._file_path(table)
        dirpath = os.path.dirname(file)
        fd, tmp_file = tempfile.mkstemp(prefix=f"{table}-", suffix=".tmp", dir=dirpath)
        try:
            with lock:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                # os.replace is atomic on Windows and will overwrite destination
                os.replace(tmp_file, file)
        finally:
            # in case of exception, ensure tmp_file removed if exists
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except OSError:
                pass

    def create_table(self, table: str):
        file = self._file_path(table)
        if not os.path.exists(file):
            self.save(table, [])
