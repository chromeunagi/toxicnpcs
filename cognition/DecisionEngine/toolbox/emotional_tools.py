from __future__ import annotations

from typing import Any, Dict, Optional
from random import choice

from . import register_tool
from .tool_base import Tool


@register_tool
class ExpressEmotionTool(Tool):
    """Display an emotional reaction."""
    
    name = "express_emotion"
    description = "NPC expresses a specific emotion."
    
    def execute(self, emotion: str = "neutral", intensity: float = 0.5, **kwargs: Any) -> str:
        """
        Express an emotional state.
        
        Args:
            emotion: The emotion to express (anger, fear, joy, sadness, surprise, disgust)
            intensity: How strongly to express it (0.0-1.0)
        """
        intensity_desc = "mildly" if intensity < 0.4 else "intensely" if intensity > 0.7 else "visibly"
        
        emotion_expressions = {
            "anger": [
                f"NPC {intensity_desc} frowns and clenches their fists in anger.",
                f"NPC {intensity_desc} glares with obvious fury.",
                f"NPC's face reddens as they {intensity_desc} express their anger."
            ],
            "fear": [
                f"NPC {intensity_desc} trembles with fear.",
                f"NPC's eyes widen in {intensity_desc} terror.",
                f"NPC {intensity_desc} shrinks back in fear."
            ],
            "joy": [
                f"NPC {intensity_desc} smiles with joy.",
                f"NPC's face lights up with {intensity_desc} happiness.",
                f"NPC {intensity_desc} laughs in delight."
            ],
            "sadness": [
                f"NPC {intensity_desc} looks downcast and sad.",
                f"NPC's shoulders slump in {intensity_desc} sadness.",
                f"NPC's eyes well up with {intensity_desc} sorrow."
            ],
            "surprise": [
                f"NPC {intensity_desc} gasps in surprise.",
                f"NPC's eyes widen with {intensity_desc} shock.",
                f"NPC {intensity_desc} jumps back, startled."
            ],
            "disgust": [
                f"NPC {intensity_desc} curls their lip in disgust.",
                f"NPC {intensity_desc} recoils with revulsion.",
                f"NPC's face shows {intensity_desc} repulsion."
            ],
            "neutral": [
                "NPC maintains a neutral expression.",
                "NPC shows no particular emotion.",
                "NPC keeps their feelings hidden."
            ]
        }
        
        # Default to neutral if emotion not found
        expressions = emotion_expressions.get(emotion.lower(), emotion_expressions["neutral"])
        return choice(expressions)


@register_tool
class LaughTool(Tool):
    """Express amusement or other emotions through laughter."""
    
    name = "laugh"
    description = "NPC laughs in response to stimulus."
    
    def execute(self, laugh_type: str = "genuine", **kwargs: Any) -> str:
        """
        Express amusement through laughter.
        
        Args:
            laugh_type: Type of laugh (genuine, nervous, mocking, polite)
        """
        if laugh_type == "nervous":
            return "NPC laughs nervously, clearly uncomfortable."
        elif laugh_type == "mocking":
            return "NPC laughs mockingly with derision."
        elif laugh_type == "polite":
            return "NPC gives a polite, restrained laugh."
        else:  # genuine
            return "NPC laughs genuinely with amusement."


@register_tool
class CryTool(Tool):
    """Express sadness or other emotions through crying."""
    
    name = "cry"
    description = "NPC cries in response to stimulus."
    
    def execute(self, cry_type: str = "sadness", intensity: float = 0.5, **kwargs: Any) -> str:
        """
        Express emotion through crying.
        
        Args:
            cry_type: Reason for crying (sadness, joy, fear, anger)
            intensity: How intensely (0.0-1.0)
        """
        if intensity < 0.3:
            prefix = "NPC's eyes well up as they"
        elif intensity < 0.7:
            prefix = "NPC cries as they"
        else:
            prefix = "NPC sobs uncontrollably as they"
            
        if cry_type == "joy":
            return f"{prefix} experience overwhelming happiness."
        elif cry_type == "fear":
            return f"{prefix} face their terror."
        elif cry_type == "anger":
            return f"{prefix} express their intense frustration."
        else:  # sadness
            return f"{prefix} process their sadness."


@register_tool
class ShowConfusionTool(Tool):
    """Express puzzlement or lack of understanding."""
    
    name = "show_confusion"
    description = "NPC displays confusion or puzzlement."
    
    def execute(self, **kwargs: Any) -> str:
        """Express confusion through body language and expression."""
        confusion_expressions = [
            "NPC tilts their head and furrows their brow in confusion.",
            "NPC looks bewildered, clearly not understanding.",
            "NPC scratches their head, visibly confused.",
            "NPC blinks repeatedly in puzzlement."
        ]
        return choice(confusion_expressions)


@register_tool
class PanicTool(Tool):
    """Express extreme fear or anxiety."""
    
    name = "panic"
    description = "NPC displays signs of panic or extreme anxiety."
    
    def execute(self, containment: float = 0.5, **kwargs: Any) -> str:
        """
        Express panic at variable levels of control.
        
        Args:
            containment: How well the panic is contained (0.0 = complete loss of control, 1.0 = mostly contained)
        """
        if containment < 0.3:
            return "NPC completely loses control in blind panic, flailing and crying out."
        elif containment < 0.7:
            return "NPC struggles to contain their rising panic, breathing rapidly and looking fearful."
        else:
            return "NPC shows signs of internal panic while trying to maintain composure." 