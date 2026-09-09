# -*- coding: utf-8 -*-

from typing import Any
from sqlalchemy import text
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession


class CustomAsyncSession(AsyncSession):
    """Session asynchrone personnalisée intégrant le wrapper text() et les méthodes utilitaires."""

    def _text(self, statement: Any) -> Any:
        return text(statement) if isinstance(statement, str) else statement

    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Result[Any]:
        return await super().execute(self._text(statement), *args, **kwargs)

    async def scalar(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
        return await super().scalar(self._text(statement), *args, **kwargs)

    async def scalars(self, statement: Any, *args: Any, **kwargs: Any) -> list[Any]:
        res = await super().scalars(self._text(statement), *args, **kwargs)
        return list(res.all())

    async def exe_tuples(self, statement: Any, *args: Any, **kwargs: Any) -> list[tuple[Any, ...]]:
        res = await self.execute(statement, *args, **kwargs)
        return list(res.tuples().all())

    async def mappings(self, statement: Any, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        res = await self.execute(statement, *args, **kwargs)
        return [dict(row) for row in res.mappings()]
