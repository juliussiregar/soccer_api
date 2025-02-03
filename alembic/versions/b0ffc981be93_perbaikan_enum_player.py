"""perbaikan enum player

Revision ID: b0ffc981be93
Revises: 553e926f333b
Create Date: 2025-02-03 14:18:55.735962

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text  

# ✅ Pastikan variabel ini ada di dalam file!
revision = 'b0ffc981be93'  # ID revisi migrasi ini
down_revision = '553e926f333b'  # ID revisi sebelumnya
branch_labels = None
depends_on = None

# ENUM lama yang akan dihapus
old_position_player_enum = postgresql.ENUM(
    "GOALKEEPER", "CENTER_BACK", "LEFT_BACK", "RIGHT_BACK", "LEFT_WING_BACK", "RIGHT_WING_BACK",
    "DEFENSIVE_MIDFIELDER", "CENTRAL_MIDFIELDER", "ATTACKING_MIDFIELDER", "LEFT_WINGER", "RIGHT_WINGER",
    "LEFT_WING_FORWARD", "RIGHT_WING_FORWARD", "SHADOW_STRIKER", "STRIKER", "SECOND_STRIKER", "COMPLETE_FORWARD",
    name="positionplayerenum"
)

# ENUM baru dengan singkatan
new_position_player_enum = postgresql.ENUM(
    "GK", "CB", "LB", "RB", "LWB", "RWB",
    "DMF", "CM", "AMF", "LW", "RW", "LWF", "RWF",
    "SS", "ST", "CF",
    name="positionplayerenum"
)

def upgrade() -> None:
    # Ubah ENUM hanya jika sudah ada di database
    bind = op.get_bind()
    existing_types = bind.execute(text("SELECT typname FROM pg_type WHERE typname = 'positionplayerenum'")).fetchall()
    
    if existing_types:
        # Rename ENUM lama untuk menghindari konflik
        op.execute("ALTER TYPE positionplayerenum RENAME TO positionplayerenum_old")
    
        # Buat ENUM baru
        new_position_player_enum.create(bind, checkfirst=True)

        # Ubah kolom untuk menggunakan ENUM baru
        op.alter_column('players', 'main_position', type_=new_position_player_enum, existing_nullable=False, postgresql_using="main_position::text::positionplayerenum")
        op.alter_column('players', 'second_position', type_=new_position_player_enum, existing_nullable=False, postgresql_using="second_position::text::positionplayerenum")
        op.alter_column('players', 'third_position', type_=new_position_player_enum, existing_nullable=True, postgresql_using="third_position::text::positionplayerenum")

        # Hapus ENUM lama
        op.execute("DROP TYPE positionplayerenum_old")

def downgrade() -> None:
    # Ubah kembali ENUM ke versi sebelumnya
    bind = op.get_bind()

    # Buat kembali ENUM lama
    old_position_player_enum.create(bind, checkfirst=True)

    # Ubah kolom kembali ke ENUM lama
    op.alter_column('players', 'main_position', type_=old_position_player_enum, existing_nullable=False, postgresql_using="main_position::text::positionplayerenum")
    op.alter_column('players', 'second_position', type_=old_position_player_enum, existing_nullable=False, postgresql_using="second_position::text::positionplayerenum")
    op.alter_column('players', 'third_position', type_=old_position_player_enum, existing_nullable=True, postgresql_using="third_position::text::positionplayerenum")

    # Hapus ENUM baru
    op.execute("DROP TYPE positionplayerenum")
