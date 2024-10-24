from faker import Faker

from learnle.application.model import (
    Lemma,
    Crossword,
    SolvedCrosswordPuzzleWord,
    CrosswordPuzzleLetter,
)
from learnle.datatypes import Position

faker = Faker()


def dummy_string() -> str:
    return faker.text(10)


def dummy_uid() -> str:
    return str(faker.uuid4())


def dummy_lemma(
    uid: str | None = None,
    word: str | None = None,
    definition: str | None = None,
    example: str | None = None,
) -> Lemma:
    return Lemma(
        uid=uid or dummy_uid(),
        word=word or faker.word(),
        definition=definition or faker.bs(),
        example=example or faker.bs(),
    )


def dummy_lemmas(size: int = 5) -> list[Lemma]:
    return [dummy_lemma() for _ in range(size)]


def dummy_position() -> Position:
    return Position(faker.random_int(10), faker.random_int(10))


def dummy_letters() -> list[CrosswordPuzzleLetter]:
    return [
        CrosswordPuzzleLetter(character=char, position=dummy_position())
        for char in faker.word()
    ]


def dummy_crossword_puzzle_word(
    lemma: Lemma | None = None, letters: list[CrosswordPuzzleLetter] | None = None
) -> SolvedCrosswordPuzzleWord:
    return SolvedCrosswordPuzzleWord(
        lemma=lemma or dummy_lemma(), letters=letters or dummy_letters()
    )


def dummy_crossword(
    solution: list[SolvedCrosswordPuzzleWord] | None = None,
) -> Crossword:
    return Crossword(
        uid=dummy_uid(),
        width=faker.random_int(max=10),
        height=faker.random_int(max=10),
        solution=solution
        or [
            dummy_crossword_puzzle_word()
            for _ in range(faker.random_int(min=3, max=10))
        ],
    )


def dummy_crosswords(size: int = 5) -> list[Crossword]:
    return [dummy_crossword() for _ in range(size)]
