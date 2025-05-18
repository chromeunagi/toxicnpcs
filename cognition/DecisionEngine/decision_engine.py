from __future__ import annotations

import random
from typing import Any, Dict, Type, Optional, List, Tuple, Set
from collections import defaultdict

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
    PERCEPTION = "perception_tools"
    NEEDS = "needs_tools"

    ALL_CATEGORIES = [
        DIALOGUE, COMBAT, MOVEMENT, SOCIAL, EMOTIONAL, 
        ITEM, ENVIRONMENTAL, PERCEPTION, NEEDS
    ]


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

        selected_tool_class, llm_params = self._select_tool_and_params(stimulus)
        
        tool_instance: Tool = selected_tool_class()
        # If using LLM and LLM provided params, use them. Otherwise, build kwargs heuristically.
        kwargs: Dict[str, Any] = llm_params if self.use_llm and self.decision_client and llm_params is not None else self._build_tool_kwargs(tool_instance, stimulus)
        action_result = tool_instance.execute(**kwargs)
        
        # Record this decision for history/patterns
        self.decision_history.append((selected_tool_class.__name__, action_result))
        
        return action_result

    # ------------------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------------------
    def _organize_tools_by_category(self) -> Dict[str, Dict[str, Type[Tool]]]:
        """Organize available tools by their module/category."""
        result = defaultdict(dict)
        
        for tool_name, tool_class in _TOOL_REGISTRY.items():
            module_name = tool_class.__module__.split('.')[-1]
            result[module_name][tool_name] = tool_class
            
        return result
    
    def _update_modifiers(self, stimulus: InterpretedStimulus) -> None:
        """Update personality modifiers based on the stimulus properties."""
        current_stress = self.personality.get_modifier(PersonalityModifier.STRESS)
        current_mood = self.personality.get_modifier(PersonalityModifier.MOOD)
        stress_change = 0.0
        mood_change = 0.0

        if StimulusSchema.THREAT in stimulus.schema or StimulusSchema.VIOLENCE in stimulus.schema:
            stress_change += 0.2 + (0.3 * stimulus.salience.get(SalienceType.EMOTIONAL, 0))
            mood_change -= 0.15
        if StimulusSchema.INSULT in stimulus.schema or stimulus.intent == StimulusIntent.HUMILIATE:
            stress_change += 0.1 + (0.2 * stimulus.salience.get(SalienceType.EMOTIONAL, 0))
            mood_change -= 0.2
        if StimulusSchema.PRAISE in stimulus.schema or stimulus.intent == StimulusIntent.BUILD_RAPPORT:
            mood_change += 0.15
            stress_change -= 0.05
        if stimulus.actor == "Environment" and StimulusSchema.THREAT in stimulus.schema:
             stress_change += 0.3 # Environmental threats are more stressful

        self.personality.update_modifier(PersonalityModifier.STRESS, max(0.0, min(1.0, current_stress + stress_change)))
        self.personality.update_modifier(PersonalityModifier.MOOD, max(0.0, min(1.0, current_mood + mood_change)))

    def _select_tool_and_params(self, stimulus: InterpretedStimulus) -> Tuple[Type[Tool], Optional[Dict[str, Any]]]:
        """Return the Tool class to handle the stimulus.

        If self.use_llm is True, we will use the DecisionClient to query an LLM.
        Otherwise, we employ personality-influenced heuristics with weighted random choices.
        """
        if self.use_llm and self.decision_client:
            return self._llm_select_tool_and_params(stimulus)
        else:
            tool_probabilities = self._calculate_tool_probabilities_heuristic(stimulus)
            if not tool_probabilities: # Fallback
                print("Warning: No heuristic tools, defaulting to DialogueResponseTool.")
                return get_tool("DialogueResponseTool"), None
            
            tool_names, weights = zip(*tool_probabilities.items())
            selected_tool_name = random.choices(tool_names, weights=weights, k=1)[0]
            return get_tool(selected_tool_name), None
    
    def _llm_select_tool_and_params(self, stimulus: InterpretedStimulus) -> Tuple[Type[Tool], Optional[Dict[str, Any]]]:
        """
        Use the DecisionClient to query an LLM for tool selection.
        """
        # 1. Get heuristically weighted tool suggestions
        heuristic_probabilities = self._calculate_tool_probabilities_heuristic(stimulus)
        
        # Sort tools by probability for the LLM prompt (top N)
        # Making sure to only include tools that are actually in the registry
        sorted_suggestions = sorted(
            [(tool_name, prob) for tool_name, prob in heuristic_probabilities.items() if tool_name in _TOOL_REGISTRY],
            key=lambda item: item[1],
            reverse=True
        )[:10] # Suggest top 10 tools

        # 2. Create context for LLM
        llm_context = self._create_llm_prompt_context(stimulus, sorted_suggestions)
        
        try:
            llm_decision_json = self.decision_client.decide_action(
                interpreted_stimulus=stimulus,
                context=llm_context
            )
            
            action_name = llm_decision_json.get("action", "DialogueResponseTool")
            params = {k: v for k, v in llm_decision_json.items() if k != "action"}
            
            tool_class_name = self._map_action_to_tool(action_name)
            selected_tool_class = get_tool(tool_class_name)
            
            # Further refine LLM params with personality if necessary, or let tool handle it.
            # For now, we assume LLM provides sufficient params, or tool defaults are fine.
            return selected_tool_class, params

        except Exception as e:
            print(f"Error during LLM decision: {e}. Falling back to heuristic.")
            # Fallback to top heuristic choice if LLM fails
            if sorted_suggestions:
                top_tool_name = sorted_suggestions[0][0]
                return get_tool(top_tool_name), None
            else: # Absolute fallback
                print("Critical fallback: Defaulting to DialogueResponseTool due to LLM error and no heuristic suggestions.")
                return get_tool("DialogueResponseTool"), None 
    
    def _create_llm_prompt_context(self, stimulus: InterpretedStimulus, suggestions: List[Tuple[str, float]]) -> Dict[str, Any]:
        context = self._create_personality_context() # Gets basic personality summary
        
        # Add suggested actions based on heuristics
        suggested_actions_formatted = []
        if suggestions:
            context["primary_suggestion"] = f"Consider primarily: {get_tool(suggestions[0][0]).name} ({suggestions[0][1]:.2f} relevance). Description: {get_tool(suggestions[0][0]).description}"
            for i, (tool_name, prob) in enumerate(suggestions):
                tool_class = get_tool(tool_name)
                suggested_actions_formatted.append(
                    f"{i+1}. {tool_class.name} (Relevance: {prob:.2f}): {tool_class.description}"
                )
        else: # Should not happen if heuristic fallback works
            context["primary_suggestion"] = "No specific heuristic suggestions, rely on general context."
        
        context["heuristic_suggestions"] = "\n".join(suggested_actions_formatted) if suggested_actions_formatted else "No specific heuristic suggestions."
        context["available_actions"] = self._get_available_tools_info() # Full list for LLM reference
        return context

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
    
    def _map_action_to_tool(self, action_name_from_llm: str) -> str:
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
        }
        
        # Generic mappings for common categories
        if action_name_from_llm in action_to_tool:
            return action_to_tool[action_name_from_llm]
            
        # Fallback to dialogue response for any other actions
        return "DialogueResponseTool"
    
    def _calculate_tool_probabilities_heuristic(self, stimulus: InterpretedStimulus) -> Dict[str, float]:
        tool_weights = defaultdict(lambda: 0.01) # Start with a tiny base weight for all known tools
        for tool_name in _TOOL_REGISTRY.keys():
            tool_weights[tool_name] = 0.01
        
        category_relevance = self._get_category_relevance(stimulus)
        for category, relevance_score in category_relevance.items():
            if category in self._tools_by_category:
                for tool_name in self._tools_by_category[category]:
                    tool_weights[tool_name] += relevance_score * 0.5 # Boost from category

        self._apply_stimulus_specific_tool_weights(tool_weights, stimulus)
        self._apply_personality_driven_tool_weights(tool_weights, stimulus)
        
        for tool_name in list(tool_weights.keys()):
            tool_weights[tool_name] = self.personality.add_randomness(max(0.001, tool_weights[tool_name]), randomness=0.05)

        positive_weights = {t: w for t, w in tool_weights.items() if w > 0}
        if not positive_weights: # Ensure there's always something to choose
             return {"DialogueResponseTool": 1.0} if "DialogueResponseTool" in _TOOL_REGISTRY else {next(iter(_TOOL_REGISTRY)):1.0} if _TOOL_REGISTRY else {}

        total_weight = sum(positive_weights.values())
        return {t: w / total_weight for t, w in positive_weights.items()}

    def _get_category_relevance(self, stimulus: InterpretedStimulus) -> Dict[str, float]:
        relevance = defaultdict(lambda: 0.05) # Base relevance for all categories
        for cat in ToolCategory.ALL_CATEGORIES: relevance[cat] = 0.05

        # Stimulus Type
        type_boosts = {
            StimulusType.DIALOGUE: {ToolCategory.DIALOGUE: 0.6, ToolCategory.SOCIAL: 0.3, ToolCategory.EMOTIONAL: 0.2},
            StimulusType.GESTURE: {ToolCategory.MOVEMENT: 0.3, ToolCategory.SOCIAL: 0.4, ToolCategory.EMOTIONAL: 0.2, ToolCategory.PERCEPTION: 0.1},
            StimulusType.PHYSICAL_CONTACT: {ToolCategory.COMBAT: 0.6, ToolCategory.MOVEMENT: 0.3, ToolCategory.EMOTIONAL: 0.2},
            StimulusType.ENVIRONMENT: {ToolCategory.ENVIRONMENTAL: 0.5, ToolCategory.MOVEMENT: 0.2, ToolCategory.PERCEPTION: 0.3, ToolCategory.NEEDS: 0.2},
            StimulusType.OBJECT_INTERACTION: {ToolCategory.ITEM: 0.6, ToolCategory.ENVIRONMENTAL: 0.2, ToolCategory.PERCEPTION: 0.2},
            StimulusType.ACTION: {ToolCategory.COMBAT: 0.3, ToolCategory.MOVEMENT: 0.4, ToolCategory.ITEM: 0.2}
        }
        if stimulus.stimulus_type in type_boosts:
            for cat, boost in type_boosts[stimulus.stimulus_type].items(): relevance[cat] += boost

        # Schema based boosts
        if StimulusSchema.THREAT in stimulus.schema or StimulusSchema.VIOLENCE in stimulus.schema:
            relevance[ToolCategory.COMBAT] += 0.3; relevance[ToolCategory.MOVEMENT] += 0.2; relevance[ToolCategory.PERCEPTION] += 0.1
        if StimulusSchema.REQUEST in stimulus.schema or stimulus.intent == StimulusIntent.SEEK_HELP:
             relevance[ToolCategory.SOCIAL] += 0.3; relevance[ToolCategory.DIALOGUE] += 0.2
        if StimulusSchema.PRAISE in stimulus.schema or StimulusSchema.FLIRTATION in stimulus.schema or stimulus.intent == StimulusIntent.BUILD_RAPPORT:
             relevance[ToolCategory.SOCIAL] += 0.4; relevance[ToolCategory.EMOTIONAL] += 0.2; relevance[ToolCategory.DIALOGUE] += 0.2
        if StimulusSchema.INSULT in stimulus.schema or stimulus.intent == StimulusIntent.HUMILIATE:
             relevance[ToolCategory.EMOTIONAL] += 0.3; relevance[ToolCategory.COMBAT] += 0.1; relevance[ToolCategory.DIALOGUE] += 0.1
        
        total_relevance = sum(relevance.values()) or 1.0
        return {cat: score / total_relevance for cat, score in relevance.items()}

    def _apply_stimulus_specific_tool_weights(self, tool_weights: Dict[str, float], stimulus: InterpretedStimulus) -> None:
        # More targeted adjustments based on specific combinations
        if StimulusSchema.THREAT in stimulus.schema:
            self._adjust_tool_probability_group(tool_weights, ["FleeTool", "HideTool", "ScanForThreatsTool", "DefendTool"], 0.15)
            if stimulus.salience.get(SalienceType.EMOTIONAL, 0) > 0.7:
                 self._adjust_tool_probability_group(tool_weights, ["PanicTool", "ExpressEmotionTool"], 0.1)
        if stimulus.stimulus_type == StimulusType.DIALOGUE and stimulus.intent == StimulusIntent.HUMILIATE:
            self._adjust_tool_probability_group(tool_weights, ["DialogueResponseTool", "TauntTool", "RetreatTool"], 0.1)

    def _apply_personality_driven_tool_weights(self, tool_weights: Dict[str, float], stimulus: InterpretedStimulus) -> None:
        p = self.personality
        # Trait influences (example, scale: -0.2 to 0.2 based on trait deviation from 0.5)
        trait_influences = {
            PersonalityDimension.AGGRESSIVENESS: (["AttackTool", "ThreatenTool", "TauntTool"], ["FleeTool", "ApologizeTool", "OfferHelpTool"]),
            PersonalityDimension.EXTRAVERSION: (["DialogueResponseTool", "GreetTool", "BefriendTool", "MonologueTool"], ["HideTool", "EavesdropTool", "ListenTool"]),
            PersonalityDimension.NEUROTICISM: (["PanicTool", "CryTool", "ExpressEmotionTool", "FleeTool"], ["PersuadeTool", "AssessIntentTool"]),
            PersonalityDimension.OPENNESS: (["SearchAreaTool", "ExamineItemTool", "AskQuestionTool", "IdentifyObjectTool"], ["TakeCoverTool", "RestTool"]),
            PersonalityDimension.CONSCIENTIOUSNESS: (["SetTrapTool", "CraftItemTool", "DefendTool"], ["CreateDistraction", "DeceiveTool"]),
            PersonalityDimension.AGREEABLENESS: (["OfferHelpTool", "ApologizeTool", "PersuadeTool"], ["TauntTool", "ThreatenTool", "DeceiveTool"]),
            PersonalityDimension.RISK_TOLERANCE: (["AttackTool", "TakeItemTool"], ["FleeTool", "HideTool", "DefendTool"])
        }
        for dim, (pos_tools, neg_tools) in trait_influences.items():
            trait_val = p.get_trait(dim)
            self._adjust_tool_probability_group(tool_weights, pos_tools, 0.25 * (trait_val - 0.5))
            self._adjust_tool_probability_group(tool_weights, neg_tools, -0.25 * (trait_val - 0.5))

        # Modifier influences
        stress = p.get_modifier(PersonalityModifier.STRESS)
        mood = p.get_modifier(PersonalityModifier.MOOD)
        if stress > 0.6:
            self._adjust_tool_probability_group(tool_weights, ["PanicTool", "FleeTool", "AttackTool", "ExpressEmotionTool"], 0.15 * stress)
            self._adjust_tool_probability_group(tool_weights, ["CraftItemTool", "RestTool", "BefriendTool"], -0.1 * stress)
        if mood < 0.4:
            self._adjust_tool_probability_group(tool_weights, ["ExpressEmotionTool", "TauntTool", "MonologueTool"], 0.15 * (1-mood))
        if mood > 0.6:
            self._adjust_tool_probability_group(tool_weights, ["LaughTool", "GreetTool", "OfferHelpTool", "DialogueResponseTool"], 0.1 * mood)
        
        # Quirk influences (simplified examples)
        for quirk in p.quirks:
            if quirk == "Always looking over shoulder": self._adjust_tool_probability_group(tool_weights, ["ScanForThreatsTool", "ListenTool"], 0.05)
            if quirk == "Cannot resist a challenge" and StimulusSchema.DOMINANCE_ASSERTION in stimulus.schema : self._adjust_tool_probability_group(tool_weights, ["AttackTool", "TauntTool"], 0.1)
            if quirk == "Avoids eye contact" and stimulus.stimulus_type == StimulusType.DIALOGUE: self._adjust_tool_probability_group(tool_weights, ["MonologueTool"], 0.05) # Less direct interaction

    def _adjust_tool_probability_group(self, tool_weights: Dict[str, float], tool_names: List[str], adjustment_factor: float) -> None:
        present_tools = [name for name in tool_names if name in _TOOL_REGISTRY]
        if not present_tools: return
        
        for tool_name in present_tools:
            # Initialize if not present from category relevance (should not happen with defaultdict(lambda: 0.01) approach)
            # tool_weights[tool_name] = tool_weights.get(tool_name, 0.01) 
            tool_weights[tool_name] += adjustment_factor 
            tool_weights[tool_name] = max(0.001, tool_weights[tool_name]) # Ensure a floor, prevent negative or zero before normalization

    # ------------------------------------------------------------------
    # MOCKS / PLACEHOLDERS
    # ------------------------------------------------------------------
    def _mock_llm_select(self, stimulus: InterpretedStimulus) -> str:
        """Pretend we queried an LLM; returns tool name string."""
        # Get probabilities for all tools
        tool_probs = self._calculate_tool_probabilities_heuristic(stimulus)
        
        # Get the most likely tool
        if tool_probs:
            highest_prob_tool = max(tool_probs.items(), key=lambda x: x[1])[0]
            return highest_prob_tool
        
        # Fallback to DialogueResponseTool if no other good choices
        return "DialogueResponseTool" 

    def _build_tool_kwargs(self, tool: Tool, stimulus: InterpretedStimulus) -> Dict[str, Any]:
        """Build kwargs for a tool in heuristic mode or as fallback for LLM mode."""
        kwargs: Dict[str, Any] = {}
        p = self.personality
        # Provide comprehensive context for the tool to use if it needs it.
        kwargs["personality_context"] = self._create_personality_context() 
        kwargs["stimulus_raw_content"] = stimulus.raw_content
        kwargs["stimulus_actor"] = stimulus.actor
        kwargs["stimulus_type"] = stimulus.stimulus_type.name
        kwargs["stimulus_schema"] = [s.name for s in stimulus.schema]
        kwargs["stimulus_intent"] = stimulus.intent.name if stimulus.intent else None
        kwargs["stimulus_salience"] = {s.name: v for s,v in stimulus.salience.items()}

        # Personality-driven parameterization for heuristic mode
        agg = p.get_trait(PersonalityDimension.AGGRESSIVENESS)
        ext = p.get_trait(PersonalityDimension.EXTRAVERSION)
        neu = p.get_trait(PersonalityDimension.NEUROTICISM)
        opn = p.get_trait(PersonalityDimension.OPENNESS)
        con = p.get_trait(PersonalityDimension.CONSCIENTIOUSNESS)
        agr = p.get_trait(PersonalityDimension.AGREEABLENESS)
        rsk = p.get_trait(PersonalityDimension.RISK_TOLERANCE)
        mood = p.get_modifier(PersonalityModifier.MOOD)
        stress = p.get_modifier(PersonalityModifier.STRESS)

        # --- Example: Tailoring specific tool parameters ---
        if tool.name == "attack":
            kwargs["strength"] = max(0.1, agg * 0.7 + stress * 0.3 - neu * 0.1)
            kwargs["attack_type"] = "power_attack" if agg > 0.75 and rsk > 0.6 else "quick_attack" if agg > 0.6 else "standard"
            # weapon_used would typically come from NPC inventory/state
        elif tool.name == "dialogue_response":
            kwargs["prompt"] = stimulus.raw_content
            if agg > 0.7 and mood < 0.3: kwargs["tone"] = "hostile"
            elif agr > 0.7 and mood > 0.65: kwargs["tone"] = "friendly"
            elif neu > 0.65 and stress > 0.6: kwargs["tone"] = "defensive"
            elif ext < 0.35: kwargs["tone"] = "neutral"
            elif neu > 0.7 and agr < 0.3: kwargs["tone"] = "sarcastic"
            else: kwargs["tone"] = "casual"
            
            # Determine dialogue_act
            if opn > 0.7 and agr > 0.6 : kwargs["dialogue_act"] = "explanation"
            elif ext > 0.7 and agr < 0.4 and mood < 0.4: kwargs["dialogue_act"] = "insult" 
            elif con > 0.7 and agr > 0.5 : kwargs["dialogue_act"] = "persuasion"
            else: kwargs["dialogue_act"] = "statement"

        elif tool.name == "flee":
            kwargs["speed"] = "panicked" if stress > 0.85 or neu > 0.85 else "fast" if rsk < 0.25 else "moderate"
            kwargs["caution_level"] = max(0.1, min(0.9, (1.0 - rsk) - (stress * 0.4) + (con * 0.2)))
            kwargs["reason"] = "imminent danger" if StimulusSchema.THREAT in stimulus.schema else "overwhelming stress"
        elif tool.name == "defend":
            kwargs["style"] = "aggressive" if agg > 0.75 else "cautious" if rsk < 0.35 or con > 0.75 else "block" if con > 0.5 else "balanced"
            kwargs["duration"] = "sustained" if con > 0.65 or stress > 0.5 else "momentarily"
        elif tool.name == "express_emotion":
            if stress > 0.8 and neu > 0.75: kwargs["emotion"] = "fear"; kwargs["intensity"] = (stress + neu) / 2
            elif mood < 0.25 : kwargs["emotion"] = "sadness"; kwargs["intensity"] = max(0.3, 1 - mood)
            elif agg > 0.75 and (StimulusSchema.INSULT in stimulus.schema or mood < 0.35): kwargs["emotion"] = "anger"; kwargs["intensity"] = agg
            elif mood > 0.75 : kwargs["emotion"] = "joy"; kwargs["intensity"] = mood
            else: kwargs["emotion"] = "neutral"; kwargs["intensity"] = 0.5
        elif tool.name == "greet":
            if con > 0.7: kwargs["formality"] = "formal"
            elif ext > 0.7 and agr > 0.6: kwargs["formality"] = "warm"
            elif agr < 0.3 or mood < 0.3: kwargs["formality"] = "cold"
            else: kwargs["formality"] = "neutral"
        elif tool.name == "scan_for_threats":
            kwargs["thoroughness"] = max(0.2, con * 0.6 + neu * 0.3 + stress * 0.3)
        # Add more tool-specific kwarg builders here...
        return kwargs 