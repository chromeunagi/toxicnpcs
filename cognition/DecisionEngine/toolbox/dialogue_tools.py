from __future__ import annotations

from typing import Any, Dict, Optional
from random import choice

from . import register_tool
from .tool_base import Tool


@register_tool
class DialogueResponseTool(Tool):
    """Respond to dialogue stimulus with generated speech."""

    name = "dialogue_response"
    description = "Generates an in-character dialogue response."

    def execute(self, prompt: str | None = None, tone: str = "neutral", 
                dialogue_act: str = "statement", 
                personality_context: Optional[Dict] = None, **kwargs: Any) -> str:
        """
        Generate a dialogue response with variable tone and dialogue act.
        
        Args:
            prompt: The stimulus to respond to
            tone: Response tone (neutral, friendly, hostile, formal, casual, defensive, sarcastic, inquisitive, empathetic)
            dialogue_act: The type of speech act (statement, question, command, compliment, insult, apology, explanation, persuasion)
            personality_context: Context about NPC personality to influence response
        """
        if prompt is None:
            prompt = "Well..."
            
        # Placeholder for LLM call – here we do simple transformations based on tone and act
        prefix = f"NPC says (Tone: {tone}, Act: {dialogue_act}): "
        
        if dialogue_act == "question":
            return f"{prefix} 'Regarding {prompt[:30]}... what do you mean by that?'"
        elif dialogue_act == "command":
            return f"{prefix} 'Concerning {prompt[:30]}... you must listen to me!'"
        elif dialogue_act == "compliment":
            return f"{prefix} 'That's an interesting point about {prompt[:30]}. Well said!'"
        elif dialogue_act == "insult":
            return f"{prefix} 'Your comment about {prompt[:30]} is utterly ridiculous!'"
        elif dialogue_act == "apology":
            return f"{prefix} 'I may have misspoken regarding {prompt[:30]}. My apologies.'"
        elif dialogue_act == "explanation":
            return f"{prefix} 'Let me clarify about {prompt[:30]}... here's the situation.'"
        elif dialogue_act == "persuasion":
            return f"{prefix} 'Think about {prompt[:30]}... surely you can see my point?'"

        # Fallback to tone-based generic responses
        if tone == "friendly":
            return f"{prefix} 'I'm glad you mentioned {prompt[:20]}... let's discuss.'"
        elif tone == "hostile":
            return f"{prefix} 'How dare you bring up {prompt[:20]}!'"
        elif tone == "formal":
            return f"{prefix} 'Regarding your statement about {prompt[:20]}, my position is clear.'"
        elif tone == "casual":
            return f"{prefix} 'Oh, {prompt[:20]}? Sure, whatever you say.'"
        elif tone == "defensive":
            return f"{prefix} 'I stand by my words on {prompt[:20]}! I will not be moved!'"
        elif tone == "sarcastic":
            return f"{prefix} 'Oh, *really*? {prompt[:20]}? How utterly fascinating.'"
        elif tone == "inquisitive":
            return f"{prefix} 'Hmm, {prompt[:20]}... Tell me more about your thoughts on that.'"
        elif tone == "empathetic":
            return f"{prefix} 'I understand your feelings about {prompt[:20]}. It's a tough situation.'"
        else:  # neutral statement
            return f"{prefix} '{(prompt[::-1].capitalize()) if prompt else 'Indeed.'}'"


@register_tool
class DeceiveTool(Tool):
    """Attempt to mislead or lie to a target."""
    
    name = "deceive"
    description = "NPC attempts to tell a lie or mislead someone."
    
    def execute(self, target: str = "the player", deception_type: str = "omission", plausibility: float = 0.6, **kwargs: Any) -> str:
        # deception_type: omission, fabrication, exaggeration, minimization
        # plausibility: How believable the lie is (0.0-1.0)
        lie_strength = "a somewhat plausible" if plausibility > 0.5 else "a rather unconvincing"
        if deception_type == "fabrication":
            return f"NPC tells {target} {lie_strength} fabrication to mislead them."
        elif deception_type == "exaggeration":
            return f"NPC {lie_strength}ly exaggerates the truth to {target}."
        elif deception_type == "minimization":
            return f"NPC tries to downplay the situation to {target} with {lie_strength} minimization."
        else: # omission
            return f"NPC carefully omits key details while talking to {target}, attempting {lie_strength} deception."


@register_tool
class PersuadeTool(Tool):
    """Attempt to convince someone to do or believe something."""
    
    name = "persuade"
    description = "NPC tries to persuade someone of their viewpoint or to take an action."
    
    def execute(self, target: str = "the player", topic: str = "their course of action", method: str = "logic", **kwargs: Any) -> str:
        # method: logic, emotional_appeal, bargaining, threat (subtle)
        if method == "emotional_appeal":
            return f"NPC makes an emotional appeal to {target} regarding {topic}."
        elif method == "bargaining":
            return f"NPC attempts to bargain with {target} to convince them about {topic}."
        elif method == "threat":
            return f"NPC subtly implies negative consequences if {target} doesn't agree about {topic}."
        else: # logic
            return f"NPC uses logical arguments to try and persuade {target} about {topic}."


@register_tool
class AskQuestionTool(Tool):
    """Ask a specific question."""

    name = "ask_question"
    description = "NPC asks a specific question."

    def execute(self, topic: str = "the situation", question_type: str = "open", directness: float = 0.7, **kwargs: Any) -> str:
        directness_desc = "pointedly" if directness > 0.7 else "indirectly" if directness < 0.3 else "directly"
        
        open_questions = [
            f"NPC {directness_desc} asks: 'What are your thoughts on {topic}?'",
            f"NPC {directness_desc} inquires: 'Could you elaborate on {topic}?'",
        ]
        closed_questions = [
            f"NPC {directness_desc} asks: 'Is it true that {topic}?'",
            f"NPC {directness_desc} questions: 'Are you involved with {topic}?'"
        ]
        rhetorical_questions = [
            f"NPC muses rhetorically: 'One has to wonder about {topic}, don't they?'",
        ]
        leading_questions = [
            f"NPC asks, leading the witness: 'Wouldn\'t you agree that {topic} is the main issue?'",
        ]
        
        if question_type == "closed":
            return choice(closed_questions)
        elif question_type == "rhetorical":
            return choice(rhetorical_questions)
        elif question_type == "leading":
            return choice(leading_questions)
        else:  # open
            return choice(open_questions)


@register_tool
class MonologueTool(Tool):
    """Deliver an extended statement without expecting response."""

    name = "monologue"
    description = "NPC delivers a monologue."

    def execute(self, topic: str = "their inner thoughts", style: str = "reflective", length: str = "medium", audience: Optional[str] = None, **kwargs: Any) -> str:
        length_desc = {"brief": "a brief", "medium": "a considered", "extended": "an extended"}.get(length, "a")
        audience_phrase = f" to {audience}" if audience else " (seemingly to themself)"

        if style == "dramatic":
            return f"NPC delivers {length_desc} dramatic monologue about {topic}{audience_phrase}, with grand gestures."
        elif style == "philosophical":
            return f"NPC shares {length_desc} philosophical musings on {topic}{audience_phrase}."
        elif style == "rambling":
            return f"NPC begins {length_desc} rambling speech concerning {topic}{audience_phrase}, jumping between points."
        elif style == "boasting":
            return f"NPC launches into {length_desc} boastful monologue about their achievements related to {topic}{audience_phrase}."
        elif style == "lamenting":
            return f"NPC expresses {length_desc} sorrowful lament about {topic}{audience_phrase}."
        else:  # reflective
            return f"NPC gives {length_desc} reflective speech about {topic}{audience_phrase}."


@register_tool
class FleeTool(Tool):
    """Initiate flight behavior (run away)."""

    name = "flee"
    description = "NPC attempts to flee from danger or an undesirable situation."

    def execute(self, speed: str = "fast", direction: str = "safety", caution_level: float = 0.5, reason: Optional[str] = None, **kwargs: Any) -> str:
        caution_desc = "cautiously" if caution_level > 0.7 else "recklessly" if caution_level < 0.3 else "quickly"
        reason_phrase = f" due to {reason}" if reason else ""
            
        if speed == "slow":
            return f"NPC {caution_desc} backs away slowly toward {direction}{reason_phrase}."
        elif speed == "moderate":
            return f"NPC {caution_desc} moves quickly but steadily toward {direction}{reason_phrase}."
        elif speed == "panicked":
            return f"NPC {caution_desc} flees in panic toward {direction}{reason_phrase}, abandoning all else."
        else:  # fast
            return f"NPC {caution_desc} turns and runs toward {direction}{reason_phrase}." 