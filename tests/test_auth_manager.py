from auth_manager import AuthManager, AuthToken
from datetime import datetime, timedelta

def test_get_token():
    auth_manager = AuthManager()
    auth_manager.add_flow("oauth2", "token", datetime.now() + timedelta(hours=1))
    assert auth_manager.get_token("oauth2") == "token"

def test_renew_token():
    auth_manager = AuthManager()
    auth_manager.add_flow("oauth2", "token", datetime.now() - timedelta(hours=1))
    auth_manager.renew_token("oauth2")
    assert auth_manager.get_token("oauth2") != "token"

def test_add_flow():
    auth_manager = AuthManager()
    auth_manager.add_flow("jwt", "token", datetime.now() + timedelta(hours=1))
    assert auth_manager.get_token("jwt") == "token"

def test_remove_flow():
    auth_manager = AuthManager()
    auth_manager.add_flow("api_key", "token", datetime.now() + timedelta(hours=1))
    auth_manager.remove_flow("api_key")
    try:
        auth_manager.get_token("api_key")
        assert False
    except ValueError:
        assert True

def test_get_token_unsupported_flow():
    auth_manager = AuthManager()
    try:
        auth_manager.get_token("unsupported_flow")
        assert False
    except ValueError:
        assert True
