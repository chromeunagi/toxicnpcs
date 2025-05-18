from __future__ import annotations

from typing import Any, Dict, Optional

from . import register_tool
from .tool_base import Tool


@register_tool
class IgnoreTool(Tool):
    """Deliberately pay no attention to someone or something."""
    name = "ignore"
    description = "NPC ignores someone or something."

    def execute(self, target: str = "the player", subtlety: str = "obvious", **kwargs: Any) -> str:
        if subtlety == "subtle":
            return f"NPC subtly ignores {target}, pretending not to notice."
        elif subtlety == "pointed":
            return f"NPC pointedly ignores {target}, making their disinterest clear."
        else: # obvious
            return f"NPC obviously ignores {target}."

@register_tool
class AvoidTool(Tool):
    """Actively try to stay away from someone or a situation."""
    name = "avoid"
    description = "NPC tries to avoid someone or something."

    def execute(self, target: str = "an awkward situation", reason: str = "discomfort", **kwargs: Any) -> str:
        return f"NPC actively tries to avoid {target} due to {reason}."

@register_tool
class JoinGroupTool(Tool):
    """Attempt to become part of a group or conversation."""
    name = "join_group"
    description = "NPC attempts to join a group or conversation."

    def execute(self, group_description: str = "a nearby group", approach_style: str = "casually", **kwargs: Any) -> str:
        if approach_style == "tentatively":
            return f"NPC tentatively approaches {group_description}, hoping to join."
        elif approach_style == "confidently":
            return f"NPC confidently walks over to {group_description} and joins in."
        else: #casually
            return f"NPC casually tries to join {group_description}."

@register_tool
class LeaveGroupTool(Tool):
    """Depart from a group or conversation."""
    name = "leave_group"
    description = "NPC leaves a group or conversation."

    def execute(self, group_description: str = "the current group", reason: str = "politely_excuses_self", **kwargs: Any) -> str:
        reasons = {
            "politely_excuses_self": f"NPC politely excuses themselves and leaves {group_description}.",
            "abruptly_departs": f"NPC abruptly leaves {group_description} without a word.",
            "gets_distracted": f"NPC seems distracted and wanders off from {group_description}."
        }
        return reasons.get(reason, reasons["politely_excuses_self"])

@register_tool
class ShowPolitenessTool(Tool):
    """Display courteous behavior."""
    name = "show_politeness"
    description = "NPC displays polite behavior."

    def execute(self, gesture: str = "nod", target: Optional[str] = None, **kwargs: Any) -> str:
        to_target = f" towards {target}" if target else ""
        gestures = {
            "nod": f"NPC gives a polite nod{to_target}.",
            "smile": f"NPC offers a polite smile{to_target}.",
            "defer": f"NPC defers politely{to_target} in the conversation.",
            "thank_you": f"NPC says 'thank you' politely{to_target}."
        }
        return gestures.get(gesture, gestures["nod"])

@register_tool
class ShowImpatienceTool(Tool):
    """Display signs of being impatient."""
    name = "show_impatience"
    description = "NPC shows signs of impatience."

    def execute(self, behavior: str = "taps_foot", intensity: float = 0.5, **kwargs: Any) -> str:
        behaviors = {
            "taps_foot": "NPC taps their foot impatiently.",
            "sighs_loudly": "NPC lets out an audible sigh of impatience.",
            "checks_time": "NPC keeps checking the time, looking impatient.",
            "interrupts": "NPC impatiently tries to interrupt."
        }
        intensity_desc = "mildly" if intensity < 0.4 else "very" if intensity > 0.7 else "noticeably"
        behavior_text = behaviors.get(behavior, behaviors["taps_foot"])
        return f"NPC {intensity_desc} {behavior_text}"