from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cfb4c18971a5'
down_revision = '93ad66758fd9'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.alter_column('companies', 'start_time', type_=sa.Time)
    op.alter_column('companies', 'end_time', type_=sa.Time)

def downgrade() -> None:
    op.alter_column('companies', 'start_time', type_=sa.DateTime)
    op.alter_column('companies', 'end_time', type_=sa.DateTime)
