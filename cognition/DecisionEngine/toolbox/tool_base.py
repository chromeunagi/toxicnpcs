from __future__ import annotations

import abc
from typing import Any, Dict


class Tool(abc.ABC):
    """Abstract base class for all character tools (actions)."""

    name: str = "generic_tool"
    description: str = "Generic tool base. Override in subclasses."

    def __init__(self) -> None:
        self.state: Dict[str, Any] = {}

    @abc.abstractmethod
    def execute(self, **kwargs: Any) -> str:
        """Run the tool logic and return a human-readable description of the action."""

    def __str__(self) -> str:
        return self.name 