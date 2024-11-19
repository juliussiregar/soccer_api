"""Change hours_worked to Integer in employee_daily_salary

Revision ID: d9fdbcdd9f39
Revises: a56f16f915ad
Create Date: 2024-11-18 16:13:03.221722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9fdbcdd9f39'
down_revision = 'a56f16f915ad'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ubah tipe data
    op.alter_column(
        'employee_daily_salary',
        'hours_worked',
        existing_type=sa.Float(),  # Tipe data sebelumnya
        type_=sa.Integer(),             # Tipe data baru
        existing_nullable=False      # Sesuaikan dengan nullable/non-nullable
    )

def downgrade() -> None:
    # Kembalikan tipe data
    op.alter_column(
        'employee_daily_salary',
        'hours_worked',
        existing_type=sa.Integer(),
        type_=sa.Float(),
        existing_nullable=False
    )
