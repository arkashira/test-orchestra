from auth_manager import AuthManager, AuthCredentials

def test_load_credentials():
    manager = AuthManager()
    assert manager.load_credentials() == {}

def test_save_credentials():
    manager = AuthManager()
    manager.add_credentials('test', 'username', 'password')
    assert manager.get_credentials('test').username == 'username'
    assert manager.get_credentials('test').password == 'password'

def test_authenticate():
    manager = AuthManager()
    manager.add_credentials('test', 'username', 'password')
    assert manager.authenticate('test', 'username', 'password') == True
    assert manager.authenticate('test', 'wrong_username', 'password') == False
    assert manager.authenticate('test', 'username', 'wrong_password') == False

def test_get_credentials():
    manager = AuthManager()
    manager.add_credentials('test', 'username', 'password')
    credentials = manager.get_credentials('test')
    assert credentials.username == 'username'
    assert credentials.password == 'password'

def test_add_credentials():
    manager = AuthManager()
    manager.add_credentials('test', 'username', 'password')
    assert manager.get_credentials('test').username == 'username'
    assert manager.get_credentials('test').password == 'password'
