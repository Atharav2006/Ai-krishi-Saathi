"""
Alembic migration: create model_retraining_jobs table
Revision: 004_add_retraining_jobs
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

revision = "004_retraining_jobs"
down_revision = "003_degradation_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE retraining_trigger_enum AS ENUM ('degradation', 'manual');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE retraining_status_enum AS ENUM ('pending', 'running', 'success', 'failed');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    op.create_table(
        "model_retraining_jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("model_type", sa.String(64), nullable=False),
        sa.Column(
            "triggered_by",
            sa.Enum("degradation", "manual", name="retraining_trigger_enum"),
            nullable=False,
            server_default="degradation",
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "running", "success", "failed", name="retraining_status_enum"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("old_model_version", sa.String(128), nullable=False),
        sa.Column("new_model_version", sa.String(128), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_retraining_jobs_model_type_status",
        "model_retraining_jobs",
        ["model_type", "status"],
    )
    op.create_index(
        "ix_retraining_jobs_created_at",
        "model_retraining_jobs",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_retraining_jobs_created_at", table_name="model_retraining_jobs")
    op.drop_index("ix_retraining_jobs_model_type_status", table_name="model_retraining_jobs")
    op.drop_table("model_retraining_jobs")
    op.execute("DROP TYPE IF EXISTS retraining_status_enum;")
    op.execute("DROP TYPE IF EXISTS retraining_trigger_enum;")
