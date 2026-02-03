"""
Orchestrator Agent - Coordinates multiple agents and workflow management
"""
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import logging

class OrchestratorAgent:
    """
    Primary Responsibilities:
    - Coordinate multiple agents and workflow management
    - Manage inter-agent communication 
    - Control analysis pipeline execution
    - Aggregate results from multiple agents
    - Guide strategic interview decisions
    - Initiate interviews and manage conversational flow
    """
    
    def __init__(self, llm_client=None, groq_api_key: str = None):
        """
        Initialize the orchestrator agent with references to all sub-agents
        """
        self.client = llm_client
        self.groq_api_key = groq_api_key
        
        # Central state management
        self.current_interview_state = {
            "active_person": None,
            "active_goal": None,
            "current_strategy": None,
            "interview_stage": "preparation",  # preparation, active, summary, complete
            "problematic_areas": [],
            "user_choices": [],
            "conversation_context": {}
        }
        
        # Agent references (will be injected by interface)
        self.interface_agent = None
        self.summarization_agent = None
        self.causality_agent = None
        self.milestone_refinement_agent = None
        self.gap_filler_agent = None
        
        # Communication logs for debugging and analysis
        self.communication_log = []
        
        logging.info("OrchestratorAgent initialized")
    
    def inject_agents(self, agents: Dict[str, Any]):
        """
        Inject references to other agents for coordination
        """
        self.interface_agent = agents.get('interface_agent')
        self.summarization_agent = agents.get('summarization_agent')
        self.causality_agent = agents.get('causality_agent')
        self.milestone_refinement_agent = agents.get('milestone_refinement_agent')
        self.gap_filler_agent = agents.get('gap_filler_agent')
        
        logging.info(f"Orchestrator injected with {len(agents)} agents")
    
    def initiate_interview(self, person: str, goal_id: str, goal_title: str, 
                          draft_roadmap: Dict, tracker) -> Dict:
        """
        CORE RESPONSIBILITY: Initiating the Interview (00:22:55 - 00:23:12)
        - Takes draft roadmap as starting input
        - Passes roadmap to Interface Agent for visualization
        - Composes and delivers opening prompt to user
        """
        try:
            self.current_interview_state.update({
                "active_person": person,
                "active_goal": goal_id,
                "interview_stage": "active",
                "start_time": datetime.now()
            })
            
            # Step 1: Pass draft roadmap to Interface Agent for visualization
            if self.interface_agent:
                visualization_result = self._delegate_to_interface_agent(
                    "visualize_roadmap", 
                    {"roadmap": draft_roadmap, "person": person, "goal_id": goal_id}
                )
                self._log_communication("interface_agent", "visualize_roadmap", visualization_result)
            
            # Step 2: Compose opening prompt for user
            opening_prompt = self._compose_opening_prompt(goal_title, draft_roadmap)
            
            # Step 3: Initialize interview session state
            interview_session = {
                "session_id": f"interview_{person}_{goal_id}_{int(datetime.now().timestamp())}",
                "opening_prompt": opening_prompt,
                "roadmap_visualization": True,
                "awaiting_initial_feedback": True,
                "strategic_options_prepared": False
            }
            
            return {
                "success": True,
                "session": interview_session,
                "opening_prompt": opening_prompt,
                "next_action": "await_user_feedback"
            }
            
        except Exception as e:
            logging.error(f"Failed to initiate interview: {e}")
            return {"success": False, "error": str(e)}
    
    def receive_and_interpret_initial_feedback(self, thumbs_scores: Dict, 
                                             vote_summary: Dict, tracker) -> Dict:
        """
        CORE RESPONSIBILITY: Receiving and Interpreting Initial Feedback (00:24:02)
        - Receives scores from Interface Agent
        - Processes problematic areas
        - Prepares strategic decision options
        """
        try:
            # Process the feedback scores
            problematic_areas = self._identify_problematic_areas(thumbs_scores, vote_summary)
            
            # Update orchestrator state
            self.current_interview_state.update({
                "problematic_areas": problematic_areas,
                "feedback_received": True,
                "scores_summary": thumbs_scores
            })
            
            # Log the feedback processing
            self._log_communication("interface_agent", "feedback_received", {
                "scores": thumbs_scores,
                "problematic_areas": len(problematic_areas)
            })
            
            # Prepare strategic options for user
            strategic_options = self._prepare_strategic_options(problematic_areas)
            
            return {
                "success": True,
                "problematic_areas": problematic_areas,
                "strategic_options": strategic_options,
                "next_action": "present_strategic_choices"
            }
            
        except Exception as e:
            logging.error(f"Failed to process initial feedback: {e}")
            return {"success": False, "error": str(e)}
    
    def make_core_strategic_decision(self, problematic_areas: List[Dict], 
                                   user_preference: str = None) -> Dict:
        """
        CORE RESPONSIBILITY: Making the Core Strategic Decision (00:24:09 - 00:26:08)
        - Core "if-else" logic based on scores
        - Presents strategic choices to user
        - Offers Option A (Targeted) vs Option B (Holistic)
        """
        try:
            strategic_decision = {
                "decision_timestamp": datetime.now(),
                "problematic_areas_count": len(problematic_areas),
                "recommended_approach": None,
                "options_presented": [],
                "user_choice": user_preference
            }
            
            # Core decision logic based on problematic areas
            if len(problematic_areas) == 0:
                # No major issues - suggest refinement approach
                strategic_decision["recommended_approach"] = "refinement"
                strategic_decision["options_presented"] = [
                    {
                        "id": "refinement",
                        "title": "Refinement Approach",
                        "description": "Your roadmap looks solid! Let's refine specific details and ensure nothing is missing."
                    }
                ]
            
            elif len(problematic_areas) <= 2:
                # Few problematic areas - offer targeted approach
                strategic_decision["recommended_approach"] = "targeted"
                strategic_decision["options_presented"] = [
                    {
                        "id": "targeted",
                        "title": "Targeted Approach (Recommended)",
                        "description": f"Focus our discussion on the {len(problematic_areas)} specific area(s) you're unhappy with."
                    },
                    {
                        "id": "holistic", 
                        "title": "Holistic Review",
                        "description": "Review the entire roadmap from the beginning to check its structure and logic."
                    }
                ]
            
            else:
                # Many problematic areas - recommend holistic approach
                strategic_decision["recommended_approach"] = "holistic"
                strategic_decision["options_presented"] = [
                    {
                        "id": "holistic",
                        "title": "Holistic Review (Recommended)", 
                        "description": "Review the entire roadmap from the beginning to check its structure and logic."
                    },
                    {
                        "id": "targeted",
                        "title": "Focus on Worst Areas",
                        "description": f"Focus only on the most problematic areas ({len(problematic_areas)} areas identified)."
                    }
                ]
            
            # Update orchestrator state
            self.current_interview_state.update({
                "strategic_decision": strategic_decision,
                "awaiting_user_choice": True
            })
            
            return strategic_decision
            
        except Exception as e:
            logging.error(f"Strategic decision making failed: {e}")
            return {"error": str(e)}
    
    def delegate_to_specialized_agents(self, user_choice: str, context: Dict, tracker) -> Dict:
        """
        CORE RESPONSIBILITY: Delegating Tasks to Specialized Agents (00:26:08 - 00:26:21)
        - Based on user choice, activates appropriate specialized agent
        - Holistic -> Structural Causality Agent
        - Targeted -> Milestone Refinement Agent (scoped to specific region)
        """
        try:
            delegation_result = {
                "user_choice": user_choice,
                "delegated_agent": None,
                "delegation_scope": {},
                "success": False
            }
            
            if user_choice == "holistic":
                # Delegate to Structural Causality Agent for systematic verification
                if self.causality_agent:
                    scope = {
                        "verification_type": "systematic_full_roadmap",
                        "person": context.get("person"),
                        "goal_id": context.get("goal_id"),
                        "milestones": context.get("milestones", {}),
                        "step_by_step": True
                    }
                    
                    causality_result = self._delegate_to_causality_agent(
                        "systematic_roadmap_verification", scope
                    )
                    
                    delegation_result.update({
                        "delegated_agent": "causality_agent",
                        "delegation_scope": scope,
                        "agent_result": causality_result,
                        "success": True
                    })
                    
                    self._log_communication("causality_agent", "systematic_verification", causality_result)
            
            elif user_choice == "targeted":
                # Delegate to Milestone Refinement Agent with limited scope
                problematic_areas = self.current_interview_state.get("problematic_areas", [])
                
                if self.milestone_refinement_agent:
                    scope = {
                        "refinement_type": "targeted_problematic_areas",
                        "problematic_areas": problematic_areas,
                        "person": context.get("person"),
                        "goal_id": context.get("goal_id"),
                        "focus_regions": [area["region"] for area in problematic_areas]
                    }
                    
                    refinement_result = self._delegate_to_milestone_refinement_agent(
                        "targeted_area_refinement", scope
                    )
                    
                    delegation_result.update({
                        "delegated_agent": "milestone_refinement_agent", 
                        "delegation_scope": scope,
                        "agent_result": refinement_result,
                        "success": True
                    })
                    
                    self._log_communication("milestone_refinement_agent", "targeted_refinement", refinement_result)
            
            elif user_choice == "refinement":
                # Delegate to Gap Filler Agent for detailed refinement
                if self.gap_filler_agent:
                    scope = {
                        "analysis_type": "comprehensive_gap_analysis",
                        "person": context.get("person"),
                        "goal_id": context.get("goal_id"),
                        "conversation": context.get("conversation", [])
                    }
                    
                    gap_result = self._delegate_to_gap_filler_agent(
                        "comprehensive_analysis", scope
                    )
                    
                    delegation_result.update({
                        "delegated_agent": "gap_filler_agent",
                        "delegation_scope": scope, 
                        "agent_result": gap_result,
                        "success": True
                    })
                    
                    self._log_communication("gap_filler_agent", "comprehensive_analysis", gap_result)
            
            # Update orchestrator state
            self.current_interview_state.update({
                "active_delegation": delegation_result,
                "current_strategy": user_choice
            })
            
            return delegation_result
            
        except Exception as e:
            logging.error(f"Agent delegation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def manage_conversational_context(self, session_messages: List[Dict], 
                                    goal_title: str, tracker) -> Dict:
        """
        CORE RESPONSIBILITY: Managing Conversational Context and Health (00:35:48)
        - Maintains clarity throughout interview
        - Calls Summarization Agent periodically
        - Pushes user to reflect on incorporated progress
        """
        try:
            context_management = {
                "message_count": len(session_messages),
                "summary_triggered": False,
                "clarity_check": False,
                "reflection_prompt": None
            }
            
            # Check if we need to trigger summarization (every 10 messages or major milestone)
            should_summarize = (
                len(session_messages) % 10 == 0 or 
                self._detect_major_milestone_in_conversation(session_messages)
            )
            
            if should_summarize and self.summarization_agent:
                # Call Summarization Agent
                summary_result = self._delegate_to_summarization_agent(
                    "generate_progress_summary",
                    {
                        "conversation": session_messages,
                        "goal_title": goal_title,
                        "current_state": self.current_interview_state
                    }
                )
                
                context_management.update({
                    "summary_triggered": True,
                    "summary_content": summary_result,
                    "clarity_check": True
                })
                
                # Generate reflection prompt to push user to reflect
                reflection_prompt = self._generate_reflection_prompt(summary_result, goal_title)
                context_management["reflection_prompt"] = reflection_prompt
                
                self._log_communication("summarization_agent", "progress_summary", summary_result)
            
            # Update conversation context in state
            self.current_interview_state["conversation_context"] = {
                "last_summary_at": len(session_messages) if should_summarize else 
                                  self.current_interview_state.get("conversation_context", {}).get("last_summary_at", 0),
                "clarity_maintained": True,
                "reflection_points": context_management.get("reflection_prompt")
            }
            
            return context_management
            
        except Exception as e:
            logging.error(f"Conversational context management failed: {e}")
            return {"error": str(e)}
    
    def coordinate_multi_agent_analysis(self, analysis_type: str, context: Dict, tracker) -> Dict:
        """
        Coordinate complex multi-agent analysis workflows
        """
        print(f"DEBUG: coordinate_multi_agent_analysis called with type: {analysis_type}")
        
        try:
            coordination_result = {
                "analysis_type": analysis_type,
                "agents_involved": [],
                "results": {},
                "aggregated_insights": {},
                "success": False
            }
            
            print(f"DEBUG: Available agents - causality: {self.causality_agent is not None}, gap_filler: {self.gap_filler_agent is not None}, summarization: {self.summarization_agent is not None}")
            
            if analysis_type == "comprehensive_roadmap_analysis":
                # Coordinate between causality, gap filler, and summarization agents
                
                # Step 1: Causality analysis
                if self.causality_agent:
                    print("DEBUG: Running causality analysis")
                    causality_result = self._delegate_to_causality_agent(
                        "analyze_causal_structure", context
                    )
                    print(f"DEBUG: Causality result: {causality_result}")
                    coordination_result["results"]["causality"] = causality_result
                    coordination_result["agents_involved"].append("causality_agent")
                else:
                    print("DEBUG: Causality agent not available")
                
                # Step 2: Gap analysis
                if self.gap_filler_agent:
                    print("DEBUG: Running gap analysis")
                    gap_result = self._delegate_to_gap_filler_agent(
                        "comprehensive_analysis", context
                    )
                    print(f"DEBUG: Gap result: {gap_result}")
                    coordination_result["results"]["gaps"] = gap_result
                    coordination_result["agents_involved"].append("gap_filler_agent")
                else:
                    print("DEBUG: Gap filler agent not available")
                
                # Step 3: Synthesize results with summarization agent
                if self.summarization_agent:
                    print("DEBUG: Running summarization")
                    synthesis_context = {
                        "causality_analysis": coordination_result["results"].get("causality"),
                        "gap_analysis": coordination_result["results"].get("gaps"),
                        "goal_title": context.get("goal_title", "")
                    }
                    
                    summary_result = self._delegate_to_summarization_agent(
                        "synthesize_multi_agent_analysis", synthesis_context
                    )
                    print(f"DEBUG: Summary result: {summary_result}")
                    coordination_result["results"]["synthesis"] = summary_result
                    coordination_result["agents_involved"].append("summarization_agent")
                else:
                    print("DEBUG: Summarization agent not available")
                
                # Step 4: Aggregate insights
                print("DEBUG: Aggregating insights")
                coordination_result["aggregated_insights"] = self._aggregate_multi_agent_insights(
                    coordination_result["results"]
                )
                print(f"DEBUG: Aggregated insights: {coordination_result['aggregated_insights']}")
                
                # Ensure we have some meaningful results even if agents fail
                if not coordination_result["agents_involved"]:
                    print("DEBUG: No agents successfully involved, creating fallback result")
                    coordination_result["aggregated_insights"] = {
                        "key_insights": ["Multi-agent analysis attempted - check agent availability"],
                        "action_items": ["Verify agent initialization", "Check API keys", "Review agent delegation methods"],
                        "confidence_score": 0.1,
                        "priority_areas": ["Agent Setup"]
                    }
                    coordination_result["agents_involved"] = ["fallback"]
                
                coordination_result["success"] = True
                print("DEBUG: Multi-agent analysis completed successfully")
            
            print(f"DEBUG: Final coordination result: {coordination_result}")
            return coordination_result
            
        except Exception as e:
            print(f"DEBUG: Exception in coordinate_multi_agent_analysis: {e}")
            import traceback
            traceback.print_exc()
            logging.error(f"Multi-agent coordination failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_orchestrator_status(self) -> Dict:
        """
        Get current status of orchestrator and managed workflow
        """
        return {
            "current_state": self.current_interview_state,
            "communication_log_size": len(self.communication_log),
            "active_agents": [
                agent_name for agent_name in ["interface_agent", "summarization_agent", 
                                            "causality_agent", "milestone_refinement_agent", 
                                            "gap_filler_agent"]
                if getattr(self, agent_name) is not None
            ],
            "last_communication": self.communication_log[-1] if self.communication_log else None,
            "interview_stage": self.current_interview_state.get("interview_stage"),
            "current_strategy": self.current_interview_state.get("current_strategy")
        }
    
    # Internal helper methods
    
    def _compose_opening_prompt(self, goal_title: str, draft_roadmap: Dict) -> str:
        """Compose the opening prompt for the user"""
        milestone_count = len(draft_roadmap.get("milestones", {}))
        
        return f"""🎯 **Welcome to your {goal_title} roadmap review!**

I've analyzed your background and created this draft roadmap with {milestone_count} key milestones. 

**Here's what we think your path looks like.**

Please review the milestones below and use the 👍/👎 buttons to indicate:
- 👍 = This milestone is correct and important
- 👎 = This milestone is wrong or unimportant

Once you've voted on a few milestones, I'll help you decide our next steps based on your feedback.

**Ready to begin?** Start voting on the milestones you see!"""
    
    def _identify_problematic_areas(self, thumbs_scores: Dict, vote_summary: Dict) -> List[Dict]:
        """Identify problematic areas from user feedback"""
        problematic_areas = []
        
        # Analyze vote summary for problematic patterns
        for milestone_id, vote_data in vote_summary.items():
            vote_score = vote_data.get("score", 0)
            negative_votes = vote_data.get("negative", 0)
            
            if vote_score < 50 or negative_votes > 0:  # Less than 50% positive or any negative votes
                problematic_areas.append({
                    "type": "milestone",
                    "milestone_id": milestone_id,
                    "issue": "low_confidence" if vote_score < 50 else "negative_feedback",
                    "score": vote_score,
                    "region": f"milestone_{milestone_id}"
                })
        
        # Analyze broader patterns
        if len(problematic_areas) > len(vote_summary) * 0.3:  # More than 30% problematic
            problematic_areas.append({
                "type": "systemic",
                "issue": "widespread_concerns",
                "affected_count": len(problematic_areas),
                "region": "entire_roadmap"
            })
        
        return problematic_areas
    
    def _prepare_strategic_options(self, problematic_areas: List[Dict]) -> List[Dict]:
        """Prepare strategic options based on identified issues"""
        options = []
        
        if len(problematic_areas) <= 2:
            options.append({
                "id": "targeted",
                "title": "🎯 Targeted Approach", 
                "description": f"Let's focus our discussion on the {len(problematic_areas)} specific areas you're unhappy with.",
                "icon": "🎯",
                "recommended": True
            })
            
            options.append({
                "id": "holistic",
                "title": "🔍 Complete Review",
                "description": "Review the entire roadmap from the beginning to check its structure and logic.",
                "icon": "🔍"
            })
        else:
            options.append({
                "id": "holistic", 
                "title": "🔍 Complete Review",
                "description": "Review the entire roadmap from the beginning to check its structure and logic.",
                "icon": "🔍",
                "recommended": True
            })
            
            options.append({
                "id": "targeted",
                "title": "🎯 Focus on Worst Areas", 
                "description": f"Address only the most problematic areas ({len(problematic_areas)} areas identified).",
                "icon": "🎯"
            })
        
        return options
    
    def _detect_major_milestone_in_conversation(self, messages: List[Dict]) -> bool:
        """Detect if a major milestone occurred in recent conversation"""
        recent_messages = messages[-3:] if len(messages) >= 3 else messages
        
        milestone_indicators = [
            "milestone added", "milestone removed", "connection changed",
            "major insight", "breakthrough", "important realization"
        ]
        
        for message in recent_messages:
            content = message.get("content", "").lower()
            if any(indicator in content for indicator in milestone_indicators):
                return True
        
        return False
    
    def _generate_reflection_prompt(self, summary_result: Dict, goal_title: str) -> str:
        """Generate reflection prompt to push user to think about progress"""
        summary_text = summary_result.get("summary", "")
        
        return f"""
        
📝 **Let's pause and reflect on our progress:**

{summary_text}

**Key Question:** Based on what we've discussed so far, what aspects of your {goal_title} journey are becoming clearer to you? 

Are there any new insights about your path that we should incorporate into your roadmap?
        """
    
    def _aggregate_multi_agent_insights(self, results: Dict) -> Dict:
        """Aggregate insights from multiple agent results"""
        aggregated = {
            "key_insights": [],
            "action_items": [],
            "confidence_score": 0.0,
            "priority_areas": []
        }
        
        # Extract insights from causality analysis
        causality = results.get("causality", {})
        if causality.get("confidence_score"):
            aggregated["confidence_score"] += causality["confidence_score"] * 0.4
        
        if causality.get("recommendations"):
            aggregated["action_items"].extend(causality["recommendations"][:3])
        
        # Extract insights from gap analysis  
        gaps = results.get("gaps", {})
        if gaps.get("suggested_milestones"):
            aggregated["key_insights"].append(
                f"Identified {len(gaps['suggested_milestones'])} potential milestone gaps"
            )
        
        # Extract insights from synthesis
        synthesis = results.get("synthesis", {})
        if synthesis.get("summary"):
            aggregated["key_insights"].append("Comprehensive analysis completed")
        
        return aggregated
    
    # Agent delegation methods
    
    def _delegate_to_interface_agent(self, method: str, params: Dict) -> Dict:
        """Delegate task to interface agent"""
        if not self.interface_agent:
            return {"error": "Interface agent not available"}
        
        try:
            if method == "visualize_roadmap":
                # Interface agent handles roadmap visualization
                return {"success": True, "method": method, "params": params}
            
            return {"success": True, "delegated": True}
        except Exception as e:
            return {"error": str(e)}
    
    def _delegate_to_summarization_agent(self, method: str, params: Dict) -> Dict:
        """Delegate task to summarization agent"""
        if not self.summarization_agent:
            return {"error": "Summarization agent not available"}
        
        try:
            if method == "generate_progress_summary":
                summary = self.summarization_agent.generate_conversation_summary(
                    params.get("conversation", []),
                    params.get("goal_title", ""),
                    "focused"
                )
                return {"success": True, "summary": summary}
            
            elif method == "synthesize_multi_agent_analysis":
                # Create comprehensive synthesis
                synthesis_prompt = f"""
                Synthesize these analysis results:
                
                Causality Analysis: {params.get('causality_analysis', {})}
                Gap Analysis: {params.get('gap_analysis', {})}
                Goal: {params.get('goal_title', '')}
                
                Provide key insights and recommendations.
                """
                
                return {"success": True, "synthesis": synthesis_prompt}
            
            return {"success": True, "delegated": True}
        except Exception as e:
            return {"error": str(e)}
    
    def _delegate_to_causality_agent(self, method: str, params: Dict) -> Dict:
        """Delegate task to causality agent"""
        if not self.causality_agent:
            return {"error": "Causality agent not available"}
        
        try:
            if method == "systematic_roadmap_verification":
                # Call causality agent's comprehensive analysis method
                milestones = list(params.get("milestones", {}).values())
                result = self.causality_agent.run_comprehensive_analysis(
                    milestones,
                    params.get("goal_title", ""),
                    params.get("person", ""),
                    analysis_types=["cofounders", "counterfactuals", "interventions"]
                )
                return {"success": True, "verification_result": result}
            
            elif method == "analyze_causal_structure":
                # Use run_comprehensive_analysis for causal structure analysis
                milestones = list(params.get("milestones", {}).values())
                result = self.causality_agent.run_comprehensive_analysis(
                    milestones,
                    params.get("goal_title", ""),
                    params.get("person", ""),
                    analysis_types=["cofounders", "counterfactuals"]
                )
                return {"success": True, "analysis_result": result}
            
            return {"success": True, "delegated": True}
        except Exception as e:
            import traceback
            print(f"DEBUG: Causality agent delegation error: {e}")
            traceback.print_exc()
            return {"error": str(e)}
    
    def _delegate_to_milestone_refinement_agent(self, method: str, params: Dict) -> Dict:
        """Delegate task to milestone refinement agent"""
        if not self.milestone_refinement_agent:
            return {"error": "Milestone refinement agent not available"}
        
        try:
            # Milestone refinement agent would handle targeted refinement
            return {
                "success": True, 
                "method": method,
                "refined_areas": params.get("problematic_areas", [])
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _delegate_to_gap_filler_agent(self, method: str, params: Dict) -> Dict:
        """Delegate task to gap filler agent"""
        if not self.gap_filler_agent:
            return {"error": "Gap filler agent not available"}
        
        try:
            if method == "comprehensive_analysis":
                # Call gap filler's gap detection method
                conversation = params.get("conversation", [])
                milestone_context = {
                    "goal_title": params.get("goal_title", ""),
                    "person": params.get("person", ""),
                    "goal_id": params.get("goal_id", "")
                }
                
                # Use the correct method from GapFillerAgent
                gap_result = self.gap_filler_agent.detect_gaps_in_conversation(
                    conversation, milestone_context
                )
                
                # Also get pattern analysis
                pattern_result = self.gap_filler_agent.analyze_conversation_patterns(
                    conversation, "comprehensive"
                )
                
                return {
                    "success": True, 
                    "gap_analysis": gap_result,
                    "pattern_analysis": pattern_result
                }
            
            return {"success": True, "delegated": True}
        except Exception as e:
            import traceback
            print(f"DEBUG: Gap filler agent delegation error: {e}")
            traceback.print_exc()
            return {"error": str(e)}
    
    def _log_communication(self, target_agent: str, method: str, result: Any):
        """Log inter-agent communication for debugging and analysis"""
        log_entry = {
            "timestamp": datetime.now(),
            "target_agent": target_agent,
            "method": method,
            "result_summary": str(result)[:200] + "..." if len(str(result)) > 200 else str(result),
            "success": "error" not in str(result).lower()
        }
        
        self.communication_log.append(log_entry)
        
        # Keep log size manageable
        if len(self.communication_log) > 100:
            self.communication_log = self.communication_log[-50:]
    
