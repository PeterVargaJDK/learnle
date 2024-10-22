from dataclasses import dataclass, field

import pytest

from learnle_site.application.model import Lemma
from learnle_site.services.lemma_database import LemmaInMemoryDatabaseAdapter
from tests.dummy_data import dummy_lemma, dummy_lemmas


async def test_save():
    adapter = LemmaInMemoryDatabaseAdapter()

    lemma = dummy_lemma()
    assert await adapter.save(lemma) == lemma.uid

    assert adapter.items[lemma.uid] == lemma


@dataclass
class SearchTestCase:
    name: str
    page_number: int = 1
    page_size: int = 10
    state: list[Lemma] = field(default_factory=list)
    expected: list[Lemma] = field(default_factory=list)


lemmas = dummy_lemmas()

search_test_cases = [
    SearchTestCase(name='empty'),
    SearchTestCase(
        name='all items fit into the first page',
        page_size=10,
        state=lemmas,
        expected=lemmas,
    ),
    SearchTestCase(
        name='all items fit into the first page, second page',
        page_size=10,
        page_number=2,
        state=lemmas,
        expected=[],
    ),
    SearchTestCase(
        name='many items, first page',
        page_size=2,
        page_number=1,
        state=lemmas,
        expected=lemmas[:2],
    ),
    SearchTestCase(
        name='many items, second page',
        page_size=2,
        page_number=2,
        state=lemmas,
        expected=lemmas[2:4],
    ),
]


@pytest.mark.parametrize('test_case', search_test_cases, ids=lambda x: x.name)
async def test_search(test_case):
    adapter = LemmaInMemoryDatabaseAdapter()

    for lemma in test_case.state:
        adapter.items[lemma.uid] = lemma

    assert (
        await adapter.list(test_case.page_number, test_case.page_size)
        == test_case.expected
    )


async def test_get_by_uid():
    adapter = LemmaInMemoryDatabaseAdapter()

    lemma = dummy_lemma()
    adapter.items[lemma.uid] = lemma

    assert await adapter.get_by_uid(lemma.uid) == lemma


async def test_get_by_uid__unknown_uid():
    adapter = LemmaInMemoryDatabaseAdapter()

    assert await adapter.get_by_uid('does not exist') is None


async def test_delete():
    adapter = LemmaInMemoryDatabaseAdapter()

    lemma = dummy_lemma()
    adapter.items[lemma.uid] = lemma

    await adapter.delete(lemma.uid)

    assert lemma.uid not in adapter.items


async def test_delete__unknown_uid():
    adapter = LemmaInMemoryDatabaseAdapter()

    with pytest.raises(Exception):
        await adapter.delete('does not exist')
