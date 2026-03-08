"""
Alembic migration: create model_registry table
Revision: 002_add_model_registry
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

revision = "002_model_registry"
down_revision = "001_monitoring"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── ENUM TYPES ────────────────────────────────────────────────────────────
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE registry_model_type_enum AS ENUM ('price_forecast', 'disease_detection');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE model_status_enum AS ENUM ('candidate', 'active', 'degraded');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # ─── TABLE ─────────────────────────────────────────────────────────────────
    op.create_table(
        "model_registry",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "model_type",
            sa.Enum("price_forecast", "disease_detection", name="registry_model_type_enum"),
            nullable=False,
        ),
        sa.Column("model_version", sa.String(128), nullable=False),
        sa.Column(
            "status",
            sa.Enum("candidate", "active", "degraded", name="model_status_enum"),
            nullable=False,
            server_default="candidate",
        ),
        sa.Column("trained_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metrics_snapshot", JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ─── REGULAR INDEXES ───────────────────────────────────────────────────────
    op.create_index(
        "ix_model_registry_type_version", "model_registry", ["model_type", "model_version"]
    )
    op.create_index("ix_model_registry_status", "model_registry", ["status"])

    # ─── PARTIAL UNIQUE INDEX ─────────────────────────────────────────────────
    # Guarantees at most ONE active record per model_type at the database level.
    # This cannot be expressed with SQLAlchemy's high-level Index API — must be raw SQL.
    op.execute("""
        CREATE UNIQUE INDEX uix_one_active_per_type
        ON model_registry (model_type)
        WHERE status = 'active';
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uix_one_active_per_type;")
    op.drop_index("ix_model_registry_status", table_name="model_registry")
    op.drop_index("ix_model_registry_type_version", table_name="model_registry")
    op.drop_table("model_registry")
    op.execute("DROP TYPE IF EXISTS model_status_enum;")
    op.execute("DROP TYPE IF EXISTS registry_model_type_enum;")
