from __future__ import annotations

from typing import Any, Dict, Optional
from random import choice

from . import register_tool
from .tool_base import Tool


@register_tool
class ScanForThreatsTool(Tool):
    """Actively scan the environment for potential dangers."""
    
    name = "scan_for_threats"
    description = "NPC actively scans the surroundings for any signs of danger or hostiles."
    
    def execute(self, thoroughness: float = 0.6, **kwargs: Any) -> str:
        if thoroughness < 0.3:
            return "NPC gives a quick, cursory glance around for threats."
        elif thoroughness < 0.7:
            return "NPC carefully scans the area for potential threats."
        else:
            return "NPC meticulously and slowly scans every corner for hidden dangers."


@register_tool
class DetectMagicTool(Tool):
    """Attempt to sense or identify magical auras or effects."""
    
    name = "detect_magic"
    description = "NPC focuses to detect magical energies or enchantments nearby."
    
    def execute(self, radius: int = 10, **kwargs: Any) -> str:
        # In a real game, this might trigger a spell or skill check
        return f"NPC attempts to detect magic within a {radius}-meter radius."


@register_tool
class AssessIntentTool(Tool):
    """Try to determine the intentions of another character."""
    
    name = "assess_intent"
    description = "NPC observes another character to gauge their intentions (friendly, hostile, neutral)."
    
    def execute(self, target: str = "the player", method: str = "observation", **kwargs: Any) -> str:
        # Method could be 'observation', 'dialogue_probe', 'intuition'
        return f"NPC carefully observes {target} using {method}, trying to understand their intentions."


@register_tool
class IdentifyObjectTool(Tool):
    """Attempt to identify an unknown object or substance."""
    
    name = "identify_object"
    description = "NPC tries to identify an unknown object, possibly using knowledge skills."
    
    def execute(self, object_name: str = "the strange device", skill_used: str = "lore", **kwargs: Any) -> str:
        return f"NPC attempts to identify {object_name} using their knowledge of {skill_used}."


@register_tool
class TrackTargetTool(Tool):
    """Follow the trail or tracks of a specific target."""
    
    name = "track_target"
    description = "NPC attempts to find and follow the tracks of a target."
    
    def execute(self, target: str = "the fugitive", difficulty: float = 0.5, **kwargs: Any) -> str:
        if difficulty < 0.3:
            return f"NPC easily picks up the trail of {target} and begins tracking."
        elif difficulty < 0.7:
            return f"NPC carefully searches for {target}'s tracks and starts following."
        else:
            return f"NPC struggles but manages to find faint tracks of {target} and attempts to follow."


@register_tool
class EavesdropTool(Tool):
    """Attempt to secretly listen to a conversation."""

    name = "eavesdrop"
    description = "NPC tries to listen in on a conversation without being detected."

    def execute(self, target_conversation: str = "a nearby discussion", risk_level: float = 0.5, **kwargs: Any) -> str:
        risk_desc = "cautiously" if risk_level < 0.4 else "boldly" if risk_level > 0.7 else "discreetly"
        return f"NPC {risk_desc} attempts to eavesdrop on {target_conversation}." 