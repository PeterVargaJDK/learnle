import uuid
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, OrderedDict

from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)


def generate_uid() -> str:
    return uuid.uuid4().hex


class CRUDAdapter(ABC, Generic[T]):
    @abstractmethod
    async def save(self, item: T) -> str:
        raise NotImplementedError

    @abstractmethod
    async def list(self, page_number: int, page_size: int) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_uid(self, uid: str) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, uid: str):
        raise NotImplementedError


def _paginate(items: list[T], page_number: int, page_size: int) -> list[T]:
    offset = (page_number - 1) * page_size
    return items[offset : offset + page_size]


class InMemoryCRUDAdapter(CRUDAdapter[T]):
    def __init__(self):
        self._items: dict[str, T] = OrderedDict[str, T]()

    @property
    def items(self):
        return self._items

    @abstractmethod
    def _extract_uid(self, item: T) -> str:
        raise NotImplementedError

    async def save(self, item: T) -> str:
        self._items[self._extract_uid(item)] = item
        return self._extract_uid(item)

    async def list(self, page_number: int, page_size: int) -> list[T]:
        return _paginate(list(self._items.values()), page_number, page_size)

    async def get_by_uid(self, uid: str) -> T | None:
        return self._items.get(uid)

    async def delete(self, uid: str):
        del self._items[uid]
