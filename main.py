from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

from cognition.Actor.actor import Actor
from cognition.clients.stimulus_client import StimulusClient
from cognition.clients.base_client import BaseClientImpl
from cognition.clients.decision_client import DecisionClient
from cognition.StimulusEngine.types import (
    RawStimulus,
    RawStimulusChannel,
    PersonalityInterpretationModifier,
    MemoryInterpretationModifier,
    AspirationsInterpretationModifier,
    InterpretationModifierKey,
    TraumaTag,
    InterpretedStimulus,
)

# from cognition.DecisionEngine.main import decision_engine_demo # Unused import

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

    # decision_engine_demo() # Commenting this out to focus on Actor demo, can be re-enabled
    # sys.exit() # Commenting this out

    # Define modifiers (as they were)
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

    # Create an Actor instance
    npc_john = Actor(actor_id="npc_john_01", interpretation_modifiers=modifiers)
    print(f"Created Actor: {npc_john}")

    with StimulusClient(
        base_client=BaseClientImpl()
    ) as client:  # Use 'client' as the variable name for StimulusClient instance
        raw_stimulus_text = "Hello, are you done with the report, you fucking idiot??"
        raw_stimulus = RawStimulus(
            content=raw_stimulus_text,
            channel=RawStimulusChannel.TEXTUAL,
            actors=["Jane"],
            target=["John"],  # Assuming John is the target
        )

        # Actor perceives the raw stimulus
        npc_john.add_raw_stimulus(raw_stimulus)
        print(
            f"NPC John's unprocessed stimuli queue: {npc_john.unprocessed_stimuli_queue}"
        )

        # Actor processes the next stimulus (conceptual step, actual interpretation by client)
        stimulus_to_process = npc_john.get_next_raw_stimulus()

        interpreted_stimulus: Optional[InterpretedStimulus] = (
            None  # Ensure variable is defined
        )
        if stimulus_to_process:
            print(f"NPC John is processing: {stimulus_to_process.content}")
            # Interpret the stimulus and print details
            # Use the 'client' instance obtained from the 'with' statement
            # Pass the actor's modifiers to the interpretation process
            interpreted_stimulus = client.interpret_stimulus(
                stimulus_to_process, npc_john.interpretation_modifiers
            )

            # Actor stores the interpreted stimulus
            npc_john.add_interpreted_stimulus(interpreted_stimulus)

            # Actor memorizes the interpreted stimulus
            npc_john.add_to_memory(interpreted_stimulus)
            print(
                f"NPC John's interpreted stimuli history: {npc_john.interpreted_stimuli_history}"
            )

            # Print the results in a more readable format
            print(f"Interpreted stimulus: '{stimulus_to_process.content}'")
            print(f"  Type: {interpreted_stimulus.stimulus_type.value}")
            print(f"  Schema: {[s.value for s in interpreted_stimulus.schema]}")
            print(
                f"  Intent: {interpreted_stimulus.intent.value if interpreted_stimulus.intent else 'Unknown'}"
            )

            # Print salience values
            print("  Salience:")
            for salience_type, value in interpreted_stimulus.salience.items():
                print(f"    {salience_type.value}: {value:.2f}")

            # Print memory references and trauma triggers
            print(
                f"  Memory references: {[m.value for m in interpreted_stimulus.memory_references]}"
            )
            print(
                f"  Trauma triggers: {[t.value for t in interpreted_stimulus.trauma_triggers]}"
            )
        else:
            print("NPC John has no stimuli to process.")

        # Actor memorizes a simple string
        npc_john.add_to_memory("Remembered that Jane can be quite rude sometimes.")

        print(f"NPC John's current memory: {npc_john.memorized_items}")
        print(f"Updated Actor state: {npc_john}")

    if (
        interpreted_stimulus
    ):  # Check if we have an interpreted stimulus before proceeding
        with DecisionClient() as decision_client:  # Removed base_client argument
            # Provide context for the decision, potentially from the actor
            decision_context = {
                "npc_personality_summary": ", ".join(
                    [type(m).__name__ for m in npc_john.interpretation_modifiers]
                ),
                # Add other relevant context from npc_john if needed
                # "npc_current_goals": [...],
                # "available_actions": [...]
            }
            decision = decision_client.decide_action(
                interpreted_stimulus, context=decision_context
            )
            print(f"Decision for NPC John: {decision}")
    else:
        print("Skipping decision making as there was no interpreted stimulus.")
