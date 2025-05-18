from __future__ import annotations

import random
from typing import Any, Dict, Type, Optional, List, Tuple, Set

from cognition.DecisionEngine.stimulus import (
    InterpretedStimulus,
    StimulusIntent,
    StimulusSchema,
    StimulusType,
    SalienceType,
)
from cognition.DecisionEngine.toolbox import get_tool, Tool, _TOOL_REGISTRY

from cognition.PersonalityEngine.personality import (
    Personality,
    PersonalityDimension,
    PersonalityModifier,
    PersonalityFactory,
)

# Import DecisionClient for LLM-based decisions
from cognition.clients.decision_client import DecisionClient


class ToolCategory:
    """Categories of tools for decision making."""
    DIALOGUE = "dialogue_tools"
    COMBAT = "combat_tools"
    MOVEMENT = "movement_tools"
    SOCIAL = "social_tools"
    EMOTIONAL = "emotional_tools"
    ITEM = "item_tools"
    ENVIRONMENTAL = "environmental_tools"
    COMMUNICATION = "communication_tools"
    OBSERVATION = "observation_tools"
    SELF_CARE = "self_care_tools"
    EVERYDAY_OBJECT = "everyday_object_tools"
    SOCIAL_MANEUVERING = "social_maneuvering_tools"
    COGNITIVE = "cognitive_tools"
    SUBTLE_EXPRESSION = "subtle_expression_tools"


class DecisionEngine:
    """Selects and executes the best tool for a given interpreted stimulus."""

    def __init__(self, 
                use_llm: bool = False, 
                personality: Optional[Personality] = None,
                decision_client: Optional[DecisionClient] = None) -> None:
        """
        Initialize the decision engine with optional personality.
        
        Args:
            use_llm: Whether to use LLM for decision making
            personality: Optional personality to influence decisions. If None, 
                         a random personality will be created.
            decision_client: Optional client for LLM-based decisions
        """
        self.use_llm = use_llm
        self.personality = personality or PersonalityFactory.create_random_personality("Default NPC")
        self.decision_client = decision_client
        
        # Set mood context - this can change over time as the NPC experiences events
        self.personality.update_modifier(PersonalityModifier.MOOD, 0.5)  # neutral mood
        self.personality.update_modifier(PersonalityModifier.STRESS, 0.2)  # low initial stress
        
        # Track decision history for potential pattern analysis
        self.decision_history: List[Tuple[InterpretedStimulus, str]] = []
        
        # Cache of available tools organized by category
        self._tools_by_category = self._organize_tools_by_category()

    # ------------------------------------------------------------------
    # PUBLIC INTERFACE
    # ------------------------------------------------------------------
    def decide_and_act(self, stimulus: InterpretedStimulus) -> str:
        """High-level API: choose a tool and execute it, returning the action."""
        # Update modifiers based on stimulus
        self._update_modifiers(stimulus)

        tool_cls = self._select_tool(stimulus)
        tool_instance: Tool = tool_cls()
        kwargs: Dict[str, Any] = self._build_tool_kwargs(tool_instance, stimulus)
        action_result = tool_instance.execute(**kwargs)
        
        # Record this decision for history/patterns
        self.decision_history.append((stimulus, tool_instance.name))
        
        return action_result

    # ------------------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------------------
    def _organize_tools_by_category(self) -> Dict[str, Dict[str, Type[Tool]]]:
        """Organize available tools by their module/category."""
        result = {}
        
        for tool_name, tool_class in _TOOL_REGISTRY.items():
            module_name = tool_class.__module__.split('.')[-1]
            if module_name not in result:
                result[module_name] = {}
            result[module_name][tool_name] = tool_class
            
        return result
    
    def _update_modifiers(self, stimulus: InterpretedStimulus) -> None:
        """Update personality modifiers based on the stimulus properties."""
        # Adjust stress level based on threat and emotional salience
        if StimulusSchema.THREAT in stimulus.schema:
            current_stress = self.personality.get_modifier(PersonalityModifier.STRESS)
            emotional_impact = stimulus.salience.get(SalienceType.EMOTIONAL, 0.5)
            # Increase stress more for high emotional impact threats
            stress_increase = 0.2 * emotional_impact
            self.personality.update_modifier(
                PersonalityModifier.STRESS, 
                min(1.0, current_stress + stress_increase)
            )
        
        # Adjust mood based on stimulus intent and schema
        current_mood = self.personality.get_modifier(PersonalityModifier.MOOD)
        mood_change = 0.0
        
        # Negative intents decrease mood
        if stimulus.intent in [StimulusIntent.HUMILIATE, StimulusIntent.PROVOKE]:
            mood_change -= 0.1
        
        # Positive intents increase mood
        if stimulus.intent in [StimulusIntent.BUILD_RAPPORT, StimulusIntent.EXPRESS_LOVE]:
            mood_change += 0.1
        
        # Negative schemas decrease mood
        if any(schema in stimulus.schema for schema in 
              [StimulusSchema.THREAT, StimulusSchema.INSULT, StimulusSchema.VIOLENCE]):
            mood_change -= 0.1
        
        # Positive schemas increase mood
        if any(schema in stimulus.schema for schema in 
              [StimulusSchema.PRAISE, StimulusSchema.REASSURANCE, StimulusSchema.COMPASSION]):
            mood_change += 0.1
            
        # Apply mood change, keeping within bounds
        self.personality.update_modifier(
            PersonalityModifier.MOOD,
            max(0.0, min(1.0, current_mood + mood_change))
        )

    def _select_tool(self, stimulus: InterpretedStimulus) -> Type[Tool]:
        """Return the Tool class to handle the stimulus.

        If self.use_llm is True, we will use the DecisionClient to query an LLM.
        Otherwise, we employ personality-influenced heuristics with weighted random choices.
        """
        if self.use_llm:
            if self.decision_client:
                return self._llm_select_tool(stimulus)
            else:
                # Placeholder for mock LLM selection logic
                tool_name = self._mock_llm_select(stimulus)
                return get_tool(tool_name)

        # Get personality-influenced probabilities for each tool
        tool_probabilities = self._calculate_tool_probabilities(stimulus)
        
        # If no tools match or are available, raise an error
        if not tool_probabilities:
            raise ValueError("No suitable tools available for decision.")
            
        # Weighted random selection based on probabilities
        tools, weights = zip(*tool_probabilities.items())
        selected_tool = random.choices(tools, weights=weights, k=1)[0]
        
        return get_tool(selected_tool)
    
    def _llm_select_tool(self, stimulus: InterpretedStimulus) -> Type[Tool]:
        """
        Use the DecisionClient to query an LLM for tool selection.
        """
        # Create a context dict with personality information for the LLM
        context = self._create_personality_context()
        
        # Add available tools information
        context["available_actions"] = self._get_available_tools_info()
        
        try:
            # Query the LLM via DecisionClient
            decision = self.decision_client.decide_action(
                interpreted_stimulus=stimulus,
                context=context
            )
            
            # Convert the LLM decision to a Tool class
            return self._decision_to_tool(decision)
        except Exception as e:
            print(f"Error using DecisionClient: {e}")
            print("Falling back to heuristic tool selection")
            # Fall back to the probability-based selection
            tool_probabilities = self._calculate_tool_probabilities(stimulus)
            tools, weights = zip(*tool_probabilities.items())
            selected_tool = random.choices(tools, weights=weights, k=1)[0]
            return get_tool(selected_tool)
    
    def _create_personality_context(self) -> Dict[str, Any]:
        """Create a context dictionary with personality information for the LLM."""
        # Extract top traits (those with values > 0.6)
        top_traits = {}
        for trait, value in sorted(
            self.personality.traits.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if value > 0.6:
                top_traits[trait.name] = value
        
        # Get current mood and stress
        mood = self.personality.get_modifier(PersonalityModifier.MOOD)
        stress = self.personality.get_modifier(PersonalityModifier.STRESS)
        
        # Create mood description
        mood_desc = "neutral"
        if mood > 0.7:
            mood_desc = "positive"
        elif mood < 0.3:
            mood_desc = "negative"
            
        # Create stress description
        stress_desc = "calm"
        if stress > 0.7:
            stress_desc = "highly stressed"
        elif stress > 0.4:
            stress_desc = "somewhat tense"
            
        # Create personality summary
        traits_summary = ", ".join([f"high {name.lower()}" for name in top_traits])
        if not traits_summary:
            traits_summary = "balanced traits"
        
        quirks_summary = ""
        if self.personality.quirks:
            quirks_summary = f" with quirks: {', '.join(self.personality.quirks)}"
        
        personality_summary = f"A character with {traits_summary}, currently {mood_desc} and {stress_desc}{quirks_summary}."
        
        return {
            "npc_personality_summary": personality_summary,
            "npc_current_mood": mood_desc,
            "npc_current_stress": stress_desc,
            "npc_traits": {t.name: v for t, v in self.personality.traits.items()},
            "npc_quirks": self.personality.quirks
        }
    
    def _get_available_tools_info(self) -> List[Dict[str, str]]:
        """Get information about available tools for the LLM."""
        tool_info = []
        
        for tool_name, tool_class in _TOOL_REGISTRY.items():
            tool_info.append({
                "name": tool_class.name,
                "description": tool_class.description
            })
            
        return tool_info
    
    def _decision_to_tool(self, decision: Dict[str, Any]) -> Type[Tool]:
        """Convert a decision from the LLM to a Tool class."""
        # Get the action name from the decision
        action = decision.get("action", "dialogue_response")
        
        # Map the action to a tool
        tool_name = self._map_action_to_tool(action)
        
        try:
            # Try to get the tool class
            return get_tool(tool_name)
        except KeyError:
            # If the tool doesn't exist, fallback to DialogueResponseTool
            print(f"Warning: Tool '{tool_name}' not found, falling back to DialogueResponseTool")
            return get_tool("DialogueResponseTool")
    
    def _map_action_to_tool(self, action: str) -> str:
        """Map an action name from the LLM to a tool class name."""
        # Direct mappings
        action_to_tool = {
            "attack": "AttackTool",
            "defend": "DefendTool",
            "threaten": "ThreatenTool",
            "disarm": "DisarmTool",
            "stun": "StunTool",
            "flee": "FleeTool",
            "retreat": "RetreatTool",
            "hide": "HideTool",
            "approach": "ApproachTool",
            "circle": "CircleTool",
            "take_cover": "TakeCoverTool",
            "greet": "GreetTool",
            "apologize": "ApologizeTool",
            "offer_help": "OfferHelpTool",
            "befriend": "BefriendTool",
            "bargain": "BargainTool",
            "request_info": "RequestInfoTool",
            "express_emotion": "ExpressEmotionTool",
            "laugh": "LaughTool",
            "cry": "CryTool",
            "panic": "PanicTool",
            "show_confusion": "ShowConfusionTool",
            "use_item": "UseItemTool",
            "give_item": "GiveItemTool",
            "take_item": "TakeItemTool",
            "examine_item": "ExamineItemTool",
            "equip_item": "EquipItemTool",
            "craft_item": "CraftItemTool",
            "search_area": "SearchAreaTool",
            "listen": "ListenTool",
            "set_trap": "SetTrapTool",
            "create_distraction": "CreateDistraction",
            "interact_environment": "InteractEnvironmentTool",

            # Communication Tools
            "persuade": "PersuadeTool",
            "deceive": "DeceiveTool",
            "gossip": "GossipTool",
            "complain": "ComplainTool",
            "comfort": "ComfortTool",
            "encourage": "EncourageTool",
            "advise": "AdviseTool",
            "argue": "ArgueTool",

            # Observation Tools
            "observe_person": "ObservePersonTool",
            "observe_environment": "ObserveEnvironmentTool",
            "eavesdrop": "EavesdropTool",
            "read_body_language": "ReadBodyLanguageTool",
            "investigate_anomaly": "InvestigateAnomalyTool",

            # Self-Care Tools
            "eat": "EatTool",
            "drink": "DrinkTool",
            "rest": "RestTool",
            "groom": "GroomTool",
            "seek_comfort": "SeekComfortTool",
            "stretch": "StretchTool",

            # Everyday Object Tools
            "pick_up_object": "PickUpObjectTool",
            "put_down_object": "PutDownObjectTool",
            "open_object": "OpenObjectTool",
            "close_object": "CloseObjectTool",
            "use_everyday_object": "UseEverydayObjectTool",
            "tidy_up": "TidyUpTool",
            "prepare_food_or_drink": "PrepareFoodOrDrinkTool",

            # Social Maneuvering Tools
            "ignore": "IgnoreTool",
            "avoid": "AvoidTool",
            "join_group": "JoinGroupTool",
            "leave_group": "LeaveGroupTool",
            "show_politeness": "ShowPolitenessTool",
            "show_impatience": "ShowImpatienceTool",

            # Cognitive Tools
            "ponder": "PonderTool",
            "make_plan": "MakePlanTool",
            "reconsider": "ReconsiderTool",
            "daydream": "DaydreamTool",
            "recall_memory": "RecallMemoryTool",
            "focus_attention": "FocusAttentionTool",

            # Subtle Expression Tools
            "sigh": "SighTool",
            "fidget": "FidgetTool",
            "shift_weight": "ShiftWeightTool",
            "glance": "GlanceTool",
            "raise_eyebrow": "RaiseEyebrowTool",
            "tighten_lips": "TightenLipsTool",
        }
        
        # Generic mappings for common categories
        if action.startswith("say_") or action.startswith("speak_") or action == "speak" or action == "say":
            return "DialogueResponseTool"
        
        if action.startswith("ask_"):
            return "AskQuestionTool"
            
        if action.startswith("monologue_") or action == "monologue":
            return "MonologueTool"
            
        # Use direct mapping if available
        if action in action_to_tool:
            return action_to_tool[action]
            
        # Fallback to dialogue response for any other actions
        return "DialogueResponseTool"
    
    def _calculate_tool_probabilities(self, 
                                     stimulus: InterpretedStimulus) -> Dict[str, float]:
        """
        Calculate probability weights for each available tool based on:
        1. The stimulus properties
        2. Personality traits and modifiers
        3. Base heuristic rules
        4. A touch of randomness for non-determinism
        
        Returns a dict mapping tool names to their probability weights.
        """
        # First determine which tool categories to consider for this stimulus
        category_probabilities = self._calculate_category_probabilities(stimulus)
        
        # Initialize with all tools having zero probability
        probabilities: Dict[str, float] = {}
        
        # Set base probabilities for tools in relevant categories
        for category, category_prob in category_probabilities.items():
            if category in self._tools_by_category:
                tools_in_category = self._tools_by_category[category]
                
                # Distribute the category probability among tools in this category
                tool_base_prob = category_prob / len(tools_in_category) if tools_in_category else 0
                
                for tool_name in tools_in_category:
                    probabilities[tool_name] = tool_base_prob
        
        # Apply stimulus-specific adjustments
        self._adjust_probabilities_for_stimulus(probabilities, stimulus)
        
        # Apply personality-specific adjustments
        self._adjust_probabilities_for_personality(probabilities, stimulus)
        
        # Add randomness for non-deterministic behavior
        for tool in list(probabilities.keys()):
            probabilities[tool] = self.personality.add_randomness(
                probabilities[tool], 
                randomness=0.15
            )
        
        # Remove tools with negligible probability
        probabilities = {k: v for k, v in probabilities.items() if v > 0.01}
        
        # Normalize probabilities to ensure they sum to 1.0
        total = sum(probabilities.values())
        if total > 0:
            for tool in probabilities:
                probabilities[tool] /= total
                
        return probabilities
    
    def _calculate_category_probabilities(self, stimulus: InterpretedStimulus) -> Dict[str, float]:
        """Determine which tool categories are most relevant for this stimulus."""
        result = {
            ToolCategory.DIALOGUE: 0.1,
            ToolCategory.COMBAT: 0.1,
            ToolCategory.MOVEMENT: 0.1,
            ToolCategory.SOCIAL: 0.1,
            ToolCategory.EMOTIONAL: 0.1,
            ToolCategory.ITEM: 0.1,
            ToolCategory.ENVIRONMENTAL: 0.1,
            ToolCategory.COMMUNICATION: 0.05,
            ToolCategory.OBSERVATION: 0.05,
            ToolCategory.SELF_CARE: 0.05,  # Base for idle/background
            ToolCategory.EVERYDAY_OBJECT: 0.05, # Base for idle/background
            ToolCategory.SOCIAL_MANEUVERING: 0.05,
            ToolCategory.COGNITIVE: 0.05, # Base for idle/background
            ToolCategory.SUBTLE_EXPRESSION: 0.05, 
        }
        
        # Stimulus type strongly influences category selection
        if stimulus.stimulus_type == StimulusType.DIALOGUE:
            result[ToolCategory.DIALOGUE] += 0.4
            result[ToolCategory.SOCIAL] += 0.2
            result[ToolCategory.EMOTIONAL] += 0.1
            result[ToolCategory.COMMUNICATION] += 0.2
            result[ToolCategory.SUBTLE_EXPRESSION] += 0.1
            result[ToolCategory.COGNITIVE] += 0.05
            
        elif stimulus.stimulus_type == StimulusType.GESTURE:
            result[ToolCategory.MOVEMENT] += 0.2
            result[ToolCategory.SOCIAL] += 0.2
            result[ToolCategory.EMOTIONAL] += 0.2
            result[ToolCategory.OBSERVATION] += 0.15
            result[ToolCategory.SUBTLE_EXPRESSION] += 0.1
            
        elif stimulus.stimulus_type == StimulusType.ACTION:
            result[ToolCategory.MOVEMENT] += 0.2
            result[ToolCategory.COMBAT] += 0.2
            # Could also be observing the action
            result[ToolCategory.OBSERVATION] += 0.1
            
        elif stimulus.stimulus_type == StimulusType.ENVIRONMENT:
            result[ToolCategory.ENVIRONMENTAL] += 0.4
            result[ToolCategory.MOVEMENT] += 0.2
            result[ToolCategory.OBSERVATION] += 0.2
            # If environment is neutral, might ponder or do self-care
            if stimulus.salience_score() < 0.3: # Assuming salience_score() is available
                result[ToolCategory.COGNITIVE] += 0.1
                result[ToolCategory.SELF_CARE] += 0.05
                result[ToolCategory.EVERYDAY_OBJECT] += 0.05
            
        elif stimulus.stimulus_type == StimulusType.OBJECT_INTERACTION:
            result[ToolCategory.ITEM] += 0.4
            result[ToolCategory.ENVIRONMENTAL] += 0.2
            result[ToolCategory.EVERYDAY_OBJECT] += 0.3
            result[ToolCategory.OBSERVATION] += 0.1 # Observe the object or interaction
            
        elif stimulus.stimulus_type == StimulusType.PHYSICAL_CONTACT:
            result[ToolCategory.COMBAT] += 0.3
            result[ToolCategory.MOVEMENT] += 0.2
            result[ToolCategory.EMOTIONAL] += 0.2
            # Could be a comforting touch, etc.
            result[ToolCategory.SOCIAL] += 0.1
            result[ToolCategory.COMMUNICATION] += 0.05 # e.g. ComfortTool could be verbal part of this
            
        # Stimulus schema affects category choice
        if StimulusSchema.THREAT in stimulus.schema or StimulusSchema.VIOLENCE in stimulus.schema:
            result[ToolCategory.COMBAT] += 0.2
            result[ToolCategory.MOVEMENT] += 0.2
            result[ToolCategory.EMOTIONAL] += 0.1 # Panic, etc.
            result[ToolCategory.SOCIAL_MANEUVERING] += 0.1 # Avoid, Ignore
            
        if StimulusSchema.PRAISE in stimulus.schema or StimulusSchema.FLIRTATION in stimulus.schema:
            result[ToolCategory.SOCIAL] += 0.3
            result[ToolCategory.EMOTIONAL] += 0.2
            result[ToolCategory.DIALOGUE] += 0.1
            result[ToolCategory.SUBTLE_EXPRESSION] += 0.1 # Smile, glance

        if StimulusSchema.REQUEST in stimulus.schema:
            result[ToolCategory.DIALOGUE] += 0.2
            result[ToolCategory.SOCIAL] += 0.15
            result[ToolCategory.COMMUNICATION] += 0.2 # Advise, Persuade, Complain
            result[ToolCategory.COGNITIVE] += 0.1 # MakePlan, Reconsider

        if StimulusSchema.MYSTERY in stimulus.schema:
            result[ToolCategory.OBSERVATION] += 0.3 # Investigate, Observe
            result[ToolCategory.ENVIRONMENTAL] += 0.15 # SearchArea
            result[ToolCategory.COGNITIVE] += 0.2 # Ponder, RecallMemory

        if StimulusSchema.DECEPTION in stimulus.schema:
            result[ToolCategory.OBSERVATION] += 0.15 # Try to see through it
            result[ToolCategory.COGNITIVE] += 0.1 # Reconsider, Ponder
            result[ToolCategory.COMMUNICATION] += 0.1 # Could be to Argue or Deceive back

        # Stimulus intent affects category choice
        if stimulus.intent == StimulusIntent.PROVOKE or stimulus.intent == StimulusIntent.HUMILIATE:
            result[ToolCategory.COMBAT] += 0.1
            result[ToolCategory.EMOTIONAL] += 0.2
            
        if stimulus.intent == StimulusIntent.BUILD_RAPPORT or stimulus.intent == StimulusIntent.EXPRESS_LOVE:
            result[ToolCategory.SOCIAL] += 0.3
            result[ToolCategory.DIALOGUE] += 0.2
            
        # Stimulus salience affects category weighting
        if SalienceType.EMOTIONAL in stimulus.salience and stimulus.salience[SalienceType.EMOTIONAL] > 0.7:
            result[ToolCategory.EMOTIONAL] += 0.2
            
        # Normalize values
        total = sum(result.values())
        for category in result:
            result[category] /= total
            
        return result
    
    def _adjust_probabilities_for_stimulus(self, probabilities: Dict[str, float], stimulus: InterpretedStimulus) -> None:
        """Make stimulus-specific adjustments to tool probabilities."""
        # THREAT response adjustments
        if StimulusSchema.THREAT in stimulus.schema:
            self._adjust_tool_probability_group(probabilities, ["FleeTool", "HideTool", "TakeCoverTool"], 0.3)
            self._adjust_tool_probability_group(probabilities, ["DefendTool", "ThreatenTool"], 0.2)
            
        # VIOLENCE response adjustments
        if StimulusSchema.VIOLENCE in stimulus.schema:
            self._adjust_tool_probability_group(probabilities, ["FleeTool", "RetreatTool"], 0.3)
            self._adjust_tool_probability_group(probabilities, ["AttackTool", "DefendTool"], 0.3)
            
        # FLIRTATION response adjustments
        if StimulusSchema.FLIRTATION in stimulus.schema:
            self._adjust_tool_probability_group(probabilities, ["DialogueResponseTool", "ExpressEmotionTool"], 0.3)
            
        # DIALOGUE response adjustments
        if stimulus.stimulus_type == StimulusType.DIALOGUE:
            self._adjust_tool_probability_group(probabilities, ["DialogueResponseTool", "AskQuestionTool", "MonologueTool"], 0.4)
            
        # Intent-specific adjustments
        if stimulus.intent == StimulusIntent.HUMILIATE:
            self._adjust_tool_probability_group(probabilities, ["ExpressEmotionTool", "DialogueResponseTool"], 0.2)
            
        elif stimulus.intent == StimulusIntent.BUILD_RAPPORT:
            self._adjust_tool_probability_group(probabilities, ["DialogueResponseTool", "ExpressEmotionTool", "BefriendTool"], 0.3)
            
        elif stimulus.intent == StimulusIntent.WARN:
            self._adjust_tool_probability_group(probabilities, ["RetreatTool", "DefendTool", "FleeTool"], 0.3)
    
    def _adjust_tool_probability_group(self, probabilities: Dict[str, float], tool_names: List[str], total_adjustment: float) -> None:
        """Increase probability for a group of tools by distributing the total adjustment among available tools."""
        # Filter to tools that are actually available
        available_tools = [tool for tool in tool_names if tool in probabilities]
        
        if not available_tools:
            return
            
        # Distribute adjustment evenly among available tools
        per_tool_adjustment = total_adjustment / len(available_tools)
        
        for tool in available_tools:
            probabilities[tool] += per_tool_adjustment
    
    def _adjust_probabilities_for_personality(self, probabilities: Dict[str, float], stimulus: InterpretedStimulus) -> None:
        """Adjust tool probabilities based on personality traits and current modifiers."""
        # AGGRESSIVENESS influence
        aggressiveness = self.personality.get_trait(PersonalityDimension.AGGRESSIVENESS)
        if aggressiveness > 0.7:  # Very aggressive
            self._adjust_tool_probability_group(probabilities, ["AttackTool", "ThreatenTool", "ArgueTool"], 0.2)
            self._adjust_tool_probability_group(probabilities, ["FleeTool", "HideTool", "RetreatTool", "ComfortTool", "ApologizeTool", "ShowPolitenessTool"], -0.2)
        elif aggressiveness < 0.3:  # Non-aggressive
            self._adjust_tool_probability_group(probabilities, ["FleeTool", "HideTool", "RetreatTool", "ComfortTool", "ApologizeTool", "ShowPolitenessTool"], 0.2)
            self._adjust_tool_probability_group(probabilities, ["AttackTool", "ThreatenTool", "ArgueTool"], -0.2)
            
        # EXTRAVERSION influence
        extraversion = self.personality.get_trait(PersonalityDimension.EXTRAVERSION)
        if extraversion > 0.7:  # Very extraverted
            self._adjust_tool_probability_group(
                probabilities, 
                ["DialogueResponseTool", "GreetTool", "AskQuestionTool", "MonologueTool", "BefriendTool", 
                 "PersuadeTool", "GossipTool", "EncourageTool", "JoinGroupTool"], 
                0.25
            )
            self._adjust_tool_probability_group(probabilities, ["IgnoreTool", "AvoidTool", "PonderTool"], -0.15)
        elif extraversion < 0.3:  # Introverted
            self._adjust_tool_probability_group(
                probabilities,
                ["HideTool", "SearchAreaTool", "ListenTool", "IgnoreTool", "AvoidTool", 
                 "LeaveGroupTool", "PonderTool", "DaydreamTool", "ObservePersonTool"],
                0.25
            )
            self._adjust_tool_probability_group(probabilities, ["GreetTool", "JoinGroupTool", "PersuadeTool"], -0.15)
            
        # NEUROTICISM influence
        neuroticism = self.personality.get_trait(PersonalityDimension.NEUROTICISM)
        if neuroticism > 0.7:  # Highly neurotic
            self._adjust_tool_probability_group(
                probabilities,
                ["ExpressEmotionTool", "PanicTool", "FleeTool", "ComplainTool", "CryTool", 
                 "SeekComfortTool", "FidgetTool", "SighTool", "ShowImpatienceTool", "ReconsiderTool"],
                0.25
            )
        elif neuroticism < 0.3: # Emotionally stable
             self._adjust_tool_probability_group(probabilities, ["ComfortTool", "ShowPolitenessTool"], 0.1)
             self._adjust_tool_probability_group(probabilities, ["PanicTool", "ComplainTool", "FidgetTool"], -0.1)
            
        # OPENNESS influence
        openness = self.personality.get_trait(PersonalityDimension.OPENNESS)
        if openness > 0.7:  # Very open
            self._adjust_tool_probability_group(
                probabilities,
                ["SearchAreaTool", "ExamineItemTool", "AskQuestionTool", "ObserveEnvironmentTool", 
                 "InvestigateAnomalyTool", "EavesdropTool", "RecallMemoryTool"],
                0.2
            )
        elif openness < 0.3: # Cautious/Less open
            self._adjust_tool_probability_group(probabilities, ["AvoidTool"], 0.1)
            self._adjust_tool_probability_group(probabilities, ["InvestigateAnomalyTool", "EavesdropTool"], -0.1)

        # CONSCIENTIOUSNESS influence
        conscientiousness = self.personality.get_trait(PersonalityDimension.CONSCIENTIOUSNESS)
        if conscientiousness > 0.7:  # Very conscientious
            self._adjust_tool_probability_group(
                probabilities,
                ["ExamineItemTool", "CraftItemTool", "SetTrapTool", "MakePlanTool", 
                 "FocusAttentionTool", "TidyUpTool", "PrepareFoodOrDrinkTool"],
                0.2
            )
        elif conscientiousness < 0.3: # Spontaneous
            self._adjust_tool_probability_group(probabilities, ["DaydreamTool", "CreateDistraction", "FidgetTool"], 0.15)
            self._adjust_tool_probability_group(probabilities, ["MakePlanTool", "FocusAttentionTool", "TidyUpTool"], -0.1)
            
        # AGREEABLENESS influence
        agreeableness = self.personality.get_trait(PersonalityDimension.AGREEABLENESS)
        if agreeableness > 0.7:  # Very agreeable
            self._adjust_tool_probability_group(
                probabilities,
                ["OfferHelpTool", "ApologizeTool", "BefriendTool", "ComfortTool", 
                 "EncourageTool", "ShowPolitenessTool"],
                0.25
            )
            self._adjust_tool_probability_group(
                probabilities,
                ["ThreatenTool", "AttackTool", "ArgueTool", "DeceiveTool", "ComplainTool"],
                -0.15
            )
        elif agreeableness < 0.3: # Disagreeable/Competitive
            self._adjust_tool_probability_group(
                probabilities,
                ["ArgueTool", "ComplainTool", "DeceiveTool", "ThreatenTool"],
                0.2
            )
            self._adjust_tool_probability_group(probabilities, ["OfferHelpTool", "ApologizeTool", "ComfortTool", "ShowPolitenessTool"], -0.15)

        # DOMINANCE influence
        dominance = self.personality.get_trait(PersonalityDimension.DOMINANCE)
        if dominance > 0.7:
            self._adjust_tool_probability_group(probabilities, ["PersuadeTool", "ThreatenTool", "ArgueTool", "MakePlanTool"], 0.2)
        elif dominance < 0.3:
            self._adjust_tool_probability_group(probabilities, ["ShowPolitenessTool", "ApologizeTool", "RequestInfoTool"], 0.15)

        # RISK_TOLERANCE influence
        risk_tolerance = self.personality.get_trait(PersonalityDimension.RISK_TOLERANCE)
        if risk_tolerance > 0.7:
            self._adjust_tool_probability_group(probabilities, ["InvestigateAnomalyTool", "ApproachTool", "DeceiveTool"], 0.15) # Add more risky actions
        elif risk_tolerance < 0.3:
            self._adjust_tool_probability_group(probabilities, ["AvoidTool", "RetreatTool", "TakeCoverTool", "PonderTool"], 0.2)
            
        # Modifier: STRESS
        stress = self.personality.get_modifier(PersonalityModifier.STRESS)
        if stress > 0.7:  # High stress
            self._adjust_tool_probability_group(
                probabilities,
                ["PanicTool", "FleeTool", "ExpressEmotionTool", "RetreatTool", "ComplainTool", 
                 "FidgetTool", "SighTool", "ShowImpatienceTool", "SeekComfortTool", "AvoidTool"],
                0.3
            )
            self._adjust_tool_probability_group(probabilities, ["FocusAttentionTool", "MakePlanTool", "PonderTool"], -0.2) # Difficulty concentrating
            
        # Modifier: MOOD
        mood = self.personality.get_modifier(PersonalityModifier.MOOD)
        if mood < 0.3:  # Bad mood
            self._adjust_tool_probability_group(
                probabilities,
                ["ExpressEmotionTool", "DialogueResponseTool", "ComplainTool", "ArgueTool", 
                 "SighTool", "IgnoreTool", "ShowImpatienceTool"],
                0.2
            )
            self._adjust_tool_probability_group(probabilities, ["EncourageTool", "LaughTool", "OfferHelpTool", "GreetTool"], -0.15)
        elif mood > 0.7:  # Good mood
            self._adjust_tool_probability_group(
                probabilities,
                ["DialogueResponseTool", "ExpressEmotionTool", "LaughTool", "GreetTool", 
                 "OfferHelpTool", "EncourageTool", "DaydreamTool"], 
                0.2
            )
            self._adjust_tool_probability_group(probabilities, ["ComplainTool", "ArgueTool", "SighTool"], -0.1)

        # Ensure no probabilities are negative after adjustments
        for tool_name in probabilities:
            probabilities[tool_name] = max(0.0, probabilities[tool_name])

    def _build_tool_kwargs(self, tool: Tool, stimulus: InterpretedStimulus) -> Dict[str, Any]:
        """Map stimulus to tool‐specific kwargs."""
        kwargs: Dict[str, Any] = {}
        
        # Common kwargs that apply to many tools
        personality_context = {
            "aggressiveness": self.personality.get_trait(PersonalityDimension.AGGRESSIVENESS),
            "extraversion": self.personality.get_trait(PersonalityDimension.EXTRAVERSION),
            "neuroticism": self.personality.get_trait(PersonalityDimension.NEUROTICISM),
            "openness": self.personality.get_trait(PersonalityDimension.OPENNESS),
            "conscientiousness": self.personality.get_trait(PersonalityDimension.CONSCIENTIOUSNESS),
            "agreeableness": self.personality.get_trait(PersonalityDimension.AGREEABLENESS),
            "dominance": self.personality.get_trait(PersonalityDimension.DOMINANCE),
            "stress": self.personality.get_modifier(PersonalityModifier.STRESS),
            "mood": self.personality.get_modifier(PersonalityModifier.MOOD),
            "quirks": self.personality.quirks,
        }

        # --- DIALOGUE TOOLS ---
        if tool.name == "dialogue_response":
            kwargs["prompt"] = stimulus.raw_content
            kwargs["personality_context"] = personality_context
            
            # Determine response tone based on personality and stimulus
            if self.personality.get_trait(PersonalityDimension.AGGRESSIVENESS) > 0.7:
                kwargs["tone"] = "hostile"
            elif self.personality.get_trait(PersonalityDimension.AGREEABLENESS) > 0.7:
                kwargs["tone"] = "friendly"
            elif self.personality.get_trait(PersonalityDimension.CONSCIENTIOUSNESS) > 0.7:
                kwargs["tone"] = "formal"
            elif self.personality.get_modifier(PersonalityModifier.STRESS) > 0.7:
                kwargs["tone"] = "defensive"
            elif self.personality.get_trait(PersonalityDimension.EXTRAVERSION) < 0.3:
                kwargs["tone"] = "neutral"
            else:
                kwargs["tone"] = "casual"
                
        elif tool.name == "ask_question":
            kwargs["topic"] = stimulus.raw_content or "the situation"
            # Determine question type based on personality
            if self.personality.get_trait(PersonalityDimension.OPENNESS) > 0.7:
                kwargs["question_type"] = "open"
            elif self.personality.get_trait(PersonalityDimension.DOMINANCE) > 0.7:
                kwargs["question_type"] = "leading"
            elif self.personality.get_trait(PersonalityDimension.NEUROTICISM) > 0.7:
                kwargs["question_type"] = "closed"
            else:
                kwargs["question_type"] = "open"
                
        elif tool.name == "monologue":
            kwargs["topic"] = stimulus.raw_content or "the situation"
            # Determine monologue style based on personality
            if self.personality.get_trait(PersonalityDimension.EXTRAVERSION) > 0.7:
                kwargs["style"] = "dramatic"
            elif self.personality.get_trait(PersonalityDimension.OPENNESS) > 0.7:
                kwargs["style"] = "philosophical"
            elif self.personality.get_trait(PersonalityDimension.CONSCIENTIOUSNESS) < 0.3:
                kwargs["style"] = "rambling"
            else:
                kwargs["style"] = "neutral"
                
            # Length based on extraversion
            if self.personality.get_trait(PersonalityDimension.EXTRAVERSION) > 0.7:
                kwargs["length"] = "extended"
            elif self.personality.get_trait(PersonalityDimension.EXTRAVERSION) < 0.3:
                kwargs["length"] = "brief"
            else:
                kwargs["length"] = "medium"

        # --- MOVEMENT TOOLS ---
        elif tool.name == "flee":
            kwargs["caution_level"] = 1.0 - self.personality.get_trait(PersonalityDimension.RISK_TOLERANCE)
            
            # Speed based on stress and aggressiveness
            stress = self.personality.get_modifier(PersonalityModifier.STRESS)
            if stress > 0.7:
                kwargs["speed"] = "panicked"
            elif self.personality.get_trait(PersonalityDimension.AGGRESSIVENESS) < 0.3:
                kwargs["speed"] = "fast"
            elif self.personality.get_trait(PersonalityDimension.AGGRESSIVENESS) > 0.7:
                kwargs["speed"] = "slow"  # Aggressive types tend to be more reluctant to flee
            else:
                kwargs["speed"] = "moderate"
                
        elif tool.name == "approach":
            # Manner of approach based on personality
            if self.personality.get_trait(PersonalityDimension.AGGRESSIVENESS) > 0.7:
                kwargs["manner"] = "aggressive"
            elif self.personality.get_trait(PersonalityDimension.AGREEABLENESS) > 0.7:
                kwargs["manner"] = "friendly"
            elif self.personality.get_trait(PersonalityDimension.OPENNESS) < 0.3:
                kwargs["manner"] = "cautious"
            elif self.personality.get_trait(PersonalityDimension.DOMINANCE) < 0.3:
                kwargs["manner"] = "stealthy"
            else:
                kwargs["manner"] = "neutral"
                
        elif tool.name == "hide" or tool.name == "take_cover":
            # No specific personality adjustments needed for these basic actions
            pass
            
        # --- COMBAT TOOLS ---
        elif tool.name == "attack":
            # Attack strength based on aggressiveness and stress
            aggression = self.personality.get_trait(PersonalityDimension.AGGRESSIVENESS)
            stress = self.personality.get_modifier(PersonalityModifier.STRESS)
            kwargs["strength"] = min(1.0, (aggression * 0.7) + (stress * 0.3))
            
        elif tool.name == "defend":
            # Defense style based on personality
            if self.personality.get_trait(PersonalityDimension.AGGRESSIVENESS) > 0.7:
                kwargs["style"] = "aggressive"
            elif self.personality.get_trait(PersonalityDimension.RISK_TOLERANCE) > 0.5:
                kwargs["style"] = "balanced"
            else:
                kwargs["style"] = "cautious"
                
        elif tool.name == "threaten":
            # Threat intensity based on aggressiveness and dominance
            aggression = self.personality.get_trait(PersonalityDimension.AGGRESSIVENESS)
            dominance = self.personality.get_trait(PersonalityDimension.DOMINANCE)
            kwargs["intensity"] = min(1.0, (aggression * 0.6) + (dominance * 0.4))
            
            # Threat type based on personality
            if self.personality.get_trait(PersonalityDimension.DOMINANCE) > 0.7:
                kwargs["threat_type"] = "display_weapon"
            elif self.personality.get_trait(PersonalityDimension.EXTRAVERSION) > 0.7:
                kwargs["threat_type"] = "verbal"
            else:
                kwargs["threat_type"] = "physical"
                
        # --- EMOTIONAL TOOLS ---
        elif tool.name == "express_emotion":
            mood = self.personality.get_modifier(PersonalityModifier.MOOD)
            stress = self.personality.get_modifier(PersonalityModifier.STRESS)
            
            # Determine emotion to express based on mood and stimulus
            if StimulusSchema.THREAT in stimulus.schema or StimulusSchema.VIOLENCE in stimulus.schema:
                kwargs["emotion"] = "fear" if self.personality.get_trait(PersonalityDimension.NEUROTICISM) > 0.5 else "anger"
            elif StimulusSchema.INSULT in stimulus.schema:
                kwargs["emotion"] = "anger" if self.personality.get_trait(PersonalityDimension.NEUROTICISM) > 0.5 else "disgust"
            elif StimulusSchema.PRAISE in stimulus.schema:
                kwargs["emotion"] = "joy"
            elif mood < 0.3:
                kwargs["emotion"] = "sadness"
            elif mood > 0.7:
                kwargs["emotion"] = "joy"
            elif stress > 0.7:
                kwargs["emotion"] = "fear"
            else:
                kwargs["emotion"] = "neutral"
                
            # Intensity based on neuroticism and extraversion
            neuroticism = self.personality.get_trait(PersonalityDimension.NEUROTICISM)
            extraversion = self.personality.get_trait(PersonalityDimension.EXTRAVERSION)
            kwargs["intensity"] = min(1.0, (neuroticism * 0.5) + (extraversion * 0.3) + (stress * 0.2))
            
        elif tool.name == "laugh":
            # Laugh type based on personality and stimulus
            if self.personality.get_trait(PersonalityDimension.NEUROTICISM) > 0.7:
                kwargs["laugh_type"] = "nervous"
            elif self.personality.get_trait(PersonalityDimension.AGREEABLENESS) < 0.3 and (
                StimulusSchema.INSULT in stimulus.schema or stimulus.intent == StimulusIntent.HUMILIATE):
                kwargs["laugh_type"] = "mocking"
            elif self.personality.get_trait(PersonalityDimension.AGREEABLENESS) > 0.7:
                kwargs["laugh_type"] = "polite"
            else:
                kwargs["laugh_type"] = "genuine"
                
        elif tool.name == "cry":
            # Cry type based on stimulus and personality
            if StimulusSchema.VIOLENCE in stimulus.schema:
                kwargs["cry_type"] = "fear"
            elif stimulus.intent == StimulusIntent.HUMILIATE:
                kwargs["cry_type"] = "anger" if self.personality.get_trait(PersonalityDimension.AGGRESSIVENESS) > 0.5 else "sadness"
            else:
                kwargs["cry_type"] = "sadness"
                
            # Intensity based on neuroticism
            kwargs["intensity"] = min(1.0, self.personality.get_trait(PersonalityDimension.NEUROTICISM) * 0.8)
            
        elif tool.name == "panic":
            # How well controlled is the panic based on neuroticism and conscientiousness
            neuroticism = self.personality.get_trait(PersonalityDimension.NEUROTICISM)
            conscientiousness = self.personality.get_trait(PersonalityDimension.CONSCIENTIOUSNESS)
            kwargs["containment"] = max(0.0, (conscientiousness * 0.7) - (neuroticism * 0.3))
            
        # --- SOCIAL TOOLS ---
        elif tool.name == "greet":
            # Formality based on personality
            if self.personality.get_trait(PersonalityDimension.CONSCIENTIOUSNESS) > 0.7:
                kwargs["formality"] = "formal"
            elif self.personality.get_trait(PersonalityDimension.EXTRAVERSION) > 0.7:
                kwargs["formality"] = "warm"
            elif self.personality.get_trait(PersonalityDimension.AGREEABLENESS) < 0.3:
                kwargs["formality"] = "cold"
            elif self.personality.get_trait(PersonalityDimension.EXTRAVERSION) < 0.3:
                kwargs["formality"] = "neutral"
            else:
                kwargs["formality"] = "casual"
                
        elif tool.name == "befriend":
            # Approach based on personality
            if self.personality.get_trait(PersonalityDimension.AGREEABLENESS) > 0.7:
                kwargs["approach"] = "genuine"
            elif self.personality.get_trait(PersonalityDimension.EXTRAVERSION) > 0.7:
                kwargs["approach"] = "enthusiastic"
            elif self.personality.get_trait(PersonalityDimension.OPENNESS) < 0.3:
                kwargs["approach"] = "cautious"
            elif self.personality.get_trait(PersonalityDimension.AGREEABLENESS) < 0.3:
                kwargs["approach"] = "manipulative"
            else:
                kwargs["approach"] = "genuine"
                
        # Default - for any tool not specifically handled, just pass the empty kwargs dict
        return kwargs

    # ------------------------------------------------------------------
    # MOCKS / PLACEHOLDERS
    # ------------------------------------------------------------------
    def _mock_llm_select(self, stimulus: InterpretedStimulus) -> str:
        """Pretend we queried an LLM; returns tool name string."""
        # Get probabilities for all tools
        tool_probs = self._calculate_tool_probabilities(stimulus)
        
        # Get the most likely tool
        if tool_probs:
            highest_prob_tool = max(tool_probs.items(), key=lambda x: x[1])[0]
            return highest_prob_tool
        
        # Fallback to DialogueResponseTool if no other good choices
        return "DialogueResponseTool" 