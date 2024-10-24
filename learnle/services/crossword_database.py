from learnle.application.crosswords import CrosswordDatabaseAdapter
from learnle.application.model import Crossword
from learnle.utils.crud_operation import InMemoryCRUDAdapter


class CrosswordInMemoryDatabaseAdapter(
    CrosswordDatabaseAdapter, InMemoryCRUDAdapter[Crossword]
):
    def _set_uid(self, item: Crossword, uid: str):
        item.uid = uid

    def _extract_uid(self, item: Crossword) -> str:
        return item.uid

    async def random_lemmas(self) -> list[Crossword]:
        raise NotImplementedError
