from fastapi import APIRouter, HTTPException, Response, Request, Depends
from backend.auth.service.session_manager import SessionManager, verify_session
from pydantic import BaseModel
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_400_BAD_REQUEST,
)
from backend.log.service.user_log_manager import UserLogManager
from backend.auth.service.user_manager import UserManager

router = APIRouter()
session_manager = SessionManager()
user_manager = UserManager()
user_log_manager = UserLogManager()


class LoginRequest(BaseModel):
    user_id: str
    password: str


@router.post("/login")
def login_user(login_data: LoginRequest, response: Response):
    user_id = login_data.user_id
    password = login_data.password
    try:
        user = user_manager.login(user_id, password)

        if user:
            user_log_manager.save_user_log(
                user_id=user_id,
                action="로그인",
                success=True,
                error_code=None,
                details="사용자가 성공적으로 로그인했습니다.",
            )
            session_manager.create_session(
                response=response,
                user_id=user_id,
                role=user.role,
            )
        else:
            user_log_manager.save_user_log(
                user_id=user_id,
                action="사용자 로그인",
                success=False,
                error_code=401,
                details="잘못된 계정 정보로 로그인에 실패하였습니다.",
            )
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="잘못된 계정 정보입니다."
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        user_log_manager.save_user_log(
            user_id=user_id,
            action="User Login",
            success=False,
            error_code=500,
            details=f"로그인 중 오류가 발생하였습니다. {str(e)}",
        )
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 중 예기치 못한 오류가 발생했습니다. {str(e)}",
        )


@router.post("/logout")
def logout(request: Request, response: Response):
    try:
        session_id = request.cookies.get("session_id")
        if session_id:
            session_manager.delete_session(session_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그아웃 중 예기치 못한 오류가 발생했습니다.{str(e)}",
        )
    finally:
        session_manager.delete_session_cookie(
            response=response,
        )
