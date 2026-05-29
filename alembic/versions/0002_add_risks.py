from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_add_risks"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "risks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("inforeason_id", sa.Integer(), nullable=True),
        sa.Column("legal_risk", sa.Text(), nullable=True),
        sa.Column("ban_risk", sa.Text(), nullable=True),
        sa.Column("audience_negative", sa.Text(), nullable=True),
        sa.Column("expiration_date", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.String(),
            nullable=True,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["inforeason_id"], ["inforeasons.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_risks_inforeason_id",
        "risks",
        ["inforeason_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_risks_inforeason_id", table_name="risks")
    op.drop_table("risks")

