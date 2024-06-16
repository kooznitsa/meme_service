from pathlib import Path

import pytest


async def upload_img(async_client):
    _test_upload_file = Path('tests/img', 'shark.jpg')
    _files = {'file': _test_upload_file.open('rb')}

    response = await async_client.post(
        'api/memes/',
        files=_files,
        data={'description': 'test'},
    )

    return response


@pytest.mark.asyncio
async def test_list(async_client):
    await upload_img(async_client)

    response = await async_client.get(
        'api/memes/',
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create(async_client):
    response = await upload_img(async_client)

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get(async_client):
    await upload_img(async_client)

    response = await async_client.get(
        'api/memes/1',
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete(async_client):
    await upload_img(async_client)

    response = await async_client.delete(
        'api/memes/1',
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update(async_client):
    await upload_img(async_client)

    response = await async_client.put(
        'api/memes/1',
        json={'name': 'shark.jpg', 'description': 'test2', 'last_updated_at': '2024-06-16T10:23:37'}
    )

    assert response.status_code == 200
