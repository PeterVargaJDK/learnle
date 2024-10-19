from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterable, Generic, TypeVar, OrderedDict

from learnle_site.constants import BLOCK_CHARACTER, NEW_LINE


T = TypeVar('T')


@dataclass(frozen=True)
class Dimensions:
    width: int
    height: int

    def fits_into(self, other: 'Dimensions') -> bool:
        return self.width <= other.width and self.height <= other.height


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
            self.shift(-unit_position.x, -unit_position.y),
        }

    def next_by_axis(self, axis: Axis) -> 'Position':
        unit_position = axis.unit_position()
        return self.shift(unit_position.x, unit_position.y)

    def prev_by_axis(self, axis: Axis) -> 'Position':
        unit_position = axis.unit_position()
        return self.shift(-unit_position.x, -unit_position.y)

    def line(
        self, length: int, axis: Axis, offset: int = 0
    ) -> tuple['Position', 'Position']:
        length = length - 1
        unit_position = axis.unit_position()
        start_pos = self.shift(
            x=-unit_position.x * offset,
            y=-unit_position.y * offset,
        )
        end_pos = start_pos.shift(
            x=unit_position.x * length, y=unit_position.y * length
        )
        return start_pos, end_pos


@dataclass
class Shape:
    min_y: int = 0
    min_x: int = 0
    max_y: int = 0
    max_x: int = 0

    def update_shape_with_new_position(self, position: Position):
        self.min_x = min(self.min_x, position.x)
        self.min_y = min(self.min_y, position.y)
        self.max_x = max(self.max_x, position.x)
        self.max_y = max(self.max_y, position.y)

    def with_new_positions(self, *positions: Position) -> 'Shape':
        shape = Shape(self.min_y, self.min_x, self.max_y, self.max_x)
        for position in positions:
            shape.update_shape_with_new_position(position)
        return shape

    @property
    def vertical_indices(self) -> Iterable[int]:
        return range(self.min_y, self.max_y + 1)

    @property
    def horizontal_indices(self) -> Iterable[int]:
        return range(self.min_x, self.max_x + 1)

    @property
    def dimensions(self) -> Dimensions:
        return Dimensions(self.max_x - self.min_x + 1, self.max_y - self.min_y + 1)


class GridItem(ABC):
    @abstractmethod
    def text_view(self):
        raise NotImplementedError


R = TypeVar('R', bound=GridItem)


class InfiniteGrid(Generic[R]):
    def __init__(self):
        self._items = OrderedDict[Position, R]()
        self._shape = Shape()

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
                line += item.text_view() if item else BLOCK_CHARACTER
            lines.append(line)
        return NEW_LINE.join(lines)

    def __len__(self):
        return len(self._items)

    def __bool__(self):
        return bool(len(self))
