import uuid
from functools import reduce
from typing import TypeVar, Iterable

T = TypeVar('T')


def union(sets: Iterable[set[T]]) -> set[T]:
    return reduce(lambda x, y: x | y, sets)


def generate_uid() -> str:
    return uuid.uuid4().hex
