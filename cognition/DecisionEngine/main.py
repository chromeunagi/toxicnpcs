from __future__ import annotations

import time
import sys
import os

from cognition.clients.decision_client import DecisionClient

# Add parent directory to path so imports work properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from cognition.DecisionEngine.decision_engine import DecisionEngine
from cognition.DecisionEngine.stimulus import (
    InterpretedStimulus,
    StimulusIntent,
    StimulusSchema,
    StimulusType,
    SalienceType,
)
from cognition.PersonalityEngine.personality import PersonalityFactory


def generate_example_stimuli() -> list[InterpretedStimulus]:
    """Return a handful of hard-coded stimuli for demo purposes."""

    timestamp = time.time()

    return [
        InterpretedStimulus(
            raw_content="You're worthless.",
            actor="Player",
            stimulus_type=StimulusType.DIALOGUE,
            schema=[StimulusSchema.THREAT, StimulusSchema.INSULT],
            intent=StimulusIntent.HUMILIATE,
            salience={
                SalienceType.EMOTIONAL: 0.95,
                SalienceType.RELATIONSHIP: 0.6,
                SalienceType.NARRATIVE: 0.7,
            },
            timestamp=timestamp,
            confidence=0.99,
        ),
        InterpretedStimulus(
            raw_content="*Player raises weapon*",
            actor="Player",
            stimulus_type=StimulusType.GESTURE,
            schema=[StimulusSchema.THREAT, StimulusSchema.VIOLENCE],
            intent=StimulusIntent.WARN,
            salience={
                SalienceType.EMOTIONAL: 0.85,
                SalienceType.NARRATIVE: 0.5,
            },
            timestamp=timestamp + 1,
        ),
        InterpretedStimulus(
            raw_content="Hey, I need your help with something.",
            actor="Player",
            stimulus_type=StimulusType.DIALOGUE,
            schema=[StimulusSchema.REQUEST],
            intent=StimulusIntent.SEEK_HELP,
            salience={
                SalienceType.RELATIONSHIP: 0.7,
                SalienceType.NARRATIVE: 0.4,
            },
            timestamp=timestamp + 2,
        ),
        InterpretedStimulus(
            raw_content="I know we've had our differences, but I'm trying to make amends.",
            actor="Player",
            stimulus_type=StimulusType.DIALOGUE,
            schema=[StimulusSchema.REASSURANCE],
            intent=StimulusIntent.BUILD_RAPPORT,
            salience={
                SalienceType.EMOTIONAL: 0.6,
                SalienceType.RELATIONSHIP: 0.8,
            },
            timestamp=timestamp + 3,
        ),
    ]


def decision_engine_demo() -> None:
    print("\n=== PERSONALITY-DRIVEN DECISION ENGINE DEMO ===\n")
    
    # Create different personality types
    aggressive_personality = PersonalityFactory.create_preset_personality("aggressive")
    cautious_personality = PersonalityFactory.create_preset_personality("cautious")
    friendly_personality = PersonalityFactory.create_preset_personality("friendly")
    random_personality = PersonalityFactory.create_random_personality("Random NPC")
    
    # Create engines with different personalities
    engines = {
        "Aggressive NPC": DecisionEngine(personality=aggressive_personality, use_llm=True, decision_client=DecisionClient()),
        "Cautious NPC": DecisionEngine(personality=cautious_personality, use_llm=True, decision_client=DecisionClient()),
        "Friendly NPC": DecisionEngine(personality=friendly_personality, use_llm=True, decision_client=DecisionClient()),
        "Random NPC": DecisionEngine(personality=random_personality, use_llm=True, decision_client=DecisionClient()),
    }
    
    # Run each stimulus through each personality type
    stimuli = generate_example_stimuli()
    
    for npc_name, engine in engines.items():
        print(f"\n--- {npc_name} Responses ---")
        print(f"Personality: {engine.personality.description}")
        print("Key traits:")
        for trait, value in sorted(engine.personality.traits.items(), 
                                  key=lambda x: x[1], reverse=True)[:3]:
            print(f"  - {trait.name}: {value:.2f}")
        print(f"Quirks: {', '.join(engine.personality.quirks)}")
        print("\nStimulus Responses:")
        
        for stimulus in stimuli:
            # Run the same stimulus through each personality type
            action = engine.decide_and_act(stimulus)
            print(f"\nStimulus: {stimulus.raw_content}")
            print(f"Intent: {stimulus.intent.value if stimulus.intent else 'Unknown'}")
            print(f" -> Action: {action}")
        
        print("\n" + "-" * 50)
    
    # Show how adding randomness creates non-deterministic behavior
    print("\n=== NON-DETERMINISM DEMONSTRATION ===")
    print("Running the same stimulus through the same personality multiple times:")
    
    demo_engine = DecisionEngine(personality=random_personality)
    demo_stimulus = stimuli[0]  # "You're worthless"
    
    print(f"\nPersonality: {demo_engine.personality.description}")
    print(f"Stimulus: {demo_stimulus.raw_content}")
    print("Results from 5 repeated trials:")
    
    for i in range(5):
        action = demo_engine.decide_and_act(demo_stimulus)
        print(f"  Trial {i+1}: {action}")


if __name__ == "__main__":
    decision_engine_demo()  