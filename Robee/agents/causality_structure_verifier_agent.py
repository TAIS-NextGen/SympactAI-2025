"""
Causality Structure Verifier Agent - Verify and validate causal relationships
"""
import json
import networkx as nx
from typing import Dict, List, Any, Tuple, Set, Optional
from groq import Groq
import numpy as np
from datetime import datetime

class CausalityStructureVerifierAgent:
    """
    Primary Responsibilities:
    - Verify and validate causal relationships
    - Analyze network structure and properties
    - Validate relationship strengths and types
    - Detect structural inconsistencies
    """
    
    def __init__(self, groq_api_key: str):
        self.relationship_verifier = RelationshipVerifier(groq_api_key)
        self.structure_analyzer = StructureAnalyzer()
        self.network_validator = NetworkValidator()
        self.inconsistency_detector = InconsistencyDetector()
        
        # Supported causal relationship types
        self.relationship_types = [
            "direct_cause", "indirect_cause", "prerequisite", "enables", 
            "supports", "mutual_reinforcement", "inhibitory", "conditional", "temporal"
        ]
        
    def verify_causal_structure(self, milestones: List[Dict], goal_title: str) -> Dict:
        """Main verification function for causal structure"""
        verification_result = {
            "structure_valid": False,
            "relationship_verification": {},
            "network_analysis": {},
            "inconsistencies": [],
            "recommendations": [],
            "confidence_score": 0.0
        }
        
        try:
            # Build causal graph for analysis
            graph = self._build_causal_graph(milestones)
            
            # Verify individual relationships
            relationship_results = self.relationship_verifier.verify_relationships(milestones, goal_title)
            verification_result["relationship_verification"] = relationship_results
            
            # Analyze network structure
            network_analysis = self.structure_analyzer.analyze_network_structure(graph, milestones)
            verification_result["network_analysis"] = network_analysis
            
            # Detect inconsistencies
            inconsistencies = self.inconsistency_detector.detect_inconsistencies(graph, milestones)
            verification_result["inconsistencies"] = inconsistencies
            
            # Generate recommendations
            recommendations = self._generate_structure_recommendations(
                relationship_results, network_analysis, inconsistencies
            )
            verification_result["recommendations"] = recommendations
            
            # Calculate overall confidence
            verification_result["confidence_score"] = self._calculate_confidence_score(
                relationship_results, network_analysis, inconsistencies
            )
            
            # Determine if structure is valid
            verification_result["structure_valid"] = (
                len(inconsistencies) == 0 and 
                verification_result["confidence_score"] > 0.7
            )
            
        except Exception as e:
            verification_result["error"] = str(e)
            
        return verification_result
        
    def validate_relationship_strength(self, relationship: Dict, context: Dict) -> Dict:
        """Validate the strength of a specific causal relationship"""
        return self.relationship_verifier.validate_single_relationship(relationship, context)
        
    def check_network_connectivity(self, milestones: List[Dict]) -> Dict:
        """Check if the causal network is properly connected"""
        graph = self._build_causal_graph(milestones)
        return self.network_validator.check_connectivity(graph)
        
    def identify_critical_paths(self, milestones: List[Dict], goal_title: str) -> Dict:
        """Identify critical causal paths in the network"""
        graph = self._build_causal_graph(milestones)
        return self.structure_analyzer.find_critical_paths(graph, goal_title)
        
    def _build_causal_graph(self, milestones: List[Dict]) -> nx.DiGraph:
        """Build directed graph from milestone causal relationships"""
        graph = nx.DiGraph()
        
        # Add milestones as nodes
        for milestone in milestones:
            graph.add_node(
                milestone.get('id'),
                name=milestone.get('name'),
                score=milestone.get('score', 5),
                milestone_type=milestone.get('type', 'general')
            )
            
        # Add causal relationships as edges
        for milestone in milestones:
            milestone_id = milestone.get('id')
            causal_relationships = milestone.get('causal_relationships', [])
            
            for rel in causal_relationships:
                source = rel.get('prerequisite_id')
                target = rel.get('dependent_id', milestone_id)
                
                if source and target and source in graph.nodes and target in graph.nodes:
                    graph.add_edge(
                        source, target,
                        relationship_type=rel.get('relationship_type', 'prerequisite'),
                        strength=rel.get('strength', 0.5),
                        confidence=rel.get('confidence', 0.5)
                    )
                    
        return graph
        
    def _generate_structure_recommendations(self, relationship_results: Dict, 
                                          network_analysis: Dict, 
                                          inconsistencies: List[Dict]) -> List[Dict]:
        """Generate recommendations for improving causal structure"""
        recommendations = []
        
        # Recommendations based on relationship verification
        if relationship_results.get("low_confidence_relationships"):
            recommendations.append({
                "type": "relationship_verification",
                "priority": "high",
                "description": "Review and strengthen low-confidence causal relationships",
                "affected_relationships": relationship_results["low_confidence_relationships"]
            })
            
        # Recommendations based on network analysis
        if network_analysis.get("isolated_nodes"):
            recommendations.append({
                "type": "connectivity",
                "priority": "medium", 
                "description": "Connect isolated milestones to the main causal network",
                "affected_nodes": network_analysis["isolated_nodes"]
            })
            
        # Recommendations based on inconsistencies
        for inconsistency in inconsistencies:
            recommendations.append({
                "type": "inconsistency_resolution",
                "priority": inconsistency.get("severity", "medium"),
                "description": f"Resolve {inconsistency['type']}: {inconsistency['description']}",
                "affected_elements": inconsistency.get("elements", [])
            })
            
        return recommendations
        
    def _calculate_confidence_score(self, relationship_results: Dict, 
                                   network_analysis: Dict, 
                                   inconsistencies: List[Dict]) -> float:
        """Calculate overall confidence score for causal structure"""
        base_score = 1.0
        
        # Reduce score for relationship issues
        low_conf_relationships = len(relationship_results.get("low_confidence_relationships", []))
        total_relationships = relationship_results.get("total_relationships", 1)
        relationship_penalty = (low_conf_relationships / total_relationships) * 0.3
        
        # Reduce score for network issues
        network_score = network_analysis.get("overall_quality", 1.0)
        network_penalty = (1.0 - network_score) * 0.3
        
        # Reduce score for inconsistencies
        critical_inconsistencies = len([i for i in inconsistencies if i.get("severity") == "critical"])
        inconsistency_penalty = critical_inconsistencies * 0.2
        
        final_score = max(0.0, base_score - relationship_penalty - network_penalty - inconsistency_penalty)
        return final_score
    
    def analyze_causal_structure(self, person: str, goal_id: str, milestones: List[Dict]) -> Dict:
        """
        Compatibility method for interface - delegates to verify_causal_structure
        This method maintains backward compatibility with the original interface
        """
        try:
            # Convert milestones to the format expected by verify_causal_structure
            if isinstance(milestones, dict):
                # If milestones is a dict, convert to list
                milestone_list = [milestone for milestone in milestones.values() if isinstance(milestone, dict)]
            else:
                milestone_list = milestones if isinstance(milestones, list) else []
            
            # Get goal title for context
            goal_title = f"Goal {goal_id}"  # Default title, could be enhanced to get actual title
            
            # Call the main verification method
            return self.verify_causal_structure(milestone_list, goal_title)
            
        except Exception as e:
            return {
                "error": f"Causal structure analysis failed: {str(e)}",
                "structure_valid": False,
                "relationship_verification": {},
                "network_analysis": {},
                "inconsistencies": [],
                "recommendations": [],
                "confidence_score": 0.0
            }


class RelationshipVerifier:
    """Verifies individual causal relationships"""
    
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.model = "moonshotai/kimi-k2-instruct"
        
    def verify_relationships(self, milestones: List[Dict], goal_title: str) -> Dict:
        """Verify all causal relationships in milestone set"""
        verification_results = {
            "total_relationships": 0,
            "verified_relationships": 0,
            "low_confidence_relationships": [],
            "invalid_relationships": [],
            "relationship_details": []
        }
        
        for milestone in milestones:
            causal_relationships = milestone.get('causal_relationships', [])
            verification_results["total_relationships"] += len(causal_relationships)
            
            for rel in causal_relationships:
                verification = self.validate_single_relationship(rel, {
                    "goal_title": goal_title,
                    "milestone": milestone,
                    "all_milestones": milestones
                })
                
                verification_results["relationship_details"].append(verification)
                
                if verification["is_valid"]:
                    verification_results["verified_relationships"] += 1
                    
                    if verification["confidence"] < 0.6:
                        verification_results["low_confidence_relationships"].append(verification)
                else:
                    verification_results["invalid_relationships"].append(verification)
                    
        return verification_results
        
    def validate_single_relationship(self, relationship: Dict, context: Dict) -> Dict:
        """Validate a specific causal relationship"""
        try:
            prompt = self._create_relationship_verification_prompt(relationship, context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at validating causal relationships in career development paths."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=400
            )
            
            result = self._parse_verification_response(response.choices[0].message.content)
            result["relationship_id"] = relationship.get("prerequisite_id") + " -> " + relationship.get("dependent_id", "")
            
            return result
            
        except Exception as e:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "reasoning": f"Verification failed: {str(e)}",
                "relationship_id": relationship.get("prerequisite_id", "") + " -> " + relationship.get("dependent_id", "")
            }
            
    def _create_relationship_verification_prompt(self, relationship: Dict, context: Dict) -> str:
        """Create prompt for relationship verification"""
        prompt = f"""Verify if this causal relationship is valid and logical for achieving the goal: "{context.get('goal_title', '')}"

RELATIONSHIP TO VERIFY:
- Prerequisite: {relationship.get('prerequisite_id', 'Unknown')}
- Dependent: {relationship.get('dependent_id', 'Unknown')} 
- Type: {relationship.get('relationship_type', 'Unknown')}
- Claimed Strength: {relationship.get('strength', 0.5)}

CONTEXT:
Current Milestone: {context.get('milestone', {}).get('name', 'Unknown')}

Evaluate:
1. Is this relationship logically sound?
2. Does the prerequisite actually enable/cause the dependent?
3. Is the relationship type appropriate?
4. Is the strength reasonable?

Respond ONLY in JSON format:
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation",
    "suggested_strength": 0.0-1.0,
    "suggested_type": "relationship_type if different",
    "improvement_suggestions": "how to improve this relationship"
}}"""
        
        return prompt
        
    def _parse_verification_response(self, response_text: str) -> Dict:
        """Parse verification response"""
        try:
            if response_text.strip().startswith('{'):
                return json.loads(response_text)
            else:
                # Fallback parsing
                return {
                    "is_valid": "valid" in response_text.lower(),
                    "confidence": 0.5,
                    "reasoning": response_text[:200]
                }
        except Exception as e:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "reasoning": f"Failed to parse response: {str(e)}"
            }


class StructureAnalyzer:
    """Analyzes network structure properties"""
    
    def __init__(self):
        pass
        
    def analyze_network_structure(self, graph: nx.DiGraph, milestones: List[Dict]) -> Dict:
        """Analyze overall network structure"""
        analysis = {
            "node_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges(),
            "density": nx.density(graph),
            "is_connected": nx.is_weakly_connected(graph),
            "is_acyclic": nx.is_directed_acyclic_graph(graph),
            "isolated_nodes": list(nx.isolates(graph)),
            "strongly_connected_components": len(list(nx.strongly_connected_components(graph))),
            "weakly_connected_components": len(list(nx.weakly_connected_components(graph)))
        }
        
        # Calculate centrality measures
        if graph.number_of_nodes() > 0:
            analysis["centrality_measures"] = {
                "betweenness": dict(nx.betweenness_centrality(graph)),
                "closeness": dict(nx.closeness_centrality(graph)),
                "degree": dict(graph.degree())
            }
            
        # Identify structural patterns
        analysis["structural_patterns"] = self._identify_structural_patterns(graph)
        
        # Calculate overall quality score
        analysis["overall_quality"] = self._calculate_structure_quality(analysis)
        
        return analysis
        
    def find_critical_paths(self, graph: nx.DiGraph, goal_title: str) -> Dict:
        """Find critical paths in the causal network"""
        critical_paths = {
            "longest_paths": [],
            "most_important_paths": [],
            "bottleneck_nodes": [],
            "critical_edges": []
        }
        
        try:
            # Find longest paths (assuming DAG)
            if nx.is_directed_acyclic_graph(graph):
                # Find all simple paths and identify longest ones
                all_paths = []
                nodes = list(graph.nodes())
                
                for source in nodes:
                    for target in nodes:
                        if source != target:
                            try:
                                paths = list(nx.all_simple_paths(graph, source, target))
                                all_paths.extend(paths)
                            except nx.NetworkXNoPath:
                                continue
                                
                # Sort by length and take top paths
                all_paths.sort(key=len, reverse=True)
                critical_paths["longest_paths"] = all_paths[:5]
                
            # Find bottleneck nodes (high betweenness centrality)
            betweenness = nx.betweenness_centrality(graph)
            sorted_centrality = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
            critical_paths["bottleneck_nodes"] = sorted_centrality[:3]
            
            # Find critical edges (edges whose removal would disconnect the graph)
            critical_paths["critical_edges"] = list(nx.bridges(graph.to_undirected()))
            
        except Exception as e:
            critical_paths["error"] = str(e)
            
        return critical_paths
        
    def _identify_structural_patterns(self, graph: nx.DiGraph) -> Dict:
        """Identify common structural patterns"""
        patterns = {
            "linear_chains": 0,
            "branching_points": 0,
            "convergence_points": 0,
            "cycles": 0
        }
        
        # Count linear chains (nodes with in_degree=1, out_degree=1)
        for node in graph.nodes():
            in_deg = graph.in_degree(node)
            out_deg = graph.out_degree(node)
            
            if in_deg == 1 and out_deg == 1:
                patterns["linear_chains"] += 1
            elif out_deg > 1:
                patterns["branching_points"] += 1
            elif in_deg > 1:
                patterns["convergence_points"] += 1
                
        # Count cycles
        try:
            patterns["cycles"] = len(list(nx.simple_cycles(graph)))
        except:
            patterns["cycles"] = 0
            
        return patterns
        
    def _calculate_structure_quality(self, analysis: Dict) -> float:
        """Calculate overall structure quality score"""
        quality_score = 1.0
        
        # Penalize for disconnected components
        if not analysis["is_connected"]:
            quality_score *= 0.7
            
        # Penalize for cycles (in causal networks, cycles are often problematic)
        if not analysis["is_acyclic"]:
            quality_score *= 0.5
            
        # Penalize for isolated nodes
        isolated_count = len(analysis["isolated_nodes"])
        if isolated_count > 0:
            quality_score *= (1.0 - isolated_count / analysis["node_count"])
            
        # Reward appropriate density (not too sparse, not too dense)
        density = analysis["density"]
        if 0.1 <= density <= 0.6:
            quality_score *= 1.1
        else:
            quality_score *= 0.9
            
        return min(1.0, quality_score)


class NetworkValidator:
    """Validates network properties and connectivity"""
    
    def __init__(self):
        pass
        
    def check_connectivity(self, graph: nx.DiGraph) -> Dict:
        """Check network connectivity properties"""
        connectivity_report = {
            "is_strongly_connected": nx.is_strongly_connected(graph),
            "is_weakly_connected": nx.is_weakly_connected(graph),
            "number_of_components": len(list(nx.weakly_connected_components(graph))),
            "largest_component_size": 0,
            "connectivity_issues": []
        }
        
        if graph.number_of_nodes() > 0:
            # Find largest component
            components = list(nx.weakly_connected_components(graph))
            connectivity_report["largest_component_size"] = max(len(comp) for comp in components)
            
            # Identify connectivity issues
            if not connectivity_report["is_weakly_connected"]:
                connectivity_report["connectivity_issues"].append({
                    "type": "disconnected_components",
                    "description": f"Network has {connectivity_report['number_of_components']} disconnected components",
                    "severity": "high"
                })
                
            # Check for isolated nodes
            isolated = list(nx.isolates(graph))
            if isolated:
                connectivity_report["connectivity_issues"].append({
                    "type": "isolated_nodes",
                    "description": f"Found {len(isolated)} isolated nodes: {isolated}",
                    "severity": "medium"
                })
                
        return connectivity_report
        
    def validate_causal_flow(self, graph: nx.DiGraph) -> Dict:
        """Validate that causal flow makes logical sense"""
        flow_validation = {
            "has_cycles": not nx.is_directed_acyclic_graph(graph),
            "cycles": [],
            "flow_issues": []
        }
        
        # Find cycles if they exist
        if flow_validation["has_cycles"]:
            try:
                cycles = list(nx.simple_cycles(graph))
                flow_validation["cycles"] = cycles
                
                for cycle in cycles:
                    flow_validation["flow_issues"].append({
                        "type": "circular_dependency",
                        "description": f"Circular dependency detected: {' -> '.join(cycle + [cycle[0]])}",
                        "severity": "high",
                        "elements": cycle
                    })
            except:
                pass
                
        return flow_validation


class InconsistencyDetector:
    """Detects inconsistencies in causal structures"""
    
    def __init__(self):
        pass
        
    def detect_inconsistencies(self, graph: nx.DiGraph, milestones: List[Dict]) -> List[Dict]:
        """Detect various types of inconsistencies"""
        inconsistencies = []
        
        # Check for logical inconsistencies
        inconsistencies.extend(self._check_logical_inconsistencies(graph, milestones))
        
        # Check for strength inconsistencies
        inconsistencies.extend(self._check_strength_inconsistencies(graph))
        
        # Check for type inconsistencies
        inconsistencies.extend(self._check_type_inconsistencies(graph))
        
        # Check for temporal inconsistencies
        inconsistencies.extend(self._check_temporal_inconsistencies(graph, milestones))
        
        return inconsistencies
        
    def _check_logical_inconsistencies(self, graph: nx.DiGraph, milestones: List[Dict]) -> List[Dict]:
        """Check for logical inconsistencies in relationships"""
        inconsistencies = []
        
        # Check for contradictory relationships
        for edge in graph.edges(data=True):
            source, target, data = edge
            rel_type = data.get('relationship_type', '')
            
            # Check if there's a reverse relationship that would be contradictory
            if graph.has_edge(target, source):
                reverse_data = graph.edges[target, source]
                reverse_type = reverse_data.get('relationship_type', '')
                
                if self._are_contradictory_types(rel_type, reverse_type):
                    inconsistencies.append({
                        "type": "contradictory_relationships",
                        "description": f"Contradictory relationship types between {source} and {target}",
                        "severity": "high",
                        "elements": [source, target],
                        "details": {
                            "forward_type": rel_type,
                            "reverse_type": reverse_type
                        }
                    })
                    
        return inconsistencies
        
    def _check_strength_inconsistencies(self, graph: nx.DiGraph) -> List[Dict]:
        """Check for inconsistent relationship strengths"""
        inconsistencies = []
        
        for node in graph.nodes():
            incoming_edges = list(graph.in_edges(node, data=True))
            
            if len(incoming_edges) > 1:
                strengths = [edge[2].get('strength', 0.5) for edge in incoming_edges]
                
                # Check for large strength variations
                if max(strengths) - min(strengths) > 0.7:
                    inconsistencies.append({
                        "type": "strength_variation",
                        "description": f"Large variation in relationship strengths for {node}",
                        "severity": "medium",
                        "elements": [node],
                        "details": {
                            "strengths": strengths,
                            "variation": max(strengths) - min(strengths)
                        }
                    })
                    
        return inconsistencies
        
    def _check_type_inconsistencies(self, graph: nx.DiGraph) -> List[Dict]:
        """Check for inconsistent relationship types"""
        inconsistencies = []
        
        # Check for type combinations that don't make sense
        problematic_combinations = [
            ("direct_cause", "inhibitory"),
            ("prerequisite", "inhibitory"),
            ("enables", "inhibitory")
        ]
        
        for node in graph.nodes():
            incoming_types = [graph.edges[edge]['relationship_type'] 
                            for edge in graph.in_edges(node) 
                            if 'relationship_type' in graph.edges[edge]]
            
            for combo in problematic_combinations:
                if combo[0] in incoming_types and combo[1] in incoming_types:
                    inconsistencies.append({
                        "type": "conflicting_relationship_types",
                        "description": f"Conflicting relationship types for {node}: {combo[0]} and {combo[1]}",
                        "severity": "medium",
                        "elements": [node],
                        "details": {"conflicting_types": combo}
                    })
                    
        return inconsistencies
        
    def _check_temporal_inconsistencies(self, graph: nx.DiGraph, milestones: List[Dict]) -> List[Dict]:
        """Check for temporal ordering inconsistencies"""
        inconsistencies = []
        
        # This would check if milestones with dates/timestamps are in logical order
        # For now, we'll check basic temporal relationship consistency
        
        temporal_edges = [(u, v, d) for u, v, d in graph.edges(data=True) 
                         if d.get('relationship_type') == 'temporal']
        
        for edge in temporal_edges:
            source, target, data = edge
            
            # Check if there's a path from target back to source (temporal paradox)
            try:
                if nx.has_path(graph, target, source):
                    inconsistencies.append({
                        "type": "temporal_paradox",
                        "description": f"Temporal relationship creates circular dependency: {source} -> {target}",
                        "severity": "high",
                        "elements": [source, target]
                    })
            except:
                pass
                
        return inconsistencies
        
    def _are_contradictory_types(self, type1: str, type2: str) -> bool:
        """Check if two relationship types are contradictory"""
        contradictory_pairs = [
            ("enables", "inhibitory"),
            ("supports", "inhibitory"),
            ("direct_cause", "inhibitory"),
            ("prerequisite", "inhibitory")
        ]
        
        return (type1, type2) in contradictory_pairs or (type2, type1) in contradictory_pairs
