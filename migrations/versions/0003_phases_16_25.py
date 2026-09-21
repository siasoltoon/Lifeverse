"""phases 16-25 simulation systems schema"""

from alembic import op
import sqlalchemy as sa

revision = "0003_phases_16_25"
down_revision = "0002_simulation"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("accounts", sa.Column("password_hash", sa.String(255), nullable=True))
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "account_id",
            sa.Uuid(),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(128), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
    )
    with op.batch_alter_table("businesses") as batch_op:
        batch_op.add_column(
            sa.Column(
                "currency_id",
                sa.Uuid(),
                sa.ForeignKey("currencies.id", ondelete="RESTRICT", name="fk_business_currency"),
                nullable=True,
            )
        )
    op.create_table(
        "event_definitions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("repeatable", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("cooldown_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "business_employees",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "business_id",
            sa.Uuid(),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "character_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("wage", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.UniqueConstraint("business_id", "character_id", name="uq_business_employee"),
    )
    op.create_table(
        "market_orders",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "listing_id",
            sa.Uuid(),
            sa.ForeignKey("market_listings.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "buyer_character_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("total_price", sa.Numeric(18, 2), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False, unique=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="completed"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "law_cases",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "character_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("state", sa.String(32), nullable=False, server_default="open"),
        sa.Column("evidence", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "combat_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "attacker_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "defender_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("state", sa.String(32), nullable=False, server_default="active"),
        sa.Column("turn", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "ai_intents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("actor_id", sa.Uuid(), sa.ForeignKey("characters.id", ondelete="SET NULL")),
        sa.Column("intent_type", sa.String(64), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("state", sa.String(32), nullable=False, server_default="proposed"),
        sa.Column("rejection_reason", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "translations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("locale", sa.String(8), nullable=False),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.UniqueConstraint("locale", "key", name="uq_translation_locale_key"),
    )
    op.create_table(
        "exploit_signals",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("character_id", sa.Uuid(), sa.ForeignKey("characters.id", ondelete="SET NULL")),
        sa.Column("rule", sa.String(64), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("state", sa.String(32), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "rate_limit_buckets",
        sa.Column("key", sa.String(128), primary_key=True),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("limit_value", sa.Integer(), nullable=False),
    )
    op.create_index(
        "ix_game_events_type_time", "game_events", ["event_type", "scheduled_at", "state"]
    )
    op.create_index("ix_market_listings_open_item", "market_listings", ["item_id", "status"])
    op.create_index("ix_ai_intents_state", "ai_intents", ["state", "created_at"])
    op.create_index(
        "ix_exploit_signals_character_state", "exploit_signals", ["character_id", "state"]
    )


def downgrade():
    op.drop_table("auth_sessions")
    op.drop_column("accounts", "password_hash")
    with op.batch_alter_table("businesses") as batch_op:
        batch_op.drop_column("currency_id")
    op.drop_index("ix_exploit_signals_character_state", table_name="exploit_signals")
    op.drop_index("ix_ai_intents_state", table_name="ai_intents")
    op.drop_index("ix_market_listings_open_item", table_name="market_listings")
    op.drop_index("ix_game_events_type_time", table_name="game_events")
    for name in (
        "rate_limit_buckets",
        "exploit_signals",
        "translations",
        "ai_intents",
        "combat_sessions",
        "law_cases",
        "market_orders",
        "business_employees",
        "event_definitions",
    ):
        op.drop_table(name)
