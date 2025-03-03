from datetime import datetime, timedelta

import jwt

from core.config import config
from core.exceptions import DecodeTokenException, ExpiredTokenException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends

security = HTTPBearer()

class TokenHelper:
    @staticmethod
    def encode(payload: dict, expire_period: int = 3600) -> str:
        token = jwt.encode(
            payload={
                **payload,
                "exp": datetime.utcnow() + timedelta(seconds=expire_period),
            },
            key=config.JWT_SECRET_KEY,
            algorithm=config.JWT_ALGORITHM,
        )
        return token

    @staticmethod
    def decode(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                config.JWT_ALGORITHM,
            )
        except jwt.exceptions.DecodeError:
            raise DecodeTokenException
        except jwt.exceptions.ExpiredSignatureError:
            raise ExpiredTokenException

    @staticmethod
    def decode_expired_token(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                config.JWT_ALGORITHM,
                options={"verify_exp": False},
            )
        except jwt.exceptions.DecodeError:
            raise DecodeTokenException
        
    @staticmethod
    def is_valid_token(authorization: HTTPAuthorizationCredentials = Depends(security)):
        try:
            decoded = jwt.decode(
                authorization.credentials,
                config.JWT_SECRET_KEY,
                config.JWT_ALGORITHM,
            )
        except jwt.exceptions.DecodeError:
            raise DecodeTokenException
        except jwt.exceptions.ExpiredSignatureError:
            raise ExpiredTokenException
        if decoded:
            return decoded

