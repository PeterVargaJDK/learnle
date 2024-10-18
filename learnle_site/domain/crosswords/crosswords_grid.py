from abc import ABC, abstractmethod
from dataclasses import (
    dataclass,
)
from functools import cached_property
from typing import (
    Iterable,
)

from learnle_site.utils import union, Position, Dimensions, Axis, InfiniteGrid
from learnle_site.utils.grid import Shape, GridItem

_START_POSITION = Position(0, 0)


@dataclass(frozen=True, unsafe_hash=True, eq=True)
class CrosswordsLetter(GridItem):
    char: str
    position: Position

    def text_view(self):
        return self.char.capitalize()


class _CrosswordsCell(GridItem):
    def __init__(self, char: str, position: Position, axis: Axis):
        self._letter = CrosswordsLetter(char, position)
        self._original_axis = axis
        self._intersected = False

    def text_view(self):
        return self._letter.text_view()

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
            if self.cells_by_position[intersecting_position].letter
            != self.grid[intersecting_position].letter
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
    def has_not_allowed_touching_positions(self) -> bool:
        return bool(self.adjacent_positions - self.allowed_touching_positions)

    @cached_property
    def exceeds_maximum_dimensions(self) -> bool:
        if self.maximum_dimensions:
            new_shape = self.grid.shape.with_new_positions(
                self.start_position, self.end_position
            )
            return not new_shape.dimensions.fits_into(self.maximum_dimensions)
        return False


class CrossWordsGrid(ABC):
    @abstractmethod
    def at(self, x: int, y: int) -> CrosswordsLetter | None:
        raise NotImplementedError

    @abstractmethod
    def letters(self) -> Iterable[CrosswordsLetter]:
        raise NotImplementedError

    @abstractmethod
    def dimensions(self) -> Dimensions:
        raise NotImplementedError

    @abstractmethod
    def text_view(self) -> str:
        raise NotImplementedError


class UnpackedCrosswordsGrid:
    """
    Represents a crosswords grid that can scale infinitely in every dimension, limited by the specified maximum
    dimensions. This grid is therefore unpacked, it does not represent a ready crosswords puzzle.
    """

    def __init__(self, maximum_dimensions: Dimensions | None = None):
        """
        Creates an empty unpacked crosswords grid. By default, there is no maximum width and height specified,
        the grid can grow infinitely in every dimension.
        :param maximum_dimensions: the maximum width and height of the grid.
        """
        self._grid = InfiniteGrid[_CrosswordsCell]()
        self._maximum_dimensions = maximum_dimensions

    def add_word(self, word: str) -> bool:
        """
        Attempts to fit a new word into the grid.
        :param word: The string that you want to insert into the grid
        :return: True, if the word was successfully inserted, False otherwise
        """
        if not self._grid:
            return self._fit_first_word(word, Axis.HORIZONTAL)
        return self._fit_additional_word(word)

    def text_view(self) -> str:
        """
        Creates a human-readable string representation of the grid. It does not contain position information,
        indices or dimensions.
        :return: String representing the state of the grid
        """
        return str(self._grid)

    @property
    def dimensions(self) -> Dimensions:
        """
        :return: The width and height of the grid.
        """
        return self._grid.dimensions

    @property
    def shape(self) -> Shape:
        """
        :return: The Shape object that describes the dimensions and index ranges
        """
        return self._grid.shape

    @property
    def cells(self) -> Iterable[_CrosswordsCell]:
        """
        :return: An iterable of cells
        """
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
                    possible_insertion.has_not_allowed_touching_positions,
                ]
            ):
                continue

            self._add_letters(possible_insertion.cells)
            for intersecting_letter in possible_insertion.intersecting_positions:
                self._grid[intersecting_letter].mark_intersected()
            return True
        return False


class PackedCrosswordsGrid(CrossWordsGrid):
    def __init__(self, infinite_grid: UnpackedCrosswordsGrid):
        self._grid = InfiniteGrid[CrosswordsLetter]()

        # min_x and min_y cannot be positive
        min_x, min_y = infinite_grid.shape.min_x, infinite_grid.shape.min_y
        offset_x = abs(min_x) if min_x < 0 else 0
        offset_y = abs(min_y) if min_y < 0 else 0

        for cell in infinite_grid.cells:
            packed_position = cell.position.shift(offset_x, offset_y)
            self._grid[packed_position] = CrosswordsLetter(
                cell.letter.char, packed_position
            )

    def at(self, x: int, y: int) -> CrosswordsLetter | None:
        return self._grid[Position(x, y)]

    def letters(self) -> Iterable[CrosswordsLetter]:
        return self._grid.items

    def text_view(self) -> str:
        return str(self._grid)

    def dimensions(self) -> Dimensions:
        return self._grid.dimensions
