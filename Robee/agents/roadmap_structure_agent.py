"""
Roadmap Structure Agent - Manages roadmap data structure and organization
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import networkx as nx
from streamlit_agraph import Node, Edge

class RoadmapStructureAgent:
    """
    Primary Responsibilities:
    - Manage roadmap data structure and organization
    - Handle adjacency matrix operations
    - Manage milestone relationships and connections
    - Generate graph components for visualization
    """
    
    def __init__(self):
        self.data_manager = DataStructureManager()
        self.matrix_manager = AdjacencyMatrixManager()
        self.milestone_manager = MilestoneManager()
        self.graph_generator = GraphComponentGenerator()
        
    def load_roadmap_data(self, json_data: Dict) -> bool:
        """Load and process roadmap data"""
        try:
            self.data_manager.load_data(json_data)
            self.matrix_manager.build_adjacency_matrices(self.data_manager.data)
            return True
        except Exception as e:
            print(f"Error loading roadmap data: {e}")
            return False
            
    def add_milestone(self, person: str, goal_id: str, milestone_name: str, 
                     score: int, parent_id: str, is_causal: bool = False, 
                     resources: List[str] = None) -> bool:
        """Add a new milestone to the roadmap"""
        return self.milestone_manager.add_milestone(
            self.data_manager, self.matrix_manager,
            person, goal_id, milestone_name, score, parent_id, is_causal, resources
        )
        
    def get_roadmap_structure(self, person: str, goal_id: str, goal_color: str = None) -> Dict:
        """Get complete roadmap structure for a person and goal"""
        return {
            "data": self.data_manager.get_goal_data(person, goal_id),
            "matrix": self.matrix_manager.get_adjacency_matrix(person, goal_id),
            "components": self.graph_generator.get_graph_components(
                self.matrix_manager, person, goal_id, goal_color
            )
        }
        
    def get_milestone_info(self, person: str, milestone_id: str) -> Optional[Dict]:
        """Get detailed information about a specific milestone"""
        return self.milestone_manager.get_milestone_info(self.data_manager.data, person, milestone_id)
        
    def find_goal_for_milestone(self, person: str, milestone_id: str) -> Optional[str]:
        """Find which goal contains a specific milestone"""
        return self.milestone_manager.find_goal_for_milestone(self.data_manager.data, person, milestone_id)
        
    def get_sub_roadmap_groups(self, person: str, goal_id: str) -> List[List[str]]:
        """Get connected components within a roadmap"""
        return self.matrix_manager.get_sub_roadmap_groups(person, goal_id)
        
    def save_roadmap_data(self) -> str:
        """Save current roadmap data to JSON format"""
        return self.data_manager.save_data()
        
    def get_persons(self) -> List[str]:
        """Get list of all persons in the dataset"""
        return self.data_manager.get_persons()
        
    def get_goals(self, person: str) -> Dict:
        """Get all goals for a specific person"""
        return self.data_manager.get_goals(person)


class DataStructureManager:
    """Manages core data structures for roadmaps"""
    
    def __init__(self):
        self.data = {}
        
    def load_data(self, json_data: Dict):
        """Load data from JSON format"""
        if isinstance(json_data, str):
            self.data = json.loads(json_data)
        else:
            self.data = json_data.copy()
            
    def save_data(self) -> str:
        """Save data to JSON format"""
        return json.dumps(self.data, indent=2, default=str)
        
    def get_persons(self) -> List[str]:
        """Get list of all persons"""
        return list(self.data.keys())
        
    def get_goals(self, person: str) -> Dict:
        """Get all goals for a person"""
        person_data = self.data.get(person, {})
        
        # Handle both 'goals' and 'roadmaps' data structure formats
        if isinstance(person_data, dict):
            if 'goals' in person_data:
                return person_data['goals']
            elif 'roadmaps' in person_data:
                return person_data['roadmaps']
        return {}
        
    def get_goal_data(self, person: str, goal_id: str) -> Optional[Dict]:
        """Get specific goal data"""
        goals = self.get_goals(person)
        return goals.get(goal_id)
    
    def get_goal(self, person: str, goal_id: str) -> Optional[Dict]:
        """Get specific goal data - alias for get_goal_data for consistency"""
        return self.get_goal_data(person, goal_id)
        
    def add_person(self, person: str) -> bool:
        """Add a new person to the dataset"""
        if person not in self.data:
            # Use 'roadmaps' for consistency with the interface
            self.data[person] = {"roadmaps": {}}
            return True
        return False
        
    def add_goal(self, person: str, goal_id: str, goal_data: Dict) -> bool:
        """Add a new goal for a person"""
        if person not in self.data:
            self.add_person(person)
            
        # Handle both 'goals' and 'roadmaps' data structure formats
        person_data = self.data[person]
        goals_key = 'goals' if 'goals' in person_data else 'roadmaps'
        
        if goals_key not in person_data:
            person_data[goals_key] = {}
            
        if goal_id not in person_data[goals_key]:
            person_data[goals_key][goal_id] = goal_data
            return True
        return False
        
    def update_milestone(self, person: str, goal_id: str, milestone_id: str, 
                        milestone_data: Dict) -> bool:
        """Update milestone data"""
        goal_data = self.get_goal_data(person, goal_id)
        if goal_data and 'milestones' in goal_data:
            if milestone_id in goal_data['milestones']:
                goal_data['milestones'][milestone_id].update(milestone_data)
                return True
            else:
                goal_data['milestones'][milestone_id] = milestone_data
                return True
        return False
    
    def update_goals(self, person: str, goals_data: Dict) -> bool:
        """Update all goals for a person"""
        try:
            if person not in self.data:
                self.data[person] = {}
            
            # Handle both 'goals' and 'roadmaps' formats
            if 'goals' in self.data[person]:
                self.data[person]['goals'] = goals_data
            else:
                self.data[person]['roadmaps'] = goals_data
            return True
        except Exception as e:
            print(f"ERROR updating goals for {person}: {e}")
            return False


class AdjacencyMatrixManager:
    """Manages adjacency matrices for graph representation"""
    
    def __init__(self):
        self.adjacency_matrices = {}
        
    def build_adjacency_matrices(self, data: Dict):
        """Build adjacency matrices for all persons and goals"""
        self.adjacency_matrices = {}
        
        for person, person_data in data.items():
            if isinstance(person_data, dict):
                # Handle both 'goals' and 'roadmaps' data structure formats
                goals_data = None
                if 'goals' in person_data:
                    goals_data = person_data['goals']
                elif 'roadmaps' in person_data:
                    goals_data = person_data['roadmaps']
                    
                if goals_data:
                    self.adjacency_matrices[person] = {}
                    
                    for goal_id, goal_data in goals_data.items():
                        matrix_data = self._create_adjacency_matrix(goal_id, goal_data)
                        self.adjacency_matrices[person][goal_id] = matrix_data
                    
    def _create_adjacency_matrix(self, goal_id: str, goal_data: Dict) -> Dict:
        """Create adjacency matrix for a specific goal"""
        milestones = goal_data.get('milestones', {})
        
        # Create node list starting with goal
        nodes = [goal_id]
        node_to_index = {goal_id: 0}
        
        # Add all milestones as nodes
        for ms_id in milestones.keys():
            nodes.append(ms_id)
            node_to_index[ms_id] = len(nodes) - 1
            
        n = len(nodes)
        adjacency_matrix = [[0] * n for _ in range(n)]
        
        goal_idx = node_to_index[goal_id]
        
        # Collect milestones with causal predecessors
        milestones_with_causes_predecessors = set()
        for ms_id, milestone in milestones.items():
            causal_relationships = milestone.get('causal_relationships', [])
            if causal_relationships:
                milestones_with_causes_predecessors.add(ms_id)
                
        # Add HAS_MILESTONE edges (goal -> milestone) for milestones without causal predecessors
        has_any_causes = any(len(milestone.get('causal_relationships', [])) > 0 
                           for milestone in milestones.values())
        
        for ms_id, milestone in milestones.items():
            ms_idx = node_to_index[ms_id]
            
            # Connect goal to milestone if no causal predecessors or no causal relationships exist
            if ms_id not in milestones_with_causes_predecessors or not has_any_causes:
                adjacency_matrix[goal_idx][ms_idx] = 1
                
        # Add CAUSES edges based on causal relationships
        causes_added = 0
        for ms_id, milestone in milestones.items():
            ms_idx = node_to_index[ms_id]
            causal_relationships = milestone.get('causal_relationships', [])
            
            for rel in causal_relationships:
                predecessor_id = rel.get('prerequisite_id')
                if predecessor_id and predecessor_id in node_to_index:
                    pred_idx = node_to_index[predecessor_id]
                    adjacency_matrix[pred_idx][ms_idx] = 1
                    causes_added += 1
                    
        # Fallback: if no milestones connected to goal, connect all
        goal_connections = sum(adjacency_matrix[goal_idx])
        if goal_connections == 0 and milestones:
            for ms_id in milestones.keys():
                ms_idx = node_to_index[ms_id]
                adjacency_matrix[goal_idx][ms_idx] = 1
                
        return {
            'nodes': nodes,
            'node_to_index': node_to_index,
            'adjacency_matrix': adjacency_matrix,
            'goal_data': goal_data
        }
        
    def get_adjacency_matrix(self, person: str, goal_id: str) -> Optional[Dict]:
        """Get adjacency matrix for specific person and goal"""
        if person in self.adjacency_matrices and goal_id in self.adjacency_matrices[person]:
            return self.adjacency_matrices[person][goal_id]
        return None
        
    def update_adjacency_matrix(self, person: str, goal_id: str, 
                               new_milestone_id: str, parent_id: str):
        """Update adjacency matrix when new milestone is added"""
        if person not in self.adjacency_matrices or goal_id not in self.adjacency_matrices[person]:
            return False
            
        matrix_data = self.adjacency_matrices[person][goal_id]
        nodes = matrix_data['nodes']
        node_to_index = matrix_data['node_to_index']
        adjacency_matrix = matrix_data['adjacency_matrix']
        
        # Add new node
        nodes.append(new_milestone_id)
        node_to_index[new_milestone_id] = len(nodes) - 1
        
        # Extend adjacency matrix
        n = len(nodes)
        new_matrix = [[0] * n for _ in range(n)]
        
        # Copy existing matrix
        for i in range(len(adjacency_matrix)):
            for j in range(len(adjacency_matrix[i])):
                new_matrix[i][j] = adjacency_matrix[i][j]
                
        # Add new edge: parent -> new_milestone
        if parent_id in node_to_index:
            parent_idx = node_to_index[parent_id]
            new_milestone_idx = node_to_index[new_milestone_id]
            new_matrix[parent_idx][new_milestone_idx] = 1
            
        # Update the matrix data
        matrix_data['adjacency_matrix'] = new_matrix
        matrix_data['nodes'] = nodes
        matrix_data['node_to_index'] = node_to_index
        
        return True
        
    def get_sub_roadmap_groups(self, person: str, goal_id: str) -> List[List[str]]:
        """Find connected components in the roadmap"""
        matrix_data = self.get_adjacency_matrix(person, goal_id)
        if not matrix_data:
            return []
            
        nodes = matrix_data['nodes']
        adjacency_matrix = matrix_data['adjacency_matrix']
        
        visited = set()
        groups = []
        
        def dfs(node_idx, current_group):
            if node_idx in visited:
                return
            visited.add(node_idx)
            current_group.append(nodes[node_idx])
            
            # Check all connections (both directions)
            for i in range(len(adjacency_matrix)):
                if ((adjacency_matrix[node_idx][i] == 1 or adjacency_matrix[i][node_idx] == 1) 
                    and i not in visited and i != 0):  # i != 0 excludes goal
                    dfs(i, current_group)
                    
        # Start DFS from each unvisited milestone (skip goal at index 0)
        for i in range(1, len(nodes)):
            if i not in visited:
                group = []
                dfs(i, group)
                if group:
                    groups.append(group)
                    
        return groups
        
    def print_adjacency_matrix(self, person: str, goal_id: str):
        """Print adjacency matrix for debugging"""
        matrix_data = self.get_adjacency_matrix(person, goal_id)
        if not matrix_data:
            print(f"No matrix found for {person} - {goal_id}")
            return
            
        nodes = matrix_data['nodes']
        adjacency_matrix = matrix_data['adjacency_matrix']
        
        print(f"\nAdjacency Matrix for {person} - {goal_id}:")
        print("Nodes:", nodes)
        print("Matrix:")
        for i, row in enumerate(adjacency_matrix):
            print(f"{nodes[i]}: {row}")


class MilestoneManager:
    """Manages milestone operations and relationships"""
    
    def __init__(self):
        pass
        
    def add_milestone(self, data_manager: DataStructureManager, 
                     matrix_manager: AdjacencyMatrixManager,
                     person: str, goal_id: str, milestone_name: str, 
                     score: int, parent_id: str, is_causal: bool = False,
                     resources: List[str] = None) -> bool:
        """Add a new milestone and update adjacency matrix"""
        try:
            # Generate unique milestone ID
            milestone_id = f"m_{uuid.uuid4().hex[:8]}"
            
            # Create milestone data
            milestone_data = {
                "id": milestone_id,
                "name": milestone_name,
                "score": score,
                "is_causal": is_causal,
                "resources": resources or [],
                "causal_relationships": [],
                "timestamp_added": datetime.now().isoformat()
            }
            
            # Add causal relationship if parent specified
            if parent_id and parent_id != "none":
                # For causal milestones, create more detailed relationship data
                if is_causal:
                    milestone_data["causal_relationships"].append({
                        "prerequisite_id": parent_id,
                        "dependent_id": milestone_id,
                        "relationship_type": "direct_cause",
                        "strength": 0.8,
                        "bidirectional": False,
                        "timestamp_created": datetime.now().isoformat()
                    })
                    
                    # Also add to predecessors list for compatibility
                    milestone_data["predecessors"] = [parent_id]
                    milestone_data["predecessor"] = parent_id
                else:
                    milestone_data["causal_relationships"].append({
                        "prerequisite_id": parent_id,
                        "dependent_id": milestone_id,
                        "relationship_type": "prerequisite",
                        "strength": 0.8,
                        "bidirectional": False,
                        "timestamp_created": datetime.now().isoformat()
                    })
                    
                    # Add to predecessors list for compatibility  
                    milestone_data["predecessors"] = [parent_id]
                    milestone_data["predecessor"] = parent_id
            else:
                # Initialize empty predecessors for consistency
                milestone_data["predecessors"] = []
                milestone_data["predecessor"] = None
                
            # Update data structure
            success = data_manager.update_milestone(person, goal_id, milestone_id, milestone_data)
            
            if success:
                # Update adjacency matrix
                matrix_manager.update_adjacency_matrix(person, goal_id, milestone_id, parent_id)
                print(f"Successfully added milestone: {milestone_name}")
                return True
            else:
                print(f"Failed to add milestone: {milestone_name}")
                return False
                
        except Exception as e:
            print(f"Error adding milestone {milestone_name}: {e}")
            return False
            
    def get_milestone_info(self, data: Dict, person: str, milestone_id: str) -> Optional[Dict]:
        """Get detailed information about a milestone"""
        if person not in data:
            return None
            
        person_data = data[person]
        
        # Handle both 'goals' and 'roadmaps' data structure formats
        goals_data = None
        if isinstance(person_data, dict):
            if 'goals' in person_data:
                goals_data = person_data['goals']
            elif 'roadmaps' in person_data:
                goals_data = person_data['roadmaps']
        
        if not goals_data:
            return None
            
        # Search through all goals for the milestone
        for goal_id, goal_data in goals_data.items():
            milestones = goal_data.get('milestones', {})
            if milestone_id in milestones:
                milestone_info = milestones[milestone_id].copy()
                milestone_info['goal_id'] = goal_id
                milestone_info['goal_title'] = goal_data.get('title', goal_id)
                return milestone_info
                
        return None
        
    def find_goal_for_milestone(self, data: Dict, person: str, milestone_id: str) -> Optional[str]:
        """Find which goal contains a specific milestone"""
        if person not in data:
            return None
            
        person_data = data[person]
        
        # Handle both 'goals' and 'roadmaps' data structure formats
        goals_data = None
        if isinstance(person_data, dict):
            if 'goals' in person_data:
                goals_data = person_data['goals']
            elif 'roadmaps' in person_data:
                goals_data = person_data['roadmaps']
        
        if not goals_data:
            return None
            
        for goal_id, goal_data in goals_data.items():
            milestones = goal_data.get('milestones', {})
            if milestone_id in milestones:
                return goal_id
                
        return None
        
    def update_milestone_relationships(self, data: Dict, person: str, milestone_id: str,
                                     new_relationships: List[Dict]) -> bool:
        """Update causal relationships for a milestone"""
        milestone_info = self.get_milestone_info(data, person, milestone_id)
        if not milestone_info:
            return False
            
        goal_id = milestone_info['goal_id']
        person_data = data[person]
        
        # Handle both 'goals' and 'roadmaps' data structure formats
        goals_data = None
        if 'goals' in person_data:
            goals_data = person_data['goals']
        elif 'roadmaps' in person_data:
            goals_data = person_data['roadmaps']
            
        if not goals_data or goal_id not in goals_data:
            return False
            
        goal_data = goals_data[goal_id]
        
        if milestone_id in goal_data['milestones']:
            goal_data['milestones'][milestone_id]['causal_relationships'] = new_relationships
            return True
            
        return False


class GraphComponentGenerator:
    """Generates graph components for visualization"""
    
    def __init__(self):
        pass
        
    def get_graph_components(self, matrix_manager: AdjacencyMatrixManager, 
                           person: str, goal_id: str, goal_color: str = None) -> Tuple[List[Node], List[Edge]]:
        """Generate nodes and edges for graph visualization"""
        matrix_data = matrix_manager.get_adjacency_matrix(person, goal_id)
        if not matrix_data:
            return [], []
            
        nodes = []
        edges = []
        
        node_list = matrix_data['nodes']
        adjacency_matrix = matrix_data['adjacency_matrix']
        goal_data = matrix_data['goal_data']
        
        goal_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        default_goal_color = goal_color if goal_color else goal_colors[0]
        
        # Create nodes
        for i, node_id in enumerate(node_list):
            if i == 0:  # Goal node
                milestone_count = len(goal_data.get('milestones', {}))
                node = Node(
                    id=node_id,
                    label=f"🎯 {goal_data.get('title', node_id)[:25]}...",
                    title=f"Goal: {goal_data.get('title', node_id)}\nHAS_GOAL relationship from person\nHAS_MILESTONE relationships to {milestone_count} milestones\n(Click to select)",
                    size=30 + milestone_count * 2,
                    color=default_goal_color,
                    shape="dot"
                )
            else:  # Milestone node
                milestone_data = goal_data.get('milestones', {}).get(node_id, {})
                score = milestone_data.get('score', 5)
                
                # Get voting summary
                votes = milestone_data.get('votes', [])
                thumbs_up = sum(1 for vote in votes if vote['vote'])
                thumbs_down = sum(1 for vote in votes if not vote['vote'])
                
                # Color based on vote summary
                if thumbs_up > thumbs_down:
                    vote_color = '#28a745'  # Green for positive
                elif thumbs_down > thumbs_up:
                    vote_color = '#dc3545'  # Red for negative
                else:
                    # Original score-based coloring
                    score_colors = {'high': '#28a745', 'good': '#ffc107', 'fair': '#fd7e14', 'low': '#dc3545'}
                    vote_color = score_colors['low']
                    if score >= 8: vote_color = score_colors['high']
                    elif score >= 6: vote_color = score_colors['good']
                    elif score >= 4: vote_color = score_colors['fair']
                
                # Create voting indicator in label
                vote_indicator = ""
                if thumbs_up > thumbs_down:
                    vote_indicator = f"👍{thumbs_up}"
                elif thumbs_down > thumbs_up:
                    vote_indicator = f"👎{thumbs_down}"
                elif votes:
                    vote_indicator = f"👍{thumbs_up}👎{thumbs_down}"
                
                shape = "box" if milestone_data.get("is_causal") else "diamond"
                label = f"⭐{score}" + (f"\n{vote_indicator}" if vote_indicator else "")
                
                # Count different relationship types for this milestone
                causal_rels = milestone_data.get('causal_relationships', [])
                causes_count = len(causal_rels)
                relationship_types = [rel.get('relationship_type', 'unknown') for rel in causal_rels]
                rel_types_str = ", ".join(set(relationship_types)) if relationship_types else "none"
                
                title_info = f"{milestone_data.get('name', node_id)}\nScore: {score}/10\nVotes: 👍{thumbs_up} 👎{thumbs_down}"
                if milestone_data.get('has_milestone_relationship'):
                    title_info += f"\nHAS_MILESTONE: from goal"
                if causes_count > 0:
                    title_info += f"\nCAUSES relationships: {causes_count} ({rel_types_str})"
                title_info += "\n(Click to vote)"
                
                node = Node(
                    id=node_id,
                    label=label,
                    title=title_info,
                    size=12 + score,
                    color=vote_color,
                    shape=shape
                )
            nodes.append(node)
            
        # Create edges
        for i in range(len(adjacency_matrix)):
            for j in range(len(adjacency_matrix[i])):
                if adjacency_matrix[i][j] == 1:
                    edge = Edge(
                        source=node_list[i],
                        target=node_list[j],
                        color="#95A5A6",
                        width=2
                    )
                    edges.append(edge)
                    
        return nodes, edges
        
    def generate_networkx_graph(self, matrix_manager: AdjacencyMatrixManager,
                               person: str, goal_id: str) -> nx.DiGraph:
        """Generate NetworkX graph for analysis"""
        matrix_data = matrix_manager.get_adjacency_matrix(person, goal_id)
        if not matrix_data:
            return nx.DiGraph()
            
        graph = nx.DiGraph()
        
        node_list = matrix_data['nodes']
        adjacency_matrix = matrix_data['adjacency_matrix']
        goal_data = matrix_data['goal_data']
        
        # Add nodes with attributes
        for i, node_id in enumerate(node_list):
            if i == 0:  # Goal node
                graph.add_node(node_id, 
                             type="goal",
                             title=goal_data.get('title', node_id))
            else:  # Milestone node
                milestone_data = goal_data.get('milestones', {}).get(node_id, {})
                graph.add_node(node_id,
                             type="milestone",
                             name=milestone_data.get('name', node_id),
                             score=milestone_data.get('score', 5),
                             is_causal=milestone_data.get('is_causal', False))
                             
        # Add edges
        for i in range(len(adjacency_matrix)):
            for j in range(len(adjacency_matrix[i])):
                if adjacency_matrix[i][j] == 1:
                    graph.add_edge(node_list[i], node_list[j])
                    
        return graph
