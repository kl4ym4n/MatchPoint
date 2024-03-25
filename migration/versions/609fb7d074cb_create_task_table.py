"""create task table

Revision ID: 609fb7d074cb
Revises: 
Create Date: 2024-03-19 18:58:40.296851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '609fb7d074cb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String()),
        sa.Column("description", sa.String()),
        sa.Column(
            "status",
            sa.Enum(
                "QUEUED",
                "RUNNING",
                "COMPLETED",
                "ERROR",
                name="taskstatus",
            ),
            nullable=False,
        ),
        sa.Column("url", sa.String()),
        sa.Column(
            "result", postgresql.JSONB(astext_type=sa.Text())
        ),
        sa.Column("is_deleted", sa.Boolean()),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("tasks")
