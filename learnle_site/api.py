from fastapi import (
    APIRouter,
    FastAPI,
)

from learnle_site.controller.words import word_api

router = APIRouter()


@router.get('/ping')
def ping():
    return 'OK'


def create_fast_api():
    api = FastAPI()
    api.include_router(router)
    api.include_router(word_api)
    return api
