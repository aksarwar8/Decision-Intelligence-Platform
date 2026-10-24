"""add canonical daily demand table"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
revision: str = "2c84d8a4e1f0"
down_revision: Union[str, Sequence[str], None] = "b9d750d11557"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("daily_demand",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("product_id", sa.String(length=100), nullable=False),
        sa.Column("market", sa.String(length=100), nullable=False),
        sa.Column("demand", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", "product_id", "market", name="uq_daily_demand_series_date"))
    op.create_index("ix_daily_demand_date", "daily_demand", ["date"])
    op.create_index("ix_daily_demand_product_id", "daily_demand", ["product_id"])
    op.create_index("ix_daily_demand_market", "daily_demand", ["market"])

def downgrade() -> None:
    op.drop_index("ix_daily_demand_market", table_name="daily_demand")
    op.drop_index("ix_daily_demand_product_id", table_name="daily_demand")
    op.drop_index("ix_daily_demand_date", table_name="daily_demand")
    op.drop_table("daily_demand")
