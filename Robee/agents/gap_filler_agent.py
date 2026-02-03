"""
Gap Filler Agent - Detects and fills gaps in roadmaps
"""
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from openai import OpenAI

class GapFillerAgent:
    """
    Primary Responsibilities:
    - Detect and fill gaps in roadmaps
    - Identify missing prerequisites and dependencies
    - Analyze conversation patterns for gaps
    - Generate milestone suggestions to fill gaps
    """
    
    def __init__(self, api_key: str):
        self.gap_detector = GapDetector(api_key)
        self.pattern_analyzer = PatternAnalyzer()
        self.milestone_suggester = MilestoneSuggester(api_key)
        self.prerequisite_analyzer = PrerequisiteAnalyzer(api_key)
        
    def detect_gaps_in_conversation(self, history: List[Dict], 
                                   milestone_context: Dict = None) -> Dict:
        """Main gap detection function for conversation analysis"""
        return self.gap_detector.detect_prerequisites_gaps(history, milestone_context)
        
    def analyze_conversation_patterns(self, history: List[Dict], 
                                    gap_type: str = "comprehensive") -> Dict:
        """Analyze conversation patterns to identify gap types"""
        return self.pattern_analyzer.analyze_gap_patterns(history, gap_type)
        
    def suggest_missing_milestones(self, gaps: Dict, context: Dict) -> List[Dict]:
        """Generate milestone suggestions based on detected gaps"""
        return self.milestone_suggester.generate_milestone_suggestions(gaps, context)
        
    def identify_prerequisite_chains(self, milestones: List[Dict], goal_title: str) -> Dict:
        """Identify prerequisite dependency chains"""
        return self.prerequisite_analyzer.analyze_prerequisite_chains(milestones, goal_title)
        
    def fill_identified_gaps(self, gaps: Dict, roadmap_context: Dict) -> Dict:
        """Generate comprehensive gap-filling strategy"""
        filling_strategy = {
            "gap_types": gaps.get("gap_types", []),
            "suggested_milestones": [],
            "prerequisite_chains": [],
            "priority_order": [],
            "estimated_impact": {}
        }
        
        # Generate milestone suggestions
        suggested_milestones = self.suggest_missing_milestones(gaps, roadmap_context)
        filling_strategy["suggested_milestones"] = suggested_milestones
        
        # Analyze prerequisite needs
        if "milestones" in roadmap_context:
            prereq_analysis = self.identify_prerequisite_chains(
                roadmap_context["milestones"], 
                roadmap_context.get("goal_title", "")
            )
            filling_strategy["prerequisite_chains"] = prereq_analysis.get("chains", [])
            
        # Prioritize gap-filling actions
        filling_strategy["priority_order"] = self._prioritize_gap_filling(
            filling_strategy["suggested_milestones"], 
            filling_strategy["prerequisite_chains"]
        )
        
        return filling_strategy
        
    def _prioritize_gap_filling(self, milestones: List[Dict], chains: List[Dict]) -> List[Dict]:
        """Prioritize gap-filling actions by importance and dependencies"""
        priorities = []
        
        for milestone in milestones:
            priority_score = milestone.get("importance", 5)
            
            # Boost priority if milestone is part of prerequisite chain
            for chain in chains:
                if milestone.get("id") in chain.get("milestone_ids", []):
                    priority_score += 2
                    
            priorities.append({
                "milestone": milestone,
                "priority_score": priority_score,
                "action": "add_milestone"
            })
            
        # Sort by priority score (highest first)
        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return priorities


class GapDetector:
    """Detects gaps in conversations and roadmaps"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def detect_prerequisites_gaps(self, history: List[Dict], 
                                 current_milestone_context: Dict = None) -> Dict:
        """Analyze user responses to detect missing prerequisites"""
        try:
            # Create enhanced context for gap detection
            gap_context = {
                "milestone_context": current_milestone_context or {},
                "conversation_history": history,
                "analysis_type": "prerequisite_detection"
            }
            
            # Use specialized gap detection prompts
            tasks = ['prerequisite_scanner', 'gap_classifier', 'dependency_mapper']
            
            # Construct queries for gap detection
            queries = self._construct_gap_detection_queries(tasks, history, gap_context)
            
            # Execute queries
            responses = {}
            for task, query in queries.items():
                try:
                    response = self.client.chat.completions.create(**query)
                    responses[task] = response.choices[0].message.content.strip()
                except Exception as e:
                    print(f"Error in {task}: {e}")
                    responses[task] = "{}"
                    
            # Synthesize responses
            return self._synthesize_gap_analysis(responses, current_milestone_context)
            
        except Exception as e:
            print(f"Error in gap detection: {e}")
            return {"gap_detected": False, "error": str(e), "missing_prerequisites": [], "suggested_milestones": [], "confidence": 0.0}
            
    def _construct_gap_detection_queries(self, tasks: List[str], history: List[Dict], 
                                       context: Dict) -> Dict:
        """Construct specialized queries for gap detection"""
        queries = {}
        
        # Prerequisite Scanner Query
        if 'prerequisite_scanner' in tasks:
            queries['prerequisite_scanner'] = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": self._get_prerequisite_scanner_prompt()},
                    {"role": "user", "content": self._format_conversation_for_analysis(history, context)}
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
        # Gap Classifier Query
        if 'gap_classifier' in tasks:
            queries['gap_classifier'] = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": self._get_gap_classifier_prompt()},
                    {"role": "user", "content": self._format_conversation_for_analysis(history, context)}
                ],
                "max_tokens": 400,
                "temperature": 0.3
            }
            
        # Dependency Mapper Query
        if 'dependency_mapper' in tasks:
            queries['dependency_mapper'] = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": self._get_dependency_mapper_prompt()},
                    {"role": "user", "content": self._format_conversation_for_analysis(history, context)}
                ],
                "max_tokens": 600,
                "temperature": 0.3
            }
            
        return queries
        
    def _get_prerequisite_scanner_prompt(self) -> str:
        """Get prompt for prerequisite scanning"""
        return """You are a prerequisite detection expert. Analyze the conversation to identify missing prerequisites or foundational elements that the person might need.

Look for:
- Skills mentioned without foundational knowledge
- Advanced concepts without basic understanding
- Tools/technologies mentioned without prerequisites
- Gaps in logical progression
- Missing educational or experience steps

Return JSON format:
{
    "missing_prerequisites": [
        {
            "type": "skill|knowledge|experience|tool|education",
            "name": "prerequisite name",
            "description": "why it's needed",
            "urgency": "high|medium|low",
            "evidence": "quote from conversation"
        }
    ],
    "confidence": 0.0-1.0
}"""

    def _get_gap_classifier_prompt(self) -> str:
        """Get prompt for gap classification"""
        return """You are a gap classification expert. Analyze the conversation to classify types of gaps in the person's journey.

Gap Types:
- KNOWLEDGE_GAP: Missing theoretical understanding
- SKILL_GAP: Missing practical abilities
- EXPERIENCE_GAP: Missing hands-on experience
- TOOL_GAP: Missing familiarity with tools/technologies
- NETWORK_GAP: Missing connections or mentorship
- CERTIFICATION_GAP: Missing formal credentials
- TEMPORAL_GAP: Wrong timing or sequence
- RESOURCE_GAP: Missing access to resources

Return JSON format:
{
    "gap_types": [
        {
            "type": "gap_type_from_above",
            "severity": "critical|high|medium|low",
            "description": "specific gap description",
            "impact": "how it affects goal achievement"
        }
    ],
    "primary_gap_type": "most important gap type",
    "confidence": 0.0-1.0
}"""

    def _get_dependency_mapper_prompt(self) -> str:
        """Get prompt for dependency mapping"""
        return """You are a dependency mapping expert. Analyze the conversation to map out what dependencies and prerequisite chains are missing.

Return JSON format:
{
    "missing_dependencies": [
        {
            "prerequisite": "what's needed first",
            "dependent": "what depends on it",
            "relationship_type": "hard_prerequisite|soft_prerequisite|helpful_background|enabler",
            "reasoning": "why this dependency exists"
        }
    ],
    "suggested_milestones": [
        {
            "name": "milestone name",
            "type": "skill|experience|project|certification|networking",
            "importance": 1-10,
            "connects_to": "existing milestone it should connect to",
            "reasoning": "why this milestone is needed"
        }
    ],
    "prerequisite_chains": [
        {
            "chain_name": "logical sequence name",
            "milestones": ["step1", "step2", "step3"],
            "total_importance": 1-10
        }
    ]
}"""

    def _format_conversation_for_analysis(self, history: List[Dict], context: Dict) -> str:
        """Format conversation history for gap analysis"""
        formatted = f"ANALYSIS CONTEXT:\n"
        formatted += f"Milestone Context: {json.dumps(context.get('milestone_context', {}), indent=2)}\n\n"
        
        formatted += "CONVERSATION HISTORY:\n"
        for i, message in enumerate(history[-10:]):  # Last 10 messages
            role = message.get('role', message.get('type', 'unknown'))
            content = message.get('content', '')
            formatted += f"{role.upper()}: {content}\n"
            
        return formatted
        
    def _synthesize_gap_analysis(self, agent_responses: Dict, milestone_context: Dict = None) -> Dict:
        """Synthesize responses from multiple gap detection agents"""
        synthesis = {
            "gap_detected": False,
            "gap_types": [],
            "missing_prerequisites": [],
            "suggested_milestones": [],
            "prerequisite_chains": [],
            "confidence": 0.0,
            "raw_responses": agent_responses
        }
        
        try:
            # Process prerequisite scanner results
            if 'prerequisite_scanner' in agent_responses:
                try:
                    prereq_data = json.loads(agent_responses['prerequisite_scanner'])
                    synthesis["missing_prerequisites"] = prereq_data.get("missing_prerequisites", [])
                except json.JSONDecodeError:
                    print("Failed to parse prerequisite scanner response")
                    synthesis["missing_prerequisites"] = []
                
            # Process gap classifier results
            if 'gap_classifier' in agent_responses:
                try:
                    gap_data = json.loads(agent_responses['gap_classifier'])
                    synthesis["gap_types"] = gap_data.get("gap_types", [])
                except json.JSONDecodeError:
                    print("Failed to parse gap classifier response")
                    synthesis["gap_types"] = []
                
            # Process dependency mapper results
            if 'dependency_mapper' in agent_responses:
                try:
                    dep_data = json.loads(agent_responses['dependency_mapper'])
                    synthesis["suggested_milestones"] = dep_data.get("suggested_milestones", [])
                    synthesis["prerequisite_chains"] = dep_data.get("prerequisite_chains", [])
                except json.JSONDecodeError:
                    print("Failed to parse dependency mapper response")
                    synthesis["suggested_milestones"] = []
                    synthesis["prerequisite_chains"] = []
                
            # Determine if gaps were detected
            synthesis["gap_detected"] = (
                len(synthesis["missing_prerequisites"]) > 0 or
                len(synthesis["gap_types"]) > 0 or
                len(synthesis["suggested_milestones"]) > 0
            )
            
            # Calculate overall confidence
            confidences = []
            for response_key in ['prerequisite_scanner', 'gap_classifier', 'dependency_mapper']:
                if response_key in agent_responses:
                    try:
                        data = json.loads(agent_responses[response_key])
                        confidences.append(data.get("confidence", 0.5))
                    except:
                        pass
                        
            synthesis["confidence"] = sum(confidences) / len(confidences) if confidences else 0.5
            
        except Exception as e:
            print(f"Error synthesizing gap analysis: {e}")
            synthesis["error"] = str(e)
            
        return synthesis


class PatternAnalyzer:
    """Analyzes conversation patterns for gap identification"""
    
    def __init__(self):
        self.skip_patterns = {
            'frequent_skips': re.compile(r'\b(skip|pass|next|don\'t know|not sure)\b', re.IGNORECASE),
            'vague_responses': re.compile(r'\b(maybe|perhaps|kind of|sort of|I guess)\b', re.IGNORECASE),
            'deflection': re.compile(r'\b(anyway|whatever|moving on|different topic)\b', re.IGNORECASE)
        }
        
    def analyze_gap_patterns(self, history: List[Dict], gap_type: str = "comprehensive") -> Dict:
        """Analyze conversation patterns to identify specific gap types"""
        patterns = {
            "skip_frequency": self._analyze_skip_patterns(history),
            "response_quality": self._analyze_response_quality(history),
            "topic_coverage": self._analyze_topic_coverage(history),
            "engagement_level": self._analyze_engagement_level(history)
        }
        
        # Generate insights from patterns
        insights = self._generate_pattern_insights(patterns)
        
        return {
            "analysis_complete": True,
            "patterns": patterns,
            "insights": insights,
            "recommended_actions": self._recommend_actions_from_patterns(patterns)
        }
        
    def _analyze_skip_patterns(self, history: List[Dict]) -> Dict:
        """Analyze how often user skips questions"""
        user_messages = [msg for msg in history if msg.get('role') == 'user' or msg.get('type') == 'answer']
        
        skip_count = 0
        total_count = len(user_messages)
        
        for msg in user_messages:
            content = msg.get('content', '').lower()
            if self.skip_patterns['frequent_skips'].search(content):
                skip_count += 1
                
        return {
            "skip_frequency": skip_count / total_count if total_count > 0 else 0,
            "total_skips": skip_count,
            "total_responses": total_count
        }
        
    def _analyze_response_quality(self, history: List[Dict]) -> Dict:
        """Analyze quality and depth of responses"""
        user_messages = [msg for msg in history if msg.get('role') == 'user' or msg.get('type') == 'answer']
        
        vague_count = 0
        short_count = 0
        detailed_count = 0
        
        for msg in user_messages:
            content = msg.get('content', '')
            
            if self.skip_patterns['vague_responses'].search(content):
                vague_count += 1
            elif len(content.split()) < 5:
                short_count += 1
            elif len(content.split()) > 20:
                detailed_count += 1
                
        total = len(user_messages)
        
        return {
            "vague_percentage": vague_count / total if total > 0 else 0,
            "short_percentage": short_count / total if total > 0 else 0,
            "detailed_percentage": detailed_count / total if total > 0 else 0,
            "average_length": sum(len(msg.get('content', '').split()) for msg in user_messages) / total if total > 0 else 0
        }
        
    def _analyze_topic_coverage(self, history: List[Dict]) -> Dict:
        """Analyze how well different topics are covered"""
        # Simple topic analysis based on keywords
        topics = {
            "technical": ['code', 'programming', 'software', 'algorithm', 'technical'],
            "experience": ['work', 'job', 'project', 'experience', 'internship'],
            "education": ['school', 'course', 'degree', 'learn', 'study'],
            "skills": ['skill', 'ability', 'knowledge', 'expertise', 'proficient']
        }
        
        topic_coverage = {}
        for topic, keywords in topics.items():
            coverage_count = 0
            for msg in history:
                content = msg.get('content', '').lower()
                if any(keyword in content for keyword in keywords):
                    coverage_count += 1
            topic_coverage[topic] = coverage_count
            
        return topic_coverage
        
    def _analyze_engagement_level(self, history: List[Dict]) -> Dict:
        """Analyze user engagement level"""
        user_messages = [msg for msg in history if msg.get('role') == 'user' or msg.get('type') == 'answer']
        
        if not user_messages:
            return {"engagement_score": 0, "indicators": []}
            
        # Calculate engagement indicators
        avg_length = sum(len(msg.get('content', '').split()) for msg in user_messages) / len(user_messages)
        question_count = sum(1 for msg in user_messages if '?' in msg.get('content', ''))
        enthusiasm_words = sum(1 for msg in user_messages 
                             if any(word in msg.get('content', '').lower() 
                                   for word in ['excited', 'love', 'passionate', 'interested', 'amazing']))
        
        engagement_score = min(1.0, (avg_length / 15) + (question_count / len(user_messages)) + (enthusiasm_words / len(user_messages)))
        
        return {
            "engagement_score": engagement_score,
            "average_response_length": avg_length,
            "questions_asked": question_count,
            "enthusiasm_indicators": enthusiasm_words
        }
        
    def _generate_pattern_insights(self, patterns: Dict) -> List[str]:
        """Generate insights from pattern analysis"""
        insights = []
        
        # Skip pattern insights
        skip_freq = patterns.get("skip_frequency", {}).get("skip_frequency", 0)
        if skip_freq > 0.3:
            insights.append("High skip frequency suggests possible knowledge gaps or discomfort with topics")
            
        # Response quality insights
        quality = patterns.get("response_quality", {})
        if quality.get("vague_percentage", 0) > 0.4:
            insights.append("Many vague responses indicate uncertainty or lack of specific knowledge")
            
        # Engagement insights
        engagement = patterns.get("engagement_level", {})
        if engagement.get("engagement_score", 0) < 0.3:
            insights.append("Low engagement suggests need for more motivating or relevant topics")
            
        return insights
        
    def _recommend_actions_from_patterns(self, patterns: Dict) -> List[Dict]:
        """Recommend actions based on pattern analysis"""
        actions = []
        
        skip_freq = patterns.get("skip_frequency", {}).get("skip_frequency", 0)
        if skip_freq > 0.3:
            actions.append({
                "action": "provide_foundational_support",
                "description": "Offer basic explanations and prerequisite information",
                "priority": "high"
            })
            
        quality = patterns.get("response_quality", {})
        if quality.get("vague_percentage", 0) > 0.4:
            actions.append({
                "action": "ask_specific_questions",
                "description": "Use more specific, concrete questions to elicit detailed responses",
                "priority": "medium"
            })
            
        return actions


class MilestoneSuggester:
    """Suggests milestones to fill identified gaps"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def generate_milestone_suggestions(self, gaps: Dict, context: Dict) -> List[Dict]:
        """Generate milestone suggestions based on detected gaps"""
        try:
            prompt = self._create_milestone_suggestion_prompt(gaps, context)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a career development expert specializing in creating milestone suggestions to fill gaps in professional development paths."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.4
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            suggestions = self._parse_milestone_suggestions(response_text)
            
            return suggestions
            
        except Exception as e:
            print(f"Error generating milestone suggestions: {e}")
            return []
            
    def _create_milestone_suggestion_prompt(self, gaps: Dict, context: Dict) -> str:
        """Create prompt for milestone suggestion"""
        prompt = f"""Based on the following gap analysis, suggest specific milestones to fill the identified gaps.

GAP ANALYSIS:
{json.dumps(gaps, indent=2)}

CONTEXT:
{json.dumps(context, indent=2)}

For each gap, suggest 1-3 specific, actionable milestones. Return in JSON format:
{{
    "milestone_suggestions": [
        {{
            "name": "specific milestone name",
            "type": "skill|experience|project|certification|networking|education",
            "addresses_gap": "which gap this addresses",
            "importance": 1-10,
            "estimated_time": "time estimate",
            "prerequisites": ["list of prerequisites"],
            "description": "detailed description",
            "success_criteria": "how to know it's completed"
        }}
    ]
}}

Focus on:
- Practical, achievable milestones
- Clear connection to identified gaps
- Logical prerequisite relationships
- Measurable success criteria"""

        return prompt
        
    def _parse_milestone_suggestions(self, response_text: str) -> List[Dict]:
        """Parse milestone suggestions from response"""
        try:
            # Try to parse as JSON
            if response_text.startswith('{'):
                data = json.loads(response_text)
                return data.get("milestone_suggestions", [])
            else:
                # Fallback: parse structured text
                return self._parse_text_suggestions(response_text)
                
        except Exception as e:
            print(f"Error parsing milestone suggestions: {e}")
            return []
            
    def _parse_text_suggestions(self, text: str) -> List[Dict]:
        """Fallback parser for text-based suggestions"""
        suggestions = []
        
        # Simple regex-based parsing
        milestone_pattern = r'(?:Milestone|Suggestion)\s*\d*:?\s*(.+?)(?=Milestone|Suggestion|\n\n|$)'
        matches = re.findall(milestone_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for i, match in enumerate(matches):
            suggestions.append({
                "name": match.strip().split('\n')[0][:100],
                "type": "general",
                "importance": 5,
                "description": match.strip(),
                "id": f"suggested_{i}"
            })
            
        return suggestions


class PrerequisiteAnalyzer:
    """Analyzes prerequisite chains and dependencies"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def analyze_prerequisite_chains(self, milestones: List[Dict], goal_title: str) -> Dict:
        """Analyze prerequisite chains in milestone list"""
        try:
            prompt = self._create_prerequisite_analysis_prompt(milestones, goal_title)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing prerequisite dependencies in career development paths."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content.strip()
            return self._parse_prerequisite_analysis(response_text)
            
        except Exception as e:
            print(f"Error analyzing prerequisite chains: {e}")
            return {"chains": [], "missing_links": []}
            
    def _create_prerequisite_analysis_prompt(self, milestones: List[Dict], goal_title: str) -> str:
        """Create prompt for prerequisite analysis"""
        milestone_list = []
        for milestone in milestones:
            milestone_list.append({
                "id": milestone.get("id", ""),
                "name": milestone.get("name", ""),
                "score": milestone.get("score", 5)
            })
            
        prompt = f"""Analyze the prerequisite chains for achieving the goal: "{goal_title}"

CURRENT MILESTONES:
{json.dumps(milestone_list, indent=2)}

Identify:
1. Logical prerequisite chains (what must come before what)
2. Missing prerequisite links
3. Gaps in the progression

Return JSON format:
{{
    "chains": [
        {{
            "name": "chain description",
            "milestone_sequence": ["milestone_id1", "milestone_id2", "milestone_id3"],
            "strength": "strong|medium|weak",
            "reasoning": "why this chain is important"
        }}
    ],
    "missing_links": [
        {{
            "between": ["milestone_id1", "milestone_id2"],
            "missing_prerequisite": "what's missing",
            "importance": 1-10
        }}
    ],
    "recommendations": ["list of recommendations"]
}}"""

        return prompt
        
    def _parse_prerequisite_analysis(self, response_text: str) -> Dict:
        """Parse prerequisite analysis response"""
        try:
            if response_text.startswith('{'):
                return json.loads(response_text)
            else:
                # Fallback parsing
                return {"chains": [], "missing_links": [], "recommendations": []}
        except Exception as e:
            print(f"Error parsing prerequisite analysis: {e}")
            return {"chains": [], "missing_links": [], "recommendations": []}
