from dataclasses import (
    dataclass,
)
from functools import cached_property
from typing import (
    Iterable,
)

from learnle_site.utils import union, Position, Dimensions, Axis, InfiniteGrid
from learnle_site.utils.grid import Shape


class CrossWordsGridException(Exception):
    pass


_START_POSITION = Position(0, 0)


@dataclass(frozen=True, unsafe_hash=True, eq=True)
class CrosswordsLetter:
    char: str
    position: Position


class _CrosswordsCell:
    def __init__(self, char: str, position: Position, axis: Axis):
        self._letter = CrosswordsLetter(char, position)
        self._original_axis = axis
        self._intersected = False

    def __str__(self):
        return self._letter.char.capitalize()

    def __eq__(self, other):
        if not isinstance(other, _CrosswordsCell):
            return False
        return self._letter == other._letter

    def __hash__(self) -> int:
        return hash(self._letter)

    @property
    def position(self) -> Position:
        return self._letter.position

    @property
    def letter(self) -> CrosswordsLetter:
        return self._letter

    def mark_intersected(self):
        self._intersected = True

    @property
    def is_already_intersected(self):
        return self._intersected

    @property
    def axis(self):
        return self._original_axis

    def __repr__(self):
        return (
            'CrosswordsCell('
            f'letter={self._letter}, '
            f'intersected={self._intersected}, '
            f'original_axis={self._original_axis}'
            ')'
        )


@dataclass(frozen=True)
class _WordInsertion:
    word: str
    start_position: Position
    end_position: Position
    axis: Axis
    grid: InfiniteGrid[_CrosswordsCell]
    maximum_dimensions: Dimensions | None

    @cached_property
    def cells_by_position(self) -> dict[Position, _CrosswordsCell]:
        return {
            letter_position: _CrosswordsCell(char, letter_position, self.axis)
            for letter_position, char in zip(
                self.start_position.to(self.end_position), self.word
            )
        }

    @cached_property
    def cells(self) -> Iterable[_CrosswordsCell]:
        return self.cells_by_position.values()

    @cached_property
    def adjacent_positions(self) -> set[Position]:
        return {
            position
            for position in union(
                [
                    letter.position.adjacent_positions_on_axis(self.axis.rotate())
                    for letter in self.cells
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
    def intersecting_positions(self) -> set[Position]:
        return {cell.position for cell in self.cells if cell.position in self.grid}

    @cached_property
    def incorrect_intersecting_positions(self) -> set[Position]:
        return {
            intersecting_position
            for intersecting_position in self.intersecting_positions
            # TODO .letter without .char
            if self.cells_by_position[intersecting_position].letter.char
            != self.grid[intersecting_position].letter.char
        }

    @cached_property
    def has_incorrect_intersections(self) -> bool:
        return bool(self.incorrect_intersecting_positions)

    @cached_property
    def allowed_touching_positions(self) -> set[Position]:
        return {
            allowed_touching_position
            for allowed_touching_position in union(
                [
                    intersecting_position.adjacent_positions_on_axis(
                        self.grid[intersecting_position].axis
                    )
                    for intersecting_position in self.intersecting_positions
                ]
            )
            if allowed_touching_position in self.grid
        }

    @cached_property
    def has_not_allowed_touching_letters(self) -> bool:
        return bool(self.adjacent_positions - self.allowed_touching_positions)

    @cached_property
    def exceeds_maximum_dimensions(self) -> bool:
        if self.maximum_dimensions:
            new_shape = self.grid.shape.with_new_positions(
                self.start_position, self.end_position
            )
            return not new_shape.dimensions.fits_into(self.maximum_dimensions)
        return False


class CrossWordsGrid:
    def __init__(self, maximum_dimensions: Dimensions | None = None):
        self._grid = InfiniteGrid[_CrosswordsCell]()
        self._maximum_dimensions = maximum_dimensions

    def add_word(self, word: str) -> bool:
        if not self._grid:
            return self._fit_first_word(word, Axis.HORIZONTAL)
        return self._fit_additional_word(word)

    def at(self, x: int, y: int) -> _CrosswordsCell | None:
        return self._grid[Position(x, y)]

    def text_view(self) -> str:
        return str(self._grid)

    @property
    def dimensions(self) -> Dimensions:
        return self._grid.dimensions

    @property
    def shape(self) -> Shape:
        return self._grid.shape

    @property
    def cells(self) -> Iterable[_CrosswordsCell]:
        return self._grid.items

    def _add_letters(self, letters: Iterable[_CrosswordsCell]):
        for letter in letters:
            self._grid[letter.position] = letter

    def _possible_insertions(self, word: str):
        for cell in self._grid.items:
            if cell.is_already_intersected or cell.letter.char not in word:
                continue
            insertion_axis = cell.axis.rotate()
            for char_index, char in enumerate(word):
                if char == cell.letter.char:
                    start_pos, end_pos = cell.position.line(
                        len(word), insertion_axis, offset=char_index
                    )
                    yield _WordInsertion(
                        word=word,
                        start_position=start_pos,
                        end_position=end_pos,
                        axis=insertion_axis,
                        grid=self._grid,
                        maximum_dimensions=self._maximum_dimensions,
                    )

    def _fit_first_word(self, word: str, axis: Axis) -> bool:
        start_position, end_position = _START_POSITION.line(len(word), axis)
        insertion = _WordInsertion(
            word,
            start_position,
            end_position,
            axis,
            self._grid,
            self._maximum_dimensions,
        )
        self._add_letters(insertion.cells)
        return True

    def _fit_additional_word(self, word: str) -> bool:
        for possible_insertion in self._possible_insertions(word):
            if any(
                [
                    possible_insertion.exceeds_maximum_dimensions,
                    possible_insertion.has_incorrect_intersections,
                    possible_insertion.has_not_allowed_touching_letters,
                ]
            ):
                continue

            self._add_letters(possible_insertion.cells)
            for intersecting_letter in possible_insertion.intersecting_positions:
                self._grid[intersecting_letter].mark_intersected()
            return True
        return False
