from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.tokens import TokenData
from schemas.users import User, UserRead
from utils.config import settings
from utils.errors import UserCredentialsError


AUTH_SECRET_KEY = settings.AUTH_SECRET_KEY
AUTH_ALGORITHM = settings.AUTH_ALGORITHM
AUTH_TOKEN_EXPIRE_MINUTES = settings.AUTH_TOKEN_EXPIRE_MINUTES


class UserRepository:
    model = User

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_user(self, username: str) -> UserRead:
        user = await self.session.exec(select(self.model).where(self.model.username == username))
        if user := user.first():
            return UserRead.from_orm(user)
        else:
            raise UserCredentialsError

    @staticmethod
    def _create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=15)
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, AUTH_SECRET_KEY, algorithm=AUTH_ALGORITHM)
        return encoded_jwt

    async def get(self, token: str) -> UserRead:
        try:
            payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM])
            username: str = payload.get('sub')
            if username is None:
                raise UserCredentialsError
            token_data = TokenData(username=username)
        except JWTError:
            raise UserCredentialsError
        user = await self._get_user(token_data.username)
        if user is None:
            raise UserCredentialsError
        return user

    async def login(self, form_data: OAuth2PasswordRequestForm) -> dict | None:
        query = select(self.model).where(self.model.username == form_data.username)
        user = await self.session.exec(query)
        user = user.first()
        if user and user.verify_password(form_data.password):
            access_token_expires = timedelta(minutes=AUTH_TOKEN_EXPIRE_MINUTES)
            access_token = self._create_access_token(
                data={'sub': user.username},
                expires_delta=access_token_expires,
            )
            return {'access_token': access_token, 'token_type': 'bearer'}
        else:
            raise UserCredentialsError
