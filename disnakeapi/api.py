from asyncio import Task, create_task
from typing import Any, Awaitable, Callable, Generic, Optional, TypeVar

from aiohttp.web import Application, AppRunner, Request, Response, TCPSite
from disnake.ext.commands import Bot
from pydantic import BaseModel

from .parser import parse_route

T = TypeVar("T", bound=Bot)

HandlerFunction = Callable[..., Awaitable[Any]]
CheckFunction = Callable[[Request], Awaitable[bool]]


class APIRoute:
    def __init__(
        self,
        method: str,
        path: str,
        handler: HandlerFunction,
        checks: Optional[list[CheckFunction]] = None,
    ) -> None:
        self.method = method
        self.path = path
        self.handler = handler
        self.checks = checks or []

        self.route = parse_route(path)

        self._qualified_handler: Optional[HandlerFunction] = None

    def set_qualified_handler(self, cog: Any) -> None:
        def handler(request: Request, *args: Any, **kwargs: Any) -> Any:
            return self.handler(cog, request, *args, **kwargs)

        self._qualified_handler = handler

    async def handle(self, request: Request) -> Response:
        if self._qualified_handler is None:
            raise RuntimeError("Route is not qualified")

        for check in self.checks:
            if not await check(request):
                return Response(status=403)

        result = await self._qualified_handler(request)

        if isinstance(result, Response):
            return result

        if result is None:
            return Response(status=204)

        if isinstance(result, str):
            return Response(
                text=result,
                content_type="text/plain",
            )

        if isinstance(result, BaseModel):
            return Response(
                text=result.json(),
                content_type="application/json",
            )

        raise TypeError(f"Unexpected return type from handler: {type(result)}")


class APIRouter(Generic[T]):
    def __init__(self, bot: T, host: str, port: int) -> None:
        self._bot = bot
        self._host = host
        self._port = port

        self._app = Application()
        self._runner = AppRunner(self._app)
        self._site: Optional[TCPSite] = None

        self._task: Optional[Task[None]] = None

        self._routes: list[APIRoute] = []

        self._app.router.add_get("/{tail:.*}", self._handler)

    def add_route(self, route: APIRoute) -> None:
        self._routes.append(route)
        self._app.router.add_route(route.method, route.path, route.handle)

    async def start(self) -> None:
        if self._site is not None:
            raise RuntimeError("API is already running")

        await self._runner.setup()
        self._site = TCPSite(self._runner, self._host, self._port)
        self._task = create_task(self._site.start())

    async def stop(self) -> None:
        if not self._site:
            raise RuntimeError("API is not running")

        await self._site.stop()
        await self._runner.cleanup()

        self._site = None

    async def _handler(self, request: Request) -> Response:
        for route in self._routes:
            if route.method == request.method and route.route.matches(request.path):
                return await route.handle(request, **route.route.params(request.path))

        return Response(status=404)
