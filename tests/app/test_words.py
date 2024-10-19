import uuid
from unittest.mock import Mock, AsyncMock

import pytest

from learnle_site.application.words import (
    create_lemma,
    LemmaDatabaseAdapter,
    list_lemmas,
)
from tests.dummy_data import (
    dummy_lemma,
    merge,
    dummy_lemmas,
)


@pytest.fixture
def lemma_db() -> LemmaDatabaseAdapter:
    return Mock(spec_set=LemmaDatabaseAdapter)


class TestCreateLemma:
    @pytest.fixture
    def uid_mock(self, monkeypatch):
        from learnle_site.application import words

        mock_uid = uuid.uuid4().hex
        monkeypatch.setattr(words, 'generate_uid', lambda: mock_uid)
        return mock_uid

    async def test_create_lemma__success(self, lemma_db, uid_mock):
        lemma_db.save = AsyncMock()

        lemma = dummy_lemma()

        assert await create_lemma(lemma, lemma_db) == uid_mock
        lemma_db.save.assert_awaited_once_with(
            merge(
                lemma,
                uid=uid_mock,
            )
        )


class TestListLemmas:
    async def test_list_lemmas__success(self, lemma_db):
        lemmas = dummy_lemmas()
        search_string = 'search string'
        page_number = 1
        page_size = 50

        lemma_db.search = AsyncMock(return_value=lemmas)

        assert (
            await list_lemmas(search_string, page_number, page_size, lemma_db) == lemmas
        )
        lemma_db.search.assert_awaited_once_with(search_string, 1, 50)
