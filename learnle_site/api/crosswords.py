from fastapi import APIRouter
from pydantic import BaseModel, Field

from learnle_site.application.model import Lemma, CrosswordDraft
import learnle_site.application.crosswords as crosswords

crossword_api = APIRouter(prefix='/crossword')


class CreateCrosswordRequest(BaseModel, frozen=True):
    lemmas: set[Lemma] = Field(max_length=3)
    maximum_width: int = Field(gt=3, le=10)
    maximum_height: int = Field(gt=3, le=10)


@crossword_api.post('/draft')
async def create_crossword_draft(request: CreateCrosswordRequest) -> CrosswordDraft:
    return crosswords.create_crossword_draft(
        request.lemmas, request.maximum_width, request.maximum_height
    )
