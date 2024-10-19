from unittest.mock import Mock, AsyncMock

import pytest

from learnle_site.application.crosswords import (
    random_crosswords_puzzle,
    CrosswordsPuzzle,
    CrosswordsPuzzleLetter,
    SolvedCrosswordsPuzzleWord,
)
from learnle_site.application.words import LemmaDatabaseAdapter
from learnle_site.application.model import Lemma
from learnle_site.datatypes import Position

LEMMA_EFGHI = Lemma(
    uid='lemma_1', word='efghi', definition='efghi definition', example='efghi example'
)
LEMMA_FBC = Lemma(
    uid='lemma_2', word='fbc', definition='fbc definition', example='fbc example'
)
LEMMA_HYY = Lemma(
    uid='lemma_3', word='hyy', definition='hyy definition', example='hyy example'
)


@pytest.fixture
def mock_shuffle(monkeypatch):
    import learnle_site.application.crosswords as crosswords

    def _mock_shuffle(shuffled_state: list[str]):
        def _shuffle(list_to_shuffle: list):
            list_to_shuffle.clear()
            list_to_shuffle.extend(shuffled_state)

        monkeypatch.setattr(crosswords, 'shuffle', _shuffle)

    return _mock_shuffle


async def test_random_crosswords_puzzle__all_lemmas_fit(mock_shuffle):
    """
    EFGHI
    ■B■Y■
    ■C■Y■
    """
    lemma_db = Mock(spec_set=LemmaDatabaseAdapter)
    lemma_db.random_lemmas = AsyncMock(return_value=[LEMMA_EFGHI, LEMMA_FBC, LEMMA_HYY])
    mock_shuffle(['b', 'c', 'i', 'y', 'g', 'h', 'y', 'e', 'f'])
    assert await random_crosswords_puzzle(lemma_db) == CrosswordsPuzzle(
        width=5,
        height=3,
        shuffled_state=[
            CrosswordsPuzzleLetter(character='b', position=Position(x=0, y=0)),
            CrosswordsPuzzleLetter(character='c', position=Position(x=1, y=0)),
            CrosswordsPuzzleLetter(character='i', position=Position(x=2, y=0)),
            CrosswordsPuzzleLetter(character='y', position=Position(x=3, y=0)),
            CrosswordsPuzzleLetter(character='g', position=Position(x=4, y=0)),
            CrosswordsPuzzleLetter(character='h', position=Position(x=1, y=1)),
            CrosswordsPuzzleLetter(character='y', position=Position(x=1, y=2)),
            CrosswordsPuzzleLetter(character='e', position=Position(x=3, y=1)),
            CrosswordsPuzzleLetter(character='f', position=Position(x=3, y=2)),
        ],
        solution=[
            SolvedCrosswordsPuzzleWord(
                lemma=LEMMA_EFGHI,
                letters=[
                    CrosswordsPuzzleLetter(position=Position(x=0, y=0), character='e'),
                    CrosswordsPuzzleLetter(position=Position(x=1, y=0), character='f'),
                    CrosswordsPuzzleLetter(position=Position(x=2, y=0), character='g'),
                    CrosswordsPuzzleLetter(position=Position(x=3, y=0), character='h'),
                    CrosswordsPuzzleLetter(position=Position(x=4, y=0), character='i'),
                ],
            ),
            SolvedCrosswordsPuzzleWord(
                lemma=LEMMA_FBC,
                letters=[
                    CrosswordsPuzzleLetter(position=Position(x=1, y=0), character='f'),
                    CrosswordsPuzzleLetter(position=Position(x=1, y=1), character='b'),
                    CrosswordsPuzzleLetter(position=Position(x=1, y=2), character='c'),
                ],
            ),
            SolvedCrosswordsPuzzleWord(
                lemma=LEMMA_HYY,
                letters=[
                    CrosswordsPuzzleLetter(position=Position(x=3, y=0), character='h'),
                    CrosswordsPuzzleLetter(position=Position(x=3, y=1), character='y'),
                    CrosswordsPuzzleLetter(position=Position(x=3, y=2), character='y'),
                ],
            ),
        ],
    )
