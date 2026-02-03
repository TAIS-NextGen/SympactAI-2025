import json
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict
from groq import Groq
import networkx as nx
from dotenv import load_dotenv

load_dotenv()

class CausalityAnalyzer:
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.model = "moonshotai/kimi-k2-instruct"
        
        self.relationship_types = [
            "direct_cause",
            "indirect_cause", 
            "prerequisite",
            "enables",
            "supports",
            "mutual_reinforcement",
            "inhibitory",
            "conditional",
            "temporal"
        ]
        
    def load_roadmaps(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading roadmaps file: {e}")
            return {}
    
    def analyze_milestone_causality(self, goal_title: str, milestones: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        # Convert milestones to the format expected by the AI
        milestone_list = []
        for i, milestone in enumerate(milestones):
            milestone_data = {
                "id": f"m{i+1}",
                "description": milestone["name"],
                "importance_score": milestone["score"] / 10.0,  # Normalize to 0-1
                "goal_relevance": f"Contributes to achieving {goal_title}"
            }
            milestone_list.append(milestone_data)
        
        prompt = f"""
        You are an expert at identifying causal relationships and dependencies in milestone networks for career goals.
        
        GOAL: {goal_title}

        Analyze ALL possible causal relationships and dependencies between these milestones in the context of achieving "{goal_title}".
        Consider logical progression, skill building, experience accumulation, and career advancement patterns.

        MILESTONES:
        {json.dumps(milestone_list, indent=2)}

        CAUSAL RELATIONSHIP TYPES:
        - direct_cause: Milestone A directly causes or enables Milestone B
        - indirect_cause: Milestone A influences Milestone B through intermediate effects
        - prerequisite: Milestone A must be completed before Milestone B can start
        - enables: Milestone A makes Milestone B possible but not required
        - supports: Milestone A helps with Milestone B but B can happen without A
        - mutual_reinforcement: Milestones A and B mutually strengthen each other
        - inhibitory: Milestone A prevents or reduces the likelihood of Milestone B
        - conditional: Milestone A causes Milestone B only under certain conditions
        - temporal: Milestone A must precede Milestone B in time for logical career progression

        ANALYSIS REQUIREMENTS:
        1. Consider educational prerequisites (degrees before advanced roles)
        2. Skill building sequences (foundational skills before advanced applications)
        3. Experience progression (internships before full-time roles, junior before senior positions)
        4. Industry knowledge accumulation
        5. Geographic and cultural transitions
        6. Technology stack dependencies

        REQUIRED JSON FORMAT:
        {{
            "dependencies": [
                {{
                    "prerequisite_id": "m1",
                    "dependent_id": "m2",
                    "relationship_type": "prerequisite|direct_cause|indirect_cause|enables|supports|mutual_reinforcement|inhibitory|conditional|temporal",
                    "strength": 0.85,
                    "bidirectional": false,
                    "conditions": "Any conditions required for this relationship",
                    "mechanism": "How the causal relationship works in context of career progression",
                    "confidence": 0.9,
                    "reasoning": "Detailed explanation of why this relationship exists for achieving {goal_title}"
                }}
            ],
            "network_properties": {{
                "total_relationships": 0,
                "critical_path": ["m1", "m2", "m3"],
                "bottlenecks": ["m3"],
                "foundational_milestones": ["m1", "m2"],
                "advanced_milestones": ["m5", "m6"],
                "relationship_density": 0.67
            }}
        }}

        Focus on realistic career progression patterns and logical dependencies for achieving "{goal_title}".
        Provide ONLY the JSON output.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are an expert at mapping causal relationships in career milestone networks. Focus on logical progression patterns for achieving: {goal_title}"},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.2,
                max_tokens=8000
            )
            
            result = self._parse_response(response.choices[0].message.content)
            
            # Enhance with network analysis
            result = self._enhance_network_analysis(result, milestone_list, goal_title)
            
            return result
            
        except Exception as e:
            print(f"Error analyzing causality for {goal_title}: {e}")
            return {"dependencies": [], "network_properties": {}}
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        try:
            # Clean up the response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response}")
            return {"dependencies": [], "network_properties": {}}
    
    def _enhance_network_analysis(self, dependency_data: Dict[str, Any], milestones: List[Dict], goal_title: str) -> Dict[str, Any]:
        """Enhance dependency analysis with network properties"""
        dependencies = dependency_data.get("dependencies", [])
        
        if not dependencies:
            return dependency_data
        
        # Build network graph
        graph = nx.DiGraph()
        
        # Add milestones as nodes
        for milestone in milestones:
            graph.add_node(milestone["id"], 
                          description=milestone["description"],
                          importance=milestone["importance_score"])
        
        # Add dependency edges
        for dep in dependencies:
            if dep.get("prerequisite_id") and dep.get("dependent_id"):
                graph.add_edge(dep["prerequisite_id"], dep["dependent_id"],
                             relationship=dep.get("relationship_type", "prerequisite"),
                             strength=dep.get("strength", 0.5))
        
        # Calculate network properties
        network_props = dependency_data.get("network_properties", {})
        
        try:
            # Find critical path (longest path through prerequisites)
            if graph.nodes():
                # Find nodes with no prerequisites (starting points)
                start_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
                longest_path = []
                
                for start in start_nodes:
                    try:
                        # Find longest path from this start node
                        descendants = nx.descendants(graph, start)
                        if descendants:
                            # Simple heuristic: path through highest importance nodes
                            path = [start] + sorted(descendants, 
                                                  key=lambda x: graph.nodes[x].get('importance', 0), 
                                                  reverse=True)[:5]
                            if len(path) > len(longest_path):
                                longest_path = path
                    except:
                        pass
                
                network_props["critical_path"] = longest_path[:6]  # Limit to 6 nodes
            
            # Find bottlenecks (nodes with high in-degree)
            if graph.nodes():
                in_degrees = dict(graph.in_degree())
                bottlenecks = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)
                network_props["bottlenecks"] = [node for node, degree in bottlenecks[:3] if degree > 1]
            
            # Identify foundational vs advanced milestones
            foundational = [n for n in graph.nodes() if graph.in_degree(n) == 0]
            advanced = [n for n in graph.nodes() if graph.out_degree(n) == 0 and graph.in_degree(n) > 0]
            
            network_props["foundational_milestones"] = foundational[:5]
            network_props["advanced_milestones"] = advanced[:5]
            
            # Calculate relationship density
            total_possible = len(milestones) * (len(milestones) - 1)
            network_props["relationship_density"] = len(dependencies) / total_possible if total_possible > 0 else 0
            
            network_props["total_relationships"] = len(dependencies)
            
        except Exception as e:
            print(f"Error calculating network properties: {e}")
        
        dependency_data["network_properties"] = network_props
        return dependency_data
    
    def process_all_roadmaps(self, input_file: str, output_file: str):
        """Process all roadmaps and generate causal analysis output"""
        print(f"Loading roadmaps from {input_file}...")
        roadmaps_data = self.load_roadmaps(input_file)
        
        if not roadmaps_data:
            print("No roadmap data found!")
            return
        
        causal_output = {
            "metadata": {
                "generation_timestamp": datetime.now().isoformat(),
                "source_file": input_file,
                "methodology": "ai_assisted_causal_analysis",
                "total_people": len(roadmaps_data),
                "total_goals": sum(len(person_data["roadmaps"]) for person_data in roadmaps_data.values())
            },
            "causal_analysis": {}
        }
        
        total_goals = 0
        processed_goals = 0
        
        # Process each person's roadmaps
        for person_name, person_data in roadmaps_data.items():
            print(f"\nProcessing roadmaps for {person_name}...")
            
            person_analysis = {
                "person_metadata": {
                    "name": person_name,
                    "total_goals": len(person_data["roadmaps"]),
                    "processing_timestamp": datetime.now().isoformat()
                },
                "goals": {}
            }
            
            roadmaps = person_data.get("roadmaps", {})
            total_goals += len(roadmaps)
            
            for goal_id, goal_data in roadmaps.items():
                goal_title = goal_data.get("title", "Unknown Goal")
                duration = goal_data.get("duration", "Unknown")
                milestones = goal_data.get("milestones", [])
                
                print(f"  Analyzing goal: {goal_title} ({len(milestones)} milestones)")
                
                # Perform causal analysis
                causal_analysis = self.analyze_milestone_causality(goal_title, milestones)
                
                # Compile goal analysis
                goal_analysis = {
                    "goal_metadata": {
                        "title": goal_title,
                        "duration": duration,
                        "total_milestones": len(milestones),
                        "analysis_timestamp": datetime.now().isoformat()
                    },
                    "milestones": [
                        {
                            "id": f"m{i+1}",
                            "description": milestone["name"],
                            "original_score": milestone["score"],
                            "normalized_importance": milestone["score"] / 10.0
                        }
                        for i, milestone in enumerate(milestones)
                    ],
                    "causal_relationships": causal_analysis.get("dependencies", []),
                    "network_analysis": causal_analysis.get("network_properties", {}),
                    "insights": self._generate_insights(goal_title, milestones, causal_analysis)
                }
                
                person_analysis["goals"][goal_id] = goal_analysis
                processed_goals += 1
                
                print(f"    Found {len(causal_analysis.get('dependencies', []))} causal relationships")
            
            causal_output["causal_analysis"][person_name] = person_analysis
        
        # Update metadata
        causal_output["metadata"]["goals_processed"] = processed_goals
        causal_output["metadata"]["total_relationships"] = sum(
            len(person["goals"][goal]["causal_relationships"])
            for person in causal_output["causal_analysis"].values()
            for goal in person["goals"]
        )
        
        # Save output
        print(f"\nSaving causal analysis to {output_file}...")
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(causal_output, f, indent=2, ensure_ascii=False)
            print(f"Successfully saved causal analysis!")
            print(f"Processed {processed_goals} goals with {causal_output['metadata']['total_relationships']} total relationships")
        except Exception as e:
            print(f"Error saving output: {e}")
    
    def _generate_insights(self, goal_title: str, milestones: List[Dict], causal_analysis: Dict) -> Dict[str, Any]:
        """Generate insights about the causal structure"""
        dependencies = causal_analysis.get("dependencies", [])
        network_props = causal_analysis.get("network_properties", {})
        
        insights = {
            "complexity_score": len(dependencies) / len(milestones) if milestones else 0,
            "relationship_types_used": list(set(dep.get("relationship_type", "prerequisite") for dep in dependencies)),
            "average_confidence": sum(dep.get("confidence", 0.5) for dep in dependencies) / len(dependencies) if dependencies else 0,
            "strongest_relationships": [
                {
                    "from": dep["prerequisite_id"],
                    "to": dep["dependent_id"],
                    "type": dep.get("relationship_type", "prerequisite"),
                    "strength": dep.get("strength", 0.5)
                }
                for dep in sorted(dependencies, key=lambda x: x.get("strength", 0), reverse=True)[:3]
            ],
            "career_progression_pattern": self._identify_progression_pattern(milestones, dependencies),
            "key_bottlenecks": network_props.get("bottlenecks", []),
            "foundational_requirements": network_props.get("foundational_milestones", [])
        }
        
        return insights
    
    def _identify_progression_pattern(self, milestones: List[Dict], dependencies: List[Dict]) -> str:
        """Identify the overall career progression pattern"""
        if len(dependencies) == 0:
            return "independent_milestones"
        
        relationship_types = [dep.get("relationship_type", "prerequisite") for dep in dependencies]
        
        if "prerequisite" in relationship_types and len([r for r in relationship_types if r == "prerequisite"]) > len(dependencies) * 0.5:
            return "sequential_progression"
        elif "enables" in relationship_types or "supports" in relationship_types:
            return "flexible_progression"
        elif "mutual_reinforcement" in relationship_types:
            return "synergistic_progression"
        else:
            return "complex_interdependent"


def main():
    # Initialize the analyzer
    api_key = os.getenv("groq_api_key")
    if not api_key:
        print("Error: groq_api_key not found in environment variables")
        return
    
    analyzer = CausalityAnalyzer(api_key)
    
    # Process the roadmaps
    input_file = "roadmaps_output.json"
    output_file = "causal_output.json"
    
    print("="*60)
    print("CAUSAL RELATIONSHIP ANALYZER")
    print("="*60)
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print("="*60)
    
    analyzer.process_all_roadmaps(input_file, output_file)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
