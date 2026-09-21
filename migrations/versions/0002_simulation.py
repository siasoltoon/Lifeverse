"""phases 6-15 persistent simulation schema"""

from alembic import op
import sqlalchemy as sa

revision = "0002_simulation"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "world_clock",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("world_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("speed", sa.Numeric(8, 2), nullable=False),
        sa.Column("paused", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
    )
    op.create_table(
        "world_state",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "employments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "character_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
    )
    op.add_column(
        "jobs", sa.Column("base_salary", sa.Numeric(18, 2), nullable=False, server_default="0")
    )
    op.add_column(
        "jobs", sa.Column("work_hours", sa.Numeric(5, 2), nullable=False, server_default="8")
    )
    op.create_table(
        "skills",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("max_level", sa.Integer(), nullable=False),
    )
    op.create_table(
        "character_skills",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "character_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "skill_id", sa.Uuid(), sa.ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("xp", sa.Integer(), nullable=False),
        sa.UniqueConstraint("character_id", "skill_id", name="uq_character_skill"),
    )
    op.create_table(
        "item_ext",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "item_id",
            sa.Uuid(),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("weight", sa.Numeric(8, 3), nullable=False),
        sa.Column("base_price", sa.Numeric(18, 2), nullable=False),
    )
    op.add_column(
        "items", sa.Column("kind", sa.String(32), nullable=False, server_default="generic")
    )
    op.add_column(
        "items", sa.Column("weight", sa.Numeric(8, 3), nullable=False, server_default="0")
    )
    op.add_column(
        "items", sa.Column("base_price", sa.Numeric(18, 2), nullable=False, server_default="0")
    )
    op.create_table(
        "properties",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "city_id", sa.Uuid(), sa.ForeignKey("cities.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(18, 2), nullable=False),
    )
    op.create_table(
        "property_ownerships",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "property_id",
            sa.Uuid(),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "character_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("acquired_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("travel_speed", sa.Numeric(8, 2), nullable=False),
    )
    op.create_table(
        "character_vehicles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "character_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "vehicle_id",
            sa.Uuid(),
            sa.ForeignKey("vehicles.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("acquired_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "travels",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "character_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "from_city_id",
            sa.Uuid(),
            sa.ForeignKey("cities.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "to_city_id", sa.Uuid(), sa.ForeignKey("cities.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("departure_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("arrival_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "social_relations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "source_character_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_character_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.UniqueConstraint(
            "source_character_id", "target_character_id", "kind", name="uq_social_relation"
        ),
    )
    op.add_column(
        "npcs", sa.Column("role", sa.String(64), nullable=False, server_default="citizen")
    )
    op.add_column(
        "npcs", sa.Column("disposition", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column(
        "missions", sa.Column("description", sa.Text(), nullable=False, server_default="")
    )
    op.add_column(
        "missions", sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column(
        "missions",
        sa.Column("currency_reward", sa.Numeric(18, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "missions", sa.Column("required_level", sa.Integer(), nullable=False, server_default="1")
    )
    op.create_table(
        "character_missions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "character_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "mission_id",
            sa.Uuid(),
            sa.ForeignKey("missions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("state", sa.String(32), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("character_id", "mission_id", name="uq_character_mission"),
    )
    op.create_table(
        "ledger_accounts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column(
            "currency_id",
            sa.Uuid(),
            sa.ForeignKey("currencies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    op.create_table(
        "ledger_transactions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False, unique=True),
        sa.Column("reference", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "transaction_id",
            sa.Uuid(),
            sa.ForeignKey("ledger_transactions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "ledger_account_id",
            sa.Uuid(),
            sa.ForeignKey("ledger_accounts.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("direction", sa.String(8), nullable=False),
        sa.Index("ix_ledger_entries_tx_account", "transaction_id", "ledger_account_id"),
    )
    op.create_table(
        "market_listings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "seller_character_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "item_id", sa.Uuid(), sa.ForeignKey("items.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 2), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
    )
    op.create_table(
        "businesses",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "owner_character_id",
            sa.Uuid(),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "city_id", sa.Uuid(), sa.ForeignKey("cities.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("kind", sa.String(64), nullable=False),
        sa.Column("balance", sa.Numeric(18, 2), nullable=False),
    )


def downgrade():
    for t in [
        "businesses",
        "market_listings",
        "ledger_entries",
        "ledger_transactions",
        "ledger_accounts",
        "character_missions",
        "social_relations",
        "travels",
        "character_vehicles",
        "vehicles",
        "property_ownerships",
        "properties",
        "character_skills",
        "skills",
        "employments",
        "world_state",
        "world_clock",
    ]:
        op.drop_table(t)
    for table, col in [
        ("missions", "required_level"),
        ("missions", "currency_reward"),
        ("missions", "xp_reward"),
        ("missions", "description"),
        ("npcs", "disposition"),
        ("npcs", "role"),
        ("items", "base_price"),
        ("items", "weight"),
        ("items", "kind"),
        ("jobs", "work_hours"),
        ("jobs", "base_salary"),
    ]:
        op.drop_column(table, col)
