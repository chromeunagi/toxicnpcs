import json
from typing import Sequence, Optional, Type, Any

from cognition.StimulusEngine.types import (
    RawStimulus,
    InterpretedStimulus,
    InterpretationModifier,
    StimulusType,
    StimulusSchema,
    StimulusIntent,
    SalienceType,
    MemoryTag,
    TraumaTag,
)
from .base_client import BaseClient  # Assuming base_client.py is in the same directory


class StimulusClient:
    """
    Client for interpreting raw stimuli into InterpretedStimulus objects using a BaseClient.
    """

    def __init__(self, base_client: BaseClient):
        self.base_client = base_client

    def interpret_stimulus(
        self, raw_stimulus: RawStimulus, modifiers: Sequence[InterpretationModifier]
    ) -> InterpretedStimulus:
        """
        Interprets a raw stimulus using the configured Gemini model,
        applying the provided interpretation modifiers.

        Args:
            raw_stimulus: The raw stimulus to interpret.
            modifiers: List of interpretation modifiers to apply.

        Returns:
            An interpreted stimulus object.
        """
        stimulus_in_progress = InterpretedStimulus(
            raw_content=raw_stimulus.content,
            actor=raw_stimulus.actors[0] if raw_stimulus.actors else "unknown",
            stimulus_type=StimulusType.DIALOGUE,  # Default, will be updated by LLM
            schema=[],
            intent=None,
            salience={},
            timestamp=raw_stimulus.timestamp,
            location=raw_stimulus.location,
            confidence=raw_stimulus.confidence,
            # memory_references and trauma_triggers will be populated by _parse_llm_response
        )

        prompt = self._build_interpretation_prompt(raw_stimulus, modifiers)
        # print(f"StimulusClient Prompt: {prompt}") # For debugging

        response_text = self.base_client.generate_content(prompt)

        if response_text:
            updated_stimulus = self._parse_llm_response(
                response_text, stimulus_in_progress
            )
        else:
            updated_stimulus = stimulus_in_progress
            print(
                "Warning: Received no text response from BaseClient for stimulus interpretation."
            )

        # Apply each modifier to the stimulus AFTER LLM interpretation
        for modifier in modifiers:
            updated_stimulus = modifier.modify(updated_stimulus, raw_stimulus)

        return updated_stimulus

    def _build_interpretation_prompt(
        self, raw_stimulus: RawStimulus, modifiers: Sequence[InterpretationModifier]
    ) -> str:
        """Builds the prompt for the LLM to interpret the stimulus."""
        prompt_parts = [
            "Interpret the following stimulus and provide a detailed analysis based on the given context.",
            f"Stimulus Content: {raw_stimulus.content}",
            f"Channel: {raw_stimulus.channel.value}",
            f"Actors: {', '.join(raw_stimulus.actors) if raw_stimulus.actors else 'unknown'}",
        ]

        if raw_stimulus.target:
            prompt_parts.append(f"Target: {', '.join(raw_stimulus.target)}")

        if raw_stimulus.location:
            prompt_parts.append(f"Location: {raw_stimulus.location}")

        if modifiers:
            prompt_parts.append("\nInterpretation Context (from modifiers):")
            for modifier in modifiers:
                contribution = modifier.get_prompt_contribution()
                if contribution:  # Ensure contribution is not empty
                    prompt_parts.append("- " + contribution)

        prompt_parts.append(
            "\nProvide your interpretation in the following JSON format:"
        )
        prompt_parts.append(
            """
        {
            "stimulus_type": "One of: dialogue, gesture, environment, action, object_interaction, physical_contact, internal_reflection",
            "schema": ["One or more of: threat, praise, insult, deception, flirtation, dominance_assertion, submission, betrayal, reassurance, request, violence, compassion, disgust, mystery, abandonment, sacrifice, insecurity"],
            "intent": "One of: provoke, humiliate, test_loyalty, build_rapport, warn, assert_control, escape_blame, seek_help, express_love, ask_for_forgiveness, manipulate",
            "salience": {
                "emotional": 0.0 to 1.0,      // General emotional impact
                "relationship": 0.0 to 1.0,  // Impact on relationships with involved actors
                "narrative": 0.0 to 1.0,     // Importance to the ongoing story or plot
                "existential": 0.0 to 1.0,   // Impact on fundamental beliefs or worldview
                "moral": 0.0 to 1.0          // Relevance to moral or ethical considerations
            },
            "memory_references": ["One or more of: childhood, friendship, betrayal, intimacy, conflict, loss, victory, failure, love, trauma"],
            "trauma_triggers": ["One or more of: abandonment, shame, betrayal, violence, powerlessness, parental_abuse, failure, neglect, rejection, death_of_loved_one"]
        }

        IMPORTANT: Use ONLY the exact values specified above for each field. Do not invent new values or use different casing.
        If a field is not applicable or cannot be determined, omit it from the JSON or set its value to null where appropriate (e.g. for 'intent').
        For 'schema', 'memory_references', and 'trauma_triggers', if none apply, provide an empty list [].
        For 'salience', if a specific salience type is not applicable, omit it or set its value to 0.0.
        """
        )
        return "\n".join(prompt_parts)

    def _parse_llm_response(
        self, response_text: str, stimulus_in_progress: InterpretedStimulus
    ) -> InterpretedStimulus:
        """Parses the LLM response text and updates the stimulus_in_progress."""
        data = None  # Initialize data to ensure it's defined in except blocks
        try:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                print(f"Warning: No JSON object found in LLM response: {response_text}")
                return stimulus_in_progress

            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)

            # Update stimulus with parsed data, handling potential errors for each field
            if "stimulus_type" in data and data["stimulus_type"]:
                try:
                    stimulus_in_progress.stimulus_type = StimulusType(
                        data["stimulus_type"].lower()
                    )
                except ValueError as e:
                    print(
                        f"Warning: Invalid stimulus_type '{data.get('stimulus_type')}': {e}"
                    )

            if "schema" in data and isinstance(data["schema"], list):
                valid_schemas = []
                for s_item in data["schema"]:
                    try:
                        valid_schemas.append(StimulusSchema(s_item.lower()))
                    except ValueError:
                        print(f"Warning: Skipping invalid schema value '{s_item}'")
                stimulus_in_progress.schema = valid_schemas

            if "intent" in data and data["intent"]:
                try:
                    stimulus_in_progress.intent = StimulusIntent(data["intent"].lower())
                except ValueError as e:
                    print(f"Warning: Invalid intent '{data.get('intent')}': {e}")
            elif (
                "intent" in data and data["intent"] is None
            ):  # Explicitly handle null intent
                stimulus_in_progress.intent = None

            if "salience" in data and isinstance(data["salience"], dict):
                valid_salience = {}
                for k, v_val in data["salience"].items():
                    try:
                        valid_salience[SalienceType(k.lower())] = float(v_val)
                    except (ValueError, TypeError):
                        print(
                            f"Warning: Skipping invalid salience entry '{k}: {v_val}'"
                        )
                stimulus_in_progress.salience = valid_salience

            if "memory_references" in data and isinstance(
                data["memory_references"], list
            ):
                valid_memories = []
                for m_item in data["memory_references"]:
                    try:
                        valid_memories.append(MemoryTag(m_item.lower()))
                    except ValueError:
                        print(f"Warning: Skipping invalid memory_reference '{m_item}'")
                stimulus_in_progress.memory_references = valid_memories

            if "trauma_triggers" in data and isinstance(data["trauma_triggers"], list):
                valid_traumas = []
                for t_item in data["trauma_triggers"]:
                    try:
                        valid_traumas.append(TraumaTag(t_item.lower()))
                    except ValueError:
                        print(f"Warning: Skipping invalid trauma_trigger '{t_item}'")
                stimulus_in_progress.trauma_triggers = valid_traumas

        except json.JSONDecodeError as e:
            print(
                f"Error parsing LLM JSON response: {e}. Response text: {response_text}"
            )
        except KeyError as e:
            print(
                f"KeyError during LLM response parsing: {e}. Data: {data if 'data' in locals() else 'N/A'}"
            )
        except Exception as e:  # Catch any other unexpected errors
            print(
                f"Unexpected error parsing LLM response: {e}. Response text: {response_text}"
            )

        return stimulus_in_progress

    def __enter__(self):
        """Enter the runtime context related to this object."""
        # If BaseClient had significant __enter__ logic, we might call it here:
        # if hasattr(self.base_client, '__enter__'):
        #     self.base_client.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[
            Any
        ],  # TracebackType is more specific, but Any is simpler here
    ):
        """Exit the runtime context related to this object."""
        # If BaseClient had significant __exit__ logic, we might call it here:
        # if hasattr(self.base_client, '__exit__'):
        #     self.base_client.__exit__(exc_type, exc_val, exc_tb)
        pass
