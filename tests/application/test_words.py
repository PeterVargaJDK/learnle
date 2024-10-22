from unittest.mock import Mock, AsyncMock

import pytest

from learnle_site.application.words import (
    create_lemma,
    LemmaDatabaseAdapter,
    list_lemmas,
)
from tests.dummy_data import (
    dummy_lemmas,
    dummy_lemma,
)


@pytest.fixture
def lemma_db() -> LemmaDatabaseAdapter:
    return Mock(spec_set=LemmaDatabaseAdapter)


class TestCreateLemma:
    async def test_create_lemma__success(self, lemma_db):
        lemma_db.save = AsyncMock()

        lemma = dummy_lemma()

        assert await create_lemma(lemma, lemma_db) == lemma.uid
        lemma_db.save.assert_awaited_once_with(lemma)


class TestListLemmas:
    async def test_list_lemmas__success(self, lemma_db):
        lemmas = dummy_lemmas()
        page_number = 1
        page_size = 50

        lemma_db.list = AsyncMock(return_value=lemmas)

        assert await list_lemmas(page_number, page_size, lemma_db) == lemmas
        lemma_db.list.assert_awaited_once_with(1, 50)
