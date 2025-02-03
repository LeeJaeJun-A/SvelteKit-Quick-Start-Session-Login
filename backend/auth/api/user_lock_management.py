from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from backend.auth.service.user_manager import UserManager
from backend.auth.service.session_manager import SessionManager, verify_admin_session
from backend.log.service.user_log_manager import UserLogManager
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_400_BAD_REQUEST,
)
from backend.auth.service.user_schemas import LockUserResponse, AdminRequest
from backend.config import (
    DEFAULT_ROOT_ACCOUNT_ID,
)

user_log_manager = UserLogManager()
router = APIRouter()
session_manager = SessionManager()
user_manager = UserManager()


@router.get("/locked")
def get_lock_user_list(_: None = Depends(verify_admin_session)):
    try:
        locked_users = user_manager.get_all_lock_users()
        return [
            LockUserResponse(
                user_id=locked_user.id,
                role=locked_user.role,
                last_failed_login=locked_user.last_failed_login,
            )
            for locked_user in locked_users
        ]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예기치 못한 오류가 발생하였습니다. {str(e)}",
        )


@router.get("/locked/count")
def get_lock_user_count(_: None = Depends(verify_admin_session)):
    try:
        locked_users = user_manager.get_all_lock_users()
        return len(locked_users)
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예기치 못한 오류가 발생하였습니다. {str(e)}",
        )


@router.post("/unlock")
def unlock_user(data: AdminRequest, _: None = Depends(verify_admin_session)):
    try:
        user_manager.unlock_account(data.user_id)
        user_log_manager.save_user_log(
            user_id=data.request_user,
            action="사용자 계정 활성화",
            success=True,
            error_code=None,
            details=f"사용자 계정 `{data.user_id}` 성공적으로 활성화되었습니다.",
        )
    except HTTPException as e:
        user_log_manager.save_user_log(
            user_id=data.request_user,
            action="사용자 계정 활성화",
            success=False,
            error_code=e.status_code,
            details=f"사용자 계정 `{data.user_id}` 활성화에 실패하였습니다. {str(e)}",
        )
        raise e
    except Exception as e:
        user_log_manager.save_user_log(
            user_id=data.request_user,
            action="사용자 계정 활성화",
            success=False,
            error_code=500,
            details=f"사용자 계정 `{data.user_id}` 활성화 중 예기치 못한 오류가 발생하였습니다. {str(e)}",
        )
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 계정 활성화 실패",
        )


@router.post("/lock")
def lock_user(data: AdminRequest, _: None = Depends(verify_admin_session)):
    try:
        if data.user_id == DEFAULT_ROOT_ACCOUNT_ID:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="기본 관리자 계정은 비활성화할 수 없습니다.",
            )

        user_manager.lock_account(data.user_id)
        session_manager.delete_session_user_id(data.user_id)
        user_log_manager.save_user_log(
            user_id=data.request_user,
            action="사용자 계정 비활성화",
            success=True,
            error_code=None,
            details=f"사용자 계정 `{data.user_id}` 성공적으로 비활성화되었습니다.",
        )
    except HTTPException as e:
        user_log_manager.save_user_log(
            user_id=data.request_user,
            action="사용자 계정 활성화",
            success=False,
            error_code=e.status_code,
            details=f"사용자 계정 `{data.user_id}` 비활성화에 실패하였습니다. {str(e)}",
        )
        raise e
    except Exception as e:
        user_log_manager.save_user_log(
            user_id=data.request_user,
            action="사용자 계정 비활성화",
            success=False,
            error_code=500,
            details=f"사용자 계정 `{data.user_id}` 비활성화 중 예기치 못한 오류가 발생하였습니다. {str(e)}",
        )
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 계정 비활성화 실패",
        )
