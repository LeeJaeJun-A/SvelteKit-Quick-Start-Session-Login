# import pytest
# from fastapi.testclient import TestClient
# from unittest.mock import patch, MagicMock
# from backend.auth.service.session_manager import SessionManager
# from backend.auth.service.user_manager import UserManager
# from backend.log.service.user_log_manager import UserLogManager
# from backend.main import app

# client = TestClient(app)

# mock_session_manager = MagicMock(spec=SessionManager)
# mock_user_manager = MagicMock(spec=UserManager)
# mock_user_log_manager = MagicMock(spec=UserLogManager)

# @pytest.fixture
# def mock_dependencies():
#     with patch("backend.auth.service.session_manager.SessionManager", return_value=mock_session_manager):
#         with patch("backend.auth.service.user_manager.UserManager", return_value=mock_user_manager):
#             with patch("backend.log.service.user_log_manager.UserLogManager", return_value=mock_user_log_manager):
#                 yield

# # 1. 올바른 로그인 요청 테스트
# def test_login_success(mock_dependencies):
#     mock_user_manager.login.return_value = MagicMock(role="admin")  # 가짜 유저 반환

#     response = client.post("/api/login", json={"user_id": "test_user", "password": "correct_password"})

#     assert response.status_code == 200
#     mock_user_log_manager.save_user_log.assert_called_with(
#         user_id="test_user",
#         action="User Login",
#         success=True,
#         error_code=None,
#         details="User logged in successfully.",
#     )
#     mock_session_manager.create_session.assert_called()

# # 2. 잘못된 로그인 요청 (비밀번호 틀림) 테스트
# def test_login_fail_invalid_credentials(mock_dependencies):
#     mock_user_manager.login.return_value = None  # 로그인 실패 가정

#     response = client.post("/api/login", json={"user_id": "test_user", "password": "wrong_password"})

#     assert response.status_code == 401
#     assert response.json()["detail"] == "잘못된 계정 정보입니다."
#     mock_user_log_manager.save_user_log.assert_called_with(
#         user_id="test_user",
#         action="User Login",
#         success=False,
#         error_code="INVALID_ACCOUNT",
#         details="Invalid account",
#     )

# # 3. 로그인 중 내부 오류 발생 테스트
# def test_login_internal_error(mock_dependencies):
#     mock_user_manager.login.side_effect = Exception("Database connection error")

#     response = client.post("/api/login", json={"user_id": "test_user", "password": "correct_password"})

#     assert response.status_code == 500
#     assert "로그인 중 내부 오류가 발생했습니다." in response.json()["detail"]
#     mock_user_log_manager.save_user_log.assert_called_with(
#         user_id="test_user",
#         action="User Login",
#         success=False,
#         error_code="INTERNAL_ERROR",
#         details="An error occurred during login: Database connection error",
#     )

# # 4. 로그아웃 성공 테스트
# def test_logout_success(mock_dependencies):
#     mock_session_manager.delete_session.return_value = None  # 세션 삭제 성공

#     response = client.post("/api/logout", cookies={"session_id": "test_session_id"})

#     assert response.status_code == 200
#     assert response.json() == {"message": "Logged out successfully"}
#     mock_session_manager.delete_session.assert_called_with("test_session_id")
#     mock_session_manager.delete_session_cookie.assert_called()

# # 5. 세션이 없는 상태에서 로그아웃 시도 테스트
# def test_logout_no_session(mock_dependencies):
#     response = client.post("/api/logout", cookies={})  # 세션 ID 없음

#     assert response.status_code == 200
#     assert response.json() == {"message": "No session ID found in cookies"}
#     mock_session_manager.delete_session_cookie.assert_called()

# # 6. 로그아웃 중 내부 오류 테스트
# def test_logout_internal_error(mock_dependencies):
#     mock_session_manager.delete_session.side_effect = Exception("Redis connection error")

#     response = client.post("/api/logout", cookies={"session_id": "test_session_id"})

#     assert response.status_code == 500
#     assert "An internal error occurred" in response.json()["detail"]
#     mock_session_manager.delete_session_cookie.assert_called()
