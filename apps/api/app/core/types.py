"""Cross-database compatible column types."""

import json
import uuid as _uuid

from sqlalchemy import String, Text, TypeDecorator


class GUID(TypeDecorator):
    """Platform-independent UUID type. Stores as String(36) on SQLite, native UUID on Postgres."""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return _uuid.UUID(value) if not isinstance(value, _uuid.UUID) else value
        return None


class StringArray(TypeDecorator):
    """Store a list[str] as JSON text — works on both Postgres and SQLite."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return []
