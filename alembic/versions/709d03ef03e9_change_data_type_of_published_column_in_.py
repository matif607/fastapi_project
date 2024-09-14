"""change data type of published column in posts table

Revision ID: 709d03ef03e9
Revises: bb763c4237fc
Create Date: 2024-09-14 00:47:13.567334

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '709d03ef03e9'
down_revision: Union[str, None] = 'bb763c4237fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE posts
        ALTER COLUMN published DROP DEFAULT
        """
    )

    # Then, alter the column type with the USING clause for casting
    op.execute(
        """
        ALTER TABLE posts
        ALTER COLUMN published TYPE BOOLEAN
        USING published::boolean
        """
    )

    # Finally, set the new default value for the boolean column
    op.alter_column(
        'posts', 'published',
        nullable=False,
        server_default=sa.text('TRUE')  # Set default as a boolean
    )
    pass


def downgrade() -> None:
    op.drop_column('posts', 'published')
    pass
