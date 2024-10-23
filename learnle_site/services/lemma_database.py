from learnle_site.application.words import LemmaDatabaseAdapter
from learnle_site.application.model import Lemma
from learnle_site.utils.crud_operation import (
    InMemoryCRUDAdapter,
)


class LemmaInMemoryDatabaseAdapter(LemmaDatabaseAdapter, InMemoryCRUDAdapter[Lemma]):
    def _set_uid(self, item: Lemma, uid: str):
        item.uid = uid

    def _extract_uid(self, item: Lemma) -> str:
        return item.uid

    async def random_lemmas(self) -> list[Lemma]:
        raise NotImplementedError
