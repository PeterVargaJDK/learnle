from abc import (
    ABC,
    abstractmethod,
)

from learnle_site.application.model import Lemma
from learnle_site.utils.crud_adapter import CRUDAdapter


class LemmaDatabaseAdapter(CRUDAdapter[Lemma], ABC):
    @abstractmethod
    async def random_lemmas(self) -> list[Lemma]:
        raise NotImplementedError


async def create_lemma(lemma: Lemma, lemma_db: LemmaDatabaseAdapter):
    await lemma_db.save(lemma)
    return lemma.uid


async def list_lemmas(
    page_number: int, page_size: int, lemma_db: LemmaDatabaseAdapter
) -> list[Lemma]:
    return await lemma_db.list(page_number, page_size)
