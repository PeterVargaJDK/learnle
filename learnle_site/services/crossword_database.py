from learnle_site.application.crosswords import CrosswordDatabaseAdapter
from learnle_site.application.model import Crossword
from learnle_site.utils.crud_adapter import InMemoryCRUDAdapter


class CrosswordInMemoryDatabaseAdapter(
    CrosswordDatabaseAdapter, InMemoryCRUDAdapter[Crossword]
):
    def _extract_uid(self, item: Crossword) -> str:
        return item.uid

    async def random_lemmas(self) -> list[Crossword]:
        raise NotImplementedError

    def _apply_search_string(self, item: Crossword, search_string: str) -> bool:
        return any([search_string in word.lemma.word for word in item.solution])
