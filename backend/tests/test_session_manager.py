import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, Response, Request
from backend.auth.service.session_manager import SessionManager
from backend.auth.database.models import SessionModel
from datetime import datetime, timedelta

# Mock 객체 설정
mock_session = MagicMock()
mock_db_session = MagicMock(spec=SessionModel)

# SessionManager 인스턴스 생성 및 Mock 세션 설정
session_manager = SessionManager()
session_manager.get_session = MagicMock(return_value=mock_session)


@pytest.fixture
def mock_db():
    """각 테스트 실행 전 세션 초기화"""
    mock_session.reset_mock()
    mock_session.commit.side_effect = None
    yield mock_session


# 1. 세션 생성 테스트
def test_create_session_success(mock_db):
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    
    response = Response()
    session_id = session_manager.create_session(response, "test_user", "user")

    assert isinstance(session_id, str)
    assert response.headers["set-cookie"]  # 쿠키 설정 확인
    mock_db.add.assert_called()
    mock_db.commit.assert_called()


# 2. 세션 생성 중 예외 발생 시 롤백 테스트
def test_create_session_exception(mock_db):
    mock_db.commit.side_effect = Exception("Database error")
    
    response = Response()
    with pytest.raises(Exception) as excinfo:
        session_manager.create_session(response, "test_user", "user")

    assert "Database error" in str(excinfo.value)
    mock_db.rollback.assert_called()


# 3. 세션 유효성 검사 성공 테스트
def test_validate_session_success(mock_db):
    mock_db_session.session_id = "test_session_id"
    mock_db_session.user_id = "test_user"
    mock_db_session.role = "user"
    mock_db_session.expires_at = datetime.now() + timedelta(minutes=30)

    mock_db.query().filter().one_or_none.return_value = mock_db_session

    request = Request(scope={"type": "http", "headers": [(b"cookie", b"session_id=test_session_id")]})
    response = Response()

    session_manager.validate_session(request, response)

    mock_db.commit.assert_not_called()  # 세션 연장이 필요하지 않으면 commit이 호출되지 않음


# 4. 만료된 세션 검증 실패 테스트
def test_validate_session_expired(mock_db):
    mock_db_session.expires_at = datetime.now() - timedelta(minutes=1)  # 세션 만료

    mock_db.query().filter().one_or_none.return_value = mock_db_session

    request = Request(scope={"type": "http", "headers": [(b"cookie", b"session_id=test_session_id")]})
    response = Response()

    with pytest.raises(HTTPException) as excinfo:
        session_manager.validate_session(request, response)

    assert excinfo.value.status_code == 401
    assert "세션이 만료되었습니다." in str(excinfo.value.detail)
    mock_db.commit.assert_called()  # 만료된 세션 삭제 수행 확인


# 5. 존재하지 않는 세션 검증 실패 테스트
def test_validate_session_not_found(mock_db):
    mock_db.query().filter().one_or_none.return_value = None  # 세션 없음

    request = Request(scope={"type": "http", "headers": [(b"cookie", b"session_id=invalid_session_id")]})
    response = Response()

    with pytest.raises(HTTPException) as excinfo:
        session_manager.validate_session(request, response)

    assert excinfo.value.status_code == 401
    assert "세션이 유효하지 않습니다." in str(excinfo.value.detail)


# 6. 세션 삭제 테스트
def test_delete_session_success(mock_db):
    mock_db.query().filter().one_or_none.return_value = mock_db_session

    session_manager.delete_session("test_session_id")

    mock_db.delete.assert_called_with(mock_db_session)
    mock_db.commit.assert_called()


# 7. 세션 삭제 (세션 없음) 테스트
def test_delete_session_not_found(mock_db):
    mock_db.query().filter().one_or_none.return_value = None  # 세션 없음

    session_manager.delete_session("test_session_id")

    mock_db.delete.assert_not_called()  # 삭제할 세션이 없으면 delete가 호출되지 않음
    mock_db.commit.assert_not_called()


# 8. 만료된 세션 삭제 테스트
def test_delete_expired_sessions(mock_db):
    expired_sessions = [
        MagicMock(session_id="expired_1"),
        MagicMock(session_id="expired_2"),
    ]
    mock_db.query().filter().all.return_value = expired_sessions

    session_manager.delete_expired_sessions()

    assert mock_db.delete.call_count == len(expired_sessions)  # 만료된 세션 개수만큼 삭제 호출
    mock_db.commit.assert_called()


# 9. 어드민 권한 세션 검증 성공 테스트
def test_validate_admin_session_success(mock_db):
    mock_db_session.role = "admin"
    mock_db_session.expires_at = datetime.now() + timedelta(minutes=30)
    mock_db.query().filter().one_or_none.return_value = mock_db_session

    request = Request(scope={"type": "http", "headers": [(b"cookie", b"session_id=test_admin_session")]})
    response = Response()

    session_manager.validate_session(request, response, role="admin")


# 10. 어드민 세션 검증 실패 테스트 (일반 사용자 세션)
def test_validate_admin_session_fail(mock_db):
    mock_db_session.role = "user"  # 일반 사용자 세션
    mock_db_session.expires_at = datetime.now() + timedelta(minutes=30)

    mock_db.query().filter().one_or_none.return_value = mock_db_session

    request = Request(scope={"type": "http", "headers": [(b"cookie", b"session_id=test_user_session")]})
    response = Response()

    with pytest.raises(HTTPException) as excinfo:
        session_manager.validate_session(request, response, role="admin")

    assert excinfo.value.status_code == 403
    assert "권한이 없습니다." in str(excinfo.value.detail)


# 11. 모든 사용자 세션 삭제 테스트
def test_delete_session_user_id(mock_db):
    user_sessions = [MagicMock(session_id="session_1"), MagicMock(session_id="session_2")]

    mock_db.query().filter().all.return_value = user_sessions

    session_manager.delete_session_user_id("test_user")

    assert mock_db.delete.call_count == len(user_sessions)  # 사용자의 모든 세션 삭제
    mock_db.commit.assert_called()
