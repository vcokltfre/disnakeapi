from typing import Callable, Optional

from disnake.ext.commands import Cog as _Cog

from .api import APIRoute, CheckFunction, HandlerFunction


class Cog(_Cog):
    @classmethod
    def route(cls, method: str, path: str, checks: Optional[list[CheckFunction]] = None) -> Callable[..., APIRoute]:
        def decorator(handler: HandlerFunction) -> APIRoute:
            return APIRoute(method, path, handler, checks)

        return decorator

    @classmethod
    def get(cls, path: str, checks: Optional[list[CheckFunction]] = None) -> Callable[..., APIRoute]:
        return cls.route("GET", path, checks)

    @classmethod
    def post(cls, path: str, checks: Optional[list[CheckFunction]] = None) -> Callable[..., APIRoute]:
        return cls.route("POST", path, checks)

    @classmethod
    def put(cls, path: str, checks: Optional[list[CheckFunction]] = None) -> Callable[..., APIRoute]:
        return cls.route("PUT", path, checks)

    @classmethod
    def patch(cls, path: str, checks: Optional[list[CheckFunction]] = None) -> Callable[..., APIRoute]:
        return cls.route("PATCH", path, checks)

    @classmethod
    def delete(cls, path: str, checks: Optional[list[CheckFunction]] = None) -> Callable[..., APIRoute]:
        return cls.route("DELETE", path, checks)

    @classmethod
    def head(cls, path: str, checks: Optional[list[CheckFunction]] = None) -> Callable[..., APIRoute]:
        return cls.route("HEAD", path, checks)

    @classmethod
    def options(cls, path: str, checks: Optional[list[CheckFunction]] = None) -> Callable[..., APIRoute]:
        return cls.route("OPTIONS", path, checks)
