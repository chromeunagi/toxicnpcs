from __future__ import annotations

from typing import Any, Dict, Optional

from . import register_tool
from .tool_base import Tool


@register_tool
class SearchAreaTool(Tool):
    """Search the immediate surroundings for something."""
    
    name = "search_area"
    description = "NPC searches an area for something specific or general reconnaissance."
    
    def execute(self, target: str = "anything unusual", area: str = "the surroundings", thoroughness: float = 0.5, **kwargs: Any) -> str:
        """
        Search an area for something.
        
        Args:
            target: What to look for
            area: Where to search
            thoroughness: How thorough the search is (0.0-1.0)
        """
        if thoroughness < 0.3:
            return f"NPC quickly glances around {area}, looking for {target}."
        elif thoroughness < 0.7:
            return f"NPC methodically searches {area} for {target}."
        else:
            return f"NPC meticulously investigates every part of {area}, determined to find {target}."


@register_tool
class InteractEnvironmentTool(Tool):
    """Interact with an environmental object or feature."""
    
    name = "interact_environment"
    description = "NPC interacts with an object or feature in the environment."
    
    def execute(self, object_name: str = "the object", interaction: str = "examines", **kwargs: Any) -> str:
        """
        Interact with something in the environment.
        
        Args:
            object_name: The feature to interact with
            interaction: How to interact (examines, touches, activates, breaks, moves)
        """
        return f"NPC {interaction} {object_name}."


@register_tool
class CreateDistraction(Tool):
    """Create a distraction to divert attention."""
    
    name = "create_distraction"
    description = "NPC creates a distraction to divert attention."
    
    def execute(self, method: str = "noise", scale: str = "moderate", **kwargs: Any) -> str:
        """
        Create a distraction.
        
        Args:
            method: Distraction method (noise, visual, staged_event, thrown_object)
            scale: How big the distraction is (subtle, moderate, dramatic)
        """
        scale_desc = scale
        
        if method == "noise":
            return f"NPC creates a {scale_desc} noise to cause a distraction."
        elif method == "visual":
            return f"NPC creates a {scale_desc} visual distraction to divert attention."
        elif method == "staged_event":
            return f"NPC stages a {scale_desc} event to distract observers."
        elif method == "thrown_object":
            return f"NPC throws something to create a {scale_desc} distraction."
        else:
            return f"NPC creates a {scale_desc} distraction."


@register_tool
class SetTrapTool(Tool):
    """Prepare a trap or ambush."""
    
    name = "set_trap"
    description = "NPC prepares a trap or ambush."
    
    def execute(self, trap_type: str = "simple", target: str = "enemies", **kwargs: Any) -> str:
        """
        Set a trap for someone.
        
        Args:
            trap_type: Kind of trap (simple, elaborate, ambush, warning)
            target: Who the trap is for
        """
        if trap_type == "elaborate":
            return f"NPC carefully sets up an elaborate trap to catch {target}."
        elif trap_type == "ambush":
            return f"NPC prepares an ambush position to surprise {target}."
        elif trap_type == "warning":
            return f"NPC sets a trap that will warn of {target} approaching."
        else:  # simple
            return f"NPC quickly sets a simple trap for {target}."


@register_tool
class ListenTool(Tool):
    """Listen carefully to detect sounds."""
    
    name = "listen"
    description = "NPC listens carefully to the environment."
    
    def execute(self, focus: str = "surroundings", intensity: float = 0.5, **kwargs: Any) -> str:
        """
        Listen to detect sounds.
        
        Args:
            focus: What to listen for/to
            intensity: How intensely focused (0.0-1.0)
        """
        if intensity < 0.3:
            return f"NPC casually listens to {focus}."
        elif intensity < 0.7:
            return f"NPC attentively listens to {focus}."
        else:
            return f"NPC listens intently to {focus}, blocking out all other distractions." 