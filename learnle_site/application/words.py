from abc import (
    ABC,
    abstractmethod,
)

from learnle_site.application.model import Lemma, LemmaDraft
from learnle_site.utils.crud_adapter import CRUDAdapter, generate_uid


class LemmaDatabaseAdapter(CRUDAdapter[Lemma], ABC):
    @abstractmethod
    async def random_lemmas(self) -> list[Lemma]:
        raise NotImplementedError


async def create_lemma(lemma: LemmaDraft, lemma_db: LemmaDatabaseAdapter):
    uid = generate_uid()
    lemma.uid = uid  # type: ignore[misc]
    await lemma_db.save(lemma)
    return uid


async def list_lemmas(
    search_string: str, page_number: int, page_size: int, lemma_db: LemmaDatabaseAdapter
) -> list[Lemma]:
    return await lemma_db.search(search_string, page_number, page_size)
