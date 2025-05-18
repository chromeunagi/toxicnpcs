from google import genai
from typing import Sequence
import json

from cognition.StimulusProcessEngine.types import (
    RawStimulus, 
    InterpretedStimulus, 
    InterpretationModifier,
    StimulusType,
    StimulusSchema,
    StimulusIntent,
    SalienceType,
    MemoryTag,
    TraumaTag,
    InterpretationModifierKey
)

API_KEY = "AIzaSyCVInLlj_-yiQRPdfhJuJyD1JDhqqmKqCo"
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"

client = genai.Client(api_key=API_KEY)

def interpret_stimulus(raw_stimulus: RawStimulus, modifiers: Sequence[InterpretationModifier]) -> InterpretedStimulus:
    """
    Interprets a raw stimulus using Gemini, applying the provided interpretation modifiers.
    
    Args:
        raw_stimulus: The raw stimulus to interpret
        modifiers: List of interpretation modifiers to apply
    
    Returns:
        An interpreted stimulus object
    """
    # Initialize a basic interpreted stimulus with required fields from raw stimulus
    stimulus_in_progress = InterpretedStimulus(
        raw_content=raw_stimulus.content,
        actor=raw_stimulus.actors[0] if raw_stimulus.actors else "unknown",
        stimulus_type=StimulusType.DIALOGUE,  # Default, will be updated by Gemini
        schema=[],
        intent=None,
        salience={},
        timestamp=raw_stimulus.timestamp,
        location=raw_stimulus.location,
        confidence=raw_stimulus.confidence
    )
    
    # Build the prompt for Gemini
    prompt = _build_interpretation_prompt(raw_stimulus, modifiers)

    print(f'Prompt: {prompt}')
    
    # Get interpretation from Gemini
    response = client.models.generate_content(
        model=DEFAULT_GEMINI_MODEL,
        contents=prompt
    )
    
    # Parse the response and update the interpreted stimulus
    response_text = response.text
    if response_text is not None:
        updated_stimulus = _parse_gemini_response(response_text, stimulus_in_progress, raw_stimulus)
    else:
        updated_stimulus = stimulus_in_progress
        print("Warning: Received empty response from Gemini")
    
    # Apply each modifier to the stimulus
    for modifier in modifiers:
        updated_stimulus = modifier.modify(updated_stimulus, raw_stimulus)
    
    return updated_stimulus

def _build_interpretation_prompt(raw_stimulus: RawStimulus, modifiers: Sequence[InterpretationModifier]) -> str:
    """Builds the prompt for Gemini to interpret the stimulus."""
    prompt_parts = [
        "Interpret the following stimulus and provide a detailed analysis based on the given context.",
        f"Stimulus: {raw_stimulus.content}",
        f"Channel: {raw_stimulus.channel.value}",
        f"Actors: {', '.join(raw_stimulus.actors) if raw_stimulus.actors else 'unknown'}"
    ]
    
    if raw_stimulus.target:
        prompt_parts.append(f"Target: {', '.join(raw_stimulus.target)}")
    
    if raw_stimulus.location:
        prompt_parts.append(f"Location: {raw_stimulus.location}")
    
    # Add context from modifiers
    if modifiers:
        prompt_parts.append("\nInterpretation Context:")
        for modifier in modifiers:
            prompt_parts.append("- " + modifier.get_prompt_contribution())
    
    # Add specific instructions for the output format with valid values
    prompt_parts.append("\nProvide your interpretation in the following JSON format:")
    prompt_parts.append("""
    {
        "stimulus_type": "One of: dialogue, gesture, environment, action, object_interaction, physical_contact, internal_reflection",
        "schema": ["One or more of: threat, praise, insult, deception, flirtation, dominance_assertion, submission, betrayal, reassurance, request, violence, compassion, disgust, mystery, abandonment, sacrifice, insecurity"],
        "intent": "One of: provoke, humiliate, test_loyalty, build_rapport, warn, assert_control, escape_blame, seek_help, express_love, ask_for_forgiveness, manipulate",
        "salience": {
            "emotional": 0.0 to 1.0,
            "relationship": 0.0 to 1.0,
            "narrative": 0.0 to 1.0,
            "existential": 0.0 to 1.0,
            "moral": 0.0 to 1.0
        },
        "memory_references": ["One or more of: childhood, friendship, betrayal, intimacy, conflict, loss, victory, failure, love, trauma"],
        "trauma_triggers": ["One or more of: abandonment, shame, betrayal, violence, powerlessness, parental_abuse, failure, neglect, rejection, death_of_loved_one"]
    }

    IMPORTANT: Use ONLY the exact values specified above for each field. Do not invent new values.
    """)
    
    return "\n".join(prompt_parts)

def _parse_gemini_response(response_text: str, stimulus_in_progress: InterpretedStimulus, raw_stimulus: RawStimulus) -> InterpretedStimulus:
    """Parses the Gemini response text and updates the stimulus_in_progress."""
    try:
        # Try to extract JSON from the response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
            
            # Update stimulus with parsed data
            if "stimulus_type" in data:
                try:
                    stimulus_in_progress.stimulus_type = StimulusType(data["stimulus_type"].lower())
                except ValueError as e:
                    print(f"Warning: Invalid stimulus_type '{data['stimulus_type']}': {e}")
            
            if "schema" in data and isinstance(data["schema"], list):
                valid_schemas = []
                for s in data["schema"]:
                    try:
                        valid_schemas.append(StimulusSchema(s.lower()))
                    except ValueError:
                        print(f"Warning: Skipping invalid schema value '{s}'")
                stimulus_in_progress.schema = valid_schemas
            
            if "intent" in data and data["intent"]:
                try:
                    stimulus_in_progress.intent = StimulusIntent(data["intent"].lower())
                except ValueError as e:
                    print(f"Warning: Invalid intent '{data['intent']}': {e}")
            
            if "salience" in data and isinstance(data["salience"], dict):
                valid_salience = {}
                for k, v in data["salience"].items():
                    try:
                        valid_salience[SalienceType(k.lower())] = float(v)
                    except ValueError:
                        print(f"Warning: Skipping invalid salience type '{k}'")
                stimulus_in_progress.salience = valid_salience
            
            if "memory_references" in data and isinstance(data["memory_references"], list):
                valid_memories = []
                for m in data["memory_references"]:
                    try:
                        valid_memories.append(MemoryTag(m.lower()))
                    except ValueError:
                        print(f"Warning: Skipping invalid memory_reference '{m}'")
                stimulus_in_progress.memory_references = valid_memories
            
            if "trauma_triggers" in data and isinstance(data["trauma_triggers"], list):
                valid_traumas = []
                for t in data["trauma_triggers"]:
                    try:
                        valid_traumas.append(TraumaTag(t.lower()))
                    except ValueError:
                        print(f"Warning: Skipping invalid trauma_trigger '{t}'")
                stimulus_in_progress.trauma_triggers = valid_traumas
    
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing Gemini response: {e}")
        # If parsing fails, we'll return the stimulus_in_progress with minimal changes
    
    return stimulus_in_progress

# Example usage
if __name__ == "__main__":
    from ..StimulusProcessEngine.types import (
        RawStimulusChannel,
        PersonalityInterpretationModifier,
        MemoryInterpretationModifier
    )
    
    # Create a sample raw stimulus
    raw_stimulus = RawStimulus(
        channel=RawStimulusChannel.TEXTUAL,
        content="Why are you always getting in my way? Move aside!",
        actors=["Angry NPC"],
        target=["Player"]
    )
    
    # Create some modifiers
    modifiers = [
        PersonalityInterpretationModifier(
            description="Tends to see confrontation as threatening due to past experiences",
            profile={
                InterpretationModifierKey.NEUROTICISM: 0.8,
                InterpretationModifierKey.SUSPICION: 0.7
            }
        ),
        MemoryInterpretationModifier(
            relevant_memories_summary="Has been bullied in the past by similar aggressive characters",
            triggered_traumas=[TraumaTag.POWERLESSNESS]
        )
    ]
    
    # Interpret the stimulus
    interpreted = interpret_stimulus(raw_stimulus, modifiers)
    
    # Print the result
    print(f"Interpreted {raw_stimulus.content} as:")
    print(f"Type: {interpreted.stimulus_type.value}")
    print(f"Schema: {[s.value for s in interpreted.schema]}")
    print(f"Intent: {interpreted.intent.value if interpreted.intent else 'Unknown'}")
    print(f"Emotional Salience: {interpreted.salience.get(SalienceType.EMOTIONAL, 0.0)}")
    print(f"Trauma Triggers: {[t.value for t in interpreted.trauma_triggers]}")
