from __future__ import annotations

from typing import Any, Dict, Optional

from . import register_tool
from .tool_base import Tool


@register_tool
class GreetTool(Tool):
    """Initiate social interaction with a greeting."""
    
    name = "greet"
    description = "NPC greets someone or responds to a greeting."
    
    def execute(self, target: str = "the player", formality: str = "neutral", **kwargs: Any) -> str:
        """
        Execute a greeting.
        
        Args:
            target: Who to greet
            formality: Greeting style (formal, casual, cold, warm)
        """
        if formality == "formal":
            return f"NPC formally greets {target} with proper etiquette."
        elif formality == "casual":
            return f"NPC casually says hello to {target}."
        elif formality == "cold":
            return f"NPC acknowledges {target} with a curt, cold greeting."
        elif formality == "warm":
            return f"NPC warmly welcomes {target} with enthusiasm."
        else:  # neutral
            return f"NPC greets {target}."


@register_tool
class OfferHelpTool(Tool):
    """Propose assistance to someone."""
    
    name = "offer_help"
    description = "NPC offers to help someone."
    
    def execute(self, target: str = "the player", task: str = "the current situation", **kwargs: Any) -> str:
        """
        Offer assistance to someone.
        
        Args:
            target: Who to help
            task: What help to offer
        """
        return f"NPC offers to help {target} with {task}."


@register_tool
class BargainTool(Tool):
    """Negotiate terms with someone."""
    
    name = "bargain"
    description = "NPC attempts to negotiate or bargain."
    
    def execute(self, target: str = "the player", offer: str = "a deal", stance: str = "neutral", **kwargs: Any) -> str:
        """
        Engage in negotiation.
        
        Args:
            target: Who to bargain with
            offer: What's being offered
            stance: Bargaining approach (desperate, firm, aggressive, collaborative)
        """
        if stance == "desperate":
            return f"NPC desperately tries to negotiate {offer} with {target}."
        elif stance == "firm":
            return f"NPC firmly states their terms for {offer} to {target}."
        elif stance == "aggressive":
            return f"NPC aggressively pushes for {offer} in negotiations with {target}."
        elif stance == "collaborative":
            return f"NPC suggests {offer} to {target} in a collaborative manner."
        else:  # neutral
            return f"NPC attempts to negotiate {offer} with {target}."


@register_tool
class RequestInfoTool(Tool):
    """Ask for information."""
    
    name = "request_info"
    description = "NPC asks for specific information."
    
    def execute(self, topic: str = "the situation", urgency: str = "normal", **kwargs: Any) -> str:
        """
        Ask a question to gather information.
        
        Args:
            topic: Subject to inquire about
            urgency: Question urgency (casual, normal, urgent, demanding)
        """
        if urgency == "casual":
            return f"NPC casually asks about {topic}."
        elif urgency == "urgent":
            return f"NPC urgently requests information about {topic}."
        elif urgency == "demanding":
            return f"NPC demands to know about {topic}."
        else:  # normal
            return f"NPC inquires about {topic}."


@register_tool
class BefriendTool(Tool):
    """Attempt to build rapport and friendship."""
    
    name = "befriend"
    description = "NPC tries to establish a friendly relationship."
    
    def execute(self, target: str = "the player", approach: str = "genuine", **kwargs: Any) -> str:
        """
        Try to build friendship with someone.
        
        Args:
            target: Who to befriend
            approach: Friendship approach (genuine, cautious, manipulative, enthusiastic)
        """
        if approach == "cautious":
            return f"NPC carefully attempts to build rapport with {target}."
        elif approach == "manipulative":
            return f"NPC tries to gain {target}'s trust with ulterior motives."
        elif approach == "enthusiastic":
            return f"NPC enthusiastically tries to befriend {target}."
        else:  # genuine
            return f"NPC makes a genuine effort to befriend {target}."


@register_tool
class ApologizeTool(Tool):
    """Express regret or remorse for an action."""
    
    name = "apologize"
    description = "NPC apologizes for something."
    
    def execute(self, target: str = "the player", sincerity: float = 0.5, **kwargs: Any) -> str:
        """
        Offer an apology.
        
        Args:
            target: Who to apologize to
            sincerity: How genuine the apology is (0.0-1.0)
        """
        if sincerity < 0.3:
            return f"NPC gives {target} a clearly insincere, forced apology."
        elif sincerity > 0.7:
            return f"NPC offers {target} a deeply sincere, heartfelt apology."
        else:
            return f"NPC apologizes to {target}." 