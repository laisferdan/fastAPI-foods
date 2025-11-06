"""add user profiles, consumption logs, recommendation feedback

Revision ID: a1b2c3d4e5f6
Revises: eadc874612b9
Create Date: 2025-11-05 23:20:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "eadc874612b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # user_profiles
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("sexo", sa.String(), nullable=False),
        sa.Column("idade", sa.Integer(), nullable=False),
        sa.Column("peso_kg", sa.Float(), nullable=False),
        sa.Column("altura_cm", sa.Float(), nullable=False),
        sa.Column("nivel_atividade", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id"),
    )

    # consumption_logs
    op.create_table(
        "consumption_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("kcal", sa.Integer(), nullable=False),
        sa.Column("tipo_refeicao", sa.String(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_consumption_logs_consumed_at", "consumption_logs", ["consumed_at"]) 

    # recommendation_feedback
    op.create_table(
        "recommendation_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("feedback", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("recommendation_feedback")
    op.drop_index("ix_consumption_logs_consumed_at", table_name="consumption_logs")
    op.drop_table("consumption_logs")
    op.drop_table("user_profiles")
