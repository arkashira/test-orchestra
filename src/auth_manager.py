import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict

@dataclass
class AuthToken:
    token: str
    expires_at: datetime

class AuthManager:
    def __init__(self):
        self.tokens: Dict[str, AuthToken] = {}

    def get_token(self, flow: str) -> str:
        if flow not in self.tokens:
            raise ValueError(f"Flow {flow} not supported")
        token = self.tokens[flow]
        if token.expires_at < datetime.now():
            self.renew_token(flow)
        return self.tokens[flow].token

    def renew_token(self, flow: str) -> None:
        if flow == "oauth2":
            self.tokens[flow] = AuthToken(token="new_oauth2_token", expires_at=datetime.now() + timedelta(hours=1))
        elif flow == "jwt":
            self.tokens[flow] = AuthToken(token="new_jwt_token", expires_at=datetime.now() + timedelta(hours=1))
        elif flow == "api_key":
            self.tokens[flow] = AuthToken(token="new_api_key_token", expires_at=datetime.now() + timedelta(hours=1))

    def add_flow(self, flow: str, token: str, expires_at: datetime) -> None:
        self.tokens[flow] = AuthToken(token=token, expires_at=expires_at)

    def remove_flow(self, flow: str) -> None:
        if flow in self.tokens:
            del self.tokens[flow]
