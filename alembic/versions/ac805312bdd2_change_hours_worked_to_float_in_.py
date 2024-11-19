"""Change hours_worked to Float in employee_daily_salary

Revision ID: ac805312bdd2
Revises: 49e49fee8efe
Create Date: 2024-11-18 13:01:35.223123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac805312bdd2'
down_revision = '49e49fee8efe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ubah tipe data
    op.alter_column(
        'employee_daily_salary',
        'hours_worked',
        existing_type=sa.Integer(),  # Tipe data sebelumnya
        type_=sa.Float(),             # Tipe data baru
        existing_nullable=False      # Sesuaikan dengan nullable/non-nullable
    )

def downgrade() -> None:
    # Kembalikan tipe data
    op.alter_column(
        'employee_daily_salary',
        'hours_worked',
        existing_type=sa.Float(),
        type_=sa.Integer(),
        existing_nullable=False
    )
