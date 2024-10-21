from faker import Faker

from learnle_site.application.model import (
    Lemma,
    Crossword,
    SolvedCrosswordPuzzleWord,
    CrosswordPuzzleLetter,
)
from learnle_site.datatypes import Position


class fake:
    _FAKERS: dict[int | None, Faker] = {}

    def __init__(self, seed: int | None = None):
        if seeded_faker := self._FAKERS.get(seed):
            self._faker = seeded_faker
        else:
            self._faker = Faker()
            self._FAKERS[seed] = self._faker
        if seed is not None:
            self._faker.seed_instance(seed)

    def uid(self) -> str:
        return str(self._faker.uuid4())

    def position(self) -> Position:
        return Position(self._faker.random_int(10), self._faker.random_int(10))

    def letters(self) -> list[CrosswordPuzzleLetter]:
        return [
            CrosswordPuzzleLetter(character=char, position=self.position())
            for char in self._faker.word()
        ]

    def crossword_puzzle_word(
        self,
        lemma: Lemma | None = None,
        letters: list[CrosswordPuzzleLetter] | None = None,
    ) -> SolvedCrosswordPuzzleWord:
        return SolvedCrosswordPuzzleWord(
            lemma=lemma or self.lemma(), letters=letters or self.letters()
        )

    def crossword(
        self, solution: list[SolvedCrosswordPuzzleWord] | None = None
    ) -> Crossword:
        return Crossword(
            uid=self.uid(),
            width=self._faker.random_int(max=10),
            height=self._faker.random_int(max=10),
            solution=solution
            if solution is not None
            else [
                self.crossword_puzzle_word()
                for _ in range(self._faker.random_int(min=3, max=10))
            ],
        )

    def lemma(
        self,
        uid: str | None = None,
        word: str | None = None,
        definition: str | None = None,
        example: str | None = None,
    ) -> Lemma:
        return Lemma(
            uid=uid or self.uid(),
            word=word or self._faker.word(),
            definition=definition or self._faker.bs(),
            example=example or self._faker.bs(),
        )
