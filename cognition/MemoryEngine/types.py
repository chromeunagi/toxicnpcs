from dataclasses import dataclass, field
import uuid
import time
from typing import Union

from cognition.StimulusEngine.types import InterpretedStimulus


@dataclass
class MemoryItem:
    """
    Represents a single item stored in an actor's long-term memory.
    It can encapsulate an interpreted stimulus or a raw string.
    """

    content: Union[InterpretedStimulus, str]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_memorized: float = field(default_factory=time.time)

    def __repr__(self) -> str:
        if isinstance(self.content, InterpretedStimulus):
            content_type = self.content.stimulus_type.value
            content_actor = self.content.actor
            content_preview = self.content.raw_content[:50]
        else:  # Assumed to be str if not InterpretedStimulus, per type hint
            content_type = "text_memory"
            content_actor = "self"
            content_preview = self.content[:50]  # self.content is str here

        return (
            f"MemoryItem(id={self.id}, memorized_at={round(self.timestamp_memorized, 2)}, "
            f"type='{content_type}', actor='{content_actor}', preview='{content_preview}...')"
        )
