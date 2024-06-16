from typing import BinaryIO

import aiohttp

from utils.config import settings


class APIGateway:
    _api_root_url: str = settings.GW_ROOT_URL
    _user: str = settings.AUTH_USER
    _password: str = settings.AUTH_PASSWORD

    class Route:
        minio_route = 'minio/'
        auth_route = 'auth/token'

    @classmethod
    async def _build_url(cls, route: str, method: str = '') -> str:
        return f'{cls._api_root_url}{route}{method}'

    @classmethod
    async def login_user(cls) -> dict:
        async with aiohttp.ClientSession() as session:
            url = await cls._build_url(cls.Route.auth_route)
            payload = {
                'username': settings.AUTH_USER,
                'password': settings.AUTH_PASSWORD,
            }
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            async with session.post(url, data=payload, headers=headers) as resp:
                json_obj = await resp.json()
                return {
                    'accept': 'application/json',
                    'Authorization': f'Bearer {json_obj.get("access_token")}'
                }

    @classmethod
    async def create_or_update(
            cls,
            file: BinaryIO,
            description: str | None = None,
    ) -> dict:
        headers = await cls.login_user()
        url = f'{await cls._build_url(cls.Route.minio_route, "create_or_update")}'

        data = aiohttp.FormData()
        data.add_field('file', file.file.read(), filename=file.filename)
        data.add_field('description', description)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                return await response.json()

    @classmethod
    async def get_file(cls, name: str) -> dict:
        headers = await cls.login_user()

        async with aiohttp.ClientSession() as session:
            url = f'{await cls._build_url(cls.Route.minio_route, "get")}?name={name}'
            async with session.get(url, headers=headers) as resp:
                return await resp.json()

    @classmethod
    async def get_files(cls) -> dict:
        headers = await cls.login_user()

        async with aiohttp.ClientSession() as session:
            url = await cls._build_url(cls.Route.minio_route, 'list')
            async with session.get(url, headers=headers) as resp:
                return await resp.json()

    @classmethod
    async def delete_file(cls, name: str) -> dict:
        headers = await cls.login_user()

        async with aiohttp.ClientSession() as session:
            url = f'{await cls._build_url(cls.Route.minio_route, "delete")}?name={name}'
            async with session.delete(url, headers=headers) as resp:
                return await resp.json()
