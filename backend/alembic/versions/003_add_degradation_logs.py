"""
Alembic migration: create model_degradation_logs table
Revision: 003_add_degradation_logs
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

revision = "003_degradation_logs"
down_revision = "002_model_registry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # model_type_enum already exists from migration 001 — no need to re-create
    op.create_table(
        "model_degradation_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "model_type",
            sa.Enum("price_forecast", "disease_detection", name="model_type_enum"),
            nullable=False,
        ),
        sa.Column("model_version", sa.String(64), nullable=False),
        sa.Column("metric_name", sa.String(50), nullable=False),
        sa.Column("metric_value", sa.Float, nullable=False),
        sa.Column("threshold", sa.Float, nullable=False),
        sa.Column(
            "triggered_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_degradation_logs_type_version_metric",
        "model_degradation_logs",
        ["model_type", "model_version", "metric_name"],
    )
    op.create_index(
        "ix_degradation_logs_triggered_at",
        "model_degradation_logs",
        ["triggered_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_degradation_logs_triggered_at", table_name="model_degradation_logs")
    op.drop_index("ix_degradation_logs_type_version_metric", table_name="model_degradation_logs")
    op.drop_table("model_degradation_logs")
