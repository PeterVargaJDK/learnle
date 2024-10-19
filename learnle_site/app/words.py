from abc import (
    ABC,
)


from learnle_site.utils.crud import CRUDAdapter, generate_uid, Entity


class Lemma(Entity):
    word: str
    definition: str
    example: str


class LemmaDatabaseAdapter(CRUDAdapter[Lemma], ABC):
    pass


async def create_lemma(lemma: Lemma, lemma_db: LemmaDatabaseAdapter):
    uid = generate_uid()
    lemma.uid = uid
    await lemma_db.save(lemma)
    return uid


async def list_lemmas(
    search_string: str, page_number: int, page_size: int, lemma_db: LemmaDatabaseAdapter
) -> list[Lemma]:
    return await lemma_db.search(search_string, page_number, page_size)
