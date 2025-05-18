from __future__ import annotations

from typing import Any, Dict, Optional

from . import register_tool
from .tool_base import Tool


@register_tool
class UseItemTool(Tool):
    """Use an item for its intended purpose."""
    
    name = "use_item"
    description = "NPC uses an item."
    
    def execute(self, item: str = "an item", target: str = "appropriately", **kwargs: Any) -> str:
        """
        Use an item on a target.
        
        Args:
            item: The item to use
            target: What to use it on
        """
        return f"NPC uses {item} on {target}."


@register_tool
class GiveItemTool(Tool):
    """Offer or hand over an item to someone."""
    
    name = "give_item"
    description = "NPC gives an item to someone."
    
    def execute(self, item: str = "an item", recipient: str = "the player", manner: str = "neutral", **kwargs: Any) -> str:
        """
        Give an item to someone.
        
        Args:
            item: The item to give
            recipient: Who to give it to
            manner: How to give it (reluctantly, eagerly, cautiously, ceremoniously)
        """
        if manner == "reluctantly":
            return f"NPC reluctantly hands {item} to {recipient}."
        elif manner == "eagerly":
            return f"NPC eagerly presents {item} to {recipient}."
        elif manner == "cautiously":
            return f"NPC cautiously offers {item} to {recipient}."
        elif manner == "ceremoniously":
            return f"NPC ceremoniously bestows {item} upon {recipient}."
        else:  # neutral
            return f"NPC gives {item} to {recipient}."


@register_tool
class TakeItemTool(Tool):
    """Acquire an item from someone or somewhere."""
    
    name = "take_item"
    description = "NPC takes an item."
    
    def execute(self, item: str = "an item", source: str = "nearby", **kwargs: Any) -> str:
        """
        Take an item from somewhere.
        
        Args:
            item: The item to take
            source: Where to take it from
        """
        return f"NPC takes {item} from {source}."


@register_tool
class ExamineItemTool(Tool):
    """Inspect an item closely."""
    
    name = "examine_item"
    description = "NPC carefully examines an item."
    
    def execute(self, item: str = "an item", thoroughness: float = 0.5, **kwargs: Any) -> str:
        """
        Examine an item with variable thoroughness.
        
        Args:
            item: The item to examine
            thoroughness: How carefully to examine (0.0-1.0)
        """
        if thoroughness < 0.3:
            return f"NPC gives {item} a quick glance."
        elif thoroughness < 0.7:
            return f"NPC examines {item} with moderate attention."
        else:
            return f"NPC scrutinizes {item} with intense focus and thoroughness."


@register_tool
class EquipItemTool(Tool):
    """Put on or ready an item for use."""
    
    name = "equip_item"
    description = "NPC equips or readies an item."
    
    def execute(self, item: str = "a weapon", **kwargs: Any) -> str:
        """
        Equip or ready an item.
        
        Args:
            item: The item to equip
        """
        weapon_terms = ["sword", "dagger", "axe", "mace", "bow", "crossbow", "gun", "blade", "weapon"]
        armor_terms = ["armor", "shield", "helmet", "breastplate", "gauntlets", "protective"]
        
        # Detect item type for more specific messaging
        if any(term in item.lower() for term in weapon_terms):
            return f"NPC readies {item}, prepared to fight."
        elif any(term in item.lower() for term in armor_terms):
            return f"NPC puts on {item} for protection."
        else:
            return f"NPC equips {item}."


@register_tool
class CraftItemTool(Tool):
    """Create something from components."""
    
    name = "craft_item"
    description = "NPC crafts something from available materials."
    
    def execute(self, item: str = "an item", quality: float = 0.5, **kwargs: Any) -> str:
        """
        Craft an item with variable quality.
        
        Args:
            item: The item to craft
            quality: Craftsmanship quality (0.0-1.0)
        """
        if quality < 0.3:
            return f"NPC hastily cobbles together {item}, with poor results."
        elif quality < 0.7:
            return f"NPC crafts {item} with adequate skill."
        else:
            return f"NPC meticulously crafts {item} with exceptional skill." 