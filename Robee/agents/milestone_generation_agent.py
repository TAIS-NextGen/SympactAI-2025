"""
Milestone Generation Agent - Generates new milestones from analysis and conversation patterns
"""
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class MilestoneSuggestion:
    """Data class for milestone suggestions"""
    name: str
    description: str
    importance_score: int
    suggested_parent: str
    milestone_type: str
    resources: List[str]
    estimated_timeline: str
    confidence: float

class MilestoneGenerationAgent:
    """
    Primary Responsibilities:
    - Generate new milestones from conversation analysis
    - Parse AI-generated milestone suggestions
    - Classify milestone taxonomy and importance
    - Suggest milestone connections and dependencies
    """
    
    def __init__(self, api_key: str = None):
        self.milestone_parser = MilestoneParser()
        self.taxonomy_classifier = TaxonomyClassifier()
        self.importance_analyzer = ImportanceAnalyzer()
        self.connection_suggester = ConnectionSuggester()
        
        # Milestone patterns for parsing
        self.milestone_patterns = {
            "suggestion_indicators": [
                r"suggest.*milestone",
                r"add.*milestone", 
                r"missing.*step",
                r"need.*to.*complete",
                r"prerequisite.*for"
            ],
            "milestone_markers": [
                r"milestone:\s*(.+)",
                r"step:\s*(.+)",
                r"goal:\s*(.+)",
                r"objective:\s*(.+)"
            ]
        }
        
    def parse_milestone_suggestion(self, agent_message: str, context: Dict = None) -> Optional[MilestoneSuggestion]:
        """Parse milestone suggestion from AI agent message"""
        
        suggestion = self.milestone_parser.extract_milestone_from_text(agent_message)
        
        if not suggestion:
            return None
            
        # Classify and enhance the suggestion
        enhanced_suggestion = self._enhance_milestone_suggestion(suggestion, context)
        
        return enhanced_suggestion
        
    def generate_milestone_from_gap(self, gap_analysis: Dict, conversation_context: Dict) -> MilestoneSuggestion:
        """Generate milestone suggestion from identified gap"""
        
        gap_type = gap_analysis.get("gap_type", "unknown")
        gap_description = gap_analysis.get("description", "")
        
        # Generate milestone based on gap type
        milestone_data = self._generate_milestone_from_gap_type(gap_type, gap_description, conversation_context)
        
        # Create structured suggestion
        suggestion = MilestoneSuggestion(
            name=milestone_data["name"],
            description=milestone_data["description"],
            importance_score=milestone_data["importance_score"],
            suggested_parent=milestone_data["suggested_parent"],
            milestone_type=milestone_data["milestone_type"],
            resources=milestone_data["resources"],
            estimated_timeline=milestone_data["estimated_timeline"],
            confidence=milestone_data["confidence"]
        )
        
        return suggestion
        
    def classify_milestone_taxonomy(self, milestone_name: str, milestone_description: str = "") -> Dict[str, Any]:
        """Classify milestone into taxonomy categories"""
        
        classification = self.taxonomy_classifier.classify_milestone(milestone_name, milestone_description)
        
        return {
            "primary_category": classification["primary_category"],
            "secondary_categories": classification["secondary_categories"],
            "skill_domains": classification["skill_domains"],
            "complexity_level": classification["complexity_level"],
            "milestone_phase": classification["milestone_phase"]
        }
        
    def calculate_milestone_importance(self, milestone_suggestion: MilestoneSuggestion, 
                                     roadmap_context: Dict) -> int:
        """Calculate importance score for milestone suggestion"""
        
        importance_score = self.importance_analyzer.calculate_importance(
            milestone_suggestion, roadmap_context
        )
        
        return min(max(importance_score, 1), 10)  # Ensure score is 1-10
        
    def suggest_milestone_connections(self, new_milestone: MilestoneSuggestion,
                                    existing_milestones: List[Dict]) -> List[Dict]:
        """Suggest connections between new milestone and existing ones"""
        
        connections = self.connection_suggester.find_connections(
            new_milestone, existing_milestones
        )
        
        return connections
        
    def generate_milestone_batch(self, conversation_history: List[Dict], 
                               goal_context: Dict, num_suggestions: int = 3) -> List[MilestoneSuggestion]:
        """Generate batch of milestone suggestions from conversation"""
        
        # Analyze conversation for patterns
        conversation_analysis = self._analyze_conversation_patterns(conversation_history)
        
        # Generate suggestions based on patterns
        suggestions = []
        
        for pattern in conversation_analysis["identified_patterns"][:num_suggestions]:
            suggestion = self._generate_milestone_from_pattern(pattern, goal_context)
            if suggestion:
                suggestions.append(suggestion)
                
        return suggestions
        
    def refine_milestone_suggestion(self, suggestion: MilestoneSuggestion,
                                  user_feedback: Dict) -> MilestoneSuggestion:
        """Refine milestone suggestion based on user feedback"""
        
        refined_suggestion = MilestoneSuggestion(
            name=user_feedback.get("name", suggestion.name),
            description=user_feedback.get("description", suggestion.description),
            importance_score=user_feedback.get("importance_score", suggestion.importance_score),
            suggested_parent=user_feedback.get("suggested_parent", suggestion.suggested_parent),
            milestone_type=suggestion.milestone_type,
            resources=user_feedback.get("resources", suggestion.resources),
            estimated_timeline=user_feedback.get("estimated_timeline", suggestion.estimated_timeline),
            confidence=suggestion.confidence
        )
        
        return refined_suggestion
        
    def _enhance_milestone_suggestion(self, raw_suggestion: Dict, context: Dict = None) -> MilestoneSuggestion:
        """Enhance raw milestone suggestion with additional metadata"""
        
        # Extract basic information
        name = raw_suggestion.get("name", "Untitled Milestone")
        description = raw_suggestion.get("description", "")
        
        # Classify taxonomy
        taxonomy = self.classify_milestone_taxonomy(name, description)
        
        # Calculate importance
        base_importance = raw_suggestion.get("importance_score", 5)
        
        # Suggest parent connection
        suggested_parent = raw_suggestion.get("suggested_parent", "")
        
        # Estimate resources and timeline
        resources = self._estimate_milestone_resources(name, description, taxonomy)
        timeline = self._estimate_milestone_timeline(name, description, taxonomy)
        
        # Calculate confidence
        confidence = self._calculate_suggestion_confidence(raw_suggestion, context)
        
        return MilestoneSuggestion(
            name=name,
            description=description,
            importance_score=base_importance,
            suggested_parent=suggested_parent,
            milestone_type=taxonomy["primary_category"],
            resources=resources,
            estimated_timeline=timeline,
            confidence=confidence
        )
        
    def _generate_milestone_from_gap_type(self, gap_type: str, gap_description: str, 
                                        context: Dict) -> Dict[str, Any]:
        """Generate milestone data based on gap type"""
        
        milestone_templates = {
            "prerequisite_gap": {
                "name_template": "Complete {prerequisite} before {target}",
                "description_template": "Essential prerequisite step for {target_goal}",
                "importance_score": 8,
                "milestone_type": "prerequisite",
                "estimated_timeline": "2-4 weeks"
            },
            "skill_gap": {
                "name_template": "Develop {skill} skills",
                "description_template": "Build foundational skills in {skill_area}",
                "importance_score": 7,
                "milestone_type": "skill_development",
                "estimated_timeline": "4-8 weeks"
            },
            "resource_gap": {
                "name_template": "Acquire {resource} resources",
                "description_template": "Obtain necessary resources for {goal_area}",
                "importance_score": 6,
                "milestone_type": "resource_acquisition",
                "estimated_timeline": "1-3 weeks"
            }
        }
        
        template = milestone_templates.get(gap_type, milestone_templates["skill_gap"])
        
        # Fill template with context
        name = template["name_template"]
        description = template["description_template"]
        
        # Extract specifics from gap description
        if gap_description:
            # Simple keyword extraction for demonstration
            keywords = gap_description.lower().split()
            relevant_keywords = [word for word in keywords if len(word) > 3]
            
            if relevant_keywords:
                name = name.replace("{prerequisite}", relevant_keywords[0])
                name = name.replace("{skill}", relevant_keywords[0])
                name = name.replace("{resource}", relevant_keywords[0])
                name = name.replace("{target}", context.get("goal_title", "goal"))
                
        return {
            "name": name,
            "description": description,
            "importance_score": template["importance_score"],
            "suggested_parent": context.get("current_milestone", ""),
            "milestone_type": template["milestone_type"],
            "resources": self._estimate_milestone_resources(name, description, {"primary_category": template["milestone_type"]}),
            "estimated_timeline": template["estimated_timeline"],
            "confidence": 0.7
        }
        
    def _analyze_conversation_patterns(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation for milestone generation patterns"""
        
        patterns = []
        
        for message in conversation_history:
            content = message.get("content", "").lower()
            
            # Look for patterns that suggest milestones
            if any(indicator in content for indicator in ["need to", "should", "must", "important to"]):
                patterns.append({
                    "type": "action_pattern",
                    "content": content,
                    "confidence": 0.6
                })
                
            if any(skill in content for skill in ["learn", "practice", "study", "master"]):
                patterns.append({
                    "type": "skill_pattern", 
                    "content": content,
                    "confidence": 0.7
                })
                
            if any(resource in content for resource in ["get", "obtain", "acquire", "buy"]):
                patterns.append({
                    "type": "resource_pattern",
                    "content": content,
                    "confidence": 0.5
                })
                
        return {
            "identified_patterns": patterns,
            "pattern_count": len(patterns),
            "confidence_score": sum(p["confidence"] for p in patterns) / len(patterns) if patterns else 0
        }
        
    def _generate_milestone_from_pattern(self, pattern: Dict, goal_context: Dict) -> Optional[MilestoneSuggestion]:
        """Generate milestone suggestion from conversation pattern"""
        
        pattern_type = pattern["type"]
        content = pattern["content"]
        
        if pattern_type == "skill_pattern":
            # Extract skill from content
            skill_keywords = ["learn", "practice", "study", "master"]
            skill_text = ""
            
            for keyword in skill_keywords:
                if keyword in content:
                    start_idx = content.find(keyword)
                    # Extract text after the keyword
                    remaining = content[start_idx + len(keyword):].strip()
                    skill_text = remaining.split()[0] if remaining.split() else "skill"
                    break
                    
            if skill_text:
                return MilestoneSuggestion(
                    name=f"Develop {skill_text} skills",
                    description=f"Build competency in {skill_text}",
                    importance_score=6,
                    suggested_parent="",
                    milestone_type="skill_development",
                    resources=["training materials", "practice exercises"],
                    estimated_timeline="4-6 weeks",
                    confidence=pattern["confidence"]
                )
                
        elif pattern_type == "action_pattern":
            # Extract action from content
            action_text = content.split("need to")[-1].split("should")[-1].strip()
            action_text = action_text.split(".")[0] if "." in action_text else action_text
            
            if action_text:
                return MilestoneSuggestion(
                    name=f"Complete: {action_text}",
                    description=f"Action item: {action_text}",
                    importance_score=7,
                    suggested_parent="",
                    milestone_type="action_item",
                    resources=["time", "focus"],
                    estimated_timeline="1-2 weeks",
                    confidence=pattern["confidence"]
                )
                
        return None
        
    def _estimate_milestone_resources(self, name: str, description: str, taxonomy: Dict) -> List[str]:
        """Estimate resources needed for milestone"""
        
        resources = ["time", "focus"]  # Base resources
        
        category = taxonomy.get("primary_category", "")
        name_lower = name.lower()
        desc_lower = description.lower()
        
        # Add category-specific resources
        if "skill" in category or any(word in name_lower for word in ["learn", "study", "practice"]):
            resources.extend(["learning materials", "practice exercises", "mentor guidance"])
            
        if "technical" in category or any(word in name_lower for word in ["code", "program", "develop"]):
            resources.extend(["development tools", "technical documentation", "testing environment"])
            
        if "business" in category or any(word in name_lower for word in ["business", "strategy", "plan"]):
            resources.extend(["market research", "business planning tools", "industry connections"])
            
        if any(word in name_lower for word in ["certification", "course", "training"]):
            resources.extend(["certification fees", "training materials", "study time"])
            
        return list(set(resources))  # Remove duplicates
        
    def _estimate_milestone_timeline(self, name: str, description: str, taxonomy: Dict) -> str:
        """Estimate timeline for milestone completion"""
        
        category = taxonomy.get("primary_category", "")
        complexity = taxonomy.get("complexity_level", "medium")
        name_lower = name.lower()
        
        # Base timeline estimation
        if complexity == "low":
            base_timeline = "1-2 weeks"
        elif complexity == "high":
            base_timeline = "8-12 weeks"
        else:
            base_timeline = "3-6 weeks"
            
        # Adjust based on content
        if any(word in name_lower for word in ["certification", "degree", "course"]):
            base_timeline = "2-6 months"
        elif any(word in name_lower for word in ["project", "build", "create", "develop"]):
            base_timeline = "4-8 weeks"
        elif any(word in name_lower for word in ["research", "study", "analyze"]):
            base_timeline = "2-4 weeks"
            
        return base_timeline
        
    def _calculate_suggestion_confidence(self, raw_suggestion: Dict, context: Dict = None) -> float:
        """Calculate confidence score for milestone suggestion"""
        
        confidence_factors = []
        
        # Name quality
        name = raw_suggestion.get("name", "")
        if len(name) > 5 and not name.startswith("Untitled"):
            confidence_factors.append(0.3)
        else:
            confidence_factors.append(0.1)
            
        # Description quality
        description = raw_suggestion.get("description", "")
        if len(description) > 10:
            confidence_factors.append(0.2)
        else:
            confidence_factors.append(0.1)
            
        # Context relevance
        if context and context.get("goal_title"):
            goal_title = context["goal_title"].lower()
            name_lower = name.lower()
            if any(word in name_lower for word in goal_title.split()):
                confidence_factors.append(0.3)
            else:
                confidence_factors.append(0.2)
        else:
            confidence_factors.append(0.1)
            
        # Parent connection
        if raw_suggestion.get("suggested_parent"):
            confidence_factors.append(0.2)
        else:
            confidence_factors.append(0.1)
            
        return min(sum(confidence_factors), 1.0)


class MilestoneParser:
    """Parses milestone suggestions from text"""
    
    def __init__(self):
        self.milestone_indicators = [
            r"milestone:?\s*(.+)",
            r"step:?\s*(.+)",
            r"objective:?\s*(.+)",
            r"goal:?\s*(.+)",
            r"need to:?\s*(.+)",
            r"should:?\s*(.+)"
        ]
        
    def extract_milestone_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract milestone information from text"""
        
        # Try to match milestone patterns
        for pattern in self.milestone_indicators:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                milestone_text = match.group(1).strip()
                
                # Clean up the text
                milestone_text = self._clean_milestone_text(milestone_text)
                
                if len(milestone_text) > 3:  # Minimum length check
                    return {
                        "name": milestone_text,
                        "description": f"Milestone: {milestone_text}",
                        "importance_score": 5,
                        "suggested_parent": "",
                        "extracted_from": text[:100] + "..." if len(text) > 100 else text
                    }
                    
        return None
        
    def _clean_milestone_text(self, text: str) -> str:
        """Clean and normalize milestone text"""
        
        # Remove common prefixes/suffixes
        text = re.sub(r'^(to\s+|that\s+)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'[.!?]+$', '', text)
        
        # Capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
            
        return text.strip()


class TaxonomyClassifier:
    """Classifies milestones into taxonomy categories"""
    
    def __init__(self):
        self.category_keywords = {
            "skill_development": ["learn", "study", "practice", "master", "skill", "training"],
            "technical": ["code", "program", "develop", "build", "implement", "technical"],
            "business": ["business", "strategy", "plan", "market", "revenue", "customer"],
            "creative": ["design", "create", "write", "art", "creative", "content"],
            "research": ["research", "analyze", "investigate", "study", "explore"],
            "networking": ["network", "connect", "meet", "relationship", "collaboration"],
            "certification": ["certification", "certificate", "license", "accreditation"],
            "project": ["project", "initiative", "campaign", "program", "launch"],
            "resource_acquisition": ["acquire", "obtain", "get", "purchase", "resource"]
        }
        
        self.complexity_indicators = {
            "high": ["complex", "advanced", "comprehensive", "complete", "full", "entire"],
            "low": ["simple", "basic", "quick", "easy", "small", "minor"]
        }
        
    def classify_milestone(self, name: str, description: str = "") -> Dict[str, Any]:
        """Classify milestone into categories"""
        
        text = f"{name} {description}".lower()
        
        # Find primary category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
                
        primary_category = max(category_scores.items(), key=lambda x: x[1])[0] if category_scores else "general"
        
        # Find secondary categories
        secondary_categories = [cat for cat, score in category_scores.items() 
                              if cat != primary_category and score > 0]
        
        # Determine complexity
        complexity_level = "medium"  # default
        for level, indicators in self.complexity_indicators.items():
            if any(indicator in text for indicator in indicators):
                complexity_level = level
                break
                
        # Determine milestone phase
        milestone_phase = self._determine_milestone_phase(text)
        
        # Extract skill domains
        skill_domains = self._extract_skill_domains(text)
        
        return {
            "primary_category": primary_category,
            "secondary_categories": secondary_categories,
            "skill_domains": skill_domains,
            "complexity_level": complexity_level,
            "milestone_phase": milestone_phase
        }
        
    def _determine_milestone_phase(self, text: str) -> str:
        """Determine which phase of development this milestone represents"""
        
        if any(word in text for word in ["learn", "study", "research", "explore"]):
            return "learning"
        elif any(word in text for word in ["plan", "design", "prepare", "setup"]):
            return "planning"
        elif any(word in text for word in ["build", "create", "develop", "implement"]):
            return "execution"
        elif any(word in text for word in ["test", "validate", "verify", "review"]):
            return "validation"
        elif any(word in text for word in ["launch", "deploy", "release", "deliver"]):
            return "deployment"
        else:
            return "general"
            
    def _extract_skill_domains(self, text: str) -> List[str]:
        """Extract skill domains from milestone text"""
        
        skill_domains = []
        
        domain_keywords = {
            "programming": ["programming", "coding", "software", "development"],
            "design": ["design", "ui", "ux", "visual", "graphics"],
            "business": ["business", "management", "strategy", "leadership"],
            "marketing": ["marketing", "sales", "promotion", "advertising"],
            "finance": ["finance", "accounting", "budget", "financial"],
            "communication": ["communication", "writing", "presentation", "speaking"],
            "project_management": ["project", "management", "coordination", "planning"],
            "data_analysis": ["data", "analysis", "analytics", "statistics"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text for keyword in keywords):
                skill_domains.append(domain)
                
        return skill_domains


class ImportanceAnalyzer:
    """Analyzes and calculates milestone importance scores"""
    
    def __init__(self):
        pass
        
    def calculate_importance(self, milestone_suggestion: MilestoneSuggestion, 
                           roadmap_context: Dict) -> int:
        """Calculate importance score for milestone"""
        
        base_score = milestone_suggestion.importance_score
        
        # Adjust based on various factors
        adjustments = []
        
        # Taxonomy-based adjustments
        if milestone_suggestion.milestone_type in ["prerequisite", "foundation"]:
            adjustments.append(2)  # Prerequisites are important
            
        if milestone_suggestion.milestone_type in ["skill_development", "certification"]:
            adjustments.append(1)  # Skills are valuable
            
        # Context-based adjustments
        goal_title = roadmap_context.get("goal_title", "").lower()
        milestone_name = milestone_suggestion.name.lower()
        
        # If milestone name relates to goal, increase importance
        goal_words = set(goal_title.split())
        milestone_words = set(milestone_name.split())
        
        if goal_words.intersection(milestone_words):
            adjustments.append(1)
            
        # Confidence-based adjustment
        if milestone_suggestion.confidence > 0.8:
            adjustments.append(1)
        elif milestone_suggestion.confidence < 0.5:
            adjustments.append(-1)
            
        # Calculate final score
        final_score = base_score + sum(adjustments)
        
        return min(max(final_score, 1), 10)  # Clamp to 1-10 range


class ConnectionSuggester:
    """Suggests connections between milestones"""
    
    def __init__(self):
        pass
        
    def find_connections(self, new_milestone: MilestoneSuggestion,
                        existing_milestones: List[Dict]) -> List[Dict]:
        """Find potential connections for new milestone"""
        
        connections = []
        
        for existing in existing_milestones:
            connection_strength = self._calculate_connection_strength(
                new_milestone, existing
            )
            
            if connection_strength > 0.3:  # Minimum threshold
                connection_type = self._determine_connection_type(
                    new_milestone, existing
                )
                
                connections.append({
                    "target_milestone": existing.get("id", existing.get("name", "")),
                    "connection_type": connection_type,
                    "strength": connection_strength,
                    "rationale": self._generate_connection_rationale(
                        new_milestone, existing, connection_type
                    )
                })
                
        # Sort by strength
        connections.sort(key=lambda x: x["strength"], reverse=True)
        
        return connections[:5]  # Return top 5 connections
        
    def _calculate_connection_strength(self, new_milestone: MilestoneSuggestion,
                                     existing_milestone: Dict) -> float:
        """Calculate strength of connection between milestones"""
        
        new_text = f"{new_milestone.name} {new_milestone.description}".lower()
        existing_text = f"{existing_milestone.get('name', '')} {existing_milestone.get('description', '')}".lower()
        
        # Word overlap
        new_words = set(new_text.split())
        existing_words = set(existing_text.split())
        
        overlap = len(new_words.intersection(existing_words))
        total_words = len(new_words.union(existing_words))
        
        word_similarity = overlap / total_words if total_words > 0 else 0
        
        # Type similarity
        existing_type = existing_milestone.get("type", existing_milestone.get("milestone_type", ""))
        type_similarity = 1.0 if new_milestone.milestone_type == existing_type else 0.3
        
        # Combine factors
        strength = (word_similarity * 0.6) + (type_similarity * 0.4)
        
        return strength
        
    def _determine_connection_type(self, new_milestone: MilestoneSuggestion,
                                 existing_milestone: Dict) -> str:
        """Determine type of connection between milestones"""
        
        new_name = new_milestone.name.lower()
        existing_name = existing_milestone.get("name", "").lower()
        
        # Check for prerequisite relationships
        if any(word in new_name for word in ["before", "prerequisite", "foundation"]):
            return "prerequisite"
            
        # Check for enabling relationships
        if any(word in new_name for word in ["enables", "allows", "leads to"]):
            return "enables"
            
        # Check for skill progression
        if ("basic" in existing_name and "advanced" in new_name) or \
           ("beginner" in existing_name and "intermediate" in new_name):
            return "progression"
            
        # Check for parallel/supporting relationships
        if new_milestone.milestone_type == existing_milestone.get("type", ""):
            return "parallel"
            
        return "related"
        
    def _generate_connection_rationale(self, new_milestone: MilestoneSuggestion,
                                     existing_milestone: Dict, connection_type: str) -> str:
        """Generate rationale for connection"""
        
        rationales = {
            "prerequisite": f"'{existing_milestone.get('name', '')}' should be completed before '{new_milestone.name}'",
            "enables": f"'{existing_milestone.get('name', '')}' enables progress toward '{new_milestone.name}'",
            "progression": f"'{new_milestone.name}' builds upon skills from '{existing_milestone.get('name', '')}'",
            "parallel": f"'{new_milestone.name}' can be worked on alongside '{existing_milestone.get('name', '')}'",
            "related": f"'{new_milestone.name}' is related to '{existing_milestone.get('name', '')}' in scope"
        }
        
        return rationales.get(connection_type, f"Connection between milestones identified")


# Backward compatibility function for parsing milestone suggestions
def parse_new_milestone_suggestion(agent_message: str) -> Optional[Dict[str, Any]]:
    """
    Parse milestone suggestion from AI agent message (backward compatibility)
    
    Args:
        agent_message: Message from AI agent potentially containing milestone suggestion
        
    Returns:
        Dictionary with milestone details if found, None otherwise
    """
    
    # Initialize parser
    parser = MilestoneParser()
    
    # Extract milestone
    suggestion = parser.extract_milestone_from_text(agent_message)
    
    if suggestion:
        # Convert to format expected by existing code
        return {
            "name": suggestion["name"],
            "description": suggestion["description"],
            "importance_score": suggestion["importance_score"],
            "suggested_parent": suggestion["suggested_parent"]
        }
        
    return None
