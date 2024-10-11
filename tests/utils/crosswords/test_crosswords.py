from abc import ABC, abstractmethod


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


class CrossWordsGrid:

    def __init__(self):
        pass

    def at(self, i: int, j: int) -> GridItem:
        return BlockedGridItem()


START_POINT = (0, 0)


def test_empty_grid():
    grid = CrossWordsGrid()
    grid_item = grid.at(*START_POINT)
    assert grid_item.is_blocked()
    assert grid_item.position() == START_POINT


def test_one_char_word():
    pass


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
