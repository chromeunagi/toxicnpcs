from cognition.clients.direct_gemini_interpreter import interpret_stimulus
from cognition.StimulusProcessEngine.types import (
    RawStimulus,
    RawStimulusChannel,
    PersonalityInterpretationModifier,
    MemoryInterpretationModifier,
    AspirationsInterpretationModifier,
    InterpretationModifierKey,
    TraumaTag,
)

if __name__ == "__main__":
    raw_stimulus = RawStimulus(
        content="Hello, are you done with the report, you fucking idiot??",
        channel=RawStimulusChannel.TEXTUAL,
        actors=["Jane"],
        target=["John"],
    )
    modifiers = [
        PersonalityInterpretationModifier(
            description="John is a friendly person",
            profile={
                InterpretationModifierKey.NEUROTICISM: 0.5,
                InterpretationModifierKey.EMPATHY: 0.5,
                InterpretationModifierKey.AGGRESSION: 1.0,
                InterpretationModifierKey.TRUST: 0.5,
                InterpretationModifierKey.SUSPICION: 0.5,
                InterpretationModifierKey.DOMINANCE_DRIVE: 1.0,
                InterpretationModifierKey.ATTACHMENT_STYLE: 0.5,
                InterpretationModifierKey.INSECURITY: 1.0,
            },
        ),
        MemoryInterpretationModifier(
            relevant_memories_summary="John has a memory of Jane being rude after he helped her with a previous report",
            triggered_traumas=[TraumaTag.BETRAYAL],
        ),
        AspirationsInterpretationModifier(
            current_goals_summary="John wants to be an alpha male"
        ),
    ]

    # Interpret the stimulus and print details
    interpreted_stimulus = interpret_stimulus(raw_stimulus, modifiers)
    
    # Print the results in a more readable format
    print(f"Interpreted stimulus: '{raw_stimulus.content}'")
    print(f"Type: {interpreted_stimulus.stimulus_type.value}")
    print(f"Schema: {[s.value for s in interpreted_stimulus.schema]}")
    print(f"Intent: {interpreted_stimulus.intent.value if interpreted_stimulus.intent else 'Unknown'}")
    
    # Print salience values
    print("Salience:")
    for salience_type, value in interpreted_stimulus.salience.items():
        print(f"  {salience_type.value}: {value:.2f}")
    
    # Print memory references and trauma triggers
    print(f"Memory references: {[m.value for m in interpreted_stimulus.memory_references]}")
    print(f"Trauma triggers: {[t.value for t in interpreted_stimulus.trauma_triggers]}")
