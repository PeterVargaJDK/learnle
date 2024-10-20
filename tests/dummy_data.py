from typing import TypeVar

from faker import Faker
from pydantic import BaseModel

from learnle_site.application.model import (
    Lemma,
    Crossword,
    SolvedCrosswordPuzzleWord,
    CrosswordPuzzleLetter,
)
from learnle_site.datatypes import Position

faker = Faker()

T = TypeVar('T', bound=BaseModel)


def dummy_string():
    return faker.text(10)


def dummy_lemma(
    uid: str | None = None,
    word: str | None = None,
    definition: str | None = None,
    example: str | None = None,
) -> Lemma:
    return Lemma(
        uid=uid or str(faker.uuid4()),
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


def dummy_crossword_puzzle_word() -> SolvedCrosswordPuzzleWord:
    return SolvedCrosswordPuzzleWord(lemma=dummy_lemma(), letters=dummy_letters())


def dummy_crossword() -> Crossword:
    return Crossword(
        uid=str(faker.uuid4()),
        width=faker.random_int(max=10),
        height=faker.random_int(max=10),
        solution=[
            dummy_crossword_puzzle_word() for _ in range(faker.random_int(min=3, max=10))
        ],
    )
