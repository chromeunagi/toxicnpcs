from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, List
import random


class PersonalityDimension(Enum):
    """Core personality dimensions based loosely on psychological models."""
    AGGRESSIVENESS = "aggressiveness"  # Fight vs flight tendencies
    EXTRAVERSION = "extraversion"  # Social engagement vs reserve
    NEUROTICISM = "neuroticism"  # Emotional stability vs volatility
    OPENNESS = "openness"  # Curiosity vs caution
    CONSCIENTIOUSNESS = "conscientiousness"  # Methodical vs spontaneous
    AGREEABLENESS = "agreeableness"  # Cooperative vs competitive
    DOMINANCE = "dominance"  # Leading vs following
    RISK_TOLERANCE = "risk_tolerance"  # Bold vs cautious


class PersonalityModifier(Enum):
    """Modifiers that can adjust how personality traits express in different contexts."""
    STRESS = "stress"  # Higher stress can amplify traits
    FAMILIARITY = "familiarity"  # Comfort with situation/person
    TRUST = "trust"  # Trust level toward interaction partner
    MOOD = "mood"  # Current emotional state
    POWER_DYNAMIC = "power_dynamic"  # Relative social position


@dataclass
class Personality:
    """
    Defines a character's personality as a set of trait dimensions.
    Each trait is a float from 0.0 to 1.0, where:
    - 0.0 represents the extreme low end of the trait
    - 0.5 represents a neutral or balanced position
    - 1.0 represents the extreme high end of the trait
    """
    name: str
    traits: Dict[PersonalityDimension, float] = field(default_factory=dict)
    modifiers: Dict[PersonalityModifier, float] = field(default_factory=dict)
    quirks: List[str] = field(default_factory=list)  # Special behavioral patterns
    description: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate and normalize trait values."""
        for trait, value in self.traits.items():
            self.traits[trait] = max(0.0, min(1.0, value))  # Clamp to [0, 1]

    def get_trait(self, trait: PersonalityDimension) -> float:
        """Get a trait value, defaulting to 0.5 (neutral) if not set."""
        return self.traits.get(trait, 0.5)

    def get_modifier(self, modifier: PersonalityModifier) -> float:
        """Get a modifier value, defaulting to 0.5 (neutral) if not set."""
        return self.modifiers.get(modifier, 0.5)

    def update_modifier(self, modifier: PersonalityModifier, value: float) -> None:
        """Update a modifier with a new value, clamped to [0, 1]."""
        self.modifiers[modifier] = max(0.0, min(1.0, value))

    def influence_value(self, base_value: float, trait: PersonalityDimension, 
                        influence_strength: float = 0.3) -> float:
        """
        Influence a base value using a personality trait.
        
        Args:
            base_value: The starting value (0.0-1.0)
            trait: Which personality trait should influence this value
            influence_strength: How strongly the trait should influence (0.0-1.0)
        
        Returns:
            Modified value (0.0-1.0)
        """
        trait_value = self.get_trait(trait)
        # Center the trait value around 0 (-0.5 to 0.5)
        trait_influence = (trait_value - 0.5) * influence_strength
        # Apply the influence to the base value and clamp
        return max(0.0, min(1.0, base_value + trait_influence))

    def add_randomness(self, value: float, randomness: float = 0.1) -> float:
        """Add a touch of randomness to a value to ensure non-deterministic behavior."""
        random_factor = random.uniform(-randomness, randomness)
        return max(0.0, min(1.0, value + random_factor))


class PersonalityFactory:
    """Creates and manages personality instances."""
    
    @staticmethod
    def create_random_personality(name: str) -> Personality:
        """Generate a random personality."""
        traits = {
            trait: random.uniform(0.0, 1.0)
            for trait in PersonalityDimension
        }
        
        # Create some random quirks
        possible_quirks = [
            "Laughs when nervous",
            "Avoids eye contact",
            "Speaks in metaphors",
            "Fidgets when lying",
            "Easily distracted by shiny objects",
            "Cannot resist a challenge",
            "Always looking over shoulder",
            "Hums when thinking",
            "Refuses to admit mistakes",
            "Collects trophies from encounters"
        ]
        quirk_count = random.randint(1, 3)
        quirks = random.sample(possible_quirks, quirk_count)
        
        return Personality(
            name=name,
            traits=traits,
            quirks=quirks,
            description=f"Randomly generated personality for {name}"
        )
    
    @staticmethod
    def create_preset_personality(preset_type: str) -> Personality:
        """Create a personality from a preset type."""
        if preset_type.lower() == "aggressive":
            return Personality(
                name="Aggressive Personality",
                traits={
                    PersonalityDimension.AGGRESSIVENESS: 0.9,
                    PersonalityDimension.DOMINANCE: 0.8,
                    PersonalityDimension.NEUROTICISM: 0.7,
                    PersonalityDimension.AGREEABLENESS: 0.2,
                    PersonalityDimension.RISK_TOLERANCE: 0.7,
                },
                quirks=["Quick to anger", "Enjoys intimidation"],
                description="An aggressive, dominant personality that tends to confront rather than flee"
            )
        elif preset_type.lower() == "cautious":
            return Personality(
                name="Cautious Personality",
                traits={
                    PersonalityDimension.AGGRESSIVENESS: 0.2,
                    PersonalityDimension.NEUROTICISM: 0.6,
                    PersonalityDimension.OPENNESS: 0.3,
                    PersonalityDimension.CONSCIENTIOUSNESS: 0.8,
                    PersonalityDimension.RISK_TOLERANCE: 0.2,
                },
                quirks=["Always looks for escape routes", "Plans before acting"],
                description="A careful, risk-averse personality that prefers safety over confrontation"
            )
        elif preset_type.lower() == "friendly":
            return Personality(
                name="Friendly Personality",
                traits={
                    PersonalityDimension.EXTRAVERSION: 0.8,
                    PersonalityDimension.AGREEABLENESS: 0.9,
                    PersonalityDimension.OPENNESS: 0.7,
                    PersonalityDimension.CONSCIENTIOUSNESS: 0.6,
                    PersonalityDimension.NEUROTICISM: 0.3,
                },
                quirks=["Smiles frequently", "Tries to diffuse tension"],
                description="A warm, social personality that seeks connection and cooperation"
            )
        else:
            # Default to random if preset not recognized
            return PersonalityFactory.create_random_personality(preset_type) 