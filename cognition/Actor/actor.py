from collections import deque
from typing import List, Deque, Optional

from cognition.StimulusEngine.types import (
    RawStimulus,
    InterpretedStimulus,
    InterpretationModifier,
)
from cognition.MemoryEngine.types import MemoryItem


class Actor:
    """
    Represents an agent in the simulation, capable of perceiving, processing,
    and reacting to stimuli.
    """

    def __init__(
        self,
        actor_id: str,
        interpretation_modifiers: List[InterpretationModifier],
    ):
        """
        Initializes an Actor instance.

        Args:
            actor_id: A unique identifier for the actor.
            interpretation_modifiers: A list of InterpretationModifier objects
                                      that define how the actor processes stimuli.
        """
        self.actor_id: str = actor_id
        self.interpretation_modifiers: List[InterpretationModifier] = (
            interpretation_modifiers
        )

        # Queue for raw stimuli that have been perceived but not yet processed
        # by the StimulusEngine into InterpretedStimulus.
        self.unprocessed_stimuli_queue: Deque[RawStimulus] = deque()

        # List of stimuli that have been interpreted by the StimulusEngine.
        # This could serve as a short-term sensory memory.
        self.interpreted_stimuli_history: List[InterpretedStimulus] = []

        # List of MemoryItem objects that have been committed to long-term memory.
        self.memorized_items: List[MemoryItem] = []

    def add_raw_stimulus(self, stimulus: RawStimulus):
        """Adds a raw stimulus to the unprocessed queue."""
        self.unprocessed_stimuli_queue.append(stimulus)

    def get_next_raw_stimulus(self) -> Optional[RawStimulus]:
        """Retrieves and removes the next raw stimulus from the queue."""
        if self.unprocessed_stimuli_queue:
            return self.unprocessed_stimuli_queue.popleft()
        return None

    def add_interpreted_stimulus(self, stimulus: InterpretedStimulus):
        """Adds an interpreted stimulus to the history."""
        self.interpreted_stimuli_history.append(stimulus)

    def add_to_memory(self, item: InterpretedStimulus | str):
        """
        Creates a MemoryItem from an InterpretedStimulus or string and adds it to
        the list of memorized items.
        """
        memory_item = MemoryItem(content=item)
        self.memorized_items.append(memory_item)

    def __repr__(self) -> str:
        modifier_types = [type(m).__name__ for m in self.interpretation_modifiers]
        return (
            f"Actor(id='{self.actor_id}', interpretation_modifiers={modifier_types}, "
            f"unprocessed_stimuli={len(self.unprocessed_stimuli_queue)}, "
            f"interpreted_history_count={len(self.interpreted_stimuli_history)}, "
            f"memorized_count={len(self.memorized_items)})"
        )
