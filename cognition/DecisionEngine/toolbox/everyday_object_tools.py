from __future__ import annotations

from typing import Any, Dict, Optional

from . import register_tool
from .tool_base import Tool

# Note: These are distinct from item_tools.py which focuses on more "game-y" items.
# This module is for interacting with common, everyday objects.

@register_tool
class PickUpObjectTool(Tool):
    """Pick up a common object."""
    name = "pick_up_object"
    description = "NPC picks up a common object."

    def execute(self, item_name: str = "a nearby object", purpose: str = "examine", **kwargs: Any) -> str:
        return f"NPC picks up {item_name} to {purpose} it."

@register_tool
class PutDownObjectTool(Tool):
    """Place a common object somewhere."""
    name = "put_down_object"
    description = "NPC puts down a common object."

    def execute(self, item_name: str = "the object they are holding", location: str = "a nearby surface", **kwargs: Any) -> str:
        return f"NPC puts down {item_name} on {location}."

@register_tool
class OpenObjectTool(Tool):
    """Open a container or passage (door, box, book)."""
    name = "open_object"
    description = "NPC opens something."

    def execute(self, object_to_open: str = "a door", manner: str = "normally", **kwargs: Any) -> str:
        return f"NPC {manner} opens {object_to_open}."

@register_tool
class CloseObjectTool(Tool):
    """Close a container or passage."""
    name = "close_object"
    description = "NPC closes something."

    def execute(self, object_to_close: str = "a door", manner: str = "gently", **kwargs: Any) -> str:
        return f"NPC {manner} closes {object_to_close}."

@register_tool
class UseEverydayObjectTool(Tool):
    """Use a common, everyday object for its typical purpose."""
    name = "use_everyday_object"
    description = "NPC uses an everyday object."

    def execute(self, item_name: str = "a tool", action: str = "its intended purpose", **kwargs: Any) -> str:
        return f"NPC uses {item_name} for {action}."

@register_tool
class TidyUpTool(Tool):
    """Arrange things neatly in the immediate environment."""
    name = "tidy_up"
    description = "NPC tidies their immediate surroundings."

    def execute(self, area: str = "their personal space", thoroughness: str = "quickly", **kwargs: Any) -> str:
        return f"NPC {thoroughness} tidies up {area}."

@register_tool
class PrepareFoodOrDrinkTool(Tool):
    """Make a simple food or beverage."""
    name = "prepare_food_or_drink"
    description = "NPC prepares some simple food or a drink."

    def execute(self, item_to_prepare: str = "a cup of tea", complexity: str = "simple", **kwargs: Any) -> str:
        return f"NPC prepares a {complexity} {item_to_prepare}." 