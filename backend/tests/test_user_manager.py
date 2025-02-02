import pytest
from unittest.mock import MagicMock, patch
from backend.auth.service.user_manager import UserManager
from backend.auth.database.models import User
from fastapi import HTTPException
from datetime import datetime, timedelta

# Mock 객체 생성
mock_session = MagicMock()
mock_user = MagicMock(spec=User)

# UserManager 인스턴스 생성
user_manager = UserManager()

# 세션을 Mock으로 변경
user_manager.get_session = MagicMock(return_value=mock_session)

@pytest.fixture
def mock_db_session():
    """각 테스트 실행 전 세션 초기화"""
    mock_session.reset_mock()
    yield mock_session


# 1. 사용자 생성 테스트
def test_create_user_success(mock_db_session):
    mock_db_session.query().filter().one_or_none.return_value = None  # 사용자가 존재하지 않음
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()

    result = user_manager.create_user("test_user", "secure_password", "user")

    assert result is True
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called()


# 2. 기존 사용자가 있을 때 사용자 생성 실패 테스트
def test_create_user_fail_existing_user(mock_db_session):
    mock_db_session.query().filter().one_or_none.return_value = mock_user  # 이미 존재하는 사용자

    result = user_manager.create_user("test_user", "secure_password", "user")

    assert result is False


# 3. 로그인 성공 테스트
def test_login_success(mock_db_session):
    mock_user.is_locked = False
    mock_user.id = "test_user"
    mock_user.password = "hashed_password"
    mock_user.salt = "test_salt"
    mock_user.failed_attempts = 0
    mock_user.logins_before_rehash = 0

    mock_db_session.query().filter().one_or_none.return_value = mock_user
    user_manager.verify_password = MagicMock(return_value=True)

    result = user_manager.login("test_user", "correct_password")

    assert result == mock_user
    assert mock_user.failed_attempts == 0
    mock_db_session.commit.assert_called()


# 4. 로그인 실패 (비밀번호 틀림) 테스트
def test_login_fail_invalid_password():
    mock_user.is_locked = False
    mock_user.id = "test_user"
    mock_user.password = "hashed_password"
    mock_user.salt = "test_salt"

    mock_user.last_failed_login = datetime.now() - timedelta(minutes=3) # 5분이 아직 안지났음
    mock_user.failed_attempts = 2

    mock_session.query().filter().one_or_none.return_value = mock_user
    user_manager.verify_password = MagicMock(return_value=False)

    with pytest.raises(HTTPException) as excinfo:
        user_manager.login("test_user", "wrong_password")

    assert excinfo.value.status_code == 401
    assert "비밀번호가 잘못되었습니다." in str(excinfo.value.detail)
    assert mock_user.failed_attempts == 3 # 5분이 안지났으니까 2 + 1 되서 3번
    mock_session.commit.assert_called()


# 5. 계정 잠김 상태에서 로그인 테스트
def test_login_fail_locked_account(mock_db_session):
    mock_user.is_locked = True
    mock_user.id = "test_user"

    mock_db_session.query().filter().one_or_none.return_value = mock_user

    with pytest.raises(HTTPException) as excinfo:
        user_manager.login("test_user", "correct_password")

    assert excinfo.value.status_code == 403
    assert "계정이 잠겼습니다" in str(excinfo.value.detail)


# 6. 계정 잠금 기능 테스트
def test_lock_account(mock_db_session):
    mock_user.is_locked = False
    mock_db_session.query().filter().one_or_none.return_value = mock_user
    mock_db_session.commit = MagicMock()

    result = user_manager.lock_account("test_user")

    assert result is True
    assert mock_user.is_locked is True
    mock_db_session.commit.assert_called()


# 7. 계정 잠금 해제 테스트
def test_unlock_account(mock_db_session):
    mock_user.is_locked = True
    mock_db_session.query().filter().one_or_none.return_value = mock_user
    mock_db_session.commit = MagicMock()

    result = user_manager.unlock_account("test_user")

    assert result is True
    assert mock_user.is_locked is False
    mock_db_session.commit.assert_called()


# 8. 비밀번호 변경 성공 테스트
def test_change_password_success(mock_db_session):
    mock_user.id = "test_user"
    mock_user.password = "hashed_password"
    mock_user.salt = "test_salt"

    mock_db_session.query().filter().one_or_none.return_value = mock_user
    user_manager.verify_password = MagicMock(return_value=True)
    user_manager.hash_password = MagicMock(return_value=("new_salt", "new_hashed_password"))
    mock_db_session.commit = MagicMock()

    result = user_manager.change_password("test_user", "old_password", "new_password")

    assert result is True
    assert mock_user.password == "new_hashed_password"
    mock_db_session.commit.assert_called()


# 9. 비밀번호 변경 실패 (현재 비밀번호 틀림)
def test_change_password_fail_invalid_old_password(mock_db_session):
    mock_user.id = "test_user"
    mock_user.password = "hashed_password"
    mock_user.salt = "test_salt"

    mock_db_session.query().filter().one_or_none.return_value = mock_user
    user_manager.verify_password = MagicMock(return_value=False)

    with pytest.raises(HTTPException) as excinfo:
        user_manager.change_password("test_user", "wrong_old_password", "new_password")

    assert excinfo.value.status_code == 401
    assert "현재 비밀번호가 올바르지 않습니다." in str(excinfo.value.detail)


# 10. 동일한 새 비밀번호 입력 시 실패 테스트
def test_change_password_fail_same_password(mock_db_session):
    mock_user.id = "test_user"
    mock_user.password = "hashed_password"
    mock_user.salt = "test_salt"

    mock_db_session.query().filter().one_or_none.return_value = mock_user
    user_manager.verify_password = MagicMock(return_value=True)

    with pytest.raises(HTTPException) as excinfo:
        user_manager.change_password("test_user", "old_password", "old_password")

    assert excinfo.value.status_code == 401
    assert "새 비밀번호는 현재 비밀번호와 같을 수 없습니다." in str(excinfo.value.detail)