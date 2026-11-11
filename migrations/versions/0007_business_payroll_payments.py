"""add an idempotent business payroll payment ledger"""

from alembic import op
import sqlalchemy as sa

revision = "0007_business_payroll"
down_revision = "0006_metrics_snapshots"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "business_payroll_payments",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("business_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("employee_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("character_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("currency_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["employee_id"], ["business_employees.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["currency_id"], ["currencies.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("idempotency_key", name="uq_business_payroll_idempotency_key"),
    )
    op.create_index(
        "ix_business_payroll_payments_business_id",
        "business_payroll_payments",
        ["business_id"],
    )
    op.create_index(
        "ix_business_payroll_payments_employee_id",
        "business_payroll_payments",
        ["employee_id"],
    )


def downgrade():
    op.drop_index(
        "ix_business_payroll_payments_employee_id",
        table_name="business_payroll_payments",
    )
    op.drop_index(
        "ix_business_payroll_payments_business_id",
        table_name="business_payroll_payments",
    )
    op.drop_table("business_payroll_payments")
