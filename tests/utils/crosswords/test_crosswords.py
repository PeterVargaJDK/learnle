from abc import ABC, abstractmethod
from dataclasses import dataclass

import pytest


class CrossWordsGridException(Exception):
    pass


class GridItem(ABC):

    @abstractmethod
    def is_blocked(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def position(self) -> tuple[int, int]:
        raise NotImplementedError

    @abstractmethod
    def text(self) -> str:
        raise NotImplementedError


class BlockedGridItem(GridItem):

    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    def is_blocked(self) -> bool:
        return True

    def position(self) -> tuple[int, int]:
        return self._x, self._y

    def text(self) -> str:
        raise CrossWordsGridException('Blocked grid item does not have a text representation')


class LetterGridItem(GridItem):
    def __init__(self, char: str, x: int, y: int):
        self._char = char
        self._x = x
        self._y = y

    def is_blocked(self) -> bool:
        return False

    def position(self) -> tuple[int, int]:
        return self._x, self._y

    def text(self) -> str:
        return self._char


START_X = 0
START_Y = 0


@dataclass
class Word:
    text: str
    start_pos: tuple[int, int]
    end_pos: tuple[int, int]


class CrossWordsGrid:

    @staticmethod
    def _key(x: int, y: int) -> str:
        return f'{x}-{y}'

    def __init__(self, words: list[str] | None = None):
        self._letters = {}
        self._words = []
        self._lowest_y = 0
        self._lowest_x = 0
        self._highest_y = 0
        self._highest_x = 0
        if words:
            for word in words:
                if not self._letters:
                    x = START_X
                    for char in word:
                        self._letters[self._key(x, START_Y)] = LetterGridItem(char, x, START_Y)
                        x += 1
                    self._highest_x = x
                    self._words.append(Word(
                        text=word,
                        start_pos=(START_X, START_Y),
                        end_pos=(START_X + len(word), START_Y)
                    ))
                else:
                    for idx, char in enumerate(word):
                        longest_word = self._words[0]
                        common_letter_idx = longest_word.text.find(char)
                        if common_letter_idx == -1:
                            continue
                        start_pos = (longest_word.start_pos[0] + common_letter_idx, longest_word.start_pos[1] - idx)
                        end_pos = (start_pos[0], start_pos[1] + len(word))
                        self._words.append(Word(
                            text=word,
                            start_pos=start_pos,
                            end_pos=end_pos
                        ))
                        for y, char_2 in zip(range(start_pos[1], end_pos[1]), word):
                            self._letters[self._key(start_pos[0], y)] = LetterGridItem(char_2, start_pos[0], y)
                        self._lowest_y = start_pos[1]
                        self._highest_y = end_pos[1]
                        break

    def at(self, x: int, y: int) -> GridItem:
        if not self._letters or self._key(x, y) not in self._letters:
            return BlockedGridItem(x, y)

        return self._letters[self._key(x, y)]

    def __repr__(self):
        result = ''
        for y in range(self._lowest_y, self._highest_y):
            for x in range(self._lowest_x, self._highest_x):
                if (key := self._key(x, y)) in self._letters:
                    result += self._letters[key].text()
                else:
                    result += '■'
            result += '\n'
        return result


def assert_letter_grid_item(grid: CrossWordsGrid, character: str, x: int, y: int):
    grid_item = grid.at(x, y)
    assert not grid_item.is_blocked()
    assert grid_item.position() == (x, y)
    assert grid_item.text() == character


def assert_blocked_grid_item(grid: CrossWordsGrid, x: int, y: int):
    grid_item = grid.at(x, y)
    assert grid_item.is_blocked()
    assert grid_item.position() == (x, y)
    with pytest.raises(CrossWordsGridException):
        grid_item.text()


def test_empty_grid():
    grid = CrossWordsGrid()
    assert_blocked_grid_item(grid, START_X, START_Y)


def test_one_char_word():
    grid = CrossWordsGrid(['a'])
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
