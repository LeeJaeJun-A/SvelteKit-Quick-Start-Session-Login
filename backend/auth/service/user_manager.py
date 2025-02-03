from fastapi import HTTPException
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)
from backend.auth.database.models import User
from backend.database.base_database_manager import (
    BaseManager,
)
from backend.log.service.user_log_manager import UserLogManager
from backend.config import (
    DEFAULT_ROOT_ACCOUNT_ID,
    DEFAULT_ROOT_ACCOUNT_PASSWORD,
    DOCKER_MYSQL_DATABASE_URI,
    MYSQL_DATABASE_URI,
    IS_DOCKER,
    FAILURE_TRACKING_WINDOW_MINUTES,
    MAX_FAILURES,
    REHASH_COUNT_STANDARD,
    DEFAULT_ROOT_ACCOUNT_ID,
)
from backend.database.base_database_manager import Base
from datetime import datetime, timedelta
import hashlib
import os
import base64

user_log_manager = UserLogManager()


class UserManager(BaseManager):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UserManager, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        user_database_uri=MYSQL_DATABASE_URI,
        docker_user_database_uri=DOCKER_MYSQL_DATABASE_URI,
        is_docker=IS_DOCKER,
    ):
        if not hasattr(self, "initialized"):
            super().__init__(
                Base, user_database_uri, docker_user_database_uri, is_docker
            )
            self.create_user(
                DEFAULT_ROOT_ACCOUNT_ID, DEFAULT_ROOT_ACCOUNT_PASSWORD, "admin"
            )
            self.initialized = True

    def create_user(self, user_id: str, password: str, role: str = "user") -> bool:
        if role not in ["admin", "user"]:
            return False

        session = self.get_session()
        try:
            existing_user = session.query(User).filter(User.id == user_id).one_or_none()
            if existing_user:
                return False

            salt, hashed_password = self.hash_password(password)

            new_user = User(
                id=user_id,
                password=hashed_password,
                salt=salt,
                role=role,
                logins_before_rehash=0,
                failed_attempts=0,
                is_locked=False,
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def hash_password(self, plain_password: str) -> tuple[str, str]:
        salt = base64.b64encode(os.urandom(16)).decode("utf-8")
        sha256_hashed_password = hashlib.sha256(
            plain_password.encode("utf-8")
        ).hexdigest()
        salted_hash = f"{salt}{sha256_hashed_password}"
        final_hashed_password = hashlib.sha256(salted_hash.encode("utf-8")).hexdigest()
        return salt, final_hashed_password

    def verify_password(
        self, sha256_hashed_password: str, stored_password: str, salt: str
    ) -> bool:
        salted_hash = f"{salt}{sha256_hashed_password}"
        final_hashed_password = hashlib.sha256(salted_hash.encode("utf-8")).hexdigest()
        return final_hashed_password == stored_password

    def handle_failed_attempt(self, user):
        session = self.get_session()
        try:
            now = datetime.now()
            if user.last_failed_login and now - user.last_failed_login < timedelta(
                minutes=FAILURE_TRACKING_WINDOW_MINUTES
            ):
                user.failed_attempts += 1
                if MAX_FAILURES > 0 and user.failed_attempts >= MAX_FAILURES:
                    user_log_manager.save_user_log(
                        user_id=user.id,
                        action="Login Failed",
                        success=False,
                        error_code="ACCOUNT_LOCKED",
                        details=f"User account {user.id} locked due to too many failed login attempts.",
                    )
                    user.is_locked = True
                    session.commit()
                    raise HTTPException(
                        status_code=HTTP_403_FORBIDDEN,
                        detail="로그인 시도 실패 횟수가 초과되어 계정이 잠겼습니다. 관리자에게 문의해주세요.",
                    )
            else:
                user.failed_attempts = 1
            user.last_failed_login = now
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def login(
        self,
        user_id: str,
        password: str,
    ):
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).one_or_none()
            if not user:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="사용자를 찾을 수 없습니다.",
                )

            if user.is_locked:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="로그인 시도 실패 횟수가 초과되어 계정이 잠겼습니다. 관리자에게 문의해주세요.",
                )

            if (
                not self.verify_password(password, user.password, user.salt)
            ) and user_id != DEFAULT_ROOT_ACCOUNT_ID:
                self.handle_failed_attempt(user)
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="비밀번호가 잘못되었습니다.",
                )

            user.failed_attempts = 0
            user.logins_before_rehash += 1

            if user.logins_before_rehash >= REHASH_COUNT_STANDARD:
                user.salt, user.password = self.hash_password(password)
                user.logins_before_rehash = 0
            session.commit()
            session.refresh(user)
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_all_users(self):
        session = self.get_session()
        try:
            return session.query(User).all()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_paginated_users(
        self,
        page: int = 1,
        per_page: int = 10,
        is_locked: bool = False,
        user_id: str = None,
        role: str = None,
    ):
        session = self.get_session()
        try:
            query = session.query(User).order_by(User.id.asc())

            if is_locked:
                query = query.filter(User.is_locked == is_locked)

            if user_id is not None:
                query = query.filter(User.id.like(f"%{user_id}%"))

            if role is not None:
                query = query.filter(User.role == role)

            total = query.count()
            offset = (page - 1) * per_page
            users = query.offset(offset).limit(per_page).all()

            return users, total
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_user(self, user_id: str) -> bool:
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).one_or_none()
            if not user:
                return False

            session.delete(user)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_all_lock_users(self):
        session = self.get_session()
        try:
            return session.query(User).filter(User.is_locked == True).all()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def unlock_account(self, user_id: str) -> bool:
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).one_or_none()
            if not user:
                return False

            if not user.is_locked:
                return False

            user.is_locked = False
            user.failed_attempts = 0
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def lock_account(self, user_id: str) -> bool:
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).one_or_none()
            if not user:
                return False

            if user.is_locked:
                return False

            user.is_locked = True
            user.failed_attempts = 0
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).one_or_none()
            if not user:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="사용자를 찾을 수 없습니다.",
                )

            if not self.verify_password(old_password, user.password, user.salt):
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="현재 비밀번호가 올바르지 않습니다.",
                )

            if old_password == new_password:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="새 비밀번호는 현재 비밀번호와 같을 수 없습니다.",
                )

            salt, final_hashed_password = self.hash_password(new_password)
            user.password = final_hashed_password
            user.salt = salt
            user.logins_before_rehash = 0
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
