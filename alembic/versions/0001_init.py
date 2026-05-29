from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "geos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_geos_code", "geos", ["code"], unique=True)

    op.create_table(
        "inforeasons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("geo_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=True, server_default="google_news_rss"),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("emotional_trigger", sa.String(length=64), nullable=True),
        sa.Column("urgency", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_inforeasons_geo_id", "inforeasons", ["geo_id"], unique=False)

    op.create_table(
        "marketing_angles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("inforeason_id", sa.Integer(), nullable=True),
        sa.Column("angle_text", sa.Text(), nullable=True),
        sa.Column("offer_connection", sa.Text(), nullable=True),
        sa.Column("target_pain", sa.Text(), nullable=True),
        sa.Column("creative_type", sa.String(length=64), nullable=True),
        sa.Column("priority", sa.String(length=8), nullable=True),
        sa.Column("created_at", sa.String(), nullable=True, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_marketing_angles_inforeason_id", "marketing_angles", ["inforeason_id"], unique=False)

    op.create_table(
        "headlines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("angle_id", sa.Integer(), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("format_type", sa.String(length=64), nullable=True),
        sa.Column("char_count", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_headlines_angle_id", "headlines", ["angle_id"], unique=False)

    op.create_table(
        "test_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("inforeason_id", sa.Integer(), nullable=True),
        sa.Column("conversion_rate", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_test_results_inforeason_id", "test_results", ["inforeason_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_test_results_inforeason_id", table_name="test_results")
    op.drop_table("test_results")

    op.drop_index("ix_headlines_angle_id", table_name="headlines")
    op.drop_table("headlines")

    op.drop_index("ix_marketing_angles_inforeason_id", table_name="marketing_angles")
    op.drop_table("marketing_angles")

    op.drop_index("ix_inforeasons_geo_id", table_name="inforeasons")
    op.drop_table("inforeasons")

    op.drop_index("ix_geos_code", table_name="geos")
    op.drop_table("geos")

