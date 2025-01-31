from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08dfb80a2de8'
down_revision = 'd661bc6ebf6c'
branch_labels = None
depends_on = None

# Definisikan ENUM sebelum digunakan
application_type_enum = sa.Enum('APPLICATION', 'INVITATION', name='applicationtype')


def upgrade() -> None:
    # Pastikan ENUM dibuat sebelum digunakan
    application_type_enum.create(op.get_bind(), checkfirst=True)

    # Tambahkan kolom setelah ENUM dibuat
    op.add_column('team_applications', sa.Column('types', application_type_enum, nullable=False))
    op.drop_column('team_applications', 'message')


def downgrade() -> None:
    op.add_column('team_applications', sa.Column('message', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('team_applications', 'types')

    # Hapus ENUM jika sudah tidak digunakan
    application_type_enum.drop(op.get_bind(), checkfirst=True)
