from random import shuffle
from typing import Iterable

from learnle_site.application.model import (
    CrosswordsPuzzleLetter,
    SolvedCrosswordsPuzzleWord,
    CrosswordsPuzzle,
)

from learnle_site.application.words import LemmaDatabaseAdapter
from learnle_site.utils.crosswords_grid import UnpackedCrosswordsGrid


def _get_shuffled_characters(letters: Iterable[CrosswordsPuzzleLetter]):
    characters = [letter.character for letter in letters]
    shuffle(characters)
    return characters


async def random_crosswords_puzzle(
    lemma_database: LemmaDatabaseAdapter,
) -> CrosswordsPuzzle:
    random_lemmas = await lemma_database.random_lemmas()
    unpacked_crosswords_grid = UnpackedCrosswordsGrid()

    inserted_lemmas: dict[str, list[CrosswordsPuzzleLetter]] = {}
    for random_lemma in random_lemmas:
        inserted_lemmas[random_lemma.uid] = unpacked_crosswords_grid.add_word(
            random_lemma.word
        )

    packed_crosswords_grid = unpacked_crosswords_grid.pack()
    letters = packed_crosswords_grid.letters()
    shuffled_characters = _get_shuffled_characters(letters)

    return CrosswordsPuzzle(
        width=packed_crosswords_grid.dimensions().width,
        height=packed_crosswords_grid.dimensions().height,
        shuffled_state=[
            CrosswordsPuzzleLetter(character=character, position=letter.position)
            for letter, character in zip(letters, shuffled_characters)
        ],
        solution=[
            SolvedCrosswordsPuzzleWord(
                lemma=lemma,
                letters=inserted_lemmas[lemma.uid],
            )
            for lemma in random_lemmas
        ],
    )
