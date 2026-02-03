import json
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple, Set, Optional
from collections import defaultdict
import networkx as nx
from groq import Groq
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class ECausalityAgent:
    """
    1. Cofounders Analysis: Suggest potential cofounders based on causal DAG
    2. Counterfactual Analysis: What-if scenarios on the graph
    3. Intervention Analysis: Effect of removing edges/nodes from the graph
    """
    
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.model = "moonshotai/kimi-k2-instruct"
        
        # Causal relationship types
        self.relationship_types = [
            "direct_cause", "indirect_cause", "prerequisite", "enables", 
            "supports", "mutual_reinforcement", "inhibitory", "conditional", "temporal"
        ]
        
    def build_causal_dag(self, milestones: List[Dict[str, Any]], goal_title: str) -> nx.DiGraph:
        """Build a causal DAG from milestones and their relationships"""
        graph = nx.DiGraph()
        
        # Add milestones as nodes
        for milestone in milestones:
            graph.add_node(
                milestone['id'], 
                name=milestone['name'],
                score=milestone.get('score', 5),
                goal=goal_title,
                milestone_data=milestone
            )
        
        # Add causal relationships as edges
        for milestone in milestones:
            causal_rels = milestone.get('causal_relationships', [])
            for rel in causal_rels:
                source = rel.get('source_milestone_id') or rel.get('prerequisite_id')
                target = rel.get('target_milestone_id') or rel.get('dependent_id') or milestone['id']
                
                if source and target and source in [m['id'] for m in milestones]:
                    graph.add_edge(
                        source, 
                        target,
                        relationship_type=rel.get('relationship_type', 'prerequisite'),
                        strength=rel.get('strength', 0.5),
                        mechanism=rel.get('mechanism', ''),
                        confidence=rel.get('confidence', 0.5)
                    )
        
        return graph
    
    def suggest_cofounders(self, graph: nx.DiGraph, goal_title: str, person_name: str) -> Dict[str, Any]:
        """
        Analyze the causal DAG to suggest potential cofounders who could have 
        contributed to milestones or sets of milestones
        
        This method now delegates to the specialized CVA agent for comprehensive analysis
        """
        
        try:
            # Import CVA agent for specialized analysis
            from agents.cva_agent import CVAAgent
            
            # Create CVA agent instance if not available
            cva_agent = CVAAgent(api_key=None)  # CVA agent will handle its own API management
            
            # Get comprehensive cofounder analysis from CVA agent
            cofounder_analysis = cva_agent.suggest_cofounders(graph, goal_title, person_name)
            
            # Extract milestones for additional context
            milestones = []
            for node in graph.nodes():
                node_data = graph.nodes[node]
                milestones.append({
                    "milestone_id": node,
                    "name": node_data.get('name', ''),
                    "score": node_data.get('score', 5),
                    "type": node_data.get('type', 'general')
                })
            
            # Get confounding variable analysis for additional insights
            confounding_analysis = cva_agent.identify_confounding_variables(
                milestones, goal_title, {"person": person_name}
            )
            
            # Get industry connections mapping
            industry_analysis = cva_agent.map_industry_connections(
                goal_title, {"person": person_name}
            )
            
            # Combine results in the expected format for the UI
            return {
                "cofounder_suggestions": cofounder_analysis.get("cofounder_suggestions", []),
                "collaboration_insights": {
                    "most_beneficial_partnerships": [
                        partnership.get("type", "Unknown") 
                        for partnership in cofounder_analysis.get("strategic_partnerships", [])[:3]
                    ],
                    "network_gaps": self._analyze_network_gaps(cofounder_analysis),
                    "collaboration_opportunities": self._summarize_collaboration_opportunities(cofounder_analysis),
                    "confounding_factors": confounding_analysis.get("global_confounders", []),
                    "industry_connections": industry_analysis.get("prioritized_connections", [])[:5],
                    "networking_strategy": industry_analysis.get("networking_strategy", {})
                },
                "milestone_analysis": cofounder_analysis.get("milestone_analysis", []),
                "collaboration_points": cofounder_analysis.get("collaboration_points", []),
                "network_requirements": cofounder_analysis.get("network_requirements", {}),
                "timestamp": cofounder_analysis.get("timestamp")
            }
            
        except Exception as e:
            print(f"Error in CVA-enhanced cofounder analysis for {goal_title}: {e}")
            # Fallback to basic analysis if CVA agent fails
            return self._basic_cofounder_analysis(graph, goal_title, person_name)
    
    def _analyze_network_gaps(self, cofounder_analysis: Dict) -> str:
        """Analyze network gaps from CVA analysis"""
        collaboration_points = cofounder_analysis.get("collaboration_points", [])
        
        if not collaboration_points:
            return "Limited collaboration opportunities identified in current network"
        
        gap_types = set()
        for point in collaboration_points:
            skill_gaps = point.get("skill_gaps", [])
            gap_types.update(skill_gaps)
        
        if len(gap_types) > 3:
            return f"Multiple skill gaps identified across {len(gap_types)} areas: {', '.join(list(gap_types)[:3])}..."
        elif gap_types:
            return f"Key gaps in: {', '.join(gap_types)}"
        else:
            return "Network appears well-connected with minimal gaps"
    
    def _summarize_collaboration_opportunities(self, cofounder_analysis: Dict) -> str:
        """Summarize collaboration opportunities from CVA analysis"""
        suggestions = cofounder_analysis.get("cofounder_suggestions", [])
        strategic_partnerships = cofounder_analysis.get("strategic_partnerships", [])
        
        total_opportunities = len(suggestions) + len(strategic_partnerships)
        
        if total_opportunities >= 5:
            return f"High collaboration potential with {total_opportunities} opportunities across multiple domains"
        elif total_opportunities >= 3:
            return f"Moderate collaboration potential with {total_opportunities} key opportunities"
        elif total_opportunities >= 1:
            return f"Limited but focused collaboration opportunities ({total_opportunities} identified)"
        else:
            return "Current path appears to be primarily individual-focused"
    
    def _basic_cofounder_analysis(self, graph: nx.DiGraph, goal_title: str, person_name: str) -> Dict[str, Any]:
        """Fallback basic cofounder analysis if CVA agent fails"""
        
        # Analyze network structure to identify cofounder opportunities
        milestone_data = []
        for node in graph.nodes():
            node_data = graph.nodes[node]
            predecessors = list(graph.predecessors(node))
            successors = list(graph.successors(node))
            
            milestone_data.append({
                "id": node,
                "name": node_data.get('name', ''),
                "score": node_data.get('score', 5),
                "predecessors": predecessors,
                "successors": successors,
                "centrality": nx.betweenness_centrality(graph).get(node, 0)
            })
        
        prompt = f"""
        You are an expert at identifying potential collaboration opportunities in career journeys.
        
        GOAL: {goal_title}
        PERSON: {person_name}
        
        Analyze this career milestone network and suggest 3-5 potential cofounders or collaborators who could have meaningfully contributed to achieving "{goal_title}".
        
        MILESTONE NETWORK:
        {json.dumps(milestone_data, indent=2)}
        
        For each cofounder suggestion, consider:
        - Which specific milestones they could have helped with
        - What type of collaboration would be most beneficial  
        - How their contribution would strengthen the causal network
        - What complementary skills or resources they might provide
        
        COFOUNDER TYPES TO CONSIDER:
        - Technical collaborators (for skill-building milestones)
        - Mentors or advisors (for guidance-heavy milestones) 
        - Peers or study partners (for learning milestones)
        - Business partners (for venture/project milestones)
        - Industry connections (for networking milestones)
        
        REQUIRED JSON FORMAT:
        {{
            "cofounder_suggestions": [
                {{
                    "cofounder_type": "Technical Collaborator|Mentor|Peer|Business Partner|Industry Connection",
                    "cofounder_description": "Brief description of ideal cofounder profile",
                    "target_milestones": ["milestone_id1", "milestone_id2"],
                    "contribution_type": "How they would help (skills, resources, connections, etc.)",
                    "network_impact": "How their contribution strengthens the causal network",
                    "collaboration_question": "Specific question to ask user about this collaboration",
                    "confidence": 0.8
                }}
            ],
            "collaboration_insights": {{
                "most_beneficial_partnerships": ["cofounder_type1", "cofounder_type2"],
                "network_gaps": "What gaps in the network could be filled by collaborators",
                "collaboration_opportunities": "Overall assessment of collaboration potential"
            }}
        }}
        
        Focus on realistic, actionable cofounder suggestions that could genuinely improve the path to "{goal_title}".
        Provide ONLY the JSON output.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are an expert at identifying collaboration opportunities in career milestone networks for achieving: {goal_title}"},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=4000
            )
            
            result = self._parse_response(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error in basic cofounder analysis for {goal_title}: {e}")
            return {"cofounder_suggestions": [], "collaboration_insights": {}}
    
    def perform_counterfactual_analysis(self, graph: nx.DiGraph, goal_title: str, scenario_type: str = "auto") -> Dict[str, Any]:
        """
        Perform counterfactual analysis on the graph to extract new insights
        "What if X had not happened?" or "What if Y was done differently?"
        """
        
        # Identify key nodes for counterfactual analysis
        centrality_scores = nx.betweenness_centrality(graph)
        degree_scores = dict(graph.degree())
        
        # Get milestone data for analysis
        milestone_data = []
        for node in graph.nodes():
            node_data = graph.nodes[node]
            milestone_data.append({
                "id": node,
                "name": node_data.get('name', ''),
                "score": node_data.get('score', 5),
                "centrality": centrality_scores.get(node, 0),
                "degree": degree_scores.get(node, 0),
                "predecessors": list(graph.predecessors(node)),
                "successors": list(graph.successors(node))
            })
        
        # Sort by importance (centrality + degree)
        milestone_data.sort(key=lambda x: x['centrality'] + (x['degree'] / 10), reverse=True)
        
        prompt = f"""
        You are an expert at counterfactual reasoning and causal analysis in career development.
        
        GOAL: {goal_title}
        
        Perform counterfactual analysis on this career milestone network. Generate 4-6 insightful "what if" scenarios that reveal alternative paths, critical dependencies, or hidden opportunities.
        
        MILESTONE NETWORK:
        {json.dumps(milestone_data, indent=2)}
        
        COUNTERFACTUAL SCENARIOS TO EXPLORE:
        1. Critical Path Analysis: "What if the most central milestone had not been achieved?"
        2. Alternative Routes: "What if a different approach had been taken to achieve the same outcome?"
        3. Timing Changes: "What if milestones had occurred in a different order?"
        4. Resource Constraints: "What if certain resources/opportunities had not been available?"
        5. Acceleration Scenarios: "What if certain milestones had been achieved faster?"
        6. Collaboration Effects: "What if external help/partnerships had been leveraged?"
        
        For each scenario, analyze:
        - What would change in the causal network
        - What alternative paths might emerge
        - What new insights this reveals about the journey
        - What actionable lessons can be learned
        
        REQUIRED JSON FORMAT:
        {{
            "counterfactual_scenarios": [
                {{
                    "scenario_title": "Clear, engaging title for the what-if scenario",
                    "scenario_type": "Critical Path|Alternative Route|Timing|Resource|Acceleration|Collaboration",
                    "what_if_question": "Specific what-if question being explored",
                    "affected_milestones": ["milestone_id1", "milestone_id2"],
                    "predicted_outcome": "What would likely have happened instead",
                    "network_changes": "How the causal network would be different",
                    "insights_revealed": "What this reveals about the journey to {goal_title}",
                    "actionable_lessons": "Practical lessons for future goal achievement",
                    "probability_assessment": 0.7,
                    "impact_level": "High|Medium|Low"
                }}
            ],
            "key_insights": {{
                "most_critical_milestones": ["milestone_id1", "milestone_id2"],
                "alternative_paths_identified": 3,
                "optimization_opportunities": "Areas where the journey could have been improved",
                "resilience_assessment": "How robust the current path is to changes"
            }}
        }}
        
        Focus on generating actionable insights that could improve future goal achievement strategies.
        Provide ONLY the JSON output.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are an expert at counterfactual analysis for career milestone networks focused on: {goal_title}"},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.4,
                max_tokens=5000
            )
            
            result = self._parse_response(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error performing counterfactual analysis for {goal_title}: {e}")
            return {"counterfactual_scenarios": [], "key_insights": {}}
    
    def perform_intervention_analysis(self, graph: nx.DiGraph, goal_title: str, intervention_nodes: List[str] = None, intervention_edges: List[Tuple[str, str]] = None) -> Dict[str, Any]:
        """
        Analyze the effect of interventions (removing nodes or edges) on the causal network
        If no specific interventions provided, suggest the most impactful ones to analyze
        """
        
        original_graph = graph.copy()
        
        # If no specific interventions provided, identify key ones to analyze
        if not intervention_nodes and not intervention_edges:
            intervention_nodes, intervention_edges = self._identify_key_interventions(graph)
        
        # Perform interventions and analyze effects
        intervention_results = []
        
        # Analyze node removals
        if intervention_nodes:
            for node in intervention_nodes:
                if node in graph.nodes():
                    modified_graph = graph.copy()
                    node_data = modified_graph.nodes[node]
                    
                    # Remove the node and analyze impact
                    modified_graph.remove_node(node)
                    
                    impact = self._analyze_network_impact(original_graph, modified_graph, node, None, goal_title)
                    intervention_results.append({
                        "intervention_type": "node_removal",
                        "target": node,
                        "target_name": node_data.get('name', ''),
                        **impact
                    })
        
        # Analyze edge removals  
        if intervention_edges:
            for source, target in intervention_edges:
                if graph.has_edge(source, target):
                    modified_graph = graph.copy()
                    edge_data = modified_graph.edges[source, target]
                    
                    # Remove the edge and analyze impact
                    modified_graph.remove_edge(source, target)
                    
                    impact = self._analyze_network_impact(original_graph, modified_graph, None, (source, target), goal_title)
                    intervention_results.append({
                        "intervention_type": "edge_removal", 
                        "target": f"{source} -> {target}",
                        "target_name": f"{graph.nodes[source].get('name', source)} -> {graph.nodes[target].get('name', target)}",
                        "relationship_type": edge_data.get('relationship_type', 'unknown'),
                        **impact
                    })
        
        # Generate insights from intervention analysis
        insights = self._generate_intervention_insights(intervention_results, goal_title)
        
        return {
            "intervention_results": intervention_results,
            "insights": insights,
            "methodology": "causal_intervention_analysis"
        }
    
    def _identify_key_interventions(self, graph: nx.DiGraph) -> Tuple[List[str], List[Tuple[str, str]]]:
        """Identify the most impactful nodes and edges to analyze for interventions"""
        
        # Key nodes: high centrality, high degree, or bottlenecks
        centrality = nx.betweenness_centrality(graph)
        key_nodes = sorted(centrality.keys(), key=lambda x: centrality[x], reverse=True)[:3]
        
        # Key edges: high strength or critical connections
        key_edges = []
        for source, target, data in graph.edges(data=True):
            strength = data.get('strength', 0.5)
            if strength > 0.7 or graph.nodes[source].get('score', 5) >= 8:
                key_edges.append((source, target))
        
        return key_nodes[:3], key_edges[:3]
    
    def _analyze_network_impact(self, original_graph: nx.DiGraph, modified_graph: nx.DiGraph, 
                               removed_node: str, removed_edge: Tuple[str, str], goal_title: str) -> Dict[str, Any]:
        """Analyze the impact of removing a node or edge from the network"""
        
        # Calculate network metrics before and after
        original_metrics = self._calculate_network_metrics(original_graph)
        modified_metrics = self._calculate_network_metrics(modified_graph)
        
        # Identify affected components
        if removed_node:
            # Find milestones that were connected to the removed node
            affected_predecessors = list(original_graph.predecessors(removed_node)) if removed_node in original_graph else []
            affected_successors = list(original_graph.successors(removed_node)) if removed_node in original_graph else []
            affected_milestones = affected_predecessors + affected_successors
        else:
            # For edge removal, the affected milestones are the source and target
            affected_milestones = [removed_edge[0], removed_edge[1]] if removed_edge else []
        
        # Calculate impact severity
        connectivity_change = original_metrics['connectivity'] - modified_metrics['connectivity']
        efficiency_change = original_metrics['efficiency'] - modified_metrics['efficiency']
        
        impact_severity = "High" if connectivity_change > 0.3 or efficiency_change > 0.3 else \
                         "Medium" if connectivity_change > 0.1 or efficiency_change > 0.1 else "Low"
        
        return {
            "affected_milestones": affected_milestones,
            "connectivity_change": connectivity_change,
            "efficiency_change": efficiency_change,
            "impact_severity": impact_severity,
            "network_fragmentation": original_metrics['components'] != modified_metrics['components'],
            "cascade_effects": len(affected_milestones) > 2
        }
    
    def _calculate_network_metrics(self, graph: nx.DiGraph) -> Dict[str, float]:
        """Calculate key network metrics"""
        if not graph.nodes():
            return {"connectivity": 0, "efficiency": 0, "components": 0}
        
        # Convert to undirected for some metrics
        undirected = graph.to_undirected()
        
        metrics = {
            "connectivity": nx.edge_connectivity(undirected) / len(graph.nodes()) if len(graph.nodes()) > 1 else 0,
            "efficiency": nx.global_efficiency(undirected),
            "components": nx.number_connected_components(undirected)
        }
        
        return metrics
    
    def _generate_intervention_insights(self, intervention_results: List[Dict], goal_title: str) -> Dict[str, Any]:
        """Generate insights from intervention analysis"""
        
        if not intervention_results:
            return {}
        
        # Find most critical interventions
        high_impact = [r for r in intervention_results if r['impact_severity'] == 'High']
        medium_impact = [r for r in intervention_results if r['impact_severity'] == 'Medium']
        
        # Identify patterns
        fragmentation_causes = [r for r in intervention_results if r['network_fragmentation']]
        cascade_causes = [r for r in intervention_results if r['cascade_effects']]
        
        insights = {
            "critical_vulnerabilities": len(high_impact),
            "most_fragile_connections": [r['target_name'] for r in high_impact[:3]],
            "cascade_risks": len(cascade_causes),
            "network_resilience": "Low" if len(high_impact) > 2 else "Medium" if len(high_impact) > 0 else "High",
            "optimization_recommendations": []
        }
        
        # Generate recommendations
        if high_impact:
            insights["optimization_recommendations"].append("Consider backup plans for high-impact milestones")
        if cascade_causes:
            insights["optimization_recommendations"].append("Build redundancy into critical pathway connections")
        if fragmentation_causes:
            insights["optimization_recommendations"].append("Strengthen connections between milestone clusters")
        
        return insights
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {}
    
    def run_comprehensive_analysis(self, milestones: List[Dict[str, Any]], goal_title: str, person_name: str, 
                                 analysis_types: List[str] = None) -> Dict[str, Any]:
        """
        Run a comprehensive causal analysis including all three features
        analysis_types: List of ['cofounders', 'counterfactuals', 'interventions'] or None for all
        """
        
        if analysis_types is None:
            analysis_types = ['cofounders', 'counterfactuals', 'interventions']
        
        # Build the causal DAG
        graph = self.build_causal_dag(milestones, goal_title)
        
        results = {
            "goal_title": goal_title,
            "person_name": person_name,
            "analysis_timestamp": datetime.now().isoformat(),
            "graph_metrics": {
                "total_milestones": len(milestones),
                "total_relationships": graph.number_of_edges(),
                "connectivity": nx.edge_connectivity(graph.to_undirected()) if graph.nodes() else 0
            }
        }
        
        # Run requested analyses
        if 'cofounders' in analysis_types:
            with st.spinner("🤝 Analyzing cofounder opportunities..."):
                results['cofounder_analysis'] = self.suggest_cofounders(graph, goal_title, person_name)
        
        if 'counterfactuals' in analysis_types:
            with st.spinner("🔍 Performing counterfactual analysis..."):
                results['counterfactual_analysis'] = self.perform_counterfactual_analysis(graph, goal_title)
        
        if 'interventions' in analysis_types:
            with st.spinner("⚡ Analyzing intervention effects..."):
                results['intervention_analysis'] = self.perform_intervention_analysis(graph, goal_title)
        
        return results
