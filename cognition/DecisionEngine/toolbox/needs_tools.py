from __future__ import annotations

from typing import Any, Dict, Optional

from . import register_tool
from .tool_base import Tool


@register_tool
class SeekShelterTool(Tool):
    """Find and move to a place of safety or cover from elements/threats."""
    
    name = "seek_shelter"
    description = "NPC looks for and moves to a sheltered or safe location."
    
    def execute(self, reason: str = "danger", urgency: float = 0.7, **kwargs: Any) -> str:
        urgency_desc = "calmly" if urgency < 0.3 else "hurriedly" if urgency > 0.7 else "quickly"
        return f"NPC {urgency_desc} seeks shelter due to {reason}."


@register_tool
class RestTool(Tool):
    """Take a moment to rest and recover fatigue or minor wounds."""
    
    name = "rest"
    description = "NPC takes a moment to rest, possibly recovering some stamina or health."
    
    def execute(self, duration: str = "briefly", **kwargs: Any) -> str:
        return f"NPC rests {duration} to recover."


@register_tool
class FindFoodTool(Tool):
    """Search for or acquire food."""
    
    name = "find_food"
    description = "NPC attempts to find or acquire food."
    
    def execute(self, method: str = "foraging", **kwargs: Any) -> str:
        # Method could be 'foraging', 'hunting', 'scavenging', 'purchasing'
        return f"NPC attempts to find food by {method}."


@register_tool
class FindWaterTool(Tool):
    """Search for or acquire a source of drinkable water."""
    
    name = "find_water"
    description = "NPC attempts to find a source of fresh water."
    
    def execute(self, **kwargs: Any) -> str:
        return "NPC looks for a source of drinkable water."


@register_tool
class HealSelfTool(Tool):
    """Attempt to heal injuries using items or abilities."""
    
    name = "heal_self"
    description = "NPC attempts to treat their wounds using items or abilities."
    
    def execute(self, method: str = "bandages", severity: float = 0.5, **kwargs: Any) -> str:
        # Method could be 'bandages', 'potion', 'magic_spell', 'first_aid_kit'
        severity_desc = "minor" if severity < 0.3 else "serious" if severity > 0.7 else "moderate"
        return f"NPC attempts to heal their {severity_desc} injuries using {method}."


@register_tool
class WarmSelfTool(Tool):
    """Attempt to get warmer if cold (e.g., find fire, put on clothes)."""

    name = "warm_self"
    description = "NPC tries to find a way to get warmer."

    def execute(self, method: str = "finding a fire", **kwargs: Any) -> str:
        return f"NPC attempts to warm themselves by {method}." 