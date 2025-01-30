from fastapi import APIRouter, HTTPException, Query, Depends
from backend.auth.service.user_manager import UserManager
from backend.auth.service.session_manager import verify_admin_session
from backend.log.service.user_log_manager import UserLogManager
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_400_BAD_REQUEST,
)
from backend.config import (
    DEFAULT_ROOT_ACCOUNT_ID,
)
from backend.auth.service.user_schemas import (
    UserCreateRequest,
    UserInfoResponse,
    ChangePasswordRequest,
    BaseRequest,
)

router = APIRouter()
user_manager = UserManager()
user_log_manager = UserLogManager()


@router.post("/")
def create_user(
    data: UserCreateRequest,
    _: None = Depends(verify_admin_session),
):
    try:
        success = user_manager.create_user(data.user_id, data.password, data.role)

        if success:
            user_log_manager.save_user_log(
                user_id=data.user_id,
                action="Create User",
                success=True,
                error_code=None,
                details=f"User {data.user_id} created with role {data.role}.",
            )
            return {"message": "User created successfully"}
        else:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

    except HTTPException as e:
        raise e

    except Exception as e:
        user_log_manager.save_user_log(
            user_id=data.user_id,
            action="Create User",
            success=False,
            error_code="INTERNAL_ERROR",
            details=f"An unexpected error occurred while creating user {data.user_id}: {str(e)}",
        )
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get("/")
def get_user_list(
    page: int = Query(1, ge=1, description="Page number (1-based index)"),
    per_page: int = Query(10, ge=1, le=100, description="Number of users per page"),
    is_locked: bool = Query(False, description="Filter by lock status"),
    user_id: str = Query(None, description="Filter by user ID (optional)"),
    role: str = Query(None, description="Filter by user role (optional)"),
    _: None = Depends(verify_admin_session),
):
    try:
        users, total = user_manager.get_paginated_users(
            page=page,
            per_page=per_page,
            is_locked=is_locked,
            user_id=user_id,
            role=role,
        )

        return {
            "users": [
                UserInfoResponse(
                    user_id=user.id,
                    role=user.role,
                    created_at=user.created_at,
                    is_locked=user.is_locked,
                )
                for user in users
            ],
            "total": total,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user list. {str(e)}",
        )


@router.post("/change/password")
def change_password(
    data: ChangePasswordRequest,
    _: None = Depends(verify_admin_session),
):
    try:
        success = user_manager.change_password(
            user_id=data.user_id,
            old_password=data.old_password,
            new_password=data.new_password,
        )

        if success:
            user_log_manager.save_user_log(
                user_id=data.user_id,
                action="Change Password",
                success=True,
                error_code=None,
                details="Password changed successfully.",
            )
            return {"message": "비밀번호가 성공적으로 변경되었습니다."}
        else:
            user_log_manager.save_user_log(
                user_id=data.user_id,
                action="Change Password",
                success=False,
                error_code="PASSWORD_CHANGE_FAILED",
                details="Password change failed.",
            )
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="비밀번호 변경에 실패하였습니다.",
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        user_log_manager.save_user_log(
            user_id=data.user_id,
            action="Change Password",
            success=False,
            error_code="INTERNAL_ERROR",
            details=f"Error occurred during password change for {data.user_id}: {str(e)}",
        )
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예기치 않은 오류가 발생하였습니다: {str(e)}",
        )


@router.delete("/")
def delete_user(
    data: BaseRequest, _: None = Depends(verify_admin_session)
):
    try:
        if data.user_id == DEFAULT_ROOT_ACCOUNT_ID:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="기본 루트 계정은 삭제할 수 없습니다.",
            )

        success = user_manager.delete_user(data.user_id)
        if success:
            user_log_manager.save_user_log(
                user_id=data.user_id,
                action="Delete User",
                success=True,
                error_code=None,
                details=f"User {data.user_id} deleted successfully.",
            )
            return {"message": "사용자가 성공적으로 삭제되었습니다."}
        else:
            user_log_manager.save_user_log(
                user_id=data.user_id,
                action="Delete User",
                success=False,
                error_code="USER_DELETE_FAILED",
                details=f"Failed to delete user {data.user_id}.",
            )
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="사용자 삭제에 실패했습니다.",
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        user_log_manager.save_user_log(
            user_id=data.user_id,
            action="Delete User",
            success=False,
            error_code="INTERNAL_ERROR",
            details=f"Error occurred while deleting user {data.user_id}: {str(e)}",
        )
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 삭제 중 오류가 발생했습니다.",
        )
