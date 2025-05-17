from __future__ import annotations

import random
from typing import Any, Dict, Type, Optional, List, Tuple

from cognition.DecisionEngine.stimulus import (
    InterpretedStimulus,
    StimulusIntent,
    StimulusSchema,
    StimulusType,
)
from cognition.DecisionEngine.toolbox import get_tool, Tool

from cognition.PersonalityEngine.personality import (
    Personality,
    PersonalityDimension,
    PersonalityFactory,
)


class DecisionEngine:
    """Selects and executes the best tool for a given interpreted stimulus."""

    def __init__(self, 
                use_llm: bool = False, 
                personality: Optional[Personality] = None) -> None:
        """
        Initialize the decision engine with optional personality.
        
        Args:
            use_llm: Whether to use LLM for decision making
            personality: Optional personality to influence decisions. If None, 
                         a random personality will be created.
        """
        self.use_llm = use_llm
        self.personality = personality or PersonalityFactory.create_random_personality("Default NPC")
        
        # Track decision history for potential pattern analysis
        self.decision_history: List[Tuple[InterpretedStimulus, str]] = []

    # ------------------------------------------------------------------
    # PUBLIC INTERFACE
    # ------------------------------------------------------------------
    def decide_and_act(self, stimulus: InterpretedStimulus) -> str:
        """High-level API: choose a tool and execute it, returning the action."""

        tool_cls = self._select_tool(stimulus)
        tool_instance: Tool = tool_cls()
        kwargs: Dict[str, Any] = self._build_tool_kwargs(tool_instance, stimulus)
        action_result = tool_instance.execute(**kwargs)
        
        # Record this decision for history/patterns
        self.decision_history.append((stimulus, tool_instance.name))
        
        return action_result

    # ------------------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------------------
    def _select_tool(self, stimulus: InterpretedStimulus) -> Type[Tool]:
        """Return the Tool class to handle the stimulus.

        If self.use_llm is True, we would construct a prompt and query an LLM.
        For now, we employ personality-influenced heuristics with weighted random choices.
        """

        if self.use_llm:
            # Placeholder for future LLM selection logic
            tool_name = self._mock_llm_select(stimulus)
            return get_tool(tool_name)

        # Discover available tools
        available_tools: Dict[str, Type[Tool]] = {}
        try:
            available_tools["FleeTool"] = get_tool("FleeTool")
        except KeyError:
            pass  # Tool not available
        try:
            available_tools["DialogueResponseTool"] = get_tool("DialogueResponseTool")
        except KeyError:
            pass  # Tool not available
            
        # Get personality-influenced probabilities for each tool
        tool_probabilities = self._calculate_tool_probabilities(stimulus, available_tools)
        
        # If no tools match or are available, raise an error
        if not tool_probabilities:
            raise ValueError("No suitable tools available for decision.")
            
        # Weighted random selection based on probabilities
        tools, weights = zip(*tool_probabilities.items())
        selected_tool = random.choices(tools, weights=weights, k=1)[0]
        
        return get_tool(selected_tool)

    def _calculate_tool_probabilities(self, 
                                     stimulus: InterpretedStimulus, 
                                     available_tools: Dict[str, Type[Tool]]) -> Dict[str, float]:
        """
        Calculate probability weights for each available tool based on:
        1. The stimulus properties
        2. Personality traits
        3. Base heuristic rules
        4. A touch of randomness for non-determinism
        
        Returns a dict mapping tool names to their probability weights.
        """
        probabilities: Dict[str, float] = {}
        
        # Initialize with base probabilities
        if "DialogueResponseTool" in available_tools:
            probabilities["DialogueResponseTool"] = 0.5
        if "FleeTool" in available_tools:
            probabilities["FleeTool"] = 0.5
        
        # Apply basic heuristic adjustments
        if StimulusSchema.THREAT in stimulus.schema:
            # Threats tend to increase flee probability
            if "FleeTool" in probabilities:
                probabilities["FleeTool"] = 0.7
            if "DialogueResponseTool" in probabilities:
                probabilities["DialogueResponseTool"] = 0.3
                
        if stimulus.stimulus_type == StimulusType.DIALOGUE:
            # Dialogue tends to increase dialogue response probability
            if "DialogueResponseTool" in probabilities:
                probabilities["DialogueResponseTool"] = 0.7
            if "FleeTool" in probabilities:
                probabilities["FleeTool"] = 0.3
        
        # Apply personality trait influences
        if "FleeTool" in probabilities:
            # Higher aggressiveness means less likely to flee
            flee_prob = probabilities["FleeTool"]
            flee_prob = self.personality.influence_value(
                flee_prob,
                PersonalityDimension.AGGRESSIVENESS,
                influence_strength=-0.4  # Negative because aggressiveness reduces flee tendency
            )
            # Risk tolerance also affects flee probability (higher risk tolerance = lower flee)
            flee_prob = self.personality.influence_value(
                flee_prob,
                PersonalityDimension.RISK_TOLERANCE,
                influence_strength=-0.3
            )
            # Apply the adjustment
            probabilities["FleeTool"] = flee_prob
        
        if "DialogueResponseTool" in probabilities:
            # Higher extraversion means more likely to engage in dialogue
            dialogue_prob = probabilities["DialogueResponseTool"]
            dialogue_prob = self.personality.influence_value(
                dialogue_prob,
                PersonalityDimension.EXTRAVERSION,
                influence_strength=0.3
            )
            # Higher agreeableness can increase dialogue probability for certain stimuli
            if stimulus.intent in [StimulusIntent.BUILD_RAPPORT, StimulusIntent.SEEK_HELP]:
                dialogue_prob = self.personality.influence_value(
                    dialogue_prob,
                    PersonalityDimension.AGREEABLENESS,
                    influence_strength=0.3
                )
            # Apply the adjustment
            probabilities["DialogueResponseTool"] = dialogue_prob
        
        # Apply situational adjustments for specific stimulus types
        if stimulus.intent == StimulusIntent.HUMILIATE:
            # Being humiliated can provoke different responses based on neuroticism
            if "DialogueResponseTool" in probabilities and "FleeTool" in probabilities:
                neuroticism = self.personality.get_trait(PersonalityDimension.NEUROTICISM)
                # Higher neuroticism may lead to fleeing when humiliated
                if neuroticism > 0.7:
                    probabilities["FleeTool"] += 0.2
                    probabilities["DialogueResponseTool"] -= 0.2
                # Lower neuroticism might lead to standing ground
                elif neuroticism < 0.3:
                    probabilities["FleeTool"] -= 0.1
                    probabilities["DialogueResponseTool"] += 0.1
        
        # Add randomness for non-deterministic behavior
        for tool in probabilities:
            probabilities[tool] = self.personality.add_randomness(
                probabilities[tool], 
                randomness=0.15
            )
        
        # Normalize probabilities to ensure they sum to 1.0
        total = sum(probabilities.values())
        if total > 0:
            for tool in probabilities:
                probabilities[tool] /= total
                
        return probabilities

    def _build_tool_kwargs(self, tool: Tool, stimulus: InterpretedStimulus) -> Dict[str, Any]:
        """Map stimulus to tool‐specific kwargs."""
        kwargs: Dict[str, Any] = {}

        if tool.name == "dialogue_response":
            # Pass the raw content for response, but modify based on personality
            prompt = stimulus.raw_content
            
            # Add personality-driven context for more nuanced responses
            aggressiveness = self.personality.get_trait(PersonalityDimension.AGGRESSIVENESS)
            extraversion = self.personality.get_trait(PersonalityDimension.EXTRAVERSION)
            
            # In a real implementation, these could be used to frame the prompt for an LLM
            # that would generate the response with the right tone and content
            kwargs["prompt"] = prompt
            kwargs["personality_context"] = {
                "aggressiveness": aggressiveness,
                "extraversion": extraversion,
                "quirks": self.personality.quirks,
            }
            
        elif tool.name == "flee":
            # FleeTool might take parameters like escape route preference
            risk_tolerance = self.personality.get_trait(PersonalityDimension.RISK_TOLERANCE)
            kwargs["caution_level"] = 1.0 - risk_tolerance  # Higher risk tolerance = lower caution
            
        return kwargs

    # ------------------------------------------------------------------
    # MOCKS / PLACEHOLDERS
    # ------------------------------------------------------------------
    def _mock_llm_select(self, stimulus: InterpretedStimulus) -> str:
        """Pretend we queried an LLM; returns tool name string."""
        # Create "mock" tool probabilities
        available_tools = ["DialogueResponseTool", "FleeTool"]
        tool_probs = self._calculate_tool_probabilities(
            stimulus, 
            {tool: None for tool in available_tools}  # Type doesn't matter for mock
        )
        
        # Get the most likely tool
        highest_prob_tool = max(tool_probs.items(), key=lambda x: x[1])[0]
        return highest_prob_tool 