from dataclasses import dataclass
from functools import cached_property
from typing import Iterable, Generic, TypeVar, OrderedDict, Callable

from learnle_site.application.model import CrosswordsPuzzleLetter
from learnle_site.datatypes import Dimensions, Position, Shape, Axis

from learnle_site.constants import BLOCK_CHARACTER, NEW_LINE
from learnle_site.utils import union

R = TypeVar('R')


class InfiniteGrid(Generic[R]):
    def __init__(self, item_to_text_converter: Callable[[R], str] = str):
        self._items = OrderedDict[Position, R]()
        self._shape = Shape()
        self._item_to_text = item_to_text_converter

    def __setitem__(self, position: Position, item: R):
        self._items[position] = item
        self._shape.update_shape_with_new_position(position)

    def __getitem__(self, position: Position) -> R:
        return self._items[position]

    def __contains__(self, item: Position) -> bool:
        return item in self._items

    @property
    def items(self) -> Iterable[R]:
        return self._items.values()

    @property
    def dimensions(self) -> Dimensions:
        return self._shape.dimensions

    @property
    def shape(self):
        return self._shape

    def __str__(self):
        lines = []
        for y in self._shape.vertical_indices:
            line = ''
            for x in self._shape.horizontal_indices:
                item = self._items.get(Position(x, y))
                line += self._item_to_text(item) if item else BLOCK_CHARACTER
            lines.append(line)
        return NEW_LINE.join(lines)

    def __len__(self):
        return len(self._items)

    def __bool__(self):
        return bool(len(self))


_START_POSITION = Position(0, 0)


@dataclass
class _CrosswordsCell:
    letter: CrosswordsPuzzleLetter
    axis: Axis
    is_intersected: bool = False

    @property
    def position(self):
        return self.letter.position

    def mark_intersected(self):
        self.is_intersected = True


@dataclass(frozen=True)
class _Insertion:
    word: str
    start_position: Position
    end_position: Position
    axis: Axis
    grid: InfiniteGrid[_CrosswordsCell]
    maximum_dimensions: Dimensions | None

    @cached_property
    def letters(self) -> list[CrosswordsPuzzleLetter]:
        return [
            CrosswordsPuzzleLetter(character=char, position=letter_position)
            for letter_position, char in zip(
                self.start_position.to(self.end_position), self.word
            )
        ]

    @cached_property
    def cells_by_position(self) -> dict[Position, _CrosswordsCell]:
        return {
            letter.position: _CrosswordsCell(letter, self.axis)
            for letter in self.letters
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
        self._grid = InfiniteGrid[_CrosswordsCell](
            item_to_text_converter=lambda x: x.letter.character.capitalize()
        )
        self._maximum_dimensions = maximum_dimensions

    def add_word(self, word: str) -> list[CrosswordsPuzzleLetter]:
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
            if cell.is_intersected or cell.letter.character not in word:
                continue
            insertion_axis = cell.axis.rotate()
            for char_index, char in enumerate(word):
                if char == cell.letter.character:
                    start_pos, end_pos = cell.position.line(
                        len(word), insertion_axis, offset=char_index
                    )
                    yield _Insertion(
                        word=word,
                        start_position=start_pos,
                        end_position=end_pos,
                        axis=insertion_axis,
                        grid=self._grid,
                        maximum_dimensions=self._maximum_dimensions,
                    )

    def _fit_first_word(
        self, word: str, starting_axis: Axis
    ) -> list[CrosswordsPuzzleLetter]:
        start_position, end_position = _START_POSITION.line(len(word), starting_axis)
        insertion = _Insertion(
            word=word,
            start_position=start_position,
            end_position=end_position,
            axis=starting_axis,
            grid=self._grid,
            maximum_dimensions=self._maximum_dimensions,
        )
        self._add_letters(insertion.cells)
        return insertion.letters

    def _fit_additional_word(self, word: str) -> list[CrosswordsPuzzleLetter]:
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
            return possible_insertion.letters
        return []

    def pack(self) -> 'PackedCrosswordsGrid':
        return PackedCrosswordsGrid(self)


class PackedCrosswordsGrid:
    def __init__(self, infinite_grid: UnpackedCrosswordsGrid):
        self._grid = InfiniteGrid[CrosswordsPuzzleLetter](
            item_to_text_converter=lambda x: x.character.capitalize()
        )

        # min_x and min_y cannot be positive
        min_x, min_y = infinite_grid.shape.min_x, infinite_grid.shape.min_y
        offset_x = abs(min_x) if min_x < 0 else 0
        offset_y = abs(min_y) if min_y < 0 else 0

        for cell in infinite_grid.cells:
            packed_position = cell.position.shift(offset_x, offset_y)
            self._grid[packed_position] = CrosswordsPuzzleLetter(
                character=cell.letter.character, position=packed_position
            )

    def letters(self) -> Iterable[CrosswordsPuzzleLetter]:
        return self._grid.items

    def dimensions(self) -> Dimensions:
        return self._grid.dimensions
