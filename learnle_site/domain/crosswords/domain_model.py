from pydantic import BaseModel


class Letter(BaseModel, frozen=True):
    x: int
    y: int
    character: str
    word: str


class Word(BaseModel, frozen=True):
    text: str
    definition: str
    example: str


class CrosswordsPuzzle(BaseModel, frozen=True):
    uuid: str
    width: int
    height: int
    letters: list[Letter]
    words: list[Word]
