import json
from dataclasses import dataclass
from typing import Dict

@dataclass
class AuthCredentials:
    username: str
    password: str

class AuthManager:
    def __init__(self, credentials_file: str = 'credentials.json'):
        self.credentials_file = credentials_file
        self.credentials: Dict[str, AuthCredentials] = self.load_credentials()

    def load_credentials(self) -> Dict[str, AuthCredentials]:
        try:
            with open(self.credentials_file, 'r') as f:
                data = json.load(f)
                return {key: AuthCredentials(**value) for key, value in data.items()}
        except FileNotFoundError:
            return {}

    def save_credentials(self) -> None:
        data = {key: {'username': value.username, 'password': value.password} for key, value in self.credentials.items()}
        with open(self.credentials_file, 'w') as f:
            json.dump(data, f)

    def add_credentials(self, key: str, username: str, password: str) -> None:
        self.credentials[key] = AuthCredentials(username, password)
        self.save_credentials()

    def get_credentials(self, key: str) -> AuthCredentials:
        return self.credentials.get(key)

    def authenticate(self, key: str, username: str, password: str) -> bool:
        credentials = self.get_credentials(key)
        if credentials and credentials.username == username and credentials.password == password:
            return True
        return False
