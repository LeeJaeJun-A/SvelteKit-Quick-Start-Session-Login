from datetime import datetime, timedelta
import uuid
from fastapi import HTTPException, Response, Request, Depends
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)
from backend.auth.database.models import SessionModel, BaseSession
from backend.database.base_database_manager import (
    BaseManager,
)
from backend.config import (
    DOCKER_SESSION_DATABASE_URI,
    SESSION_DATABASE_URI,
    IS_DOCKER,
    SESSION_EXPIRE_MINUTE,
)
from backend.log.service.user_log_manager import UserLogManager
from typing import Optional

user_log_manager = UserLogManager()


class SessionManager(BaseManager):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        session_database_uri=SESSION_DATABASE_URI,
        docker_session_database_uri=DOCKER_SESSION_DATABASE_URI,
        is_docker=IS_DOCKER,
    ):
        if not hasattr(self, "initialized"):
            super().__init__(
                BaseSession,
                session_database_uri,
                docker_session_database_uri,
                is_docker,
            )
            self.initialized = True

    def create_session(self, response: Response, user_id: str, role: str) -> str:
        session = self.get_session()
        try:
            session_id = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(minutes=SESSION_EXPIRE_MINUTE)
            db_session = SessionModel(
                session_id=session_id,
                user_id=user_id,
                role=role,
                expires_at=expires_at,
            )
            session.add(db_session)
            session.commit()
            self.set_session_cookie(response, session_id)
            return session_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def extend_session(self, db_session: SessionModel, response: Response):
        session = self.get_session()
        try:
            new_session_id = str(uuid.uuid4())
            new_expires_at = datetime.now() + timedelta(minutes=SESSION_EXPIRE_MINUTE)

            extended_session = SessionModel(
                session_id=new_session_id,
                user_id=db_session.user_id,
                role=db_session.role,
                expires_at=new_expires_at,
            )
            session.add(extended_session)
            session.commit()
            self.set_session_cookie(response, new_session_id)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # need to change samesite and secure setting
    def set_session_cookie(
        self,
        response: Response,
        session_id: str,
        max_age: int = SESSION_EXPIRE_MINUTE * 60,
    ):
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=max_age,
        )

    def delete_session_cookie(
        self,
        response: Response,
    ):
        response.set_cookie(
            key="session_id",
            value="",
            httponly=True,
            max_age=0,
            expires=0,
            path="/",
            samesite="Lax",
        )

    def validate_session(self, request: Request, response: Response, role=None):
        session = self.get_session()
        try:
            session_id = request.cookies.get("session_id")
            if not session_id:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="세션 ID를 찾을 수 없습니다.",
                )

            db_session = (
                session.query(SessionModel)
                .filter(SessionModel.session_id == session_id)
                .one_or_none()
            )

            if not db_session:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="세션이 유효하지 않습니다.",
                )

            now = datetime.now().replace(microsecond=0)

            if db_session.expires_at < now:
                self.delete_session(session_id)
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="세션이 만료되었습니다.",
                )

            if role and db_session.role != role:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="권한이 없습니다.",
                )

            remaining_time = (db_session.expires_at - now).total_seconds() / 60
            if remaining_time <= 30:
                self.extend_session(session, db_session, response)
        except Exception as e:
            raise e
        finally:
            session.close()

    def get_user_id(self, session_id: str) -> str:
        session = self.get_session()
        try:
            db_session = (
                session.query(SessionModel)
                .filter(SessionModel.session_id == session_id)
                .one_or_none()
            )

            if not db_session:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="세션이 유효하지 않습니다.",
                )

            if db_session.expires_at < datetime.now():
                self.delete_session(session_id)
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="세션이 만료되었습니다.",
                )

            return db_session.user_id
        except Exception as e:
            raise e
        finally:
            session.close()
            
    def get_role(self, session_id: str) -> str:
        session = self.get_session()
        try:
            db_session = (
                session.query(SessionModel)
                .filter(SessionModel.session_id == session_id)
                .one_or_none()
            )

            if not db_session:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="세션이 유효하지 않습니다.",
                )

            if db_session.expires_at < datetime.now():
                self.delete_session(session_id)
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="세션이 만료되었습니다.",
                )

            return db_session.role
        except Exception as e:
            raise e
        finally:
            session.close()

    def delete_session(self, session_id: str):
        session = self.get_session()
        try:
            db_session = (
                session.query(SessionModel)
                .filter(SessionModel.session_id == session_id)
                .one_or_none()
            )

            if db_session:
                session.delete(db_session)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_session_user_id(self, user_id: str):
        session = self.get_session()
        try:
            db_sessions = (
                session.query(SessionModel)
                .filter(SessionModel.user_id == user_id)
                .all()
            )
            for db_session in db_sessions:
                session.delete(db_session)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_expired_sessions(self):
        session = self.get_session()
        try:
            now = datetime.now()
            expired_sessions = (
                session.query(SessionModel).filter(SessionModel.expires_at < now).all()
            )

            for db_session in expired_sessions:
                session.delete(db_session)

            session.commit()
            print(
                f"\033[32m[SessionManager] Deleted {len(expired_sessions)} expired sessions.\033[0m"
            )
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


session_manager_instance = SessionManager()


def verify_session(
    request: Request,
    response: Response,
    session_manager: SessionManager = Depends(lambda: session_manager_instance),
):
    """Dependency to validate session and ensure it's valid."""
    session_manager.validate_session(request, response)


def verify_admin_session(
    request: Request,
    response: Response,
    session_manager: SessionManager = Depends(lambda: session_manager_instance),
):
    """Dependency to validate session for admin users only."""
    session_manager.validate_session(request, response, role="admin")