from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.auth.api import login, user_crud_management, user_lock_management, session
from backend.auth.service.session_manager import SessionManager
from backend.log.service.user_log_manager import UserLogManager
from backend.log.api import user_log
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
import logging
from backend.config import CORS_ALLOW_ORIGINS
import unittest.mock


class UvicornErrorFilter(logging.Filter):
    def filter(self, record):
        return "uvicorn.error" not in record.name


logger = logging.getLogger()
for handler in logger.handlers:
    handler.addFilter(UvicornErrorFilter())

session_manager = SessionManager()
user_log_manager = UserLogManager()
scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        scheduler.add_job(
            session_manager.delete_expired_sessions, "interval", minutes=5
        )
        scheduler.add_job(user_log_manager.delete_expired_logs, "interval", hours=24)
        scheduler.start()
        yield
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise
    finally:
        scheduler.shutdown()
        pass


app = FastAPI(lifespan=lifespan)

# app.dependency_overrides[SessionManager] = lambda: unittest.mock.MagicMock()

app.include_router(user_crud_management.router, tags=["user"], prefix="/api/user")
app.include_router(user_lock_management.router, tags=["user"], prefix="/api/user")
app.include_router(login.router, tags=["login"], prefix="/api")
app.include_router(session.router, tags=["session"], prefix="/api")
app.include_router(user_log.router, tags=["log"], prefix="/api/log")

origins = CORS_ALLOW_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello World!"}
