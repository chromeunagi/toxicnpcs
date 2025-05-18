from __future__ import annotations

from typing import Any, Dict, Optional
from random import choice

from . import register_tool
from .tool_base import Tool


@register_tool
class ObservePersonTool(Tool):
    """Carefully watch a person to gather details."""
    name = "observe_person"
    description = "NPC observes a person closely."

    def execute(self, target: str = "the player", focus: str = "general_demeanor", 
                intensity: float = 0.6, **kwargs: Any) -> str:
        focus_points = {
            "general_demeanor": f"NPC observes {target}'s general demeanor and posture.",
            "facial_expressions": f"NPC studies {target}'s facial expressions for subtle cues.",
            "body_language": f"NPC carefully watches {target}'s body language.",
            "attire_and_belongings": f"NPC notes {target}'s attire and any visible belongings."
        }
        subtlety = "discreetly" if intensity < 0.5 else "intently"
        return f"NPC {subtlety} {focus_points.get(focus, focus_points['general_demeanor'])}"


@register_tool
class ObserveEnvironmentTool(Tool):
    """Scan the surroundings for points of interest or changes."""
    name = "observe_environment"
    description = "NPC observes their surroundings."

    def execute(self, area: str = "the immediate area", detail_level: str = "general_scan", 
                purpose: str = "situational_awareness", **kwargs: Any) -> str:
        purposes = {
            "situational_awareness": f"NPC scans {area} for situational awareness.",
            "look_for_threats": f"NPC cautiously scans {area} for any potential threats.",
            "find_object": f"NPC searches {area} for a specific object.",
            "notice_changes": f"NPC looks around {area}, trying to notice any recent changes."
        }
        return purposes.get(purpose, purposes["situational_awareness"]) + f" (Detail: {detail_level})"


@register_tool
class EavesdropTool(Tool):
    """Attempt to secretly listen to a conversation."""
    name = "eavesdrop"
    description = "NPC tries to eavesdrop on a conversation."

    def execute(self, target_conversation: str = "a nearby conversation", 
                discretion_level: float = 0.7, **kwargs: Any) -> str:
        if discretion_level > 0.8:
            return f"NPC very discreetly attempts to overhear {target_conversation}."
        elif discretion_level > 0.4:
            return f"NPC tries to subtly listen in on {target_conversation}."
        else:
            return f"NPC poorly attempts to eavesdrop on {target_conversation}, likely being noticed."


@register_tool
class ReadBodyLanguageTool(Tool):
    """Interpret someone's non-verbal cues."""
    name = "read_body_language"
    description = "NPC attempts to interpret body language."

    def execute(self, target: str = "the player", accuracy_chance: float = 0.6, **kwargs: Any) -> str:
        # This is a simplified representation. True interpretation would be complex.
        interpretations = [
            f"NPC tries to read {target}'s body language, sensing some nervousness.",
            f"NPC interprets {target}'s posture as confident and open.",
            f"NPC senses hidden tension in {target}'s stance.",
            f"NPC is unsure what to make of {target}'s current body language."
        ]
        if accuracy_chance > 0.7:
            return f"NPC keenly observes {target}'s body language, gaining insight. ({choice(interpretations) })"
        elif accuracy_chance > 0.4:
            return f"NPC attempts to decipher {target}'s body language. ({choice(interpretations) })"
        else:
            return f"NPC struggles to interpret {target}'s body language. (NPC seems confused by the signals.)"


@register_tool
class InvestigateAnomalyTool(Tool):
    """Look into something unusual or out of place."""
    name = "investigate_anomaly"
    description = "NPC investigates something strange."

    def execute(self, anomaly: str = "a strange noise", caution_level: float = 0.5, **kwargs: Any) -> str:
        if caution_level > 0.7:
            return f"NPC cautiously approaches to investigate {anomaly}."
        elif caution_level > 0.3:
            return f"NPC investigates {anomaly} with moderate caution."
        else:
            return f"NPC recklessly rushes to investigate {anomaly}." 