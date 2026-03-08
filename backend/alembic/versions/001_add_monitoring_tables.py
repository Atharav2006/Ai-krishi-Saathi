"""
Alembic migration: add model monitoring tables
Revision: 001_add_monitoring_tables
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

revision = "001_monitoring"
down_revision = None  # Set this to your latest existing revision if applicable
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── ENUM TYPE ─────────────────────────────────────────────────────────────
    # Create enum only if not exists (idempotent)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE model_type_enum AS ENUM ('price_forecast', 'disease_detection');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # ─── prediction_logs ───────────────────────────────────────────────────────
    op.create_table(
        "prediction_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("model_type", sa.Enum("price_forecast", "disease_detection",
                                        name="model_type_enum"), nullable=False),
        sa.Column("model_version", sa.String(64), nullable=False),
        sa.Column("input_hash", sa.String(64), nullable=False),
        sa.Column("predicted_value", sa.Text, nullable=False),
        sa.Column("confidence_score", sa.Float, nullable=False),
        sa.Column("latency_ms", sa.Float, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_prediction_logs_model_version", "prediction_logs", ["model_version"])
    op.create_index("ix_prediction_logs_model_type", "prediction_logs", ["model_type"])
    op.create_index("ix_prediction_logs_created_at", "prediction_logs", ["created_at"])
    op.create_index("ix_prediction_logs_input_hash", "prediction_logs", ["input_hash"])

    # ─── ground_truth_logs ─────────────────────────────────────────────────────
    op.create_table(
        "ground_truth_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("prediction_id", UUID(as_uuid=True),
                  sa.ForeignKey("prediction_logs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actual_value", sa.Text, nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint(
        "uq_ground_truth_prediction_id", "ground_truth_logs", ["prediction_id"]
    )
    op.create_index("ix_ground_truth_logs_recorded_at", "ground_truth_logs", ["recorded_at"])

    # ─── model_metrics ─────────────────────────────────────────────────────────
    op.create_table(
        "model_metrics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("model_type", sa.Enum("price_forecast", "disease_detection",
                                        name="model_type_enum"), nullable=False),
        sa.Column("model_version", sa.String(64), nullable=False),
        sa.Column("metric_name", sa.String(50), nullable=False),
        sa.Column("metric_value", sa.Float, nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_model_metrics_type_version", "model_metrics", ["model_type", "model_version"]
    )


def downgrade() -> None:
    op.drop_table("model_metrics")
    op.drop_table("ground_truth_logs")
    op.drop_table("prediction_logs")
    op.execute("DROP TYPE IF EXISTS model_type_enum;")
