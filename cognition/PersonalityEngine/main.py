from __future__ import annotations

from cognition.PersonalityEngine.personality import (
    Personality, 
    PersonalityDimension,
    PersonalityFactory
)


def demonstrate_personality_variations():
    """Show how different personality types influence the same base action."""
    aggressive = PersonalityFactory.create_preset_personality("aggressive")
    cautious = PersonalityFactory.create_preset_personality("cautious")
    friendly = PersonalityFactory.create_preset_personality("friendly")
    random_npc = PersonalityFactory.create_random_personality("Random NPC")
    
    # Define a base action probability value (0.5 = neutral chance)
    base_flee_chance = 0.5
    base_attack_chance = 0.5
    base_negotiate_chance = 0.5
    
    # Show how personalities influence these base chances
    personalities = [aggressive, cautious, friendly, random_npc]
    
    print("\nPersonality Influence Demo:")
    print("-" * 50)
    
    for p in personalities:
        # Apply personality traits to action probabilities
        flee_chance = p.influence_value(
            base_flee_chance, 
            PersonalityDimension.AGGRESSIVENESS,
            influence_strength=0.5  # Higher strength = more influence
        )
        # Invert aggressiveness for attack tendency (high aggression = high attack)
        attack_chance = p.influence_value(
            base_attack_chance, 
            PersonalityDimension.AGGRESSIVENESS,
            influence_strength=0.5
        )
        # Extraversion influences negotiation tendency
        negotiate_chance = p.influence_value(
            base_negotiate_chance, 
            PersonalityDimension.EXTRAVERSION,
            influence_strength=0.4
        )
        
        # Add some randomness (non-determinism)
        flee_chance = p.add_randomness(flee_chance, 0.1)
        attack_chance = p.add_randomness(attack_chance, 0.1)
        negotiate_chance = p.add_randomness(negotiate_chance, 0.1)
        
        print(f"\n{p.name} ({p.description}):")
        for trait, value in p.traits.items():
            print(f"  - {trait.name}: {value:.2f}")
        print(f"  Quirks: {', '.join(p.quirks)}")
        print(f"  Action tendencies:")
        print(f"    - Flee: {flee_chance:.2f}")
        print(f"    - Attack: {attack_chance:.2f}")
        print(f"    - Negotiate: {negotiate_chance:.2f}")


if __name__ == "__main__":
    demonstrate_personality_variations() 