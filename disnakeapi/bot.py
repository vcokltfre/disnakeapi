from typing import Any, Union

from aiohttp.web import Request
from disnake.ext.commands import Bot as _Bot
from disnake.ext.commands import Cog as DisnakeCog

from .api import APIRoute, APIRouter
from .cog import Cog as APICog

Cog = Union[DisnakeCog, APICog]


class Bot(_Bot):
    def __init__(self, host: str, port: int, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._host = host
        self._port = port

        self.api = APIRouter(self, host, port)

    async def start(self, *args: Any, **kwargs: Any) -> None:
        await self.api.start()
        await super().start(*args, **kwargs)

    def _add_route(self, route: APIRoute, cog: APICog) -> None:
        def handler(request: Request, *args: Any, **kwargs: Any) -> Any:
            return route.handler(cog, request, *args, **kwargs)

        route.set_qualified_handler(handler)

        self.api.add_route(route)

    def add_cog(self, cog: Cog, *, override: bool = False) -> None:
        super().add_cog(cog, override=override)

        if isinstance(cog, APICog):
            for route in cog.__class__.__dict__.values():
                if isinstance(route, APIRoute):
                    self._add_route(route, cog)
