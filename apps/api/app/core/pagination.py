"""Cursor-based pagination utilities."""

import base64
import json
from uuid import UUID

from sqlalchemy import Select


def encode_cursor(id: UUID) -> str:
    """Encode a UUID into an opaque cursor string."""
    return base64.urlsafe_b64encode(json.dumps({"id": str(id)}).encode()).decode()


def decode_cursor(cursor: str) -> UUID:
    """Decode an opaque cursor string back into a UUID."""
    data = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
    return UUID(data["id"])


def apply_cursor(query: Select, cursor: str | None, id_column, limit: int) -> Select:
    """Apply cursor-based pagination to a SQLAlchemy select query.

    Uses the id column as the cursor key with descending order
    (newest first). The cursor points to the last item seen.
    """
    if cursor:
        cursor_id = decode_cursor(cursor)
        query = query.where(id_column < cursor_id)
    return query.order_by(id_column.desc()).limit(limit + 1)  # Fetch one extra to check has_more
