from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB

# SQLite-compatible JSON column (JSONB on PostgreSQL).
JsonDocument = JSON().with_variant(JSONB, "postgresql")
