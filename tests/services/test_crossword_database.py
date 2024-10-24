from dataclasses import dataclass, field

import pytest

from learnle.application.model import Crossword
from learnle.services.crossword_database import CrosswordInMemoryDatabaseAdapter
from tests.dummy_data import (
    dummy_crossword,
    dummy_crosswords,
)


async def test_save():
    adapter = CrosswordInMemoryDatabaseAdapter()

    crossword = dummy_crossword()
    assert await adapter.save(crossword) == crossword

    assert adapter.items[crossword.uid] == crossword


@dataclass
class SearchTestCase:
    name: str
    page_number: int = 1
    page_size: int = 10
    state: list[Crossword] = field(default_factory=list)
    expected: list[Crossword] = field(default_factory=list)


crosswords = dummy_crosswords()

search_test_cases = [
    SearchTestCase(name='empty'),
    SearchTestCase(
        name='all items fit into the first page',
        page_size=10,
        state=crosswords,
        expected=crosswords,
    ),
    SearchTestCase(
        name='all items fit into the first page, second page',
        page_size=10,
        page_number=2,
        state=crosswords,
        expected=[],
    ),
    SearchTestCase(
        name='many items, first page',
        page_size=2,
        page_number=1,
        state=crosswords,
        expected=crosswords[:2],
    ),
    SearchTestCase(
        name='many items, second page',
        page_size=2,
        page_number=2,
        state=crosswords,
        expected=crosswords[2:4],
    ),
]


@pytest.mark.parametrize('test_case', search_test_cases, ids=lambda x: x.name)
async def test_search(test_case):
    adapter = CrosswordInMemoryDatabaseAdapter()

    for lemma in test_case.state:
        adapter.items[lemma.uid] = lemma

    assert (
        await adapter.list(test_case.page_number, test_case.page_size)
        == test_case.expected
    )


async def test_get_by_uid():
    adapter = CrosswordInMemoryDatabaseAdapter()

    crossword = dummy_crossword()
    adapter.items[crossword.uid] = crossword

    assert await adapter.get_by_uid(crossword.uid) == crossword


async def test_get_by_uid__unknown_uid():
    adapter = CrosswordInMemoryDatabaseAdapter()

    assert await adapter.get_by_uid('does not exist') is None


async def test_delete():
    adapter = CrosswordInMemoryDatabaseAdapter()

    crossword = dummy_crossword()
    adapter.items[crossword.uid] = crossword

    await adapter.delete(crossword.uid)

    assert crossword.uid not in adapter.items


async def test_delete__unknown_uid():
    adapter = CrosswordInMemoryDatabaseAdapter()

    with pytest.raises(Exception):
        await adapter.delete('does not exist')
