from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.orm import declarative_base  
from datetime import datetime
from backend.database.base_database_manager import Base

BaseSession = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(String(255), primary_key=True, index=True)
    password = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    logins_before_rehash = Column(Integer, nullable=False, default=0)
    last_failed_login = Column(DateTime, nullable=True)
    failed_attempts = Column(Integer, nullable=False, default=0)
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)


class SessionModel(BaseSession):
    __tablename__ = "session"

    session_id = Column(String(255), primary_key=True)
    user_id = Column(String(255))
    role = Column(String(255))
    expires_at = Column(DateTime)
