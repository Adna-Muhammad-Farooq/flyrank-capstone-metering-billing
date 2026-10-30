"""add usage cost column

Revision ID: 0a962242ca9d
Revises: 849ef8ad1867
Create Date: 2026-10-30 18:11:46.605082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a962242ca9d'
down_revision: Union[str, Sequence[str], None] = '849ef8ad1867'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usage_events",
        sa.Column(
            "cost_micro_usd",
            sa.BigInteger(),
            nullable=False,
            server_default="0"
        )
    )


def downgrade() -> None:
    op.drop_column("usage_events", "cost_micro_usd")