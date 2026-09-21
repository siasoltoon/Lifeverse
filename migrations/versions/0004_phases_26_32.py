"""background jobs, observability and production support schema"""

from alembic import op
import sqlalchemy as sa

revision = "0004_phases_26_32"
down_revision = "0003_phases_16_25"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "background_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("job_type", sa.String(96), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="queued"),
        sa.Column("payload", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("run_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("locked_by", sa.String(128)),
        sa.Column("locked_at", sa.DateTime(timezone=True)),
        sa.Column("idempotency_key", sa.String(160), nullable=False, unique=True),
        sa.Column("last_error", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_background_jobs_claim", "background_jobs", ["status", "run_at"])
    op.create_index("ix_background_jobs_lock", "background_jobs", ["status", "locked_at"])


def downgrade():
    op.drop_index("ix_background_jobs_lock", table_name="background_jobs")
    op.drop_index("ix_background_jobs_claim", table_name="background_jobs")
    op.drop_table("background_jobs")
