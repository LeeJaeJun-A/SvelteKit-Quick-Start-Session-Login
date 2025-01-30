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
                action="User Login",
                success=True,
                error_code=None,
                details="User logged in successfully.",
            )
            session_manager.create_session(
                response=response,
                user_id=user_id,
                role=user.role,
            )
        else:
            user_log_manager.save_user_log(
                user_id=user_id,
                action="User Login",
                success=False,
                error_code="INVALID_ACCOUNT",
                details="Invalid account",
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
            error_code="INTERNAL_ERROR",
            details=f"An error occurred during login: {e}",
        )
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 중 내부 오류가 발생했습니다. {e}",
        )


@router.post("/logout")
def logout(request: Request, response: Response):
    try:
        session_id = request.cookies.get("session_id")

        if not session_id:
            return {"message": "No session ID found in cookies"}

        session_manager.delete_session(session_id)

        return {"message": "Logged out successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred {str(e)}",
        )
    finally:
        session_manager.delete_session_cookie(
            response=response,
        )
