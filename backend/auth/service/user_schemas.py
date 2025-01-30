from pydantic import BaseModel
from datetime import datetime

class BaseRequest(BaseModel):
    user_id: str


class LoginRequest(BaseRequest):
    password: str


class UserCreateRequest(LoginRequest):
    role: str


class ChangePasswordRequest(BaseRequest):
    old_password: str
    new_password: str


class BaseResponse(BaseModel):
    user_id: str
    role: str


class UserInfoResponse(BaseResponse):
    created_at: datetime
    is_locked: bool


class LockUserResponse(BaseResponse):
    last_failed_login: datetime
