from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class StimulusType(Enum):
    """High-level modality of the incoming stimulus."""

    DIALOGUE = "dialogue"
    GESTURE = "gesture"
    ENVIRONMENT = "environment"
    ACTION = "action"
    OBJECT_INTERACTION = "object_interaction"
    PHYSICAL_CONTACT = "physical_contact"


class StimulusSchema(Enum):
    """Archetypal cognitive/narrative patterns applied to a stimulus."""

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


class StimulusIntent(Enum):
    """Perceived motive behind the stimulus."""

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
    """Dimensions which contribute to overall importance weighting."""

    EMOTIONAL = "emotional"
    RELATIONSHIP = "relationship"
    NARRATIVE = "narrative"
    EXISTENTIAL = "existential"
    MORAL = "moral"


class TraumaTag(Enum):
    """Core psychological wounds that can be triggered."""

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
    """Standard taxonomy for episodic / semantic memories."""

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
    """Personality or transient state multipliers that bias interpretation."""

    NEUROTICISM = "neuroticism"
    EMPATHY = "empathy"
    AGGRESSION = "aggression"
    TRUST = "trust"
    SUSPICION = "suspicion"
    DOMINANCE_DRIVE = "dominance_drive"
    ATTACHMENT_STYLE = "attachment_style"
    INSECURITY = "insecurity"


@dataclass
class InterpretedStimulus:
    """Normalized perception package passed into the decision engine."""

    # Raw observation
    raw_content: str
    actor: str
    stimulus_type: StimulusType

    # Cognitive interpretation
    schema: List[StimulusSchema]
    intent: StimulusIntent
    salience: Dict[SalienceType, float]

    # Memory & trauma interactions
    memory_references: List[MemoryTag] = field(default_factory=list)
    trauma_triggers: List[TraumaTag] = field(default_factory=list)

    # Personality / dynamic modifiers
    interpretation_modifiers: Dict[InterpretationModifierKey, float] = field(default_factory=dict)

    # Meta
    timestamp: Optional[float] = None
    location: Optional[str] = None
    confidence: Optional[float] = 1.0

    # Utility helpers -----------------------------------------------------
    def salience_score(self) -> float:
        """Return an overall salience score (simple average for now)."""
        if not self.salience:
            return 0.0
        return sum(self.salience.values()) / len(self.salience)

    def __post_init__(self) -> None:
        # Basic validation to catch obvious mistakes early
        if any(s not in StimulusSchema for s in self.schema):
            illegal = [s for s in self.schema if s not in StimulusSchema]
            raise ValueError(f"Unknown schema values: {illegal}") 