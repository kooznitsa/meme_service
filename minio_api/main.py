from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import minio_router, users
from utils.config import settings
from utils.add_sample_data import add_sample_data

app = FastAPI(
    title=settings.TITLE,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_prefix=settings.OPENAPI_PREFIX,
    docs_url=settings.DOCS_URL,
    openapi_url=settings.OPENAPI_URL,
)

app.include_router(
    minio_router.router,
    prefix=settings.API_PREFIX,
    tags=['MinIO'],
)

app.include_router(
    users.router,
    prefix=settings.API_PREFIX,
    tags=['Auth'],
)

origins = [
    'http://localhost:9000',
    'http://127.0.0.1:9000',
    'http://localhost:8001',
    'http://127.0.0.1:8001',
    'http://localhost:9001',
    'http://127.0.0.1:9001',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
async def init_data():
    try:
        add_sample_data()
    except Exception:
        pass


@app.get('/')
async def root():
    return {'status': 'OK'}
