from __future__ import annotations

from typing import Any, Dict, Optional
from random import choice

from . import register_tool
from .tool_base import Tool


@register_tool
class PersuadeTool(Tool):
    """Attempt to convince someone of something."""
    name = "persuade"
    description = "NPC tries to persuade someone."

    def execute(self, target: str = "the player", topic: str = "a course of action", 
                approach: str = "logical", intensity: float = 0.6, **kwargs: Any) -> str:
        approaches = {
            "logical": f"NPC presents a logical argument to {target} regarding {topic}.",
            "emotional": f"NPC makes an emotional appeal to {target} about {topic}.",
            "authoritative": f"NPC speaks with authority, trying to persuade {target} about {topic}.",
            "charming": f"NPC uses charm to try and win {target} over regarding {topic}."
        }
        return approaches.get(approach, approaches["logical"]) + f" (Intensity: {intensity:.2f})"


@register_tool
class DeceiveTool(Tool):
    """Attempt to mislead someone."""
    name = "deceive"
    description = "NPC attempts to deceive someone."

    def execute(self, target: str = "the player", topic: str = "a secret", 
                method: str = "omission", confidence: float = 0.7, **kwargs: Any) -> str:
        methods = {
            "omission": f"NPC carefully avoids mentioning key details about {topic} to {target}.",
            "misdirection": f"NPC tries to misdirect {target}'s attention away from {topic}.",
            "outright_lie": f"NPC tells an outright lie to {target} about {topic}.",
            "half_truth": f"NPC tells {target} a half-truth regarding {topic}, mixing facts with falsehoods."
        }
        return methods.get(method, methods["omission"]) + f" (Confidence: {confidence:.2f})"


@register_tool
class GossipTool(Tool):
    """Share unverified information about someone or something."""
    name = "gossip"
    description = "NPC shares some gossip."

    def execute(self, about_who: str = "another character", juicy_detail: str = "a rumor", 
                tone: str = "conspiratorial", **kwargs: Any) -> str:
        tones = {
            "conspiratorial": f"NPC leans in and whispers conspiratorially about {about_who} concerning {juicy_detail}.",
            "scandalized": f"NPC gasps, sharing scandalous gossip about {about_who} regarding {juicy_detail}.",
            "gleeful": f"NPC shares gossip about {about_who} with thinly veiled glee, focusing on {juicy_detail}."
        }
        return tones.get(tone, tones["conspiratorial"])


@register_tool
class ComplainTool(Tool):
    """Express dissatisfaction or annoyance."""
    name = "complain"
    description = "NPC complains about something."

    def execute(self, topic: str = "the situation", intensity: float = 0.5, 
                target_audience: Optional[str] = None, **kwargs: Any) -> str:
        to_whom = f" to {target_audience}" if target_audience else " to anyone who will listen"
        intensity_desc = "mildly" if intensity < 0.4 else "bitterly" if intensity > 0.7 else "vehemently"
        return f"NPC complains {intensity_desc} about {topic}{to_whom}."


@register_tool
class ComfortTool(Tool):
    """Offer solace or reassurance."""
    name = "comfort"
    description = "NPC attempts to comfort someone."

    def execute(self, target: str = "the player", method: str = "verbal", 
                sincerity: float = 0.8, **kwargs: Any) -> str:
        methods = {
            "verbal": f"NPC offers comforting words to {target}.",
            "physical": f"NPC gently pats {target} on the shoulder in a comforting gesture.",
            "empathetic_listening": f"NPC listens empathetically to {target}'s troubles."
        }
        return methods.get(method, methods["verbal"]) + f" (Sincerity: {sincerity:.2f})"


@register_tool
class EncourageTool(Tool):
    """Offer support or motivation."""
    name = "encourage"
    description = "NPC encourages someone."

    def execute(self, target: str = "the player", task: str = "their current endeavor", 
                optimism_level: float = 0.7, **kwargs: Any) -> str:
        encouragements = [
            f"NPC tells {target}, 'You can do it! I believe in you regarding {task}!'",
            f"NPC offers encouragement to {target} for {task}, highlighting their strengths.",
            f"NPC tries to boost {target}'s confidence for {task}."
        ]
        return choice(encouragements) + f" (Optimism: {optimism_level:.2f})"


@register_tool
class AdviseTool(Tool):
    """Offer guidance or a recommendation."""
    name = "advise"
    description = "NPC offers advice."

    def execute(self, target: str = "the player", topic: str = "a difficult choice", 
                wisdom_level: float = 0.6, **kwargs: Any) -> str:
        if wisdom_level > 0.7:
            return f"NPC offers sage advice to {target} concerning {topic}."
        elif wisdom_level > 0.4:
            return f"NPC gives {target} some practical advice about {topic}."
        else:
            return f"NPC hesitantly offers some questionable advice to {target} about {topic}."


@register_tool
class ArgueTool(Tool):
    """Engage in a disagreement or debate."""
    name = "argue"
    description = "NPC argues a point."

    def execute(self, target: str = "the player", point: str = "a contentious issue", 
                style: str = "heated", stubbornness: float = 0.7, **kwargs: Any) -> str:
        styles = {
            "heated": f"NPC gets into a heated argument with {target} over {point}.",
            "logical": f"NPC attempts a logical debate with {target} about {point}.",
            "passive_aggressive": f"NPC makes passive-aggressive remarks while arguing with {target} about {point}."
        }
        return styles.get(style, styles["heated"]) + f" (Stubbornness: {stubbornness:.2f})"

# More tools can be added here: ShareInformation, TellStory, AskFavor, ExpressOpinion, Interrupt, ChangeSubject etc. 