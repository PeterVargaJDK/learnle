from abc import ABC, abstractmethod

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

    def is_blocked(self) -> bool:
        return True

    def position(self) -> tuple[int, int]:
        return 0, 0

    def text(self) -> str:
        raise CrossWordsGridException('Blocked grid item does not have a text representation')


class Letter(GridItem):
    def is_blocked(self) -> bool:
        return False

    def position(self) -> tuple[int, int]:
        return 0, 0

    def text(self) -> str:
        return 'a'


class CrossWordsGrid:

    def __init__(self, words: list[str] | None = None):
        self._words = words

    def at(self, i: int, j: int) -> GridItem:
        if self._words:
            return Letter()
        return BlockedGridItem()


START_POINT = (0, 0)


def test_empty_grid():
    grid = CrossWordsGrid()
    grid_item = grid.at(*START_POINT)
    assert grid_item.is_blocked()
    assert grid_item.position() == START_POINT

    with pytest.raises(CrossWordsGridException):
        grid_item.text()


def test_one_char_word():
    grid = CrossWordsGrid(['a'])
    grid_item = grid.at(*START_POINT)
    assert not grid_item.is_blocked()
    assert grid_item.position() == START_POINT
    assert grid_item.text() == 'a'


def test_two_char_word():
    pass


def test_long_word():
    pass


def test_two_long_words():
    pass


def test_three_long_words():
    pass


def test_long_word_and_short_word():
    pass
