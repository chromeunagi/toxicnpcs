#!/usr/bin/env python
"""Demonstrate the DecisionEngine using all available tools with different personality types."""

import sys
import os
import time
from collections import Counter

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


def generate_diverse_stimuli() -> list[InterpretedStimulus]:
    """Generate a diverse set of stimuli to showcase different tool categories."""
    timestamp = time.time()
    
    return [
        # Dialogue stimuli
        InterpretedStimulus(
            raw_content="You're nothing but a worthless coward.",
            actor="Player",
            stimulus_type=StimulusType.DIALOGUE,
            schema=[StimulusSchema.INSULT, StimulusSchema.DOMINANCE_ASSERTION],
            intent=StimulusIntent.HUMILIATE,
            salience={
                SalienceType.EMOTIONAL: 0.9,
                SalienceType.RELATIONSHIP: 0.7,
            },
            timestamp=timestamp,
        ),
        InterpretedStimulus(
            raw_content="I think you're amazing and brave.",
            actor="Player",
            stimulus_type=StimulusType.DIALOGUE,
            schema=[StimulusSchema.PRAISE],
            intent=StimulusIntent.BUILD_RAPPORT,
            salience={
                SalienceType.EMOTIONAL: 0.8,
                SalienceType.RELATIONSHIP: 0.9,
            },
            timestamp=timestamp + 1,
        ),
        
        # Gesture/Action stimuli
        InterpretedStimulus(
            raw_content="*Player raises weapon threateningly*",
            actor="Player",
            stimulus_type=StimulusType.GESTURE,
            schema=[StimulusSchema.THREAT, StimulusSchema.VIOLENCE],
            intent=StimulusIntent.WARN,
            salience={
                SalienceType.EMOTIONAL: 0.9,
                SalienceType.RELATIONSHIP: 0.5,
            },
            timestamp=timestamp + 2,
        ),
        InterpretedStimulus(
            raw_content="*Player extends hand for a handshake*",
            actor="Player",
            stimulus_type=StimulusType.GESTURE,
            schema=[StimulusSchema.REASSURANCE],
            intent=StimulusIntent.BUILD_RAPPORT,
            salience={
                SalienceType.EMOTIONAL: 0.6,
                SalienceType.RELATIONSHIP: 0.8,
            },
            timestamp=timestamp + 3,
        ),
        
        # Physical contact
        InterpretedStimulus(
            raw_content="*Player shoves you hard*",
            actor="Player",
            stimulus_type=StimulusType.PHYSICAL_CONTACT,
            schema=[StimulusSchema.VIOLENCE, StimulusSchema.DOMINANCE_ASSERTION],
            intent=StimulusIntent.PROVOKE,
            salience={
                SalienceType.EMOTIONAL: 0.9,
                SalienceType.RELATIONSHIP: 0.7,
            },
            timestamp=timestamp + 4,
        ),
        
        # Environmental stimulus
        InterpretedStimulus(
            raw_content="*A loud explosion occurs nearby*",
            actor="Environment",
            stimulus_type=StimulusType.ENVIRONMENT,
            schema=[StimulusSchema.THREAT],
            intent=None,
            salience={
                SalienceType.EMOTIONAL: 0.8,
                SalienceType.NARRATIVE: 0.9,
            },
            timestamp=timestamp + 5,
        ),
        
        # Object interaction
        InterpretedStimulus(
            raw_content="*Player holds out a valuable item*",
            actor="Player",
            stimulus_type=StimulusType.OBJECT_INTERACTION,
            schema=[StimulusSchema.MYSTERY],
            intent=StimulusIntent.TEST_LOYALTY,
            salience={
                SalienceType.EMOTIONAL: 0.5,
                SalienceType.NARRATIVE: 0.7,
            },
            timestamp=timestamp + 6,
        ),
    ]


def demonstrate_personality_variation(personalities, stimuli):
    """Show how different personalities respond to the same stimuli."""
    print("\n==== PERSONALITY VARIATION DEMONSTRATION ====")
    
    for personality_name, personality in personalities.items():
        print(f"\n--- {personality_name} NPC ---")
        print(f"Description: {personality.description}")
        
        # Create decision engine with this personality
        engine = DecisionEngine(personality=personality)
        
        # Track which tools are selected
        tool_choices = []
        
        for stimulus in stimuli:
            print(f"\nStimulus: {stimulus.raw_content}")
            print(f"Type: {stimulus.stimulus_type.name}, Intent: {stimulus.intent.value if stimulus.intent else 'None'}")
            
            # Get decision 5 times to show non-determinism
            responses = []
            for _ in range(5):
                action = engine.decide_and_act(stimulus)
                # Extract just the tool name from the decision history
                tool_name = engine.decision_history[-1][1]
                tool_choices.append(tool_name)
                responses.append((tool_name, action))
            
            # Show unique responses
            for i, (tool_name, response) in enumerate(responses):
                print(f"  Response {i+1} ({tool_name}): {response}")
        
        # Show tool distribution
        tool_counter = Counter(tool_choices)
        print("\nTool usage distribution:")
        for tool, count in tool_counter.most_common():
            print(f"  {tool}: {count} times ({count/len(tool_choices)*100:.1f}%)")
        print("\n" + "-" * 50)


def main():
    """Run the demonstration."""
    # Create personalities 
    personalities = {
        "Aggressive": PersonalityFactory.create_preset_personality("aggressive"),
        "Cautious": PersonalityFactory.create_preset_personality("cautious"),
        "Friendly": PersonalityFactory.create_preset_personality("friendly"),
        "Random": PersonalityFactory.create_random_personality("Random NPC"),
    }
    
    # Generate diverse stimuli
    stimuli = generate_diverse_stimuli()
    
    # Run demonstration
    demonstrate_personality_variation(personalities, stimuli)
    

if __name__ == "__main__":
    main() 