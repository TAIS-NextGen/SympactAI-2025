"""
CVA Agent (Confounder Variable Agent) - Identifies confounding variables and potential collaborators
"""
import json
import networkx as nx
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

class CVAAgent:
    """
    Primary Responsibilities:
    - Identify potential confounders and collaborators in career roadmaps
    - Analyze external factors that could influence milestone achievement
    - Suggest strategic partnerships and mentorship opportunities
    - Map industry connections and networking opportunities
    """
    
    def __init__(self, api_key: str = None):
        self.confounder_detector = ConfounderDetector()
        self.collaborator_analyzer = CollaboratorAnalyzer()
        self.network_mapper = NetworkMapper()
        self.strategic_partnership_finder = StrategicPartnershipFinder()
        
        # Confounder categories
        self.confounder_types = [
            "technical_mentors",
            "business_partners", 
            "industry_connections",
            "resource_providers",
            "skill_complementors",
            "market_influencers",
            "institutional_supporters"
        ]
        
    def suggest_cofounders(self, graph: nx.DiGraph, goal_title: str, person_name: str) -> Dict[str, Any]:
        """Analyze the causal DAG to suggest potential cofounders and collaborators"""
        
        # Analyze milestone requirements for collaboration opportunities
        milestone_analysis = self.collaborator_analyzer.analyze_milestone_requirements(graph, goal_title)
        
        # Identify collaboration points
        collaboration_points = self.collaborator_analyzer.identify_collaboration_points(
            milestone_analysis, person_name
        )
        
        # Generate cofounder suggestions
        cofounder_suggestions = self.collaborator_analyzer.generate_cofounder_suggestions(
            collaboration_points, goal_title
        )
        
        # Map strategic partnerships
        strategic_partnerships = self.strategic_partnership_finder.find_strategic_partnerships(
            graph, goal_title, person_name
        )
        
        # Analyze network requirements
        network_requirements = self.network_mapper.analyze_network_requirements(
            graph, goal_title
        )
        
        # Format cofounder suggestions for the interface
        formatted_suggestions = []
        for suggestion in cofounder_suggestions:
            # Extract relevant milestones for this suggestion
            relevant_milestones = []
            for point in collaboration_points:
                if any(skill in point.get("skill_gaps", []) for skill in suggestion.get("required_skills", [])):
                    relevant_milestones.append(point.get("milestone", ""))
            
            formatted_suggestion = {
                "cofounder_type": suggestion.get("collaborator_type", "General Collaborator"),
                "cofounder_description": self._generate_cofounder_description(suggestion),
                "target_milestones": relevant_milestones[:3],  # Limit to top 3
                "contribution_type": suggestion.get("collaboration_model", "Strategic partnership"),
                "network_impact": self._calculate_network_impact(suggestion, collaboration_points),
                "collaboration_question": self._generate_collaboration_question(suggestion, goal_title),
                "confidence": suggestion.get("priority", 0.5),
                "required_skills": suggestion.get("required_skills", []),
                "finding_strategy": suggestion.get("finding_strategy", [])
            }
            formatted_suggestions.append(formatted_suggestion)
        
        return {
            "analysis_type": "cofounder_suggestion",
            "goal_title": goal_title,
            "person_name": person_name,
            "cofounder_suggestions": formatted_suggestions,
            "milestone_analysis": milestone_analysis,
            "collaboration_points": collaboration_points,
            "strategic_partnerships": strategic_partnerships,
            "network_requirements": network_requirements,
            "timestamp": datetime.now().isoformat()
        }
        
    def _generate_cofounder_description(self, suggestion: Dict) -> str:
        """Generate a description for a cofounder suggestion"""
        collaborator_type = suggestion.get("collaborator_type", "Collaborator")
        required_skills = suggestion.get("required_skills", [])
        
        if required_skills:
            skills_text = ", ".join(required_skills[:2])
            return f"{collaborator_type} with expertise in {skills_text}"
        else:
            return f"{collaborator_type} to complement your skill set"
    
    def _calculate_network_impact(self, suggestion: Dict, collaboration_points: List[Dict]) -> str:
        """Calculate how the collaboration would impact the network"""
        required_skills = suggestion.get("required_skills", [])
        
        # Count how many collaboration points this addresses
        addressed_points = sum(1 for point in collaboration_points 
                             if any(skill in point.get("skill_gaps", []) for skill in required_skills))
        
        total_points = len(collaboration_points)
        
        if addressed_points >= total_points * 0.7:
            return "High impact - addresses multiple critical gaps in your network"
        elif addressed_points >= total_points * 0.4:
            return "Medium impact - fills important skill and network gaps"
        else:
            return "Focused impact - addresses specific collaboration needs"
    
    def _generate_collaboration_question(self, suggestion: Dict, goal_title: str) -> str:
        """Generate a question to ask the user about this collaboration"""
        collaborator_type = suggestion.get("collaborator_type", "collaborator").lower()
        
        question_templates = {
            "technical": f"Have you considered partnering with a technical expert to accelerate your progress toward '{goal_title}'?",
            "business": f"Would working with a business partner help you achieve '{goal_title}' more effectively?",
            "creative": f"Could collaborating with a creative professional enhance your journey to '{goal_title}'?",
            "marketing": f"Have you thought about partnering with someone skilled in marketing for '{goal_title}'?",
            "mentor": f"Would having a mentor in this field help guide your path to '{goal_title}'?",
            "advisor": f"Could an industry advisor provide valuable insights for achieving '{goal_title}'?"
        }
        
        # Find matching template
        for key, template in question_templates.items():
            if key in collaborator_type:
                return template
        
        # Default question
        return f"Have you considered collaborating with others to achieve '{goal_title}'?"
        
    def identify_confounding_variables(self, milestones: List[Dict], goal_title: str, 
                                     context: Dict = None) -> Dict[str, Any]:
        """Identify external factors that could confound milestone relationships"""
        
        # Detect potential confounders for each milestone
        milestone_confounders = []
        for milestone in milestones:
            confounders = self.confounder_detector.detect_milestone_confounders(
                milestone, goal_title, context
            )
            milestone_confounders.append({
                "milestone": milestone,
                "confounders": confounders
            })
            
        # Identify global confounders affecting multiple milestones
        global_confounders = self.confounder_detector.identify_global_confounders(
            milestones, goal_title, context
        )
        
        # Analyze confounder impact
        impact_analysis = self.confounder_detector.analyze_confounder_impact(
            milestone_confounders, global_confounders
        )
        
        return {
            "analysis_type": "confounder_identification",
            "milestone_confounders": milestone_confounders,
            "global_confounders": global_confounders,
            "impact_analysis": impact_analysis,
            "mitigation_strategies": self._generate_mitigation_strategies(global_confounders),
            "timestamp": datetime.now().isoformat()
        }
        
    def analyze_external_dependencies(self, graph: nx.DiGraph, goal_title: str) -> Dict[str, Any]:
        """Analyze external dependencies and factors outside direct control"""
        
        external_dependencies = []
        
        for node in graph.nodes():
            # Analyze each milestone for external dependencies
            ext_deps = self.confounder_detector.identify_external_dependencies(node, goal_title)
            if ext_deps:
                external_dependencies.append({
                    "milestone": node,
                    "external_dependencies": ext_deps
                })
                
        # Categorize external dependencies
        categorized_deps = self._categorize_external_dependencies(external_dependencies)
        
        # Assess controllability
        controllability_analysis = self._assess_dependency_controllability(categorized_deps)
        
        return {
            "analysis_type": "external_dependencies",
            "external_dependencies": external_dependencies,
            "categorized_dependencies": categorized_deps,
            "controllability_analysis": controllability_analysis,
            "risk_assessment": self._assess_external_risks(categorized_deps)
        }
        
    def map_industry_connections(self, goal_title: str, person_background: Dict = None) -> Dict[str, Any]:
        """Map potential industry connections and networking opportunities"""
        
        # Identify relevant industry domains
        industry_domains = self.network_mapper.identify_industry_domains(goal_title)
        
        # Map connection types for each domain
        connection_mapping = []
        for domain in industry_domains:
            connections = self.network_mapper.map_domain_connections(domain, person_background)
            connection_mapping.append({
                "domain": domain,
                "connections": connections
            })
            
        # Prioritize connections
        prioritized_connections = self.network_mapper.prioritize_connections(
            connection_mapping, goal_title
        )
        
        return {
            "analysis_type": "industry_connections",
            "industry_domains": industry_domains,
            "connection_mapping": connection_mapping,
            "prioritized_connections": prioritized_connections,
            "networking_strategy": self._generate_networking_strategy(prioritized_connections)
        }
        
    def _generate_mitigation_strategies(self, global_confounders: List[Dict]) -> List[Dict]:
        """Generate strategies to mitigate confounding factors"""
        strategies = []
        
        for confounder in global_confounders:
            confounder_type = confounder.get("type", "unknown")
            
            if confounder_type == "market_conditions":
                strategies.append({
                    "confounder": confounder_type,
                    "strategy": "Diversify approach and create market-agnostic milestones",
                    "priority": "high"
                })
            elif confounder_type == "technology_changes":
                strategies.append({
                    "confounder": confounder_type,
                    "strategy": "Focus on fundamental skills and adaptable technologies",
                    "priority": "medium"
                })
            elif confounder_type == "resource_availability":
                strategies.append({
                    "confounder": confounder_type,
                    "strategy": "Develop multiple resource acquisition channels",
                    "priority": "high"
                })
                
        return strategies
        
    def _categorize_external_dependencies(self, external_dependencies: List[Dict]) -> Dict[str, List]:
        """Categorize external dependencies by type"""
        categories = {
            "people": [],
            "technology": [],
            "market": [],
            "regulatory": [],
            "financial": [],
            "institutional": []
        }
        
        for dep_item in external_dependencies:
            milestone = dep_item["milestone"]
            dependencies = dep_item["external_dependencies"]
            
            for dep in dependencies:
                dep_type = dep.get("type", "unknown")
                categories.setdefault(dep_type, []).append({
                    "milestone": milestone,
                    "dependency": dep
                })
                
        return categories
        
    def _assess_dependency_controllability(self, categorized_deps: Dict) -> Dict[str, str]:
        """Assess how controllable each category of dependencies is"""
        controllability = {}
        
        control_mapping = {
            "people": "medium",      # Can influence through networking
            "technology": "high",    # Can learn and adapt
            "market": "low",         # External market forces
            "regulatory": "low",     # Government/institutional
            "financial": "medium",   # Can be influenced through planning
            "institutional": "low"   # Large institutions move slowly
        }
        
        for category, deps in categorized_deps.items():
            if deps:  # Only assess if dependencies exist
                controllability[category] = control_mapping.get(category, "unknown")
                
        return controllability
        
    def _assess_external_risks(self, categorized_deps: Dict) -> Dict[str, Dict]:
        """Assess risks associated with external dependencies"""
        risks = {}
        
        for category, deps in categorized_deps.items():
            if not deps:
                continue
                
            risk_count = len(deps)
            
            if risk_count >= 5:
                risk_level = "high"
            elif risk_count >= 2:
                risk_level = "medium"
            else:
                risk_level = "low"
                
            risks[category] = {
                "risk_level": risk_level,
                "dependency_count": risk_count,
                "mitigation_priority": "high" if risk_level == "high" else "medium"
            }
            
        return risks
        
    def _generate_networking_strategy(self, prioritized_connections: List[Dict]) -> Dict[str, Any]:
        """Generate networking strategy based on connection analysis"""
        
        # Extract high-priority connections
        high_priority = [conn for conn in prioritized_connections if conn.get("priority") == "high"]
        
        strategy = {
            "immediate_focus": high_priority[:3],  # Top 3 high-priority connections
            "medium_term_goals": prioritized_connections[3:8],  # Next 5 connections
            "networking_channels": self._identify_networking_channels(prioritized_connections),
            "timeline": self._create_networking_timeline(prioritized_connections)
        }
        
        return strategy
        
    def _identify_networking_channels(self, connections: List[Dict]) -> List[str]:
        """Identify best channels for networking based on connection types"""
        channels = set()
        
        for conn in connections:
            conn_type = conn.get("type", "")
            
            if "technical" in conn_type.lower():
                channels.add("Technical conferences and meetups")
                channels.add("Open source communities")
            elif "business" in conn_type.lower():
                channels.add("Industry events and networking")
                channels.add("Professional associations")
            elif "academic" in conn_type.lower():
                channels.add("Academic conferences")
                channels.add("Research communities")
                
        return list(channels)
        
    def _create_networking_timeline(self, connections: List[Dict]) -> Dict[str, List]:
        """Create timeline for networking activities"""
        timeline = {
            "immediate": [],    # Next 1-3 months
            "short_term": [],   # 3-6 months
            "medium_term": []   # 6-12 months
        }
        
        for i, conn in enumerate(connections[:9]):  # Limit to 9 connections
            if i < 3:
                timeline["immediate"].append(conn)
            elif i < 6:
                timeline["short_term"].append(conn)
            else:
                timeline["medium_term"].append(conn)
                
        return timeline


class ConfounderDetector:
    """Detects confounding variables and external factors"""
    
    def __init__(self):
        self.confounder_patterns = self._load_confounder_patterns()
        
    def detect_milestone_confounders(self, milestone: Dict, goal_title: str, 
                                   context: Dict = None) -> List[Dict]:
        """Detect potential confounders for a specific milestone"""
        confounders = []
        
        milestone_name = milestone.get("name", "")
        milestone_type = milestone.get("type", "")
        
        # Technical skill confounders
        if "programming" in milestone_name.lower() or "coding" in milestone_name.lower():
            confounders.extend([
                {"type": "technology_evolution", "description": "Rapid changes in programming languages/frameworks"},
                {"type": "mentorship_availability", "description": "Access to experienced developers"},
                {"type": "project_opportunities", "description": "Availability of real projects to work on"}
            ])
            
        # Business/entrepreneurship confounders
        if "business" in milestone_name.lower() or "startup" in milestone_name.lower():
            confounders.extend([
                {"type": "market_conditions", "description": "Economic climate and market readiness"},
                {"type": "funding_availability", "description": "Access to investment and capital"},
                {"type": "regulatory_environment", "description": "Legal and regulatory constraints"}
            ])
            
        # Learning/education confounders
        if "learn" in milestone_name.lower() or "study" in milestone_name.lower():
            confounders.extend([
                {"type": "educational_resources", "description": "Quality and accessibility of learning materials"},
                {"type": "time_availability", "description": "Personal time and life circumstances"},
                {"type": "learning_support", "description": "Access to tutors, study groups, or mentors"}
            ])
            
        return confounders
        
    def identify_global_confounders(self, milestones: List[Dict], goal_title: str, 
                                  context: Dict = None) -> List[Dict]:
        """Identify confounders that affect multiple milestones"""
        global_confounders = []
        
        # Economic factors
        global_confounders.append({
            "type": "economic_conditions",
            "description": "Overall economic climate affecting opportunities and resources",
            "impact_scope": "all_milestones",
            "controllability": "low"
        })
        
        # Personal circumstances
        global_confounders.append({
            "type": "personal_circumstances",
            "description": "Health, family, and personal life factors",
            "impact_scope": "all_milestones", 
            "controllability": "medium"
        })
        
        # Industry trends
        if "technology" in goal_title.lower() or "software" in goal_title.lower():
            global_confounders.append({
                "type": "technology_trends",
                "description": "Rapid evolution in technology landscape",
                "impact_scope": "technical_milestones",
                "controllability": "medium"
            })
            
        # Network effects
        global_confounders.append({
            "type": "professional_network",
            "description": "Size and quality of professional connections",
            "impact_scope": "all_milestones",
            "controllability": "high"
        })
        
        return global_confounders
        
    def identify_external_dependencies(self, milestone: str, goal_title: str) -> List[Dict]:
        """Identify external dependencies for a milestone"""
        dependencies = []
        
        milestone_lower = milestone.lower()
        
        # Common external dependencies based on milestone content
        if "certification" in milestone_lower:
            dependencies.append({
                "type": "institutional",
                "description": "Certification body availability and requirements",
                "controllability": "low"
            })
            
        if "job" in milestone_lower or "employment" in milestone_lower:
            dependencies.append({
                "type": "market",
                "description": "Job market conditions and employer needs",
                "controllability": "low"
            })
            
        if "funding" in milestone_lower or "investment" in milestone_lower:
            dependencies.append({
                "type": "financial",
                "description": "Investor availability and market conditions",
                "controllability": "medium"
            })
            
        if "launch" in milestone_lower or "release" in milestone_lower:
            dependencies.append({
                "type": "market",
                "description": "Market readiness and customer demand",
                "controllability": "low"
            })
            
        return dependencies
        
    def analyze_confounder_impact(self, milestone_confounders: List[Dict], 
                                global_confounders: List[Dict]) -> Dict[str, Any]:
        """Analyze the overall impact of identified confounders"""
        
        # Count confounders by type
        confounder_counts = {}
        all_confounders = []
        
        # Collect all confounders
        for mc in milestone_confounders:
            all_confounders.extend(mc["confounders"])
        all_confounders.extend(global_confounders)
        
        # Count by type
        for confounder in all_confounders:
            conf_type = confounder.get("type", "unknown")
            confounder_counts[conf_type] = confounder_counts.get(conf_type, 0) + 1
            
        # Assess overall impact
        total_confounders = len(all_confounders)
        high_impact_confounders = [c for c in all_confounders 
                                 if c.get("controllability", "medium") == "low"]
        
        impact_assessment = {
            "total_confounders": total_confounders,
            "high_impact_count": len(high_impact_confounders),
            "confounder_distribution": confounder_counts,
            "risk_level": self._assess_overall_risk(total_confounders, len(high_impact_confounders))
        }
        
        return impact_assessment
        
    def _assess_overall_risk(self, total_confounders: int, high_impact_count: int) -> str:
        """Assess overall risk level based on confounder analysis"""
        
        if high_impact_count >= 5 or total_confounders >= 15:
            return "high"
        elif high_impact_count >= 2 or total_confounders >= 8:
            return "medium"
        else:
            return "low"
            
    def _load_confounder_patterns(self) -> Dict:
        """Load patterns for detecting confounders"""
        return {
            "technical_patterns": [
                "programming", "coding", "development", "software", "technology"
            ],
            "business_patterns": [
                "business", "startup", "entrepreneurship", "company", "venture"
            ],
            "learning_patterns": [
                "learn", "study", "education", "course", "training"
            ],
            "career_patterns": [
                "job", "career", "employment", "position", "role"
            ]
        }


class CollaboratorAnalyzer:
    """Analyzes milestone requirements for collaboration opportunities"""
    
    def __init__(self):
        pass
        
    def analyze_milestone_requirements(self, graph: nx.DiGraph, goal_title: str) -> List[Dict]:
        """Analyze each milestone for collaboration requirements"""
        milestone_analysis = []
        
        for node in graph.nodes():
            analysis = {
                "milestone": node,
                "collaboration_potential": self._assess_collaboration_potential(node),
                "skill_requirements": self._identify_skill_requirements(node),
                "collaboration_type": self._determine_collaboration_type(node),
                "urgency": self._assess_collaboration_urgency(graph, node)
            }
            milestone_analysis.append(analysis)
            
        return milestone_analysis
        
    def identify_collaboration_points(self, milestone_analysis: List[Dict], 
                                    person_name: str) -> List[Dict]:
        """Identify specific points where collaboration would be beneficial"""
        collaboration_points = []
        
        for analysis in milestone_analysis:
            if analysis["collaboration_potential"] >= 0.6:  # High collaboration potential
                collaboration_points.append({
                    "milestone": analysis["milestone"],
                    "collaboration_type": analysis["collaboration_type"],
                    "skill_gaps": analysis["skill_requirements"],
                    "priority": analysis["urgency"],
                    "collaboration_benefits": self._identify_collaboration_benefits(analysis)
                })
                
        return collaboration_points
        
    def generate_cofounder_suggestions(self, collaboration_points: List[Dict], 
                                     goal_title: str) -> List[Dict]:
        """Generate specific cofounder/collaborator suggestions"""
        suggestions = []
        
        # Analyze skill gaps across all collaboration points
        all_skill_gaps = []
        for point in collaboration_points:
            all_skill_gaps.extend(point["skill_gaps"])
            
        # Group similar skills
        skill_groups = self._group_similar_skills(all_skill_gaps)
        
        # Generate suggestions for each skill group
        for skill_group in skill_groups:
            suggestion = {
                "collaborator_type": self._map_skills_to_collaborator_type(skill_group),
                "required_skills": skill_group,
                "collaboration_model": self._suggest_collaboration_model(skill_group),
                "finding_strategy": self._suggest_finding_strategy(skill_group),
                "priority": self._calculate_suggestion_priority(skill_group, collaboration_points)
            }
            suggestions.append(suggestion)
            
        # Sort by priority
        suggestions.sort(key=lambda x: x["priority"], reverse=True)
        
        return suggestions
        
    def _assess_collaboration_potential(self, milestone: str) -> float:
        """Assess how much a milestone could benefit from collaboration (0-1)"""
        milestone_lower = milestone.lower()
        
        collaboration_indicators = [
            "team", "group", "partnership", "collaboration", "together",
            "business", "startup", "product", "marketing", "sales",
            "design", "development", "research", "analysis"
        ]
        
        matches = sum(1 for indicator in collaboration_indicators 
                     if indicator in milestone_lower)
        
        # Normalize to 0-1 scale
        return min(matches / 3, 1.0)
        
    def _identify_skill_requirements(self, milestone: str) -> List[str]:
        """Identify skills required for a milestone"""
        milestone_lower = milestone.lower()
        skills = []
        
        skill_mapping = {
            "programming": ["programming", "coding", "development", "software"],
            "design": ["design", "ui", "ux", "visual", "graphics"],
            "business": ["business", "strategy", "planning", "management"],
            "marketing": ["marketing", "sales", "promotion", "advertising"],
            "finance": ["finance", "accounting", "budgeting", "funding"],
            "research": ["research", "analysis", "investigation", "study"],
            "writing": ["writing", "content", "documentation", "communication"]
        }
        
        for skill, keywords in skill_mapping.items():
            if any(keyword in milestone_lower for keyword in keywords):
                skills.append(skill)
                
        return skills
        
    def _determine_collaboration_type(self, milestone: str) -> str:
        """Determine the type of collaboration needed"""
        milestone_lower = milestone.lower()
        
        if any(word in milestone_lower for word in ["business", "startup", "company"]):
            return "business_partner"
        elif any(word in milestone_lower for word in ["technical", "programming", "development"]):
            return "technical_collaborator"
        elif any(word in milestone_lower for word in ["design", "creative", "visual"]):
            return "creative_partner"
        elif any(word in milestone_lower for word in ["marketing", "sales", "promotion"]):
            return "marketing_partner"
        else:
            return "general_collaborator"
            
    def _assess_collaboration_urgency(self, graph: nx.DiGraph, milestone: str) -> str:
        """Assess urgency of collaboration for a milestone"""
        
        # High urgency if milestone has many dependents
        successors = list(graph.successors(milestone))
        predecessors = list(graph.predecessors(milestone))
        
        total_connections = len(successors) + len(predecessors)
        
        if total_connections >= 3:
            return "high"
        elif total_connections >= 1:
            return "medium"
        else:
            return "low"
            
    def _identify_collaboration_benefits(self, analysis: Dict) -> List[str]:
        """Identify specific benefits of collaboration for a milestone"""
        benefits = []
        
        collab_type = analysis["collaboration_type"]
        skill_reqs = analysis["skill_requirements"]
        
        if "business_partner" in collab_type:
            benefits.extend([
                "Shared business expertise and decision-making",
                "Divided responsibilities and workload",
                "Access to business networks and connections"
            ])
            
        if "technical_collaborator" in collab_type:
            benefits.extend([
                "Faster development and implementation",
                "Code review and quality assurance",
                "Knowledge sharing and skill development"
            ])
            
        if len(skill_reqs) > 2:
            benefits.append("Complementary skills covering multiple domains")
            
        return benefits
        
    def _group_similar_skills(self, skills: List[str]) -> List[List[str]]:
        """Group similar skills together"""
        skill_groups = []
        used_skills = set()
        
        similarity_mapping = {
            "technical": ["programming", "development", "software", "technical"],
            "business": ["business", "strategy", "management", "finance"],
            "creative": ["design", "creative", "visual", "writing"],
            "marketing": ["marketing", "sales", "promotion"]
        }
        
        for group_name, group_skills in similarity_mapping.items():
            group = [skill for skill in skills if skill in group_skills and skill not in used_skills]
            if group:
                skill_groups.append(group)
                used_skills.update(group)
                
        # Add remaining skills as individual groups
        remaining_skills = [skill for skill in skills if skill not in used_skills]
        for skill in remaining_skills:
            skill_groups.append([skill])
            
        return skill_groups
        
    def _map_skills_to_collaborator_type(self, skill_group: List[str]) -> str:
        """Map skill group to collaborator type"""
        
        if any(skill in ["programming", "development", "software"] for skill in skill_group):
            return "Technical Co-founder/Developer"
        elif any(skill in ["business", "strategy", "management"] for skill in skill_group):
            return "Business Co-founder/Strategist"
        elif any(skill in ["design", "creative", "visual"] for skill in skill_group):
            return "Creative Partner/Designer"
        elif any(skill in ["marketing", "sales"] for skill in skill_group):
            return "Marketing Partner/Growth Hacker"
        else:
            return "Domain Expert/Advisor"
            
    def _suggest_collaboration_model(self, skill_group: List[str]) -> str:
        """Suggest collaboration model based on skills"""
        
        if len(skill_group) >= 3:
            return "Co-founder partnership"
        elif len(skill_group) >= 2:
            return "Strategic partnership"
        else:
            return "Advisory/consulting relationship"
            
    def _suggest_finding_strategy(self, skill_group: List[str]) -> List[str]:
        """Suggest strategies for finding collaborators with specific skills"""
        strategies = []
        
        if any(skill in ["programming", "technical"] for skill in skill_group):
            strategies.extend([
                "Technical meetups and hackathons",
                "Open source communities (GitHub, Stack Overflow)",
                "University computer science programs"
            ])
            
        if any(skill in ["business", "strategy"] for skill in skill_group):
            strategies.extend([
                "Business networking events",
                "MBA programs and alumni networks",
                "Industry conferences and associations"
            ])
            
        if any(skill in ["design", "creative"] for skill in skill_group):
            strategies.extend([
                "Design communities (Dribbble, Behance)",
                "Creative agencies and freelancer platforms",
                "Design schools and programs"
            ])
            
        return strategies
        
    def _calculate_suggestion_priority(self, skill_group: List[str], 
                                     collaboration_points: List[Dict]) -> float:
        """Calculate priority score for a suggestion"""
        
        # Count how many collaboration points need these skills
        relevant_points = sum(1 for point in collaboration_points 
                            if any(skill in point["skill_gaps"] for skill in skill_group))
        
        # Priority based on relevance and skill group size
        relevance_score = relevant_points / len(collaboration_points) if collaboration_points else 0
        complexity_score = len(skill_group) / 5  # Normalize skill group size
        
        return (relevance_score + complexity_score) / 2


class NetworkMapper:
    """Maps industry connections and networking opportunities"""
    
    def __init__(self):
        pass
        
    def identify_industry_domains(self, goal_title: str) -> List[str]:
        """Identify relevant industry domains based on goal"""
        domains = []
        goal_lower = goal_title.lower()
        
        domain_mapping = {
            "technology": ["software", "programming", "tech", "development", "app", "web"],
            "business": ["business", "entrepreneur", "startup", "company", "venture"],
            "finance": ["finance", "investment", "trading", "fintech", "banking"],
            "healthcare": ["health", "medical", "healthcare", "biotech", "pharma"],
            "education": ["education", "teaching", "learning", "academic", "school"],
            "entertainment": ["entertainment", "media", "gaming", "content", "creative"],
            "retail": ["retail", "ecommerce", "sales", "commerce", "marketplace"]
        }
        
        for domain, keywords in domain_mapping.items():
            if any(keyword in goal_lower for keyword in keywords):
                domains.append(domain)
                
        if not domains:  # Default to general business if no specific domain
            domains.append("general_business")
            
        return domains
        
    def map_domain_connections(self, domain: str, person_background: Dict = None) -> List[Dict]:
        """Map connection types for a specific domain"""
        
        connection_templates = {
            "technology": [
                {"type": "Senior Developer", "value": "high", "accessibility": "medium"},
                {"type": "Tech Lead/Architect", "value": "high", "accessibility": "low"},
                {"type": "Product Manager", "value": "medium", "accessibility": "medium"},
                {"type": "CTO/VP Engineering", "value": "very_high", "accessibility": "low"},
                {"type": "Fellow Developer", "value": "medium", "accessibility": "high"}
            ],
            "business": [
                {"type": "Business Mentor", "value": "high", "accessibility": "medium"},
                {"type": "Successful Entrepreneur", "value": "very_high", "accessibility": "low"},
                {"type": "Industry Executive", "value": "high", "accessibility": "low"},
                {"type": "Business Coach", "value": "medium", "accessibility": "high"},
                {"type": "Fellow Entrepreneur", "value": "medium", "accessibility": "medium"}
            ],
            "finance": [
                {"type": "Angel Investor", "value": "very_high", "accessibility": "low"},
                {"type": "VC Partner", "value": "very_high", "accessibility": "very_low"},
                {"type": "Financial Advisor", "value": "medium", "accessibility": "high"},
                {"type": "CFO/Finance Executive", "value": "high", "accessibility": "low"},
                {"type": "Fintech Professional", "value": "medium", "accessibility": "medium"}
            ]
        }
        
        return connection_templates.get(domain, [
            {"type": "Industry Professional", "value": "medium", "accessibility": "medium"},
            {"type": "Domain Expert", "value": "high", "accessibility": "low"},
            {"type": "Peer Practitioner", "value": "medium", "accessibility": "high"}
        ])
        
    def analyze_network_requirements(self, graph: nx.DiGraph, goal_title: str) -> Dict[str, Any]:
        """Analyze network requirements for achieving the goal"""
        
        # Identify relevant industry domains
        industry_domains = self.identify_industry_domains(goal_title)
        
        # Analyze graph structure for networking needs
        node_count = graph.number_of_nodes()
        edge_count = graph.number_of_edges()
        
        # Calculate network density
        density = nx.density(graph) if node_count > 1 else 0
        
        # Identify critical nodes (high centrality)
        centrality_scores = nx.betweenness_centrality(graph) if node_count > 0 else {}
        critical_nodes = [node for node, score in centrality_scores.items() if score > 0.1]
        
        # Assess networking needs based on goal complexity
        networking_needs = {
            "industry_domains": industry_domains,
            "network_density": density,
            "critical_milestones": critical_nodes,
            "estimated_connections_needed": self._estimate_connection_needs(node_count, density),
            "networking_priority": self._assess_networking_priority(density, len(critical_nodes)),
            "recommended_channels": self._recommend_networking_channels(industry_domains)
        }
        
        return networking_needs
    
    def _estimate_connection_needs(self, node_count: int, density: float) -> int:
        """Estimate how many professional connections would be beneficial"""
        if node_count <= 3:
            return 5  # Basic networking for simple goals
        elif node_count <= 7:
            return 10  # Moderate networking for medium complexity
        else:
            return 15  # Extensive networking for complex goals
    
    def _assess_networking_priority(self, density: float, critical_nodes: int) -> str:
        """Assess the priority level for networking"""
        if density < 0.3 or critical_nodes >= 3:
            return "high"
        elif density < 0.6 or critical_nodes >= 1:
            return "medium"
        else:
            return "low"
    
    def _recommend_networking_channels(self, industry_domains: List[str]) -> List[str]:
        """Recommend networking channels based on industry domains"""
        channels = []
        
        for domain in industry_domains:
            if domain == "technology":
                channels.extend(["Tech meetups", "GitHub communities", "Stack Overflow"])
            elif domain == "business":
                channels.extend(["Business networking events", "LinkedIn groups", "Industry conferences"])
            elif domain == "finance":
                channels.extend(["Fintech meetups", "Investment clubs", "Professional associations"])
            elif domain == "healthcare":
                channels.extend(["Medical conferences", "Healthcare innovation events", "Research symposiums"])
            else:
                channels.extend(["Professional associations", "Industry meetups", "LinkedIn networking"])
        
        # Remove duplicates and return top 5
        return list(set(channels))[:5]
        
    def prioritize_connections(self, connection_mapping: List[Dict], goal_title: str) -> List[Dict]:
        """Prioritize connections based on value and accessibility"""
        all_connections = []
        
        for mapping in connection_mapping:
            domain = mapping["domain"]
            connections = mapping["connections"]
            
            for conn in connections:
                priority_score = self._calculate_connection_priority(conn, domain, goal_title)
                all_connections.append({
                    "domain": domain,
                    "type": conn["type"],
                    "value": conn["value"],
                    "accessibility": conn["accessibility"],
                    "priority_score": priority_score,
                    "priority": self._score_to_priority_level(priority_score)
                })
                
        # Sort by priority score
        all_connections.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return all_connections
        
    def _calculate_connection_priority(self, connection: Dict, domain: str, goal_title: str) -> float:
        """Calculate priority score for a connection"""
        
        value_scores = {
            "very_high": 1.0,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
        
        accessibility_scores = {
            "high": 1.0,
            "medium": 0.7,
            "low": 0.4,
            "very_low": 0.2
        }
        
        value_score = value_scores.get(connection["value"], 0.5)
        accessibility_score = accessibility_scores.get(connection["accessibility"], 0.5)
        
        # Weight value higher than accessibility (70% value, 30% accessibility)
        priority_score = (value_score * 0.7) + (accessibility_score * 0.3)
        
        return priority_score
        
    def _score_to_priority_level(self, score: float) -> str:
        """Convert numeric score to priority level"""
        if score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "medium"
        else:
            return "low"


class StrategicPartnershipFinder:
    """Finds strategic partnership opportunities"""
    
    def __init__(self):
        pass
        
    def find_strategic_partnerships(self, graph: nx.DiGraph, goal_title: str, 
                                  person_name: str) -> List[Dict]:
        """Find strategic partnership opportunities based on milestone analysis"""
        partnerships = []
        
        # Analyze milestone complexity for partnership opportunities
        complex_milestones = self._identify_complex_milestones(graph)
        
        for milestone in complex_milestones:
            partnership_opportunities = self._analyze_milestone_partnerships(milestone, goal_title)
            partnerships.extend(partnership_opportunities)
            
        # Remove duplicates and prioritize
        unique_partnerships = self._deduplicate_partnerships(partnerships)
        prioritized_partnerships = self._prioritize_partnerships(unique_partnerships)
        
        return prioritized_partnerships
        
    def _identify_complex_milestones(self, graph: nx.DiGraph) -> List[str]:
        """Identify milestones that would benefit from strategic partnerships"""
        complex_milestones = []
        
        for node in graph.nodes():
            # Consider milestones with high connectivity as complex
            in_degree = graph.in_degree(node)
            out_degree = graph.out_degree(node)
            total_degree = in_degree + out_degree
            
            if total_degree >= 3:  # High connectivity suggests complexity
                complex_milestones.append(node)
                
        return complex_milestones
        
    def _analyze_milestone_partnerships(self, milestone: str, goal_title: str) -> List[Dict]:
        """Analyze partnership opportunities for a specific milestone"""
        partnerships = []
        milestone_lower = milestone.lower()
        
        # Business partnerships
        if any(term in milestone_lower for term in ["business", "launch", "startup", "company"]):
            partnerships.append({
                "type": "business_partnership",
                "description": "Strategic business alliance for market entry",
                "milestone": milestone,
                "benefits": ["Market access", "Shared resources", "Risk mitigation"]
            })
            
        # Technical partnerships
        if any(term in milestone_lower for term in ["development", "technical", "platform"]):
            partnerships.append({
                "type": "technical_partnership",
                "description": "Technology collaboration and integration",
                "milestone": milestone,
                "benefits": ["Technical expertise", "Faster development", "Quality assurance"]
            })
            
        # Distribution partnerships
        if any(term in milestone_lower for term in ["marketing", "sales", "distribution"]):
            partnerships.append({
                "type": "distribution_partnership",
                "description": "Channel partnership for market reach",
                "milestone": milestone,
                "benefits": ["Market reach", "Customer access", "Brand credibility"]
            })
            
        return partnerships
        
    def _deduplicate_partnerships(self, partnerships: List[Dict]) -> List[Dict]:
        """Remove duplicate partnership opportunities"""
        seen_types = set()
        unique_partnerships = []
        
        for partnership in partnerships:
            partnership_key = partnership["type"]
            if partnership_key not in seen_types:
                unique_partnerships.append(partnership)
                seen_types.add(partnership_key)
                
        return unique_partnerships
        
    def _prioritize_partnerships(self, partnerships: List[Dict]) -> List[Dict]:
        """Prioritize partnerships by strategic value"""
        
        priority_mapping = {
            "business_partnership": 3,
            "technical_partnership": 2,
            "distribution_partnership": 2,
            "financial_partnership": 3,
            "strategic_alliance": 3
        }
        
        for partnership in partnerships:
            partnership_type = partnership["type"]
            priority_score = priority_mapping.get(partnership_type, 1)
            partnership["priority_score"] = priority_score
            partnership["priority"] = "high" if priority_score >= 3 else "medium" if priority_score >= 2 else "low"
            
        # Sort by priority score
        partnerships.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return partnerships
