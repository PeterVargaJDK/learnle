from learnle_site.app.words import Lemma, LemmaDatabaseAdapter
from learnle_site.utils.crud import (
    InMemoryCRUDAdapter,
)


class LemmaInMemoryDatabaseAdapter(LemmaDatabaseAdapter, InMemoryCRUDAdapter[Lemma]):
    def _apply_search_string(self, item: Lemma, search_string: str) -> bool:
        return (
            search_string in item.word
            or search_string in item.definition
            or search_string in item.example
        )
