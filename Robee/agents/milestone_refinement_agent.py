"""
Milestone Refinement Agent - Handles milestone optimization, validation, and enhancement

Role: Conducts detailed discussions about individual milestones.
Responsibilities:
- "Digs deeper" into the specifics of a milestone when the user wants to elaborate.
- Facilitates conversation to refine the content, name, or properties of a single milestone.
- Analyzes milestone prerequisites and gaps
- Suggests milestone improvements and connections
- Manages milestone properties and metadata
"""

import logging
import re
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from openai import OpenAI


@dataclass
class MilestoneRefinement:
    """Data structure for milestone refinement information"""
    milestone_id: str
    original_name: str
    refined_name: Optional[str] = None
    original_description: Optional[str] = None
    refined_description: Optional[str] = None
    prerequisites_identified: List[Dict] = None
    gaps_detected: List[Dict] = None
    confidence_score: float = 0.0
    refinement_suggestions: List[str] = None
    
    def __post_init__(self):
        if self.prerequisites_identified is None:
            self.prerequisites_identified = []
        if self.gaps_detected is None:
            self.gaps_detected = []
        if self.refinement_suggestions is None:
            self.refinement_suggestions = []


class MilestoneRefinementAgent:
    """
    Agent responsible for detailed milestone discussions and refinement.
    Handles milestone elaboration, prerequisite detection, and property refinement.
    """
    
    def __init__(self, llm_client: Optional[OpenAI] = None, parameters: Optional[Dict] = None):
        """
        Initialize the Milestone Refinement Agent
        
        Args:
            llm_client: OpenAI client for LLM interactions
            parameters: Configuration parameters for the agent
        """
        self.client = llm_client
        self.parameters = parameters or {}
        self.refinement_cache = {}
        self.conversation_history = []
        
        # Default parameters for milestone refinement
        self.default_params = {
            'model': 'gpt-4o',
            'temperature': 0.6,
            'max_tokens': 400,
            'max_refinement_iterations': 3
        }
        
        # Merge with provided parameters
        self.params = {**self.default_params, **self.parameters}
        
    def initiate_milestone_discussion(self, milestone: Dict[str, Any], 
                                    conversation_context: List[Dict] = None) -> str:
        """
        Start a detailed discussion about a specific milestone
        
        Args:
            milestone: The milestone dictionary to discuss
            conversation_context: Previous conversation history
            
        Returns:
            Initial question/prompt to start the discussion
        """
        milestone_name = milestone.get('name', 'Unknown Milestone')
        
        # Store context for this milestone
        self.current_milestone = milestone
        self.conversation_history = conversation_context or []
        
        # Generate initial discussion prompt
        prompt = f"""
        I'd like to dive deeper into your milestone: "{milestone_name}".
        
        Let's explore the details of how you achieved this. Could you tell me about:
        - The specific steps you took to reach this milestone
        - Any challenges you encountered along the way
        - What resources or support you needed
        - How long it took and what the key requirements were
        
        What aspect would you like to start with?
        """
        
        return prompt.strip()
    
    def process_milestone_details(self, user_response: str, milestone: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user's detailed response about a milestone to extract refinement information
        
        Args:
            user_response: User's detailed explanation about the milestone
            milestone: The milestone being discussed
            
        Returns:
            Dictionary containing extracted details and suggestions
        """
        try:
            # Detect new prerequisites mentioned
            prerequisites = self._detect_prerequisites_in_response(user_response, milestone)
            
            # Analyze gaps in the milestone progression
            gaps = self._analyze_milestone_gaps(user_response, milestone)
            
            # Generate follow-up questions
            follow_up_questions = self._generate_follow_up_questions(user_response, milestone)
            
            # Suggest milestone refinements
            refinement_suggestions = self._generate_refinement_suggestions(user_response, milestone)
            
            return {
                "prerequisites_detected": prerequisites,
                "gaps_identified": gaps,
                "follow_up_questions": follow_up_questions,
                "refinement_suggestions": refinement_suggestions,
                "new_milestone_suggestions": self._extract_milestone_suggestions(user_response)
            }
            
        except Exception as e:
            logging.error(f"Error processing milestone details: {e}")
            return {"error": str(e)}
    
    def _detect_prerequisites_in_response(self, response: str, milestone: Dict) -> List[Dict]:
        """
        Detect prerequisites mentioned in user's response
        
        Args:
            response: User's response text
            milestone: Current milestone context
            
        Returns:
            List of detected prerequisites
        """
        if not self.client:
            return []
            
        try:
            prompt = f"""
            CONTEXT: User is describing how they achieved: "{milestone.get('name', '')}"
            
            USER RESPONSE: {response}
            
            TASK: Identify specific prerequisites, requirements, or preparatory steps mentioned.
            
            Look for:
            - Specific skills that were needed
            - Courses or training completed
            - Resources gathered
            - Applications or processes completed
            - People who helped or connections made
            - Prior experiences that were necessary
            
            OUTPUT FORMAT (JSON):
            {{
                "prerequisites": [
                    {{
                        "name": "specific prerequisite name",
                        "type": "skill|experience|resource|connection|process",
                        "description": "brief description",
                        "confidence": 0.8
                    }}
                ]
            }}
            
            Provide ONLY the JSON output.
            """
            
            response_obj = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a prerequisite detection specialist."},
                    {"role": "user", "content": prompt}
                ],
                model=self.params['model'],
                temperature=0.3,
                max_tokens=300
            )
            
            result = response_obj.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            try:
                parsed = json.loads(result)
                return parsed.get('prerequisites', [])
            except json.JSONDecodeError:
                # Fallback to regex extraction
                return self._extract_prerequisites_with_regex(response)
                
        except Exception as e:
            logging.error(f"Error detecting prerequisites: {e}")
            return []
    
    def _extract_prerequisites_with_regex(self, response: str) -> List[Dict]:
        """Fallback method to extract prerequisites using regex patterns"""
        prerequisites = []
        
        # Common prerequisite patterns
        patterns = [
            r"I had to ([^.]+)",
            r"I needed to ([^.]+)", 
            r"First, I ([^.]+)",
            r"Before .+ I ([^.]+)",
            r"I completed ([^.]+)",
            r"I studied ([^.]+)",
            r"I learned ([^.]+)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                prerequisites.append({
                    "name": match.strip(),
                    "type": "inferred",
                    "description": f"Prerequisite inferred from: '{match.strip()}'",
                    "confidence": 0.6
                })
        
        return prerequisites
    
    def _analyze_milestone_gaps(self, response: str, milestone: Dict) -> List[Dict]:
        """
        Analyze potential gaps in milestone progression
        
        Args:
            response: User's response text
            milestone: Current milestone context
            
        Returns:
            List of identified gaps
        """
        if not self.client:
            return []
            
        try:
            prompt = f"""
            CONTEXT: Analyzing milestone achievement for: "{milestone.get('name', '')}"
            
            USER EXPLANATION: {response}
            
            TASK: Identify logical gaps or missing steps in the milestone progression.
            
            Look for:
            - Missing foundational skills or knowledge
            - Skipped preparatory steps
            - Unexplained jumps in progression
            - Missing support systems or resources
            - Timing or sequencing gaps
            
            OUTPUT FORMAT:
            GAP_TYPE: [SKILL|KNOWLEDGE|PROCESS|RESOURCE|TIMING]
            DESCRIPTION: [What's missing]
            IMPACT: [HIGH|MEDIUM|LOW]
            
            If no gaps found, respond with: NO_GAPS_DETECTED
            """
            
            response_obj = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a gap analysis specialist for career progression."},
                    {"role": "user", "content": prompt}
                ],
                model=self.params['model'],
                temperature=0.4,
                max_tokens=200
            )
            
            result = response_obj.choices[0].message.content.strip()
            
            if "NO_GAPS_DETECTED" in result:
                return []
            
            return self._parse_gap_analysis(result)
            
        except Exception as e:
            logging.error(f"Error analyzing gaps: {e}")
            return []
    
    def _parse_gap_analysis(self, analysis_text: str) -> List[Dict]:
        """Parse gap analysis text into structured format"""
        gaps = []
        lines = analysis_text.split('\n')
        
        current_gap = {}
        for line in lines:
            line = line.strip()
            if line.startswith('GAP_TYPE:'):
                if current_gap:
                    gaps.append(current_gap)
                current_gap = {'type': line.replace('GAP_TYPE:', '').strip()}
            elif line.startswith('DESCRIPTION:'):
                current_gap['description'] = line.replace('DESCRIPTION:', '').strip()
            elif line.startswith('IMPACT:'):
                current_gap['impact'] = line.replace('IMPACT:', '').strip()
        
        if current_gap:
            gaps.append(current_gap)
            
        return gaps
    
    def _generate_follow_up_questions(self, response: str, milestone: Dict) -> List[str]:
        """
        Generate follow-up questions to dig deeper into milestone details
        
        Args:
            response: User's response text
            milestone: Current milestone context
            
        Returns:
            List of follow-up questions
        """
        if not self.client:
            return ["Could you tell me more about the specific steps you took?"]
            
        try:
            prompt = f"""
            CONTEXT: User explained how they achieved: "{milestone.get('name', '')}"
            
            USER RESPONSE: {response}
            
            TASK: Generate 2-3 specific follow-up questions to dig deeper into:
            - Specific details that were mentioned but not elaborated
            - Missing prerequisites or steps that might exist
            - Challenges or obstacles they might have faced
            - Resources or support they might have needed
            
            Make questions specific to their response, not generic.
            
            OUTPUT FORMAT:
            1. [Specific question about something they mentioned]
            2. [Question about potential missing detail]
            3. [Question about a different aspect]
            """
            
            response_obj = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a skilled interviewer specializing in career milestone discussions."},
                    {"role": "user", "content": prompt}
                ],
                model=self.params['model'],
                temperature=0.7,
                max_tokens=200
            )
            
            result = response_obj.choices[0].message.content.strip()
            
            # Extract numbered questions
            questions = []
            for line in result.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering and clean up
                    question = re.sub(r'^\d+\.?\s*', '', line)
                    question = re.sub(r'^-\s*', '', question)
                    if question:
                        questions.append(question.strip())
            
            return questions[:3]  # Limit to 3 questions
            
        except Exception as e:
            logging.error(f"Error generating follow-up questions: {e}")
            return ["Could you elaborate on any specific challenges you faced?"]
    
    def _generate_refinement_suggestions(self, response: str, milestone: Dict) -> List[str]:
        """
        Generate suggestions for refining the milestone based on user's detailed explanation
        
        Args:
            response: User's response text
            milestone: Current milestone context
            
        Returns:
            List of refinement suggestions
        """
        if not self.client:
            return []
            
        try:
            current_name = milestone.get('name', '')
            current_score = milestone.get('score', 5)
            
            prompt = f"""
            CONTEXT: Milestone refinement for: "{current_name}" (Current importance: {current_score}/10)
            
            USER EXPLANATION: {response}
            
            TASK: Based on the detailed explanation, suggest improvements to:
            1. Milestone name (make it more specific/accurate if needed)
            2. Importance score (1-10, based on effort/impact revealed)
            3. Missing details that should be added
            
            OUTPUT FORMAT:
            NAME_SUGGESTION: [Improved name if needed, or "No change needed"]
            SCORE_SUGGESTION: [1-10] - [Brief justification]
            DETAILS_TO_ADD: [What additional details should be captured]
            """
            
            response_obj = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a milestone optimization specialist."},
                    {"role": "user", "content": prompt}
                ],
                model=self.params['model'],
                temperature=0.5,
                max_tokens=250
            )
            
            result = response_obj.choices[0].message.content.strip()
            return self._parse_refinement_suggestions(result)
            
        except Exception as e:
            logging.error(f"Error generating refinement suggestions: {e}")
            return []
    
    def _parse_refinement_suggestions(self, suggestions_text: str) -> List[str]:
        """Parse refinement suggestions into a structured list"""
        suggestions = []
        lines = suggestions_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('NAME_SUGGESTION:'):
                name_suggestion = line.replace('NAME_SUGGESTION:', '').strip()
                if name_suggestion != "No change needed":
                    suggestions.append(f"Consider renaming to: {name_suggestion}")
            elif line.startswith('SCORE_SUGGESTION:'):
                score_suggestion = line.replace('SCORE_SUGGESTION:', '').strip()
                suggestions.append(f"Importance score suggestion: {score_suggestion}")
            elif line.startswith('DETAILS_TO_ADD:'):
                details = line.replace('DETAILS_TO_ADD:', '').strip()
                if details:
                    suggestions.append(f"Add details: {details}")
        
        return suggestions
    
    def _extract_milestone_suggestions(self, response: str) -> List[Dict]:
        """
        Extract new milestone suggestions from user response
        
        Args:
            response: User's response text
            
        Returns:
            List of suggested new milestones
        """
        suggestions = []
        
        # Look for explicit milestone patterns mentioned in LLM responses
        milestone_pattern = r'\[NEW_MILESTONE\]\s*Name:\s*([^|]+)\s*\|\s*Suggest connect to:\s*([^|\n]+)'
        matches = re.findall(milestone_pattern, response)
        
        for name, connection in matches:
            suggestions.append({
                "name": name.strip(),
                "connect_to": connection.strip(),
                "type": "explicit",
                "confidence": 0.9
            })
        
        # Also look for implicit mentions of prerequisites or steps
        implicit_patterns = [
            r"I had to ([^.]+) before",
            r"First, I ([^.]+)",
            r"I needed to ([^.]+) in order to",
            r"The requirement was to ([^.]+)"
        ]
        
        for pattern in implicit_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                suggestions.append({
                    "name": match.strip(),
                    "connect_to": "current_milestone",
                    "type": "implicit",
                    "confidence": 0.7
                })
        
        return suggestions
    
    def refine_milestone_properties(self, milestone: Dict[str, Any], 
                                  refinements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply refinements to milestone properties
        
        Args:
            milestone: Original milestone dictionary
            refinements: Dictionary of proposed refinements
            
        Returns:
            Updated milestone dictionary
        """
        updated_milestone = milestone.copy()
        
        # Apply name refinement
        if refinements.get('refined_name'):
            updated_milestone['name'] = refinements['refined_name']
            updated_milestone['original_name'] = milestone.get('name')
        
        # Apply description refinement
        if refinements.get('refined_description'):
            updated_milestone['description'] = refinements['refined_description']
            if 'original_description' not in updated_milestone:
                updated_milestone['original_description'] = milestone.get('description', '')
        
        # Apply score refinement
        if refinements.get('refined_score'):
            updated_milestone['score'] = refinements['refined_score']
            updated_milestone['original_score'] = milestone.get('score')
        
        # Add refinement metadata
        updated_milestone['refinement_applied'] = True
        updated_milestone['refinement_timestamp'] = datetime.now().isoformat()
        
        if refinements.get('prerequisites_identified'):
            updated_milestone['identified_prerequisites'] = refinements['prerequisites_identified']
        
        if refinements.get('gaps_detected'):
            updated_milestone['gaps_detected'] = refinements['gaps_detected']
        
        return updated_milestone
    
    def generate_milestone_summary(self, milestone: Dict[str, Any], 
                                 discussion_history: List[str]) -> str:
        """
        Generate a comprehensive summary of milestone discussion and refinements
        
        Args:
            milestone: The milestone that was discussed
            discussion_history: List of discussion exchanges
            
        Returns:
            Comprehensive summary text
        """
        if not self.client:
            return f"Summary for milestone: {milestone.get('name', 'Unknown')}"
            
        try:
            discussion_text = "\n".join(discussion_history)
            
            prompt = f"""
            CONTEXT: Create a comprehensive summary of milestone discussion
            
            MILESTONE: {milestone.get('name', '')}
            ORIGINAL SCORE: {milestone.get('score', 'N/A')}/10
            
            DISCUSSION HISTORY:
            {discussion_text}
            
            TASK: Create a structured summary including:
            1. Key details learned about the milestone
            2. Prerequisites and requirements identified
            3. Challenges and obstacles mentioned
            4. Resources and support needed
            5. Refinement suggestions
            6. Any gaps or missing information identified
            
            Keep it concise but comprehensive.
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a milestone analysis specialist creating comprehensive summaries."},
                    {"role": "user", "content": prompt}
                ],
                model=self.params['model'],
                temperature=0.4,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Error generating milestone summary: {e}")
            return f"Summary generation failed for milestone: {milestone.get('name', 'Unknown')}"
    
    def update_milestone_with_ai_insights(self, tracker, person: str, goal_id: str, 
                                        milestone_id: str, user_response: str) -> Dict[str, Any]:
        """
        Update milestone with AI-generated insights from user discussion
        
        Args:
            tracker: MilestoneTracker instance
            person: Person identifier
            goal_id: Goal identifier
            milestone_id: Milestone identifier
            user_response: User's detailed response about the milestone
            
        Returns:
            Results of the update process
        """
        try:
            # Get current milestone
            milestone = tracker.get_milestone(person, milestone_id)
            if not milestone:
                return {"error": "Milestone not found"}
            
            # Process the details
            insights = self.process_milestone_details(user_response, milestone)
            
            # Update milestone properties based on insights
            update_results = {
                "milestone_updated": False,
                "new_milestones_suggested": len(insights.get('new_milestone_suggestions', [])),
                "prerequisites_found": len(insights.get('prerequisites_detected', [])),
                "gaps_identified": len(insights.get('gaps_identified', [])),
                "insights": insights
            }
            
            # Apply any refinement suggestions
            if insights.get('refinement_suggestions'):
                # Update milestone with additional metadata
                milestone['ai_insights'] = {
                    'last_analysis': datetime.now().isoformat(),
                    'prerequisites_detected': insights.get('prerequisites_detected', []),
                    'gaps_identified': insights.get('gaps_identified', []),
                    'refinement_suggestions': insights.get('refinement_suggestions', [])
                }
                update_results["milestone_updated"] = True
            
            return update_results
            
        except Exception as e:
            logging.error(f"Error updating milestone with AI insights: {e}")
            return {"error": str(e)}
    
    def get_refinement_statistics(self) -> Dict[str, Any]:
        """Get statistics about milestone refinement activities"""
        return {
            "total_milestones_refined": len(self.refinement_cache),
            "average_prerequisites_per_milestone": sum(
                len(r.prerequisites_identified) for r in self.refinement_cache.values()
            ) / max(len(self.refinement_cache), 1),
            "total_gaps_identified": sum(
                len(r.gaps_detected) for r in self.refinement_cache.values()
            ),
            "agent_parameters": self.params
        }
    
    def clear_refinement_cache(self):
        """Clear the refinement cache"""
        self.refinement_cache.clear()
        self.conversation_history.clear()
        logging.info("Milestone refinement cache cleared")