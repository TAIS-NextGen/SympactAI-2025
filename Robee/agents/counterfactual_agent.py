"""
Counterfactual Agent - Performs what-if scenario analysis and alternative path exploration
"""
import json
import networkx as nx
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import copy

class CounterfactualAgent:
    """
    Primary Responsibilities:
    - Perform what-if scenario analysis on career roadmaps
    - Generate alternative path scenarios
    - Analyze critical dependency impacts
    - Explore timing modification effects
    """
    
    def __init__(self, api_key: str = None):
        self.scenario_generator = ScenarioGenerator()
        self.impact_analyzer = ImpactAnalyzer()
        self.alternative_path_finder = AlternativePathFinder()
        self.dependency_analyzer = DependencyAnalyzer()
        
        # Analysis configuration
        self.scenario_types = [
            "milestone_removal",
            "timing_modification", 
            "resource_change",
            "alternative_approach",
            "prerequisite_bypass",
            "collaboration_addition"
        ]
        
    def perform_counterfactual_analysis(self, graph: nx.DiGraph, goal_title: str, 
                                      scenario_type: str = "auto") -> Dict[str, Any]:
        """Perform comprehensive counterfactual analysis"""
        
        if scenario_type == "auto":
            # Generate multiple scenario types
            all_scenarios = []
            for s_type in self.scenario_types:
                scenarios = self.scenario_generator.generate_scenarios(graph, s_type, goal_title)
                all_scenarios.extend(scenarios)
        else:
            all_scenarios = self.scenario_generator.generate_scenarios(graph, scenario_type, goal_title)
            
        # Analyze impact of each scenario
        scenario_results = []
        for scenario in all_scenarios:
            impact_result = self.impact_analyzer.analyze_scenario_impact(
                graph, scenario, goal_title
            )
            scenario_results.append({
                "scenario": scenario,
                "impact": impact_result
            })
            
        # Find alternative paths
        alternative_paths = self.alternative_path_finder.find_alternative_paths(
            graph, goal_title
        )
        
        # Generate insights
        insights = self._generate_counterfactual_insights(scenario_results, alternative_paths)
        
        return {
            "analysis_type": "counterfactual",
            "goal_title": goal_title,
            "total_scenarios": len(scenario_results),
            "scenario_results": scenario_results,
            "alternative_paths": alternative_paths,
            "insights": insights,
            "recommendations": self._generate_recommendations(scenario_results),
            "timestamp": datetime.now().isoformat()
        }
        
    def analyze_critical_path_scenarios(self, graph: nx.DiGraph, goal_title: str) -> Dict[str, Any]:
        """Analyze scenarios focused on critical path modifications"""
        
        # Identify critical path
        critical_path = self.dependency_analyzer.find_critical_path(graph)
        
        # Generate critical path scenarios
        critical_scenarios = []
        
        for i, milestone in enumerate(critical_path):
            # Scenario: Remove milestone from critical path
            removal_scenario = {
                "type": "critical_milestone_removal",
                "milestone_removed": milestone,
                "position_in_path": i,
                "description": f"What if {milestone} was not required on the critical path?"
            }
            critical_scenarios.append(removal_scenario)
            
            # Scenario: Accelerate milestone
            acceleration_scenario = {
                "type": "critical_milestone_acceleration", 
                "milestone_accelerated": milestone,
                "position_in_path": i,
                "description": f"What if {milestone} could be completed much faster?"
            }
            critical_scenarios.append(acceleration_scenario)
            
        # Analyze each critical scenario
        results = []
        for scenario in critical_scenarios:
            impact = self.impact_analyzer.analyze_critical_path_impact(
                graph, scenario, critical_path
            )
            results.append({
                "scenario": scenario,
                "impact": impact
            })
            
        return {
            "analysis_type": "critical_path_counterfactual",
            "original_critical_path": critical_path,
            "scenarios_analyzed": len(results),
            "results": results,
            "summary": self._summarize_critical_path_analysis(results)
        }
        
    def explore_alternative_sequences(self, graph: nx.DiGraph, goal_title: str, 
                                    target_milestone: str = None) -> Dict[str, Any]:
        """Explore alternative milestone sequences to reach the goal"""
        
        sequences = self.alternative_path_finder.find_alternative_sequences(
            graph, target_milestone
        )
        
        # Analyze each sequence
        sequence_analysis = []
        for sequence in sequences:
            analysis = {
                "sequence": sequence,
                "path_length": len(sequence),
                "estimated_efficiency": self._calculate_sequence_efficiency(graph, sequence),
                "risk_factors": self._identify_sequence_risks(graph, sequence),
                "advantages": self._identify_sequence_advantages(graph, sequence)
            }
            sequence_analysis.append(analysis)
            
        # Rank sequences by viability
        ranked_sequences = sorted(
            sequence_analysis, 
            key=lambda x: x["estimated_efficiency"], 
            reverse=True
        )
        
        return {
            "analysis_type": "alternative_sequences",
            "total_sequences_found": len(sequences),
            "sequence_analysis": sequence_analysis,
            "ranked_sequences": ranked_sequences,
            "recommendations": self._recommend_best_sequences(ranked_sequences)
        }
        
    def analyze_timing_scenarios(self, milestones: List[Dict], goal_title: str) -> Dict[str, Any]:
        """Analyze scenarios with different timing modifications"""
        
        timing_scenarios = self.scenario_generator.generate_timing_scenarios(milestones)
        
        scenario_results = []
        for scenario in timing_scenarios:
            # Calculate impact of timing changes
            impact = self.impact_analyzer.analyze_timing_impact(milestones, scenario)
            
            scenario_results.append({
                "scenario": scenario,
                "impact": impact,
                "feasibility": self._assess_timing_feasibility(scenario),
                "risk_level": self._assess_timing_risk(scenario)
            })
            
        return {
            "analysis_type": "timing_counterfactual",
            "scenarios_analyzed": len(scenario_results),
            "results": scenario_results,
            "optimal_timing": self._find_optimal_timing(scenario_results),
            "timing_insights": self._generate_timing_insights(scenario_results)
        }
        
    def _generate_counterfactual_insights(self, scenario_results: List[Dict], 
                                        alternative_paths: List[Dict]) -> List[str]:
        """Generate insights from counterfactual analysis"""
        insights = []
        
        # Analyze scenario impacts
        high_impact_scenarios = [
            r for r in scenario_results 
            if r["impact"].get("impact_score", 0) > 0.7
        ]
        
        if high_impact_scenarios:
            insights.append(f"Found {len(high_impact_scenarios)} high-impact scenarios that could significantly change the outcome")
            
        # Analyze alternative paths
        if alternative_paths:
            shorter_paths = [p for p in alternative_paths if p.get("efficiency_gain", 0) > 0.2]
            if shorter_paths:
                insights.append(f"Identified {len(shorter_paths)} alternative paths that could be 20%+ more efficient")
                
        # Risk analysis
        risky_scenarios = [
            r for r in scenario_results 
            if r["impact"].get("risk_level", "low") == "high"
        ]
        
        if risky_scenarios:
            insights.append(f"Warning: {len(risky_scenarios)} scenarios show high-risk outcomes")
            
        return insights
        
    def _generate_recommendations(self, scenario_results: List[Dict]) -> List[Dict]:
        """Generate actionable recommendations from counterfactual analysis"""
        recommendations = []
        
        # Find beneficial scenarios
        beneficial_scenarios = [
            r for r in scenario_results 
            if r["impact"].get("outcome_improvement", 0) > 0.3
        ]
        
        for scenario in beneficial_scenarios[:3]:  # Top 3 beneficial scenarios
            recommendations.append({
                "type": "beneficial_modification",
                "scenario": scenario["scenario"]["type"],
                "description": scenario["scenario"].get("description", ""),
                "expected_benefit": scenario["impact"].get("outcome_improvement", 0),
                "priority": "high" if scenario["impact"].get("outcome_improvement", 0) > 0.5 else "medium"
            })
            
        # Find scenarios to avoid
        risky_scenarios = [
            r for r in scenario_results 
            if r["impact"].get("risk_level", "low") == "high"
        ]
        
        for scenario in risky_scenarios[:2]:  # Top 2 risky scenarios
            recommendations.append({
                "type": "risk_mitigation",
                "scenario": scenario["scenario"]["type"],
                "description": f"Avoid: {scenario['scenario'].get('description', '')}",
                "risk_level": scenario["impact"].get("risk_level", "unknown"),
                "priority": "critical"
            })
            
        return recommendations
    
    def _calculate_sequence_efficiency(self, graph: nx.DiGraph, sequence: List[str]) -> float:
        """Calculate efficiency score for a milestone sequence"""
        if len(sequence) <= 1:
            return 1.0
        
        # Shorter sequences are more efficient
        length_efficiency = 1.0 / len(sequence)
        
        # Check dependency alignment
        dependency_efficiency = 1.0
        total_violations = 0
        
        for i in range(len(sequence) - 1):
            current = sequence[i]
            next_item = sequence[i + 1]
            
            # Check if this order violates dependencies
            if graph.has_edge(next_item, current):  # Next should come after current
                total_violations += 1
        
        if total_violations > 0:
            dependency_efficiency = 1.0 / (1 + total_violations)
        
        return (length_efficiency + dependency_efficiency) / 2
    
    def _identify_sequence_risks(self, graph: nx.DiGraph, sequence: List[str]) -> List[str]:
        """Identify risk factors in a milestone sequence"""
        risks = []
        
        # Check for dependency violations
        violations = 0
        for i in range(len(sequence) - 1):
            current = sequence[i]
            next_item = sequence[i + 1]
            
            if graph.has_edge(next_item, current):
                violations += 1
        
        if violations > 0:
            risks.append(f"Dependency violations: {violations} milestones out of order")
        
        # Check for bottlenecks
        high_degree_nodes = [node for node in sequence if graph.degree(node) > 3]
        if high_degree_nodes:
            risks.append(f"Bottleneck nodes: {len(high_degree_nodes)} nodes with high dependencies")
        
        # Check sequence length
        if len(sequence) > 10:
            risks.append("Long sequence - high complexity risk")
        
        return risks
    
    def _identify_sequence_advantages(self, graph: nx.DiGraph, sequence: List[str]) -> List[str]:
        """Identify advantages of a milestone sequence"""
        advantages = []
        
        # Check for parallel opportunities
        independent_pairs = 0
        for i in range(len(sequence) - 1):
            for j in range(i + 1, len(sequence)):
                node1, node2 = sequence[i], sequence[j]
                if not nx.has_path(graph, node1, node2) and not nx.has_path(graph, node2, node1):
                    independent_pairs += 1
        
        if independent_pairs > 0:
            advantages.append(f"Parallel execution possible: {independent_pairs} independent milestone pairs")
        
        # Check for efficient progression
        if len(sequence) <= 6:
            advantages.append("Concise path - lower complexity and faster execution")
        
        # Check for balanced workload
        if all(graph.degree(node) <= 3 for node in sequence):
            advantages.append("Balanced dependencies - no major bottlenecks")
        
        return advantages
    
    def _recommend_best_sequences(self, ranked_sequences: List[Dict]) -> List[str]:
        """Generate recommendations for the best sequences"""
        recommendations = []
        
        if not ranked_sequences:
            return ["No alternative sequences available"]
        
        # Recommend top sequence
        best_sequence = ranked_sequences[0]
        efficiency = best_sequence.get('estimated_efficiency', 0)
        recommendations.append(f"Top recommendation: Sequence with {efficiency:.2f} efficiency score")
        
        # Check for risk-free sequences
        low_risk_sequences = [
            seq for seq in ranked_sequences 
            if len(seq.get('risk_factors', [])) == 0
        ]
        
        if low_risk_sequences:
            recommendations.append(f"Found {len(low_risk_sequences)} low-risk alternative sequences")
        
        # Check for highly parallel sequences
        parallel_sequences = [
            seq for seq in ranked_sequences 
            if any("parallel" in adv.lower() for adv in seq.get('advantages', []))
        ]
        
        if parallel_sequences:
            recommendations.append(f"Consider {len(parallel_sequences)} sequences with parallel execution opportunities")
        
        return recommendations
    
    def _find_optimal_timing(self, scenario_results: List[Dict]) -> str:
        """Find optimal timing recommendation from scenario results"""
        if not scenario_results:
            return "No timing scenarios available for analysis"
        
        # Find scenarios with best outcome improvement
        beneficial_scenarios = [
            result for result in scenario_results 
            if result.get('impact', {}).get('outcome_improvement', 0) > 0
        ]
        
        if beneficial_scenarios:
            best_scenario = max(
                beneficial_scenarios, 
                key=lambda x: x.get('impact', {}).get('outcome_improvement', 0)
            )
            
            scenario_type = best_scenario.get('scenario', {}).get('type', 'unknown')
            improvement = best_scenario.get('impact', {}).get('outcome_improvement', 0)
            
            if 'acceleration' in scenario_type:
                return f"Optimal timing: Accelerate key milestones for {improvement:.1%} improvement"
            elif 'delay' in scenario_type:
                return f"Optimal timing: Strategic delays could improve outcomes by {improvement:.1%}"
            else:
                return f"Optimal timing: {scenario_type.replace('_', ' ')} approach shows {improvement:.1%} improvement"
        
        # If no beneficial scenarios, recommend baseline
        return "Optimal timing: Current timeline appears well-balanced"
    
    def _generate_timing_insights(self, scenario_results: List[Dict]) -> List[str]:
        """Generate insights from timing scenario analysis"""
        insights = []
        
        if not scenario_results:
            return ["No timing scenarios to analyze"]
        
        # Analyze acceleration scenarios
        acceleration_scenarios = [
            result for result in scenario_results 
            if 'acceleration' in result.get('scenario', {}).get('type', '')
        ]
        
        if acceleration_scenarios:
            avg_improvement = sum(
                r.get('impact', {}).get('outcome_improvement', 0) 
                for r in acceleration_scenarios
            ) / len(acceleration_scenarios)
            
            if avg_improvement > 0.1:
                insights.append(f"Acceleration strategies show average {avg_improvement:.1%} improvement potential")
            else:
                insights.append("Acceleration may not provide significant benefits")
        
        # Analyze delay scenarios
        delay_scenarios = [
            result for result in scenario_results 
            if 'delay' in result.get('scenario', {}).get('type', '')
        ]
        
        if delay_scenarios:
            high_risk_delays = [
                r for r in delay_scenarios 
                if r.get('risk_level', 'low') == 'high'
            ]
            
            if high_risk_delays:
                insights.append(f"Warning: {len(high_risk_delays)} delay scenarios show high risk")
        
        # Overall timing insights
        feasible_scenarios = [
            result for result in scenario_results 
            if result.get('feasibility', 'unknown') in ['feasible', 'realistic']
        ]
        
        if feasible_scenarios:
            insights.append(f"{len(feasible_scenarios)} timing modifications appear feasible")
        
        return insights
    
    def _assess_timing_feasibility(self, scenario: Dict) -> str:
        """Assess feasibility of a timing scenario"""
        scenario_type = scenario.get('type', '')
        
        if 'acceleration' in scenario_type:
            time_reduction = scenario.get('time_reduction', 0)
            if time_reduction > 0.5:  # More than 50% faster
                return "challenging"
            elif time_reduction > 0.2:  # 20-50% faster
                return "realistic"
            else:
                return "feasible"
        
        elif 'delay' in scenario_type:
            time_increase = scenario.get('time_increase', 1.0)
            if time_increase > 3.0:  # More than 3x longer
                return "unrealistic"
            elif time_increase > 2.0:  # 2-3x longer
                return "challenging"
            else:
                return "feasible"
        
        return "unknown"
    
    def _assess_timing_risk(self, scenario: Dict) -> str:
        """Assess risk level of a timing scenario"""
        scenario_type = scenario.get('type', '')
        
        if 'acceleration' in scenario_type:
            time_reduction = scenario.get('time_reduction', 0)
            if time_reduction > 0.5:
                return "high"  # Aggressive acceleration
            elif time_reduction > 0.3:
                return "medium"
            else:
                return "low"
        
        elif 'delay' in scenario_type:
            time_increase = scenario.get('time_increase', 1.0)
            if time_increase > 2.0:
                return "high"  # Long delays
            elif time_increase > 1.5:
                return "medium"
            else:
                return "low"
        
        return "medium"
    
    def _summarize_critical_path_analysis(self, results: List[Dict]) -> Dict[str, Any]:
        """Summarize critical path analysis results"""
        if not results:
            return {"summary": "No critical path scenarios analyzed"}
        
        # Count scenario types
        removal_scenarios = sum(1 for r in results if 'removal' in r.get('scenario', {}).get('type', ''))
        acceleration_scenarios = sum(1 for r in results if 'acceleration' in r.get('scenario', {}).get('type', ''))
        
        # Find highest impact scenario
        max_impact = 0
        most_critical_scenario = None
        
        for result in results:
            impact_score = result.get('impact', {}).get('impact_score', 0)
            if impact_score > max_impact:
                max_impact = impact_score
                most_critical_scenario = result.get('scenario', {})
        
        summary = {
            "total_scenarios": len(results),
            "removal_scenarios": removal_scenarios,
            "acceleration_scenarios": acceleration_scenarios,
            "highest_impact_score": max_impact,
            "most_critical_milestone": most_critical_scenario.get('milestone_removed') if most_critical_scenario else None,
            "summary": f"Analyzed {len(results)} critical path scenarios with maximum impact score of {max_impact:.2f}"
        }
        
        return summary


class ScenarioGenerator:
    """Generates different types of counterfactual scenarios"""
    
    def __init__(self):
        pass
        
    def generate_scenarios(self, graph: nx.DiGraph, scenario_type: str, 
                         goal_title: str) -> List[Dict]:
        """Generate scenarios of specified type"""
        
        if scenario_type == "milestone_removal":
            return self._generate_milestone_removal_scenarios(graph)
        elif scenario_type == "timing_modification":
            return self._generate_timing_modification_scenarios(graph)
        elif scenario_type == "resource_change":
            return self._generate_resource_change_scenarios(graph)
        elif scenario_type == "alternative_approach":
            return self._generate_alternative_approach_scenarios(graph)
        elif scenario_type == "prerequisite_bypass":
            return self._generate_prerequisite_bypass_scenarios(graph)
        elif scenario_type == "collaboration_addition":
            return self._generate_collaboration_scenarios(graph)
        else:
            return []
            
    def _generate_milestone_removal_scenarios(self, graph: nx.DiGraph) -> List[Dict]:
        """Generate scenarios where specific milestones are removed"""
        scenarios = []
        
        for node in graph.nodes():
            if node.startswith("milestone_"):
                scenarios.append({
                    "type": "milestone_removal",
                    "milestone_removed": node,
                    "description": f"What if milestone '{node}' was not necessary?",
                    "modified_graph": self._remove_node_from_graph(graph, node)
                })
                
        return scenarios
        
    def _generate_timing_modification_scenarios(self, graph: nx.DiGraph) -> List[Dict]:
        """Generate scenarios with modified timing/durations"""
        scenarios = []
        
        # Scenario: Accelerate all milestones by 50%
        scenarios.append({
            "type": "global_acceleration",
            "modification": "50% faster completion",
            "description": "What if all milestones could be completed 50% faster?"
        })
        
        # Scenario: Delay critical milestones
        scenarios.append({
            "type": "critical_delays",
            "modification": "Critical milestones delayed",
            "description": "What if critical milestones faced significant delays?"
        })
        
        return scenarios
        
    def _generate_resource_change_scenarios(self, graph: nx.DiGraph) -> List[Dict]:
        """Generate scenarios with different resource availability"""
        scenarios = []
        
        resource_scenarios = [
            {"change": "double_budget", "description": "What if budget was doubled?"},
            {"change": "half_time", "description": "What if available time was halved?"},
            {"change": "unlimited_mentorship", "description": "What if unlimited expert mentorship was available?"},
            {"change": "no_external_help", "description": "What if no external help was available?"}
        ]
        
        for scenario in resource_scenarios:
            scenarios.append({
                "type": "resource_change",
                "resource_modification": scenario["change"],
                "description": scenario["description"]
            })
            
        return scenarios
        
    def _generate_alternative_approach_scenarios(self, graph: nx.DiGraph) -> List[Dict]:
        """Generate scenarios with completely different approaches"""
        scenarios = []
        
        # Bottom-up vs Top-down approach
        scenarios.append({
            "type": "approach_reversal",
            "description": "What if a bottom-up approach was taken instead of top-down?",
            "modification": "reverse_milestone_order"
        })
        
        # Parallel vs Sequential approach
        scenarios.append({
            "type": "parallelization",
            "description": "What if multiple milestones could be pursued in parallel?",
            "modification": "parallel_execution"
        })
        
        return scenarios
        
    def _generate_prerequisite_bypass_scenarios(self, graph: nx.DiGraph) -> List[Dict]:
        """Generate scenarios where prerequisites are bypassed"""
        scenarios = []
        
        # Find nodes with prerequisites
        for node in graph.nodes():
            predecessors = list(graph.predecessors(node))
            if len(predecessors) > 1:  # Has multiple prerequisites
                scenarios.append({
                    "type": "prerequisite_bypass",
                    "milestone": node,
                    "bypassed_prerequisites": predecessors[:-1],  # Keep only one prerequisite
                    "description": f"What if prerequisites for {node} could be bypassed?"
                })
                
        return scenarios
        
    def _generate_collaboration_scenarios(self, graph: nx.DiGraph) -> List[Dict]:
        """Generate scenarios with additional collaborations"""
        scenarios = []
        
        collaboration_types = [
            {"type": "technical_mentor", "description": "What if a technical mentor was available?"},
            {"type": "business_partner", "description": "What if a business partner joined?"},
            {"type": "team_expansion", "description": "What if the team was expanded?"},
            {"type": "industry_connections", "description": "What if strong industry connections were available?"}
        ]
        
        for collab in collaboration_types:
            scenarios.append({
                "type": "collaboration_addition",
                "collaboration_type": collab["type"],
                "description": collab["description"]
            })
            
        return scenarios
        
    def generate_timing_scenarios(self, milestones: List[Dict]) -> List[Dict]:
        """Generate timing-specific scenarios"""
        scenarios = []
        
        for milestone in milestones:
            milestone_id = milestone.get("id", "")
            
            # Acceleration scenario
            scenarios.append({
                "type": "milestone_acceleration",
                "milestone_id": milestone_id,
                "time_reduction": 0.5,  # 50% faster
                "description": f"What if {milestone.get('name', milestone_id)} could be completed 50% faster?"
            })
            
            # Delay scenario
            scenarios.append({
                "type": "milestone_delay",
                "milestone_id": milestone_id,
                "time_increase": 2.0,  # 2x longer
                "description": f"What if {milestone.get('name', milestone_id)} took twice as long?"
            })
            
        return scenarios
        
    def _remove_node_from_graph(self, graph: nx.DiGraph, node: str) -> nx.DiGraph:
        """Create modified graph with node removed"""
        modified_graph = graph.copy()
        if node in modified_graph:
            # Connect predecessors to successors before removing node
            predecessors = list(modified_graph.predecessors(node))
            successors = list(modified_graph.successors(node))
            
            for pred in predecessors:
                for succ in successors:
                    modified_graph.add_edge(pred, succ)
                    
            modified_graph.remove_node(node)
            
        return modified_graph


class ImpactAnalyzer:
    """Analyzes the impact of counterfactual scenarios"""
    
    def __init__(self):
        pass
        
    def analyze_scenario_impact(self, original_graph: nx.DiGraph, scenario: Dict, 
                              goal_title: str) -> Dict[str, Any]:
        """Analyze the impact of a specific scenario"""
        
        scenario_type = scenario.get("type", "unknown")
        
        if scenario_type == "milestone_removal":
            return self._analyze_removal_impact(original_graph, scenario)
        elif scenario_type in ["global_acceleration", "critical_delays"]:
            return self._analyze_timing_impact(original_graph, scenario)
        elif scenario_type == "resource_change":
            return self._analyze_resource_impact(original_graph, scenario)
        else:
            return self._analyze_generic_impact(original_graph, scenario)
            
    def _analyze_removal_impact(self, graph: nx.DiGraph, scenario: Dict) -> Dict[str, Any]:
        """Analyze impact of removing a milestone"""
        removed_milestone = scenario.get("milestone_removed", "")
        modified_graph = scenario.get("modified_graph", graph)
        
        # Calculate metrics before and after
        original_metrics = self._calculate_graph_metrics(graph)
        modified_metrics = self._calculate_graph_metrics(modified_graph)
        
        # Analyze connectivity impact
        connectivity_impact = self._analyze_connectivity_change(graph, modified_graph)
        
        # Calculate impact score
        impact_score = self._calculate_impact_score(original_metrics, modified_metrics)
        
        return {
            "impact_type": "milestone_removal",
            "removed_milestone": removed_milestone,
            "impact_score": impact_score,
            "connectivity_change": connectivity_impact,
            "path_length_change": modified_metrics["avg_path_length"] - original_metrics["avg_path_length"],
            "complexity_change": modified_metrics["graph_density"] - original_metrics["graph_density"],
            "risk_level": self._assess_removal_risk(graph, removed_milestone),
            "outcome_improvement": self._estimate_outcome_improvement(original_metrics, modified_metrics)
        }
        
    def _analyze_timing_impact(self, graph: nx.DiGraph, scenario: Dict) -> Dict[str, Any]:
        """Analyze impact of timing modifications"""
        
        modification_type = scenario.get("modification", "unknown")
        
        if modification_type == "50% faster completion":
            time_savings = 0.5
            risk_increase = 0.3  # Faster execution often increases risk
        elif modification_type == "Critical milestones delayed":
            time_savings = -0.5  # Negative savings (delay)
            risk_increase = 0.2
        else:
            time_savings = 0
            risk_increase = 0
            
        return {
            "impact_type": "timing_modification",
            "time_impact": time_savings,
            "risk_impact": risk_increase,
            "impact_score": abs(time_savings),
            "outcome_improvement": max(0, time_savings - risk_increase),
            "feasibility": self._assess_timing_feasibility(scenario)
        }
        
    def analyze_critical_path_impact(self, graph: nx.DiGraph, scenario: Dict, critical_path: List[str]) -> Dict[str, Any]:
        """Analyze impact of modifications to critical path milestones"""
        
        scenario_type = scenario.get("type", "unknown")
        
        if "removal" in scenario_type:
            # Analyze removing a milestone from critical path
            removed_milestone = scenario.get("milestone_removed", "")
            position = scenario.get("position_in_path", 0)
            
            # Create modified graph
            modified_graph = graph.copy()
            if removed_milestone in modified_graph:
                # Connect predecessors to successors
                predecessors = list(modified_graph.predecessors(removed_milestone))
                successors = list(modified_graph.successors(removed_milestone))
                
                for pred in predecessors:
                    for succ in successors:
                        modified_graph.add_edge(pred, succ)
                
                modified_graph.remove_node(removed_milestone)
            
            # Calculate impact
            original_metrics = self._calculate_graph_metrics(graph)
            modified_metrics = self._calculate_graph_metrics(modified_graph)
            
            # Critical path specific metrics
            path_disruption = 1.0 if removed_milestone in critical_path else 0.5
            path_position_impact = position / max(len(critical_path), 1)  # Earlier milestones have higher impact
            
            return {
                "impact_type": "critical_path_removal",
                "removed_milestone": removed_milestone,
                "impact_score": self._calculate_impact_score(original_metrics, modified_metrics) * path_disruption,
                "path_disruption": path_disruption,
                "position_impact": path_position_impact,
                "connectivity_change": self._analyze_connectivity_change(graph, modified_graph),
                "risk_level": "high" if path_disruption > 0.8 else "medium",
                "outcome_improvement": self._estimate_outcome_improvement(original_metrics, modified_metrics)
            }
            
        elif "acceleration" in scenario_type:
            # Analyze accelerating a critical path milestone
            accelerated_milestone = scenario.get("milestone_accelerated", "")
            position = scenario.get("position_in_path", 0)
            
            # Acceleration impact increases for earlier milestones
            time_savings = 0.5 * (1 - position / max(len(critical_path), 1))
            risk_increase = 0.3 * time_savings  # Higher acceleration = higher risk
            
            return {
                "impact_type": "critical_path_acceleration",
                "accelerated_milestone": accelerated_milestone,
                "impact_score": time_savings,
                "time_savings": time_savings,
                "risk_increase": risk_increase,
                "position_impact": position / max(len(critical_path), 1),
                "outcome_improvement": max(0, time_savings - risk_increase),
                "feasibility": "challenging" if time_savings > 0.4 else "realistic"
            }
        
        else:
            # Generic critical path impact
            return {
                "impact_type": "critical_path_generic",
                "scenario_type": scenario_type,
                "impact_score": 0.5,
                "outcome_improvement": 0.0,
                "risk_level": "medium"
            }
    
    def analyze_timing_impact(self, milestones: List[Dict], scenario: Dict) -> Dict[str, Any]:
        """Analyze impact of timing modifications on milestone list"""
        
        scenario_type = scenario.get("type", "unknown")
        
        if "acceleration" in scenario_type:
            milestone_id = scenario.get("milestone_id", "")
            time_reduction = scenario.get("time_reduction", 0)
            
            # Find the milestone in the list
            target_milestone = None
            for milestone in milestones:
                if milestone.get("milestone_id") == milestone_id or milestone.get("id") == milestone_id:
                    target_milestone = milestone
                    break
            
            if target_milestone:
                # Calculate impact based on milestone importance and position
                importance = target_milestone.get("score", 5) / 10.0  # Normalize to 0-1
                impact_score = time_reduction * importance
                
                # Risk assessment
                risk_level = "high" if time_reduction > 0.5 else "medium" if time_reduction > 0.3 else "low"
                
                return {
                    "impact_type": "milestone_acceleration",
                    "milestone_id": milestone_id,
                    "time_reduction": time_reduction,
                    "impact_score": impact_score,
                    "importance_factor": importance,
                    "risk_level": risk_level,
                    "outcome_improvement": max(0, impact_score - (0.3 if risk_level == "high" else 0.1)),
                    "feasibility": "challenging" if time_reduction > 0.5 else "realistic"
                }
            
        elif "delay" in scenario_type:
            milestone_id = scenario.get("milestone_id", "")
            time_increase = scenario.get("time_increase", 1.0)
            
            # Find the milestone in the list
            target_milestone = None
            for milestone in milestones:
                if milestone.get("milestone_id") == milestone_id or milestone.get("id") == milestone_id:
                    target_milestone = milestone
                    break
            
            if target_milestone:
                # Delays generally have negative impact
                importance = target_milestone.get("score", 5) / 10.0
                impact_score = (time_increase - 1.0) * importance  # Impact increases with delay
                
                # Risk assessment for delays
                risk_level = "high" if time_increase > 2.0 else "medium" if time_increase > 1.5 else "low"
                
                return {
                    "impact_type": "milestone_delay",
                    "milestone_id": milestone_id,
                    "time_increase": time_increase,
                    "impact_score": impact_score,
                    "importance_factor": importance,
                    "risk_level": risk_level,
                    "outcome_improvement": -impact_score,  # Delays typically worsen outcomes
                    "feasibility": "realistic" if time_increase < 2.0 else "challenging"
                }
        
        # Generic timing impact
        return {
            "impact_type": "timing_generic",
            "scenario_type": scenario_type,
            "impact_score": 0.3,
            "outcome_improvement": 0.0,
            "risk_level": "medium",
            "feasibility": "unknown"
        }
        
    def _analyze_resource_impact(self, graph: nx.DiGraph, scenario: Dict) -> Dict[str, Any]:
        """Analyze impact of resource changes"""
        
        resource_mod = scenario.get("resource_modification", "")
        
        impact_mapping = {
            "double_budget": {"outcome_improvement": 0.4, "risk_reduction": 0.2},
            "half_time": {"outcome_improvement": -0.3, "risk_increase": 0.4},
            "unlimited_mentorship": {"outcome_improvement": 0.6, "risk_reduction": 0.3},
            "no_external_help": {"outcome_improvement": -0.5, "risk_increase": 0.5}
        }
        
        impact_data = impact_mapping.get(resource_mod, {"outcome_improvement": 0, "risk_change": 0})
        
        return {
            "impact_type": "resource_change",
            "resource_modification": resource_mod,
            "outcome_improvement": impact_data.get("outcome_improvement", 0),
            "risk_change": impact_data.get("risk_reduction", 0) - impact_data.get("risk_increase", 0),
            "impact_score": abs(impact_data.get("outcome_improvement", 0)),
            "feasibility": self._assess_resource_feasibility(resource_mod)
        }
        
    def _analyze_generic_impact(self, graph: nx.DiGraph, scenario: Dict) -> Dict[str, Any]:
        """Generic impact analysis for unknown scenario types"""
        
        return {
            "impact_type": "generic",
            "scenario_type": scenario.get("type", "unknown"),
            "impact_score": 0.5,  # Medium impact by default
            "outcome_improvement": 0.0,
            "risk_level": "medium",
            "note": "Generic impact analysis - specific metrics not available"
        }
        
    def _calculate_graph_metrics(self, graph: nx.DiGraph) -> Dict[str, float]:
        """Calculate basic graph metrics"""
        if len(graph.nodes()) == 0:
            return {"avg_path_length": 0, "graph_density": 0, "connectivity": 0}
            
        try:
            # Average shortest path length
            if nx.is_connected(graph.to_undirected()):
                avg_path_length = nx.average_shortest_path_length(graph)
            else:
                avg_path_length = float('inf')
        except:
            avg_path_length = 0
            
        # Graph density
        graph_density = nx.density(graph)
        
        # Connectivity (number of connected components)
        connectivity = nx.number_weakly_connected_components(graph)
        
        return {
            "avg_path_length": avg_path_length,
            "graph_density": graph_density,
            "connectivity": connectivity
        }
        
    def _calculate_impact_score(self, original_metrics: Dict, modified_metrics: Dict) -> float:
        """Calculate overall impact score between 0 and 1"""
        
        # Compare key metrics
        path_length_change = abs(modified_metrics["avg_path_length"] - original_metrics["avg_path_length"])
        density_change = abs(modified_metrics["graph_density"] - original_metrics["graph_density"])
        connectivity_change = abs(modified_metrics["connectivity"] - original_metrics["connectivity"])
        
        # Normalize and combine (simple weighted average)
        normalized_changes = [
            min(path_length_change / 10, 1.0),  # Normalize path length change
            density_change,  # Density is already 0-1
            min(connectivity_change / 5, 1.0)   # Normalize connectivity change
        ]
        
        return sum(normalized_changes) / len(normalized_changes)
        
    def _analyze_connectivity_change(self, original_graph: nx.DiGraph, 
                                   modified_graph: nx.DiGraph) -> Dict[str, Any]:
        """Analyze how connectivity changed between graphs"""
        
        original_components = nx.number_weakly_connected_components(original_graph)
        modified_components = nx.number_weakly_connected_components(modified_graph)
        
        return {
            "original_components": original_components,
            "modified_components": modified_components,
            "component_change": modified_components - original_components,
            "connectivity_preserved": modified_components <= original_components
        }
        
    def _assess_removal_risk(self, graph: nx.DiGraph, milestone: str) -> str:
        """Assess risk level of removing a specific milestone"""
        
        if milestone not in graph:
            return "low"
            
        # High risk if milestone has many dependents
        successors = list(graph.successors(milestone))
        predecessors = list(graph.predecessors(milestone))
        
        total_connections = len(successors) + len(predecessors)
        
        if total_connections >= 5:
            return "high"
        elif total_connections >= 2:
            return "medium"
        else:
            return "low"
            
    def _estimate_outcome_improvement(self, original_metrics: Dict, 
                                    modified_metrics: Dict) -> float:
        """Estimate if the modification improves the outcome"""
        
        # Shorter average path length is generally better
        path_improvement = (original_metrics["avg_path_length"] - modified_metrics["avg_path_length"]) / 10
        
        # More connected (fewer components) is generally better
        connectivity_improvement = (original_metrics["connectivity"] - modified_metrics["connectivity"]) / 5
        
        # Combine improvements
        total_improvement = (path_improvement + connectivity_improvement) / 2
        
        # Clamp between -1 and 1
        return max(-1.0, min(1.0, total_improvement))
        
    def _assess_timing_feasibility(self, scenario: Dict) -> str:
        """Assess feasibility of timing modifications"""
        
        modification = scenario.get("modification", "")
        
        if "50% faster" in modification:
            return "challenging"  # Possible but difficult
        elif "delayed" in modification:
            return "feasible"     # Usually possible but undesirable
        else:
            return "unknown"
            
    def _assess_resource_feasibility(self, resource_modification: str) -> str:
        """Assess feasibility of resource modifications"""
        
        feasibility_map = {
            "double_budget": "challenging",
            "half_time": "realistic",
            "unlimited_mentorship": "unrealistic",
            "no_external_help": "realistic"
        }
        
        return feasibility_map.get(resource_modification, "unknown")


class AlternativePathFinder:
    """Finds alternative paths and sequences to achieve goals"""
    
    def __init__(self):
        pass
        
    def find_alternative_paths(self, graph: nx.DiGraph, goal_title: str) -> List[Dict]:
        """Find alternative paths through the milestone graph"""
        
        # Identify start and end nodes
        start_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
        end_nodes = [n for n in graph.nodes() if graph.out_degree(n) == 0]
        
        alternative_paths = []
        
        for start in start_nodes:
            for end in end_nodes:
                # Find all simple paths
                try:
                    paths = list(nx.all_simple_paths(graph, start, end, cutoff=10))
                    
                    for path in paths:
                        path_analysis = {
                            "path": path,
                            "length": len(path),
                            "start_milestone": start,
                            "end_milestone": end,
                            "efficiency_score": self._calculate_path_efficiency(graph, path),
                            "risk_factors": self._identify_path_risks(graph, path)
                        }
                        alternative_paths.append(path_analysis)
                        
                except nx.NetworkXNoPath:
                    continue
                    
        # Sort by efficiency
        alternative_paths.sort(key=lambda x: x["efficiency_score"], reverse=True)
        
        return alternative_paths
        
    def find_alternative_sequences(self, graph: nx.DiGraph, 
                                 target_milestone: str = None) -> List[List[str]]:
        """Find alternative milestone sequences"""
        
        sequences = []
        
        # Topological sort to get one valid sequence
        try:
            base_sequence = list(nx.topological_sort(graph))
            sequences.append(base_sequence)
        except nx.NetworkXError:
            # Graph has cycles, use approximate ordering
            base_sequence = list(graph.nodes())
            sequences.append(base_sequence)
            
        # Generate variations by swapping independent milestones
        for i in range(len(base_sequence) - 1):
            for j in range(i + 1, len(base_sequence)):
                node1, node2 = base_sequence[i], base_sequence[j]
                
                # Check if swapping is valid (no dependency violations)
                if self._can_swap_milestones(graph, node1, node2):
                    swapped_sequence = base_sequence.copy()
                    swapped_sequence[i], swapped_sequence[j] = swapped_sequence[j], swapped_sequence[i]
                    sequences.append(swapped_sequence)
                    
        # Remove duplicates
        unique_sequences = []
        for seq in sequences:
            if seq not in unique_sequences:
                unique_sequences.append(seq)
                
        return unique_sequences
        
    def _calculate_path_efficiency(self, graph: nx.DiGraph, path: List[str]) -> float:
        """Calculate efficiency score for a path (0-1, higher is better)"""
        
        if len(path) <= 1:
            return 1.0
            
        # Shorter paths are generally more efficient
        length_efficiency = 1.0 / len(path)
        
        # Paths with fewer dependencies are more efficient
        total_dependencies = sum(graph.in_degree(node) for node in path)
        dependency_efficiency = 1.0 / (1 + total_dependencies / len(path))
        
        # Combined efficiency
        return (length_efficiency + dependency_efficiency) / 2
        
    def _identify_path_risks(self, graph: nx.DiGraph, path: List[str]) -> List[str]:
        """Identify risk factors in a path"""
        risks = []
        
        # Check for bottlenecks (nodes with many dependencies)
        for node in path:
            if graph.in_degree(node) > 3:
                risks.append(f"High dependency bottleneck at {node}")
                
        # Check for critical single points of failure
        for node in path:
            if graph.out_degree(node) > 3:
                risks.append(f"Critical hub at {node} - many dependents")
                
        # Check path length
        if len(path) > 8:
            risks.append("Long path - high complexity risk")
            
        return risks
        
    def _can_swap_milestones(self, graph: nx.DiGraph, node1: str, node2: str) -> bool:
        """Check if two milestones can be swapped without violating dependencies"""
        
        # Can't swap if there's a direct dependency between them
        if graph.has_edge(node1, node2) or graph.has_edge(node2, node1):
            return False
            
        # Can't swap if they share critical dependencies
        node1_deps = set(graph.predecessors(node1))
        node2_deps = set(graph.predecessors(node2))
        
        if node1_deps.intersection(node2_deps):
            return False
            
        return True


class DependencyAnalyzer:
    """Analyzes dependencies and critical paths in roadmaps"""
    
    def __init__(self):
        pass
        
    def find_critical_path(self, graph: nx.DiGraph) -> List[str]:
        """Find the critical path through the milestone graph"""
        
        try:
            # Use longest path algorithm (convert to negative weights)
            longest_path = nx.dag_longest_path(graph)
            return longest_path
        except:
            # Fallback: find path through highest degree nodes
            return self._find_high_degree_path(graph)
            
    def _find_high_degree_path(self, graph: nx.DiGraph) -> List[str]:
        """Fallback method to find critical path using node degrees"""
        
        # Sort nodes by total degree (in + out)
        nodes_by_degree = sorted(
            graph.nodes(), 
            key=lambda x: graph.in_degree(x) + graph.out_degree(x), 
            reverse=True
        )
        
        # Build path through highest degree nodes
        critical_path = []
        used_nodes = set()
        
        for node in nodes_by_degree:
            if node not in used_nodes:
                critical_path.append(node)
                used_nodes.add(node)
                
                # Limit path length
                if len(critical_path) >= 8:
                    break
                    
        return critical_path
