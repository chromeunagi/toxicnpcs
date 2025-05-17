from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import uuid
import time

class RawStimulusChannel(Enum):
    TEXTUAL = "textual"
    AUDITORY = "auditory"
    VISUAL = "visual"
    TACTILE = "tactile"
    ENVIRONMENTAL_EVENT = "environmental_event"
    GAME_EVENT = "game_event"

class StimulusType(Enum):
    DIALOGUE = "dialogue"
    GESTURE = "gesture"
    ENVIRONMENT = "environment"
    ACTION = "action"
    OBJECT_INTERACTION = "object_interaction"
    PHYSICAL_CONTACT = "physical_contact"
    INTERNAL_REFLECTION = "internal_reflection"

class StimulusSchema(Enum):
    THREAT = "threat"
    PRAISE = "praise"
    INSULT = "insult"
    DECEPTION = "deception"
    FLIRTATION = "flirtation"
    DOMINANCE_ASSERTION = "dominance_assertion"
    SUBMISSION = "submission"
    BETRAYAL = "betrayal"
    REASSURANCE = "reassurance"
    REQUEST = "request"
    VIOLENCE = "violence"
    COMPASSION = "compassion"
    DISGUST = "disgust"
    MYSTERY = "mystery"
    ABANDONMENT = "abandonment"
    SACRIFICE = "sacrifice"
    INSECURITY = "insecurity"

class StimulusIntent(Enum):
    PROVOKE = "provoke"
    HUMILIATE = "humiliate"
    TEST_LOYALTY = "test_loyalty"
    BUILD_RAPPORT = "build_rapport"
    WARN = "warn"
    ASSERT_CONTROL = "assert_control"
    ESCAPE_BLAME = "escape_blame"
    SEEK_HELP = "seek_help"
    EXPRESS_LOVE = "express_love"
    ASK_FOR_FORGIVENESS = "ask_for_forgiveness"
    MANIPULATE = "manipulate"

class SalienceType(Enum):
    EMOTIONAL = "emotional"
    RELATIONSHIP = "relationship"
    NARRATIVE = "narrative"
    EXISTENTIAL = "existential"
    MORAL = "moral"

class TraumaTag(Enum):
    ABANDONMENT = "abandonment"
    SHAME = "shame"
    BETRAYAL = "betrayal"
    VIOLENCE = "violence"
    POWERLESSNESS = "powerlessness"
    PARENTAL_ABUSE = "parental_abuse"
    FAILURE = "failure"
    NEGLECT = "neglect"
    REJECTION = "rejection"
    DEATH_OF_LOVED_ONE = "death_of_loved_one"

class MemoryTag(Enum):
    CHILDHOOD = "childhood"
    FRIENDSHIP = "friendship"
    BETRAYAL = "betrayal"
    INTIMACY = "intimacy"
    CONFLICT = "conflict"
    LOSS = "loss"
    VICTORY = "victory"
    FAILURE = "failure"
    LOVE = "love"
    TRAUMA = "trauma"

class InterpretationModifierKey(Enum):
    NEUROTICISM = "neuroticism"
    EMPATHY = "empathy"
    AGGRESSION = "aggression"
    TRUST = "trust"
    SUSPICION = "suspicion"
    DOMINANCE_DRIVE = "dominance_drive"
    ATTACHMENT_STYLE = "attachment_style"
    INSECURITY = "insecurity"

@dataclass
class RawStimulus:
    channel: RawStimulusChannel
    content: str
    actors: List[str] = field(default_factory=list)
    target: List[str] = field(default_factory=list)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    location: Optional[str] = None

@dataclass
class InterpretedStimulus:
    raw_content: str
    actor: str
    stimulus_type: StimulusType
    schema: List[StimulusSchema]
    intent: Optional[StimulusIntent]
    salience: Dict[SalienceType, float]
    memory_references: List[MemoryTag] = field(default_factory=list)
    trauma_triggers: List[TraumaTag] = field(default_factory=list)
    interpretation_modifiers: Dict[InterpretationModifierKey, float] = field(default_factory=dict)
    timestamp: Optional[float] = None
    location: Optional[str] = None
    confidence: Optional[float] = 1.0