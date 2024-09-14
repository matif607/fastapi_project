"""add foreign key to post table

Revision ID: bb763c4237fc
Revises: 6e6e1f6b60ca
Create Date: 2024-09-14 00:31:59.366043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb763c4237fc'
down_revision: Union[str, None] = '6e6e1f6b60ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'posts',
        sa.Column('owner_id', sa.Integer(), nullable=False)
    )

    # Create the foreign key constraint between 'posts.owner_id' and 'users.id'
    op.create_foreign_key(
        'post_users_fk',
        source_table='posts',
        referent_table='users',
        local_cols=['owner_id'],
        remote_cols=['id'],
        ondelete='CASCADE'
    )
    pass


def downgrade() -> None:
    op.drop_constraint('post_users_fk')
    op.drop_column('posts', 'owner_id')
    pass
