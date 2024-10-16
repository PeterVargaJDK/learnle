from dataclasses import dataclass
from enum import (
    Enum,
    auto
)
from typing import (
    Iterable,
    Generic,
    TypeVar
)

from learnle_site.constants import (
    BLOCK_CHARACTER,
    NEW_LINE
)


@dataclass(frozen=True)
class Dimensions:
    width: int
    height: int


class Axis(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()

    def rotate(self):
        return self.VERTICAL if self == self.HORIZONTAL else self.HORIZONTAL

    def unit_position(self) -> 'Position':
        return Position(1, 0) if self == self.HORIZONTAL else Position(0, 1)


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class Position:
    x: int
    y: int

    def shift(self, x: int = 0, y: int = 0) -> 'Position':
        return Position(self.x + x, self.y + y)

    def to(self, other: 'Position') -> Iterable['Position']:
        if self.x == other.x:
            for y in range(self.y, other.y + 1):
                yield Position(self.x, y)
        elif self.y == other.y:
            for x in range(self.x, other.x + 1):
                yield Position(x, self.y)

    def adjacent_positions(self) -> list['Position']:
        return [
            self.shift(x=-1),
            self.shift(x=+1),
            self.shift(y=-1),
            self.shift(y=+1),
        ]

    def adjacent_positions_on_axis(self, axis: Axis) -> set['Position']:
        unit_position = axis.unit_position()
        return {
            self.shift(unit_position.x, unit_position.y),
            self.shift(-unit_position.x, -unit_position.y)
        }

    def next_by_axis(self, axis: Axis) -> 'Position':
        unit_position = axis.unit_position()
        return self.shift(unit_position.x, unit_position.y)

    def prev_by_axis(self, axis: Axis) -> 'Position':
        unit_position = axis.unit_position()
        return self.shift(-unit_position.x, -unit_position.y)


T = TypeVar('T')
R = TypeVar('R')


@dataclass
class _Cell(Generic[T]):
    value: T


class InfiniteGrid(Generic[T, R]):

    def __init__(self):
        self._items: dict[Position, _Cell] = {}
        self._min_y = 0
        self._min_x = 0
        self._max_y = 0
        self._max_x = 0

    def _update_shape(self, position: Position):
        self._min_x = min(self._min_x, position.x)
        self._min_y = min(self._min_y, position.y)
        self._max_x = max(self._max_x, position.x)
        self._max_y = max(self._max_y, position.y)

    def __setitem__(self, position: Position, item: T):
        self._items[position] = item
        self._update_shape(position)

    def __getitem__(self, position: Position) -> T | None:
        return self._items.get(position)

    def __contains__(self, item: Position) -> bool:
        return item in self._items

    @property
    def _vertical_indices(self) -> Iterable[int]:
        return range(self._min_y, self._max_y + 1)

    @property
    def _horizontal_indices(self) -> Iterable[int]:
        return range(self._min_x, self._max_x + 1)

    @property
    def items(self) -> Iterable[T]:
        for y in self._vertical_indices:
            for x in self._horizontal_indices:
                pos = Position(x, y)
                if item := self._items.get(pos):
                    yield item
                else:
                    yield R(pos)

    @property
    def dimensions(self) -> Dimensions:
        return Dimensions(self._max_x - self._min_x + 1, self._max_y - self._min_y + 1)

    def __str__(self):
        lines = []
        for y in self._vertical_indices:
            line = ''
            for x in self._horizontal_indices:
                item = self._items.get(Position(x, y))
                line += str(item) if item else BLOCK_CHARACTER
            lines.append(line)
        return NEW_LINE.join(lines)


    


