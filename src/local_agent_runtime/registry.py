from __future__ import annotations

from .contracts import Connector, Skill


class ConnectorRegistry:
    def __init__(self) -> None:
        self._items: dict[str, Connector] = {}

    def register(self, connector: Connector) -> None:
        if connector.name in self._items:
            raise ValueError(f"connector already registered: {connector.name}")
        self._items[connector.name] = connector

    def get(self, name: str) -> Connector:
        try:
            return self._items[name]
        except KeyError as exc:
            raise KeyError(f"connector not found: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._items)


class SkillRegistry:
    def __init__(self) -> None:
        self._items: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        if skill.name in self._items:
            raise ValueError(f"skill already registered: {skill.name}")
        self._items[skill.name] = skill

    def get(self, name: str) -> Skill:
        try:
            return self._items[name]
        except KeyError as exc:
            raise KeyError(f"skill not found: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._items)
