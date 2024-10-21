from dataclasses import dataclass, field

import pytest

from learnle_site.application.model import Crossword
from learnle_site.services.crossword_database import CrosswordInMemoryDatabaseAdapter
from tests.dummy_data import (
    dummy_crossword,
    dummy_crosswords,
)
from tests.fake_data import fake


async def test_save():
    adapter = CrosswordInMemoryDatabaseAdapter()

    crossword = dummy_crossword()
    assert await adapter.save(crossword) == crossword.uid

    assert adapter.items[crossword.uid] == crossword


@dataclass
class SearchTestCase:
    name: str
    search_string: str = ''
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
    SearchTestCase(
        name='common search string',
        search_string='b',
        state=[
            fake(0).crossword(solution=[]),
            fake(1).crossword(
                solution=[fake(1).crossword_puzzle_word(fake(1).lemma(word='word_a'))]
            ),
            fake(2).crossword(
                solution=[
                    fake(1).crossword_puzzle_word(fake(1).lemma(word='word_a')),
                    fake(2).crossword_puzzle_word(fake(2).lemma(word='word_b')),
                ]
            ),
            fake(3).crossword(
                solution=[
                    fake(1).crossword_puzzle_word(fake(1).lemma(word='word_a')),
                    fake(2).crossword_puzzle_word(fake(2).lemma(word='word_b')),
                    fake(3).crossword_puzzle_word(fake(3).lemma(word='word_c')),
                ]
            ),
        ],
        expected=[
            fake(2).crossword(
                solution=[
                    fake(1).crossword_puzzle_word(fake(1).lemma(word='word_a')),
                    fake(2).crossword_puzzle_word(fake(2).lemma(word='word_b')),
                ]
            ),
            fake(3).crossword(
                solution=[
                    fake(1).crossword_puzzle_word(fake(1).lemma(word='word_a')),
                    fake(2).crossword_puzzle_word(fake(2).lemma(word='word_b')),
                    fake(3).crossword_puzzle_word(fake(3).lemma(word='word_c')),
                ]
            ),
        ],
    ),
    SearchTestCase(
        name='common search string, pagination applies',
        search_string='a',
        state=[
            fake(1).crossword(
                solution=[fake(0).crossword_puzzle_word(fake(0).lemma(word='word_b'))]
            ),
            fake(2).crossword(
                solution=[fake(1).crossword_puzzle_word(fake(1).lemma(word='word_a'))]
            ),
            fake(3).crossword(
                solution=[fake(1).crossword_puzzle_word(fake(1).lemma(word='word_a'))]
            ),
        ],
        expected=[
            fake(3).crossword(
                solution=[fake(1).crossword_puzzle_word(fake(1).lemma(word='word_a'))]
            ),
        ],
        page_size=1,
        page_number=2,
    ),
]


@pytest.mark.parametrize('test_case', search_test_cases, ids=lambda x: x.name)
async def test_search(test_case):
    adapter = CrosswordInMemoryDatabaseAdapter()

    for lemma in test_case.state:
        adapter.items[lemma.uid] = lemma

    assert (
        await adapter.search(
            test_case.search_string, test_case.page_number, test_case.page_size
        )
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
