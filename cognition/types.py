from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import uuid
import time
from abc import ABC, abstractmethod

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
    confidence: Optional[float] = 1.0

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

# New classes for Interpretation Modifiers

class InterpretationModifier(ABC):
    """
    Base class for modifiers that transform a RawStimulus into or
    alter an InterpretedStimulus.
    """
    @abstractmethod
    def modify(self, stimulus_in_progress: InterpretedStimulus, raw_stimulus: RawStimulus) -> InterpretedStimulus:
        """
        Applies the modifier's logic to an InterpretedStimulus.
        This method's role might evolve if Gemini handles the full interpretation.
        It could be used for pre/post-processing around the Gemini call.

        Args:
            stimulus_in_progress: The current state of the interpreted stimulus.
            raw_stimulus: The original raw stimulus.

        Returns:
            The modified InterpretedStimulus.
        """
        pass

    @abstractmethod
    def get_prompt_contribution(self) -> str:
        """
        Returns a string describing this modifier's influence,
        to be used in constructing a prompt for an LLM.
        """
        pass

class PersonalityInterpretationModifier(InterpretationModifier):
    """
    Modifies stimulus interpretation based on personality traits.
    """
    def __init__(self, description: str, profile: Optional[Dict[InterpretationModifierKey, float]] = None):
        self.description = description
        self.profile = profile if profile else {}

    def get_prompt_contribution(self) -> str:
        contribution = f"Personality: {self.description}."
        if self.profile:
            profile_desc = ", ".join([f"{key.value}: {value}" for key, value in self.profile.items()])
            contribution += f" Specific traits: {profile_desc}."
        return contribution

    def modify(self, stimulus_in_progress: InterpretedStimulus, raw_stimulus: RawStimulus) -> InterpretedStimulus:
        print(f"Applying PersonalityInterpretationModifier to: {raw_stimulus.content}")
        # Actual modification logic (if any beyond prompt contribution) will go here
        # For instance, could directly populate stimulus_in_progress.interpretation_modifiers
        for key, value in self.profile.items():
            stimulus_in_progress.interpretation_modifiers[key] = value
        return stimulus_in_progress

class MemoryInterpretationModifier(InterpretationModifier):
    """
    Modifies stimulus interpretation based on memories and past experiences.
    """
    def __init__(self, relevant_memories_summary: str, triggered_traumas: Optional[List[TraumaTag]] = None):
        self.relevant_memories_summary = relevant_memories_summary
        self.triggered_traumas = triggered_traumas if triggered_traumas else []

    def get_prompt_contribution(self) -> str:
        contribution = f"Memory Context: {self.relevant_memories_summary}."
        if self.triggered_traumas:
            traumas_desc = ", ".join([trauma.value for trauma in self.triggered_traumas])
            contribution += f" Potential trauma triggers active: {traumas_desc}."
        return contribution

    def modify(self, stimulus_in_progress: InterpretedStimulus, raw_stimulus: RawStimulus) -> InterpretedStimulus:
        print(f"Applying MemoryInterpretationModifier to: {raw_stimulus.content}")
        # Actual modification logic (if any beyond prompt contribution) will go here
        # For instance, could directly populate stimulus_in_progress.trauma_triggers or memory_references
        if self.triggered_traumas:
            for trauma in self.triggered_traumas:
                if trauma not in stimulus_in_progress.trauma_triggers:
                    stimulus_in_progress.trauma_triggers.append(trauma)
        return stimulus_in_progress

class AspirationsInterpretationModifier(InterpretationModifier):
    """
    Modifies stimulus interpretation based on an agent's goals and aspirations.
    """
    def __init__(self, current_goals_summary: str):
        self.current_goals_summary = current_goals_summary

    def get_prompt_contribution(self) -> str:
        return f"Aspirations Context: {self.current_goals_summary}."

    def modify(self, stimulus_in_progress: InterpretedStimulus, raw_stimulus: RawStimulus) -> InterpretedStimulus:
        print(f"Applying AspirationsInterpretationModifier to: {raw_stimulus.content}")
        # Actual modification logic (if any beyond prompt contribution) will go here
        return stimulus_in_progress