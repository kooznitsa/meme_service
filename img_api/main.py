from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.config import settings
from routers import memes

app = FastAPI(
    title=settings.TITLE,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_prefix=settings.OPENAPI_PREFIX,
    docs_url=settings.DOCS_URL,
    openapi_url=settings.OPENAPI_URL,
)

app.include_router(
    memes.router,
    prefix=settings.API_PREFIX,
    tags=['Memes'],
)

origins = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
async def root():
    return {'status': 'OK'}
