from __future__ import annotations

from typing import Any, Dict, Optional
from random import choice

from . import register_tool
from .tool_base import Tool


@register_tool
class SighTool(Tool):
    """Emit a sigh to express an emotion subtly."""
    name = "sigh"
    description = "NPC sighs subtly."

    def execute(self, emotion_implied: str = "weariness", **kwargs: Any) -> str:
        emotions = {
            "weariness": "NPC lets out a quiet sigh of weariness.",
            "frustration": "NPC sighs, a hint of frustration in the sound.",
            "resignation": "NPC gives a small sigh of resignation.",
            "relief": "NPC exhales a soft sigh, possibly of relief."
        }
        return emotions.get(emotion_implied, emotions["weariness"])

@register_tool
class FidgetTool(Tool):
    """Make small, restless movements."""
    name = "fidget"
    description = "NPC fidgets subtly."

    def execute(self, manner: str = "taps_fingers", reason: str = "nervousness", **kwargs: Any) -> str:
        return f"NPC fidgets by {manner.replace('_', ' ')}, perhaps due to {reason}."

@register_tool
class ShiftWeightTool(Tool):
    """Subtly change posture by shifting weight."""
    name = "shift_weight"
    description = "NPC shifts their weight."

    def execute(self, reason: str = "discomfort", **kwargs: Any) -> str:
        return f"NPC subtly shifts their weight from one foot to the other, possibly indicating {reason}."

@register_tool
class GlanceTool(Tool):
    """Take a quick, brief look at someone or something."""
    name = "glance"
    description = "NPC glances at something or someone."

    def execute(self, target: str = "their surroundings", expression: str = "neutral", **kwargs: Any) -> str:
        expressions = {
            "neutral": f"NPC takes a quick, neutral glance at {target}.",
            "curious": f"NPC glances curiously at {target}.",
            "nervous": f"NPC darts a nervous glance towards {target}.",
            "annoyed": f"NPC throws a brief, annoyed glance at {target}."
        }
        return expressions.get(expression, expressions["neutral"])

@register_tool
class RaiseEyebrowTool(Tool):
    """Raise one or both eyebrows to express surprise, skepticism, etc."""
    name = "raise_eyebrow"
    description = "NPC raises an eyebrow."

    def execute(self, emotion_implied: str = "skepticism", **kwargs: Any) -> str:
        return f"NPC raises an eyebrow, subtly expressing {emotion_implied}."

@register_tool
class TightenLipsTool(Tool):
    """Compress lips to show disapproval, concentration, or restraint."""
    name = "tighten_lips"
    description = "NPC tightens their lips."

    def execute(self, reason: str = "displeasure", **kwargs: Any) -> str:
        return f"NPC tightens their lips, a sign of {reason}." 