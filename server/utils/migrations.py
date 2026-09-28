"""Lightweight, idempotent schema migrations.

The project has no Alembic setup — tables are created by ``db.create_all()``,
which never alters an existing table. Any column added to a model after a local
database already exists would therefore be missing at runtime. ``ensure_schema``
closes that gap by adding known columns when they are absent, so existing
databases keep working without being deleted and re-seeded.
"""
from sqlalchemy import inspect, text
from models import db

# Columns added to existing tables after their initial release, mapped to the
# DDL used to add them. Each entry must be safe to apply to an existing row set.
_ADDED_COLUMNS: dict[str, dict[str, str]] = {
    'games': {
        'is_archived': 'ALTER TABLE games ADD COLUMN is_archived BOOLEAN NOT NULL DEFAULT 0',
    },
}


def ensure_schema() -> list[str]:
    """Apply any missing column additions and return the statements executed."""
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())
    applied: list[str] = []

    for table_name, columns in _ADDED_COLUMNS.items():
        if table_name not in existing_tables:
            # Table does not exist yet, so create_all() will build it in full.
            continue

        existing_columns = {column['name'] for column in inspector.get_columns(table_name)}

        for column_name, statement in columns.items():
            if column_name in existing_columns:
                continue

            db.session.execute(text(statement))
            db.session.commit()
            applied.append(statement)
            print(f'Applied schema migration: {statement}')

    return applied
