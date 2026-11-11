"""persist per-process operational metric snapshots"""

from alembic import op
import sqlalchemy as sa

revision = "0006_operational_metric_snapshots"
down_revision = "0005_worker_heartbeats"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "operational_metric_snapshots",
        sa.Column("instance_id", sa.String(128), primary_key=True),
        sa.Column("service_name", sa.String(16), nullable=False),
        sa.Column("metrics_json", sa.Text(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_operational_metric_snapshots_service_name",
        "operational_metric_snapshots",
        ["service_name"],
    )
    op.create_index(
        "ix_operational_metric_snapshots_last_seen_at",
        "operational_metric_snapshots",
        ["last_seen_at"],
    )


def downgrade():
    op.drop_index(
        "ix_operational_metric_snapshots_last_seen_at",
        table_name="operational_metric_snapshots",
    )
    op.drop_index(
        "ix_operational_metric_snapshots_service_name",
        table_name="operational_metric_snapshots",
    )
    op.drop_table("operational_metric_snapshots")
