import logging
from core.auxiliary import (
    execute_queries, 
    fill_prompt_with_interview, 
    chat_to_string
)
from io import BytesIO
from base64 import b64decode
from openai import OpenAI
import os
import re
import sys

# Add agents directory to path for importing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'agents'))
try:
    from agents.summarization_agent import SummarizationAgent
except ImportError:
    # Fallback if import fails
    SummarizationAgent = None
    logging.warning("SummarizationAgent not available, falling back to inline methods")


class LLMAgent(object):
    """ Class to manage LLM-based agents. """
    def __init__(self, api_key, timeout:int=30, max_retries:int=3):
        # Configure OpenAI client
        self.client = OpenAI(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries
        )
        
        # Initialize summarization agent if available
        if SummarizationAgent:
            self.summarization_agent = SummarizationAgent(
                llm_client=self.client,
                parameters={'model': 'gpt-4o', 'max_tokens': 800, 'temperature': 0.3}
            )
        else:
            self.summarization_agent = None
            
        logging.info("OpenAI client instantiated. Should happen only once!")

    def load_parameters(self, parameters:dict):
        """ Load interview guidelines for prompt construction. """
        self.parameters = parameters
        
        # Update summarization agent parameters if available
        if self.summarization_agent:
            self.summarization_agent.parameters.update({
                'model': parameters.get('model', 'gpt-4o'),
                'max_tokens': parameters.get('max_tokens', 800),
                'temperature': parameters.get('temperature', 0.3)
            })

    def transcribe(self, audio) -> str:
        """ Transcribe audio file. """
        audio_file = BytesIO(b64decode(audio))
        audio_file.name = "audio.webm"

        response = self.client.audio.transcriptions.create(
          model="whisper-1", 
          file=audio_file,
          language="en" 
        )
        return response.text

    def construct_query(self, tasks:list, history:list, user_message:str=None) -> dict:
        """ 
        Construct OpenRouter API completions query, 
        defaults to qwen/qwen3-14b:free model, 300 token answer limit, and temperature of 0. 
        """
        return {
            task: {
                "messages": [{
                    "role":"user", 
                    "content": fill_prompt_with_interview(
                        self.parameters[task]['prompt'], 
                        self.parameters['interview_plan'],
                        history,
                        user_message=user_message
                    )
                }],
                "model": self.parameters[task].get('model', 'gpt-4o'),
                "max_tokens": self.parameters[task].get('max_tokens', 300),
                "temperature": self.parameters[task].get('temperature', 0)
            } for task in tasks
        }

    def review_answer(self, message:str, history:list) -> bool:
        """ Moderate answers: Are they on topic? """
        response = execute_queries(
            self.client.chat.completions.create,
            self.construct_query(['moderator'], history, message)
        )
        return "yes" in response["moderator"].lower()

    def review_question(self, next_question:str) -> bool:
        """ Moderate questions: Are they flagged by the moderation endpoint? """
        response = self.client.moderations.create(
            model="text-moderation-latest",
            input=next_question,
        )
        return response.to_dict()["results"][0]["flagged"]
        
    def probe_within_topic(self, history:list) -> str:
        """ Return next 'within-topic' probing question. """
        response = execute_queries(
            self.client.chat.completions.create,
            self.construct_query(['probe'], history)
        )
        return response['probe']

    def handle_skip_pattern(self, history:list, skip_type:str, milestones:list = None, goal_title:str = "") -> str:
        """ 
        Generate adaptive responses based on skip patterns:
        - 'first_skip': Ask a completely different question in the same context
        - 'multiple_skips': Ask about different milestones or other contributing features
        - 'consistent_skips': Break suggestions and different approaches
        """
        # Create specialized prompts based on skip type
        skip_context = {
            'first_skip': f"User skipped the previous question. Instead of reformatting the same question, ask a COMPLETELY DIFFERENT question about the same goal '{goal_title}'. Focus on a different angle like: timing, challenges overcome, resources used, people who helped, or unexpected discoveries. Generate a fresh perspective question.",
            
            'multiple_skips': f"User has skipped multiple questions about '{goal_title}'. Switch focus to ask about a DIFFERENT MILESTONE from the existing ones: {[ms['name'] for ms in milestones] if milestones else 'None'}. Or ask about OTHER FEATURES that contributed to reaching this goal: external factors, support systems, tools, timing, or serendipitous events. Make it engaging and specific.",
            
            'consistent_skips': "User consistently skips questions. Offer break suggestions, summary options, and different approaches with empathy."
        }
        
        # Add skip context to history for specialized response
        enhanced_history = history.copy()
        enhanced_history.append({
            "type": "context",
            "content": f"SKIP_PATTERN_HANDLING: {skip_context.get(skip_type, 'Handle user skipping behavior adaptively')}",
            "topic_idx": 0,
            "summary": ""
        })
        
        response = execute_queries(
            self.client.chat.completions.create,
            self.construct_query(['probe'], enhanced_history)
        )
        return response['probe']

    def detect_prerequisites_gaps(self, history: list, current_milestone_context: dict = None) -> dict:
        """
        Analyze user responses to detect missing prerequisites using specialized gap detection.
        Returns comprehensive gap analysis with suggested milestones and connections.
        """
        try:
            # Create enhanced context for gap detection
            gap_context = {
                "milestone_context": current_milestone_context or {},
                "conversation_history": history,
                "analysis_type": "prerequisite_detection"
            }
            
            # Use multiple specialized agents for comprehensive analysis
            tasks = ['prerequisite_scanner', 'gap_classifier', 'dependency_mapper']
            available_tasks = [task for task in tasks if task in self.parameters]
            
            if not available_tasks:
                # Fallback to regular probe if gap agents not configured
                return {"gap_detected": False, "suggestions": []}
            
            response = execute_queries(
                self.client.chat.completions.create,
                self.construct_query(available_tasks, history)
            )
            
            # Process and synthesize responses from multiple agents
            return self._synthesize_gap_analysis(response, current_milestone_context)
            
        except Exception as e:
            logging.error(f"Error in gap detection: {e}")
            return {"gap_detected": False, "error": str(e)}

    def _synthesize_gap_analysis(self, agent_responses: dict, milestone_context: dict = None) -> dict:
        """Synthesize responses from multiple gap detection agents"""
        synthesis = {
            "gap_detected": False,
            "gap_types": [],
            "confidence_score": 0.0,
            "suggested_milestones": [],
            "prerequisite_chains": [],
            "priority_gaps": []
        }
        
        # Analyze scanner results
        if 'prerequisite_scanner' in agent_responses:
            scanner_result = agent_responses['prerequisite_scanner']
            if "GAP_DETECTED" in scanner_result.upper():
                synthesis["gap_detected"] = True
                synthesis["confidence_score"] += 0.3
        
        # Analyze classifier results
        if 'gap_classifier' in agent_responses:
            classifier_result = agent_responses['gap_classifier']
            synthesis["gap_types"] = self._extract_gap_types(classifier_result)
            if synthesis["gap_types"]:
                synthesis["confidence_score"] += 0.4
        
        # Analyze dependency mapper results
        if 'dependency_mapper' in agent_responses:
            mapper_result = agent_responses['dependency_mapper']
            synthesis["suggested_milestones"] = self._extract_milestone_suggestions(mapper_result)
            synthesis["prerequisite_chains"] = self._extract_prerequisite_chains(mapper_result)
            if synthesis["suggested_milestones"]:
                synthesis["confidence_score"] += 0.3
        
        return synthesis

    def _extract_gap_types(self, classifier_response: str) -> list:
        """Extract gap types from classifier response"""
        gap_types = []
        gap_patterns = [
            ("SKILL_GAP", "skill"),
            ("EXPERIENCE_GAP", "experience"), 
            ("KNOWLEDGE_GAP", "knowledge"),
            ("NETWORK_GAP", "network"),
            ("RESOURCE_GAP", "resource"),
            ("TIMING_GAP", "timing"),
            ("CONTEXTUAL_GAP", "contextual")
        ]
        
        for pattern, gap_type in gap_patterns:
            if pattern in classifier_response.upper():
                gap_types.append(gap_type)
        
        return gap_types

    def _extract_milestone_suggestions(self, mapper_response: str) -> list:
        """Extract milestone suggestions from dependency mapper response"""
        suggestions = []
        
        # Look for NEW_MILESTONE patterns
        import re
        milestone_pattern = r'\[NEW_MILESTONE\]\s*Name:\s*([^|]+)\s*\|\s*Suggest connect to:\s*([^|\n]+)'
        matches = re.findall(milestone_pattern, mapper_response)
        
        for name, connection in matches:
            suggestions.append({
                "name": name.strip(),
                "connect_to": connection.strip(),
                "type": "prerequisite",
                "confidence": 0.8
            })
        
        return suggestions

    def _extract_prerequisite_chains(self, mapper_response: str) -> list:
        """Extract prerequisite chains from dependency mapper response"""
        chains = []
        
        # Look for chain patterns like "A -> B -> C"
        import re
        chain_pattern = r'([A-Za-z0-9\s]+)\s*->\s*([A-Za-z0-9\s]+)(?:\s*->\s*([A-Za-z0-9\s]+))?'
        matches = re.findall(chain_pattern, mapper_response)
        
        for match in matches:
            chain = [item.strip() for item in match if item.strip()]
            if len(chain) >= 2:
                chains.append(chain)
        
        return chains

    def analyze_gap_patterns(self, history: list, gap_type: str = "comprehensive") -> dict:
        """
        Analyze conversation patterns to identify specific gap types and provide
        targeted recommendations for milestone generation.
        """
        if self.summarization_agent:
            try:
                # Use the dedicated summarization agent for gap analysis
                goal_title = gap_type if isinstance(gap_type, str) and gap_type != "comprehensive" else ""
                existing_milestones = []  # Could be passed as parameter in future
                
                gap_analysis = self.summarization_agent.generate_gap_analysis_summary(
                    conversation=history,
                    existing_milestones=existing_milestones,
                    goal_title=goal_title
                )
                
                return gap_analysis
                
            except Exception as e:
                logging.error(f"SummarizationAgent gap analysis failed, falling back: {e}")
        
        # Fallback to original method
        try:
            # Use gap_synthesizer agent if available
            if 'gap_synthesizer' in self.parameters:
                enhanced_history = history.copy()
                enhanced_history.append({
                    "type": "gap_analysis",
                    "content": f"ANALYZE_GAPS: {gap_type}",
                    "topic_idx": 0,
                    "summary": ""
                })
                
                response = execute_queries(
                    self.client.chat.completions.create,
                    self.construct_query(['gap_synthesizer'], enhanced_history)
                )
                
                return self._parse_gap_analysis(response['gap_synthesizer'])
            
            return {"analysis_complete": False, "message": "Gap synthesizer not configured"}
            
        except Exception as e:
            logging.error(f"Error in gap pattern analysis: {e}")
            return {"analysis_complete": False, "error": str(e)}

    def _parse_gap_analysis(self, analysis_response: str) -> dict:
        """Parse gap analysis response into structured format"""
        return {
            "analysis_complete": True,
            "gaps_identified": "HIGH_PRIORITY" in analysis_response.upper(),
            "recommendations": analysis_response,
            "action_items": self._extract_action_items(analysis_response)
        }

    def _extract_action_items(self, response: str) -> list:
        """Extract actionable items from gap analysis"""
        action_items = []
        lines = response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['action:', 'recommend:', 'suggest:', 'next step:']):
                action_items.append(line.strip())
        
        return action_items

    def generate_comprehensive_summary(self, history: list, gap_analysis: dict = None) -> str:
        """
        Generate comprehensive summary with integrated gap analysis using the SummarizationAgent.
        """
        if self.summarization_agent:
            try:
                # Use the dedicated summarization agent
                return self.summarization_agent.generate_conversation_summary(
                    history=history,
                    goal_title=gap_analysis.get('goal_title', '') if gap_analysis else '',
                    summary_type='comprehensive'
                )
            except Exception as e:
                logging.error(f"SummarizationAgent failed, falling back to original method: {e}")
        
        # Fallback to original method if summarization agent not available
        try:
            # Use multiple agents for comprehensive analysis
            summary_tasks = ['summary']
            if gap_analysis and gap_analysis.get('gap_detected'):
                if 'personalization_agent' in self.parameters:
                    summary_tasks.append('personalization_agent')
            
            response = execute_queries(
                self.client.chat.completions.create,
                self.construct_query(summary_tasks, history)
            )
            
            base_summary = response.get('summary', '')
            
            # Enhance with personalization if available
            if 'personalization_agent' in response:
                personalized_insights = response['personalization_agent']
                return f"{base_summary}\n\n**Personalized Insights:**\n{personalized_insights}"
            
            return base_summary
            
        except Exception as e:
            logging.error(f"Error generating comprehensive summary: {e}")
            return "Summary generation failed."

    def transition_topic(self, history:list) -> tuple[str, str]:
        """ 
        Determine next interview question transition from one topic
        cluster to the next. If have defined summarize model in parameters
        will also get summarization of interview thus far.
        """
        if self.summarization_agent:
            try:
                # Use the dedicated summarization agent for topic transitions
                return self.summarization_agent.generate_topic_transition_summary(history)
            except Exception as e:
                logging.error(f"SummarizationAgent transition failed, falling back: {e}")
        
        # Fallback to original method
        summarize = self.parameters.get('summarize')
        tasks = ['summary','transition'] if summarize else ['transition']
        response = execute_queries(
            self.client.chat.completions.create,
            self.construct_query(tasks, history)
        )
        return response['transition'], response.get('summary', '')


    def generate_session_report(self, history: list, goal_title: str = "", 
                               milestones_discussed: list = None, gaps_identified: list = None) -> str:
        """
        Generate a comprehensive session report using the SummarizationAgent.
        """
        if self.summarization_agent:
            try:
                return self.summarization_agent.generate_session_report(
                    conversation=history,
                    goal_title=goal_title,
                    milestones_discussed=milestones_discussed or [],
                    gaps_identified=gaps_identified or []
                )
            except Exception as e:
                logging.error(f"SummarizationAgent session report failed: {e}")
                return f"Session report generation failed: {str(e)}"
        else:
            return "SummarizationAgent not available for session reports."

    def generate_milestone_prerequisites_summary(self, history: list, milestone_name: str, 
                                               goal_context: str = "") -> dict:
        """
        Generate a summary focused on prerequisites for a specific milestone.
        """
        if self.summarization_agent:
            try:
                return self.summarization_agent.generate_milestone_prerequisite_summary(
                    conversation=history,
                    milestone_name=milestone_name,
                    goal_context=goal_context
                )
            except Exception as e:
                logging.error(f"SummarizationAgent milestone prerequisites failed: {e}")
                return {"error": str(e), "milestone_name": milestone_name}
        else:
            return {"error": "SummarizationAgent not available", "milestone_name": milestone_name}

    def get_summarization_statistics(self) -> dict:
        """Get statistics about the summarization agent."""
        if self.summarization_agent:
            return self.summarization_agent.get_summary_statistics()
        else:
            return {"summarization_agent_available": False}

    def clear_summary_cache(self):
        """Clear the summary cache in the summarization agent."""
        if self.summarization_agent:
            self.summarization_agent.clear_cache()
            logging.info("Summary cache cleared via LLMAgent")


def parse_new_milestone_suggestion(agent_message):
    # Example: [NEW_MILESTONE] Name: Internship in Paris | Suggest connect to: Bachelor Degree
    match = re.search(r"\[NEW_MILESTONE\]\s*Name:\s*(.?)\s\|\s*Suggest connect to:\s*(.*)", agent_message)
    if match:
        return {
            "name": match.group(1).strip(),
            "connect_to": match.group(2).strip()
        }
    return None

# def render_interview_tab():
#     # ... (existing code up to after agent response is appended)
#     if user_input:
#         st.session_state[chat_key].append({"role": "user", "content": user_input})
#         with st.spinner("Thinking..."):
#             agent = st.session_state.interview_agent
#             history = st.session_state[chat_key][-10:]
#             topic_idx = 1
#             for i, m in enumerate(history):
#                 if m["role"] == "assistant":
#                     msg_type = "question"
#                 else:
#                     msg_type = "answer"
#                 history[i] = {"type": msg_type, "content": m["content"], "topic_idx": topic_idx, "summary": ""}
#             try:
#                 next_question = agent.probe_within_topic(history)
#             except Exception as e:
#                 next_question = f"[Error from agent: {e}]"
#             st.session_state[chat_key].append({"role": "assistant", "content": next_question})

#             # --- NEW: Detect milestone suggestion ---
#             suggestion = parse_new_milestone_suggestion(next_question)
#             if suggestion:
#                 st.session_state[f"pending_milestone_{selected_milestone_id}"] = suggestion
#         st.rerun()

#     # --- NEW: Show milestone add form if suggestion exists ---
#     pending_key = f"pending_milestone_{selected_milestone_id}"
#     if pending_key in st.session_state:
#         suggestion = st.session_state[pending_key]
#         st.markdown("### 🚩 The AI suggests adding a new milestone!")
#         with st.form(key=f"add_milestone_form_{selected_milestone_id}", clear_on_submit=True):
#             name = st.text_input("Milestone Name", value=suggestion["name"])
#             score = st.slider("Importance Score", 1, 10, 5)
#             # List all milestones for causal connection
#             connect_options = {ms['id']: ms['name'] for ms in milestones}
#             connect_to = st.selectbox("Connect this milestone to (causal parent):", list(connect_options.keys()), format_func=lambda x: connect_options[x])
#             submitted = st.form_submit_button("Add Milestone")
#             if submitted:
#                 # Add the milestone to the data structure
#                 tracker.add_child_milestone(selected_person, selected_goal, name, score, connect_to)
#                 st.success(f"Milestone '{name}' added and connected to '{connect_options[connect_to]}'!")
#                 del st.session_state[pending_key]
#                 st.rerun()