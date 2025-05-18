#!/usr/bin/env python
"""Demonstrate the DecisionEngine using LLM integration for decision making."""

import sys
import os
import time
from typing import Dict, Any

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
from cognition.clients.decision_client import DecisionClient
from cognition.clients.base_client import BaseClient


class MockBaseClient(BaseClient):
    """Mock version of BaseClient for demonstration purposes."""
    
    def __init__(self):
        """Initialize the mock client."""
        pass
        
    def generate_content(self, prompt: str) -> str:
        """Mock implementation that returns predefined decisions based on keywords in the prompt."""
        print("\n=== MOCK LLM PROMPT ===")
        print(prompt)
        print("======================\n")
        
        # Check for specific stimulus keywords and return appropriate mock decisions
        if "worthless coward" in prompt:
            return '{"action": "express_emotion", "emotion": "anger", "intensity": 0.8, "reason": "responding to insult"}'
        
        if "amazing and brave" in prompt:
            return '{"action": "thank", "tone": "appreciative", "follow_up": "offer_help"}'
            
        if "raises weapon" in prompt:
            return '{"action": "defend", "style": "cautious", "prepare_for": "possible attack"}'
            
        if "extends hand" in prompt:
            return '{"action": "greet", "formality": "warm", "include_handshake": true}'
            
        if "shoves you" in prompt:
            return '{"action": "retreat", "speed": "moderate", "express": "confusion"}'
            
        if "explosion" in prompt:
            return '{"action": "take_cover", "urgency": "high", "look_for": "threat source"}'
            
        if "valuable item" in prompt:
            return '{"action": "examine_item", "thoroughness": 0.7, "maintain_suspicion": true}'
            
        # Default response if no specific keywords match
        return '{"action": "dialogue_response", "message": "I need to consider this situation carefully."}'
    
    def close(self) -> None:
        """Close the client."""
        pass


def generate_test_stimuli() -> list[InterpretedStimulus]:
    """Generate a diverse set of stimuli to showcase LLM-based decisions."""
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


def demonstrate_llm_decisions():
    """Show how the DecisionEngine works with LLM integration."""
    print("\n==== LLM-INTEGRATED DECISION ENGINE DEMONSTRATION ====")
    
    # Create a mock client
    base_client = MockBaseClient()
    decision_client = DecisionClient(base_client)
    
    # Create different personalities for testing
    personalities = {
        "Aggressive": PersonalityFactory.create_preset_personality("aggressive"),
        "Cautious": PersonalityFactory.create_preset_personality("cautious"),
    }
    
    stimuli = generate_test_stimuli()
    
    for personality_name, personality in personalities.items():
        print(f"\n--- {personality_name} NPC with LLM Decision Making ---")
        print(f"Description: {personality.description}")
        
        # Create decision engine with this personality and the decision client
        engine = DecisionEngine(
            use_llm=True,
            personality=personality,
            decision_client=decision_client
        )
        
        for stimulus in stimuli:
            print(f"\nStimulus: {stimulus.raw_content}")
            print(f"Type: {stimulus.stimulus_type.name}, Intent: {stimulus.intent.value if stimulus.intent else 'None'}")
            
            # Get LLM-based decision and execute it
            action = engine.decide_and_act(stimulus)
            
            # Extract the tool name from the decision history
            tool_name = engine.decision_history[-1][1]
            print(f"Selected Tool: {tool_name}")
            print(f"Action Result: {action}")
            
        print("\n" + "-" * 50)


def main():
    """Run the LLM-integrated decision engine demonstration."""
    demonstrate_llm_decisions()
    

if __name__ == "__main__":
    main() 