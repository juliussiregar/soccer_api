from typing import List, Tuple
from app.models.role import Role
from app.models.user import User
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.schemas.user_mgt import UserCreate, UserUpdate, UserFilter, RegisterUpdate, PasswordUpdate

from app.utils.exception import (
    UnprocessableException,
    NotFoundException,
    InternalErrorException,
)
from app.utils.logger import logger

class UserService:
    def __init__(self) -> None:
        self.role_repo = RoleRepository()
        self.user_repo = UserRepository(user_repo=self, role_repo=self.role_repo)


    def list(self, filter: UserFilter) -> Tuple[List[User], int, int]:
        users = self.user_repo.get_all_filtered(filter)

        total_rows = self.user_repo.count_by_filter(filter)
        total_pages = (total_rows + filter.limit - 1) // filter.limit

        return users, total_rows, total_pages


    def create(self, payload: UserCreate) -> User:
        is_username_exists = self.user_repo.is_username_used(payload.username)
        if is_username_exists:
            raise UnprocessableException("username already used")


        if payload.email is not None:
            is_email_exists = self.user_repo.is_username_used(payload.email)
            if is_email_exists:
                raise UnprocessableException("email already used")

        if payload.role is None:
            payload.role = "HR"

        is_role_exists = self.role_repo.find_by_name(payload.role)
        if not is_role_exists:
            raise NotFoundException("role does not exists")

        try:
            user = self.user_repo.insert(payload)
        except Exception as err:
            err_msg = str(err)
            logger.error(err_msg)
            raise InternalErrorException(err_msg)

        return user

    def update(self, user_id: int, payload: UserUpdate) -> User:
        # Check if user exists
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        # Check username uniqueness if being updated
        if payload.username and payload.username != user.username:
            if self.user_repo.is_username_used(payload.username, except_id=user_id):
                raise UnprocessableException("Username already used")

        # Check email uniqueness if being updated
        if payload.email and payload.email != user.email:
            if self.user_repo.is_email_used(payload.email, except_id=user_id):
                raise UnprocessableException("Email already used")

        # Check role exists if being updated
        if payload.role:
            role = self.role_repo.find_by_name(payload.role)
            if not role:
                raise NotFoundException("Role does not exist")

        try:
            updated_user = self.user_repo.update(user_id, payload)
            if not updated_user:
                raise NotFoundException("Failed to update user")
            return updated_user
        except Exception as err:
            logger.error(f"Error updating user: {str(err)}")
            raise InternalErrorException(f"Error updating user: {str(err)}")

    def update_password(self, user_id: int, payload: PasswordUpdate) -> User:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        # Verify password confirmation
        if payload.new_password != payload.confirm_password:
            raise UnprocessableException("New password and confirmation do not match")

        # Check if new password is same as current
        if self.user_repo.verify_password(payload.new_password, user.password):
            raise UnprocessableException("New password must be different from current password")

        try:
            updated_user = self.user_repo.update_password(user_id, payload.new_password)
            if not updated_user:
                raise NotFoundException("Failed to update password")
            return updated_user
        except Exception as err:
            logger.error(f"Error updating password: {str(err)}")
            raise InternalErrorException(f"Error updating password: {str(err)}")

    def delete(self, user_id: int) -> bool:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        try:
            return self.user_repo.delete(user_id)
        except Exception as err:
            logger.error(f"Error deleting user: {str(err)}")
            raise InternalErrorException(f"Error deleting user: {str(err)}")

    def update_password(self, id: int, payload: RegisterUpdate) -> User:
        userdetil = self.user_repo.find_by_id(id)
        if not userdetil:
            raise UnprocessableException("username not found")

        pass_is_same = self.user_repo.verify_password(payload.password, userdetil.password)
        if pass_is_same:
            raise UnprocessableException("Find another password")

        try:
            user = self.user_repo.update_password(id, payload)
        except Exception as err:
            err_msg = str(err)
            logger.error(err_msg)
            raise InternalErrorException(err_msg)

        if user is None:
            raise NotFoundException("user does not exists")

        return user
    
    def update_user_password(self, id: int, payload: PasswordUpdate) -> User:
        userdetil = self.user_repo.find_by_id(id)
        if not userdetil:
            raise UnprocessableException("username not found")

        pass_is_same = self.user_repo.verify_password(payload.new_password, userdetil.password)
        if pass_is_same:
            raise UnprocessableException("Find another password")

        if payload.new_password != payload.confirm_password:
            raise UnprocessableException("password not same")   
         
        try:
            user = self.user_repo.update_user_password(id, payload)
        except Exception as err:
            err_msg = str(err)
            logger.error(err_msg)
            raise InternalErrorException(err_msg)

        if user is None:
            raise NotFoundException("user does not exists")

        return user