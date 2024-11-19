from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '49e49fee8efe'
down_revision = '8fa3afcfc0a5'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Ubah tipe data kolom work_date menjadi DATE
    op.alter_column(
        'employee_daily_salary',
        'work_date',
        existing_type=sa.DateTime(),  # Tipe data sebelumnya
        type_=sa.Date(),             # Tipe data baru
        existing_nullable=False      # Sesuaikan dengan nullable/non-nullable
    )

def downgrade() -> None:
    # Kembalikan tipe data kolom work_date menjadi DateTime
    op.alter_column(
        'employee_daily_salary',
        'work_date',
        existing_type=sa.Date(),
        type_=sa.DateTime(),
        existing_nullable=False
    )
