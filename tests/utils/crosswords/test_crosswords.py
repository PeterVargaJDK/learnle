from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Generator, Iterable

import pytest

BLOCK_CHARACTER = '■'


class CrossWordsGridException(Exception):
    pass


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class GridPosition:
    x: int
    y: int

    def with_delta(self, x: int = 0, y: int = 0) -> 'GridPosition':
        return GridPosition(self.x + x, self.y + y)

    def to(self, other: 'GridPosition') -> Iterable['GridPosition']:
        if self.x == other.x:
            for i in range(self.y, other.y):
                yield GridPosition(self.x, i)
        if self.y == other.y:
            for i in range(self.x, other.x):
                yield GridPosition(i, self.y)


class GridItem(ABC):

    @abstractmethod
    def is_blocked(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def position(self) -> GridPosition:
        raise NotImplementedError

    @abstractmethod
    def text(self) -> str:
        raise NotImplementedError


class BlockedGridItem(GridItem):

    def __init__(self, position: GridPosition):
        self._position = position

    def is_blocked(self) -> bool:
        return True

    def position(self) -> GridPosition:
        return self._position

    def text(self) -> str:
        raise CrossWordsGridException('Blocked grid item does not have a text representation')


class LetterGridItem(GridItem):
    def __init__(self, char: str, position: GridPosition):
        self._char = char
        self._position = position
        self._used = False

    def is_blocked(self) -> bool:
        return False

    def position(self) -> GridPosition:
        return self._position

    def text(self) -> str:
        return self._char

    def mark_used(self):
        self._used = True

    def is_used(self):
        return self._used


START_X = 0
START_Y = 0
START_POSITION = GridPosition(START_X, START_Y)


class Orientation(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()


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

        # if words:
        #     for word in words:
        #         if not self._letters:
        #             x = START_X
        #             for char in word:
        #                 self._letters[GridPosition(x, START_Y)] = LetterGridItem(char, GridPosition(x, START_Y))
        #                 x += 1
        #             self._highest_x = x
        #             self._words.append(Word(
        #                 text=word,
        #                 start_pos=GridPosition(START_X, START_Y),
        #                 end_pos=GridPosition(START_X + len(word), START_Y)
        #             ))
        #         else:
        #             for idx, char in enumerate(word):
        #                 longest_word = self._words[0]
        #                 common_letter_idx = longest_word.text.find(char)
        #                 if common_letter_idx == -1:
        #                     continue
        #                 start_pos = GridPosition(longest_word.start_pos.x + common_letter_idx, longest_word.start_pos.y - idx)
        #                 end_pos = GridPosition(start_pos.x, start_pos.y + len(word))
        #                 self._words.append(Word(
        #                     text=word,
        #                     start_pos=start_pos,
        #                     end_pos=end_pos
        #                 ))
        #                 for y, char_2 in zip(range(start_pos.y, end_pos.y), word):
        #                     self._letters[GridPosition(start_pos.x, y)] = LetterGridItem(char_2, GridPosition(start_pos.x, y))
        #                 self._lowest_y = start_pos.y
        #                 self._highest_y = end_pos.y
        #                 break

        if not words:
            return

        self._first_word(words[0], Orientation.HORIZONTAL)
        for word in words[1:]:
            self._fit_word(word, orientation=Orientation.VERTICAL)

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
        if word_item.start_pos.y < self._lowest_y:
            self._lowest_y = word_item.start_pos.y
        if word_item.end_pos.y > self._highest_y:
            self._highest_y = word_item.end_pos.y
        if word_item.start_pos.x < self._lowest_x:
            self._lowest_x = word_item.start_pos.x
        if word_item.end_pos.x > self._highest_x:
            self._highest_x = word_item.end_pos.x

    def _first_word(self, word: str, orientation: Orientation):
        start_pos, end_pos = self.determine_endpoints(len(word), 0, START_POSITION, orientation)
        self._add_letters(end_pos, start_pos, word)

    def _add_letters(self, end_pos: GridPosition, start_pos: GridPosition, word: str):
        for position, new_char in zip(start_pos.to(end_pos), word):
            if position not in self._letters:
                self._letters[position] = LetterGridItem(new_char, position)
        word_item = Word(word, start_pos, end_pos)
        self._words.append(word_item)
        self._update_shape(word_item)
        print(self)

    def _fit_word(self, word: str, orientation: Orientation):
        for intersecting_letter in self._letter_sequence():
            if intersecting_letter.is_used():
                continue

            if (intersection_index := word.find(intersecting_letter.text())) == -1:
                continue

            start_pos, end_pos = self.determine_endpoints(len(word), intersection_index, intersecting_letter.position(),
                                                          orientation)
            self._add_letters(end_pos, start_pos, word)
            intersecting_letter.mark_used()
            return

    def at(self, x: int, y: int) -> GridItem:
        if not self._letters or GridPosition(x, y) not in self._letters:
            return BlockedGridItem(GridPosition(x, y))

        return self._letters[GridPosition(x, y)]

    def __repr__(self):
        result = ''
        for y in range(self._lowest_y, self._highest_y or 1):
            for x in range(self._lowest_x, self._highest_x or 1):
                if (key := GridPosition(x, y)) in self._letters:
                    result += self._letters[key].text()
                else:
                    result += BLOCK_CHARACTER
            result += '\n'
        return result


def assert_letter_grid_item(grid: CrossWordsGrid, character: str, x: int, y: int):
    grid_item = grid.at(x, y)
    assert not grid_item.is_blocked()
    assert grid_item.position() == GridPosition(x, y)
    assert grid_item.text() == character


def assert_blocked_grid_item(grid: CrossWordsGrid, x: int, y: int):
    grid_item = grid.at(x, y)
    assert grid_item.is_blocked()
    assert grid_item.position() == GridPosition(x, y)
    with pytest.raises(CrossWordsGridException):
        grid_item.text()


def test_empty_grid():
    grid = CrossWordsGrid()
    assert_blocked_grid_item(grid, START_X, START_Y)


def test_one_char_word():
    grid = CrossWordsGrid(['a'])
    print(grid)
    assert_letter_grid_item(grid, 'a', START_X, START_Y)
    assert_blocked_grid_item(grid, START_X + 1, START_Y)


def test_two_char_word():
    grid = CrossWordsGrid(['ab'])
    assert_letter_grid_item(grid, 'a', START_X, START_Y)
    assert_letter_grid_item(grid, 'b', START_X + 1, START_Y)
    print(grid)


def test_two_words_same_length__first_letter_in_common():
    grid = CrossWordsGrid(['dig', 'dry'])
    print(f'\n{grid}')
    assert_letter_grid_item(grid, 'd', START_X, START_Y)
    assert_letter_grid_item(grid, 'i', START_X + 1, START_Y)
    assert_letter_grid_item(grid, 'g', START_X + 2, START_Y)
    assert_letter_grid_item(grid, 'r', START_X, START_Y + 1)
    assert_letter_grid_item(grid, 'y', START_X, START_Y + 2)


def test_two_words_same_length__second_letter_in_common():
    grid = CrossWordsGrid(['dig', 'odd'])
    print(f'\n{grid}')
    assert_letter_grid_item(grid, 'd', START_X, START_Y)
    assert_letter_grid_item(grid, 'i', START_X + 1, START_Y)
    assert_letter_grid_item(grid, 'g', START_X + 2, START_Y)
    assert_letter_grid_item(grid, 'o', START_X, START_Y - 1)
    assert_letter_grid_item(grid, 'd', START_X, START_Y + 1)


def test_two_words_same_length__last_letter_in_common():
    grid = CrossWordsGrid(['dig', 'rug'])
    print(f'\n{grid}')
    assert_letter_grid_item(grid, 'd', START_X, START_Y)
    assert_letter_grid_item(grid, 'i', START_X + 1, START_Y)
    assert_letter_grid_item(grid, 'g', START_X + 2, START_Y)
    assert_letter_grid_item(grid, 'r', START_X + 2, START_Y - 2)
    assert_letter_grid_item(grid, 'u', START_X + 2, START_Y - 1)
    assert_letter_grid_item(grid, 'g', START_X + 2, START_Y)


def test_three_words__two_words_share_a_character():
    grid = CrossWordsGrid(['doggy', 'ding', 'trudge'])
    print(f'\n{grid}')
    assert_letter_grid_item(grid, 'd', START_X, START_Y)
    assert_letter_grid_item(grid, 'o', START_X + 1, START_Y)
    assert_letter_grid_item(grid, 'g', START_X + 2, START_Y)
    assert_letter_grid_item(grid, 'g', START_X + 3, START_Y)
    assert_letter_grid_item(grid, 'y', START_X + 4, START_Y)

    assert_letter_grid_item(grid, 'd', START_X, START_Y)
    assert_letter_grid_item(grid, 'i', START_X, START_Y + 1)
    assert_letter_grid_item(grid, 'n', START_X, START_Y + 2)
    assert_letter_grid_item(grid, 'g', START_X, START_Y + 3)

    assert_letter_grid_item(grid, 't', START_X + 2, START_Y - 4)
    assert_letter_grid_item(grid, 'r', START_X + 2, START_Y - 3)
    assert_letter_grid_item(grid, 'u', START_X + 2, START_Y - 2)
    assert_letter_grid_item(grid, 'd', START_X + 2, START_Y - 1)
    assert_letter_grid_item(grid, 'g', START_X + 2, START_Y)
    assert_letter_grid_item(grid, 'e', START_X + 2, START_Y + 1)

# def test_long_word():
#     pass
#
#
# def test_two_long_words():
#     pass
#
#
# def test_three_long_words():
#     pass
#
#
# def test_long_word_and_short_word():
#     pass
