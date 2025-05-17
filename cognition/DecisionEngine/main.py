from __future__ import annotations

import time

from decision_engine import DecisionEngine
from stimulus import (
    InterpretedStimulus,
    StimulusIntent,
    StimulusSchema,
    StimulusType,
    SalienceType,
)


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
    ]


def main() -> None:
    engine = DecisionEngine()
    for stimulus in generate_example_stimuli():
        action = engine.decide_and_act(stimulus)
        print(f"Stimulus: {stimulus.raw_content}\n -> Action: {action}\n")


if __name__ == "__main__":
    main() 