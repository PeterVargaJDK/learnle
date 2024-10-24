from functools import cached_property
from itertools import chain

from pydantic import (
    BaseModel,
)

from learnle.datatypes import Position


class Lemma(BaseModel):
    uid: str
    word: str
    definition: str
    example: str


class CrosswordPuzzleLetter(BaseModel):
    character: str
    position: Position


class SolvedCrosswordPuzzleWord(BaseModel):
    lemma: Lemma
    letters: list[CrosswordPuzzleLetter]


class Crossword(BaseModel):
    uid: str
    width: int
    height: int
    solution: list[SolvedCrosswordPuzzleWord]

    @cached_property
    def solution_letters(self) -> list[CrosswordPuzzleLetter]:
        return list(chain(*map(lambda x: x.letters, self.solution)))


class CrosswordPuzzle(Crossword):
    shuffled_state: list[CrosswordPuzzleLetter]


class CrosswordDraft(BaseModel):
    crossword: Crossword
    lemmas_excluded: list[Lemma]
