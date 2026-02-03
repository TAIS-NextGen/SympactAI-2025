import json
import uuid
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config


class CareerGraphManager:
    """
    Manages career roadmaps as adjacency matrices for better visualization
    and real-time updates when new milestones are added.
    """
    
    def __init__(self):
        self.data = {}
        self.adjacency_matrices = {} 
        
    def load_data(self, json_data: dict):
        """Load data and convert to adjacency matrix format"""
        self.data = json_data
        self._build_adjacency_matrices()
        
    def _build_adjacency_matrices(self):
        """Convert the data structure to adjacency matrices for each goal"""
        self.adjacency_matrices = {}
        
        for person, person_data in self.data.items():
            self.adjacency_matrices[person] = {}
            goals = person_data.get('roadmaps', {})
            
            for goal_id, goal_data in goals.items():
                self.adjacency_matrices[person][goal_id] = self._create_adjacency_matrix(goal_id, goal_data)
    
    def _create_adjacency_matrix(self, goal_id: str, goal_data: dict) -> dict:
        """Create adjacency matrix for a specific goal including all relationship types - matching Neo4j behavior"""
        milestones = goal_data.get('milestones', {})
        
        nodes = [goal_id]
        node_to_index = {goal_id: 0}
        
        for ms_id in milestones.keys():
            if ms_id not in node_to_index:
                nodes.append(ms_id)
                node_to_index[ms_id] = len(nodes) - 1
            
        n = len(nodes)
        adjacency_matrix = [[0] * n for _ in range(n)]
        
        goal_idx = node_to_index[goal_id]
        
        # First, collect all milestone IDs that have CAUSES relationships as dependents
        milestones_with_causes_predecessors = set()
        for ms_id, milestone in milestones.items():
            causal_rels = milestone.get('causal_relationships', [])
            for rel in causal_rels:
                prerequisite_id = rel.get('prerequisite_id')
                # Check if prerequisite exists in this goal's milestones (not the goal itself)
                if prerequisite_id in node_to_index and prerequisite_id != goal_id:
                    milestones_with_causes_predecessors.add(ms_id)
        
        print(f"DEBUG: Goal {goal_id} - Milestones with CAUSES predecessors: {milestones_with_causes_predecessors}")
        
        # Add HAS_MILESTONE edges (goal -> milestone) for milestones without CAUSES predecessors
        # OR if no CAUSES relationships exist at all (fallback to ensure all milestones are connected)
        has_any_causes = any(len(milestone.get('causal_relationships', [])) > 0 for milestone in milestones.values())
        
        for ms_id, milestone in milestones.items():
            if ms_id in node_to_index:
                ms_idx = node_to_index[ms_id]
                
                # Create HAS_MILESTONE if:
                # 1. This milestone doesn't have CAUSES predecessors, OR
                # 2. No causal relationships exist at all (fallback mode)
                if ms_id not in milestones_with_causes_predecessors or not has_any_causes:
                    adjacency_matrix[goal_idx][ms_idx] = 1  # HAS_MILESTONE relationship
                    print(f"DEBUG: Created HAS_MILESTONE: {goal_id} -> {ms_id}")
        
        # Add CAUSES edges based on causal relationships within this goal only
        causes_added = 0
        for ms_id, milestone in milestones.items():
            if ms_id not in node_to_index:
                continue
                
            # Process causal relationships (CAUSES)
            causal_rels = milestone.get('causal_relationships', [])
            for rel in causal_rels:
                prerequisite_id = rel.get('prerequisite_id')
                dependent_id = rel.get('dependent_id')
                
                # Ensure both milestone IDs belong to this goal and exist in our node list
                if (prerequisite_id in node_to_index and 
                    dependent_id == ms_id and  # dependent should be current milestone
                    prerequisite_id != goal_id):  # prerequisite should not be the goal
                    
                    pred_idx = node_to_index[prerequisite_id]
                    curr_idx = node_to_index[ms_id]
                    adjacency_matrix[pred_idx][curr_idx] = 1  # CAUSES relationship
                    causes_added += 1
                    print(f"DEBUG: Created CAUSES: {prerequisite_id} -> {ms_id} ({rel.get('relationship_type', 'unknown')})")
        
        print(f"DEBUG: Goal {goal_id} - Added {causes_added} CAUSES relationships")
        
        # Fallback: If no milestones are connected to the goal, connect all of them
        goal_connections = sum(adjacency_matrix[goal_idx])
        if goal_connections == 0 and milestones:
            print(f"DEBUG: No goal connections found, connecting all milestones to goal {goal_id}")
            for ms_id in milestones.keys():
                if ms_id in node_to_index:
                    ms_idx = node_to_index[ms_id]
                    adjacency_matrix[goal_idx][ms_idx] = 1
                    print(f"DEBUG: Fallback HAS_MILESTONE: {goal_id} -> {ms_id}")
                
        return {
            'nodes': nodes,
            'node_to_index': node_to_index,
            'adjacency_matrix': adjacency_matrix,
            'goal_data': goal_data
        }
    
    def add_milestone(self, person: str, goal_id: str, milestone_name: str, 
                     score: int, parent_id: str, is_causal: bool = False, resources=None) -> bool:
        """Add a new milestone and update adjacency matrix"""
        try:
            # Add to data structure
            goal = self.data[person]['roadmaps'][goal_id]
            if 'milestones' not in goal:
                goal['milestones'] = {}
                
            new_milestone_id = str(uuid.uuid4())
            milestone_data = {
                "id": new_milestone_id,
                "name": milestone_name,
                "score": score,
                "predecessor": parent_id,
                "created_at": datetime.now().isoformat(),
                "is_causal": is_causal
            }
            if resources:
                milestone_data["resources"] = resources
            goal['milestones'][new_milestone_id] = milestone_data
            
            # Rebuild the matrices from the updated source of truth
            self._build_adjacency_matrices()
            self._update_adjacency_matrix(person, goal_id, new_milestone_id, parent_id)
            
            print(f"DEBUG: Added milestone '{milestone_name}' (ID: {new_milestone_id}) and rebuilt matrices.")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to add milestone: {e}")
            return False
    
    def _update_adjacency_matrix(self, person: str, goal_id: str, 
                               new_milestone_id: str, parent_id: str):
        """Update adjacency matrix when new milestone is added"""
        if person not in self.adjacency_matrices or goal_id not in self.adjacency_matrices[person]:
            # Rebuild if not exists
            self._build_adjacency_matrices()
            return
            
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
            new_idx = node_to_index[new_milestone_id]
            new_matrix[parent_idx][new_idx] = 1
            
        # Update the matrix data
        matrix_data['adjacency_matrix'] = new_matrix
        matrix_data['nodes'] = nodes
        matrix_data['node_to_index'] = node_to_index
        
        print(f"DEBUG: Updated adjacency matrix for goal '{goal_id}'")
        print(f"DEBUG: Matrix size: {n}x{n}")
        print(f"DEBUG: Added edge: {parent_id} -> {new_milestone_id}")

    # NEW VOTING SYSTEM METHODS
    def add_milestone_vote(self, person: str, goal_id: str, milestone_id: str, vote: bool):
        """Add a thumbs up (True) or thumbs down (False) vote to a milestone - only one vote allowed per milestone"""
        try:
            milestone = self.data[person]['roadmaps'][goal_id]['milestones'][milestone_id]
            if 'votes' not in milestone:
                milestone['votes'] = []
            
            # Check if vote already exists - only allow one vote per milestone
            if len(milestone['votes']) > 0:
                print(f"DEBUG: Vote already exists for milestone '{milestone['name']}'. Cannot vote again.")
                return False
            
            # Add the single vote with timestamp
            milestone['votes'].append({
                'vote': vote,  # True for thumbs up, False for thumbs down
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"DEBUG: Added {'👍' if vote else '👎'} vote to milestone '{milestone['name']}'")
            return True
            
        except KeyError as e:
            print(f"ERROR adding vote: {e}")
            return False

    def has_milestone_vote(self, person: str, goal_id: str, milestone_id: str):
        """Check if a milestone already has a vote"""
        try:
            milestone = self.data[person]['roadmaps'][goal_id]['milestones'][milestone_id]
            votes = milestone.get('votes', [])
            return len(votes) > 0
        except KeyError:
            return False

    def get_milestone_current_vote(self, person: str, goal_id: str, milestone_id: str):
        """Get the current vote for a milestone (True for up, False for down, None if no vote)"""
        try:
            milestone = self.data[person]['roadmaps'][goal_id]['milestones'][milestone_id]
            votes = milestone.get('votes', [])
            if len(votes) > 0:
                return votes[0]['vote']  # Return the single vote
            return None
        except KeyError:
            return None

    def clear_milestone_vote(self, person: str, goal_id: str, milestone_id: str):
        """Clear the vote for a milestone (for testing/admin purposes)"""
        try:
            milestone = self.data[person]['roadmaps'][goal_id]['milestones'][milestone_id]
            milestone['votes'] = []
            print(f"DEBUG: Cleared vote for milestone '{milestone['name']}'")
            return True
        except KeyError as e:
            print(f"ERROR clearing vote: {e}")
            return False

    def get_milestone_vote_summary(self, person: str, goal_id: str, milestone_id: str):
        """Get voting summary for a milestone"""
        try:
            milestone = self.data[person]['roadmaps'][goal_id]['milestones'][milestone_id]
            votes = milestone.get('votes', [])
            
            thumbs_up = sum(1 for vote in votes if vote['vote'])
            thumbs_down = sum(1 for vote in votes if not vote['vote'])
            
            return {
                'thumbs_up': thumbs_up,
                'thumbs_down': thumbs_down,
                'total_votes': len(votes),
                'score': thumbs_up - thumbs_down,  # Net positive score
                'confidence': (thumbs_up / len(votes)) if votes else 0.5  # 0.5 = neutral
            }
            
        except KeyError:
            return {'thumbs_up': 0, 'thumbs_down': 0, 'total_votes': 0, 'score': 0, 'confidence': 0.5}

    def get_sub_roadmap_groups(self, person: str, goal_id: str):
        """
        Identify connected milestone groups (sub-roadmaps) for a goal.
        Each group represents a connected component of milestones.
        Example: Goal X -> [a, b, c] where a -> [a10, a20, a30] and a10 -> [a11]
        Results in groups: [a, a10, a20, a30, a11], [b], [c]
        """
        try:
            if person not in self.adjacency_matrices or goal_id not in self.adjacency_matrices[person]:
                return []
            
            matrix_data = self.adjacency_matrices[person][goal_id]
            nodes = matrix_data['nodes']
            adjacency_matrix = matrix_data['adjacency_matrix']
            goal_data = matrix_data['goal_data']
            
            # Remove the goal node from consideration (it's always index 0)
            milestone_nodes = [node for node in nodes if node != goal_id]
            milestone_indices = [i for i, node in enumerate(nodes) if node != goal_id]
            
            if not milestone_nodes:
                return []
            
            # Find connected components using DFS
            visited = set()
            groups = []
            
            def dfs(node_idx, current_group):
                if node_idx in visited:
                    return
                visited.add(node_idx)
                current_group.append(nodes[node_idx])
                
                # Check all connections (both directions)
                for i in range(len(adjacency_matrix)):
                    if (adjacency_matrix[node_idx][i] == 1 or adjacency_matrix[i][node_idx] == 1) and i not in visited and i != 0:  # i != 0 excludes goal
                        dfs(i, current_group)
            
            # Find all connected components
            for node_idx in milestone_indices:
                if node_idx not in visited:
                    current_group = []
                    dfs(node_idx, current_group)
                    if current_group:
                        groups.append(current_group)
            
            # Calculate group scores based on votes
            scored_groups = []
            for group in groups:
                group_vote_scores = []
                group_milestones = []
                
                for milestone_id in group:
                    vote_summary = self.get_milestone_vote_summary(person, goal_id, milestone_id)
                    milestone_info = goal_data['milestones'][milestone_id]
                    
                    group_vote_scores.append(vote_summary['score'])
                    group_milestones.append({
                        'id': milestone_id,
                        'name': milestone_info['name'],
                        'importance_score': milestone_info['score'],
                        'vote_summary': vote_summary
                    })
                
                # Group score calculation
                total_vote_score = sum(group_vote_scores)
                avg_vote_score = total_vote_score / len(group_vote_scores) if group_vote_scores else 0
                thumbs_down_count = sum(1 for milestone in group_milestones if milestone['vote_summary']['thumbs_down'] > 0)
                
                # Lower scores indicate more problematic groups
                problematic_score = avg_vote_score - (thumbs_down_count * 0.5)
                
                scored_groups.append({
                    'milestones': group_milestones,
                    'total_vote_score': total_vote_score,
                    'avg_vote_score': avg_vote_score,
                    'thumbs_down_count': thumbs_down_count,
                    'problematic_score': problematic_score,
                    'size': len(group)
                })
            
            # Sort by problematic score (lowest first = most problematic)
            scored_groups.sort(key=lambda x: x['problematic_score'])
            
            print(f"DEBUG: Found {len(scored_groups)} sub-roadmap groups for goal '{goal_id}'")
            for i, group in enumerate(scored_groups):
                milestone_names = [m['name'] for m in group['milestones']]
                print(f"  Group {i+1} (score: {group['problematic_score']:.2f}): {milestone_names}")
            
            return scored_groups
            
        except Exception as e:
            print(f"ERROR getting sub-roadmap groups: {e}")
            return []

    def get_most_problematic_group(self, person: str, goal_id: str):
        """Get the most problematic sub-roadmap group for AI assistant focus"""
        groups = self.get_sub_roadmap_groups(person, goal_id)
        if groups:
            most_problematic = groups[0]  # Already sorted by problematic score
            
            # Get milestones with thumbs up (confirmed good) vs thumbs down (problematic)
            confirmed_milestones = [m for m in most_problematic['milestones'] if m['vote_summary']['thumbs_up'] > 0]
            problematic_milestones = [m for m in most_problematic['milestones'] if m['vote_summary']['thumbs_down'] > 0]
            unvoted_milestones = [m for m in most_problematic['milestones'] if m['vote_summary']['total_votes'] == 0]
            
            return {
                'group': most_problematic,
                'confirmed_milestones': confirmed_milestones,
                'problematic_milestones': problematic_milestones,
                'unvoted_milestones': unvoted_milestones,
                'focus_strategy': 'problematic' if problematic_milestones else 'gaps' if confirmed_milestones else 'general'
            }
        
        return None
    
    def get_graph_components(self, person: str, goal_id: str) -> Tuple[List[Node], List[Edge]]:
        """Get nodes and edges for Streamlit visualization with voting indicators and all relationship types"""
        if person not in self.adjacency_matrices or goal_id not in self.adjacency_matrices[person]:
            return [], []
            
        matrix_data = self.adjacency_matrices[person][goal_id]
        nodes = matrix_data['nodes']
        adjacency_matrix = matrix_data['adjacency_matrix']
        goal_data = matrix_data['goal_data']
        
        # Create Streamlit nodes
        st_nodes = []
        st_edges = []
        
        goal_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        
        # Add goal node
        goal_color = goal_colors[0]
        milestone_count = len(goal_data.get('milestones', {}))
        st_nodes.append(Node(
            id=goal_id, 
            label=f"🎯 {goal_data['title'][:25]}...",
            title=f"Goal: {goal_data['title']}\nHAS_GOAL relationship from person\nHAS_MILESTONE relationships to {milestone_count} milestones\n(Click to select)",
            size=30 + milestone_count * 2,
            color=goal_color, 
            shape="dot"
        ))
        
        # Add milestone nodes with voting indicators and relationship info
        milestones = goal_data.get('milestones', {})
        for ms_id, milestone in milestones.items():
            score = milestone['score']
            
            # Get voting summary
            votes = milestone.get('votes', [])
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
            
            shape = "box" if milestone.get("is_causal") else "diamond"
            label = f"⭐{score}" + (f"\n{vote_indicator}" if vote_indicator else "")
            
            # Count different relationship types for this milestone
            causal_rels = milestone.get('causal_relationships', [])
            causes_count = len(causal_rels)
            relationship_types = [rel.get('relationship_type', 'unknown') for rel in causal_rels]
            rel_types_str = ", ".join(set(relationship_types)) if relationship_types else "none"
            
            title_info = f"{milestone['name']}\nScore: {score}/10\nVotes: 👍{thumbs_up} 👎{thumbs_down}"
            if milestone.get('has_milestone_relationship'):
                title_info += f"\nHAS_MILESTONE: from goal"
            if causes_count > 0:
                title_info += f"\nCAUSES relationships: {causes_count} ({rel_types_str})"
            title_info += "\n(Click to vote)"
            
            st_nodes.append(Node(
                id=ms_id, 
                label=label,
                title=title_info,
                size=12 + score, 
                color=vote_color, 
                shape=shape
            ))
            
            # Add edges based on adjacency matrix with relationship type colors
            if ms_id in matrix_data['node_to_index']:
                ms_idx = matrix_data['node_to_index'][ms_id]
                for i, row in enumerate(adjacency_matrix):
                    if row[ms_idx] == 1:  # There's an edge from node i to ms_idx
                        source_id = nodes[i]
                        
                        # Determine edge color and type based on relationship
                        edge_color = "#6E6E6E"  # Default
                        edge_title = "Connection"
                        
                        if source_id == goal_id:
                            # HAS_MILESTONE relationship
                            edge_color = "#FF6B6B"  # Red for HAS_MILESTONE
                            edge_title = "HAS_MILESTONE"
                            st_edges.append(Edge(
                                source=goal_id,
                                target=ms_id,
                                color=edge_color,
                                title=edge_title
                            ))
                        else:
                            # CAUSES relationship - look at the target milestone's causal relationships
                            target_milestone = milestones.get(ms_id)
                            if target_milestone:
                                # Find the relationship where source_id is the prerequisite and ms_id is the dependent
                                for rel in target_milestone.get('causal_relationships', []):
                                    if rel.get('prerequisite_id') == source_id and rel.get('dependent_id') == ms_id:
                                        rel_type = rel.get('relationship_type', 'unknown')
                                        strength = rel.get('strength', 0)
                                        
                                        # Color based on relationship type
                                        type_colors = {
                                            'prerequisite': '#FFA500',      # Orange
                                            'direct_cause': '#FF0000',      # Red
                                            'supports': '#00FF00',          # Green
                                            'enables': '#0000FF',           # Blue
                                            'mutual_reinforcement': '#800080' # Purple
                                        }
                                        edge_color = type_colors.get(rel_type, '#6E6E6E')
                                        edge_title = f"CAUSES ({rel_type}, strength: {strength:.2f})"
                                        
                                        st_edges.append(Edge(
                                            source=source_id,
                                            target=ms_id,
                                            color=edge_color,
                                            title=edge_title,
                                            width=4  # Make causal inference edges bold/thick
                                        ))
                                        break
        
        return st_nodes, st_edges
    
    def get_milestone_info(self, person: str, milestone_id: str) -> Optional[dict]:
        """Get milestone information by ID"""
        for goal_data in self.data.get(person, {}).get('roadmaps', {}).values():
            if milestone_id in goal_data.get('milestones', {}):
                return goal_data['milestones'][milestone_id]
        return None
    
    def find_goal_for_milestone(self, person: str, milestone_id: str) -> Optional[str]:
        """Find which goal contains a specific milestone"""
        for goal_id, goal_data in self.data.get(person, {}).get('roadmaps', {}).items():
            if milestone_id in goal_data.get('milestones', {}):
                return goal_id
        return None
    
    def get_goals(self, person: str) -> dict:
        """Get all goals for a person"""
        return self.data.get(person, {}).get('roadmaps', {})
    
    def get_persons(self) -> List[str]:
        """Get all persons"""
        return list(self.data.keys())
    
    def save_data(self) -> str:
        """Save data as JSON string"""
        return json.dumps(self.data, indent=4)
    
    def print_adjacency_matrix(self, person: str, goal_id: str):
        """Debug: Print adjacency matrix for a specific goal"""
        if person not in self.adjacency_matrices or goal_id not in self.adjacency_matrices[person]:
            print(f"No adjacency matrix found for person '{person}', goal '{goal_id}'")
            return
            
        matrix_data = self.adjacency_matrices[person][goal_id]
        nodes = matrix_data['nodes']
        adjacency_matrix = matrix_data['adjacency_matrix']
        
        print(f"\nAdjacency Matrix for Goal: {goal_id}")
        print("Nodes:", nodes)
        print("Matrix:")
        for i, row in enumerate(adjacency_matrix):
            print(f"{nodes[i]:<20}: {row}")


def render_graph_with_manager(graph_manager: CareerGraphManager, person: str, goal_id: str):
    """Render the graph using the graph manager"""
    nodes, edges = graph_manager.get_graph_components(person, goal_id)
    
    # Add goal-to-goal edges if multiple goals exist
    goals = graph_manager.get_goals(person)
    goal_ids = list(goals.keys())
    for i in range(len(goal_ids) - 1):
        edges.append(Edge(
            source=goal_ids[i], 
            target=goal_ids[i+1], 
            color="#a0a0a0", 
            dashes=True, 
            width=3
        ))
    
    config = Config(
        width="100%", 
        height=580, 
        directed=True, 
        physics=True,
        nodeHighlightBehavior=True, 
        highlightColor="#F7A7A6",
        hierarchical={
            "enabled": True, 
            "sortMethod": "directed",
            "direction": "LR",
            "nodeSpacing": 400, 
            "levelSeparation": 500,
        }
    )
    
    return agraph(nodes=nodes, edges=edges, config=config)