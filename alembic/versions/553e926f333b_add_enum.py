from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '553e926f333b'
down_revision = '8ed2ba2a6252'
branch_labels = None
depends_on = None

# ENUM Baru untuk posisi pemain
position_player_enum = postgresql.ENUM(
    'GK', 'CB', 'LB', 'RB', 'LWB', 'RWB',
    'DMF', 'CM', 'AMF', 'LW', 'RW', 'LWF', 'RWF',
    'SS', 'ST', 'CF',
    name="positionplayerenum"
)

def upgrade() -> None:
    bind = op.get_bind()

    # 1️⃣ Buat ENUM baru tanpa menghapus ENUM lama
    position_player_enum.create(bind, checkfirst=True)

    # 2️⃣ Ubah kolom ke VARCHAR sementara untuk menghindari error cast
    op.alter_column('players', 'main_position', type_=sa.String())
    op.alter_column('players', 'second_position', type_=sa.String())
    op.alter_column('players', 'third_position', type_=sa.String(), existing_nullable=True)

    # 3️⃣ Ubah kembali ke ENUM baru dengan konversi eksplisit
    op.execute("ALTER TABLE players ALTER COLUMN main_position TYPE positionplayerenum USING main_position::text::positionplayerenum")
    op.execute("ALTER TABLE players ALTER COLUMN second_position TYPE positionplayerenum USING second_position::text::positionplayerenum")
    op.execute("ALTER TABLE players ALTER COLUMN third_position TYPE positionplayerenum USING third_position::text::positionplayerenum")

def downgrade() -> None:
    bind = op.get_bind()

    # 1️⃣ Ubah kolom ke VARCHAR sementara sebelum rollback ENUM
    op.alter_column('players', 'main_position', type_=sa.String())
    op.alter_column('players', 'second_position', type_=sa.String())
    op.alter_column('players', 'third_position', type_=sa.String(), existing_nullable=True)

    # 2️⃣ Hapus ENUM baru jika tidak digunakan
    position_player_enum.drop(bind, checkfirst=True)

    # 3️⃣ Kembalikan kolom ke STRING untuk menghindari error cast
    op.alter_column('players', 'main_position', type_=sa.String())
    op.alter_column('players', 'second_position', type_=sa.String())
    op.alter_column('players', 'third_position', type_=sa.String(), existing_nullable=True)
