from learnle_site.app.words import LemmaDatabaseAdapter
from learnle_site.app.model import Lemma
from learnle_site.utils.crud_adapter import (
    InMemoryCRUDAdapter,
)


class LemmaInMemoryDatabaseAdapter(LemmaDatabaseAdapter, InMemoryCRUDAdapter[Lemma]):
    def _extract_uid(self, item: Lemma) -> str:
        return item.uid

    async def random_lemmas(self) -> list[Lemma]:
        raise NotImplementedError

    def _apply_search_string(self, item: Lemma, search_string: str) -> bool:
        return (
            search_string in item.word
            or search_string in item.definition
            or search_string in item.example
        )
