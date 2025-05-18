from __future__ import annotations

from typing import Any, Dict
from random import choice

from . import register_tool
from .tool_base import Tool


@register_tool
class DialogueResponseTool(Tool):
    """Respond to dialogue stimulus with generated speech."""

    name = "dialogue_response"
    description = "Generates an in-character dialogue response."

    def execute(self, prompt: str | None = None, tone: str = "neutral", 
                personality_context: Dict = None, **kwargs: Any) -> str:
        """
        Generate a dialogue response with variable tone.
        
        Args:
            prompt: The stimulus to respond to
            tone: Response tone (neutral, friendly, hostile, formal, casual, defensive)
            personality_context: Context about NPC personality to influence response
        """
        if prompt is None:
            prompt = "Hello."
            
        # Placeholder for LLM call – here we do simple transformations based on tone
        # In a production implementation, this would be replaced with actual LLM calls
        if tone == "friendly":
            return f"NPC responds warmly: 'I'm glad you said {prompt[:20]}... let's talk more about that.'"
        elif tone == "hostile":
            return f"NPC snaps angrily: 'How dare you say {prompt[:20]}!'"
        elif tone == "formal":
            return f"NPC replies with formality: 'Regarding your statement about {prompt[:20]}, I must respond thusly...'"
        elif tone == "casual":
            return f"NPC casually says: 'Oh, {prompt[:20]}? Yeah, whatever.'"
        elif tone == "defensive":
            return f"NPC defensively responds: 'I never said anything about {prompt[:20]}! Don't put words in my mouth!'"
        else:  # neutral
            return f"NPC replies: '{prompt[::-1]}'"  # silly reversed text as placeholder


@register_tool
class AskQuestionTool(Tool):
    """Ask a specific question."""

    name = "ask_question"
    description = "NPC asks a specific question."

    def execute(self, topic: str = "the situation", question_type: str = "open", **kwargs: Any) -> str:
        """
        Ask a question about a topic.
        
        Args:
            topic: What to ask about
            question_type: Type of question (open, closed, rhetorical, leading)
        """
        open_questions = [
            f"NPC asks: 'What do you think about {topic}?'",
            f"NPC inquires: 'How would you describe {topic}?'",
            f"NPC questions: 'Can you tell me more about {topic}?'"
        ]
        
        closed_questions = [
            f"NPC asks: 'Do you know about {topic}?'",
            f"NPC inquires: 'Have you dealt with {topic} before?'",
            f"NPC questions: 'Is {topic} important to you?'"
        ]
        
        rhetorical_questions = [
            f"NPC muses: 'Who really understands {topic}, anyway?'",
            f"NPC says rhetorically: 'Isn't {topic} just the strangest thing?'",
            f"NPC asks: 'Why do we even bother with {topic}?'"
        ]
        
        leading_questions = [
            f"NPC suggests: 'You do realize that {topic} is dangerous, right?'",
            f"NPC asks leadingly: 'Surely you wouldn't disagree about {topic}?'",
            f"NPC probes: 'You're planning something with {topic}, aren't you?'"
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

    def execute(self, topic: str = "their thoughts", style: str = "neutral", length: str = "medium", **kwargs: Any) -> str:
        """
        Deliver a monologue on a topic.
        
        Args:
            topic: Subject of the monologue
            style: Delivery style (neutral, dramatic, philosophical, rambling)
            length: Monologue length (brief, medium, extended)
        """
        length_prefix = ""
        if length == "brief":
            length_prefix = "a brief "
        elif length == "extended":
            length_prefix = "a lengthy "
        else:  # medium
            length_prefix = "a "
            
        if style == "dramatic":
            return f"NPC delivers {length_prefix}dramatic monologue about {topic}, gesturing passionately."
        elif style == "philosophical":
            return f"NPC shares {length_prefix}philosophical discourse on the nature of {topic}."
        elif style == "rambling":
            return f"NPC goes on {length_prefix}rambling tangent about {topic}, barely pausing for breath."
        else:  # neutral
            return f"NPC gives {length_prefix}measured speech about {topic}."


@register_tool
class FleeTool(Tool):
    """Initiate flight behavior (run away)."""

    name = "flee"
    description = "NPC attempts to flee from danger."

    def execute(self, speed: str = "fast", direction: str = "away", caution_level: float = 0.5, **kwargs: Any) -> str:
        """
        Execute flight behavior.
        
        Args:
            speed: How quickly to flee (slow, moderate, fast, panicked)
            direction: Where to flee to
            caution_level: How careful to be while fleeing (0.0-1.0)
        """
        caution_desc = ""
        if caution_level > 0.7:
            caution_desc = "cautiously "
        elif caution_level < 0.3:
            caution_desc = "recklessly "
            
        if speed == "slow":
            return f"NPC {caution_desc}backs away slowly toward {direction}."
        elif speed == "moderate":
            return f"NPC {caution_desc}moves quickly but steadily toward {direction}."
        elif speed == "panicked":
            return f"NPC {caution_desc}flees in panic toward {direction}, abandoning all else."
        else:  # fast
            return f"NPC {caution_desc}turns and runs away to seek safety." 