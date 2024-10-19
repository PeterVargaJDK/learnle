from fastapi import FastAPI, APIRouter

from learnle_site.api.crosswords import crossword_api
from learnle_site.api.words import word_api

root_api_router = APIRouter()
root_api_router.include_router(word_api)
root_api_router.include_router(crossword_api)


@root_api_router.get('/ping')
def ping():
    return 'OK'


def create_fast_api():
    api = FastAPI()
    api.include_router(root_api_router)
    return api
