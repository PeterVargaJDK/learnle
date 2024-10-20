import uuid
from unittest.mock import Mock, AsyncMock

import pytest

from learnle_site.application.crosswords import (
    random_crossword_puzzle,
    CrosswordPuzzle,
    CrosswordPuzzleLetter,
    SolvedCrosswordPuzzleWord,
    create_crossword_draft,
    CrosswordError,
)
from learnle_site.application.words import LemmaDatabaseAdapter
from learnle_site.application.model import Lemma, Crossword, CrosswordDraft
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

LEMMA_IJKL = Lemma(
    uid='lemma_4', word='ijkl', definition='ijkl definition', example='ijkl example'
)


@pytest.fixture
def mock_uid(monkeypatch):
    from learnle_site.application import crosswords

    mocked_uid = uuid.uuid4().hex
    monkeypatch.setattr(crosswords, 'generate_uid', lambda: mocked_uid)
    return mocked_uid


@pytest.fixture
def mock_shuffle(monkeypatch):
    import learnle_site.application.crosswords as crossword

    def _mock_shuffle(shuffled_state: list[str]):
        def _shuffle(list_to_shuffle: list):
            list_to_shuffle.clear()
            list_to_shuffle.extend(shuffled_state)

        monkeypatch.setattr(crossword, 'shuffle', _shuffle)

    return _mock_shuffle


async def test_random_crossword_puzzle__all_lemmas_fit(mock_shuffle, mock_uid):
    """
    EFGHI
    ■B■Y■
    ■C■Y■
    """
    lemma_db = Mock(spec_set=LemmaDatabaseAdapter)
    lemma_db.random_lemmas = AsyncMock(return_value=[LEMMA_EFGHI, LEMMA_FBC, LEMMA_HYY])
    mock_shuffle(['b', 'c', 'i', 'y', 'g', 'h', 'y', 'e', 'f'])
    assert await random_crossword_puzzle(lemma_db) == CrosswordPuzzle(
        uid=mock_uid,
        width=5,
        height=3,
        shuffled_state=[
            CrosswordPuzzleLetter(character='b', position=Position(x=0, y=0)),
            CrosswordPuzzleLetter(character='c', position=Position(x=1, y=0)),
            CrosswordPuzzleLetter(character='i', position=Position(x=2, y=0)),
            CrosswordPuzzleLetter(character='y', position=Position(x=3, y=0)),
            CrosswordPuzzleLetter(character='g', position=Position(x=4, y=0)),
            CrosswordPuzzleLetter(character='h', position=Position(x=1, y=0)),
            CrosswordPuzzleLetter(character='y', position=Position(x=1, y=1)),
            CrosswordPuzzleLetter(character='e', position=Position(x=1, y=2)),
            CrosswordPuzzleLetter(character='f', position=Position(x=3, y=0)),
        ],
        solution=[
            SolvedCrosswordPuzzleWord(
                lemma=LEMMA_EFGHI,
                letters=[
                    CrosswordPuzzleLetter(position=Position(x=0, y=0), character='e'),
                    CrosswordPuzzleLetter(position=Position(x=1, y=0), character='f'),
                    CrosswordPuzzleLetter(position=Position(x=2, y=0), character='g'),
                    CrosswordPuzzleLetter(position=Position(x=3, y=0), character='h'),
                    CrosswordPuzzleLetter(position=Position(x=4, y=0), character='i'),
                ],
            ),
            SolvedCrosswordPuzzleWord(
                lemma=LEMMA_FBC,
                letters=[
                    CrosswordPuzzleLetter(position=Position(x=1, y=0), character='f'),
                    CrosswordPuzzleLetter(position=Position(x=1, y=1), character='b'),
                    CrosswordPuzzleLetter(position=Position(x=1, y=2), character='c'),
                ],
            ),
            SolvedCrosswordPuzzleWord(
                lemma=LEMMA_HYY,
                letters=[
                    CrosswordPuzzleLetter(position=Position(x=3, y=0), character='h'),
                    CrosswordPuzzleLetter(position=Position(x=3, y=1), character='y'),
                    CrosswordPuzzleLetter(position=Position(x=3, y=2), character='y'),
                ],
            ),
        ],
    )


def test_create_crossword_draft(mock_uid):
    lemmas = {LEMMA_FBC, LEMMA_EFGHI, LEMMA_IJKL}
    crossword = create_crossword_draft(lemmas, 5, 5)
    assert crossword == CrosswordDraft(
        crossword=Crossword(
            uid=mock_uid,
            width=5,
            height=4,
            solution=[
                SolvedCrosswordPuzzleWord(
                    lemma=Lemma(
                        uid='lemma_1',
                        word='efghi',
                        definition='efghi definition',
                        example='efghi example',
                    ),
                    letters=[
                        CrosswordPuzzleLetter(
                            character='e', position=Position(x=0, y=0)
                        ),
                        CrosswordPuzzleLetter(
                            character='f', position=Position(x=1, y=0)
                        ),
                        CrosswordPuzzleLetter(
                            character='g', position=Position(x=2, y=0)
                        ),
                        CrosswordPuzzleLetter(
                            character='h', position=Position(x=3, y=0)
                        ),
                        CrosswordPuzzleLetter(
                            character='i', position=Position(x=4, y=0)
                        ),
                    ],
                ),
                SolvedCrosswordPuzzleWord(
                    lemma=Lemma(
                        uid='lemma_2',
                        word='fbc',
                        definition='fbc definition',
                        example='fbc example',
                    ),
                    letters=[
                        CrosswordPuzzleLetter(
                            character='f', position=Position(x=1, y=0)
                        ),
                        CrosswordPuzzleLetter(
                            character='b', position=Position(x=1, y=1)
                        ),
                        CrosswordPuzzleLetter(
                            character='c', position=Position(x=1, y=2)
                        ),
                    ],
                ),
                SolvedCrosswordPuzzleWord(
                    lemma=Lemma(
                        uid='lemma_4',
                        word='ijkl',
                        definition='ijkl definition',
                        example='ijkl example',
                    ),
                    letters=[
                        CrosswordPuzzleLetter(
                            character='i', position=Position(x=4, y=0)
                        ),
                        CrosswordPuzzleLetter(
                            character='j', position=Position(x=4, y=1)
                        ),
                        CrosswordPuzzleLetter(
                            character='k', position=Position(x=4, y=2)
                        ),
                        CrosswordPuzzleLetter(
                            character='l', position=Position(x=4, y=3)
                        ),
                    ],
                ),
            ],
        ),
        lemmas_excluded=set(),
    )


def test_create_crossword_draft__little_maximum_dimensions(mock_uid):
    lemmas = {LEMMA_FBC, LEMMA_EFGHI, LEMMA_IJKL}
    assert create_crossword_draft(lemmas, 1, 1) == CrosswordDraft(
        crossword=Crossword(uid=mock_uid, width=1, height=1, solution=[]),
        lemmas_excluded={LEMMA_EFGHI, LEMMA_IJKL, LEMMA_FBC},
    )


def test_create_crossword_draft__lemmas_with_a_common_word():
    lemmas = {
        Lemma(
            uid='uid1',
            word='common word',
            definition='definition1',
            example='example1',
        ),
        Lemma(
            uid='uid2',
            word='common word',
            definition='definition2',
            example='example2',
        ),
    }
    with pytest.raises(CrosswordError, match='Non-unique words detected'):
        create_crossword_draft(lemmas, 3, 3)
