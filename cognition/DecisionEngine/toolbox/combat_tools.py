from __future__ import annotations

from typing import Any, Dict, Optional
from random import choice

from . import register_tool
from .tool_base import Tool


@register_tool
class AttackTool(Tool):
    """Initiate an attack on a target."""
    
    name = "attack"
    description = "NPC attacks a target."
    
    def execute(self, target: str = "the threat", strength: float = 0.5, weapon_used: Optional[str] = None, attack_type: str = "standard", **kwargs: Any) -> str:
        """
        Execute an attack with variable strength, weapon, and type.
        
        Args:
            target: Who/what to attack
            strength: Attack intensity (0.0-1.0)
            weapon_used: Specific weapon (e.g., 'short sword', 'fists', 'fireball spell')
            attack_type: Type of attack (standard, power_attack, quick_attack, aimed_shot, spell_cast)
        """
        weapon_phrase = f" with {weapon_used}" if weapon_used else ""
        
        if attack_type == "power_attack":
            return f"NPC winds up for a powerful {attack_type}{weapon_phrase} against {target}! Strength: {strength:.2f}."
        elif attack_type == "quick_attack":
            return f"NPC makes a swift {attack_type}{weapon_phrase} at {target}. Strength: {strength:.2f}."
        elif attack_type == "aimed_shot":
            return f"NPC carefully aims a shot{weapon_phrase} at {target}. Precision based on strength: {strength:.2f}."
        elif attack_type == "spell_cast" and weapon_used:
            return f"NPC casts {weapon_used} at {target} with power {strength:.2f}."
        
        # Default/standard attack based on strength
        if strength < 0.3:
            return f"NPC makes a hesitant, weak attack{weapon_phrase} toward {target}."
        elif strength < 0.7:
            return f"NPC attacks {target}{weapon_phrase} with moderate force."
        else:
            return f"NPC launches a powerful, aggressive attack{weapon_phrase} at {target}!"


@register_tool
class DefendTool(Tool):
    """Take a defensive posture."""
    
    name = "defend"
    description = "NPC adopts a defensive stance."
    
    def execute(self, style: str = "cautious", against_target: Optional[str] = None, duration: str = "momentarily", **kwargs: Any) -> str:
        """
        Execute a defensive maneuver.
        
        Args:
            style: Defense style (cautious, aggressive, balanced, parry, dodge, block)
            against_target: Specific target being defended against
            duration: How long to maintain defense (momentarily, sustained)
        """
        target_phrase = f" against {against_target}" if against_target else ""
        duration_phrase = f" ({duration})"
        
        if style == "aggressive":
            return f"NPC adopts an aggressive defensive posture{target_phrase}, ready to counter-attack{duration_phrase}."
        elif style == "balanced":
            return f"NPC takes a balanced defensive stance{target_phrase}, watching for openings{duration_phrase}."
        elif style == "parry":
            return f"NPC attempts to parry an incoming attack{target_phrase}{duration_phrase}."
        elif style == "dodge":
            return f"NPC tries to dodge an attack{target_phrase}{duration_phrase}."
        elif style == "block":
            return f"NPC raises their guard to block an attack{target_phrase}{duration_phrase}."
        else:  # cautious
            return f"NPC assumes a cautious defensive position{target_phrase}, prioritizing protection{duration_phrase}."


@register_tool
class TauntTool(Tool):
    """Provoke or mock an opponent."""
    
    name = "taunt"
    description = "NPC taunts or mocks an opponent to provoke a reaction."
    
    def execute(self, target: str = "the opponent", taunt_type: str = "insult", **kwargs: Any) -> str:
        taunts = {
            "insult": [
                f"NPC hurls a cutting insult at {target}.",
                f"NPC mocks {target}'s abilities."
            ],
            "challenge": [
                f"NPC boldly challenges {target} to a fight.",
                f"NPC questions {target}'s courage."
            ],
            "arrogant": [
                f"NPC boasts arrogantly to {target} about their own superiority.",
                f"NPC smirks condescendingly at {target}."
            ]
        }
        selected_taunts = taunts.get(taunt_type, taunts["insult"])
        return choice(selected_taunts)


@register_tool
class TacticalRepositionTool(Tool):
    """Move to a more advantageous position in combat."""
    
    name = "tactical_reposition"
    description = "NPC moves to a better combat position (e.g., flanking, high ground)."
    
    def execute(self, new_position: str = "flanking position", reason: str = "gain advantage", **kwargs: Any) -> str:
        return f"NPC tactically repositions to {new_position} to {reason}."


@register_tool
class ThreatenTool(Tool):
    """Make a threatening gesture or statement."""
    
    name = "threaten"
    description = "NPC makes a threat to intimidate."
    
    def execute(self, threat_type: str = "verbal", intensity: float = 0.5, target: Optional[str] = None, **kwargs: Any) -> str:
        intensity_desc = "mildly" if intensity < 0.4 else "severely" if intensity > 0.7 else "firmly"
        target_phrase = f" towards {target}" if target else ""
        
        if threat_type == "physical":
            return f"NPC {intensity_desc} threatens with aggressive body language and posturing{target_phrase}."
        elif threat_type == "display_weapon":
            return f"NPC {intensity_desc} threatens by displaying their weapon menacingly{target_phrase}."
        else:  # verbal
            return f"NPC {intensity_desc} threatens with intimidating words{target_phrase}."


@register_tool
class DisarmTool(Tool):
    """Attempt to disarm an opponent."""
    
    name = "disarm"
    description = "NPC tries to remove a weapon from target."
    
    def execute(self, target: str = "the opponent", technique: str = "forcefully", **kwargs: Any) -> str:
        return f"NPC attempts to {technique} disarm {target}."


@register_tool
class StunTool(Tool):
    """Temporarily incapacitate a target."""
    
    name = "stun"
    description = "NPC attempts to momentarily incapacitate target."
    
    def execute(self, method: str = "physical", target: str = "the opponent", duration_effect: str = "briefly", **kwargs: Any) -> str:
        if method == "magical":
            return f"NPC casts a stunning spell at {target}, aiming to incapacitate them {duration_effect}."
        elif method == "verbal":
            return f"NPC shouts a disorienting remark at {target}, hoping to confuse them {duration_effect}."
        else:  # physical
            return f"NPC attempts to physically stun {target}, trying to daze them {duration_effect}." 