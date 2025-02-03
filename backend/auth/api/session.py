from fastapi import APIRouter, HTTPException, Request, Response, Depends
from backend.auth.service.session_manager import SessionManager, verify_session
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_400_BAD_REQUEST,
)
from backend.log.service.user_log_manager import UserLogManager
from backend.auth.service.user_manager import UserManager

router = APIRouter()
session_manager = SessionManager()
user_manager = UserManager()
user_log_manager = UserLogManager()


@router.get("/session")
def validate_session(
    _: None = Depends(verify_session),
):
    return {"message": "Session is valid"}


@router.get("/session/role")
def get_uers_info(request: Request):
    session_id = request.cookies.get("session_id")

    if not session_id:
        return {"role": ""}

    try:
        role = session_manager.get_role(session_id)

        if not role:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="유효하지 않은 세션입니다."
            )

        return {
            "role": role,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"권한 조회 중 예기치 못한 오류가 발생했습니다: {str(e)}",
        )


@router.get("/session/id")
def get_uers_info(request: Request):
    session_id = request.cookies.get("session_id")

    if not session_id:
        return {"id": ""}

    try:
        user_id = session_manager.get_user_id(session_id)

        if not user_id:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="유효하지 않은 세션입니다."
            )

        return {
            "user_id": user_id,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 ID 조회 중 예기치 못한 오류가 발생했습니다: {str(e)}",
        )
