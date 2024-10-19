from abc import (
    ABC,
    abstractmethod,
)

from learnle_site.app.model import Lemma
from learnle_site.utils.crud_adapter import CRUDAdapter, generate_uid


class LemmaDatabaseAdapter(CRUDAdapter[Lemma], ABC):
    @abstractmethod
    async def random_lemmas(self) -> list[Lemma]:
        raise NotImplementedError


async def create_lemma(lemma: Lemma, lemma_db: LemmaDatabaseAdapter):
    uid = generate_uid()
    lemma.uid = uid
    await lemma_db.save(lemma)
    return uid


async def list_lemmas(
    search_string: str, page_number: int, page_size: int, lemma_db: LemmaDatabaseAdapter
) -> list[Lemma]:
    return await lemma_db.search(search_string, page_number, page_size)
