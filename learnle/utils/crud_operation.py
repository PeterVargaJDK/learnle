from abc import ABC, abstractmethod
from typing import (
    Generic,
    TypeVar,
    OrderedDict,
    Type,
    Callable,
)

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
)
from pydantic import BaseModel, PositiveInt, Field


T = TypeVar('T', bound=BaseModel)


class CRUDAdapter(ABC, Generic[T]):
    @abstractmethod
    async def save(self, item: T) -> T:
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

    @abstractmethod
    def _set_uid(self, item: T, uid: str):
        raise NotImplementedError

    async def save(self, item: T) -> T:
        uid = self._extract_uid(item)
        self._set_uid(item, uid)
        self._items[uid] = item
        return item

    async def list(self, page_number: int, page_size: int) -> list[T]:
        return _paginate(list(self._items.values()), page_number, page_size)

    async def get_by_uid(self, uid: str) -> T | None:
        return self._items.get(uid)

    async def delete(self, uid: str):
        del self._items[uid]


class _DeleteResponse(BaseModel):
    message: str = Field(
        default='DELETED',
        json_schema_extra={
            'const': 'DELETED',
        },
    )


def crud_api(
    adapter_factory: Callable[..., CRUDAdapter[T]], model_class: Type[T]
) -> APIRouter:
    model_name = model_class.__name__
    api_router = APIRouter(prefix=f'/{model_name.lower()}')

    @api_router.get(
        path='/{uid}',
        description=f'Read endpoint for {model_name} objects',
        summary=f'Read {model_name}',
        tags=[model_name],
    )
    async def _(
        uid: str,
        adapter: CRUDAdapter[model_class] = Depends(adapter_factory),  # type: ignore[valid-type]
    ) -> model_class:  # type: ignore[valid-type]
        item_found = await adapter.get_by_uid(uid)
        if not item_found:
            raise HTTPException(status_code=404)
        return item_found

    @api_router.get(
        path='',
        description=f'List endpoint for {model_name} objects',
        summary=f'List {model_name} objects',
        tags=[model_name],
    )
    async def _(
        page_number: PositiveInt = 1,
        page_size: PositiveInt = 20,
        adapter: CRUDAdapter[model_class] = Depends(adapter_factory),  # type: ignore[valid-type]
    ) -> list[model_class]:  # type: ignore[valid-type]
        return await adapter.list(page_number, page_size)

    @api_router.post(
        path='',
        response_model=model_class,
        description=f'Save endpoint for {model_name} objects',
        summary=f'Save {model_name} objects',
        tags=[model_name],
    )
    async def _(
        item: model_class,  # type: ignore[valid-type]
        adapter: CRUDAdapter[model_class] = Depends(adapter_factory),  # type: ignore[valid-type]
    ) -> model_class:  # type: ignore[valid-type]
        return await adapter.save(item)

    @api_router.delete(
        path='/{uid}',
        description=f'Delete endpoint for {model_name} objects',
        summary=f'Delete {model_name}',
        tags=[model_name],
    )
    async def _(
        uid: str,
        adapter: CRUDAdapter[model_class] = Depends(adapter_factory),  # type: ignore[valid-type]
    ) -> _DeleteResponse:
        await adapter.delete(uid)
        return _DeleteResponse()

    return api_router
