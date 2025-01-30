from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)
from datetime import datetime
from backend.database.base_database_manager import Base
import pytz


def get_kst_now():
    kst = pytz.timezone("Asia/Seoul")
    return datetime.now(kst)


class UserLog(Base):
    __tablename__ = "user_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)
    action = Column(String(50), nullable=False)  # 어떤 작업인지
    success = Column(String(5), nullable=False)  # "True" or "False"
    error_code = Column(String(20), nullable=True)  # 에러 코드 (예: 404, 500)
    details = Column(Text, nullable=True)  # 추가 설명
    log_timestamp = Column(DateTime, default=get_kst_now)
