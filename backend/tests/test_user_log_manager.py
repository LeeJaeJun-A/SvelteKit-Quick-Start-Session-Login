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

    user_log_manager.save_user_log(
        "log_test_user", "LOGIN", True, None, "User logged in"
    )

    # `session.add()`와 `session.commit()`이 호출되었는지 확인
    mock_session.add.assert_called()
    mock_session.commit.assert_called()

    # `add()` 호출된 객체 확인
    new_log = mock_session.add.call_args[0][0]
    assert new_log.user_id == "log_test_user"
    assert new_log.action == "LOGIN"
    assert new_log.success is True
    assert new_log.error_code is None
    assert new_log.details == "User logged in"


# 2. 특정 유저 ID로 로그 조회 테스트
def test_get_user_logs_by_user_id(user_log_manager, mock_session):
    mock_session.reset_mock()

    # Mock 반환값 설정
    mock_session.query.return_value.filter.return_value.all.return_value = [
        UserLog(user_id="log_test_user2", action="LOGIN", success=True)
    ]
    mock_session.query.return_value.filter.return_value.count.return_value = 1

    # 함수 실행
    logs, total = user_log_manager.get_user_logs(user_id="log_test_user2")

    # 검증
    assert len(logs) == 1
    assert total == 1
    assert logs[0].user_id == "log_test_user2"
    assert logs[0].success is True
    mock_session.query.return_value.filter.assert_called()


# 3. 성공 여부 필터링 테스트
def test_get_user_logs_by_success(user_log_manager, mock_session):
    mock_session.reset_mock()

    mock_query = mock_session.query.return_value
    mock_filter1 = mock_query.filter.return_value
    mock_filter2 = mock_filter1.filter.return_value

    # 로그 데이터 반환 설정
    mock_filter2.all.return_value = [
        UserLog(user_id="error_log_user", action="LOGIN", success=False)
    ]
    mock_filter2.count.return_value = 1

    logs, total = user_log_manager.get_user_logs(
        user_id="error_log_user", success=False
    )

    assert len(logs) == 1, f"기대한 1개가 아닌 {len(logs)}개 반환됨"
    assert total == 1
    assert logs[0].success is False
    mock_session.query.return_value.filter.assert_called()


# 4. 날짜 범위로 로그 조회 테스트
def test_get_user_logs_by_date_range(user_log_manager, mock_session):
    mock_session.reset_mock()

    # Mock 체이닝을 명확히 설정하여 여러 개의 filter() 호출이 가능하도록 함
    mock_query = mock_session.query.return_value
    mock_filter = MagicMock()

    # 여러 번의 filter() 호출을 고려하여 같은 mock_filter를 반환하도록 설정
    mock_query.filter.return_value = mock_filter
    mock_filter.filter.return_value = mock_filter
    mock_filter.all.return_value = [
        UserLog(
            user_id="date_log_user",
            action="LOGIN",
            success=True,
            log_timestamp=datetime(2024, 1, 15),
        )
    ]
    mock_filter.count.return_value = 1

    logs, total = user_log_manager.get_user_logs(
        user_id="date_log_user", start_date="2024-01-01", end_date="2024-01-31"
    )

    # 검증
    assert len(logs) == 1, f"기대한 1개가 아닌 {len(logs)}개 반환됨"
    assert total == 1
    assert logs[0].user_id == "date_log_user"
    assert logs[0].success is True

    # Mock 검증
    mock_session.query.return_value.filter.assert_called()


def test_get_user_logs_pagination(user_log_manager, mock_session):
    mock_session.reset_mock()

    # Mock 체이닝을 명확히 설정하여 여러 개의 filter() 및 페이지네이션이 올바르게 동작하도록 설정
    mock_query = mock_session.query.return_value
    mock_filter = MagicMock()
    mock_pagination = MagicMock()

    # 여러 번의 filter() 호출을 고려하여 같은 mock_filter를 반환하도록 설정
    mock_query.filter.return_value = mock_filter
    mock_filter.filter.return_value = mock_filter

    # limit()과 offset()을 설정하여 올바르게 반환되도록 처리
    mock_filter.limit.return_value = mock_pagination
    mock_pagination.offset.return_value = mock_pagination

    # 로그 데이터 반환 설정
    mock_pagination.all.return_value = [
        UserLog(user_id="page_log_user", action="LOGIN", success=True)
    ]
    mock_filter.count.return_value = 1

    logs, total = user_log_manager.get_user_logs(
        user_id="page_log_user", page=1, per_page=10
    )

    # 검증
    assert len(logs) == 1, f"기대한 1개가 아닌 {len(logs)}개 반환됨"
    assert total == 1
    assert logs[0].user_id == "page_log_user"
    assert logs[0].success is True


# 6. 만료된 로그 삭제 테스트
def test_delete_expired_logs(user_log_manager, mock_session):
    mock_session.reset_mock()
    expired_log = UserLog(user_id="expired_log_user", action="LOGIN", success=True)

    mock_session.query.return_value.filter.return_value.all.return_value = [expired_log]

    user_log_manager.delete_expired_logs()

    mock_session.query.return_value.filter.assert_called()
    mock_session.delete.assert_called_with(expired_log)
    mock_session.commit.assert_called()
