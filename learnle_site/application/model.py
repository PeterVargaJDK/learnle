from pydantic import BaseModel

from learnle_site.datatypes import Position


class Lemma(BaseModel):
    uid: str
    word: str
    definition: str
    example: str


class CrosswordsPuzzleLetter(BaseModel, frozen=True):
    character: str
    position: Position


class SolvedCrosswordsPuzzleWord(BaseModel, frozen=True):
    lemma: Lemma
    letters: list[CrosswordsPuzzleLetter]


class CrosswordsPuzzle(BaseModel, frozen=True):
    width: int
    height: int
    shuffled_state: list[CrosswordsPuzzleLetter]
    solution: list[SolvedCrosswordsPuzzleWord]
