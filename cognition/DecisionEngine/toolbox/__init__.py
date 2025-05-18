from __future__ import annotations

from typing import Dict, Type

from .tool_base import Tool

# Central registry for available tools
_TOOL_REGISTRY: Dict[str, Type[Tool]] = {}


def register_tool(cls: Type[Tool]) -> Type[Tool]:
    """Decorator to register a Tool subclass in the global registry."""

    _TOOL_REGISTRY[cls.__name__] = cls
    return cls


def get_tool(tool_name: str) -> Type[Tool]:
    """Retrieve tool class by name, raising KeyError if not found."""

    return _TOOL_REGISTRY[tool_name]

# ---------------------------------------------------------------------
# Import tool modules AFTER helpers are defined to avoid circular import
# ---------------------------------------------------------------------
from . import dialogue_tools  # noqa: E402  # pylint: disable=wrong-import-position
from . import combat_tools  # noqa: E402  # pylint: disable=wrong-import-position
from . import movement_tools  # noqa: E402  # pylint: disable=wrong-import-position
from . import social_tools  # noqa: E402  # pylint: disable=wrong-import-position
from . import emotional_tools  # noqa: E402  # pylint: disable=wrong-import-position
from . import item_tools  # noqa: E402  # pylint: disable=wrong-import-position
from . import environmental_tools  # noqa: E402  # pylint: disable=wrong-import-position

__all__ = [
    "Tool",
    "register_tool",
    "get_tool",
] + list(_TOOL_REGISTRY.keys()) 