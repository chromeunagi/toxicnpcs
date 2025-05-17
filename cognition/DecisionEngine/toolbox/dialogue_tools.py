from __future__ import annotations

from typing import Any

from . import register_tool
from .tool_base import Tool


@register_tool
class DialogueResponseTool(Tool):
    """Respond to dialogue stimulus with generated speech (stub)."""

    name = "dialogue_response"
    description = "Generates an in-character dialogue response."

    def execute(self, prompt: str | None = None, **kwargs: Any) -> str:
        # Placeholder for LLM call – here we echo or simple transform.
        if prompt is None:
            prompt = "Hello."
        # Pretend we query an LLM and get a reply
        reply = f"NPC replies: '{prompt[::-1]}'"  # silly reversed text as placeholder
        return reply


@register_tool
class FleeTool(Tool):
    """Initiate flight behavior (run away)."""

    name = "flee"
    description = "NPC attempts to flee from danger."

    def execute(self, **kwargs: Any) -> str:
        return "NPC turns and runs away to seek safety." 