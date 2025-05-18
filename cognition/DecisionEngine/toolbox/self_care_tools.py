from __future__ import annotations

from typing import Any, Dict, Optional
from random import choice

from . import register_tool
from .tool_base import Tool


@register_tool
class EatTool(Tool):
    """Consume food."""
    name = "eat"
    description = "NPC eats some food."

    def execute(self, food_item: str = "nearby food", manner: str = "casually", **kwargs: Any) -> str:
        manners = {
            "casually": f"NPC casually eats some {food_item}.",
            "ravenously": f"NPC ravenously devours {food_item}.",
            "politely": f"NPC politely partakes of {food_item}.",
            "suspiciously": f"NPC suspiciously nibbles at {food_item}."
        }
        return manners.get(manner, manners["casually"])


@register_tool
class DrinkTool(Tool):
    """Consume a beverage."""
    name = "drink"
    description = "NPC drinks something."

    def execute(self, beverage_item: str = "water", manner: str = "normally", **kwargs: Any) -> str:
        manners = {
            "normally": f"NPC drinks some {beverage_item}.",
            "thirstily": f"NPC thirstily gulps down {beverage_item}.",
            "slowly": f"NPC slowly sips their {beverage_item}.",
            "warily": f"NPC warily tastes the {beverage_item}."
        }
        return manners.get(manner, manners["normally"])


@register_tool
class RestTool(Tool):
    """Take a break to recover energy."""
    name = "rest"
    description = "NPC rests for a moment."

    def execute(self, duration: str = "briefly", posture: str = "sits_down", **kwargs: Any) -> str:
        postures = {
            "sits_down": "sits down to rest",
            "leans_against_wall": "leans against a wall to rest",
            "closes_eyes": "closes their eyes and rests"
        }
        return f"NPC {postures.get(posture, postures['sits_down'])} {duration}."


@register_tool
class GroomTool(Tool):
    """Attend to personal appearance."""
    name = "groom"
    description = "NPC attends to their grooming."

    def execute(self, activity: str = "smooths_clothes", **kwargs: Any) -> str:
        activities = {
            "smooths_clothes": "NPC smooths their clothes.",
            "adjusts_hair": "NPC adjusts their hair.",
            "checks_reflection": "NPC briefly checks their reflection if possible."
        }
        return activities.get(activity, activities["smooths_clothes"])


@register_tool
class SeekComfortTool(Tool):
    """Try to find something to alleviate distress or discomfort."""
    name = "seek_comfort"
    description = "NPC seeks comfort."

    def execute(self, method: str = "find_quiet_place", **kwargs: Any) -> str:
        methods = {
            "find_quiet_place": "NPC looks for a quiet place to compose themselves.",
            "fidget_object": "NPC fiddles with a small object for comfort.",
            "self_soothe_gesture": "NPC performs a self-soothing gesture, like rubbing their arm."
        }
        return methods.get(method, methods["find_quiet_place"])


@register_tool
class StretchTool(Tool):
    """Extend limbs or body to relieve stiffness."""
    name = "stretch"
    description = "NPC stretches their body."

    def execute(self, **kwargs: Any) -> str:
        stretches = [
            "NPC stretches their arms and back.",
            "NPC rolls their shoulders and neck.",
            "NPC lets out a small yawn as they stretch."
        ]
        return choice(stretches) 