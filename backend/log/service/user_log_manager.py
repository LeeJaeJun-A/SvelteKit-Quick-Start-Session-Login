from backend.log.database.models import UserLog
from backend.database.base_database_manager import BaseManager
from backend.config import (
    DOCKER_MYSQL_DATABASE_URI,
    MYSQL_DATABASE_URI,
    IS_DOCKER,
    OPERATION_LOG_RETENTION_PERIOD,
)
from backend.database.base_database_manager import Base
from datetime import datetime, timedelta
import pytz


class UserLogManager(BaseManager):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UserLogManager, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        log_database_uri=MYSQL_DATABASE_URI,
        docker_log_database_uri=DOCKER_MYSQL_DATABASE_URI,
        is_docker=IS_DOCKER,
    ):
        if not hasattr(self, "initialized"):
            super().__init__(Base, log_database_uri, docker_log_database_uri, is_docker)
            self.initialized = True

    def save_user_log(self, user_id, action, success, error_code=None, details=None):
        session = self.get_session()
        try:
            new_log = UserLog(
                user_id=user_id,
                action=action,
                success=success,
                error_code=error_code,
                details=details,
            )
            session.add(new_log)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_user_logs(
        self,
        user_id=None,
        success=None,
        start_date=None,
        end_date=None,
        page=None,
        per_page=None,
    ):
        session = self.get_session()
        try:
            query = session.query(UserLog)

            if user_id is not None:
                query = query.filter(UserLog.user_id.like(f"%{user_id}%"))

            if success is not None:
                query = query.filter(UserLog.success == success)

            if start_date is not None:
                try:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                    query = query.filter(UserLog.log_timestamp >= start_date_obj)
                except ValueError:
                    raise ValueError("잘못된 시작 날짜 형식입니다. YYYY-MM-DD 형식을 사용하세요.")

            if end_date is not None:
                try:
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                    query = query.filter(UserLog.log_timestamp <= end_date_obj)
                except ValueError:
                    raise ValueError("잘못된 시작 날짜 형식입니다. YYYY-MM-DD 형식을 사용하세요.")

            query = query.order_by(UserLog.log_timestamp.desc())
            
            total = query.count()

            if page is not None and per_page is not None:
                query = query.limit(per_page).offset((page - 1) * per_page)
            
            logs = query.all()
            return logs, total
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_expired_logs(self):
        session = self.get_session()
        try:
            kst = pytz.timezone("Asia/Seoul")
            now = datetime.now(kst)
            standard_date = now - timedelta(days=OPERATION_LOG_RETENTION_PERIOD)
            old_logs = (
                session.query(UserLog)
                .filter(UserLog.log_timestamp <= standard_date)
                .all()
            )
            for old_log in old_logs:
                session.delete(old_log)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
