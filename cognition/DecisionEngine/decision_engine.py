from __future__ import annotations

import random
from typing import Any, Dict, Type

from stimulus import (
    InterpretedStimulus,
    StimulusIntent,
    StimulusSchema,
)
from toolbox import get_tool, Tool


class DecisionEngine:
    """Selects and executes the best tool for a given interpreted stimulus."""

    def __init__(self, use_llm: bool = False) -> None:
        self.use_llm = use_llm

    # ------------------------------------------------------------------
    # PUBLIC INTERFACE
    # ------------------------------------------------------------------
    def decide_and_act(self, stimulus: InterpretedStimulus) -> str:
        """High-level API: choose a tool and execute it, returning the action."""

        tool_cls = self._select_tool(stimulus)
        tool_instance: Tool = tool_cls()
        kwargs: Dict[str, Any] = self._build_tool_kwargs(tool_instance, stimulus)
        return tool_instance.execute(**kwargs)

    # ------------------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------------------
    def _select_tool(self, stimulus: InterpretedStimulus) -> Type[Tool]:
        """Return the Tool class to handle the stimulus.

        If self.use_llm is True, we would construct a prompt and query an LLM.
        For now, we employ deterministic heuristics with a fallback random choice.
        """

        if self.use_llm:
            # Placeholder for future LLM selection logic
            tool_name = self._mock_llm_select(stimulus)
            return get_tool(tool_name)

        # Heuristic rules -------------------------------------------------
        if StimulusSchema.THREAT in stimulus.schema:
            return get_tool("FleeTool")

        if stimulus.stimulus_type.name == "DIALOGUE":
            return get_tool("DialogueResponseTool")

        # Default fallback
        return random.choice([
            get_tool("DialogueResponseTool"),
            get_tool("FleeTool"),
        ])

    def _build_tool_kwargs(self, tool: Tool, stimulus: InterpretedStimulus) -> Dict[str, Any]:
        """Map stimulus to tool‐specific kwargs."""

        if tool.name == "dialogue_response":
            return {"prompt": stimulus.raw_content}
        return {}

    # ------------------------------------------------------------------
    # MOCKS / PLACEHOLDERS
    # ------------------------------------------------------------------
    def _mock_llm_select(self, stimulus: InterpretedStimulus) -> str:
        """Pretend we queried an LLM; returns tool name string."""

        # Simple prompt -> choose tool logically
        if StimulusSchema.THREAT in stimulus.schema:
            return "FleeTool"
        return "DialogueResponseTool" 