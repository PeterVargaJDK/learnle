from functools import reduce
from typing import TypeVar, Iterable
from learnle_site.utils.grid import InfiniteGrid, Position, Axis, Dimensions

T = TypeVar('T')


def union(sets: Iterable[set[T]]) -> set[T]:
    return reduce(lambda x, y: x | y, sets)
