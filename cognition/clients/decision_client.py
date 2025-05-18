import json
from typing import Any, Dict, Optional, Type

from .base_client import BaseClientImpl
from cognition.StimulusEngine.types import InterpretedStimulus

# Potentially import types from DecisionEngine or PersonalityEngine as needed in the future
# from cognition.DecisionEngine.types import Action, Goal
# from cognition.PersonalityEngine.types import PersonalityProfile


class DecisionClient:
    """
    Client for making decisions based on interpreted stimuli and other contextual factors,
    using a BaseClient.
    """

    def __init__(self):
        base_client = BaseClientImpl()
        self.base_client = base_client

    def decide_action(
        self,
        interpreted_stimulus: InterpretedStimulus,
        # personality: PersonalityProfile, # Example: NPC's personality
        # current_goals: List[Goal],       # Example: NPC's current objectives
        # available_actions: List[str],   # Example: Possible actions NPC can take
        context: Optional[Dict[str, Any]] = None,  # Changed to Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:  # Placeholder for an Action object or similar structure
        """
        Decides on an action based on the interpreted stimulus and other factors.

        Args:
            interpreted_stimulus: The interpreted stimulus to react to.
            context: A dictionary for any other relevant context (e.g., personality, goals).
                     This is a placeholder and will need to be defined more concretely.

        Returns:
            A dictionary representing the decided action (placeholder).
        """
        prompt = self._build_decision_prompt(interpreted_stimulus, context)
        # print(f"DecisionClient Prompt: {prompt}") # For debugging

        response_text = self.base_client.generate_content(prompt)

        if response_text:
            action = self._parse_decision_response(response_text)
        else:
            print(
                "Warning: Received no text response from BaseClient for decision making."
            )
            action = {
                "action": "default_fallback_action",
                "error": "No response from LLM",
            }

        return action

    def _build_decision_prompt(
        self,
        interpreted_stimulus: InterpretedStimulus,
        context: Optional[Dict[str, Any]] = None,  # Changed to Optional[Dict[str, Any]]
    ) -> str:
        """Builds the prompt for the LLM to make a decision."""
        prompt_parts = [
            "Based on the following interpreted stimulus and context, decide the next best action.",
            "\n[Interpreted Stimulus]",
            f"  Raw Content: {interpreted_stimulus.raw_content}",
            f"  Actor: {interpreted_stimulus.actor}",
            f"  Stimulus Type: {interpreted_stimulus.stimulus_type.value}",
            f"  Schema: {[s.value for s in interpreted_stimulus.schema]}",
            f"  Intent: {interpreted_stimulus.intent.value if interpreted_stimulus.intent else 'N/A'}",
            f"  Salience: { {s_type.value: val for s_type, val in interpreted_stimulus.salience.items()} }",
            f"  Memory References: {[m.value for m in interpreted_stimulus.memory_references]}",
            f"  Trauma Triggers: {[t.value for t in interpreted_stimulus.trauma_triggers]}",
            f"  Timestamp: {interpreted_stimulus.timestamp}",
            f"  Location: {interpreted_stimulus.location}",
            f"  Confidence: {interpreted_stimulus.confidence}",
        ]

        # Add other contextual information (placeholder)
        if context:  # This check is now correct
            prompt_parts.append("\n[Additional Context]")
            # Example: personality traits, current goals, world state
            # This section needs to be developed based on actual DecisionEngine needs
            if context.get("npc_personality_summary"):
                prompt_parts.append(
                    f"  NPC Personality Summary: {context['npc_personality_summary']}"
                )
            if context.get("npc_current_goals"):
                prompt_parts.append(
                    f"  NPC Current Goals: {context['npc_current_goals']}"
                )
            if context.get("available_actions"):
                prompt_parts.append(
                    f"  Available Actions: {context['available_actions']}"
                )
            # ... add more context as needed ...

        prompt_parts.append("\n[Output Format]")
        prompt_parts.append(
            "Provide your decision as a JSON object with the action and any relevant parameters."
        )
        # The following lines with JSON examples are fine as they are not f-strings.
        prompt_parts.append(
            'Example: {"action": "greet", "target": "Player", "tone": "friendly"}'
        )
        prompt_parts.append(
            'Example: {"action": "attack", "target": "Player", "weapon": "sword"}'
        )
        prompt_parts.append(
            'Example: {"action": "investigate", "object": "strange_noise"}'
        )
        prompt_parts.append("IMPORTANT: Respond ONLY with the JSON object.")

        return "\n".join(prompt_parts)

    def _parse_decision_response(self, response_text: str) -> Dict[str, Any]:
        """Parses the LLM response text into an action structure."""
        data = None  # Initialize data
        try:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                print(
                    f"Warning: No JSON object found in LLM decision response: {response_text}"
                )
                return {
                    "action": "parse_error",
                    "error": "No JSON found",
                    "raw_response": response_text,
                }

            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)  # data is assigned here
            return data
        except json.JSONDecodeError as e:
            print(
                f"Error parsing LLM decision JSON response: {e}. Response text: {response_text}"
            )
            return {
                "action": "parse_error",
                "error": str(e),
                "raw_response": response_text,
            }
        except (
            KeyError
        ) as e:  # Added to handle potential KeyErrors during parsing if structure is assumed
            print(f"KeyError during LLM decision response parsing: {e}. Data: {data}")
            return {
                "action": "parse_error",
                "error": f"KeyError: {str(e)}",
                "raw_response": response_text,
                "parsed_data": data,
            }
        except Exception as e:  # Catch any other unexpected errors
            print(
                f"Unexpected error parsing LLM decision response: {e}. Response text: {response_text}"
            )
            return {
                "action": "parse_error",
                "error": str(e),
                "raw_response": response_text,
            }

    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],  # Using Any for traceback type for simplicity
    ):
        """Exit the runtime context related to this object."""
        pass


# Example placeholder for Action type (would likely be in DecisionEngine.types)
# class Action:
#     def __init__(self, name: str, parameters: Dict[str, Any] = None):
#         self.name = name
#         self.parameters = parameters if parameters else {}
#
#     def __repr__(self):
#         return f"Action(name='{self.name}', parameters={self.parameters})"
