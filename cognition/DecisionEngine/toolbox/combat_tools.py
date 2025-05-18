from __future__ import annotations

from typing import Any, Dict, Optional

from . import register_tool
from .tool_base import Tool


@register_tool
class AttackTool(Tool):
    """Initiate an attack on a target."""
    
    name = "attack"
    description = "NPC attacks a target."
    
    def execute(self, target: str = "the threat", strength: float = 0.5, **kwargs: Any) -> str:
        """
        Execute an attack with variable strength.
        
        Args:
            target: Who/what to attack
            strength: Attack intensity (0.0-1.0)
        """
        if strength < 0.3:
            return f"NPC makes a hesitant, weak attack toward {target}."
        elif strength < 0.7:
            return f"NPC attacks {target} with moderate force."
        else:
            return f"NPC launches a powerful, aggressive attack at {target}!"


@register_tool
class DefendTool(Tool):
    """Take a defensive posture."""
    
    name = "defend"
    description = "NPC adopts a defensive stance."
    
    def execute(self, style: str = "cautious", **kwargs: Any) -> str:
        """
        Execute a defensive maneuver.
        
        Args:
            style: Defense style (cautious, aggressive, balanced)
        """
        if style == "aggressive":
            return "NPC adopts an aggressive defensive posture, ready to counter-attack."
        elif style == "balanced":
            return "NPC takes a balanced defensive stance, watching for openings."
        else:  # cautious
            return "NPC assumes a cautious defensive position, prioritizing protection."


@register_tool
class ThreatenTool(Tool):
    """Make a threatening gesture or statement."""
    
    name = "threaten"
    description = "NPC makes a threat to intimidate."
    
    def execute(self, threat_type: str = "verbal", intensity: float = 0.5, **kwargs: Any) -> str:
        """
        Execute a threatening action.
        
        Args:
            threat_type: Type of threat (verbal, physical, display_weapon)
            intensity: How intense the threat is (0.0-1.0)
        """
        intensity_desc = "mildly" if intensity < 0.4 else "severely" if intensity > 0.7 else "firmly"
        
        if threat_type == "physical":
            return f"NPC {intensity_desc} threatens with aggressive body language and posturing."
        elif threat_type == "display_weapon":
            return f"NPC {intensity_desc} threatens by displaying their weapon menacingly."
        else:  # verbal
            return f"NPC {intensity_desc} threatens with intimidating words."


@register_tool
class DisarmTool(Tool):
    """Attempt to disarm an opponent."""
    
    name = "disarm"
    description = "NPC tries to remove a weapon from target."
    
    def execute(self, target: str = "the opponent", **kwargs: Any) -> str:
        """Execute a disarming maneuver."""
        return f"NPC attempts to disarm {target}."


@register_tool
class StunTool(Tool):
    """Temporarily incapacitate a target."""
    
    name = "stun"
    description = "NPC attempts to momentarily incapacitate target."
    
    def execute(self, method: str = "physical", target: str = "the opponent", **kwargs: Any) -> str:
        """
        Execute a stunning attack.
        
        Args:
            method: How to stun (physical, magical, verbal)
            target: Who to stun
        """
        if method == "magical":
            return f"NPC casts a stunning spell at {target}."
        elif method == "verbal":
            return f"NPC shouts a disorienting remark at {target}."
        else:  # physical
            return f"NPC attempts to physically stun {target}." 