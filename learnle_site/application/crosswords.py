from abc import ABC
from random import shuffle
from typing import Iterable

from learnle_site.application.model import (
    CrosswordPuzzleLetter,
    SolvedCrosswordPuzzleWord,
    CrosswordPuzzle,
    Lemma,
    Crossword,
    CrosswordDraft,
)

from learnle_site.application.words import LemmaDatabaseAdapter
from learnle_site.datatypes import Dimensions
from learnle_site.utils.crossword_grid import (
    UnpackedCrosswordGrid,
)
from learnle_site.utils.crud_operation import CRUDAdapter
from learnle_site.utils import generate_uid


def _get_shuffled_characters(letters: Iterable[CrosswordPuzzleLetter]):
    characters = [letter.character for letter in letters]
    shuffle(characters)
    return characters


async def random_crossword_puzzle(
    lemma_database: LemmaDatabaseAdapter,
) -> CrosswordPuzzle:
    random_lemmas = await lemma_database.random_lemmas()
    draft = _build_crossword_grid(list(random_lemmas))
    solution_letters = draft.crossword.solution_letters
    shuffled_characters = _get_shuffled_characters(solution_letters)
    return CrosswordPuzzle(
        uid=generate_uid(),
        width=draft.crossword.width,
        height=draft.crossword.height,
        shuffled_state=[
            CrosswordPuzzleLetter(character=character, position=letter.position)
            for letter, character in zip(solution_letters, shuffled_characters)
        ],
        solution=draft.crossword.solution,
    )


class CrosswordDatabaseAdapter(CRUDAdapter[Crossword], ABC):
    pass


class CrosswordError(Exception):
    pass


def create_crossword_draft(
    lemmas: list[Lemma],
    maximum_width: int | None = None,
    maximum_height: int | None = None,
) -> CrosswordDraft:
    maximum_dimensions = (
        Dimensions(maximum_width, maximum_height)
        if maximum_width and maximum_height
        else None
    )
    return _build_crossword_grid(lemmas, maximum_dimensions)


def _sort_lemmas(lemmas: Iterable[Lemma]) -> list[Lemma]:
    sorted_lemmas = list(lemmas)
    sorted_lemmas.sort(key=lambda x: len(x.word), reverse=True)
    return sorted_lemmas


def _insert_lemmas(
    sorted_lemmas: Iterable[Lemma], unpacked_crossword_grid: UnpackedCrosswordGrid
) -> dict[str, list[CrosswordPuzzleLetter]]:
    letters_by_lemma: dict[str, list[CrosswordPuzzleLetter]] = {}
    for lemma in sorted_lemmas:
        if letters := unpacked_crossword_grid.add_word(lemma.word):
            letters_by_lemma[lemma.uid] = letters
    return letters_by_lemma


def _has_non_unique_words(lemmas: list[Lemma]):
    return len(lemmas) != len(set(map(lambda x: x.word, lemmas)))


def _build_crossword_grid(
    lemmas: list[Lemma], maximum_dimensions: Dimensions | None = None
):
    if _has_non_unique_words(lemmas):
        raise CrosswordError('Non-unique words detected')

    unpacked_crossword_grid = UnpackedCrosswordGrid(maximum_dimensions)
    sorted_lemmas = _sort_lemmas(lemmas)
    inserted_letters_by_lemma = _insert_lemmas(sorted_lemmas, unpacked_crossword_grid)

    packed_crossword_grid = unpacked_crossword_grid.pack()
    print(unpacked_crossword_grid.text_view())
    return CrosswordDraft(
        crossword=Crossword(
            uid=generate_uid(),
            width=packed_crossword_grid.dimensions().width,
            height=packed_crossword_grid.dimensions().height,
            solution=[
                SolvedCrosswordPuzzleWord(
                    lemma=lemma,
                    letters=inserted_letters_by_lemma[lemma.uid],
                )
                for lemma in sorted_lemmas
                if lemma.uid in inserted_letters_by_lemma
            ],
        ),
        lemmas_excluded=[
            lemma
            for lemma in sorted_lemmas
            if lemma.uid not in inserted_letters_by_lemma
        ],
    )
