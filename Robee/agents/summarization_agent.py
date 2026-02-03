"""
Summarization Agent - A comprehensive agent for generating various types of summaries
during interview conversations, gap analysis, and milestone discussions.

This agent consolidates all summarization functionality from the system into a single,
reusable class that can handle different types of summaries:
- Interview conversation summaries
- Gap analysis summaries  
- Milestone prerequisite summaries
- Comprehensive reports
- Topic transition summaries
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime


class SummarizationAgent:
    """
    A comprehensive summarization agent that handles all types of summaries
    in the career development interview system.
    """
    
    def __init__(self, llm_client, parameters: Dict = None):
        """
        Initialize the summarization agent.
        
        Args:
            llm_client: OpenAI client for API calls
            parameters: Configuration parameters for different summary types
        """
        self.client = llm_client
        self.parameters = parameters or {}
        self.summary_cache = {}
        
        logging.info("SummarizationAgent initialized")
    
    def generate_conversation_summary(self, history: List[Dict], 
                                    goal_title: str = "", 
                                    summary_type: str = "comprehensive") -> str:
        """
        Generate a summary of the conversation history.
        
        Args:
            history: List of conversation messages
            goal_title: The goal being discussed
            summary_type: Type of summary ('brief', 'comprehensive', 'focused')
            
        Returns:
            str: Generated summary
        """
        try:
            if not history:
                return "No conversation data available for summary."
            
            # Prepare conversation text
            conversation_text = self._format_conversation_history(history)
            
            # Create summary prompt based on type
            if summary_type == "brief":
                prompt = self._create_brief_summary_prompt(conversation_text, goal_title)
            elif summary_type == "focused":
                prompt = self._create_focused_summary_prompt(conversation_text, goal_title)
            else:  # comprehensive
                prompt = self._create_comprehensive_summary_prompt(conversation_text, goal_title)
            
            # Generate summary using LLM
            response = self.client.chat.completions.create(
                model=self.parameters.get('model', 'gpt-4o'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.parameters.get('max_tokens', 500),
                temperature=self.parameters.get('temperature', 0.3)
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Cache the summary
            cache_key = f"conversation_{goal_title}_{summary_type}_{len(history)}"
            self.summary_cache[cache_key] = {
                'summary': summary,
                'timestamp': datetime.now(),
                'message_count': len(history)
            }
            
            return summary
            
        except Exception as e:
            logging.error(f"Error generating conversation summary: {e}")
            return f"Summary generation failed: {str(e)}"
    
    def generate_gap_analysis_summary(self, conversation: List[Dict], 
                                    existing_milestones: List[str],
                                    goal_title: str = "") -> Dict:
        """
        Generate a summary focused on identifying gaps and missing prerequisites.
        
        Args:
            conversation: Conversation history
            existing_milestones: List of existing milestone names
            goal_title: The goal being analyzed
            
        Returns:
            Dict: Gap analysis summary with suggestions
        """
        try:
            conversation_text = self._format_conversation_history(conversation)
            
            prompt = f"""
            Analyze this career development conversation to identify missing prerequisites and gaps.
            
            GOAL: {goal_title}
            EXISTING MILESTONES: {existing_milestones}
            
            CONVERSATION:
            {conversation_text}
            
            Provide a comprehensive gap analysis including:
            1. **Missing Prerequisites**: Specific steps or requirements not mentioned
            2. **Skill Gaps**: Abilities or knowledge that seem to be missing
            3. **Experience Gaps**: Types of experience that would be beneficial
            4. **Network Gaps**: People or connections that could help
            5. **Resource Gaps**: Tools, resources, or support systems needed
            6. **Suggested Milestones**: New milestones to fill identified gaps
            
            Format your response as a structured analysis with clear sections.
            For each suggested milestone, specify what existing milestone it should connect to.
            """
            
            response = self.client.chat.completions.create(
                model=self.parameters.get('model', 'gpt-4o'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.parameters.get('max_tokens', 800),
                temperature=self.parameters.get('temperature', 0.3)
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Parse the analysis into structured format
            structured_analysis = self._parse_gap_analysis(analysis_text)
            structured_analysis['raw_analysis'] = analysis_text
            structured_analysis['goal_title'] = goal_title
            structured_analysis['existing_milestones'] = existing_milestones
            
            return structured_analysis
            
        except Exception as e:
            logging.error(f"Error generating gap analysis summary: {e}")
            return {
                'error': str(e),
                'comprehensive_summary': f"Gap analysis failed: {str(e)}",
                'suggested_milestones': []
            }
    
    def generate_milestone_prerequisite_summary(self, conversation: List[Dict],
                                              milestone_name: str,
                                              goal_context: str = "") -> Dict:
        """
        Generate a summary focused on prerequisites for a specific milestone.
        
        Args:
            conversation: Conversation history
            milestone_name: The milestone to analyze
            goal_context: Context about the overall goal
            
        Returns:
            Dict: Prerequisites analysis for the milestone
        """
        try:
            conversation_text = self._format_conversation_history(conversation)
            
            prompt = f"""
            Analyze this conversation to identify prerequisites for achieving the milestone: "{milestone_name}"
            
            GOAL CONTEXT: {goal_context}
            
            CONVERSATION:
            {conversation_text}
            
            Focus on identifying:
            1. **Direct Prerequisites**: What must be completed before this milestone
            2. **Skill Requirements**: What skills are needed
            3. **Knowledge Requirements**: What knowledge is necessary
            4. **Resource Requirements**: What resources, tools, or support is needed
            5. **Timeline Considerations**: How long things might take
            6. **Risk Factors**: What could go wrong or create delays
            
            Provide specific, actionable insights based on the conversation.
            """
            
            response = self.client.chat.completions.create(
                model=self.parameters.get('model', 'gpt-4o'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.parameters.get('max_tokens', 600),
                temperature=self.parameters.get('temperature', 0.3)
            )
            
            analysis = response.choices[0].message.content.strip()
            
            return {
                'milestone_name': milestone_name,
                'prerequisite_analysis': analysis,
                'goal_context': goal_context,
                'conversation_length': len(conversation)
            }
            
        except Exception as e:
            logging.error(f"Error generating milestone prerequisite summary: {e}")
            return {
                'error': str(e),
                'milestone_name': milestone_name,
                'prerequisite_analysis': f"Analysis failed: {str(e)}"
            }
    
    def generate_topic_transition_summary(self, history: List[Dict]) -> Tuple[str, str]:
        """
        Generate a summary for transitioning between interview topics.
        
        Args:
            history: Conversation history
            
        Returns:
            Tuple[str, str]: (transition_question, summary_of_previous_topics)
        """
        try:
            conversation_text = self._format_conversation_history(history)
            
            # Generate topic summary
            summary_prompt = f"""
            Summarize the key points discussed in this interview conversation so far:
            
            {conversation_text}
            
            Provide a concise summary of:
            - Main topics covered
            - Key insights shared
            - Important milestones or achievements mentioned
            - Areas that need more exploration
            
            Keep the summary focused and under 200 words.
            """
            
            # Generate transition question
            transition_prompt = f"""
            Based on this interview conversation, generate an appropriate transition question 
            to move to the next topic or explore deeper:
            
            {conversation_text}
            
            The question should:
            - Build on what has been discussed
            - Explore new angles or deeper details
            - Be engaging and open-ended
            - Help uncover more specific information
            
            Generate just the question, no additional text.
            """
            
            # Make both API calls
            summary_response = self.client.chat.completions.create(
                model=self.parameters.get('model', 'gpt-4o'),
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            transition_response = self.client.chat.completions.create(
                model=self.parameters.get('model', 'gpt-4o'),
                messages=[{"role": "user", "content": transition_prompt}],
                max_tokens=150,
                temperature=0.5
            )
            
            summary = summary_response.choices[0].message.content.strip()
            transition_question = transition_response.choices[0].message.content.strip()
            
            return transition_question, summary
            
        except Exception as e:
            logging.error(f"Error generating topic transition summary: {e}")
            return f"Error generating transition: {str(e)}", ""
    
    def generate_session_report(self, conversation: List[Dict],
                              goal_title: str,
                              milestones_discussed: List[str] = None,
                              gaps_identified: List[str] = None) -> str:
        """
        Generate a comprehensive session report.
        
        Args:
            conversation: Full conversation history
            goal_title: The main goal discussed
            milestones_discussed: List of milestones mentioned
            gaps_identified: List of gaps found
            
        Returns:
            str: Comprehensive session report
        """
        try:
            conversation_text = self._format_conversation_history(conversation)
            milestones_text = ", ".join(milestones_discussed) if milestones_discussed else "None specified"
            gaps_text = ", ".join(gaps_identified) if gaps_identified else "None identified"
            
            prompt = f"""
            Generate a comprehensive session report for this career development interview.
            
            GOAL: {goal_title}
            MILESTONES DISCUSSED: {milestones_text}
            GAPS IDENTIFIED: {gaps_text}
            
            CONVERSATION:
            {conversation_text}
            
            Create a professional report including:
            
            ## Session Summary
            - Overview of the goal and discussion
            - Key topics covered
            - Duration and depth of conversation
            
            ## Key Insights
            - Important discoveries about the career path
            - Strengths and opportunities identified
            - Critical success factors discussed
            
            ## Milestones Analysis
            - Current milestone status
            - Prerequisites and dependencies
            - Gaps or missing steps identified
            
            ## Recommendations
            - Next steps for career development
            - Priority areas to focus on
            - Resources or support needed
            
            ## Action Items
            - Specific actions to take
            - Timeline considerations
            - Follow-up needed
            
            Make the report actionable and insightful.
            """
            
            response = self.client.chat.completions.create(
                model=self.parameters.get('model', 'gpt-4o'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            report = response.choices[0].message.content.strip()
            
            # Add metadata
            metadata = f"""
            ---
            **Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            **Conversation Length:** {len(conversation)} messages
            **Goal:** {goal_title}
            ---
            
            """
            
            return metadata + report
            
        except Exception as e:
            logging.error(f"Error generating session report: {e}")
            return f"Session report generation failed: {str(e)}"
    
    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Format conversation history into readable text."""
        if not history:
            return "No conversation history available."
        
        formatted_text = ""
        for i, msg in enumerate(history):
            msg_type = msg.get('type', 'unknown')
            content = msg.get('content', '')
            
            if msg_type == 'question':
                formatted_text += f"Interviewer: {content}\n\n"
            elif msg_type == 'answer':
                formatted_text += f"User: {content}\n\n"
            elif msg_type in ['guidance', 'intervention', 'system']:
                formatted_text += f"System: {content}\n\n"
        
        return formatted_text.strip()
    
    def _create_brief_summary_prompt(self, conversation: str, goal_title: str) -> str:
        """Create prompt for brief summary."""
        return f"""
        Create a brief summary (under 100 words) of this career development conversation about "{goal_title}":
        
        {conversation}
        
        Focus on the most important points and key takeaways.
        """
    
    def _create_focused_summary_prompt(self, conversation: str, goal_title: str) -> str:
        """Create prompt for focused summary."""
        return f"""
        Create a focused summary of this career development conversation about "{goal_title}":
        
        {conversation}
        
        Focus on:
        - Specific milestones discussed
        - Key challenges or obstacles mentioned
        - Resources or support systems identified
        - Next steps or action items
        
        Keep it concise but comprehensive (200-300 words).
        """
    
    def _create_comprehensive_summary_prompt(self, conversation: str, goal_title: str) -> str:
        """Create prompt for comprehensive summary."""
        return f"""
        Create a comprehensive summary of this career development conversation about "{goal_title}":
        
        {conversation}
        
        Include:
        1. **Goal Overview**: What the user is trying to achieve
        2. **Current Status**: Where they are now
        3. **Milestones Discussed**: Specific steps or achievements mentioned
        4. **Challenges**: Obstacles or difficulties identified
        5. **Resources**: Support systems, tools, or people mentioned
        6. **Insights**: Key learnings or realizations
        7. **Next Steps**: Proposed actions or areas for further exploration
        
        Make it detailed and actionable (400-500 words).
        """
    
    def _parse_gap_analysis(self, analysis_text: str) -> Dict:
        """Parse gap analysis text into structured format."""
        try:
            # Extract suggested milestones using regex
            milestone_pattern = r'(?:^|\n)(?:\d+\.?\s*)?([^:\n]+)(?:\s*[:\-→]\s*connect(?:s)?\s+to\s+([^:\n]+))?'
            matches = re.findall(milestone_pattern, analysis_text, re.MULTILINE | re.IGNORECASE)
            
            suggested_milestones = []
            for match in matches:
                if match[0] and len(match[0].strip()) > 5:  # Filter out very short matches
                    milestone = {
                        'name': match[0].strip(),
                        'connects_to': match[1].strip() if match[1] else 'Unspecified',
                        'used': False
                    }
                    suggested_milestones.append(milestone)
            
            # Extract different types of gaps
            gap_types = []
            gap_indicators = {
                'skill': ['skill', 'ability', 'competency', 'expertise'],
                'experience': ['experience', 'practice', 'exposure'],
                'knowledge': ['knowledge', 'understanding', 'awareness'],
                'network': ['network', 'connection', 'contact', 'relationship'],
                'resource': ['resource', 'tool', 'support', 'funding']
            }
            
            analysis_lower = analysis_text.lower()
            for gap_type, indicators in gap_indicators.items():
                if any(indicator in analysis_lower for indicator in indicators):
                    gap_types.append(gap_type)
            
            return {
                'comprehensive_summary': analysis_text,
                'suggested_milestones': suggested_milestones,
                'gap_types_identified': gap_types,
                'analysis_timestamp': datetime.now().isoformat(),
                'milestone_count': len(suggested_milestones)
            }
            
        except Exception as e:
            logging.error(f"Error parsing gap analysis: {e}")
            return {
                'comprehensive_summary': analysis_text,
                'suggested_milestones': [],
                'gap_types_identified': [],
                'parse_error': str(e)
            }
    
    def get_cached_summary(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached summary if available and recent."""
        if cache_key in self.summary_cache:
            cached = self.summary_cache[cache_key]
            # Check if cache is less than 1 hour old
            time_diff = datetime.now() - cached['timestamp']
            if time_diff.total_seconds() < 3600:  # 1 hour
                return cached
        return None
    
    def clear_cache(self):
        """Clear the summary cache."""
        self.summary_cache.clear()
        logging.info("Summary cache cleared")
    
    def get_summary_statistics(self) -> Dict:
        """Get statistics about summaries generated."""
        return {
            'cache_size': len(self.summary_cache),
            'cache_keys': list(self.summary_cache.keys()),
            'agent_initialized': hasattr(self, 'client')
        }