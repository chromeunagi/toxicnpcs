from cognition.clients.stimulus_client import StimulusClient
from cognition.clients.base_client import BaseClient
from cognition.clients.decision_client import DecisionClient
from cognition.StimulusEngine.types import (
    RawStimulus,
    RawStimulusChannel,
    PersonalityInterpretationModifier,
    MemoryInterpretationModifier,
    AspirationsInterpretationModifier,
    InterpretationModifierKey,
    TraumaTag,
)

if __name__ == "__main__":
    # Now we can use StimulusClient as a context manager
    # BaseClient() is instantiated here and passed to StimulusClient.
    # If BaseClient itself needed to be managed by a 'with' block for its own resources,
    # it would be:
    # with BaseClient() as base_client_instance:
    #     with StimulusClient(base_client=base_client_instance) as stimulus_client_instance:
    #         # ... code ...
    # But since StimulusClient now handles its context, and BaseClient's context methods are simple,
    # this direct approach should work for the user's desired syntax.

    with StimulusClient(
        base_client=BaseClient()
    ) as client:  # Use 'client' as the variable name for StimulusClient instance
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
        # Use the 'client' instance obtained from the 'with' statement
        interpreted_stimulus = client.interpret_stimulus(raw_stimulus, modifiers)

        # Print the results in a more readable format
        print(f"Interpreted stimulus: '{raw_stimulus.content}'")
        print(f"Type: {interpreted_stimulus.stimulus_type.value}")
        print(f"Schema: {[s.value for s in interpreted_stimulus.schema]}")
        print(
            f"Intent: {interpreted_stimulus.intent.value if interpreted_stimulus.intent else 'Unknown'}"
        )

        # Print salience values
        print("Salience:")
        for salience_type, value in interpreted_stimulus.salience.items():
            print(f"  {salience_type.value}: {value:.2f}")

        # Print memory references and trauma triggers
        print(
            f"Memory references: {[m.value for m in interpreted_stimulus.memory_references]}"
        )
        print(
            f"Trauma triggers: {[t.value for t in interpreted_stimulus.trauma_triggers]}"
        )

    with DecisionClient(base_client=BaseClient()) as decision_client:
        decision = decision_client.decide_action(interpreted_stimulus)
        print(f"Decision: {decision}")
