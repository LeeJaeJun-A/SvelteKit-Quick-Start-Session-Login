from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from backend.auth.service.user_manager import UserManager
from backend.auth.service.session_manager import SessionManager, verify_admin_session
from backend.log.service.user_log_manager import UserLogManager
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_400_BAD_REQUEST,
)
from backend.auth.service.user_schemas import LockUserResponse, BaseRequest
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
            detail="Failed to retrieve locked users",
        )


@router.get("/locked/count")
def get_lock_user_count(_: None = Depends(verify_admin_session)):
    try:
        locked_users = user_manager.get_all_lock_users()
        return len(locked_users)
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to count locked users.",
        )


@router.post("/unlock")
def unlock_user(
    data: BaseRequest, _: None = Depends(verify_admin_session)
):
    try:
        success = user_manager.unlock_account(data.user_id)
        if success:
            user_log_manager.save_user_log(
                user_id=data.user_id,
                action="Unlock User",
                success=True,
                error_code=None,
                details=f"User account {data.user_id} unlocked successfully.",
            )
            return {"message": "사용자 계정이 성공적으로 활성화되었습니다."}
        else:
            user_log_manager.save_user_log(
                user_id=data.user_id,
                action="Unlock User",
                success=False,
                error_code="USER_ACCOUNT_NOT_LOCKED",
                details=f"Failed to unlock user account {data.user_id} or account is not locked.",
            )
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="사용자 계정 활성화에 실패했거나 계정이 잠금 상태가 아닙니다.",
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        user_log_manager.save_user_log(
            user_id=data.user_id,
            action="Unlock User",
            success=False,
            error_code="INTERNAL_ERROR",
            details=f"Failed to unlock user account {data.user_id}. Error: {str(e)}",
        )
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 계정 활성화 실패",
        )


@router.post("/lock")
def lock_user(
    data: BaseRequest, _: None = Depends(verify_admin_session)
):
    try:
        if data.user_id == DEFAULT_ROOT_ACCOUNT_ID:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="기본 루트 계정은 비활성화할 수 없습니다.",
            )

        success = user_manager.lock_account(data.user_id)
        if success:
            session_manager.delete_session_user_id(data.user_id)
            user_log_manager.save_user_log(
                user_id=data.user_id,
                action="Lock User",
                success=True,
                error_code=None,
                details=f"User account {data.user_id} locked successfully.",
            )
            return {"message": "사용자 계정이 성공적으로 비활성화되었습니다."}
        else:
            user_log_manager.save_user_log(
                user_id=data.user_id,
                action="Lock User",
                success=False,
                error_code="USER_ACCOUNT_ALREADY_LOCKED",
                details=f"Failed to lock user account {data.user_id} or account is already locked.",
            )
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="사용자 계정 비활성화에 실패했거나 계정이 이미 잠금 상태입니다.",
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        user_log_manager.save_user_log(
            user_id=data.user_id,
            action="Lock User",
            success=False,
            error_code="INTERNAL_ERROR",
            details=f"Failed to lock user account {data.user_id}. Error: {str(e)}",
        )
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 계정 비활성화 실패",
        )
