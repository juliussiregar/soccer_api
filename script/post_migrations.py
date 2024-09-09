import logging
from app.models.configuration import Category

from app.models.user import User
from app.models.role import Role, user_role_association
from passlib.context import CryptContext
from app.core.database import get_session

USER_ROLES = ["superadmin", "rekan", "peserta-rekan", "peserta"]
DEFAULT_USERNAME = "superSOLID"
DEFAULT_FULLNAME = "Super Admin Solid Pace"
DEFAULT_PASSWORD = "siPalingSolid"



bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)

def update_roles() -> None:
    logger = logging.getLogger("alembic.post_migration.roles")
    logger.info("creating/updating roles")
    with get_session() as db:
        all_role = []
        for role in USER_ROLES:
            all_role.append(Role(name=role))
        db.query(Role).filter(Role.name.notin_(USER_ROLES)).delete(synchronize_session=False)
        for role in all_role:
            role_db = db.query(Role).filter(Role.name == role.name).one_or_none()
            if not role_db:
                db.add(role)
                db.commit()
                db.refresh(role)


def create_admin() -> None:
    logger = logging.getLogger("alembic.post_migration.users")
    logger.info("creating default users")
    with get_session() as db:

        admin_user: User = (
            db.query(User).filter(User.username == DEFAULT_USERNAME).one_or_none()
        )
        if not admin_user:
            hash_password = get_password_hash(DEFAULT_PASSWORD)
            admin_user = User(
                username=DEFAULT_USERNAME,
                password=hash_password,
                full_name=DEFAULT_FULLNAME
            )
            db.add(admin_user)
            db.commit()
        else:
            hash_password = get_password_hash(DEFAULT_PASSWORD)
            admin_user.password = hash_password
        db.flush()
        logger.info("creating/updating user admin roles")
        admin_user_role = (
            db.query(user_role_association)
            .filter(user_role_association.c.role_id == 1)
            .filter(user_role_association.c.user_id == admin_user.id)
            .one_or_none()
        )
        if not admin_user_role:
            insert_user_role = user_role_association.insert().values(
                user_id=admin_user.id, role_id=1
            )
            db.execute(insert_user_role)
            db.commit()

def create_category () -> None:
        category = Category ()
        category.category = "Standard"
        category.name = "Lunch"
        category.value = "Lunch"

        with get_session () as db:
            db.add (category)
            db.flush ()
            db.commit ()
            db.refresh (category)
        
        category = Category ()
        category.category = "Standard"
        category.name = "Snack"
        category.value = "Snack"

        with get_session () as db:
            db.add (category)
            db.flush ()
            db.commit ()
            db.refresh (category)
        
        category = Category ()
        category.category = "Standard"
        category.name = "Dinner"
        category.value = "Dinner"

        with get_session () as db:
            db.add (category)
            db.flush ()
            db.commit ()
            db.refresh (category)


def post_migration() -> None:
    logger = logging.getLogger("alembic.post_migration")
    logger.info("doing post migration")
    update_roles()
    # create_category()
    create_admin()
    logger.info("post migration completed")

post_migration()
print("selesai")