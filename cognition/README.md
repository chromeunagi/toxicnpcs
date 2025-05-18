# Toxicnpcs Cognition System

The cognition system is responsible for the intelligence, personality and decision-making of NPCs in the game. It's designed to create emergent behavior through a combination of stimulus processing, personality traits, and weighted decision making.

## Key Components

### 1. Stimulus Interpretation

Incoming game events (dialogue, actions, environmental changes) are processed and transformed into `InterpretedStimulus` objects, which include:

- Raw content (what happened)
- Actor (who did it)
- Schema (archetypal patterns like THREAT, INSULT, REQUEST)
- Intent (perceived motivation like HUMILIATE, BUILD_RAPPORT)
- Salience (importance across emotional, narrative, relationship dimensions)

### 2. PersonalityEngine

The `PersonalityEngine` defines core traits that influence how an NPC interprets and responds to stimuli. Features include:

- Core personality dimensions (aggressiveness, extraversion, neuroticism, etc.)
- Context-sensitive modifiers (stress, mood, trust levels)
- Quirks (unique behavioral patterns)
- Non-deterministic trait influences with controlled randomness
- Preset personalities and random generation

### 3. DecisionEngine

The `DecisionEngine` selects and executes tools (actions) in response to stimuli, influenced by:

- Personality traits of the NPC
- Properties of the stimulus
- Base heuristic rules
- Non-deterministic weighted selection
- Decision history tracking

### 4. Tools

Tools are the concrete actions an NPC can take, such as:

- DialogueResponseTool: Generate verbal responses
- FleeTool: Run away from threats
- (Future) AttackTool, ItemUseTool, etc.

## How It Works Together

1. A game event is converted into an `InterpretedStimulus`
2. The `DecisionEngine` receives the stimulus
3. Personality traits influence the probability of different responses
4. A tool is selected based on weighted probabilities (with intentional non-determinism)
5. The tool is executed, producing a concrete NPC action
6. The action is recorded in decision history for potential pattern analysis

## Example Flow

```
Player insults NPC →
  Interpreted as {INSULT schema, HUMILIATE intent} →
    DecisionEngine evaluates options influenced by Personality:
      - High aggressiveness → Higher chance of DialogueResponseTool (confrontation)
      - High neuroticism → Higher chance of FleeTool (avoidance)
      - Plus some randomness for non-deterministic behavior →
        Selected tool executes the concrete action
```

## Future Enhancements

- Memory system for long-term storage of events, relationships, and patterns
- Emotional modeling for more dynamic responses
- Narrative arc awareness for cohesive character development
- Moral system with values and ethical reasoning
- Learning and adaptation based on experience
