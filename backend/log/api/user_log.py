from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from backend.log.service.user_log_manager import UserLogManager
from backend.auth.service.session_manager import verify_admin_session
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_400_BAD_REQUEST
)

router = APIRouter()
user_log_manager = UserLogManager()


@router.get("/user")
async def get_user_log(
    user_id: Optional[str] = Query(None, description="User ID"),
    success: Optional[bool] = Query(None, description="Filter by success status"),
    start_date: Optional[str] = Query(
        None, description="Start date for filtering logs"
    ),
    end_date: Optional[str] = Query(None, description="End date for filtering logs"),
    page: int = Query(1, ge=1, description="Page number (1-based index)"),
    per_page: int = Query(10, ge=1, le=100, description="Number of logs per page"),
    _: None = Depends(verify_admin_session),
):
    try:
        logs, total = user_log_manager.get_user_logs(
            user_id=user_id,
            success=success,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page,
        )

        return {"logs": logs, "total": total}
    except ValueError as e:
        raise HTTPException(
        status_code=HTTP_400_BAD_REQUEST,
        detail=f"{str(e)}",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 로그를 불러오는 중 예기치 않은 오류가 발생했습니다: {str(e)}",
        )
