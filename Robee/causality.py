import json
import re
import textwrap
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import random
from datetime import datetime
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict
from groq import Groq
from matplotlib.patches import FancyBboxPatch
from dotenv import load_dotenv
import os
load_dotenv()

secret_value_0 = os.getenv("groq_api_key")


with open('./extraction/final_transcription.txt' , 'r' ) as f : 
    translated_text = f.read().strip()

with open('./extraction/title.txt' , 'r' ) as f : 
    title = f.read().strip()


class RoadmapExtractor:
    def __init__(self, groq_api_key: str, title: str):
        self.client = Groq(api_key=groq_api_key)
        self.model = "mistral-saba-24b"
        self.anonymizer_model = "llama3-70b-8192"
        self.goal_title = self._clean_goal_title(title)  # Clean the title immediately
        self.original_title = title  
        
        self.roadmap_taxonomy = [
            "Career Entry",
            "Career Transition", 
            "Career Growth",
            "Career Growth Leadership",
            "Specialized Technical Tracks",
            "Research",
            "Academic Excellence",
            "Entrepreneurship",
            "Freelancing",
            "Certification",
            "Public Impact & Thought Leadership",
            "Personal Development"
        ]
        
        self.milestone_taxonomy = [
            "Technical skills",
            "Soft Skills",
            "Hands-on project",
            "Internship",
            "Job experience",
            "Degree",
            "Diploma",
            "Certificate",
            "Workshop",
            "Networking",
            "Mentorship",
            "Personal development (well-being)",
            "Award",
            "Paper",
            "Patent",
            "Leadership"
        ]
        
    def _clean_goal_title(self, goal_title: str) -> str:
        """Clean up goal title to be a clear objective statement"""
        if not goal_title:
            return "Unknown Goal"
        
        # Remove common question words and phrases
        cleaned = goal_title.strip()
        
        # Remove "How to" at the beginning
        if cleaned.lower().startswith("how to "):
            cleaned = cleaned[7:]  # Remove "How to "
        
        # Remove trailing descriptions after dash or colon
        if " - " in cleaned:
            cleaned = cleaned.split(" - ")[0]
        elif ": " in cleaned:
            cleaned = cleaned.split(": ")[0]
        
        # Remove question marks
        cleaned = cleaned.replace("?", "")
        
        # Remove other question words at the beginning
        question_words = ["what is ", "what are ", "why ", "when ", "where ", "which "]
        for qword in question_words:
            if cleaned.lower().startswith(qword):
                cleaned = cleaned[len(qword):]
                break
        
        # Ensure it starts with a capital letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:] if len(cleaned) > 1 else cleaned.upper()
        
        return cleaned.strip()
        
    def classify_roadmap_type(self, text: str) -> Dict[str, Any]:
        """Classify the overall roadmap type from the narrative"""
        prompt = f"""
        You are an expert classifier. Analyze this narrative and determine its primary roadmap type.
        
        GOAL: {self.goal_title}

        ROADMAP TYPES:
        {', '.join(self.roadmap_taxonomy)}

        TEXT TO ANALYZE:
        {text}

        Identify the primary roadmap type that best describes the journey toward achieving: "{self.goal_title}"

        REQUIRED JSON FORMAT:
        {{
            "primary_roadmap_type": "exact_match_from_taxonomy",
            "confidence_score": 0.95,
            "secondary_types": ["other_relevant_types"],
            "reasoning": "Why this classification was chosen for achieving the goal"
        }}

        Provide ONLY the JSON output.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert roadmap classifier focused on goal achievement."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=500
            )
            
            return self._parse_response(response.choices[0].message.content)
        except Exception as e:
            print(f"Roadmap classification error: {e}")
            return {"primary_roadmap_type": "Personal Development", "confidence_score": 0.5}

    def extract_milestones(self, text: str) -> Dict[str, Any]:
        """Extract all milestones/steps from the narrative"""
        prompt = f"""
        You are an expert at extracting milestones from personal narratives. 
        
        GOAL: {self.goal_title}
        
        Analyze this text and identify ALL significant steps, actions, achievements, or milestones that contributed to achieving: "{self.goal_title}"

        Focus on actions that:
        - Directly contributed to reaching "{self.goal_title}"
        - Built necessary skills/knowledge for "{self.goal_title}"
        - Created opportunities leading to "{self.goal_title}"
        - Overcame obstacles preventing "{self.goal_title}"

        TEXT TO ANALYZE:
        {text}

        Extract every meaningful milestone/step that relates to achieving the goal. Show how each action connects to the ultimate goal.

        REQUIRED JSON FORMAT:
        {{
            "milestones": [
                {{
                    "id": "m1",
                    "description": "Clear description of the milestone/step",
                    "goal_relevance": "How this milestone relates to achieving '{self.goal_title}'",
                    "temporal_context": "when this happened (if mentioned)",
                    "importance": "high|medium|low"
                }}
            ]
        }}

        Provide ONLY the JSON output.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are an expert at extracting goal-oriented milestones focused on achieving: {self.goal_title}"},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=4000
            )
            
            return self._parse_response(response.choices[0].message.content)
        except Exception as e:
            print(f"Milestone extraction error: {e}")
            return {"milestones": []}

    def anonymize_milestones(self, milestone_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert personal narratives to general actionable steps while preserving specificity"""
        milestones = milestone_data.get("milestones", [])
        
        for milestone in milestones:
            original_description = milestone["description"]
            
            anonymization_prompt = f"""
            Transform this personal milestone into a general, actionable step while preserving important specificity.
            
            GOAL CONTEXT: This step should help someone achieve "{self.goal_title}"
            
            TRANSFORMATION RULES:
            1. Remove personal identifiers (names like "Sarah", "John", personal pronouns like "I", "my")
            2. Convert narrative form to imperative/action form
            3. Preserve specific platforms, technologies, certifications, or measurable achievements
            4. Keep domain-specific terminology that adds value
            5. Maintain concrete, measurable goals when possible
            6. Frame the action in context of achieving "{self.goal_title}"

            IMPORTANT: Keep specific platforms, certifications, numbers, and technical terms that make the goal concrete and measurable.
            
            ORIGINAL DESCRIPTION: {original_description}
            
            Provide ONLY the transformed description, nothing else.
            """
            
            try:
                response = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": f"You are an expert at converting personal narratives into universal actionable steps focused on achieving: {self.goal_title}"},
                        {"role": "user", "content": anonymization_prompt}
                    ],
                    model=self.anonymizer_model,
                    temperature=0.1,
                    max_tokens=200
                )
                
                anonymized_description = response.choices[0].message.content.strip()
                anonymized_description = anonymized_description.strip('"').strip("'").strip()
                
                milestone["original_description"] = original_description
                milestone["description"] = anonymized_description
                
            except Exception as e:
                print(f"Anonymization error for milestone {milestone['id']}: {e}")
                milestone["original_description"] = original_description
        
        return milestone_data

    def classify_milestones(self, milestone_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify each milestone according to the milestone taxonomy"""
        milestones = milestone_data.get("milestones", [])
        
        classification_prompt = f"""
        You are an expert milestone classifier. For each milestone, determine its type from the taxonomy.
        
        GOAL CONTEXT: These milestones should lead to achieving "{self.goal_title}"

        MILESTONE TAXONOMY:
        {', '.join(self.milestone_taxonomy)}

        MILESTONES TO CLASSIFY:
        {json.dumps(milestones, indent=2)}

        For each milestone, identify the most appropriate type that best describes what this milestone represents in the context of achieving "{self.goal_title}".

        REQUIRED JSON FORMAT:
        {{
            "classified_milestones": [
                {{
                    "id": "m1",
                    "milestone_type": "exact_match_from_taxonomy",
                    "confidence": 0.9,
                    "reasoning": "Brief explanation of classification choice and relevance to goal"
                }}
            ]
        }}

        Provide ONLY the JSON output.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are an expert milestone classifier specializing in paths to achieve: {self.goal_title}"},
                    {"role": "user", "content": classification_prompt}
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=3000
            )
            
            classification_result = self._parse_response(response.choices[0].message.content)
            
            # Merge classification results back into milestones
            classified_milestones = classification_result.get("classified_milestones", [])
            classification_map = {cm["id"]: cm for cm in classified_milestones}
            
            for milestone in milestones:
                classification = classification_map.get(milestone["id"], {})
                milestone["milestone_type"] = classification.get("milestone_type", "Personal development (well-being)")
                milestone["classification_confidence"] = classification.get("confidence", 0.5)
                milestone["classification_reasoning"] = classification.get("reasoning", "Default classification")
            
            return milestone_data
            
        except Exception as e:
            print(f"Milestone classification error: {e}")
            for milestone in milestones:
                milestone["milestone_type"] = "Personal development (well-being)"
                milestone["classification_confidence"] = 0.5
            return milestone_data

    def identify_dependencies(self, milestone_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify causal dependencies and relationships between milestones with enhanced analysis"""
        milestones = milestone_data.get("milestones", [])
        
        prompt = f"""
        You are an expert at identifying causal relationships and dependencies in complex milestone networks.
        
        GOAL: {self.goal_title}

        Analyze ALL possible causal relationships and dependencies between these milestones in the context of achieving "{self.goal_title}".
        Consider both direct and indirect causal connections between every pair of nodes.

        MILESTONES:
        {json.dumps(milestones, indent=2)}

        IMPORTANT: Use the full range of causal relationship types. Do NOT limit yourself to just 'prerequisite' and 'supports'. 

        CAUSAL RELATIONSHIP TYPES (USE ALL OF THESE):
        - direct_cause: Milestone A directly causes or enables Milestone B (use this for strong direct causation)
        - indirect_cause: Milestone A influences Milestone B through intermediate effects (use this for less direct causation)
        - prerequisite: Milestone A must be completed before Milestone B can start (strict dependency)
        - enables: Milestone A makes Milestone B possible but not required (opportunity creation)
        - supports: Milestone A helps with Milestone B but B can happen without A (supportive but not essential)
        - mutual_reinforcement: Milestones A and B mutually strengthen each other (bidirectional positive effects)
        - inhibitory: Milestone A prevents or reduces the likelihood of Milestone B (negative causation)
        - conditional: Milestone A causes Milestone B only under certain conditions (conditional causation)
        - temporal: Milestone A must precede Milestone B in time for causal effect (time-based ordering)

        ANALYSIS REQUIREMENTS:
        1. For each pair of milestones, determine if there's a causal relationship in either direction
        2. Use the MOST APPROPRIATE relationship type from the list above - don't default to just prerequisite/supports
        3. Consider the strength and type of causation carefully
        4. Include mediating factors or conditions when relevant
        5. Look for potential feedback loops or circular causation
        6. Identify bidirectional relationships where appropriate

        Focus on relationships that are logical for achieving "{self.goal_title}".

        REQUIRED JSON FORMAT:
        {{
            "dependencies": [
                {{
                    "prerequisite_id": "m1",
                    "dependent_id": "m2",
                    "relationship_type": "direct_cause|indirect_cause|prerequisite|enables|supports|mutual_reinforcement|inhibitory|conditional|temporal",
                    "strength": 0.85,
                    "bidirectional": false,
                    "conditions": "Any conditions required for this relationship",
                    "mechanism": "How the causal relationship/dependency works",
                    "confidence": 0.9,
                    "reasoning": "Detailed explanation of the causal relationship or dependency"
                }}
            ],
            "dependency_network_properties": {{
                "total_relationships": 0,
                "strongest_dependency_chain": ["m1", "m2", "m3"],
                "feedback_loops": [["m1", "m2", "m1"]],
                "dependency_density": 0.67,
                "key_dependency_hubs": ["m1", "m3"],
                "critical_path_milestones": ["m2", "m5"],
                "bottleneck_milestones": ["m3"]
            }}
        }}

        GENERATE DIVERSE RELATIONSHIP TYPES: Ensure you use multiple different relationship types, not just prerequisite and supports. Include direct_cause, indirect_cause, mutual_reinforcement, conditional, and temporal relationships where appropriate.
        
        Analyze ALL possible pairs of milestones for causal relationships and dependencies. Include weak relationships if they contribute to goal achievement.
        Provide ONLY the JSON output.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are an expert at mapping diverse causal relationships in complex milestone networks. Always use multiple different relationship types including direct_cause, indirect_cause, mutual_reinforcement, conditional, temporal, inhibitory - not just prerequisite and supports. Focus on achieving: {self.goal_title}"},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.2,  # Slightly higher temperature for more diverse relationship types
                max_tokens=8000   # More tokens for detailed analysis
            )
            
            dependency_data = self._parse_response(response.choices[0].message.content)
            
            dependency_data = self._enrich_dependency_analysis(dependency_data, milestones)
            
            return dependency_data
        except Exception as e:
            print(f"Dependency identification error: {e}")
            return {"dependencies": [], "dependency_network_properties": {}}

    def identify_dependencies_iterative(self, milestone_data: Dict[str, Any], 
                                      num_iterations: int = 8,
                                      num_groups: int = 6,
                                      coverage_threshold: float = 0.85) -> Dict[str, Any]:
        """
        Identify dependencies using iterative group-based analysis for comprehensive coverage
        
        Args:
            milestone_data: Dictionary containing milestones
            num_iterations: Maximum number of iterations to run
            num_groups: Fixed number of groups to generate per iteration
            coverage_threshold: Stop when this percentage of pairs is covered
        """
        milestones = milestone_data.get("milestones", [])
        
        print(f"Starting iterative dependency analysis with {len(milestones)} milestones")
        print(f"Using {num_groups} groups per iteration, target coverage: {coverage_threshold*100}%")
        
        # Initialize tracking structures
        all_dependencies = {}  # (prereq_id, dependent_id) -> dependency_data
        pair_coverage = set()  # Track which pairs have been analyzed
        milestone_ids = [m["id"] for m in milestones]
        
        # Calculate total possible pairs
        total_possible_pairs = len(milestone_ids) * (len(milestone_ids) - 1)
        target_pairs = int(total_possible_pairs * coverage_threshold)
        
        print(f"Total possible pairs: {total_possible_pairs}, Target: {target_pairs}")
        
        # Run iterative analysis
        for iteration in range(num_iterations):
            print(f"\n--- Iteration {iteration + 1}/{num_iterations} ---")
            
            # Generate groups for this iteration
            groups = self._generate_milestone_groups(milestone_ids, num_groups)
            print(f"Generated {len(groups)} groups")
            
            # Analyze each group
            iteration_dependencies = 0
            for group_idx, group in enumerate(groups):
                print(f"  Analyzing group {group_idx + 1}/{len(groups)} ({len(group)} nodes)")
                
                # Create group milestone data
                group_milestones = [m for m in milestones if m["id"] in group]
                group_data = {"milestones": group_milestones}
                
                # Analyze dependencies within this group
                group_results = self.identify_dependencies(group_data)
                group_dependencies = group_results.get("dependencies", [])
                
                # Merge results and track coverage
                for dep in group_dependencies:
                    prereq_id = dep.get("prerequisite_id")
                    dependent_id = dep.get("dependent_id")
                    
                    if prereq_id and dependent_id:
                        pair_key = (prereq_id, dependent_id)
                        
                        # Add to coverage tracking
                        pair_coverage.add(pair_key)
                        
                        # Store the dependency (prefer higher confidence if duplicate)
                        existing_dep = all_dependencies.get(pair_key)
                        if not existing_dep or dep.get("confidence", 0) > existing_dep.get("confidence", 0):
                            all_dependencies[pair_key] = dep
                            iteration_dependencies += 1
            
            # Calculate current coverage
            current_coverage = len(pair_coverage) / total_possible_pairs
            print(f"  Found {iteration_dependencies} new dependencies")
            print(f"  Total unique pairs analyzed: {len(pair_coverage)}")
            print(f"  Coverage: {current_coverage*100:.1f}%")
            
            # Check if we've reached our coverage threshold
            if len(pair_coverage) >= target_pairs:
                print(f"Reached target coverage! Stopping early.")
                break
        
        print(f"\n=== Final Results ===")
        print(f"Total dependencies found: {len(all_dependencies)}")
        print(f"Final coverage: {len(pair_coverage)/total_possible_pairs*100:.1f}%")
        
        # Compile final results
        final_dependencies = list(all_dependencies.values())
        
        # Generate comprehensive network properties
        final_data = {
            "dependencies": final_dependencies,
            "dependency_network_properties": self._generate_dependency_network_properties(final_dependencies, milestones)
        }
        
        # Add coverage statistics
        final_data["analysis_metadata"] = {
            "total_iterations": iteration + 1,
            "pairs_analyzed": len(pair_coverage),
            "total_possible_pairs": total_possible_pairs,
            "coverage_percentage": len(pair_coverage) / total_possible_pairs,
            "dependencies_found": len(final_dependencies),
            "num_groups_per_iteration": num_groups
        }
        
        return final_data

    def _generate_milestone_groups(self, milestone_ids: List[str], num_groups: int) -> List[List[str]]:
        """Generate groups of milestones for analysis"""
        import random
        
        milestone_ids = milestone_ids.copy()
        random.shuffle(milestone_ids)
        
        num_milestones = len(milestone_ids)
        
        if num_groups >= num_milestones:
            # Create single-item groups and fill with combinations
            groups = [[mid] for mid in milestone_ids]
            
            while len(groups) < num_groups:
                group_size = random.randint(2, min(3, num_milestones))
                random_group = random.sample(milestone_ids, group_size)
                groups.append(random_group)
            
            return groups[:num_groups]
        
        groups = []
        
        # Distribute milestones evenly
        base_group_size = num_milestones // num_groups
        remainder = num_milestones % num_groups
        
        start_idx = 0
        for i in range(num_groups):
            group_size = base_group_size + (1 if i < remainder else 0)
            end_idx = start_idx + group_size
            
            group = milestone_ids[start_idx:end_idx]
            groups.append(group)
            
            start_idx = end_idx
        
        # Add overlap for better coverage
        avg_group_size = num_milestones / num_groups
        overlap_size = max(1, int(avg_group_size * 0.3))
        
        for i in range(len(groups)):
            next_group_idx = (i + 1) % len(groups)
            
            overlap_candidates = [m for m in groups[next_group_idx] if m not in groups[i]]
            overlap_elements = random.sample(
                overlap_candidates, 
                min(overlap_size, len(overlap_candidates))
            )
            
            groups[i].extend(overlap_elements)
        
        return groups

    def _generate_dependency_network_properties(self, dependencies: List[Dict], milestones: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive dependency network properties"""
        milestone_ids = [m.get("id", "") for m in milestones]
        
        # Basic properties
        props = {
            "total_relationships": len(dependencies),
            "total_milestones": len(milestones)
        }
        
        if dependencies:
            # Calculate relationship type distribution
            rel_types = [dep.get("relationship_type", "prerequisite") for dep in dependencies]
            type_distribution = {}
            for rel_type in rel_types:
                type_distribution[rel_type] = type_distribution.get(rel_type, 0) + 1
            
            props["relationship_type_distribution"] = type_distribution
            
            # Calculate average confidence
            confidences = [dep.get("confidence", 0.5) for dep in dependencies]
            props["average_confidence"] = sum(confidences) / len(confidences)
            
            # Find strongest dependencies
            strongest_deps = sorted(dependencies, key=lambda x: x.get("strength", 0), reverse=True)[:3]
            props["strongest_dependencies"] = [
                f"{dep['prerequisite_id']} -> {dep['dependent_id']}" 
                for dep in strongest_deps
            ]
        
        return props

    def _enrich_dependency_analysis(self, dependency_data: Dict[str, Any], milestones: List[Dict]) -> Dict[str, Any]:
        dependencies = dependency_data.get("dependencies", [])
        
        # Build adjacency information for network analysis
        dependency_graph = {}
        milestone_ids = [m.get("id", "") for m in milestones]
        
        for milestone_id in milestone_ids:
            dependency_graph[milestone_id] = {
                "prerequisites": [],
                "dependents": [],
                "mutual_relationships": [],
                "supports": [],
                "supported_by": []
            }
        
        # Populate the dependency graph
        for dep in dependencies:
            prereq_id = dep.get("prerequisite_id")
            dependent_id = dep.get("dependent_id")
            rel_type = dep.get("relationship_type", "prerequisite")
            
            if prereq_id in dependency_graph and dependent_id in dependency_graph:
                if rel_type == "mutual_reinforcement":
                    dependency_graph[prereq_id]["mutual_relationships"].append(dependent_id)
                    dependency_graph[dependent_id]["mutual_relationships"].append(prereq_id)
                elif rel_type in ["prerequisite", "direct_cause", "temporal"]:
                    dependency_graph[prereq_id]["dependents"].append(dependent_id)
                    dependency_graph[dependent_id]["prerequisites"].append(prereq_id)
                elif rel_type in ["supports", "enables", "indirect_cause"]:
                    dependency_graph[prereq_id]["supports"].append(dependent_id)
                    dependency_graph[dependent_id]["supported_by"].append(prereq_id)
        
        if not dependency_data.get("dependency_network_properties"):
            dependency_data["dependency_network_properties"] = {}
        
        props = dependency_data["dependency_network_properties"]
        props["total_relationships"] = len(dependencies)
        props["dependency_graph"] = dependency_graph
        
        # Find critical path and bottlenecks
        critical_path = self._find_critical_path(dependency_graph, milestone_ids)
        bottlenecks = self._find_bottlenecks(dependency_graph)
        
        props["critical_path_milestones"] = critical_path
        props["bottleneck_milestones"] = bottlenecks
        
        # Calculate influence scores (nodes that affect many others)
        influence_scores = {}
        for node_id, connections in dependency_graph.items():
            influence_scores[node_id] = (
                len(connections["dependents"]) * 3 +  # Strong influence
                len(connections["supports"]) * 2 +    # Moderate influence  
                len(connections["prerequisites"]) * 1  # Foundational influence
            )
        
        props["influence_ranking"] = sorted(influence_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Find feedback loops
        feedback_loops = self._find_feedback_loops(dependency_graph)
        props["feedback_loops"] = feedback_loops
        
        # Calculate dependency density
        total_possible_connections = len(milestone_ids) * (len(milestone_ids) - 1)
        props["dependency_density"] = len(dependencies) / total_possible_connections if total_possible_connections > 0 else 0
        
        return dependency_data

    def _find_critical_path(self, dependency_graph: Dict, milestone_ids: List[str]) -> List[str]:
        """Find the critical path through the dependency network"""
        # Simple heuristic: find the longest path through prerequisites
        try:
            # Find nodes with no prerequisites (starting points)
            start_nodes = [mid for mid in milestone_ids 
                          if not dependency_graph[mid]["prerequisites"]]
            
            if not start_nodes:
                return milestone_ids[:3]  # Fallback
                
            # Find longest path from each start node
            longest_path = []
            for start_node in start_nodes:
                path = self._dfs_longest_path(dependency_graph, start_node, set())
                if len(path) > len(longest_path):
                    longest_path = path
                    
            return longest_path[:5]  # Return top 5 for critical path
        except:
            return milestone_ids[:3]  # Fallback

    def _dfs_longest_path(self, graph: Dict, node: str, visited: Set[str]) -> List[str]:
        """DFS to find longest path from a node"""
        if node in visited:
            return [node]
            
        visited.add(node)
        longest_path = [node]
        
        for dependent in graph[node]["dependents"]:
            path = [node] + self._dfs_longest_path(graph, dependent, visited.copy())
            if len(path) > len(longest_path):
                longest_path = path
                
        return longest_path

    def _find_bottlenecks(self, dependency_graph: Dict) -> List[str]:
        """Find bottleneck nodes that many other nodes depend on"""
        bottleneck_scores = {}
        
        for node_id, connections in dependency_graph.items():
            # Bottlenecks have many dependents
            bottleneck_scores[node_id] = len(connections["dependents"]) + len(connections["supports"])
        
        # Return top bottlenecks
        sorted_bottlenecks = sorted(bottleneck_scores.items(), key=lambda x: x[1], reverse=True)
        return [node for node, score in sorted_bottlenecks[:3] if score > 0]

    def _find_feedback_loops(self, dependency_graph: Dict) -> List[List[str]]:
        """Find feedback loops in the dependency network"""
        loops = []
        
        # Simple cycle detection
        for start_node in dependency_graph.keys():
            visited = set()
            path = []
            if self._dfs_cycle_detection(dependency_graph, start_node, visited, path):
                # Found a cycle
                cycle_start = path[-1]
                cycle_start_idx = path.index(cycle_start)
                cycle = path[cycle_start_idx:]
                if len(cycle) > 1 and cycle not in loops:
                    loops.append(cycle)
                    
        return loops[:3]  # Return up to 3 feedback loops

    def _dfs_cycle_detection(self, graph: Dict, node: str, visited: Set[str], path: List[str]) -> bool:
        """DFS for cycle detection"""
        if node in path:
            return True
            
        if node in visited:
            return False
            
        visited.add(node)
        path.append(node)
        
        # Check all outgoing connections
        for dependent in graph[node]["dependents"] + graph[node]["supports"]:
            if self._dfs_cycle_detection(graph, dependent, visited, path):
                return True
                
        path.pop()
        return False

    def order_milestones(self, milestone_data: Dict[str, Any], dependency_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Order milestones based on dependencies and temporal context"""
        milestones = milestone_data.get("milestones", [])
        dependencies = dependency_data.get("dependencies", [])
        
        # Create dependency graph
        graph = nx.DiGraph()
        
        # Add milestones as nodes
        for milestone in milestones:
            graph.add_node(milestone["id"], **milestone)
        
        # Add dependency edges (only strong dependencies)
        for dep in dependencies:
            if (dep.get("prerequisite_id") in graph.nodes and 
                dep.get("dependent_id") in graph.nodes and
                dep.get("dependency_type") == "prerequisite" and
                dep.get("strength", 0) > 0.6):
                graph.add_edge(dep["prerequisite_id"], dep["dependent_id"], **dep)
        
        # Determine order
        try:
            if nx.is_directed_acyclic_graph(graph):
                ordered_ids = list(nx.topological_sort(graph))
            else:
                # Resolve cycles by removing weakest edges
                ordered_ids = self._resolve_cycles_and_sort(graph, milestones)
        except:
            # Fallback: sort by importance and temporal indicators
            ordered_ids = [m["id"] for m in sorted(milestones, 
                                                 key=lambda x: (x.get("importance", "medium"), len(x.get("temporal_context", ""))))]
        
        # Create ordered milestone list
        ordered_milestones = []
        id_to_milestone = {m["id"]: m for m in milestones}
        
        for i, milestone_id in enumerate(ordered_ids):
            milestone = id_to_milestone.get(milestone_id)
            if milestone:
                milestone["order_position"] = i + 1
                ordered_milestones.append(milestone)
        
        return ordered_milestones

    def _resolve_cycles_and_sort(self, graph: nx.DiGraph, milestones: List[Dict]) -> List[str]:
        """Resolve cycles in dependency graph and return topological order"""
        try:
            cycles = list(nx.simple_cycles(graph))
            for cycle in cycles:
                # Remove weakest dependency in cycle
                cycle_edges = [(cycle[i], cycle[(i+1) % len(cycle)]) for i in range(len(cycle))]
                weakest_edge = min(cycle_edges, 
                                 key=lambda edge: graph[edge[0]][edge[1]].get("strength", 0.5))
                graph.remove_edge(*weakest_edge)
            
            return list(nx.topological_sort(graph))
        except:
            return [m["id"] for m in milestones]

    def calculate_milestone_scores(self, ordered_milestones: List[Dict], dependencies: List[Dict]) -> List[Dict]:
        """Calculate importance scores for milestones based on goal relevance"""
        # Create graph for centrality analysis
        graph = nx.DiGraph()
        
        for milestone in ordered_milestones:
            graph.add_node(milestone["id"])
        
        for dep in dependencies:
            if (dep.get("prerequisite_id") in graph.nodes and 
                dep.get("dependent_id") in graph.nodes):
                weight = dep.get("strength", 0.5)
                graph.add_edge(dep["prerequisite_id"], dep["dependent_id"], weight=weight)
        
        try:
            # Calculate various centrality measures
            pagerank_scores = nx.pagerank(graph, weight='weight')
            in_degree = dict(graph.in_degree())
            out_degree = dict(graph.out_degree())
            
            # Normalize degree scores
            max_in = max(in_degree.values()) if in_degree.values() else 1
            max_out = max(out_degree.values()) if out_degree.values() else 1
            
            for milestone in ordered_milestones:
                milestone_id = milestone["id"]
                
                # Base importance from original classification
                base_score = 0.5
                if milestone.get("importance") == "high":
                    base_score = 0.7
                elif milestone.get("importance") == "low":
                    base_score = 0.3
                
                # Goal relevance bonus (new)
                goal_relevance_bonus = 0.0
                if milestone.get("goal_relevance"):
                    goal_relevance_bonus = 0.15  # Higher bonus for goal-relevant milestones
                
                # Milestone type bonus
                type_bonus = 0.0
                high_value_types = ["Degree", "Certificate", "Award", "Job experience", "Paper"]
                if milestone.get("milestone_type") in high_value_types:
                    type_bonus = 0.1
                
                # Network centrality score
                centrality_score = pagerank_scores.get(milestone_id, 0) * 2
                
                # Connectivity score (how connected this milestone is)
                connectivity_score = (
                    (in_degree.get(milestone_id, 0) / max_in) * 0.3 +
                    (out_degree.get(milestone_id, 0) / max_out) * 0.2
                )
                
                # Final weighted score (adjusted for goal relevance)
                final_score = (
                    base_score * 0.3 + 
                    centrality_score * 0.25 + 
                    connectivity_score * 0.15 + 
                    type_bonus * 0.1 +
                    goal_relevance_bonus * 0.2  # Goal relevance gets significant weight
                )
                
                milestone["importance_score"] = min(1.0, max(0.1, final_score))
                
        except Exception as e:
            print(f"Score calculation error: {e}")
            for milestone in ordered_milestones:
                milestone["importance_score"] = 0.5
        
        return ordered_milestones

    def generate_roadmap_json(self, ordered_milestones: List[Dict], dependencies: List[Dict], 
                            roadmap_classification: Dict, source_metadata: Dict = None) -> str:
        """Generate the final roadmap JSON"""
        
        # Calculate statistics
        milestone_distribution = {}
        for milestone in ordered_milestones:
            mtype = milestone["milestone_type"]
            milestone_distribution[mtype] = milestone_distribution.get(mtype, 0) + 1
        
        critical_milestones = [m for m in ordered_milestones if m.get("importance_score", 0) >= 0.7]
        
        # Build final roadmap structure
        roadmap = {
            "roadmap_metadata": {
                "extraction_timestamp": datetime.now().isoformat(),
                "goal_title": self.goal_title,  # Add goal title to metadata
                "source_metadata": source_metadata or {},
                "total_milestones": len(ordered_milestones),
                "total_dependencies": len(dependencies),
                "methodology": "goal_focused_roadmap_extraction",
                "primary_roadmap_type": roadmap_classification.get("primary_roadmap_type", "Personal Development"),
                "roadmap_classification_confidence": roadmap_classification.get("confidence_score", 0.5),
                "secondary_roadmap_types": roadmap_classification.get("secondary_types", []),
                "milestone_distribution": milestone_distribution
            },
            "milestones": [
                {
                    "id": milestone["id"],
                    "description": milestone["description"],
                    "original_description": milestone.get("original_description", ""),
                    "goal_relevance": milestone.get("goal_relevance", ""),  # Add goal relevance
                    "milestone_type": milestone.get("milestone_type", "Personal development (well-being)"),
                    "classification_confidence": milestone.get("classification_confidence", 0.5),
                    "order_position": milestone.get("order_position", 0),
                    "importance_score": milestone.get("importance_score", 0.5),
                    "temporal_context": milestone.get("temporal_context", ""),
                    "original_importance": milestone.get("importance", "medium")
                }
                for milestone in ordered_milestones
            ],
            "dependencies": dependencies,
            "analysis": {
                "goal_title": self.goal_title,  # Add goal to analysis
                "critical_milestones": [m["description"] for m in critical_milestones],
                "roadmap_complexity": len(dependencies) / len(ordered_milestones) if ordered_milestones else 0,
                "dominant_milestone_types": sorted(milestone_distribution.items(), 
                                                 key=lambda x: x[1], reverse=True)[:3],
                "total_steps": len(ordered_milestones),
                "high_importance_steps": len(critical_milestones),
                "goal_relevance_coverage": len([m for m in ordered_milestones if m.get("goal_relevance")]) / len(ordered_milestones) if ordered_milestones else 0
            }
        }
        
        return json.dumps(roadmap, indent=2, ensure_ascii=False)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {}

    def run_pipeline(self, text: str, source_metadata: Dict = None) -> str:
        """Run the complete roadmap extraction pipeline"""
        print(f"Extracting roadmap for goal: {self.goal_title}")
        print("1. Classifying roadmap type...")
        roadmap_classification = self.classify_roadmap_type(text)
        
        print("2. Extracting milestones...")
        milestone_data = self.extract_milestones(text)
        
        print("3. Anonymizing milestones...")
        anonymized_data = self.anonymize_milestones(milestone_data)
        
        print("4. Classifying milestone types...")
        classified_data = self.classify_milestones(anonymized_data)
        
        print("5. Identifying dependencies...")
        # Use iterative method for larger milestone sets for better coverage
        milestones = classified_data.get("milestones", [])
        if len(milestones) > 15:
            print("   Using iterative dependency analysis for comprehensive coverage...")
            dependency_data = self.identify_dependencies_iterative(classified_data)
        else:
            dependency_data = self.identify_dependencies(classified_data)
        
        print("6. Ordering milestones...")
        ordered_milestones = self.order_milestones(classified_data, dependency_data)
        
        print("7. Calculating importance scores...")
        scored_milestones = self.calculate_milestone_scores(ordered_milestones, 
                                                          dependency_data.get("dependencies", []))
        
        print("8. Generating final roadmap...")
        roadmap_json = self.generate_roadmap_json(scored_milestones, 
                                                dependency_data.get("dependencies", []),
                                                roadmap_classification, 
                                                source_metadata)
        
        print("Pipeline completed!")
        return roadmap_json


if __name__ == "__main__":
    # Read the title from file
    # with open('/kaggle/input/transcription-generation-process-english-v3/title.txt', 'r') as f:
    #     title = f.read().strip()
    
    extractor = RoadmapExtractor(secret_value_0, title)
    
    # Example text
    text = translated_text
    
    # Optional source metadata
    source_metadata = {
        "type": "personal_narrative",
        "language": "english",
        "domain": "goal_achievement",
        "target_goal": title
    }
    
    # Run the pipeline
    roadmap_json = extractor.run_pipeline(text, source_metadata)
    
    print("\n" + "="*60)
    print(f"ROADMAP JSON FOR GOAL: {title}")
    print("="*60)
    print(roadmap_json)

if __name__ == "__main__":

    extractor = RoadmapExtractor(secret_value_0, title)
    
    text = translated_text
    
    # Optional source metadata
    source_metadata = {
        "type": "personal_narrative",
        "language": "english",
        "domain": "goal_achievement",
        "target_goal": title
    }
    
    # Run the pipeline
    roadmap_json = extractor.run_pipeline(text, source_metadata)
    
    print("\n" + "="*60)
    print(f"ROADMAP JSON FOR GOAL: {title}")
    print("="*60)
    print(roadmap_json)
    with open('./result.txt' , 'w') as f : 
        f.write(roadmap_json)