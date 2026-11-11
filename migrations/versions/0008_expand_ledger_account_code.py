"""expand ledger account code for full wallet and currency UUIDs"""

from alembic import op
import sqlalchemy as sa

revision = "0008_expand_ledger_account_code"
down_revision = "0007_business_payroll"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("ledger_accounts") as batch_op:
        batch_op.alter_column(
            "code",
            existing_type=sa.String(length=64),
            type_=sa.String(length=128),
            existing_nullable=False,
        )


def downgrade():
    bind = op.get_bind()
    oversized = bind.scalar(
        sa.text("SELECT COUNT(*) FROM ledger_accounts WHERE length(code) > 64")
    )
    if oversized:
        raise RuntimeError(
            "Cannot downgrade ledger account codes while values exceed 64 characters"
        )
    with op.batch_alter_table("ledger_accounts") as batch_op:
        batch_op.alter_column(
            "code",
            existing_type=sa.String(length=128),
            type_=sa.String(length=64),
            existing_nullable=False,
        )
