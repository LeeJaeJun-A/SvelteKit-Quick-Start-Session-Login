import pytest
from unittest.mock import MagicMock, patch
from backend.log.service.user_log_manager import UserLogManager
from backend.log.database.models import UserLog
from datetime import datetime


@pytest.fixture
def mock_session():
    """Mock된 데이터베이스 세션 생성"""
    return MagicMock()


@pytest.fixture
def user_log_manager(mock_session):
    """UserLogManager 인스턴스 생성 및 get_session 메서드 Mocking"""
    user_log_manager = UserLogManager()
    user_log_manager.get_session = MagicMock(return_value=mock_session)
    return user_log_manager


# 1. 로그 저장 테스트
def test_save_user_log(user_log_manager, mock_session):
    mock_session.reset_mock()

    user_log_manager.save_user_log("log_test_user", "LOGIN", True, None, "User logged in")

    # `session.add()`와 `session.commit()`이 호출되었는지 확인
    mock_session.add.assert_called()
    mock_session.commit.assert_called()

    # `add()` 호출된 객체 확인
    new_log = mock_session.add.call_args[0][0]
    assert new_log.user_id == "log_test_user"
    assert new_log.action == "LOGIN"
    assert new_log.success == "True"  # 문자열 변환 확인
    assert new_log.error_code is None
    assert new_log.details == "User logged in"


# 2. 특정 유저 ID로 로그 조회 테스트
def test_get_user_logs_by_user_id(user_log_manager, mock_session):
    mock_session.reset_mock()

    # Mock 반환값 설정
    mock_session.query.return_value.filter.return_value.all.return_value = [
        UserLog(user_id="log_test_user2", action="LOGIN", success="True")
    ]
    mock_session.query.return_value.filter.return_value.count.return_value = 1

    # 함수 실행
    logs, total = user_log_manager.get_user_logs(user_id="log_test_user2")

    # 검증
    assert len(logs) == 1
    assert total == 1
    assert logs[0].user_id == "log_test_user2"
    mock_session.query.return_value.filter.assert_called()


# 3. 에러 로그 필터링 테스트
def test_get_user_logs_error_only(user_log_manager, mock_session):
    mock_session.reset_mock()

    # 🔹 filter()가 여러 번 호출될 경우에도 같은 객체를 반환하도록 설정
    mock_query = mock_session.query.return_value
    mock_filter = MagicMock()
    mock_filter.all.return_value = [
        UserLog(user_id="error_log_user", action="LOGIN", success=False)
    ]
    mock_filter.count.return_value = 1
    mock_query.filter.side_effect = lambda *args, **kwargs: mock_filter  # 모든 filter() 호출이 동일한 Mock 반환

    logs, total = user_log_manager.get_user_logs(user_id="error_log_user", is_error="True")

    assert len(logs) == 1, f"기대한 1개가 아닌 {len(logs)}개 반환됨"
    assert total == 1
    assert logs[0].success == "False"
    mock_session.query.return_value.filter.assert_called()


# 4. 날짜 범위로 로그 조회 테스트
def test_get_user_logs_by_date_range(user_log_manager, mock_session):
    mock_session.reset_mock()
    mock_session.query.return_value.filter.return_value.all.return_value = [
        UserLog(
            user_id="date_log_user",
            action="LOGIN",
            success="True",
            log_timestamp=datetime(2024, 1, 15),
        )
    ]
    mock_session.query.return_value.filter.return_value.count.return_value = 1

    logs, total = user_log_manager.get_user_logs(
        user_id="date_log_user", start_date="2024-01-01", end_date="2024-01-31"
    )

    assert len(logs) == 1
    assert total == 1
    assert logs[0].user_id == "date_log_user"
    mock_session.query.return_value.filter.assert_called()


# 5. 페이지네이션 테스트
def test_get_user_logs_pagination(user_log_manager, mock_session):
    mock_session.reset_mock()
    mock_session.query.return_value.limit.return_value.offset.return_value.all.return_value = [
        UserLog(user_id="page_log_user", action="LOGIN", success="True")
    ]
    mock_session.query.return_value.count.return_value = 1

    logs, total = user_log_manager.get_user_logs(user_id="page_log_user", page=1, per_page=10)

    assert len(logs) == 1
    assert total == 1
    assert logs[0].user_id == "page_log_user"
    mock_session.query.return_value.limit.assert_called()
    mock_session.query.return_value.offset.assert_called()


# 6. 만료된 로그 삭제 테스트
def test_delete_expired_logs(user_log_manager, mock_session):
    mock_session.reset_mock()
    expired_log = UserLog(user_id="expired_log_user", action="LOGIN", success="True")

    mock_session.query.return_value.filter.return_value.all.return_value = [expired_log]

    user_log_manager.delete_expired_logs()

    mock_session.query.return_value.filter.assert_called()
    mock_session.delete.assert_called_with(expired_log)
    mock_session.commit.assert_called()
