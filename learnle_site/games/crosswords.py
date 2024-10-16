from abc import (
    ABC,
    abstractmethod
)
from dataclasses import dataclass
from typing import (
    Iterable,
)

from learnle_site.constants import BLOCK_CHARACTER
from learnle_site.utils import (
    Position,
    Dimensions,
    Axis,
    InfiniteGrid
)


class CrossWordsGridException(Exception):
    pass


START_POSITION = Position(0, 0)


class GridItem(ABC):

    @abstractmethod
    def is_blocked(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def position(self) -> Position:
        raise NotImplementedError

    @property
    @abstractmethod
    def text(self) -> str:
        raise NotImplementedError


class BlockedGridItem(GridItem):

    def __init__(self, position: Position):
        self._position = position

    @property
    def is_blocked(self) -> bool:
        return True

    @property
    def position(self) -> Position:
        return self._position

    @property
    def text(self) -> str:
        raise CrossWordsGridException('Blocked grid item does not have a text representation')


class LetterGridItem(GridItem):
    def __init__(self, char: str, position: Position, axis: Axis):
        self._original_axis = axis
        self._char = char
        self._position = position
        self._intersected = False
        self._colliding = False

    def __str__(self):
        return self._char.capitalize()

    @property
    def is_blocked(self) -> bool:
        return False

    @property
    def position(self) -> Position:
        return self._position

    @property
    def text(self) -> str:
        return self._char

    def mark_intersected(self):
        self._intersected = True

    def mark_colliding(self):
        self._colliding = True

    @property
    def is_intersected(self):
        return self._intersected

    @property
    def is_colliding(self):
        return self._colliding

    @property
    def original_axis(self):
        return self._original_axis

    def __repr__(self):
        return f'LetterGridItem(char={self._char}, position={self.position}, intersected={self._intersected}, colliding={self._colliding})'


@dataclass
class Word:
    text: str
    start_pos: Position
    end_pos: Position


@dataclass
class Letter:
    text: str


class CrossWordsGrid:

    def __init__(self, words: list[str] | None = None):
        self._grid = InfiniteGrid[LetterGridItem, BlockedGridItem]()
        self._words: list[Word] = []

        if not words:
            return

        self._fit_first_word(words[0], Axis.HORIZONTAL)
        for word in words[1:]:
            self._fit_word(word)

    @property
    def dimensions(self) -> Dimensions:
        return self._grid.dimensions

    def items(self) -> Iterable[GridItem]:
        return self._grid.items

    def _letter_sequence(self) -> list[LetterGridItem]:
        letters = []
        for word in self._words:
            for position in word.start_pos.to(word.end_pos):
                letters.append(self._grid[position])
        return letters

    def determine_endpoints(
            self, length: int, offset: int, reference_position: Position, axis: Axis
    ) -> tuple[Position, Position]:
        match axis:
            case Axis.HORIZONTAL:
                start_pos = reference_position.shift(x=-offset)
                end_pos = start_pos.shift(x=length - 1)
            case Axis.VERTICAL:
                start_pos = reference_position.shift(y=-offset)
                end_pos = start_pos.shift(y=length - 1)
            case _:
                raise NotImplementedError
        return start_pos, end_pos

    def _add_letters(self, start_pos: Position, end_pos: Position, word: str, axis: Axis):
        for position, new_char in zip(start_pos.to(end_pos), word):
            if position not in self._grid:
                self._grid[position] = LetterGridItem(new_char, position, axis)
        word_item = Word(word, start_pos, end_pos)
        self._words.append(word_item)

    def _is_endpoint_touching_other_words(self, start_pos: Position, end_pos: Position, insertion_axis: Axis):
        return any([
            insertion_axis == Axis.HORIZONTAL and (
                    start_pos.shift(x=-1) in self._grid or end_pos.shift() in self._grid
                ),
            insertion_axis == Axis.VERTICAL and (
                    start_pos.shift(y=-1) in self._grid or end_pos.shift() in self._grid
                )
        ])

    def _fit_first_word(self, word: str, axis: Axis):
        start_pos, end_pos = self.determine_endpoints(len(word), 0, START_POSITION, axis)
        self._add_letters(start_pos, end_pos, word, axis)

    def _fit_word(self, word: str):
        for intersecting_letter in self._letter_sequence():
            if intersecting_letter.is_intersected:
                continue

            if (intersection_index := word.find(intersecting_letter.text)) == -1:
                continue

            insertion_axis = intersecting_letter.original_axis.rotate()
            start_pos, end_pos = self.determine_endpoints(
                length=len(word),
                offset=intersection_index,
                reference_position=intersecting_letter.position,
                axis=insertion_axis,
            )
            grid_items = []
            for idx, pos in enumerate(start_pos.to(end_pos)):
                grid_items.append(LetterGridItem(word[idx], pos, insertion_axis))

            touching_positions = set()
            neighbour_positions = set()

            for item in grid_items:
                neighbour_positions.update(item.position.adjacent_positions_on_axis(insertion_axis.rotate()))
            neighbour_positions.add(start_pos.prev_by_axis(insertion_axis))
            neighbour_positions.add(end_pos.next_by_axis(insertion_axis))

            for neighbour_position in neighbour_positions:
                if neighbour_position in self._grid:
                    touching_positions.add(neighbour_position)

            would_incorrectly_intersect_other_word = False
            extra_intersections: list[LetterGridItem] = []
            for idx, pos in enumerate(start_pos.to(end_pos)):
                if pos in self._grid and pos != intersecting_letter.position:
                    extra_intersecting_letter = self._grid[pos]
                    if extra_intersecting_letter.text == word[idx]:
                        extra_intersections.append(extra_intersecting_letter)
                    else:
                        would_incorrectly_intersect_other_word = True
                        break
            if would_incorrectly_intersect_other_word:
                continue

            allowed_touching_positions = {
                intersecting_letter.position,
                *intersecting_letter.position.adjacent_positions_on_axis(insertion_axis.rotate()),

            }
            for extra_intersection in extra_intersections:
                allowed_touching_positions.update(extra_intersection.position.adjacent_positions_on_axis(insertion_axis.rotate()))

            if touching_positions - allowed_touching_positions:
                continue

            self._add_letters(start_pos, end_pos, word, insertion_axis)
            self._mark_intersections_and_collisions([intersecting_letter, *extra_intersections])
            return

    def _mark_intersections_and_collisions(self, intersecting_letters: list[LetterGridItem]):
        for intersecting_letter in intersecting_letters:
            intersecting_letter.mark_intersected()
            for adjacent_position in intersecting_letter.position.adjacent_positions():
                if adjacent_position in self._grid:
                    self._grid[adjacent_position].mark_colliding()

    def at(self, x: int, y: int) -> GridItem:
        if not self._grid or Position(x, y) not in self._grid:
            return BlockedGridItem(Position(x, y))

        return self._grid[Position(x, y)]

    def text_view(self) -> str:
        return str(self._grid)

