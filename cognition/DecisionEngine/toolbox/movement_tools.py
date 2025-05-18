from __future__ import annotations

from typing import Any, Dict, Optional

from . import register_tool
from .tool_base import Tool


@register_tool
class ApproachTool(Tool):
    """Move toward a target."""
    
    name = "approach"
    description = "NPC approaches a target."
    
    def execute(self, target: str = "the player", manner: str = "neutral", **kwargs: Any) -> str:
        """
        Move toward a target in a specified manner.
        
        Args:
            target: Who/what to approach
            manner: How to approach (cautious, friendly, aggressive, stealthy)
        """
        if manner == "cautious":
            return f"NPC carefully and slowly approaches {target}."
        elif manner == "friendly":
            return f"NPC approaches {target} with a friendly demeanor."
        elif manner == "aggressive":
            return f"NPC aggressively advances toward {target}."
        elif manner == "stealthy":
            return f"NPC quietly sneaks toward {target}, trying to remain unnoticed."
        else:  # neutral
            return f"NPC approaches {target}."


@register_tool
class RetreatTool(Tool):
    """Move away from a threat in a controlled manner."""
    
    name = "retreat"
    description = "NPC moves away from danger in an orderly fashion."
    
    def execute(self, speed: str = "moderate", **kwargs: Any) -> str:
        """
        Execute a controlled retreat.
        
        Args:
            speed: Retreat speed (slow, moderate, fast)
        """
        if speed == "slow":
            return "NPC backs away slowly, maintaining vigilance."
        elif speed == "fast":
            return "NPC quickly retreats to a safer position."
        else:  # moderate
            return "NPC retreats at a measured pace to maintain distance."


@register_tool
class CircleTool(Tool):
    """Move around a target to maintain distance or seek advantage."""
    
    name = "circle"
    description = "NPC circles around a target."
    
    def execute(self, target: str = "the opponent", purpose: str = "evaluate", **kwargs: Any) -> str:
        """
        Circle around a target.
        
        Args:
            target: Who/what to circle around
            purpose: Why circling (evaluate, find_opening, maintain_distance, confuse)
        """
        if purpose == "find_opening":
            return f"NPC circles {target}, looking for a weakness to exploit."
        elif purpose == "maintain_distance":
            return f"NPC circles {target}, keeping a safe distance."
        elif purpose == "confuse":
            return f"NPC circles {target} erratically to cause confusion."
        else:  # evaluate
            return f"NPC circles {target}, carefully assessing the situation."


@register_tool
class HideTool(Tool):
    """Conceal oneself to avoid detection."""
    
    name = "hide"
    description = "NPC hides to avoid being seen."
    
    def execute(self, location: str = "nearby cover", **kwargs: Any) -> str:
        """
        Hide in or behind something.
        
        Args:
            location: Where to hide
        """
        return f"NPC hides behind {location}."


@register_tool
class TakeCoverTool(Tool):
    """Move to a protected position."""
    
    name = "take_cover"
    description = "NPC seeks protection behind cover."
    
    def execute(self, cover_type: str = "available cover", **kwargs: Any) -> str:
        """
        Move to cover for protection.
        
        Args:
            cover_type: Type of cover to seek
        """
        return f"NPC quickly takes cover behind {cover_type}." 