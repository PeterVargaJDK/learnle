from functools import lru_cache

from fastapi import FastAPI, APIRouter

from learnle.api.crossword_api import crossword_api_router
from learnle.application.model import Lemma, Crossword
from learnle.services.crossword_database import CrosswordInMemoryDatabaseAdapter
from learnle.services.lemma_database import LemmaInMemoryDatabaseAdapter
from learnle.utils.crud_operation import crud_api


@lru_cache
def get_lemma_database():
    return LemmaInMemoryDatabaseAdapter()


@lru_cache
def get_crossword_database():
    return CrosswordInMemoryDatabaseAdapter()


root_api_router = APIRouter()
root_api_router.include_router(crud_api(get_lemma_database, Lemma))
root_api_router.include_router(crud_api(get_crossword_database, Crossword))
root_api_router.include_router(crossword_api_router)


@root_api_router.get('/ping', tags=['misc'])
def ping():
    return 'OK'


def create_fast_api():
    api = FastAPI()
    api.include_router(root_api_router)
    return api
