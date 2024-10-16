from dataclasses import (
    dataclass,
)
from functools import cached_property
from typing import (
    Iterable,
)

from learnle_site.utils import Position, Dimensions, Axis, InfiniteGrid, union


class CrossWordsGridException(Exception):
    pass


_START_POSITION = Position(0, 0)


class Letter:
    def __init__(self, char: str, position: Position, axis: Axis):
        self._char = char
        self._position = position
        # TODO: These two fields are not really part of the class, they are control params, should not be here
        self._original_axis = axis
        self._intersected = False

    def __str__(self):
        return self._char.capitalize()

    def __eq__(self, other):
        if not isinstance(other, Letter):
            return False
        return all(
            [
                self._char == other._char,
                self._position == other._position,
            ]
        )

    def __hash__(self) -> int:
        return hash(self._char) + hash(self._position)

    @property
    def position(self) -> Position:
        return self._position

    @property
    def text(self) -> str:
        return self._char

    def mark_intersected(self):
        self._intersected = True

    @property
    def is_already_intersected(self):
        return self._intersected

    @property
    def axis(self):
        return self._original_axis

    def __repr__(self):
        return f'Letter(char={self._char}, position={self.position}, intersected={self._intersected})'


@dataclass(frozen=True)
class _WordInsertion:
    word: str
    start_position: Position
    end_position: Position
    axis: Axis
    grid: InfiniteGrid

    @cached_property
    def letters_by_position(self) -> dict[Position, Letter]:
        return {
            letter_position: Letter(char, letter_position, self.axis)
            for letter_position, char in zip(
                self.start_position.to(self.end_position), self.word
            )
        }

    @cached_property
    def letters(self) -> Iterable[Letter]:
        return self.letters_by_position.values()

    @cached_property
    def adjacent_letters(self) -> set[Letter]:
        return {
            self.grid[position]
            for position in union(
                [
                    letter.position.adjacent_positions_on_axis(self.axis.rotate())
                    for letter in self.letters
                ]
                + [
                    {
                        self.start_position.prev_by_axis(self.axis),
                        self.end_position.next_by_axis(self.axis),
                    }
                ]
            )
            if position in self.grid
        }

    @cached_property
    def intersections(self) -> set[Letter]:
        return {
            self.grid[letter.position]
            for letter in self.letters
            if letter.position in self.grid
        }

    @cached_property
    def incorrect_intersections(self) -> set[Letter]:
        return {
            intersection
            for intersection in self.intersections
            if self.letters_by_position[intersection.position].text != intersection.text
        }

    @cached_property
    def has_incorrect_intersections(self) -> bool:
        return bool(self.incorrect_intersections)

    @cached_property
    def allowed_touching_letters(self) -> set[Letter]:
        return {
            self.grid[allowed_touching_position]
            for allowed_touching_position in union(
                [
                    intersection.position.adjacent_positions_on_axis(intersection.axis)
                    for intersection in self.intersections
                ]
            )
            if allowed_touching_position in self.grid
        }

    @cached_property
    def has_not_allowed_touching_letters(self) -> bool:
        return bool(self.adjacent_letters - self.allowed_touching_letters)


class CrossWordsGrid:
    def __init__(self):
        self._grid = InfiniteGrid[Letter]()

    def add_word(self, word: str) -> bool:
        if not self._grid:
            return self._fit_first_word(word, Axis.HORIZONTAL)
        return self._fit_additional_word(word)

    def at(self, x: int, y: int) -> Letter | None:
        return self._grid[Position(x, y)]

    def text_view(self) -> str:
        return str(self._grid)

    @property
    def dimensions(self) -> Dimensions:
        return self._grid.dimensions

    def _add_letters(self, letters: Iterable[Letter]):
        for letter in letters:
            self._grid[letter.position] = letter

    def _possible_insertions(self, word: str):
        for letter in self._grid.items:
            if letter.is_already_intersected or letter.text not in word:
                continue
            insertion_axis = letter.axis.rotate()
            for char_index, char in enumerate(word):
                if char == letter.text:
                    start_pos, end_pos = letter.position.line(
                        len(word), insertion_axis, offset=char_index
                    )
                    yield _WordInsertion(
                        word=word,
                        start_position=start_pos,
                        end_position=end_pos,
                        axis=insertion_axis,
                        grid=self._grid,
                    )

    def _fit_first_word(self, word: str, axis: Axis) -> bool:
        start_position, end_position = _START_POSITION.line(len(word), axis)
        insertion = _WordInsertion(word, start_position, end_position, axis, self._grid)
        self._add_letters(insertion.letters)
        return True

    def _fit_additional_word(self, word: str) -> bool:
        for possible_insertion in self._possible_insertions(word):
            if any(
                [
                    possible_insertion.has_incorrect_intersections,
                    possible_insertion.has_not_allowed_touching_letters,
                ]
            ):
                continue

            self._add_letters(possible_insertion.letters)
            for intersecting_letter in possible_insertion.intersections:
                intersecting_letter.mark_intersected()
            return True
        return False
