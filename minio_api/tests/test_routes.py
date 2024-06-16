from pathlib import Path

from fastapi import status
import pytest

from utils.config import settings


async def upload_img(async_client_authenticated):
    _test_upload_file = Path('tests/img', 'cat.png')
    _files = {'file': _test_upload_file.open('rb')}

    response = await async_client_authenticated.post(
        'api/minio/create_or_update',
        files=_files,
        data={'description': 'test'},
    )

    return response


@pytest.mark.asyncio
async def test_create_or_update(async_client_authenticated):
    response = await upload_img(async_client_authenticated)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get(async_client_authenticated):
    await upload_img(async_client_authenticated)

    response = await async_client_authenticated.get(
        'api/minio/get?name=cat.png',
    )

    assert response.status_code == 200
    assert response.json().get('description') == 'test'


@pytest.mark.asyncio
async def test_list(async_client_authenticated):
    await upload_img(async_client_authenticated)

    response = await async_client_authenticated.get(
        'api/minio/list',
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_delete(async_client_authenticated):
    await upload_img(async_client_authenticated)

    response_delete = await async_client_authenticated.delete(
        'api/minio/delete?name=cat.png',
    )

    response_get = await async_client_authenticated.get(
        'api/minio/get?name=cat.png',
    )

    assert response_delete.status_code == 200
    assert response_get.status_code == 404


@pytest.mark.parametrize(
    'user_info, status_code',
    [
        ({'username': settings.AUTH_USER, 'password': settings.AUTH_PASSWORD}, status.HTTP_200_OK),
        ({'username': settings.AUTH_USER, 'password': '123'}, status.HTTP_400_BAD_REQUEST),
        ({'username': 'shark', 'password': settings.AUTH_PASSWORD}, status.HTTP_400_BAD_REQUEST),
    ]
)
@pytest.mark.asyncio
async def test_login(create_user, async_client, user_info, status_code):
    await create_user()

    response = await async_client.post('api/auth/token', data=user_info)

    assert response.status_code == status_code
