from functools import lru_cache

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from learnle_site.app.words import LemmaDatabaseAdapter
from learnle_site.app.model import Lemma
from learnle_site.app import words
from learnle_site.services.lemma_database import LemmaInMemoryDatabaseAdapter

word_api = APIRouter(prefix='/word')


@lru_cache
def get_lemma_database():
    return LemmaInMemoryDatabaseAdapter()


@word_api.post('/lemma')
async def create_lemma(
    lemma: Lemma, lemma_db: LemmaDatabaseAdapter = Depends(get_lemma_database)
) -> str:
    return await words.create_lemma(lemma, lemma_db)


class ListRequest(BaseModel):
    search_string: str = ''
    page_number: int = 1
    page_size: int = 50


@word_api.get('/lemma')
async def list_lemmas(
    list_request: ListRequest = Query(),
    lemma_db: LemmaDatabaseAdapter = Depends(get_lemma_database),
) -> list[Lemma]:
    return await words.list_lemmas(
        list_request.search_string,
        list_request.page_number,
        list_request.page_size,
        lemma_db,
    )
