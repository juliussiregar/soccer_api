"""Update Employee model to use position_id as foreign key

Revision ID: 042c4353e757
Revises: 49ad929f38fc
Create Date: 2024-11-13 15:22:07.698532

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '042c4353e757'
down_revision = '49ad929f38fc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('employees', sa.Column('position_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'employees', 'positions', ['position_id'], ['id'])
    op.drop_column('employees', 'position')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('employees', sa.Column('position', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'employees', type_='foreignkey')
    op.drop_column('employees', 'position_id')
    # ### end Alembic commands ###
