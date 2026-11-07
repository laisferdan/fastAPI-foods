"""consumption_logs.quantidade_g and model-aligned indexes

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-11-07 10:05:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'consumption_logs',
        sa.Column('quantidade_g', sa.Float(), nullable=True),
    )
    op.drop_index(
        'ix_consumption_logs_consumed_at', table_name='consumption_logs'
    )
    op.create_index(
        'ix_consumption_user_date',
        'consumption_logs',
        ['user_id', 'consumed_at'],
    )
    op.create_index(
        'ix_consumption_user_meal',
        'consumption_logs',
        ['user_id', 'tipo_refeicao'],
    )


def downgrade() -> None:
    op.drop_index('ix_consumption_user_meal', table_name='consumption_logs')
    op.drop_index('ix_consumption_user_date', table_name='consumption_logs')
    op.create_index(
        'ix_consumption_logs_consumed_at',
        'consumption_logs',
        ['consumed_at'],
    )
    with op.batch_alter_table('consumption_logs') as batch_op:
        batch_op.drop_column('quantidade_g')
