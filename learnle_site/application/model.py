from functools import cached_property
from itertools import chain

from pydantic import (
    BaseModel,
)

from learnle_site.datatypes import Position


class Lemma(BaseModel, frozen=True):
    uid: str
    word: str
    definition: str
    example: str


class CrosswordPuzzleLetter(BaseModel, frozen=True):
    character: str
    position: Position


class SolvedCrosswordPuzzleWord(BaseModel, frozen=True):
    lemma: Lemma
    letters: list[CrosswordPuzzleLetter]


class Crossword(BaseModel, frozen=True):
    uid: str
    width: int
    height: int
    solution: list[SolvedCrosswordPuzzleWord]

    @cached_property
    def solution_letters(self) -> list[CrosswordPuzzleLetter]:
        return list(chain(*map(lambda x: x.letters, self.solution)))


class CrosswordPuzzle(Crossword, frozen=True):
    shuffled_state: list[CrosswordPuzzleLetter]


class CrosswordDraft(BaseModel, frozen=True):
    crossword: Crossword
    lemmas_excluded: set[Lemma]
