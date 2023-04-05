from functools import cached_property
from re import Pattern, compile
from typing import Final

PATTERNS: Final[dict[str, str]] = {
    "int": r"\d+",
    "str": r".+",
    "float": r"\d+(\.\d+)?",
}

CONVERTERS: Final[dict[str, type]] = {
    "int": int,
    "str": str,
    "float": float,
}


class RouteComponent:
    def __init__(
        self,
        type: str,
        param_name: str,
        *,
        param_type: str = "",
    ) -> None:
        self.type = type
        self.param_name = param_name
        self.param_type = param_type


class Route:
    def __init__(self, components: list[RouteComponent]) -> None:
        self.components = components
        self._component_types = {
            component.param_name: component.param_type for component in components if component.type == "param"
        }

    @cached_property
    def _regex(self) -> Pattern[str]:
        regex = ""

        for component in self.components:
            if component.type == "static":
                regex += component.param_name
            elif component.type == "param":
                regex += f"(?P<{component.param_name}>{PATTERNS[component.param_type]})"

        return compile("^" + regex + "$")

    def matches(self, path: str) -> bool:
        return self._regex.match(path) is not None

    def params(self, path: str) -> dict[str, str]:
        match = self._regex.match(path)

        if match is None:
            raise ValueError(f"Path {path} does not match route {self}")

        raw = match.groupdict()

        return {key: CONVERTERS[self._component_types[key]](value) for key, value in raw.items() if value}


def parse_route(route: str) -> Route:
    components: list[RouteComponent] = []

    current = ""
    in_param = False

    for char in route:
        if in_param:
            if char == "}":
                param_name, param_type = current.split(":")
                components.append(RouteComponent("param", param_name=param_name, param_type=param_type))
                current = ""
                in_param = False
            else:
                current += char

            continue

        if char == "{":
            if current:
                components.append(RouteComponent("static", param_name=current))
                current = ""

            in_param = True
            continue

        current += char

    if in_param:
        raise ValueError(f"Route {route} is invalid")

    if current:
        components.append(RouteComponent("static", param_name=current))

    return Route(components)
