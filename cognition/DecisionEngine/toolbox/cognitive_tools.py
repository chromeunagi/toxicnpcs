from __future__ import annotations

from typing import Any, Dict, Optional
from random import choice

from . import register_tool
from .tool_base import Tool


@register_tool
class PonderTool(Tool):
    """Think deeply about something."""
    name = "ponder"
    description = "NPC ponders or thinks deeply."

    def execute(self, topic: str = "the current situation", duration: str = "a moment", **kwargs: Any) -> str:
        return f"NPC becomes quiet and appears to ponder {topic} for {duration}."

@register_tool
class MakePlanTool(Tool):
    """Formulate a course of action."""
    name = "make_plan"
    description = "NPC formulates a plan."

    def execute(self, objective: str = "their next move", complexity: str = "simple", **kwargs: Any) -> str:
        return f"NPC seems to be formulating a {complexity} plan regarding {objective}."

@register_tool
class ReconsiderTool(Tool):
    """Think again about a previous decision or opinion."""
    name = "reconsider"
    description = "NPC reconsiders a previous thought or decision."

    def execute(self, topic: str = "their stance", **kwargs: Any) -> str:
        return f"NPC pauses, appearing to reconsider {topic}."

@register_tool
class DaydreamTool(Tool):
    """Get lost in thought, often about pleasant things."""
    name = "daydream"
    description = "NPC gets lost in a daydream."

    def execute(self, **kwargs: Any) -> str:
        daydreams = [
            "NPC stares off into the distance, seemingly lost in a daydream.",
            "A faint smile plays on NPC's lips as they appear to daydream.",
            "NPC seems momentarily distracted, perhaps daydreaming."
        ]
        return choice(daydreams)

@register_tool
class RecallMemoryTool(Tool):
    """Actively try to remember something from the past."""
    name = "recall_memory"
    description = "NPC tries to recall a memory."

    def execute(self, topic: str = "a past event", effort_level: str = "moderate", **kwargs: Any) -> str:
        if effort_level == "high":
            return f"NPC concentrates hard, trying to recall details about {topic}."
        elif effort_level == "low":
            return f"NPC casually tries to remember something about {topic}."
        else:
            return f"NPC makes an effort to recall a memory concerning {topic}."

@register_tool
class FocusAttentionTool(Tool):
    """Concentrate on a specific task or stimulus."""
    name = "focus_attention"
    description = "NPC focuses their attention."

    def execute(self, target: str = "the task at hand", intensity: float = 0.7, **kwargs: Any) -> str:
        if intensity > 0.8:
            return f"NPC focuses with intense concentration on {target}."
        elif intensity > 0.4:
            return f"NPC directs their attention towards {target}."
        else:
            return f"NPC gives fleeting attention to {target}." 