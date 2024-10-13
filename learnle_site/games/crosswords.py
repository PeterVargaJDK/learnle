from abc import (
    ABC,
    abstractmethod
)
from dataclasses import dataclass
from enum import (
    Enum,
    auto
)
from typing import Iterable

BLOCK_CHARACTER = '■'


class CrossWordsGridException(Exception):
    pass


# TODO huge mess
class PositionIterator:

    def __init__(self, start_pos: 'GridPosition', end_pos: 'GridPosition', exclude_pos: 'GridPosition|None' = None):
        self.start_pos = start_pos
        self._end_pos = end_pos
        self._idx = 0
        self._offset_x = 1 if start_pos.y == end_pos.y else 0
        self._offset_y = 1 if start_pos.x == end_pos.x else 0
        self._exclude_pos = exclude_pos

    def excluding(self, exclude_pos: 'GridPosition') -> 'PositionIterator':
        return PositionIterator(self.start_pos, self._end_pos, exclude_pos)

    def __iter__(self):
        return self

    def __next__(self):
        next_pos = self.start_pos.with_delta(self._idx * self._offset_x, self._idx * self._offset_y)
        if next_pos == self._exclude_pos:
            next_pos = self.start_pos.with_delta(self._idx * self._offset_x, self._idx * self._offset_y)
        if next_pos == self._end_pos:
            raise StopIteration
        self._idx += 1
        return next_pos


class Orientation(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()

    def opposite(self):
        return self.VERTICAL if self == self.HORIZONTAL else self.HORIZONTAL


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class GridPosition:
    x: int
    y: int

    def with_delta(self, x: int = 0, y: int = 0) -> 'GridPosition':
        return GridPosition(self.x + x, self.y + y)

    def to(self, other: 'GridPosition') -> PositionIterator:
        return PositionIterator(self, other)

    def adjacent_positions(self) -> list['GridPosition']:
        return [
            self.with_delta(x=-1),
            self.with_delta(x=+1),
            self.with_delta(y=-1),
            self.with_delta(y=+1),
        ]

    def neighbours_by_orientation(self, orientation: Orientation) -> set['GridPosition']:
        if orientation == orientation.HORIZONTAL:
            return {
                self.with_delta(x=-1),
                self.with_delta(x=1),
            }
        else:
            return {
                self.with_delta(y=-1),
                self.with_delta(y=1)
            }

    def next_by_orientation(self, orientation: Orientation) -> 'GridPosition':
        if orientation == orientation.HORIZONTAL:
            return self.with_delta(x=1)
        else:
            return self.with_delta(y=1)

    def prev_by_orientation(self, orientation: Orientation) -> 'GridPosition':
        if orientation == orientation.HORIZONTAL:
            return self.with_delta(x=-1)
        else:
            return self.with_delta(y=-1)


START_X = 0
START_Y = 0
START_POSITION = GridPosition(START_X, START_Y)


class GridItem(ABC):

    @abstractmethod
    def is_blocked(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def position(self) -> GridPosition:
        raise NotImplementedError

    @property
    @abstractmethod
    def text(self) -> str:
        raise NotImplementedError


class BlockedGridItem(GridItem):

    def __init__(self, position: GridPosition):
        self._position = position

    @property
    def is_blocked(self) -> bool:
        return True

    @property
    def position(self) -> GridPosition:
        return self._position

    @property
    def text(self) -> str:
        raise CrossWordsGridException('Blocked grid item does not have a text representation')


class LetterGridItem(GridItem):
    def __init__(self, char: str, position: GridPosition, orientation: Orientation):
        self._original_orientation = orientation
        self._char = char
        self._position = position
        self._intersected = False
        self._colliding = False

    @property
    def is_blocked(self) -> bool:
        return False

    @property
    def position(self) -> GridPosition:
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
    def original_orientation(self):
        return self._original_orientation

    def __repr__(self):
        return f'LetterGridItem(char={self._char}, position={self.position}, intersected={self._intersected}, colliding={self._colliding})'


@dataclass
class Word:
    text: str
    start_pos: GridPosition
    end_pos: GridPosition


class CrossWordsGrid:

    def __init__(self, words: list[str] | None = None):
        self._letters: dict[GridPosition, LetterGridItem] = {}
        self._words: list[Word] = []
        self._lowest_y = 0
        self._lowest_x = 0
        self._highest_y = 0
        self._highest_x = 0

        if not words:
            return

        self._fit_first_word(words[0], Orientation.HORIZONTAL)
        # TODO remove
        print(self.text_view())
        for word in words[1:]:
            self._fit_word(word)
            # TODO remove
            print(self.text_view())

    def _letter_sequence(self) -> list[LetterGridItem]:
        letters = []
        for word in self._words:
            for position in word.start_pos.to(word.end_pos):
                letters.append(self._letters[position])
        return letters

    def determine_endpoints(
            self, length: int, offset: int, reference_position: GridPosition, orientation: Orientation
    ) -> tuple[GridPosition, GridPosition]:
        match orientation:
            case Orientation.HORIZONTAL:
                start_pos = reference_position.with_delta(x=-offset)
                end_pos = start_pos.with_delta(x=length)
            case Orientation.VERTICAL:
                start_pos = reference_position.with_delta(y=-offset)
                end_pos = start_pos.with_delta(y=length)
            case _:
                raise NotImplementedError
        return start_pos, end_pos

    def _update_shape(self, word_item: Word):
        # TODO use max() and min()
        if word_item.start_pos.y < self._lowest_y:
            self._lowest_y = word_item.start_pos.y
        if word_item.end_pos.y > self._highest_y:
            self._highest_y = word_item.end_pos.y
        if word_item.start_pos.x < self._lowest_x:
            self._lowest_x = word_item.start_pos.x
        if word_item.end_pos.x > self._highest_x:
            self._highest_x = word_item.end_pos.x

    def _add_letters(self, start_pos: GridPosition, end_pos: GridPosition, word: str, orientation: Orientation):
        for position, new_char in zip(start_pos.to(end_pos), word):
            if position not in self._letters:
                self._letters[position] = LetterGridItem(new_char, position, orientation)
        word_item = Word(word, start_pos, end_pos)
        self._words.append(word_item)
        self._update_shape(word_item)

    def _endpoint_is_touching_other_words(self, start_pos: GridPosition, end_pos: GridPosition, insertion_orientation: Orientation):
        return any([
                insertion_orientation == Orientation.HORIZONTAL and (
                        start_pos.with_delta(x=-1) in self._letters or end_pos.with_delta() in self._letters
                ),
                insertion_orientation == Orientation.VERTICAL and (
                    start_pos.with_delta(y=-1) in self._letters or end_pos.with_delta() in self._letters
                )
        ])

    def _fit_first_word(self, word: str, orientation: Orientation):
        start_pos, end_pos = self.determine_endpoints(len(word), 0, START_POSITION, orientation)
        self._add_letters(start_pos, end_pos, word, orientation)

    def _fit_word(self, word: str):
        for intersecting_letter in self._letter_sequence():
            if intersecting_letter.is_intersected:
                continue

            if (intersection_index := word.find(intersecting_letter.text)) == -1:
                continue

            insertion_orientation = intersecting_letter.original_orientation.opposite()
            # TODO star_pos inc, end_pos exc?
            start_pos, end_pos = self.determine_endpoints(
                length=len(word),
                offset=intersection_index,
                reference_position=intersecting_letter.position,
                orientation=insertion_orientation,
            )
            grid_items = []
            for idx, pos in enumerate(start_pos.to(end_pos)):
                grid_items.append(LetterGridItem(word[idx], pos, insertion_orientation))

            touching_positions = set()
            neighbour_positions = set()

            for item in grid_items:
                neighbour_positions.update(item.position.neighbours_by_orientation(insertion_orientation.opposite()))
            neighbour_positions.add(start_pos.prev_by_orientation(insertion_orientation))
            # TODO end_pos exclusive
            neighbour_positions.add(end_pos)

            for neighbour_position in neighbour_positions:
                if neighbour_position in self._letters:
                    touching_positions.add(neighbour_position)

            would_incorrectly_intersect_other_word = False
            extra_intersections: list[LetterGridItem] = []
            for idx, pos in enumerate(start_pos.to(end_pos)):
                if pos in self._letters and pos != intersecting_letter.position:
                    extra_intersecting_letter = self._letters[pos]
                    if extra_intersecting_letter.text == word[idx]:
                        extra_intersections.append(extra_intersecting_letter)
                    else:
                        would_incorrectly_intersect_other_word = True
                        break
            if would_incorrectly_intersect_other_word:
                continue

            allowed_touching_positions = {
                intersecting_letter.position,
                *intersecting_letter.position.neighbours_by_orientation(insertion_orientation.opposite()),

            }
            for extra_intersection in extra_intersections:
                allowed_touching_positions.update(extra_intersection.position.neighbours_by_orientation(insertion_orientation.opposite()))

            if touching_positions - allowed_touching_positions:
                continue

            self._add_letters(start_pos, end_pos, word, insertion_orientation)
            self._mark_intersections_and_collisions([intersecting_letter, *extra_intersections])
            return

    def _mark_intersections_and_collisions(self, intersecting_letters: list[LetterGridItem]):
        for intersecting_letter in intersecting_letters:
            intersecting_letter.mark_intersected()
            for adjacent_position in intersecting_letter.position.adjacent_positions():
                if adjacent_position in self._letters:
                    self._letters[adjacent_position].mark_colliding()

    def at(self, x: int, y: int) -> GridItem:
        if not self._letters or GridPosition(x, y) not in self._letters:
            return BlockedGridItem(GridPosition(x, y))

        return self._letters[GridPosition(x, y)]

    def text_view(self) -> str:
        lines = []
        for y in range(self._lowest_y, self._highest_y or 1):
            line = ''
            for x in range(self._lowest_x, self._highest_x or 1):
                if (key := GridPosition(x, y)) in self._letters:
                    letter = self._letters[key]
                    text = letter.text.capitalize()
                    line += text
                else:
                    line += BLOCK_CHARACTER
            lines.append(line)
        return '\n'.join(lines)

