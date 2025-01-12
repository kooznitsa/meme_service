import asyncio
from typing import AsyncGenerator, Callable, Generator

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from utils.config import settings
from schemas.users import User

test_db = (
    f'postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}'
    f'@{settings.POSTGRES_TEST_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_TEST_DB}'
)

engine = create_async_engine(
    test_db,
    echo=settings.DB_ECHO_LOG,
    future=True,
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope='session')
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def db_session() -> AsyncSession:
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)
        await connection.run_sync(SQLModel.metadata.create_all)
        async with async_session(bind=connection) as session:
            yield session
            await session.flush()
            await session.rollback()


@pytest.fixture()
def override_get_db(db_session: AsyncSession) -> Callable:
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest.fixture()
def app(override_get_db: Callable) -> FastAPI:
    from utils.sessions import get_db
    from main import app

    app.dependency_overrides[get_db] = override_get_db

    return app


@pytest_asyncio.fixture()
async def async_client(app: FastAPI) -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture()
async def async_client_authenticated(app: FastAPI) -> AsyncGenerator:
    from routers.users import get_current_user

    def skip_auth():
        pass

    app.dependency_overrides[get_current_user] = skip_auth

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac


@pytest.fixture()
def user_to_create() -> User:
    user = User(username=settings.AUTH_USER)
    user.set_password(settings.AUTH_PASSWORD)
    return user


@pytest_asyncio.fixture()
async def create_user(db_session: AsyncSession, user_to_create: User) -> User:
    async def _create_user():
        db_session.add(user_to_create)
        await db_session.commit()
        await db_session.refresh(user_to_create)
        return user_to_create

    return _create_user
