import streamlit as st
import json
from datetime import datetime
import uuid
import openai
import sys
import os
import re
from dotenv import load_dotenv

sys.path.append(os.path.abspath(r".\interviews\app"))
from interviews.app.core.agent import LLMAgent, parse_new_milestone_suggestion
from interviews.app.parameters import INTERVIEW_PARAMETERS , OPENAI_API_KEY
from graph_manager import CareerGraphManager, render_graph_with_manager
from streamlit_agraph import agraph, Node, Edge, Config

from safety_agent import (
    GroqInterviewModerator, 
    moderate_interview_input_groq,
    moderate_interview_input_groq_async,
    InterviewContext
)

from _causality_agent import ECausalityAgent

# --- Page Configuration ---
st.set_page_config(
    page_title="Robee",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
try:
    openai.api_key = OPENAI_API_KEY
except (FileNotFoundError, KeyError):
    st.error("OpenAI API key not found. Please create a `.streamlit/secrets.toml` file with your key.")
    st.stop()


# --- CSS Styling (with fix for chat) ---
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: 1.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.graph-container {
    border: 1px solid #e1e5e9;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    height: 600px;
    display: flex;
    flex-direction: column;
}
.graph-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px 10px 0 0;
    font-weight: 600;
    text-align: center;
    margin: 0;
    font-size: 1.2rem;
}
.stats-card {
    background-color: white;
    border: 1px solid #e1e5e9;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin: 0.5rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.milestone-item {
    background: white;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    padding: 0.75rem;
    margin: 0.5rem 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.milestone-info { flex: 1; }
.milestone-name { font-weight: 600; color: #2c3e50; margin-bottom: 0.25rem; }
.milestone-score { font-size: 0.9rem; color: #7f8c8d; }
.score-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    color: white;
    margin-right: 0.5rem;
}
.score-high { background-color: #28a745; }
.score-good { background-color: #ffc107; color: #212529; }
.score-fair { background-color: #fd7e14; }
.score-low { background-color: #dc3545; }
.management-section {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 1rem;
    border: 1px solid #e1e5e9;
    height: 800px; /* Taller container for chat */
    display: flex;
    flex-direction: column;
}
.section-header {
    font-size: 1.2rem;
    font-weight: 600;
    color: #495057;
    text-align: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e9ecef;
}
/* Chat-specific styles -- CORRECTED */
.chat-container {
    flex-grow: 1;
    overflow-y: auto;
    padding: 0 10px;
    display: flex;
    flex-direction: column-reverse; /* THIS IS THE KEY FIX: Newest messages at the bottom */
}
.chat-message {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
}
.user-message {
    align-self: flex-end;
    background-color: #007bff;
    color: white;
    border-radius: 20px 20px 5px 20px;
    padding: 10px 15px;
    max-width: 80%;
}
.assistant-message {
    align-self: flex-start;
    background-color: #e9ecef;
    color: #495057;
    border-radius: 20px 20px 20px 5px;
    padding: 10px 15px;
    max-width: 80%;
}
.ai-suggestion-card {
    background-color: #e6f7ff;
    border: 1px solid #91d5ff;
    border-radius: 8px;
    padding: 1rem;
    margin-top: 0.5rem;
}
.skip-pattern-indicator {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 8px;
    padding: 0.75rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
    color: #856404;
}
.skip-first { border-left: 4px solid #17a2b8; }
.skip-multiple { border-left: 4px solid #fd7e14; }
.skip-consistent { border-left: 4px solid #e83e8c; }
.interactive-options {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}
.break-suggestion {
    background-color: #e8f5e8;
    border: 1px solid #c3e6cb;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    color: #155724;
}
.voting-container {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}
.vote-button {
    margin: 0 0.25rem;
    padding: 0.5rem 1rem;
    font-size: 1.2rem;
    border: none;
    border-radius: 50px;
    cursor: pointer;
    transition: all 0.2s;
}
.vote-up {
    background-color: #28a745;
    color: white;
}
.vote-up:hover {
    background-color: #218838;
}
.vote-down {
    background-color: #dc3545;
    color: white;
}
.vote-down:hover {
    background-color: #c82333;
}
.group-analysis {
    background-color: #e6f3ff;
    border: 1px solid #91d5ff;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}
.problematic-group {
    background-color: #fff2f0;
    border-left: 4px solid #dc3545;
}
.good-group {
    background-color: #f0f9f0;
    border-left: 4px solid #28a745;
}
/* Safety Agent Styling */
.safety-guidance {
    background-color: #e8f4f8;
    border: 1px solid #b3e0ff;
    border-left: 4px solid #007bff;
    border-radius: 8px;
    padding: 0.75rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
    color: #004085;
}
.safety-intervention {
    background-color: #fff3e0;
    border: 1px solid #ffcc80;
    border-left: 4px solid #ff9800;
    border-radius: 8px;
    padding: 0.75rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
    color: #e65100;
}
.safety-monitor {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 0.5rem;
    margin: 0.25rem 0;
    font-size: 0.8rem;
}
/* Enhanced Causality Analysis Styling */
.causality-analysis {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}
.cofounder-suggestion {
    background-color: #e8f5e8;
    border: 1px solid #c3e6cb;
    border-left: 4px solid #28a745;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}
.counterfactual-scenario {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    border-left: 4px solid #ffc107;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}
.intervention-result {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-left: 4px solid #dc3545;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}
.analysis-metric {
    background-color: #e1ecf4;
    border: 1px solid #bee5eb;
    border-radius: 6px;
    padding: 0.5rem;
    margin: 0.25rem;
    text-align: center;
}
.impact-high {
    border-left: 4px solid #dc3545;
    background-color: #f8d7da;
}
.impact-medium {
    border-left: 4px solid #ffc107;
    background-color: #fff3cd;
}
.impact-low {
    border-left: 4px solid #28a745;
    background-color: #d4edda;
}
.safety-intervention {
    background-color: #fff3e0;
    border: 1px solid #ffcc80;
    border-left: 4px solid #ff9800;
    border-radius: 8px;
    padding: 0.75rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
    color: #e65100;
}
.safety-monitor {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 0.5rem;
    margin: 0.25rem 0;
    font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)


def check_and_trigger_causality_analysis(person: str, goal_id: str, goal_title: str, milestones: list, questions_asked: int):
    """
    Check if we should trigger automatic causality analysis based on question count
    Triggers every 5 questions to provide ongoing insights
    """
    if questions_asked > 0 and questions_asked % 5 == 0:  # Every 5 questions
        causality_key = f"causality_analysis_{person}_{goal_id}"
        
        # Only run if we haven't run analysis recently or if significant new data
        if (causality_key not in st.session_state.causality_analysis_results or 
            len(milestones) >= 3):  # Ensure sufficient data for analysis
            
            try:
                with st.spinner(f"🔍 Running automatic causality analysis (Question #{questions_asked})..."):
                    analysis_results = st.session_state.causality_agent.run_comprehensive_analysis(
                        milestones=milestones,
                        goal_title=goal_title,
                        person_name=person,
                        analysis_types=['cofounders', 'counterfactuals']  # Light analysis during interview
                    )
                    st.session_state.causality_analysis_results[causality_key] = analysis_results
                    
                    # Show a brief notification about new insights
                    st.success(f"🔍 **New causality insights discovered!** Click 'Causal Analysis' to explore {len(analysis_results.get('cofounder_analysis', {}).get('cofounder_suggestions', []))} cofounder opportunities and {len(analysis_results.get('counterfactual_analysis', {}).get('counterfactual_scenarios', []))} what-if scenarios.")
                    
            except Exception as e:
                st.warning(f"Automatic causality analysis failed: {e}")


# --- Create enhanced conversation context function (previously defined but moved here for clarity) ---
def create_enhanced_conversation_context(session_messages: list, goal_title: str, max_context_length: int = 1000) -> str:
    """
    Create enhanced conversation context for safety moderation and AI responses.
    Filters out safety messages to avoid confusion and focuses on career discussion.
    """
    career_messages = []
    for msg in session_messages:
        # Skip safety-related messages for context
        if msg.get("type") not in ["guidance", "intervention"]:
            content = msg.get("content", "")
            if content and len(content.strip()) > 0:
                role = "User" if msg.get("type") == "answer" else "Assistant"
                career_messages.append(f"{role}: {content[:200]}...")  # Truncate long messages
    
    # Join recent messages (last 5) for context
    recent_context = " | ".join(career_messages[-5:]) if career_messages else ""
    context_with_goal = f"Goal: {goal_title} | {recent_context}"
    
    # Truncate if too long
    if len(context_with_goal) > max_context_length:
        context_with_goal = context_with_goal[:max_context_length] + "..."
    
    return context_with_goal

def get_safety_intervention_message(violation_count: int, goal_title: str) -> str:
    """Generate contextually appropriate safety intervention messages"""
    messages = [
        f"Let's keep our discussion focused on your career development for '{goal_title}'. What specific challenges or opportunities would you like to explore?",
        f"I'd like to help you with '{goal_title}' planning. Can you share what prerequisites or skills you needed for this goal?",
        f"Let's stay on track with your professional journey for '{goal_title}'. What steps or milestones are you thinking about?",
        f"This is important: let's focus on actionable career insights for '{goal_title}'. What would be most helpful to discuss?",
        f"Final reminder: our conversation should center on your career development. What aspects of '{goal_title}' would you like to explore?"
    ]
    return messages[min(violation_count - 1, len(messages) - 1)]


class MilestoneTracker:
    def __init__(self):
        self.graph_manager = CareerGraphManager()
        self.selected_person = None
        self.selected_goal = None

    def load_data(self, uploaded_file):
        try:
            content = uploaded_file.getvalue().decode('utf-8')
            data = json.loads(content)
            
            # Check if this is causal_output.json format
            is_causal_format = self._is_causal_format(data)
            if is_causal_format:
                data = self._convert_causal_to_roadmap_format(data)
                # Store format info for UI display
                st.session_state.data_format = "causal"
            else:
                st.session_state.data_format = "standard"
            
            self._migrate_data_structure(data)
            self.graph_manager.load_data(data)
            self.selected_person = None
            self.selected_goal = None
            return True
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return False

    def _is_causal_format(self, data):
        """Check if the data is in causal_output.json format"""
        return "causal_analysis" in data and "metadata" in data

    def _convert_causal_to_roadmap_format(self, causal_data):
        """Convert causal_output.json format to roadmap format"""
        roadmap_data = {}
        
        print(f"DEBUG: Converting causal data for {len(causal_data['causal_analysis'])} people")
        
        for person_name, person_data in causal_data["causal_analysis"].items():
            print(f"DEBUG: Processing person: {person_name}")
            roadmap_data[person_name] = {
                "person_metadata": person_data.get("person_metadata", {}),
                "has_goal_relationships": True,  # This person has HAS_GOAL relationships
                "roadmaps": {}
            }
            
            for goal_id, goal_data in person_data["goals"].items():
                print(f"DEBUG: Processing goal: {goal_id} - {goal_data['goal_metadata']['title']}")
                
                # Convert goal structure
                roadmap_goal = {
                    "id": goal_id,
                    "title": goal_data["goal_metadata"]["title"],
                    "duration": goal_data["goal_metadata"]["duration"],
                    "total_milestones": goal_data["goal_metadata"]["total_milestones"],
                    "analysis_timestamp": goal_data["goal_metadata"]["analysis_timestamp"],
                    "has_goal_relationship": True,  # This goal has HAS_GOAL relationship to person
                    "person_name": person_name,
                    "milestones": {}
                }
                
                # Convert milestones - generate unique IDs to avoid conflicts
                milestone_dict = {}
                milestone_id_mapping = {}  # Map original IDs to new unique IDs
                
                print(f"DEBUG: Converting {len(goal_data['milestones'])} milestones for goal {goal_id}")
                
                for milestone in goal_data["milestones"]:
                    original_id = milestone["id"]
                    # Generate a unique ID for this milestone
                    new_milestone_id = f"{goal_id}_{original_id}_{str(uuid.uuid4())[:8]}"
                    milestone_id_mapping[original_id] = new_milestone_id
                    
                    print(f"DEBUG: Mapping milestone {original_id} -> {new_milestone_id}")
                    
                    milestone_dict[new_milestone_id] = {
                        "id": new_milestone_id,
                        "name": milestone["description"],
                        "score": milestone["original_score"],
                        "normalized_importance": milestone["normalized_importance"],
                        "predecessor": None,  # Will be set based on causal relationships
                        "predecessors": [],
                        "causal_relationships": [],  # Store all causal relationship details
                        "has_goal_relationship": True,  # This milestone has HAS_MILESTONE relationship to goal
                        "created_at": datetime.now().isoformat(),
                        "is_causal": True,
                        "original_causal_id": original_id  # Keep track of original ID for relationships
                    }
                
                # Process causal relationships to set predecessors using the ID mapping
                print(f"DEBUG: Processing {len(goal_data.get('causal_relationships', []))} causal relationships for goal {goal_id}")
                
                for relationship in goal_data.get("causal_relationships", []):
                    original_dependent_id = relationship["dependent_id"]
                    original_prerequisite_id = relationship["prerequisite_id"]
                    
                    # Map original IDs to new unique IDs - only within this goal's scope
                    dependent_id = milestone_id_mapping.get(original_dependent_id)
                    prerequisite_id = milestone_id_mapping.get(original_prerequisite_id)
                    
                    print(f"DEBUG: Processing relationship {original_prerequisite_id} -> {original_dependent_id}")
                    print(f"DEBUG: Mapped to {prerequisite_id} -> {dependent_id}")
                    
                    if dependent_id and dependent_id in milestone_dict and prerequisite_id and prerequisite_id in milestone_dict:
                        print(f"DEBUG: Creating CAUSES relationship {prerequisite_id} -> {dependent_id} (type: {relationship['relationship_type']})")
                        
                        # Store full relationship details
                        causal_relationship = {
                            "prerequisite_id": prerequisite_id,
                            "dependent_id": dependent_id,
                            "relationship_type": relationship["relationship_type"],
                            "strength": relationship["strength"],
                            "bidirectional": relationship["bidirectional"],
                            "conditions": relationship.get("conditions", ""),
                            "mechanism": relationship.get("mechanism", ""),
                            "confidence": relationship["confidence"],
                            "reasoning": relationship["reasoning"],
                            "connection_type": "CAUSES"  # Neo4j relationship type
                        }
                        
                        # Add to the dependent milestone's causal relationships
                        milestone_dict[dependent_id]["causal_relationships"].append(causal_relationship)
                        
                        # Add the prerequisite to the dependent milestone's predecessors list
                        if prerequisite_id not in milestone_dict[dependent_id]["predecessors"]:
                            milestone_dict[dependent_id]["predecessors"].append(prerequisite_id)
                        
                        # For backward compatibility, set the first prerequisite as the main predecessor
                        if milestone_dict[dependent_id]["predecessor"] is None:
                            milestone_dict[dependent_id]["predecessor"] = prerequisite_id
                    else:
                        print(f"DEBUG: SKIPPING relationship {original_prerequisite_id} -> {original_dependent_id}")
                        print(f"DEBUG: dependent_id in milestone_dict: {dependent_id in milestone_dict if dependent_id else False}")
                        print(f"DEBUG: prerequisite_id in milestone_dict: {prerequisite_id in milestone_dict if prerequisite_id else False}")
                        print(f"DEBUG: Available milestone IDs: {list(milestone_dict.keys())}")
                        print(f"DEBUG: ID mapping: {milestone_id_mapping}")
                
                print(f"DEBUG: Finished processing causal relationships for goal {goal_id}")
                
                # Set milestones without predecessors to point to the goal (HAS_MILESTONE relationship)
                milestones_without_predecessors = 0
                for new_milestone_id, milestone in milestone_dict.items():
                    if not milestone["predecessors"] and milestone["predecessor"] is None:
                        milestone["predecessor"] = goal_id
                        milestone["predecessors"] = [goal_id]
                        milestones_without_predecessors += 1
                        print(f"DEBUG: Creating HAS_MILESTONE relationship {goal_id} -> {new_milestone_id}")
                    
                    # Ensure all milestones maintain HAS_MILESTONE relationship info
                    milestone["goal_id"] = goal_id
                    milestone["has_milestone_relationship"] = True
                
                print(f"DEBUG: Goal {goal_id} - {milestones_without_predecessors} milestones connected directly to goal")
                print(f"DEBUG: Goal {goal_id} - Total milestones: {len(milestone_dict)}")
                
                # Special handling for goals with very few milestones or sparse relationships
                if len(milestone_dict) <= 3 or milestones_without_predecessors == 0:
                    print(f"DEBUG: Goal {goal_id} - Applying fallback connection strategy")
                    for new_milestone_id, milestone in milestone_dict.items():
                        if not milestone["predecessors"]:
                            milestone["predecessor"] = goal_id
                            milestone["predecessors"] = [goal_id]
                            print(f"DEBUG: Fallback HAS_MILESTONE relationship {goal_id} -> {new_milestone_id}")
                
                roadmap_goal["milestones"] = milestone_dict
                roadmap_data[person_name]["roadmaps"][goal_id] = roadmap_goal
        
        print(f"DEBUG: Causal data conversion completed successfully")
        return roadmap_data

    def get_causal_insights(self, person, goal_id):
        """Get causal insights for a specific goal if available"""
        # Check if this goal has causal data stored
        goals = self.get_goals(person)
        if not goals or goal_id not in goals:
            return None
            
        goal_data = goals[goal_id]
        milestones = goal_data.get('milestones', {})
        
        # Check if milestones have causal metadata
        causal_milestones = [m for m in milestones.values() if m.get('is_causal', False)]
        if not causal_milestones:
            return None
            
        # Generate comprehensive insights
        total_causes_relationships = 0
        total_has_milestone_relationships = 0
        relationship_types_count = {}
        
        for milestone in milestones.values():
            # Count CAUSES relationships
            causal_rels = milestone.get('causal_relationships', [])
            total_causes_relationships += len(causal_rels)
            
            # Count relationship types
            for rel in causal_rels:
                rel_type = rel.get('relationship_type', 'unknown')
                relationship_types_count[rel_type] = relationship_types_count.get(rel_type, 0) + 1
            
            # Count HAS_MILESTONE relationships
            if milestone.get('has_milestone_relationship', False):
                total_has_milestone_relationships += 1
            
        insights = {
            'has_causal_data': True,
            'total_milestones': len(milestones),
            'total_causes_relationships': total_causes_relationships,
            'total_has_milestone_relationships': total_has_milestone_relationships,
            'has_goal_relationship': goal_data.get('has_goal_relationship', False),
            'relationship_types_distribution': relationship_types_count,
            'average_score': sum(m.get('score', 0) for m in milestones.values()) / len(milestones) if milestones else 0,
            'foundational_milestones': [],
            'terminal_milestones': [],
            'connection_summary': {
                'person_to_goal': f"HAS_GOAL: {person} -> {goal_data.get('title', goal_id)}",
                'goal_to_milestones': f"HAS_MILESTONE: {len(milestones)} connections",
                'milestone_to_milestone': f"CAUSES: {total_causes_relationships} connections",
                'total_connections': 1 + total_has_milestone_relationships + total_causes_relationships
            }
        }
        
        # Find foundational milestones (no predecessors except goal)
        for ms_id, milestone in milestones.items():
            predecessors = milestone.get('predecessors', [])
            if not predecessors or all(pred == goal_id for pred in predecessors):
                insights['foundational_milestones'].append({
                    'id': ms_id,
                    'name': milestone.get('name', 'Unknown'),
                    'score': milestone.get('score', 0)
                })
                
        # Find terminal milestones (no other milestones depend on them)
        dependent_milestones = set()
        for milestone in milestones.values():
            for pred in milestone.get('predecessors', []):
                if pred != goal_id:  # Ignore goal as predecessor
                    dependent_milestones.add(pred)
                    
        for ms_id, milestone in milestones.items():
            if ms_id not in dependent_milestones:
                insights['terminal_milestones'].append({
                    'id': ms_id,
                    'name': milestone.get('name', 'Unknown'),
                    'score': milestone.get('score', 0)
                })
                
        return insights

    def _migrate_data_structure(self, data):
        for person_data in data.values():
            goals = person_data.get('roadmaps', {})
            for goal_id, goal_data in goals.items():
                if isinstance(goal_data.get('milestones'), list): # Old list format
                    old_milestones = goal_data['milestones']
                    new_milestones_dict = {}
                    for i, milestone in enumerate(old_milestones):
                        ms_id = f"ms_{goal_id}_{i+1}_{str(uuid.uuid4())[:4]}"
                        milestone['id'] = ms_id
                        milestone['predecessor'] = goal_id # Old milestones point to the goal
                        if 'created_at' not in milestone:
                            milestone['created_at'] = datetime.now().isoformat()
                        new_milestones_dict[ms_id] = milestone
                    goal_data['milestones'] = new_milestones_dict

                # --- NEW MIGRATION STEP ---
                # Ensure all milestones have a 'predecessors' list for forward compatibility
                for ms_id, milestone in goal_data.get('milestones', {}).items():
                    if 'predecessors' not in milestone:
                        if 'predecessor' in milestone and milestone['predecessor']:
                            milestone['predecessors'] = [milestone['predecessor']]
                        else:
                            milestone['predecessors'] = [] # Default to empty list

    def get_persons(self):
        return self.graph_manager.get_persons()

    def get_goals(self, person):
        return self.graph_manager.get_goals(person)

    def get_milestone(self, person, milestone_id):
        return self.graph_manager.get_milestone_info(person, milestone_id)

    def find_goal_for_milestone(self, person, milestone_id):
        return self.graph_manager.find_goal_for_milestone(person, milestone_id)

    def add_child_milestone(self, person, goal_id, milestone_name, score, parent_id, resources=None):
        return self.graph_manager.add_milestone(person, goal_id, milestone_name, score, parent_id, resources=resources)

    def insert_milestone_before(self, person, goal_id, milestone_name, score, target_milestone_id, resources=None):
        # Get target milestone info
        target_milestone = self.graph_manager.get_milestone_info(person, target_milestone_id)
        if not target_milestone: return False
        
        original_predecessor = target_milestone['predecessor']
        
        # Add new milestone with original predecessor
        success = self.graph_manager.add_milestone(person, goal_id, milestone_name, score, original_predecessor, resources=resources)
        if not success: return False
        
        # Update target milestone to point to new milestone
        # This requires updating the data structure directly
        for goal_data in self.graph_manager.data[person]['roadmaps'].values():
            if target_milestone_id in goal_data.get('milestones', {}):
                goal_data['milestones'][target_milestone_id]['predecessor'] = f"temp_{uuid.uuid4()}"
                # We need to rebuild the adjacency matrix after this change
                self.graph_manager._build_adjacency_matrices()
                return True
        return False

    def insert_milestone_after(self, person, goal_id, milestone_name, score, target_milestone_id, resources=None):
        # Add new milestone with target as predecessor
        return self.graph_manager.add_milestone(person, goal_id, milestone_name, score, target_milestone_id, resources=resources)
    # in interface.py, inside the MilestoneTracker class

    def insert_causal_milestone(self, person, goal_id, new_milestone_name, new_milestone_score, enabled_milestone_id):
        """
        Inserts a new milestone as a prerequisite (cause) for an existing 'enabled' milestone.
        This function ensures that multiple prerequisites for the same milestone are added in parallel, not in a chain.
        Correct Logic: New Milestone -> Enabled Milestone
        """
        try:
            goal = self.graph_manager.data[person]['roadmaps'][goal_id]
            
            # Special case: if we're adding a milestone that enables the goal itself
            if enabled_milestone_id == goal_id:
                # Create the new milestone as a direct child of the goal
                new_milestone_id = str(uuid.uuid4())
                goal['milestones'][new_milestone_id] = {
                    "id": new_milestone_id,
                    "name": new_milestone_name,
                    "score": new_milestone_score,
                    "predecessor": goal_id,  # Links directly to the goal
                    "predecessors": [],
                    "causal_relationships": [],  # Initialize causal relationships
                    "created_at": datetime.now().isoformat(),
                    "is_causal": True
                }
                
                # Rebuild the matrices from the updated data structure
                self.graph_manager._build_adjacency_matrices()
                print(f"DEBUG: Added milestone '{new_milestone_name}' as prerequisite for goal")
                print(f"DEBUG: Goal now has {len(goal['milestones'])} milestones")
                return True            # Regular case: milestone enabling another milestone
            # Get the milestone that was enabled by our new step.
            enabled_milestone = goal['milestones'][enabled_milestone_id]
            print(f"DEBUG: Regular case - connecting to existing milestone '{enabled_milestone['name']}'")
            
            # 1. Create the new milestone. It has NO predecessors of its own initially.
            new_milestone_id = str(uuid.uuid4())
            goal['milestones'][new_milestone_id] = {
                "id": new_milestone_id,
                "name": new_milestone_name,
                "score": new_milestone_score,
                # Set the old predecessor field to None or an empty string to prevent the fallback from triggering.
                "predecessor": None, 
                "predecessors": [], # Start with an empty list
                "causal_relationships": [],  # Initialize causal relationships
                "created_at": datetime.now().isoformat(),
                "is_causal": True
            }
            
            # 2. Ensure the enabled milestone has a `predecessors` list AND causal_relationships
            if 'predecessors' not in enabled_milestone:
                if 'predecessor' in enabled_milestone and enabled_milestone['predecessor']:
                     enabled_milestone['predecessors'] = [enabled_milestone['predecessor']]
                else:
                     enabled_milestone['predecessors'] = []
            
            # Initialize causal_relationships if missing
            if 'causal_relationships' not in enabled_milestone:
                enabled_milestone['causal_relationships'] = []
            
            # 3. Add the new milestone as a predecessor to the enabled milestone.
            # This creates the desired New Milestone -> Enabled Milestone link.
            enabled_milestone['predecessors'].append(new_milestone_id)
            
            # 4. CRITICAL: Create the causal relationship that graph_manager expects!
            causal_relationship = {
                "prerequisite_id": new_milestone_id,
                "dependent_id": enabled_milestone_id,
                "relationship_type": "prerequisite",
                "strength": 0.8,
                "created_at": datetime.now().isoformat()
            }
            enabled_milestone['causal_relationships'].append(causal_relationship)
            
            print(f"DEBUG: Created causal relationship: {new_milestone_name} -> {enabled_milestone['name']}")
            print(f"DEBUG: Causal relationship details: {causal_relationship}")
            
            # 5. Rebuild the matrices from the updated data structure.
            self.graph_manager._build_adjacency_matrices()
            
            print(f"DEBUG: Inserted causal link: {new_milestone_name} -> {enabled_milestone['name']}")
            return True

        except KeyError as e:
            print(f"ERROR inserting causal milestone: {e}")
            st.error(f"Could not find a required element: {e}. The graph state might be inconsistent.")
            return False
    def remove_milestone(self, person, goal_id, milestone_id):
        """
        Remove a milestone and properly reconnect its dependencies.
        Handles both old 'predecessor' field and new 'predecessors' list.
        """
        try:
            milestones = self.graph_manager.data[person]['roadmaps'][goal_id]['milestones']
            if milestone_id not in milestones: 
                print(f"ERROR: Milestone {milestone_id} not found in goal {goal_id}")
                return None
            
            # Safety check: Don't allow removing the last milestone
            if len(milestones) <= 1:
                print(f"ERROR: Cannot remove the last milestone from goal {goal_id}")
                return None
                
            milestone_to_remove = milestones[milestone_id]
            predecessor_id = milestone_to_remove.get('predecessor')
            predecessors_list = milestone_to_remove.get('predecessors', [])
            
            print(f"DEBUG: Removing milestone '{milestone_to_remove['name']}' (ID: {milestone_id})")
            print(f"DEBUG: Milestone has predecessor: {predecessor_id}, predecessors: {predecessors_list}")
            
            # Find all milestones that depend on the one we're removing
            dependent_milestones = []
            for ms_id, ms in milestones.items():
                # Check old predecessor field
                if ms.get('predecessor') == milestone_id:
                    dependent_milestones.append((ms_id, ms))
                
                # Check new predecessors list
                ms_predecessors = ms.get('predecessors', [])
                if milestone_id in ms_predecessors:
                    dependent_milestones.append((ms_id, ms))
            
            print(f"DEBUG: Found {len(dependent_milestones)} dependent milestones")
            
            # Reconnect dependent milestones
            for dep_id, dep_milestone in dependent_milestones:
                # Update old predecessor field if it points to removed milestone
                if dep_milestone.get('predecessor') == milestone_id:
                    dep_milestone['predecessor'] = predecessor_id
                    print(f"DEBUG: Updated {dep_milestone['name']} predecessor from {milestone_id} to {predecessor_id}")
                
                # Update predecessors list - remove the deleted milestone and add its predecessors
                if 'predecessors' not in dep_milestone:
                    dep_milestone['predecessors'] = []
                
                # Remove the milestone we're deleting from the list
                if milestone_id in dep_milestone['predecessors']:
                    dep_milestone['predecessors'].remove(milestone_id)
                    print(f"DEBUG: Removed {milestone_id} from {dep_milestone['name']}'s predecessors list")
                
                # Add the removed milestone's predecessors (if any)
                if predecessors_list:
                    for pred in predecessors_list:
                        if pred not in dep_milestone['predecessors']:
                            dep_milestone['predecessors'].append(pred)
                            print(f"DEBUG: Added {pred} to {dep_milestone['name']}'s predecessors list")
                elif predecessor_id and predecessor_id not in dep_milestone['predecessors']:
                    dep_milestone['predecessors'].append(predecessor_id)
                    print(f"DEBUG: Added fallback predecessor {predecessor_id} to {dep_milestone['name']}'s predecessors list")
            
            # Remove the milestone
            removed = milestones.pop(milestone_id)
            print(f"DEBUG: Successfully removed milestone '{removed['name']}'")
            
            # Rebuild adjacency matrices after removal
            self.graph_manager._build_adjacency_matrices()
            print(f"DEBUG: Rebuilt adjacency matrices after removal")
            
            return removed
            
        except (KeyError, IndexError, TypeError) as e:
            print(f"ERROR removing milestone: {e}")
            return None
    
    def update_milestone_score(self, person, goal_id, milestone_id, new_score):
        """Update the importance score of an existing milestone"""
        try:
            milestones = self.graph_manager.data[person]['roadmaps'][goal_id]['milestones']
            if milestone_id not in milestones:
                return False
            
            # Update the score
            milestones[milestone_id]['score'] = new_score
            
            # No need to rebuild adjacency matrices since we're only updating the score
            print(f"DEBUG: Updated milestone '{milestones[milestone_id]['name']}' score to {new_score}")
            return True
            
        except (KeyError, TypeError) as e:
            print(f"ERROR updating milestone score: {e}")
            return False

    def _update_milestone_connection(self, person, goal_id, milestone_id, target_milestone_id):
        """Update an existing milestone to connect to a different target milestone"""
        try:
            goal = self.graph_manager.data[person]['roadmaps'][goal_id]
            milestones = goal.get('milestones', {})
            
            if milestone_id not in milestones or target_milestone_id not in milestones:
                print(f"ERROR: Milestone IDs not found - source: {milestone_id}, target: {target_milestone_id}")
                return False
            
            target_milestone = milestones[target_milestone_id]
            
            # Initialize predecessors list if it doesn't exist
            if 'predecessors' not in target_milestone:
                if 'predecessor' in target_milestone and target_milestone['predecessor']:
                    target_milestone['predecessors'] = [target_milestone['predecessor']]
                else:
                    target_milestone['predecessors'] = []
            
            # Add the milestone as a predecessor to the target if not already there
            if milestone_id not in target_milestone['predecessors']:
                target_milestone['predecessors'].append(milestone_id)
            
            # Update the source milestone to have no direct connection to goal
            source_milestone = milestones[milestone_id]
            source_milestone['predecessor'] = None  # Remove goal connection
            if 'predecessors' not in source_milestone:
                source_milestone['predecessors'] = []
            
            # Rebuild adjacency matrices
            self.graph_manager._build_adjacency_matrices()
            
            print(f"DEBUG: Updated connection - {source_milestone['name']} now connects to {target_milestone['name']}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to update milestone connection: {e}")
            return False

    def get_ordered_milestones_for_goal(self, person, goal_id):
        goal = self.graph_manager.get_goals(person).get(goal_id)
        if not goal or 'milestones' not in goal: return []
        milestones = list(goal.get('milestones', {}).values())
        milestones.sort(key=lambda x: x.get('created_at', ''))
        return milestones
        
    def save_data(self):
        return self.graph_manager.save_data()

    def insert_goal_between(self, person, goal_id_a, goal_id_b, new_goal_title, milestones):
        """
        Insert a new goal between goal_id_a and goal_id_b (which must be consecutive in order).
        milestones: list of (name, score) tuples
        """
        goals = self.graph_manager.data[person]['roadmaps']
        goal_ids = list(goals.keys())
        try:
            idx_a = goal_ids.index(goal_id_a)
            idx_b = goal_ids.index(goal_id_b)
            if idx_b != idx_a + 1:
                return False  # They must be consecutive
            
            new_goal_id = str(uuid.uuid4())

            # Build the new milestones dictionary for the new goal
            new_milestones_dict = {}
            for ms_name, ms_score in milestones:
                ms_id = str(uuid.uuid4())
                new_milestones_dict[ms_id] = {
                    "id": ms_id,
                    "name": ms_name,
                    "score": ms_score,
                    "predecessor": new_goal_id, # This milestone's predecessor is the goal itself
                    "created_at": datetime.now().isoformat()
                }
            
            # Build new ordered dict of goals
            new_goals = {}
            for gid in goal_ids:
                new_goals[gid] = goals[gid]
                if gid == goal_id_a:
                    # Insert new goal right after goal_id_a
                    new_goals[new_goal_id] = {
                        "title": new_goal_title,
                        "milestones": new_milestones_dict
                    }
            
            self.graph_manager.data[person]['roadmaps'] = new_goals
            # Rebuild adjacency matrices
            self.graph_manager._build_adjacency_matrices()
            return True
        except ValueError:
            # goal_id_a or goal_id_b not found in list
            return False

    def insert_goal_at_beginning(self, person, new_goal_title, milestones):
        """
        Insert a new goal at the beginning of the roadmap.
        milestones: list of (name, score) tuples
        """
        goals = self.graph_manager.data[person]['roadmaps']
        goal_ids = list(goals.keys())
        
        new_goal_id = str(uuid.uuid4())

        # Build the new milestones dictionary for the new goal
        new_milestones_dict = {}
        for ms_name, ms_score in milestones:
            ms_id = str(uuid.uuid4())
            new_milestones_dict[ms_id] = {
                "id": ms_id,
                "name": ms_name,
                "score": ms_score,
                "predecessor": new_goal_id, # This milestone's predecessor is the goal itself
                "created_at": datetime.now().isoformat()
            }
        
        # Build new ordered dict with new goal at the beginning
        new_goals = {new_goal_id: {
            "title": new_goal_title,
            "milestones": new_milestones_dict
        }}
        
        # Add all existing goals after the new one
        for gid in goal_ids:
            new_goals[gid] = goals[gid]
        
        self.graph_manager.data[person]['roadmaps'] = new_goals
        # Rebuild adjacency matrices
        self.graph_manager._build_adjacency_matrices()
        return True

    def insert_goal_at_end(self, person, new_goal_title, milestones):
        """
        Insert a new goal at the end of the roadmap.
        milestones: list of (name, score) tuples
        """
        goals = self.graph_manager.data[person]['roadmaps']
        
        new_goal_id = str(uuid.uuid4())

        # Build the new milestones dictionary for the new goal
        new_milestones_dict = {}
        for ms_name, ms_score in milestones:
            ms_id = str(uuid.uuid4())
            new_milestones_dict[ms_id] = {
                "id": ms_id,
                "name": ms_name,
                "score": ms_score,
                "predecessor": new_goal_id, # This milestone's predecessor is the goal itself
                "created_at": datetime.now().isoformat()
            }
        
        # Simply add the new goal to the end
        goals[new_goal_id] = {
            "title": new_goal_title,
            "milestones": new_milestones_dict
        }
        
        # Rebuild adjacency matrices
        self.graph_manager._build_adjacency_matrices()
        return True

    def update_milestone_resources(self, person, goal_id, milestone_id, resources):
        """Update the resources for a specific milestone."""
        try:
            milestones = self.graph_manager.data[person]['roadmaps'][goal_id]['milestones']
            if milestone_id in milestones:
                milestones[milestone_id]['resources'] = resources
                return True
            return False
        except Exception as e:
            print(f"ERROR updating milestone resources: {e}")
            return False

    def update_goal_resources(self, person, goal_id, resources):
        """Update the resources for a specific goal."""
        try:
            goal = self.graph_manager.data[person]['roadmaps'][goal_id]
            goal['resources'] = resources
            return True
        except Exception as e:
            print(f"ERROR updating goal resources: {e}")
            return False

    def remove_goal(self, person, goal_id):
        """Remove a goal and all its milestones for a person."""
        try:
            if goal_id in self.graph_manager.data[person]['roadmaps']:
                del self.graph_manager.data[person]['roadmaps'][goal_id]
                # Rebuild adjacency matrices
                self.graph_manager._build_adjacency_matrices()
                return True
            return False
        except Exception as e:
            print(f"ERROR removing goal: {e}")
            return False

    def remove_goal_and_reconnect(self, person, goal_id):
        """Remove a goal and reconnect its predecessor and successor goals in the roadmap order."""
        try:
            goals = self.graph_manager.data[person]['roadmaps']
            goal_ids = list(goals.keys())
            if goal_id not in goal_ids:
                return False, "Goal not found."
            idx = goal_ids.index(goal_id)
            # Find predecessor and successor
            pred_id = goal_ids[idx-1] if idx > 0 else None
            succ_id = goal_ids[idx+1] if idx < len(goal_ids)-1 else None
            # Remove the goal
            del goals[goal_id]
            # Reconnect: if both predecessor and successor exist, move successor after predecessor
            if pred_id and succ_id:
                # Remove successor from its current position
                goal_ids.remove(succ_id)
                # Insert successor after predecessor
                pred_idx = goal_ids.index(pred_id)
                goal_ids.insert(pred_idx+1, succ_id)
                # Rebuild the ordered dict
                new_goals = {gid: goals[gid] for gid in goal_ids}
                self.graph_manager.data[person]['roadmaps'] = new_goals
            # If only one of pred or succ exists, nothing to reconnect
            # Rebuild adjacency matrices
            self.graph_manager._build_adjacency_matrices()
            return True, f"Goal and its milestones deleted. Graph reconnected."
        except Exception as e:
            print(f"ERROR removing and reconnecting goal: {e}")
            return False, f"Error: {e}"

    # NEW VOTING SYSTEM METHODS
    def add_milestone_vote(self, person: str, goal_id: str, milestone_id: str, vote: bool):
        """Add a thumbs up (True) or thumbs down (False) vote to a milestone - only one vote allowed per milestone"""
        return self.graph_manager.add_milestone_vote(person, goal_id, milestone_id, vote)

    def get_milestone_vote_summary(self, person: str, goal_id: str, milestone_id: str):
        """Get voting summary for a milestone"""
        return self.graph_manager.get_milestone_vote_summary(person, goal_id, milestone_id)

    def has_milestone_vote(self, person: str, goal_id: str, milestone_id: str):
        """Check if a milestone already has a vote"""
        return self.graph_manager.has_milestone_vote(person, goal_id, milestone_id)

    def get_milestone_current_vote(self, person: str, goal_id: str, milestone_id: str):
        """Get the current vote for a milestone (True for up, False for down, None if no vote)"""
        return self.graph_manager.get_milestone_current_vote(person, goal_id, milestone_id)

    def clear_milestone_vote(self, person: str, goal_id: str, milestone_id: str):
        """Clear the vote for a milestone (for testing/admin purposes)"""
        return self.graph_manager.clear_milestone_vote(person, goal_id, milestone_id)

    def get_sub_roadmap_groups(self, person: str, goal_id: str):
        """Get connected milestone groups (sub-roadmaps) for a goal"""
        return self.graph_manager.get_sub_roadmap_groups(person, goal_id)

    def get_most_problematic_group(self, person: str, goal_id: str):
        """Get the most problematic sub-roadmap group for AI assistant focus"""
        return self.graph_manager.get_most_problematic_group(person, goal_id)

    def remove_milestone_group(self, person: str, goal_id: str, group_milestones: list) -> int:
        """Remove all milestones in a group and return count of successfully removed milestones"""
        removed_count = 0
        for milestone in group_milestones:
            if self.remove_milestone(person, goal_id, milestone['id']):
                removed_count += 1
        return removed_count

    def should_remove_entire_group(self, group: dict, threshold: float = 0.8) -> bool:
        """Determine if an entire group should be removed based on negative feedback"""
        if not group['milestones']:
            return False
        
        # Count milestones with thumbs down
        thumbs_down_milestones = [m for m in group['milestones'] if m['vote_summary']['thumbs_down'] > 0]
        
        # If most milestones (threshold %) have thumbs down, suggest removal
        if len(thumbs_down_milestones) >= len(group['milestones']) * threshold:
            return True
            
        # Also suggest removal if problematic score is very low (below -2)
        if group['problematic_score'] < -2:
            return True
            
        return False

# --- Session State Management (MODIFIED) ---
def initialize_session_state():
    if 'tracker' not in st.session_state:
        st.session_state.tracker = MilestoneTracker()
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'last_uploaded_file_name' not in st.session_state:
        st.session_state.last_uploaded_file_name = None
    if 'add_milestone_target' not in st.session_state:
        st.session_state.add_milestone_target = None
    # --- NEW: State for graph focus mode ---
    if 'focus_on_goal' not in st.session_state:
        st.session_state.focus_on_goal = False
    # --- Initialize clicked milestone tracking ---
    if 'clicked_milestone_id' not in st.session_state:
        st.session_state.clicked_milestone_id = None
    # --- Initialize pending delete states ---
    if 'pending_goal_delete' not in st.session_state:
        st.session_state.pending_goal_delete = None
    
    # --- Safety Agent: Initialize as hidden element for enhanced discussions ---
    if 'safety_moderator' not in st.session_state:
        # Use Groq API key from the safety agent
        groq_api_key = 'groq_api_key'  # Replace with your actual Groq API key or environment variable
        st.session_state.safety_moderator = GroqInterviewModerator(
            groq_api_key=groq_api_key,
            max_violations=3,  # Allow 3 off-topic attempts before intervention
            model="llama-3.1-8b-instant"  # Fast model for real-time moderation
        )
    
    if 'causality_agent' not in st.session_state:
        groq_api_key = os.getenv("groq_api_key") or 'groq_api_key'  # Replace with your actual Groq API key or environment variable
        st.session_state.causality_agent = ECausalityAgent(groq_api_key=groq_api_key)
    
    # Track moderation statistics for improvement insights
    if 'moderation_stats' not in st.session_state:
        st.session_state.moderation_stats = {
            'total_checks': 0,
            'flagged_questions': 0,
            'flagged_answers': 0,
            'suggestions_provided': 0,
            'interventions': 0
        }
    
    # Track causality analysis state
    if 'causality_analysis_results' not in st.session_state:
        st.session_state.causality_analysis_results = {}
    if 'show_causality_ui' not in st.session_state:
        st.session_state.show_causality_ui = False
        
# --- UI Rendering Functions (Unchanged) ---
def render_sidebar():
    st.sidebar.header("🔧 Configuration")
    uploaded_file = st.sidebar.file_uploader(
        "📁 Upload Career Data", type=['json'], help="Upload a JSON file containing career data"
    )
    if uploaded_file is not None and uploaded_file.name != st.session_state.get('last_uploaded_file_name'):
        st.session_state.last_uploaded_file_name = uploaded_file.name
        if st.session_state.tracker.load_data(uploaded_file):
            data_format = st.session_state.get('data_format', 'standard')
            if data_format == 'causal':
                st.sidebar.success("✅ Causal Data Loaded Successfully")
                st.sidebar.info("🧠 Detected causal relationships from AI analysis")
            else:
                st.sidebar.success("✅ Data Loaded Successfully")
            st.session_state.data_loaded = True
            st.rerun()
        else:
            st.session_state.data_loaded = False

    if not st.session_state.data_loaded: return

    persons = st.session_state.tracker.get_persons()
    if persons:
        current_person = st.session_state.tracker.selected_person
        person_index = 0
        if current_person and current_person in persons:
            person_index = persons.index(current_person)
        else:
            st.session_state.tracker.selected_person = persons[0]

        selected_person = st.sidebar.selectbox(
            "👤 Select Person", persons, index=person_index
        )
        if selected_person != st.session_state.tracker.selected_person:
            st.session_state.tracker.selected_person = selected_person
            st.session_state.tracker.selected_goal = None
            st.session_state.add_milestone_target = None
            st.rerun()

    goals = st.session_state.tracker.get_goals(st.session_state.tracker.selected_person)
    if goals:
        goal_options = {goal_id: data['title'] for goal_id, data in goals.items()}
        current_goal = st.session_state.tracker.selected_goal
        options_list = [None] + list(goal_options.keys())
        selected_goal_id = st.sidebar.selectbox(
            "🎯 Select Goal (or click in graph)",
            options=options_list,
            format_func=lambda x: "Select a goal..." if x is None else goal_options[x],
            index=options_list.index(current_goal) if current_goal in options_list else 0
        )
        if selected_goal_id != current_goal:
            st.session_state.tracker.selected_goal = selected_goal_id
            st.session_state.add_milestone_target = None
            st.rerun()

    # --- GAP ANALYSIS PANEL ---
    if st.session_state.tracker.selected_goal:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 Gap Analysis")
        
        # Get current selections from tracker
        current_selected_person = st.session_state.tracker.selected_person
        current_selected_goal = st.session_state.tracker.selected_goal
        
        # Get gap analysis from session state if available
        interview_key = f"interview_session_{current_selected_person}_{current_selected_goal}_GOAL"
        gap_analysis_key = f"gap_analysis_{interview_key}"
        
        if gap_analysis_key in st.session_state and st.session_state[gap_analysis_key]:
            latest_analysis = st.session_state[gap_analysis_key][-1]  # Get most recent analysis
            
            if latest_analysis.get('gaps_found'):
                st.sidebar.success(f"🎯 Found {len(latest_analysis.get('identified_gaps', []))} gaps")
                
                # Show confidence score
                if latest_analysis.get('confidence_score'):
                    confidence = latest_analysis['confidence_score']
                    color = "🟢" if confidence >= 7 else "🟡" if confidence >= 4 else "🔴"
                    st.sidebar.write(f"{color} Confidence: {confidence:.1f}/10")
                
                # Show top gaps in sidebar
                with st.sidebar.expander("View Detected Gaps"):
                    for i, gap in enumerate(latest_analysis.get('identified_gaps', [])[:3]):  # Show top 3
                        st.write(f"**{i+1}. {gap.get('type', 'Unknown')} Gap**")
                        st.write(f"_{gap.get('description', 'No description')[:100]}..._")
                        if gap.get('suggested_milestones'):
                            st.write(f"💡 Suggests: {', '.join(gap['suggested_milestones'][:2])}")
                        st.write("---")
                
                # Generate comprehensive gap report button
                if st.sidebar.button("📊 Generate Full Gap Report", key="generate_gap_report"):
                    try:
                        # Get interview agent
                        if "interview_agent" not in st.session_state:
                            st.session_state.interview_agent = LLMAgent(api_key=OPENAI_API_KEY)
                            st.session_state.interview_agent.load_parameters(INTERVIEW_PARAMETERS["ROADMAP_DETAILER"])
                        
                        agent = st.session_state.interview_agent
                        session_key = f"interview_{interview_key}"
                        
                        if session_key in st.session_state:
                            conversation_messages = st.session_state[session_key]["messages"]
                            current_goal_data = st.session_state.tracker.get_goals(current_selected_person)[current_selected_goal]
                            
                            # Generate comprehensive gap analysis
                            with st.spinner("🔄 Generating comprehensive gap analysis..."):
                                comprehensive_analysis = agent.analyze_gap_patterns(
                                    conversation_messages,
                                    current_goal_data['title'],
                                    existing_milestones=[ms['name'] for ms in st.session_state.tracker.get_ordered_milestones_for_goal(current_selected_person, current_selected_goal)]
                                )
                                
                                # Store comprehensive analysis
                                st.session_state[f"comprehensive_gap_analysis_{interview_key}"] = comprehensive_analysis
                                st.sidebar.success("✅ Report generated! Check the interview tab.")
                    except Exception as e:
                        st.sidebar.error(f"Error generating report: {str(e)}")
            else:
                st.sidebar.info("💬 Start interviewing to detect gaps")
        else:
            st.sidebar.info("💬 Start interviewing to detect gaps")

    # --- DELETE GOAL PANEL ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗑️ Delete a Goal")
    if goals:
        delete_goal_id = st.sidebar.selectbox(
            "Select goal to delete:",
            options=list(goal_options.keys()),
            format_func=lambda x: goal_options[x],
            key="delete_goal_select"
        )
        if st.sidebar.button("🗑️ Delete Selected Goal", key="delete_goal_btn", use_container_width=True):
            st.session_state['pending_goal_delete'] = delete_goal_id

        if st.session_state.get('pending_goal_delete') == delete_goal_id:
            st.sidebar.warning(f"Are you sure you want to delete the goal '{goal_options[delete_goal_id]}' and all its milestones? This cannot be undone.")
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button("✅ Yes, delete", key="confirm_delete_goal"):
                    success, msg = st.session_state.tracker.remove_goal_and_reconnect(st.session_state.tracker.selected_person, delete_goal_id)
                    if success:
                        st.sidebar.success(msg)
                        if st.session_state.tracker.selected_goal == delete_goal_id:
                            st.session_state.tracker.selected_goal = None
                            st.session_state.focus_on_goal = False
                        st.session_state['pending_goal_delete'] = None
                        st.rerun()
                    else:
                        st.sidebar.error(msg)
            with col2:
                if st.button("❌ Cancel", key="cancel_delete_goal"):
                    st.session_state['pending_goal_delete'] = None
                    st.rerun()

def get_score_badge_class(score):
    if score >= 8: return "score-high"
    if score >= 6: return "score-good"
    if score >= 4: return "score-fair"
    return "score-low"

# --- Main Content Rendering (HEAVILY MODIFIED) ---
def render_main_content():
    if not st.session_state.data_loaded:
        st.markdown("""
        ## 🐝 Welcome to Robee's Career Milestone Tracker
        Get started by uploading your JSON data file using the sidebar.
        """)
        return

    tracker = st.session_state.tracker
    if not tracker.selected_person:
        st.info("👤 Please select a person from the sidebar to view their career network.")
        return

    selected_person = tracker.selected_person
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown(f'<div class="graph-header">🌐 Career Network for {selected_person}</div>', unsafe_allow_html=True)
        
        # # Show data format indicator
        # data_format = st.session_state.get('data_format', 'standard')
        # if data_format == 'causal':
        #     st.info("🧠 **Causal Analysis Data Detected** - This data contains AI-generated causal relationships between milestones")
        
        goals = tracker.get_goals(selected_person)

        # --- GOAL RESOURCES UI ---
        if tracker.selected_goal:
            goal_data = goals[tracker.selected_goal]
            goal_resources = goal_data.get('resources', [])
            st.markdown("**Goal Resources:**")
            if goal_resources:
                for res in goal_resources:
                    st.markdown(f"- [{res['name']}]({res['url']})")
            else:
                st.markdown("_No resources added for this goal yet._")
            goal_edit_key = f"edit_goal_resources_{tracker.selected_goal}"
            goal_edit_flag = f"{goal_edit_key}_flag"
            if st.button("✏️ Edit Goal Resources", key=goal_edit_key):
                # Toggle the edit state - if already open, close it (like clicking cancel)
                st.session_state[goal_edit_flag] = not st.session_state.get(goal_edit_flag, False)
            if st.session_state.get(goal_edit_flag, False):
                existing_names = ", ".join([r['name'] for r in goal_resources])
                existing_urls = ", ".join([r['url'] for r in goal_resources])
                with st.form(key=f"edit_goal_resources_form_{tracker.selected_goal}", clear_on_submit=True):
                    new_names = st.text_area("Resource Names (comma-separated)", value=existing_names, key=f"edit_goal_names_{tracker.selected_goal}")
                    new_urls = st.text_area("Resource URLs (comma-separated, in same order)", value=existing_urls, key=f"edit_goal_urls_{tracker.selected_goal}")
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("💾 Save Goal Resources", use_container_width=True):
                            names = [n.strip() for n in new_names.split(",") if n.strip()]
                            urls = [u.strip() for u in new_urls.split(",") if u.strip()]
                            new_resources = []
                            for n, u in zip(names, urls):
                                if n and u:
                                    new_resources.append({"name": n, "url": u})
                            tracker.update_goal_resources(selected_person, tracker.selected_goal, new_resources)
                            st.session_state[goal_edit_flag] = False
                            st.success("Goal resources updated!")
                            st.rerun()
                    with col_cancel:
                        if st.form_submit_button("Cancel", use_container_width=True):
                            st.session_state[goal_edit_flag] = False
                            st.rerun()

        # --- Always render the graph, even if delete goal UI is shown ---
        previous_focus = st.session_state.get('focus_on_goal', False)
        checkbox_enabled = bool(tracker.selected_goal) or previous_focus
        new_focus_state = st.checkbox(
            "🔍 Focus on Selected Goal",
            key='goal_focus_checkbox',
            value=previous_focus,
            disabled=not checkbox_enabled,
            help="Select a goal to enable focus mode. When checked, only the selected goal and its milestones will be shown. Click again to exit focus mode."
        )
        st.session_state.focus_on_goal = new_focus_state
        if new_focus_state and not tracker.selected_goal:
            st.session_state.focus_on_goal = False
        if tracker.selected_goal:
            tracker.graph_manager.print_adjacency_matrix(selected_person, tracker.selected_goal)

        all_nodes, all_edges = [], []
        goal_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        focus_mode_is_active = st.session_state.focus_on_goal and tracker.selected_goal

        if focus_mode_is_active:
            selected_goal_id = tracker.selected_goal
            nodes, edges = tracker.graph_manager.get_graph_components(selected_person, selected_goal_id)
            if not nodes:
                goal_data = goals[selected_goal_id]
                nodes = [Node(
                    id=selected_goal_id,
                    label=f"🎯 {goal_data['title'][:25]}...",
                    title=f"Goal: {goal_data['title']}\n(Click to select)",
                    size=30,
                    color=goal_colors[0],
                    shape="dot"
                )]
                edges = []
            all_nodes.extend(nodes)
            all_edges.extend(edges)
            if nodes:
                goal_ids_list = list(goals.keys())
                try:
                    goal_index = goal_ids_list.index(selected_goal_id)
                    goal_color = goal_colors[goal_index % len(goal_colors)]
                    nodes[0].color = goal_color
                except ValueError:
                    nodes[0].color = goal_colors[0]
            st.session_state['last_graph_nodes'] = all_nodes
            st.session_state['last_graph_edges'] = all_edges
        else:
            goal_ids = list(goals.keys())
            print(f"DEBUG: Rendering {len(goal_ids)} goals for {selected_person}: {goal_ids}")
            
            for i, goal_id in enumerate(goal_ids):
                nodes, edges = tracker.graph_manager.get_graph_components(selected_person, goal_id)
                print(f"DEBUG: Goal {goal_id} - Got {len(nodes)} nodes and {len(edges)} edges")
                
                if not nodes:
                    print(f"DEBUG: No nodes found for goal {goal_id}, creating fallback goal node")
                    goal_data = goals[goal_id]
                    nodes = [Node(
                        id=goal_id,
                        label=f"🎯 {goal_data['title'][:25]}...",
                        title=f"Goal: {goal_data['title']}\n(Click to select)",
                        size=30,
                        color=goal_colors[i % len(goal_colors)],
                        shape="dot"
                    )]
                    edges = []
                all_nodes.extend(nodes)
                all_edges.extend(edges)
                if nodes:
                    goal_node = nodes[0]
                    goal_node.color = goal_colors[i % len(goal_colors)]
                    print(f"DEBUG: Added goal node {goal_id} with color {goal_node.color}")
            
            # Add goal-to-goal connections for better visual flow
            print(f"DEBUG: Adding {len(goal_ids) - 1} goal-to-goal connections")
            for i in range(len(goal_ids) - 1):
                edge = Edge(
                    source=goal_ids[i], 
                    target=goal_ids[i+1], 
                    color="#a0a0a0", 
                    dashes=True, 
                    width=3,
                    arrows=""  # Remove arrows for goal-to-goal connections
                )
                all_edges.append(edge)
                print(f"DEBUG: Added goal-to-goal edge: {goal_ids[i]} -> {goal_ids[i+1]}")
            
            st.session_state['last_graph_nodes'] = all_nodes
            st.session_state['last_graph_edges'] = all_edges
        # Configure graph with better click handling
        config = Config(
            width="100%", 
            height=580, 
            directed=True, 
            physics=True,
            nodeHighlightBehavior=True, 
            highlightColor="#F7A7A6",
            selectByNodeId=True,  # Enable node selection by ID
            highlightOpacity=0.3,
            hierarchical={
                "enabled": True, 
                "sortMethod": "directed",
                "direction": "LR",
                "nodeSpacing": 400, 
                "levelSeparation": 500,
            },
            # Improve interactivity
            interaction={
                "hover": True,
                "selectConnectedEdges": False,
                "tooltipDelay": 300,
                "hideEdgesOnDrag": False,
                "hideNodesOnDrag": False
            }
        )
        
        # Render graph with proper error handling
        try:
            if all_nodes:
                clicked_node_id = agraph(
                    nodes=all_nodes, 
                    edges=all_edges, 
                    config=config
                )
            else:
                # Fallback to cached nodes if available
                cached_nodes = st.session_state.get('last_graph_nodes', [])
                cached_edges = st.session_state.get('last_graph_edges', [])
                if cached_nodes:
                    clicked_node_id = agraph(
                        nodes=cached_nodes, 
                        edges=cached_edges, 
                        config=config
                    )
                else:
                    st.warning("⚠️ No graph data available. Please upload data first.")
                    clicked_node_id = None
        except Exception as e:
            st.error(f"Graph rendering error: {str(e)}")
            clicked_node_id = None

        # --- DELETE GOAL BUTTON (localized, does not move right panel) ---
        if tracker.selected_goal:
            st.markdown("---")
            delete_goal_flag = f"pending_delete_goal_{tracker.selected_goal}"
            delete_goal_container = st.empty()
            # Show confirmation immediately if delete button is clicked or flag is set
            show_confirm = st.session_state.get(delete_goal_flag, False)
            if st.button("🗑️ Delete Goal", type="primary", use_container_width=True, key=f"delete_goal_{tracker.selected_goal}"):
                show_confirm = True
                st.session_state[delete_goal_flag] = True
            if show_confirm:
                with delete_goal_container:
                    st.warning(f"Are you sure you want to delete the goal '{goal_data['title']}' and all its milestones? This cannot be undone.")
                    col1_, col2_ = st.columns(2)
                    with col1_:
                        if st.button("✅ Yes, delete goal", key=f"confirm_delete_goal_{tracker.selected_goal}"):
                            if tracker.remove_goal(selected_person, tracker.selected_goal):
                                st.success(f"Goal '{goal_data['title']}' deleted.")
                                tracker.selected_goal = None
                                st.session_state.focus_on_goal = False
                                st.session_state[delete_goal_flag] = False
                                st.rerun()
                    with col2_:
                        if st.button("❌ Cancel", key=f"cancel_delete_goal_{tracker.selected_goal}"):
                            st.session_state[delete_goal_flag] = False

        # --- The rest of the function remains the same ---
        goal_ids = list(goals.keys()) # Recalculate for the section below
        if len(goal_ids) >= 1:  # Changed from > 1 to >= 1 to allow adding when there's only one goal
            st.markdown("---")
            st.subheader("➕ Insert a Missing Goal")
            
            # Build position options
            position_options = []
            position_labels = []
            
            # Add "Before first goal" option
            if goal_ids:
                position_options.append(("before_first", goal_ids[0]))
                position_labels.append(f"📍 Before '{goals[goal_ids[0]]['title']}'")
            
            # Add "Between goals" options (only if more than one goal exists)
            if len(goal_ids) > 1:
                edge_options = [(goal_ids[i], goal_ids[i+1]) for i in range(len(goal_ids)-1)]
                for goal_a, goal_b in edge_options:
                    position_options.append(("between", goal_a, goal_b))
                    position_labels.append(f"🔗 Between '{goals[goal_a]['title']}' → '{goals[goal_b]['title']}'")
            
            # Add "After last goal" option
            if goal_ids:
                position_options.append(("after_last", goal_ids[-1]))
                position_labels.append(f"📍 After '{goals[goal_ids[-1]]['title']}'")
            
            selected_position_label = st.selectbox(
                "Select where to insert the new goal:", 
                options=[None] + position_labels, 
                index=0,
                format_func=lambda x: "Choose a position..." if x is None else x
            )
            
            if selected_position_label:
                position_idx = position_labels.index(selected_position_label)
                selected_position = position_options[position_idx]
                
                # Create a unique form key based on the position
                form_key = f"insert_goal_form_{selected_position[0]}_{hash(str(selected_position))}"
                
                with st.form(key=form_key, clear_on_submit=True):
                    # Display different messages based on position type
                    if selected_position[0] == "before_first":
                        st.markdown(f"**New goal before _'{goals[selected_position[1]]['title']}'_**")
                    elif selected_position[0] == "after_last":
                        st.markdown(f"**New goal after _'{goals[selected_position[1]]['title']}'_**")
                    else:  # between
                        goal_a, goal_b = selected_position[1], selected_position[2]
                        st.markdown(f"**New goal between _'{goals[goal_a]['title']}'_ and _'{goals[goal_b]['title']}'_**")
                    
                    new_goal_title = st.text_input("New Goal Title", placeholder="e.g., 'Become Proficient in Cloud Tech'")
                    milestones_text = st.text_area("Milestones (one per line, format: name|score)", 
                                                   placeholder="AWS Certified Developer|8\nDeploy a serverless app|7",
                                                   height=100)
                    submitted = st.form_submit_button("✅ Add New Goal", use_container_width=True, type="primary")
                    
                    if submitted:
                        milestones = []
                        for line in milestones_text.splitlines():
                            if '|' in line:
                                name, score_str = line.split('|', 1)
                                try:
                                    milestones.append((name.strip(), int(score_str.strip())))
                                except ValueError:
                                    continue
                            elif line.strip():
                                milestones.append((line.strip(), 5))

                        if new_goal_title.strip() and milestones:
                            success = False
                            
                            # Handle different insertion types
                            if selected_position[0] == "before_first":
                                success = tracker.insert_goal_at_beginning(selected_person, new_goal_title.strip(), milestones)
                            elif selected_position[0] == "after_last":
                                success = tracker.insert_goal_at_end(selected_person, new_goal_title.strip(), milestones)
                            else:  # between
                                goal_a, goal_b = selected_position[1], selected_position[2]
                                success = tracker.insert_goal_between(selected_person, goal_a, goal_b, new_goal_title.strip(), milestones)
                            
                            if success:
                                st.success("🎉 Goal added successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to insert goal. Please try again.")
                        else:
                            st.warning("⚠️ Please provide a goal title and at least one milestone.")

        # Handle node clicks - improved with debugging
        debug_mode = st.checkbox("🔧 Show Debug Info", key="debug_checkbox")
        
        # Check if we just cancelled the milestone editor (to prevent interference)
        just_cancelled = st.session_state.get('just_cancelled_milestone_edit', False)
        if just_cancelled:
            st.session_state.just_cancelled_milestone_edit = False
            
        if clicked_node_id and not just_cancelled:
            # Ensure clicked_node_id is a string for proper comparison
            clicked_node_id = str(clicked_node_id)
            
            # Debug: Show what was clicked
            if debug_mode:
                st.write(f"DEBUG: Clicked node ID: `{clicked_node_id}`")
                st.write(f"DEBUG: Available goal IDs: `{list(goals.keys())}`")
                st.write(f"DEBUG: Current selected goal: `{tracker.selected_goal}`")
                st.write(f"DEBUG: Node ID type: `{type(clicked_node_id)}`")
            
            # Check if clicked node is a goal
            if clicked_node_id in goals:
                if tracker.selected_goal != clicked_node_id:
                    tracker.selected_goal = clicked_node_id
                    st.session_state.add_milestone_target = None
                    # Add visual feedback
                    st.success(f"🎯 Selected goal: '{goals[clicked_node_id]['title']}'")
                    # Force refresh to update UI
                    st.rerun()
                else:
                    # Goal already selected, show feedback
                    st.info(f"🎯 Goal '{goals[clicked_node_id]['title']}' is already selected")
            
            # Check if clicked node is a milestone
            elif tracker.get_milestone(selected_person, clicked_node_id):
                # Store the clicked milestone for potential score editing
                st.session_state.clicked_milestone_id = clicked_node_id
                milestone_info = tracker.get_milestone(selected_person, clicked_node_id)
                if st.session_state.add_milestone_target != clicked_node_id:
                    st.session_state.add_milestone_target = clicked_node_id
                    # Find and select the goal that contains this milestone
                    goal_for_milestone = tracker.find_goal_for_milestone(selected_person, clicked_node_id)
                    if goal_for_milestone:
                        tracker.selected_goal = goal_for_milestone
                        st.success(f"⭐ Selected milestone: '{milestone_info['name']}'")
                    st.rerun()
                else:
                    st.info(f"⭐ Milestone '{milestone_info['name']}' is already selected")
            
            # If clicked node is not recognized
            else:
                if debug_mode:
                    st.warning(f"⚠️ Clicked node `{clicked_node_id}` not found in goals or milestones")
                    st.write("Available goals:", list(goals.keys()))
                    # Check if any milestone matches
                    all_milestones = []
                    for goal in goals.values():
                        all_milestones.extend(goal.get('milestones', {}).keys())
                    st.write("Available milestones (first 10):", all_milestones[:10])

        st.markdown("---")
        total_milestones = sum(len(g.get('milestones', {})) for g in goals.values())
        all_scores = [m['score'] for g in goals.values() for m in g.get('milestones', {}).values()]
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0

        stat_col1, stat_col2, stat_col3 = st.columns(3)
        stat_col1.markdown(f'<div class="stats-card"><h3>🎯 {len(goals)}</h3><p>Active Goals</p></div>', unsafe_allow_html=True)
        stat_col2.markdown(f'<div class="stats-card"><h3>⭐ {total_milestones}</h3><p>Total Milestones</p></div>', unsafe_allow_html=True)
        stat_col3.markdown(f'<div class="stats-card"><h3>📊 {avg_score:.1f}</h3><p>Average Score</p></div>', unsafe_allow_html=True)
        
        if debug_mode:
            st.markdown("### Debug Information")
            st.markdown("**Current Data Structure:**")
            st.json(tracker.graph_manager.data)
            
            if tracker.selected_goal:
                st.markdown("**Adjacency Matrix for Selected Goal:**")
                matrix_data = tracker.graph_manager.adjacency_matrices.get(selected_person, {}).get(tracker.selected_goal)
                if matrix_data:
                    st.markdown(f"**Nodes:** {matrix_data['nodes']}")
                    st.markdown("**Matrix:**")
                    for i, row in enumerate(matrix_data['adjacency_matrix']):
                        st.text(f"{matrix_data['nodes'][i]:<20}: {row}")
                else:
                    st.text("No adjacency matrix found for selected goal")

    with col2:
        render_right_panel()

def render_right_panel():
    # Quick score editor for clicked milestones - moved here to avoid pushing graph down
    if st.session_state.get('clicked_milestone_id'):
        tracker = st.session_state.tracker
        selected_person = tracker.selected_person
        clicked_milestone = tracker.get_milestone(selected_person, st.session_state.clicked_milestone_id)
        if clicked_milestone:
            with st.container(border=True):
                st.markdown("### 🎯 Quick Edit Milestone")
                st.markdown(f"**Editing:** {clicked_milestone['name']}")
                
                col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
                with col1:
                    new_score = st.slider(
                        "Importance Score",
                        min_value=1,
                        max_value=10,
                        value=clicked_milestone['score'],
                        key="quick_score_edit"
                    )
                    
                with col2:
                    if st.button("💾 Save", key="save_quick_score", type="primary", use_container_width=True):
                        goal_id = tracker.find_goal_for_milestone(selected_person, st.session_state.clicked_milestone_id)
                        if tracker.update_milestone_score(selected_person, goal_id, st.session_state.clicked_milestone_id, new_score):
                            st.success(f"✅ Score updated to {new_score}/10!")
                            # Clear the clicked milestone to close the editor
                            st.session_state.clicked_milestone_id = None
                            st.session_state.just_cancelled_milestone_edit = True
                            st.rerun()
                        else:
                            st.error("❌ Failed to update score")
                    
                    if st.button("❌ Cancel", key="cancel_quick_edit", use_container_width=True):
                        # Clear the clicked milestone to close the editor
                        st.session_state.clicked_milestone_id = None
                        st.session_state.just_cancelled_milestone_edit = True
                        st.rerun()
                
                with col3:
                    # Quick remove functionality
                    quick_remove_key = f"quick_remove_confirm_{st.session_state.clicked_milestone_id}"
                    
                    if not st.session_state.get(quick_remove_key, False):
                        if st.button("🗑️ Remove", key="quick_remove_btn", type="secondary", use_container_width=True):
                            st.session_state[quick_remove_key] = True
                            st.rerun()
                    else:
                        st.markdown("**Confirm?**")
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("✅", key="quick_remove_yes", use_container_width=True):
                                goal_id = tracker.find_goal_for_milestone(selected_person, st.session_state.clicked_milestone_id)
                                
                                # Check if this is the last milestone
                                milestones = tracker.get_goals(selected_person)[goal_id]['milestones']
                                if len(milestones) <= 1:
                                    st.error("❌ Cannot remove the last milestone from a goal!")
                                    st.session_state[quick_remove_key] = False
                                    st.rerun()
                                    return
                                
                                removed_milestone = tracker.remove_milestone(selected_person, goal_id, st.session_state.clicked_milestone_id)
                                if removed_milestone:
                                    st.success("🗑️ Milestone removed!")
                                    st.session_state.clicked_milestone_id = None
                                    st.session_state[quick_remove_key] = False
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to remove milestone")
                                    st.session_state[quick_remove_key] = False
                        with col_no:
                            if st.button("❌", key="quick_remove_no", use_container_width=True):
                                st.session_state[quick_remove_key] = False
                                st.rerun()
                
                # Add voting interface
                st.markdown("---")
                st.markdown("### 👍👎 Vote on this Milestone")
                goal_id = tracker.find_goal_for_milestone(selected_person, st.session_state.clicked_milestone_id)
                vote_summary = tracker.get_milestone_vote_summary(selected_person, goal_id, st.session_state.clicked_milestone_id)
                
                # Check if already voted
                has_vote = tracker.has_milestone_vote(selected_person, goal_id, st.session_state.clicked_milestone_id)
                current_vote = tracker.get_milestone_current_vote(selected_person, goal_id, st.session_state.clicked_milestone_id)
                
                # Display current vote status
                col_votes, col_buttons = st.columns([0.6, 0.4])
                with col_votes:
                    if has_vote:
                        vote_icon = "👍" if current_vote else " "
                        vote_text = "Thumbs Up" if current_vote else "Thumbs Down"
                        st.markdown(f"**Your vote:** {vote_icon} {vote_text}")
                        st.markdown("*You have already voted on this milestone*")
                    else:
                        st.markdown(f"**No vote yet** - Click to vote:")
                        st.markdown("👍 = Correct & Important | 👎 = Wrong or Unimportant")
                
                with col_buttons:
                    if has_vote:
                        # Show current vote status with disabled buttons and clear option
                        col_up, col_down = st.columns(2)
                        with col_up:
                            st.button("👍", key="vote_up", disabled=True, 
                                    use_container_width=True,
                                    help="You already voted on this milestone")
                        with col_down:
                            st.button("👎", key="vote_down", disabled=True, 
                                    use_container_width=True,
                                    help="You already voted on this milestone")
                        
                        # Add clear vote option for testing
                        if st.button("🔄 Clear Vote", key="clear_vote", use_container_width=True, 
                                   help="Clear your vote (for testing purposes)"):
                            if tracker.clear_milestone_vote(selected_person, goal_id, st.session_state.clicked_milestone_id):
                                st.success("🔄 Vote cleared!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to clear vote")
                                
                    else:
                        # Show voting buttons
                        col_up, col_down = st.columns(2)
                        with col_up:
                            if st.button("👍", key="vote_up", use_container_width=True, 
                                        help="This milestone is correct and important"):
                                if tracker.add_milestone_vote(selected_person, goal_id, st.session_state.clicked_milestone_id, True):
                                    st.success("👍 Vote added!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to add vote - you may have already voted")
                        with col_down:
                            if st.button("👎", key="vote_down", use_container_width=True,
                                        help="This milestone is wrong or unimportant"):
                                if tracker.add_milestone_vote(selected_person, goal_id, st.session_state.clicked_milestone_id, False):
                                    st.success("👎 Vote added!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to add vote - you may have already voted")
                
                st.markdown("---")

    # Add Sub-Roadmap Analysis Panel (Collapsible)
    tracker = st.session_state.tracker
    if tracker.selected_person and tracker.selected_goal:
        # Initialize session state for collapsible panel
        analysis_panel_key = f"show_analysis_{tracker.selected_person}_{tracker.selected_goal}"
        if analysis_panel_key not in st.session_state:
            st.session_state[analysis_panel_key] = False
        
        # Collapsible header with toggle button
        col_header, col_toggle = st.columns([0.8, 0.2])
        with col_header:
            st.markdown("### 🎯 Sub-Roadmap Analysis")
        with col_toggle:
            toggle_text = "🔽 Show" if not st.session_state[analysis_panel_key] else "🔼 Hide"
            if st.button(toggle_text, key=f"toggle_analysis_{tracker.selected_person}_{tracker.selected_goal}"):
                st.session_state[analysis_panel_key] = not st.session_state[analysis_panel_key]
                st.rerun()
        
        # Show analysis content only if expanded
        if st.session_state[analysis_panel_key]:
            with st.container(border=True):
                # Get sub-roadmap groups
                groups = tracker.get_sub_roadmap_groups(tracker.selected_person, tracker.selected_goal)
                
                if groups:
                    st.markdown(f"**Found {len(groups)} connected milestone groups:**")
                    
                    for i, group in enumerate(groups[:3]):  # Show top 3 most problematic
                        group_class = "problematic-group" if group['problematic_score'] < 0 else "good-group"
                        
                        with st.expander(f"Group {i+1} (Score: {group['problematic_score']:.2f}) - {group['size']} milestones"):
                            milestone_names = [m['name'] for m in group['milestones']]
                            st.markdown(f"**Milestones:** {', '.join(milestone_names[:3])}{'...' if len(milestone_names) > 3 else ''}")
                            
                            st.markdown(f"**Statistics:**")
                            st.markdown(f"- Total vote score: {group['total_vote_score']}")
                            st.markdown(f"- Average vote score: {group['avg_vote_score']:.2f}")
                            st.markdown(f"- Milestones with 👎: {group['thumbs_down_count']}")
                            
                            # Show individual milestone votes
                            for milestone in group['milestones']:
                                vote_summary = milestone['vote_summary']
                                if vote_summary['total_votes'] > 0:
                                    indicator = "👍" if vote_summary['thumbs_up'] > vote_summary['thumbs_down'] else "👎" if vote_summary['thumbs_down'] > vote_summary['thumbs_up'] else "➖"
                                    st.markdown(f"  {indicator} **{milestone['name']}**: 👍{vote_summary['thumbs_up']} 👎{vote_summary['thumbs_down']}")
                            
                            # Add group removal option if group should be removed
                            if tracker.should_remove_entire_group(group):
                                st.markdown("---")
                                st.error("🚨 **Highly Problematic Group Detected**")
                                st.markdown("This group has predominantly negative feedback or very low scores.")
                                
                                col_warn, col_remove = st.columns([0.7, 0.3])
                                with col_warn:
                                    st.markdown("⚠️ **Removing this group will delete all connected milestones**")
                                with col_remove:
                                    if st.button(f"🗑️ Remove Group {i+1}", key=f"remove_group_{i}", help="Remove all milestones in this problematic group", type="secondary"):
                                        removed_count = tracker.remove_milestone_group(tracker.selected_person, tracker.selected_goal, group['milestones'])
                                        if removed_count > 0:
                                            st.success(f"✅ Removed {removed_count} milestones from problematic group!")
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to remove group milestones")
                
                else:
                    st.info("No milestone groups found. Add some milestones to see analysis.")

    # Add Causal Insights Panel
    if tracker.selected_person and tracker.selected_goal:
        causal_insights = tracker.get_causal_insights(tracker.selected_person, tracker.selected_goal)
        if causal_insights:
            # Initialize session state for collapsible causal panel
            causal_panel_key = f"show_causal_{tracker.selected_person}_{tracker.selected_goal}"
            if causal_panel_key not in st.session_state:
                st.session_state[causal_panel_key] = False
            
            # Collapsible header with toggle button
            col_header, col_toggle = st.columns([0.8, 0.2])
            with col_header:
                st.markdown("### 🧠 Causal Analysis")
            with col_toggle:
                toggle_text = "🔽 Show" if not st.session_state[causal_panel_key] else "🔼 Hide"
                if st.button(toggle_text, key=f"toggle_causal_{tracker.selected_person}_{tracker.selected_goal}"):
                    st.session_state[causal_panel_key] = not st.session_state[causal_panel_key]
                    st.rerun()
            
            # Show causal insights content only if expanded
            if st.session_state[causal_panel_key]:
                with st.container(border=True):
                    st.markdown("**📊 Overview**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Milestones", causal_insights['total_milestones'])
                        st.metric("CAUSES Links", causal_insights['total_causes_relationships'])
                    with col2:
                        st.metric("HAS_MILESTONE Links", causal_insights['total_has_milestone_relationships'])
                        complexity = causal_insights['total_causes_relationships'] / causal_insights['total_milestones'] if causal_insights['total_milestones'] > 0 else 0
                        st.metric("Complexity", f"{complexity:.2f}")
                    
                    # Show connection summary
                    if causal_insights.get('connection_summary'):
                        st.markdown("**🔗 Connection Summary**")
                        conn_summary = causal_insights['connection_summary']
                        st.markdown(f"- **Person → Goal**: {conn_summary['person_to_goal']}")
                        st.markdown(f"- **Goal → Milestones**: {conn_summary['goal_to_milestones']}")
                        st.markdown(f"- **Milestone → Milestone**: {conn_summary['milestone_to_milestone']}")
                        st.markdown(f"- **Total Connections**: {conn_summary['total_connections']}")
                    
                    # Show relationship types distribution
                    if causal_insights.get('relationship_types_distribution'):
                        st.markdown("**📈 CAUSES Relationship Types**")
                        rel_types = causal_insights['relationship_types_distribution']
                        
                        # Create color mapping for relationship types
                        type_colors = {
                            'prerequisite': '🟠',
                            'direct_cause': '🔴', 
                            'supports': '🟢',
                            'enables': '🔵',
                            'mutual_reinforcement': '🟣'
                        }
                        
                        for rel_type, count in rel_types.items():
                            emoji = type_colors.get(rel_type, '⚪')
                            st.markdown(f"- {emoji} **{rel_type}**: {count} connections")
                    
                    st.markdown("---")
                    
                    # Show foundational milestones
                    if causal_insights['foundational_milestones']:
                        st.markdown("**🌱 Foundational Milestones** (Prerequisites for everything else)")
                        for milestone in causal_insights['foundational_milestones']:
                            score_class = get_score_badge_class(milestone['score'])
                            st.markdown(
                                f'<div class="milestone-item">'
                                f'<div class="milestone-info">'
                                f'<div class="milestone-name">{milestone["name"][:50]}...</div>'
                                f'</div>'
                                f'<span class="score-badge {score_class}">{milestone["score"]}/10</span>'
                                f'</div>', 
                                unsafe_allow_html=True
                            )
                    
                    st.markdown("---")
                    
                    # Show terminal milestones
                    if causal_insights['terminal_milestones']:
                        st.markdown("**🎯 Terminal Milestones** (Final outcomes)")
                        for milestone in causal_insights['terminal_milestones']:
                            score_class = get_score_badge_class(milestone['score'])
                            st.markdown(
                                f'<div class="milestone-item">'
                                f'<div class="milestone-info">'
                                f'<div class="milestone-name">{milestone["name"][:50]}...</div>'
                                f'</div>'
                                f'<span class="score-badge {score_class}">{milestone["score"]}/10</span>'
                                f'</div>', 
                                unsafe_allow_html=True
                            )
                    
                    st.markdown("---")
                    st.markdown("*🧠 This goal contains causal relationship data from AI analysis*")
                    st.markdown("*🎨 **Visualization**: HAS_MILESTONE (red), prerequisite (orange), direct_cause (red), supports (green), enables (blue), mutual_reinforcement (purple)*")

    # Add Milestone Management Section
    if tracker.selected_person and tracker.selected_goal:
        # Initialize session state for collapsible milestone management panel
        milestone_mgmt_key = f"show_milestone_mgmt_{tracker.selected_person}_{tracker.selected_goal}"
        if milestone_mgmt_key not in st.session_state:
            st.session_state[milestone_mgmt_key] = False
        
        # Collapsible header with toggle button
        col_header, col_toggle = st.columns([0.8, 0.2])
        with col_header:
            st.markdown("### 🗑️ Milestone Management")
        with col_toggle:
            toggle_text = "🔽 Show" if not st.session_state[milestone_mgmt_key] else "🔼 Hide"
            if st.button(toggle_text, key=f"toggle_milestone_mgmt_{tracker.selected_person}_{tracker.selected_goal}"):
                st.session_state[milestone_mgmt_key] = not st.session_state[milestone_mgmt_key]
                st.rerun()
        
        # Show milestone management content only if expanded
        if st.session_state[milestone_mgmt_key]:
            with st.container(border=True):
                goals = tracker.get_goals(tracker.selected_person)
                current_goal = goals[tracker.selected_goal]
                milestones = current_goal.get('milestones', {})
                
                if not milestones:
                    st.info("No milestones to manage in this goal.")
                else:
                    st.markdown(f"**Goal**: {current_goal['title']}")
                    st.markdown(f"**Total Milestones**: {len(milestones)}")
                    
                    # Quick stats
                    milestone_list = list(milestones.values())
                    avg_score = sum(ms.get('score', 0) for ms in milestone_list) / len(milestone_list)
                    low_score_count = len([ms for ms in milestone_list if ms.get('score', 0) < 4])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Average Score", f"{avg_score:.1f}/10")
                    with col2:
                        st.metric("Low Score (<4)", low_score_count)
                    with col3:
                        causal_count = len([ms for ms in milestone_list if ms.get('is_causal', False)])
                        st.metric("Causal Milestones", causal_count)
                    
                    st.markdown("---")
                    
                    # Bulk operations
                    st.markdown("**🔧 Bulk Operations**")
                    
                    # Select milestones to remove
                    milestone_options = {ms_id: f"{ms['name']} (Score: {ms['score']}/10)" 
                                       for ms_id, ms in milestones.items()}
                    
                    selected_for_removal = st.multiselect(
                        "Select milestones to remove:",
                        options=list(milestone_options.keys()),
                        format_func=lambda x: milestone_options[x],
                        help="Select multiple milestones to remove them all at once"
                    )
                    
                    if selected_for_removal:
                        # Show what will be affected
                        st.markdown("**⚠️ Removal Impact Preview:**")
                        
                        for ms_id in selected_for_removal:
                            ms = milestones[ms_id]
                            dependents = []
                            for other_id, other_ms in milestones.items():
                                if other_id != ms_id and (
                                    other_ms.get('predecessor') == ms_id or 
                                    ms_id in other_ms.get('predecessors', [])
                                ):
                                    dependents.append(other_ms['name'])
                            
                            if dependents:
                                st.markdown(f"- **{ms['name']}**: Will reconnect {len(dependents)} dependent milestone(s)")
                            else:
                                st.markdown(f"- **{ms['name']}**: No dependencies, safe to remove")
                        
                        # Bulk remove button with confirmation
                        bulk_confirm_key = f"bulk_remove_confirm_{tracker.selected_goal}"
                        
                        col1, col2 = st.columns([0.7, 0.3])
                        with col1:
                            if st.session_state.get(bulk_confirm_key, False):
                                st.error("⚠️ This will permanently delete the selected milestones!")
                        with col2:
                            if not st.session_state.get(bulk_confirm_key, False):
                                if st.button(f"🗑️ Remove {len(selected_for_removal)} Milestone(s)", 
                                           key="bulk_remove_btn", type="secondary"):
                                    st.session_state[bulk_confirm_key] = True
                                    st.rerun()
                            else:
                                col_yes, col_no = st.columns(2)
                                with col_yes:
                                    if st.button("✅ Confirm", key="bulk_confirm_yes", type="primary"):
                                        # Check if we're trying to remove all milestones
                                        if len(selected_for_removal) >= len(milestones):
                                            st.error("❌ Cannot remove all milestones from a goal! At least one milestone must remain.")
                                            st.session_state[bulk_confirm_key] = False
                                            st.rerun()
                                            return
                                        
                                        removed_count = 0
                                        failed_removals = []
                                        
                                        for ms_id in selected_for_removal:
                                            removed_milestone = tracker.remove_milestone(tracker.selected_person, tracker.selected_goal, ms_id)
                                            if removed_milestone:
                                                removed_count += 1
                                            else:
                                                failed_removals.append(milestone_options[ms_id])
                                        
                                        if removed_count > 0:
                                            st.success(f"✅ Successfully removed {removed_count} milestone(s)!")
                                        if failed_removals:
                                            st.error(f"❌ Failed to remove: {', '.join(failed_removals)}")
                                        
                                        st.session_state[bulk_confirm_key] = False
                                        st.rerun()
                                with col_no:
                                    if st.button("❌ Cancel", key="bulk_confirm_no"):
                                        st.session_state[bulk_confirm_key] = False
                                        st.rerun()
                    
                    st.markdown("---")
                    
                    # Quick filters for milestone management
                    st.markdown("**🔍 Quick Filters**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📉 Show Low Score Milestones (<4)", key="filter_low_score"):
                            low_score_milestones = [(ms_id, ms) for ms_id, ms in milestones.items() if ms.get('score', 0) < 4]
                            if low_score_milestones:
                                st.markdown("**Low Score Milestones:**")
                                for ms_id, ms in low_score_milestones:
                                    st.markdown(f"- **{ms['name']}** (Score: {ms['score']}/10)")
                            else:
                                st.info("No low score milestones found!")
                    
                    with col2:
                        if st.button("🔗 Show Causal Milestones", key="filter_causal"):
                            causal_milestones = [(ms_id, ms) for ms_id, ms in milestones.items() if ms.get('is_causal', False)]
                            if causal_milestones:
                                st.markdown("**Causal Milestones:**")
                                for ms_id, ms in causal_milestones:
                                    st.markdown(f"- **{ms['name']}** (Score: {ms['score']}/10)")
                            else:
                                st.info("No causal milestones found!")

    with st.container(border=True):
        ai_tab, dictation_tab, manual_tab = st.tabs(["🤖 AI Assistant", "🎤 Career Dictation", "📝 Manual Entry"])
        with ai_tab:
            render_interview_tab()
        with dictation_tab:
            render_career_dictation_tab()
        with manual_tab:
            render_manual_entry_tab()


# --- Manual Entry Logic (Unchanged) ---
def render_manual_entry_tab():
    st.markdown('<div class="section-header">Manual Milestone Management</div>', unsafe_allow_html=True)

    tracker = st.session_state.tracker
    selected_person = tracker.selected_person
    selected_goal = tracker.selected_goal
    target_node_id = st.session_state.get('add_milestone_target') or selected_goal

    if not selected_goal:
        st.info("Select a goal from the sidebar or graph to manage milestones.")
        return

    form_title = ""
    target_name = ""
    if target_node_id:
        if target_node_id == selected_goal:
            target_name = tracker.get_goals(selected_person)[selected_goal]['title']
            form_title = f"➕ Add New Milestone to Goal"
        else:
            target_milestone = tracker.get_milestone(selected_person, target_node_id)
            if target_milestone:
                target_name = target_milestone['name']
                form_title = f"➕ Add Step Related to Milestone"
    
    st.markdown(f"**Target:** `{target_name}`")

    # --- Resource Links UI ---
    with st.form(key=f"manual_add_form_{target_node_id}", clear_on_submit=True):
        st.markdown(f"**{form_title}**")
        milestone_name = st.text_input("Milestone Name", placeholder="e.g., 'Complete advanced Python course'")
        milestone_score = st.slider("Importance Score", 1, 10, 5)
        
        # Resource links input
        st.markdown("**Resource Links (optional):**")
        st.markdown("You can add multiple resources by separating names and URLs with commas. The order must match.")
        resource_names = st.text_area(
            "Resource Names (comma-separated)",
            placeholder="DAAD, Mitacs, Coursera",
            help="Enter one or more resource names, separated by commas. Example: DAAD, Mitacs, Coursera",
            key=f"resource_names_{target_node_id}"
        )
        resource_urls = st.text_area(
            "Resource URLs (comma-separated, in same order)",
            placeholder="https://daad.de, https://mitacs.ca, https://coursera.org",
            help="Enter the URLs for each resource, in the same order as the names, separated by commas.",
            key=f"resource_urls_{target_node_id}"
        )
        
        insert_position = "Parallel (Sub-task)"
        if target_node_id != selected_goal:
             insert_position = st.radio(
                "Relation to target:",
                ("Before (Prerequisite)", "After (Follow-up)", "Parallel (Sub-task)"),
                key=f"insert_pos_{target_node_id}", horizontal=True, index=2
            )

        if st.form_submit_button("🐝 Add Milestone", type="primary", use_container_width=True):
            if milestone_name.strip():
                success = False
                goal_for_milestone = tracker.find_goal_for_milestone(selected_person, target_node_id) or selected_goal
                
                parent_id = target_node_id
                if target_node_id == selected_goal:
                    parent_id = selected_goal # Add to the goal itself

                # Parse resources
                resources = []
                names = [n.strip() for n in resource_names.split(",") if n.strip()]
                urls = [u.strip() for u in resource_urls.split(",") if u.strip()]
                for n, u in zip(names, urls):
                    if n and u:
                        resources.append({"name": n, "url": u})

                if "Before" in insert_position:
                    success = tracker.insert_milestone_before(selected_person, goal_for_milestone, milestone_name.strip(), milestone_score, target_node_id, resources=resources)
                elif "After" in insert_position:
                    success = tracker.insert_milestone_after(selected_person, goal_for_milestone, milestone_name.strip(), milestone_score, target_node_id, resources=resources)
                else: # "Parallel"
                    success = tracker.add_child_milestone(selected_person, goal_for_milestone, milestone_name.strip(), milestone_score, parent_id, resources=resources)
                
                if success:
                    st.success("✅ Milestone Added!")
                    st.session_state.add_milestone_target = None 
                    st.rerun()
                else:
                    st.error("❌ Failed to add milestone.")
            else:
                st.warning("⚠️ Please enter a milestone name.")
    
    st.markdown("---")
    goal_title = tracker.get_goals(selected_person)[selected_goal]['title']
    st.markdown(f"##### 📋 Current Milestones for '{goal_title}'")
    
    with st.container(height=250):
        current_milestones = tracker.get_ordered_milestones_for_goal(selected_person, selected_goal)
        if not current_milestones:
            st.info("This goal has no milestones yet.")
        else:
            for milestone in current_milestones:
                # Create expandable milestone item with edit capabilities
                with st.expander(f"⭐ {milestone['score']}/10 - {milestone['name']}", expanded=False):
                    col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
                    
                    with col1:
                        st.markdown(f"**Name:** {milestone['name']}")
                        st.markdown(f"**ID:** `{milestone['id'][:8]}...`")
                        if milestone.get('is_causal'):
                            st.markdown("**Type:** 🔗 Causal prerequisite")
                        else:
                            st.markdown("**Type:** 📋 Regular milestone")
                        # Display resources if present
                        resources = milestone.get('resources', [])
                        if resources:
                            st.markdown("**Resources:**")
                            for res in resources:
                                st.markdown(f"- [{res['name']}]({res['url']})")
                        # Edit resources UI
                        edit_btn_key = f"edit_resources_btn_{milestone['id']}"
                        edit_flag_key = f"edit_resources_flag_{milestone['id']}"
                        if st.button("✏️ Edit Resources", key=edit_btn_key):
                            st.session_state[edit_flag_key] = True
                        if st.session_state.get(edit_flag_key, False):
                            # Show edit form
                            existing_names = ", ".join([r['name'] for r in resources])
                            existing_urls = ", ".join([r['url'] for r in resources])
                            with st.form(key=f"edit_resources_form_{milestone['id']}", clear_on_submit=True):
                                new_names = st.text_area("Resource Names (comma-separated)", value=existing_names, key=f"edit_names_{milestone['id']}")
                                new_urls = st.text_area("Resource URLs (comma-separated, in same order)", value=existing_urls, key=f"edit_urls_{milestone['id']}")
                                col_save, col_cancel = st.columns(2)
                                with col_save:
                                    if st.form_submit_button("💾 Save Resources", use_container_width=True):
                                        names = [n.strip() for n in new_names.split(",") if n.strip()]
                                        urls = [u.strip() for u in new_urls.split(",") if u.strip()]
                                        new_resources = []
                                        for n, u in zip(names, urls):
                                            if n and u:
                                                new_resources.append({"name": n, "url": u})
                                        tracker.update_milestone_resources(selected_person, selected_goal, milestone['id'], new_resources)
                                        st.session_state[edit_flag_key] = False
                                        st.success("Resources updated!")
                                        st.rerun()
                                with col_cancel:
                                    if st.form_submit_button("Cancel", use_container_width=True):
                                        st.session_state[edit_flag_key] = False
                                        st.rerun()
                    
                    with col2:
                        # Score editor
                        new_score = st.slider(
                            "Importance",
                            min_value=1,
                            max_value=10,
                            value=milestone['score'],
                            key=f"score_slider_{milestone['id']}"
                        )
                        
                        if new_score != milestone['score']:
                            if st.button("💾 Update", key=f"update_score_{milestone['id']}", 
                                       use_container_width=True, type="secondary"):
                                if tracker.update_milestone_score(selected_person, selected_goal, milestone['id'], new_score):
                                    st.success(f"✅ Score updated to {new_score}!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to update score")
                    
                    with col3:
                        remove_confirm_key = f"confirm_remove_{milestone['id']}"
                        
                        # Check if we're in confirmation mode for this milestone
                        if st.session_state.get(remove_confirm_key, False):
                            st.markdown("⚠️ **Confirm removal?**")
                            col_confirm, col_cancel = st.columns(2)
                            
                            with col_confirm:
                                if st.button("✅ Yes", key=f"confirm_yes_{milestone['id']}", 
                                           use_container_width=True, type="primary"):
                                    # Check if this is the last milestone
                                    milestones_dict = tracker.get_goals(selected_person)[selected_goal]['milestones']
                                    if len(milestones_dict) <= 1:
                                        st.error("❌ Cannot remove the last milestone from a goal!")
                                        st.session_state[remove_confirm_key] = False
                                        return
                                    
                                    # Find dependent milestones to show user what will be affected
                                    dependents = []
                                    for ms_id, ms in milestones_dict.items():
                                        if (ms.get('predecessor') == milestone['id'] or 
                                            milestone['id'] in ms.get('predecessors', [])):
                                            dependents.append(ms['name'])
                                    
                                    removed_milestone = tracker.remove_milestone(selected_person, selected_goal, milestone['id'])
                                    if removed_milestone:
                                        success_msg = f"🗑️ Milestone '{milestone['name']}' removed!"
                                        if dependents:
                                            success_msg += f"\n📎 {len(dependents)} dependent milestone(s) reconnected: {', '.join(dependents[:3])}{'...' if len(dependents) > 3 else ''}"
                                        st.success(success_msg)
                                        st.session_state[remove_confirm_key] = False
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to remove milestone - it may be the last one in the goal")
                                        st.session_state[remove_confirm_key] = False
                            
                            with col_cancel:
                                if st.button("❌ No", key=f"confirm_no_{milestone['id']}", 
                                           use_container_width=True):
                                    st.session_state[remove_confirm_key] = False
                                    st.rerun()
                        else:
                            # Show initial remove button
                            if st.button("🗑️ Remove", key=f"remove_expand_{milestone['id']}", 
                                       use_container_width=True, type="secondary"):
                                st.session_state[remove_confirm_key] = True
                                st.rerun()

def render_career_dictation_tab():
    """Render the career dictation interface where users can record their entire career story"""
    st.markdown('<div class="section-header">🎤 Career Story Dictation</div>', unsafe_allow_html=True)
    
    tracker = st.session_state.tracker
    selected_person = tracker.selected_person
    
    if not selected_person:
        st.info("👤 Please select a person from the sidebar to start career dictation.")
        return
    
    st.markdown(f"### Recording Career Story for: **{selected_person}**")
    st.markdown("Click the microphone button below to start recording your complete career journey. Speak naturally about your education, work experience, achievements, and goals.")
    
    # Initialize session state for dictation
    dictation_key = f"career_dictation_{selected_person}"
    if dictation_key not in st.session_state:
        st.session_state[dictation_key] = {
            "is_recording": False,
            "transcription": "",
            "audio_chunks": [],
            "session_id": str(uuid.uuid4())
        }
    
    dictation_session = st.session_state[dictation_key]
    
    # Audio recording interface
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Recording status
        if dictation_session["is_recording"]:
            st.markdown("🔴 **RECORDING IN PROGRESS**")
            st.markdown("Speak clearly about your career journey...")
        else:
            st.markdown("⚪ **READY TO RECORD**")
            st.markdown("Click start when you're ready to share your career story")
    
    # Control buttons
    col_start, col_stop, col_clear = st.columns(3)
    
    with col_start:
        if st.button(
            "🎤 Start Recording" if not dictation_session["is_recording"] else "⏸️ Recording...", 
            disabled=dictation_session["is_recording"],
            use_container_width=True,
            type="primary"
        ):
            dictation_session["is_recording"] = True
            dictation_session["transcription"] = ""
            st.success("🎤 Recording started! Begin speaking...")
            st.rerun()
    
    with col_stop:
        if st.button(
            "⏹️ Stop & Transcribe", 
            disabled=not dictation_session["is_recording"],
            use_container_width=True,
            type="secondary"
        ):
            dictation_session["is_recording"] = False
            
            # Simulate audio transcription (in real implementation, this would use audio recording)
            st.info("🔄 Processing audio and transcribing...")
            
            # For demo purposes, we'll use a text area for manual input
            # In real implementation, this would be replaced with actual audio transcription
            st.session_state[f"{dictation_key}_show_input"] = True
            st.rerun()
    
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            dictation_session["transcription"] = ""
            dictation_session["is_recording"] = False
            if f"{dictation_key}_show_input" in st.session_state:
                del st.session_state[f"{dictation_key}_show_input"]
            st.success("Cleared recording session")
            st.rerun()
    
    # Show manual input area when recording is stopped (demo simulation)
    if st.session_state.get(f"{dictation_key}_show_input", False):
        st.markdown("---")
        st.markdown("### 📝 **Transcribe Your Career Story**")
        st.info("💡 In the demo mode, please type your career story below. In production, this would be automatically transcribed from your voice recording.")
        
        career_story = st.text_area(
            "Your Career Story:",
            height=200,
            placeholder="Tell your complete career journey here... Include your education, work experience, achievements, challenges overcome, skills developed, and future goals...",
            key=f"career_input_{dictation_key}"
        )
        
        if st.button("🎯 Process Career Story", type="primary", use_container_width=True):
            if career_story.strip():
                dictation_session["transcription"] = career_story
                
                # Process with AI to extract career insights
                with st.spinner("🤖 AI is analyzing your career story..."):
                    # Initialize interview agent if not exists
                    if "interview_agent" not in st.session_state:
                        st.session_state.interview_agent = LLMAgent(api_key=OPENAI_API_KEY)
                        st.session_state.interview_agent.load_parameters(INTERVIEW_PARAMETERS["ROADMAP_DETAILER"])
                    
                    # Save transcription to file
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"career_story_{selected_person}_{timestamp}.txt"
                    
                    # Create the career story content
                    career_content = f"""CAREER STORY TRANSCRIPTION
=========================
Person: {selected_person}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Session ID: {dictation_session['session_id']}

FULL CAREER NARRATIVE:
{career_story}

=========================
Generated by Robee's Career Milestone Tracker
"""
                    
                    # Provide download button for the transcription
                    st.success("✅ Career story processed successfully!")
                    st.download_button(
                        label="📥 Download Career Story (TXT)",
                        data=career_content,
                        file_name=filename,
                        mime="text/plain",
                        help="Download your complete career story transcription"
                    )
                    
                    # Show AI analysis
                    try:
                        # Create a simple analysis prompt
                        analysis_prompt = f"""
                        Analyze this career story and identify:
                        1. Key career milestones and achievements
                        2. Educational background
                        3. Professional experience
                        4. Skills and competencies developed
                        5. Career progression patterns
                        6. Future goals and aspirations
                        
                        Career Story:
                        {career_story}
                        """
                        
                        # For demo, we'll show a structured analysis
                        st.markdown("---")
                        st.markdown("### 🧠 **AI Career Analysis**")
                        
                        with st.expander("📊 Career Insights", expanded=True):
                            st.markdown("**Key Themes Identified:**")
                            st.markdown("• Career progression and growth")
                            st.markdown("• Skill development journey")
                            st.markdown("• Professional achievements")
                            st.markdown("• Educational foundation")
                            st.markdown("• Future aspirations")
                            
                            st.markdown("**💡 Potential Milestone Suggestions:**")
                            st.info("Based on your story, the AI could suggest specific milestones to add to your roadmap. This would integrate with the existing milestone detection system.")
                            
                            # Show word count and basic stats
                            word_count = len(career_story.split())
                            char_count = len(career_story)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Word Count", word_count)
                            with col2:
                                st.metric("Characters", char_count)
                            with col3:
                                st.metric("Session Time", "Live")
                    
                    except Exception as e:
                        st.error(f"Analysis error: {e}")
                    
                    # Clear the input flag
                    del st.session_state[f"{dictation_key}_show_input"]
            else:
                st.warning("Please enter your career story before processing.")
    
    # Display previous transcription if exists
    if dictation_session["transcription"] and not st.session_state.get(f"{dictation_key}_show_input", False):
        st.markdown("---")
        st.markdown("### 📋 **Previous Career Story**")
        with st.expander("View Last Transcription", expanded=False):
            st.text_area(
                "Career Story:",
                value=dictation_session["transcription"],
                height=150,
                disabled=True,
                key=f"previous_story_{dictation_key}"
            )
            
            # Option to re-download
            if st.button("📥 Re-download Story", key=f"redownload_{dictation_key}"):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"career_story_{selected_person}_{timestamp}.txt"
                career_content = f"""CAREER STORY TRANSCRIPTION
=========================
Person: {selected_person}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Session ID: {dictation_session['session_id']}

FULL CAREER NARRATIVE:
{dictation_session["transcription"]}

=========================
Generated by Robee's Career Milestone Tracker
"""
                st.download_button(
                    label="📥 Download Career Story (TXT)",
                    data=career_content,
                    file_name=filename,
                    mime="text/plain",
                    help="Download your complete career story transcription",
                    key=f"redownload_btn_{dictation_key}"
                )

def render_interview_tab():
    st.markdown('<div class="section-header">Milestone Interview Chatbot</div>', unsafe_allow_html=True)
    tracker = st.session_state.tracker
    selected_person = tracker.selected_person
    selected_goal = tracker.selected_goal

    if not selected_goal:
        st.info("Select a goal to start the interview.")
        return

    # Initialize the interview agent in session state if not already
    if "interview_agent" not in st.session_state:
        st.session_state.interview_agent = LLMAgent(api_key=OPENAI_API_KEY)
        st.session_state.interview_agent.load_parameters(INTERVIEW_PARAMETERS["ROADMAP_DETAILER"])

    milestones = tracker.get_ordered_milestones_for_goal(selected_person, selected_goal)
    goal_data = tracker.get_goals(selected_person)[selected_goal]
    
    # NEW: Get most problematic group for AI focus
    most_problematic = tracker.get_most_problematic_group(selected_person, selected_goal)
    
    # NEW: When goal is clicked, start interview about the goal and its milestones
    interview_key = f"interview_session_{selected_person}_{selected_goal}_GOAL"
    
    # Check if strategy should be updated due to voting changes
    voting_state_key = f"voting_state_{selected_person}_{selected_goal}"
    current_voting_state = {}
    for ms in milestones:
        vote_summary = tracker.get_milestone_vote_summary(selected_person, selected_goal, ms['id'])
        current_voting_state[ms['id']] = {
            'thumbs_up': vote_summary['thumbs_up'],
            'thumbs_down': vote_summary['thumbs_down']
        }
    
    # If session exists, check if voting state changed
    if interview_key in st.session_state:
        last_voting_state = st.session_state.get(voting_state_key, {})
        if current_voting_state != last_voting_state:
            # Voting changed, update the focus strategy
            updated_most_problematic = tracker.get_most_problematic_group(selected_person, selected_goal)
            st.session_state[interview_key]["focus_group"] = updated_most_problematic
            st.session_state[voting_state_key] = current_voting_state
            
            # Add a system message about strategy change
            if updated_most_problematic:
                strategy_name = {'problematic': 'problematic milestone fixing', 'gaps': 'gap finding', 'general': 'general exploration'}[updated_most_problematic['focus_strategy']]
                strategy_change_msg = f"🔄 **Strategy Updated**: Now focusing on {strategy_name} based on your voting feedback"
                st.session_state[interview_key]["messages"].append({
                    "type": "system", "content": strategy_change_msg, "topic_idx": 0, "summary": ""
                })
                
                # Generate adaptive follow-up question based on new strategy
                if updated_most_problematic['focus_strategy'] == 'problematic':
                    problematic_milestones = updated_most_problematic['problematic_milestones']
                    if problematic_milestones:
                        lowest_problematic = min(problematic_milestones, key=lambda m: m.get('score', 0))
                        adaptive_question = f"I notice you've downvoted some milestones. Let's focus on '**{lowest_problematic['name']}**' - what specific issues do you see with this milestone that we should address?"
                    else:
                        adaptive_question = "I see your voting feedback. What would you like to focus on next?"
                elif updated_most_problematic['focus_strategy'] == 'gaps':
                    confirmed_milestones = updated_most_problematic['confirmed_milestones']
                    if confirmed_milestones:
                        lowest_confirmed = min(confirmed_milestones, key=lambda m: m.get('score', 0))
                        adaptive_question = f"Great to see you've confirmed some milestones! Let's find missing steps around '**{lowest_confirmed['name']}**' - what prerequisites were needed before this milestone?"
                    else:
                        adaptive_question = "I see you've confirmed some milestones. Let's find missing prerequisites around them."
                else:
                    adaptive_question = "Based on your feedback, let's continue exploring the connections between your milestones."
                
                st.session_state[interview_key]["messages"].append({
                    "type": "question", "content": adaptive_question, "topic_idx": 0, "summary": ""
                })
    
    if interview_key not in st.session_state:
        # Create a new goal-focused interview session
        existing_milestones = [ms['name'] for ms in milestones]
        milestone_list = "\n".join([f"- {ms['name']} (Score: {ms['score']}/10)" for ms in milestones])
        
        # Count milestones linked to the goal (works for both standard and causal formats)
        directly_linked_milestones = []
        for ms in milestones:
            # Standard format: predecessor == selected_goal
            # Causal format: selected_goal in predecessors list
            if (ms.get('predecessor') == selected_goal or 
                selected_goal in ms.get('predecessors', [])):
                directly_linked_milestones.append(ms)
        
        # Fallback: if no direct connections found, use all milestones to prevent 0 questions
        if not directly_linked_milestones and milestones:
            directly_linked_milestones = milestones
        
        st.session_state[interview_key] = {
            "messages": [],
            "summary": "",
            "session_id": str(uuid.uuid4()),
            "milestone_name": f"GOAL: {goal_data['title']}",
            "show_summary_ui": False,
            "summary_suggestions": [],
            "questions_asked": 0,
            "max_questions": len(directly_linked_milestones) * 6,  # Dynamic: 6 questions per milestone directly linked to goal
            "focus_group": most_problematic  # NEW: Focus on most problematic group
        }
        
        # Store initial voting state
        st.session_state[voting_state_key] = current_voting_state
        
        # Generate initial question based on problematic group analysis
        if most_problematic:
            focus_strategy = most_problematic['focus_strategy']
            group_milestones = most_problematic['group']['milestones']
            
            if focus_strategy == 'problematic':
                # Focus on the lowest-scoring problematic milestone first
                problematic_milestones = most_problematic['problematic_milestones']
                if problematic_milestones:
                    # Find the milestone with the lowest score among problematic ones
                    lowest_score_milestone = min(problematic_milestones, key=lambda m: m.get('score', 0))
                    first_question = f"Looking at your goal **{goal_data['title']}**, I notice some milestones that need attention.\n\nLet's start with '**{lowest_score_milestone['name']}**' - this milestone has received negative feedback. What specific issues do you see with this milestone? What would be a better alternative or how should we correct it?"
                else:
                    # Fallback if no problematic milestones found
                    first_question = f"I can see your goal: **{goal_data['title']}**. Let's explore the connections between your milestones - what prerequisites or missing steps exist? Start with your first milestone."
                    
            elif focus_strategy == 'gaps':
                # Focus on gaps around confirmed milestones, starting with lowest-scored confirmed milestone
                confirmed_milestones = most_problematic['confirmed_milestones']
                if confirmed_milestones:
                    lowest_confirmed = min(confirmed_milestones, key=lambda m: m.get('score', 0))
                    first_question = f"I can see your goal: **{goal_data['title']}** and you have some well-validated milestones.\n\nLet's find missing prerequisites around '**{lowest_confirmed['name']}**' - what specific steps or requirements were needed BEFORE you could start working on this milestone?"
                else:
                    first_question = f"Let's explore the connections in your goal **{goal_data['title']}** - what prerequisites or missing steps exist between these milestones?"
                    
            else:
                # General approach for unvoted groups - start with lowest-scored milestone
                if group_milestones:
                    lowest_milestone = min(group_milestones, key=lambda m: m.get('score', 0))
                    first_question = f"I can see your goal: **{goal_data['title']}** with milestone cluster including '**{lowest_milestone['name']}**'.\n\nLet's explore the connections - what prerequisites or missing steps exist before this milestone? What came before '**{lowest_milestone['name']}**'?"
                else:
                    first_question = f"I can see your goal: **{goal_data['title']}**. Let's explore what milestones and prerequisites are needed to achieve this goal."
        else:
            # Fallback to original approach if no groups
            if existing_milestones:
                first_ms = existing_milestones[0]
                first_question = f"I can see your goal: **{goal_data['title']}** with these existing milestones:\n{milestone_list}\n\nLet's find missing prerequisites and connections. Looking at your first milestone '**{first_ms}**', what specific requirements or steps were needed before you could even start working on it?"
            else:
                first_question = f"I can see your goal: **{goal_data['title']}** but it has no milestones yet. What were the very first steps or requirements you needed to work towards this goal?"
        
        st.session_state[interview_key]["messages"].append({
            "type": "question", "content": first_question, "topic_idx": 0, "summary": ""
        })

    session = st.session_state[interview_key]
    questions_asked_count = session.get("questions_asked", 0)
    max_questions = session.get("max_questions", 6)

    agent = st.session_state.interview_agent

    # === COMPREHENSIVE GAP ANALYSIS REPORT ===
    comprehensive_analysis_key = f"comprehensive_gap_analysis_{interview_key}"
    if comprehensive_analysis_key in st.session_state:
        with st.expander("📊 Comprehensive Gap Analysis Report", expanded=False):
            analysis = st.session_state[comprehensive_analysis_key]
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("### 🎯 Analysis Summary")
                if analysis.get('comprehensive_summary'):
                    st.write(analysis['comprehensive_summary'])
                
                if analysis.get('pattern_analysis'):
                    st.markdown("### 🔍 Pattern Analysis")
                    for pattern in analysis['pattern_analysis']:
                        st.write(f"• **{pattern.get('pattern_type', 'Unknown')}**: {pattern.get('description', 'No description')}")
                
                if analysis.get('dependency_gaps'):
                    st.markdown("### 🔗 Dependency Gaps")
                    for gap in analysis['dependency_gaps']:
                        st.write(f"• **{gap.get('from_milestone', 'Unknown')}** → **{gap.get('to_milestone', 'Unknown')}**")
                        st.write(f"  *Missing: {gap.get('missing_dependency', 'Unknown connection')}*")
                
                if analysis.get('milestone_suggestions'):
                    st.markdown("### 💡 Recommended Milestones")
                    for suggestion in analysis['milestone_suggestions']:
                        st.write(f"• **{suggestion.get('name', 'Untitled')}**")
                        st.write(f"  *Type: {suggestion.get('type', 'Unknown')}, Priority: {suggestion.get('priority', 'Medium')}*")
                        if suggestion.get('rationale'):
                            st.write(f"  *Rationale: {suggestion['rationale']}*")
            
            with col2:
                st.markdown("### 📈 Metrics")
                if analysis.get('analysis_confidence'):
                    confidence = analysis['analysis_confidence']
                    color = "🟢" if confidence >= 7 else "🟡" if confidence >= 4 else "🔴"
                    st.metric("Confidence Score", f"{confidence:.1f}/10", help="Overall confidence in the gap analysis")
                
                if analysis.get('coverage_assessment'):
                    coverage = analysis['coverage_assessment']
                    st.metric("Coverage", f"{coverage.get('percentage', 0):.1f}%", help="Percentage of goal covered by current milestones")
                
                if analysis.get('personalization_score'):
                    personalization = analysis['personalization_score']
                    st.metric("Personalization", f"{personalization:.1f}/10", help="How well recommendations match user profile")
                
                # Action buttons
                st.markdown("### 🚀 Actions")
                if st.button("🔄 Refresh Analysis", key="refresh_gap_analysis"):
                    try:
                        with st.spinner("Refreshing gap analysis..."):
                            new_analysis = agent.analyze_gap_patterns(
                                session["messages"],
                                goal_data['title'],
                                existing_milestones=[ms['name'] for ms in milestones]
                            )
                            st.session_state[comprehensive_analysis_key] = new_analysis
                            st.success("✅ Analysis refreshed!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error refreshing analysis: {str(e)}")
                
                if st.button("📥 Export Report", key="export_gap_report"):
                    # Create exportable report
                    report_content = f"""# Gap Analysis Report for {goal_data['title']}

## Summary
{analysis.get('comprehensive_summary', 'No summary available')}

## Detected Patterns
"""
                    if analysis.get('pattern_analysis'):
                        for pattern in analysis['pattern_analysis']:
                            report_content += f"- **{pattern.get('pattern_type', 'Unknown')}**: {pattern.get('description', 'No description')}\n"
                    
                    report_content += "\n## Recommended Milestones\n"
                    if analysis.get('milestone_suggestions'):
                        for suggestion in analysis['milestone_suggestions']:
                            report_content += f"- **{suggestion.get('name', 'Untitled')}** ({suggestion.get('type', 'Unknown')}) - {suggestion.get('rationale', 'No rationale')}\n"
                    
                    st.download_button(
                        label="Download Report",
                        data=report_content,
                        file_name=f"gap_analysis_{goal_data['title'].replace(' ', '_')}.md",
                        mime="text/markdown"
                    )

    # Display current milestone being discussed with dynamic strategy info
    st.markdown(f"**📋 Currently exploring:** {session['milestone_name']}")
    
    # Check if strategy was recently updated
    recent_messages = session["messages"][-3:] if len(session["messages"]) >= 3 else session["messages"]
    strategy_updated = any(msg.get("type") == "system" and "Strategy Updated" in msg.get("content", "") for msg in recent_messages)
    
    # Dynamic question counter and strategy display based on current voting state
    most_problematic_current = tracker.get_most_problematic_group(selected_person, selected_goal)
    if most_problematic_current:
        strategy = most_problematic_current['focus_strategy']
        if strategy == 'problematic':
            problematic_milestones = most_problematic_current['problematic_milestones']
            if problematic_milestones:
                lowest_problematic = min(problematic_milestones, key=lambda m: m.get('score', 0))
                strategy_info = f"🎯 Fixing: '{lowest_problematic['name']}' (👎 downvoted)"
            else:
                strategy_info = f"🎯 Focus: Fixing problematic milestones"
        elif strategy == 'gaps':
            confirmed_milestones = most_problematic_current['confirmed_milestones']
            if confirmed_milestones:
                lowest_confirmed = min(confirmed_milestones, key=lambda m: m.get('score', 0))
                strategy_info = f"🔍 Gaps around: '{lowest_confirmed['name']}' (👍 confirmed)"
            else:
                strategy_info = f"🔍 Focus: Finding gaps around confirmed milestones"
        else:
            group_milestones = most_problematic_current['group']['milestones']
            if group_milestones:
                lowest_milestone = min(group_milestones, key=lambda m: m.get('score', 0))
                strategy_info = f"🧩 Exploring: '{lowest_milestone['name']}' cluster"
            else:
                strategy_info = f"🧩 Focus: Exploring milestone cluster"
    else:
        strategy_info = "🚀 Focus: General goal exploration"
    
    status_indicator = "🔄 **UPDATED**" if strategy_updated else ""
    st.markdown(f"**❓ Questions:** {questions_asked_count}/{max_questions} | {strategy_info} {status_indicator}")

    # Display chat history
    chat_container = st.container(height=350, border=False)
    with chat_container:
        for msg in session["messages"]:
            if msg["type"] == "system":
                # Display system messages differently
                st.info(msg["content"])
            elif msg["type"] == "guidance":
                # Display safety guidance with special styling
                st.markdown(f'<div class="safety-guidance">{msg["content"]}</div>', unsafe_allow_html=True)
            elif msg["type"] == "intervention":
                # Display safety intervention with special styling
                st.markdown(f'<div class="safety-intervention">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                with st.chat_message("assistant" if msg["type"] == "question" else "user"):
                    st.markdown(msg["content"])

    # --- Chat input and Pass button ---
    col_input, col_pass = st.columns([0.7, 0.3])
    with col_input:
        user_input = st.chat_input(f"Tell me about prerequisites and steps for {goal_data['title']}...", key=f"interview_input_{interview_key}")
    with col_pass:
        pass_clicked = st.button("⏭️ Pass", key=f"pass_btn_{interview_key}", use_container_width=True)

    # Track consecutive passes in session state
    pass_count_key = f"consecutive_passes_{interview_key}"
    if pass_count_key not in st.session_state:
        st.session_state[pass_count_key] = 0

    if user_input:
        # === SAFETY AGENT: Hidden moderation for enhanced discussion ===
        # Create interview context for moderation
        interview_context = InterviewContext(
            topic=f"Career Development - {goal_data['title']}",
            stage="behavioral",  # Career discussions are behavioral in nature
            key_skills=["career planning", "goal setting", "milestone development", "professional growth"]
        )
        
        # Get recent conversation history for context using enhanced helper
        conversation_history = create_enhanced_conversation_context(session["messages"], goal_data['title'])
        
        # Get the current question context for better moderation
        current_question = ""
        current_milestone_context = ""
        if session["messages"]:
            # Find the most recent question
            for msg in reversed(session["messages"]):
                if msg.get("type") == "question":
                    current_question = msg.get("content", "")
                    break
        
        # Extract milestone context from current question or strategy
        current_problematic = tracker.get_most_problematic_group(selected_person, selected_goal)
        if current_problematic:
            strategy = current_problematic['focus_strategy']
            if strategy == 'problematic':
                problematic_milestones = current_problematic['problematic_milestones']
                if problematic_milestones:
                    lowest_problematic = min(problematic_milestones, key=lambda m: m.get('score', 0))
                    current_milestone_context = f"Currently discussing milestone: '{lowest_problematic['name']}'"
            elif strategy == 'gaps':
                confirmed_milestones = current_problematic['confirmed_milestones']
                if confirmed_milestones:
                    lowest_confirmed = min(confirmed_milestones, key=lambda m: m.get('score', 0))
                    current_milestone_context = f"Currently finding gaps around milestone: '{lowest_confirmed['name']}'"
            else:
                group_milestones = current_problematic['group']['milestones']
                if group_milestones:
                    lowest_milestone = min(group_milestones, key=lambda m: m.get('score', 0))
                    current_milestone_context = f"Currently exploring milestone: '{lowest_milestone['name']}'"
        
        enhanced_interview_topic = f"Career Development - {goal_data['title']}"
        if current_milestone_context:
            enhanced_interview_topic += f" | {current_milestone_context}"
        if current_question:
            # Extract key context from current question
            enhanced_interview_topic += f" | Current question context: {current_question[:100]}..."
        
        # Moderate user input (as interviewee answer)
        moderation_result = moderate_interview_input_groq(
            text=user_input,
            is_chatbot_question=False,  # This is user's answer
            interview_topic=enhanced_interview_topic,
            groq_api_key='groq_api_key',  # Replace with actual key or retrieval method
            interview_stage="behavioral",
            key_skills=["career planning", "goal setting", "milestone development"],
            conversation_history=conversation_history,
            moderator=st.session_state.safety_moderator
        )
        
        # Update moderation statistics
        st.session_state.moderation_stats['total_checks'] += 1
        
        # Handle moderation results with enhanced context awareness
        if not moderation_result['is_valid']:
            st.session_state.moderation_stats['flagged_answers'] += 1
            
            # Check if the user is actually answering a milestone-specific question
            is_answering_milestone_question = False
            if current_question:
                # Check if current question mentions specific milestones
                milestone_names = [ms['name'].lower() for ms in milestones]
                question_lower = current_question.lower()
                is_answering_milestone_question = any(
                    milestone_name in question_lower for milestone_name in milestone_names
                ) or any(keyword in question_lower for keyword in [
                    'milestone', 'prerequisite', 'requirement', 'step', 'before', 'needed for'
                ])
            
            # Be more lenient if user is clearly answering milestone-related questions
            if is_answering_milestone_question and not moderation_result.get('severe_violation', False):
                # Skip moderation for milestone-specific answers unless it's a severe violation
                print(f"DEBUG: Skipping moderation - user answering milestone question: {current_question[:50]}...")
            elif moderation_result['should_stop']:
                # Severe violation - end interview gracefully
                st.session_state.moderation_stats['interventions'] += 1
                session["messages"].append({
                    "type": "system", 
                    "content": "🛡️ **Discussion Focus**: Let's keep our conversation focused on your career development and professional goals. What specific challenges or next steps would you like to explore?", 
                    "topic_idx": 0, 
                    "summary": session["summary"]
                })
                st.rerun()  # Refresh to show the intervention message
                return
            
            elif moderation_result['should_realign'] and not is_answering_milestone_question:
                # Gentle redirection - but only if not answering milestone questions
                st.session_state.moderation_stats['suggestions_provided'] += 1
                guidance_message = get_safety_intervention_message(
                    st.session_state.safety_moderator.consecutive_violations,
                    goal_data['title']
                )
                session["messages"].append({
                    "type": "guidance", 
                    "content": f"💡 <strong>Staying on Track</strong>: {guidance_message}", 
                    "topic_idx": 0, 
                    "summary": session["summary"]
                })
        
        # Continue with normal processing - add user input to conversation
        session["messages"].append({"type": "answer", "content": user_input, "topic_idx": 0, "summary": session["summary"]})
        st.session_state[pass_count_key] = 0  # Reset pass counter on any answer
        with st.spinner("🤖 AI is analyzing..."):
            try:
                # NEW: Check stopping condition
                if questions_asked_count >= max_questions:
                    next_question = f"Thank you for sharing those details about **{goal_data['title']}**! I've gathered enough information about the prerequisites and missing steps. Click 'Show Summary' to see all the suggested milestones I found."
                elif len(user_input.strip()) < 10:  # NEW: Check if response is too brief
                    next_question = "Could you provide more details? I'm looking for specific steps, requirements, or prerequisites that were needed for your goal."
                else:
                    # NEW: Generate strategy-based questions based on current voting state
                    existing_milestones = [ms['name'] for ms in milestones]
                    
                    # === GAP DETECTION: Analyze conversation for missing prerequisites ===
                    try:
                        # Detect gaps and missing prerequisites from conversation
                        gap_analysis = agent.detect_prerequisites_gaps(session["messages"], goal_data['title'])
                        
                        # Store gap analysis in session for potential display
                        if f"gap_analysis_{interview_key}" not in st.session_state:
                            st.session_state[f"gap_analysis_{interview_key}"] = []
                        
                        if gap_analysis and gap_analysis.get('gaps_found'):
                            st.session_state[f"gap_analysis_{interview_key}"].append(gap_analysis)
                            
                            # Show gap detection results in a collapsible section
                            with st.expander(f"🔍 Gap Analysis - Found {len(gap_analysis.get('identified_gaps', []))} potential gaps"):
                                if gap_analysis.get('identified_gaps'):
                                    st.write("**Missing Prerequisites Detected:**")
                                    for gap in gap_analysis['identified_gaps']:
                                        st.write(f"• **{gap.get('type', 'Unknown')} Gap**: {gap.get('description', 'No description')}")
                                        if gap.get('suggested_milestones'):
                                            st.write(f"  *Suggested: {', '.join(gap['suggested_milestones'])}*")
                                
                                if gap_analysis.get('confidence_score'):
                                    st.write(f"**Confidence Score**: {gap_analysis['confidence_score']:.1f}/10")
                                
                                if gap_analysis.get('personalized_recommendations'):
                                    st.write("**Personalized Recommendations:**")
                                    for rec in gap_analysis['personalized_recommendations']:
                                        st.write(f"• {rec}")
                        
                        # AUTO-TRIGGER: Generate comprehensive analysis after 5+ exchanges
                        message_count = len([msg for msg in session["messages"] if msg.get("type") in ["answer", "question"]])
                        comprehensive_analysis_key = f"comprehensive_gap_analysis_{interview_key}"
                        
                        if (message_count >= 10 and message_count % 5 == 0 and 
                            comprehensive_analysis_key not in st.session_state):
                            
                            with st.spinner("🔄 Auto-generating comprehensive gap analysis..."):
                                try:
                                    comprehensive_analysis = agent.analyze_gap_patterns(
                                        session["messages"],
                                        goal_data['title'],
                                        existing_milestones=existing_milestones
                                    )
                                    st.session_state[comprehensive_analysis_key] = comprehensive_analysis
                                    
                                    # Show notification
                                    st.success("🎯 Comprehensive gap analysis generated! Check the report above.")
                                except Exception as e:
                                    print(f"Auto gap analysis failed: {e}")
                        
                    except Exception as e:
                        print(f"Gap detection failed: {e}")
                    
                    # Get current strategy based on voting
                    current_problematic = tracker.get_most_problematic_group(selected_person, selected_goal)
                    
                    if current_problematic:
                        strategy = current_problematic['focus_strategy']
                        
                        if strategy == 'problematic':
                            # Focus on fixing problematic milestones
                            problematic_milestones = current_problematic['problematic_milestones']
                            if problematic_milestones:
                                lowest_problematic = min(problematic_milestones, key=lambda m: m.get('score', 0))
                                enhanced_messages = session["messages"].copy()
                                enhanced_messages.append({
                                    "type": "context", 
                                    "content": f"STRATEGY: Fix problematic milestone '{lowest_problematic['name']}' (downvoted). Ask about issues, alternatives, or corrections needed for this milestone. EXISTING MILESTONES: {existing_milestones}.",
                                    "topic_idx": 0, 
                                    "summary": session["summary"]
                                })
                                next_question = agent.probe_within_topic(enhanced_messages)
                            else:
                                # Fallback for problematic strategy
                                enhanced_messages = session["messages"].copy()
                                enhanced_messages.append({
                                    "type": "context", 
                                    "content": f"STRATEGY: Fix problematic milestones. Focus on identifying issues and alternatives. EXISTING MILESTONES: {existing_milestones}.",
                                    "topic_idx": 0, 
                                    "summary": session["summary"]
                                })
                                next_question = agent.probe_within_topic(enhanced_messages)
                                
                        elif strategy == 'gaps':
                            # Focus on finding gaps around confirmed milestones
                            confirmed_milestones = current_problematic['confirmed_milestones']
                            if confirmed_milestones:
                                lowest_confirmed = min(confirmed_milestones, key=lambda m: m.get('score', 0))
                                enhanced_messages = session["messages"].copy()
                                enhanced_messages.append({
                                    "type": "context", 
                                    "content": f"STRATEGY: Find missing prerequisites around confirmed milestone '{lowest_confirmed['name']}' (upvoted). Ask what steps, requirements, or preparations were needed BEFORE this milestone. EXISTING MILESTONES: {existing_milestones}.",
                                    "topic_idx": 0, 
                                    "summary": session["summary"]
                                })
                                next_question = agent.probe_within_topic(enhanced_messages)
                            else:
                                # Fallback for gaps strategy
                                enhanced_messages = session["messages"].copy()
                                enhanced_messages.append({
                                    "type": "context", 
                                    "content": f"STRATEGY: Find gaps and missing prerequisites around confirmed milestones. Focus on what came before existing milestones. EXISTING MILESTONES: {existing_milestones}.",
                                    "topic_idx": 0, 
                                    "summary": session["summary"]
                                })
                                next_question = agent.probe_within_topic(enhanced_messages)
                                
                        else:
                            # General exploration strategy
                            group_milestones = current_problematic['group']['milestones']
                            if group_milestones:
                                lowest_milestone = min(group_milestones, key=lambda m: m.get('score', 0))
                                enhanced_messages = session["messages"].copy()
                                enhanced_messages.append({
                                    "type": "context", 
                                    "content": f"STRATEGY: General exploration around milestone '{lowest_milestone['name']}'. Ask about prerequisites, connections, or missing steps. EXISTING MILESTONES: {existing_milestones}.",
                                    "topic_idx": 0, 
                                    "summary": session["summary"]
                                })
                                next_question = agent.probe_within_topic(enhanced_messages)
                            else:
                                # Final fallback
                                enhanced_messages = session["messages"].copy()
                                enhanced_messages.append({
                                    "type": "context", 
                                    "content": f"STRATEGY: General exploration. Focus on finding NEW prerequisites, requirements, or missing steps. EXISTING MILESTONES: {existing_milestones}.",
                                    "topic_idx": 0, 
                                    "summary": session["summary"]
                                })
                                next_question = agent.probe_within_topic(enhanced_messages)
                    else:
                        # Fallback when no problematic group detected
                        enhanced_messages = session["messages"].copy()
                        enhanced_messages.append({
                            "type": "context", 
                            "content": f"EXISTING MILESTONES: {existing_milestones}. Focus on finding NEW prerequisites, requirements, or missing steps that aren't already listed.",
                            "topic_idx": 0, 
                            "summary": session["summary"]
                        })
                        next_question = agent.probe_within_topic(enhanced_messages)

                # === SAFETY AGENT: Moderate AI-generated questions ===
                try:
                    question_moderation = moderate_interview_input_groq(
                        text=next_question,
                        is_chatbot_question=True,  # This is AI's question
                        interview_topic=f"Career Development - {goal_data['title']}",
                        groq_api_key='groq_api_key',  # Replace with actual key or retrieval method
                        interview_stage="behavioral",
                        key_skills=["career planning", "goal setting", "milestone development"],
                        conversation_history=conversation_history,
                        moderator=st.session_state.safety_moderator
                    )
                    
                    st.session_state.moderation_stats['total_checks'] += 1
                    if not question_moderation['is_valid']:
                        st.session_state.moderation_stats['flagged_questions'] += 1
                        # If AI question is inappropriate, generate a safer alternative
                        next_question = f"Can you tell me more about the specific skills or prerequisites needed for {goal_data['title']}?"
                except Exception as e:
                    # If moderation fails, continue with original question
                    print(f"Question moderation failed: {e}")

                session["messages"].append({"type": "question", "content": next_question, "topic_idx": 0, "summary": session["summary"]})
                session["questions_asked"] = questions_asked_count + 1
                
                # Check if we should trigger automatic causality analysis
                check_and_trigger_causality_analysis(
                    selected_person, selected_goal, goal_data['title'], 
                    milestones, session["questions_asked"]
                )
                
                suggestion = parse_new_milestone_suggestion(next_question)
                if suggestion:
                    st.session_state[f"pending_milestone_{interview_key}"] = suggestion
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                session["messages"].append({"type": "question", "content": error_msg, "topic_idx": 0, "summary": session["summary"]})
        st.rerun()

    if pass_clicked:
        st.session_state[pass_count_key] += 1
        skip_count = st.session_state[pass_count_key]
        session["messages"].append({"type": "answer", "content": "[User chose to pass this question]", "topic_idx": 0, "summary": session["summary"]})
        
        # Visual feedback for skip pattern detection
        if skip_count == 1:
            st.markdown('<div class="skip-pattern-indicator skip-first">🔄 <strong>Skip Pattern Detected:</strong> Asking a different question about the same goal</div>', unsafe_allow_html=True)
        elif skip_count == 2:
            st.markdown('<div class="skip-pattern-indicator skip-multiple">🎯 <strong>Multiple Skips Detected:</strong> Switching focus to different milestone or contributing factors</div>', unsafe_allow_html=True)
        elif skip_count >= 3:
            st.markdown('<div class="skip-pattern-indicator skip-consistent">🌟 <strong>Consistent Skips Detected:</strong> Offering supportive alternatives and break options</div>', unsafe_allow_html=True)
        
        # AI: Skip Pattern Analysis - Different responses based on skip frequency
        if skip_count == 1:
            # AI: First Skip - Ask a completely different question about the same goal
            with st.spinner("Generating a different question about the same goal..."):
                try:
                    if questions_asked_count >= max_questions:
                        next_question = f"Thank you for sharing those details about **{goal_data['title']}**! I've gathered enough information about the prerequisites and missing steps. Click 'Show Summary' to see all the suggested milestones I found."
                    else:
                        # Generate strategy-aware skip question for first skip
                        existing_milestones = [ms['name'] for ms in milestones]
                        current_problematic = tracker.get_most_problematic_group(selected_person, selected_goal)
                        
                        if current_problematic:
                            strategy = current_problematic['focus_strategy']
                            
                            if strategy == 'problematic':
                                problematic_milestones = current_problematic['problematic_milestones']
                                if problematic_milestones:
                                    lowest_problematic = min(problematic_milestones, key=lambda m: m.get('score', 0))
                                    enhanced_messages = session["messages"].copy()
                                    enhanced_messages.append({
                                        "type": "context", 
                                        "content": f"USER SKIPPED - Ask a completely different question. STRATEGY: Fix problematic milestone '{lowest_problematic['name']}' (downvoted). Try a different angle about what's wrong with this milestone or what alternatives exist. EXISTING MILESTONES: {existing_milestones}.",
                                        "topic_idx": 0, 
                                        "summary": session["summary"]
                                    })
                                else:
                                    enhanced_messages = session["messages"].copy()
                                    enhanced_messages.append({
                                        "type": "context", 
                                        "content": f"USER SKIPPED - Ask a completely different question. STRATEGY: Fix problematic milestones. Try different angle about issues or alternatives. EXISTING MILESTONES: {existing_milestones}.",
                                        "topic_idx": 0, 
                                        "summary": session["summary"]
                                    })
                            elif strategy == 'gaps':
                                confirmed_milestones = current_problematic['confirmed_milestones']
                                if confirmed_milestones:
                                    lowest_confirmed = min(confirmed_milestones, key=lambda m: m.get('score', 0))
                                    enhanced_messages = session["messages"].copy()
                                    enhanced_messages.append({
                                        "type": "context", 
                                        "content": f"USER SKIPPED - Ask a completely different question. STRATEGY: Find gaps around confirmed milestone '{lowest_confirmed['name']}' (upvoted). Try different angle about prerequisites or what came before. EXISTING MILESTONES: {existing_milestones}.",
                                        "topic_idx": 0, 
                                        "summary": session["summary"]
                                    })
                                else:
                                    enhanced_messages = session["messages"].copy()
                                    enhanced_messages.append({
                                        "type": "context", 
                                        "content": f"USER SKIPPED - Ask a completely different question. STRATEGY: Find gaps around confirmed milestones. Try different angle about prerequisites. EXISTING MILESTONES: {existing_milestones}.",
                                        "topic_idx": 0, 
                                        "summary": session["summary"]
                                    })
                            else:
                                # General strategy
                                group_milestones = current_problematic['group']['milestones']
                                if group_milestones:
                                    lowest_milestone = min(group_milestones, key=lambda m: m.get('score', 0))
                                    enhanced_messages = session["messages"].copy()
                                    enhanced_messages.append({
                                        "type": "context", 
                                        "content": f"USER SKIPPED - Ask a completely different question. STRATEGY: General exploration around '{lowest_milestone['name']}'. Try different angle about connections or prerequisites. EXISTING MILESTONES: {existing_milestones}.",
                                        "topic_idx": 0, 
                                        "summary": session["summary"]
                                    })
                                else:
                                    enhanced_messages = session["messages"].copy()
                                    enhanced_messages.append({
                                        "type": "context", 
                                        "content": f"USER SKIPPED - Ask a completely different question about general exploration. EXISTING MILESTONES: {existing_milestones}.",
                                        "topic_idx": 0, 
                                        "summary": session["summary"]
                                    })
                        else:
                            # Fallback when no strategy detected
                            enhanced_messages = session["messages"].copy()
                            enhanced_messages.append({
                                "type": "context", 
                                "content": f"USER SKIPPED - Ask a completely different question. GOAL: {goal_data['title']}. EXISTING MILESTONES: {existing_milestones}. Ask a completely different question - not a reformatted version.",
                                "topic_idx": 0, 
                                "summary": session["summary"]
                            })
                        
                        next_question = agent.handle_skip_pattern(enhanced_messages, 'first_skip', milestones, goal_data['title'])
                        # Add helpful context
                        next_question += "\n\n *Let me try a different angle on the same topic.*"
                        
                    # === SAFETY AGENT: Moderate skip pattern questions ===
                    try:
                        question_moderation = moderate_interview_input_groq(
                            text=next_question,
                            is_chatbot_question=True,
                            interview_topic=f"Career Development - {goal_data['title']}",
                            groq_api_key='groq_api_key',  # Replace with actual key or retrieval method
                            interview_stage="behavioral",
                            key_skills=["career planning", "goal setting", "milestone development"],
                            conversation_history=create_enhanced_conversation_context(session["messages"], goal_data['title']),
                            moderator=st.session_state.safety_moderator
                        )
                        
                        st.session_state.moderation_stats['total_checks'] += 1
                        if not question_moderation['is_valid']:
                            st.session_state.moderation_stats['flagged_questions'] += 1
                            next_question = f"Let's try a different approach. What specific steps or skills were most important for achieving {goal_data['title']}?"
                    except Exception as e:
                        print(f"Skip pattern question moderation failed: {e}")
                        
                    session["messages"].append({"type": "question", "content": next_question, "topic_idx": 0, "summary": session["summary"]})
                    session["questions_asked"] = questions_asked_count + 1
                    
                    # Check if we should trigger automatic causality analysis
                    check_and_trigger_causality_analysis(
                        selected_person, selected_goal, goal_data['title'], 
                        milestones, session["questions_asked"]
                    )
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    session["messages"].append({"type": "question", "content": error_msg, "topic_idx": 0, "summary": session["summary"]})
                    
        elif skip_count == 2:
            # AI: Multiple Skips - Ask about different milestone or contributing factors
            with st.spinner("Switching focus to different aspects of your goal..."):
                try:
                    # Generate strategy-aware question for multiple skips
                    existing_milestones = [ms['name'] for ms in milestones]
                    current_problematic = tracker.get_most_problematic_group(selected_person, selected_goal)
                    
                    if current_problematic:
                        strategy = current_problematic['focus_strategy']
                        
                        if strategy == 'problematic':
                            # Switch to a different problematic milestone or suggest alternatives
                            problematic_milestones = current_problematic['problematic_milestones']
                            if problematic_milestones and len(problematic_milestones) > 1:
                                # Find a different problematic milestone
                                other_problematic = [m for m in problematic_milestones if m['name'] != session.get('last_focused_milestone')]
                                if other_problematic:
                                    different_problematic = min(other_problematic, key=lambda m: m.get('score', 0))
                                    enhanced_messages = session["messages"].copy()
                                    enhanced_messages.append({
                                        "type": "context", 
                                        "content": f"USER SKIPPED MULTIPLE - Switch to different problematic milestone '{different_problematic['name']}' (downvoted). Ask about issues with THIS milestone instead. EXISTING MILESTONES: {existing_milestones}.",
                                        "topic_idx": 0, 
                                        "summary": session["summary"]
                                    })
                                    ai_different_focus_question = agent.handle_skip_pattern(enhanced_messages, 'multiple_skips', milestones, goal_data['title'])
                                else:
                                    enhanced_messages = session["messages"].copy()
                                    enhanced_messages.append({
                                        "type": "context", 
                                        "content": f"USER SKIPPED MULTIPLE - Try completely different approach to problematic milestones. Ask about external factors, support systems, or resources that could help fix them. EXISTING MILESTONES: {existing_milestones}.",
                                        "topic_idx": 0, 
                                        "summary": session["summary"]
                                    })
                                    ai_different_focus_question = agent.handle_skip_pattern(enhanced_messages, 'multiple_skips', milestones, goal_data['title'])
                            else:
                                enhanced_messages = session["messages"].copy()
                                enhanced_messages.append({
                                    "type": "context", 
                                    "content": f"USER SKIPPED MULTIPLE - Switch approach from fixing problems to finding external factors, support, or resources. EXISTING MILESTONES: {existing_milestones}.",
                                    "topic_idx": 0, 
                                    "summary": session["summary"]
                                })
                                ai_different_focus_question = agent.handle_skip_pattern(enhanced_messages, 'multiple_skips', milestones, goal_data['title'])
                                
                        elif strategy == 'gaps':
                            # Switch to a different confirmed milestone or ask about external factors
                            confirmed_milestones = current_problematic['confirmed_milestones']
                            if confirmed_milestones and len(confirmed_milestones) > 1:
                                # Find a different confirmed milestone
                                other_confirmed = [m for m in confirmed_milestones if m['name'] != session.get('last_focused_milestone')]
                                if other_confirmed:
                                    different_confirmed = min(other_confirmed, key=lambda m: m.get('score', 0))
                                    enhanced_messages = session["messages"].copy()
                                    enhanced_messages.append({
                                        "type": "context", 
                                        "content": f"USER SKIPPED MULTIPLE - Switch to finding gaps around different confirmed milestone '{different_confirmed['name']}' (upvoted). Ask about prerequisites for THIS milestone instead. EXISTING MILESTONES: {existing_milestones}.",
                                        "topic_idx": 0, 
                                        "summary": session["summary"]
                                    })
                                    ai_different_focus_question = agent.handle_skip_pattern(enhanced_messages, 'multiple_skips', milestones, goal_data['title'])
                                else:
                                    enhanced_messages = session["messages"].copy()
                                    enhanced_messages.append({
                                        "type": "context", 
                                        "content": f"USER SKIPPED MULTIPLE - Switch from prerequisites to external factors, timing, or resources that enabled confirmed milestones. EXISTING MILESTONES: {existing_milestones}.",
                                        "topic_idx": 0, 
                                        "summary": session["summary"]
                                    })
                                    ai_different_focus_question = agent.handle_skip_pattern(enhanced_messages, 'multiple_skips', milestones, goal_data['title'])
                            else:
                                enhanced_messages = session["messages"].copy()
                                enhanced_messages.append({
                                    "type": "context", 
                                    "content": f"USER SKIPPED MULTIPLE - Switch approach from finding gaps to exploring external factors, support systems, or timing. EXISTING MILESTONES: {existing_milestones}.",
                                    "topic_idx": 0, 
                                    "summary": session["summary"]
                                })
                                ai_different_focus_question = agent.handle_skip_pattern(enhanced_messages, 'multiple_skips', milestones, goal_data['title'])
                        else:
                            # General strategy - try different milestone or external factors
                            group_milestones = current_problematic['group']['milestones']
                            if group_milestones and len(group_milestones) > 1:
                                other_milestones = [m for m in group_milestones if m['name'] != session.get('last_focused_milestone')]
                                if other_milestones:
                                    different_milestone = min(other_milestones, key=lambda m: m.get('score', 0))
                                    enhanced_messages = session["messages"].copy()
                                    enhanced_messages.append({
                                        "type": "context", 
                                        "content": f"USER SKIPPED MULTIPLE - Switch focus to different milestone '{different_milestone['name']}'. Ask about its prerequisites or connections. EXISTING MILESTONES: {existing_milestones}.",
                                        "topic_idx": 0, 
                                        "summary": session["summary"]
                                    })
                                    ai_different_focus_question = agent.handle_skip_pattern(enhanced_messages, 'multiple_skips', milestones, goal_data['title'])
                                else:
                                    enhanced_messages = session["messages"].copy()
                                    enhanced_messages.append({
                                        "type": "context", 
                                        "content": f"USER SKIPPED MULTIPLE - Switch to external factors, support systems, or resources. EXISTING MILESTONES: {existing_milestones}.",
                                        "topic_idx": 0, 
                                        "summary": session["summary"]
                                    })
                                    ai_different_focus_question = agent.handle_skip_pattern(enhanced_messages, 'multiple_skips', milestones, goal_data['title'])
                            else:
                                enhanced_messages = session["messages"].copy()
                                enhanced_messages.append({
                                    "type": "context", 
                                    "content": f"USER SKIPPED MULTIPLE - Ask about external factors, support, or resources instead of milestones. EXISTING MILESTONES: {existing_milestones}.",
                                    "topic_idx": 0, 
                                    "summary": session["summary"]
                                })
                                ai_different_focus_question = agent.handle_skip_pattern(enhanced_messages, 'multiple_skips', milestones, goal_data['title'])
                    else:
                        # Fallback when no strategy detected
                        enhanced_messages = session["messages"].copy()
                        enhanced_messages.append({
                            "type": "context", 
                            "content": f"USER SKIPPED MULTIPLE - Ask about different milestone or contributing factors. GOAL: {goal_data['title']}. EXISTING MILESTONES: {existing_milestones}.",
                            "topic_idx": 0, 
                            "summary": session["summary"]
                        })
                        ai_different_focus_question = agent.handle_skip_pattern(enhanced_messages, 'multiple_skips', milestones, goal_data['title'])
                    
                    # Enhance with structured options for different perspectives
                    different_focus_question = f"""{ai_different_focus_question}

🔍 **Or consider these contributing factors:**
- 🎯 **Different Milestone**: Pick any existing milestone to discuss its prerequisites
- ⚡ **External Factors**: What circumstances made this goal possible?
- 👥 **Support System**: Who helped you or provided guidance? 
- 🛠️ **Tools & Resources**: What specific resources were crucial?
- ⏰ **Timing**: What made this the right time to pursue this goal?
- 🎲 **Unexpected Elements**: Any surprises or lucky breaks along the way?

*Feel free to share about any of these aspects that feel relevant to your journey.*
                    """
                    
                    # === SAFETY AGENT: Moderate multiple skip questions ===
                    try:
                        question_moderation = moderate_interview_input_groq(
                            text=different_focus_question,
                            is_chatbot_question=True,
                            interview_topic=f"Career Development - {goal_data['title']}",
                            groq_api_key='groq_api_key',  # Replace with actual key or retrieval method
                            interview_stage="behavioral",
                            key_skills=["career planning", "goal setting", "milestone development"],
                            conversation_history=create_enhanced_conversation_context(session["messages"], goal_data['title']),
                            moderator=st.session_state.safety_moderator
                        )
                        
                        st.session_state.moderation_stats['total_checks'] += 1
                        if not question_moderation['is_valid']:
                            st.session_state.moderation_stats['flagged_questions'] += 1
                            different_focus_question = f"Let's explore different aspects of {goal_data['title']}. What resources, people, or circumstances were most helpful in your journey?"
                    except Exception as e:
                        print(f"Multiple skip question moderation failed: {e}")
                    
                    session["messages"].append({"type": "question", "content": different_focus_question, "topic_idx": 0, "summary": session["summary"]})
                    session["questions_asked"] = questions_asked_count + 1
                    
                    # Check if we should trigger automatic causality analysis
                    check_and_trigger_causality_analysis(
                        selected_person, selected_goal, goal_data['title'], 
                        milestones, session["questions_asked"]
                    )
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    session["messages"].append({"type": "question", "content": error_msg, "topic_idx": 0, "summary": session["summary"]})
                    
        elif skip_count >= 3:
            # AI: Consistent Skips - Suggest Break & Different Approach
            with st.spinner("Generating supportive response..."):
                try:
                    # Use agent's skip pattern handling for empathetic response
                    enhanced_messages = session["messages"].copy()
                    enhanced_messages.append({
                        "type": "context", 
                        "content": f"GOAL: {goal_data['title']}. User has consistently skipped questions. Provide empathetic break suggestions and alternative approaches.",
                        "topic_idx": 0, 
                        "summary": session["summary"]
                    })
                    ai_break_response = agent.handle_skip_pattern(enhanced_messages, 'consistent_skips', milestones, goal_data['title'])
                    
                    # Enhance with structured break options
                    break_suggestion = f"""{ai_break_response}

🌟 **Here are some supportive options:**

🔄 **Take a Break**: Sometimes stepping away helps clarify thoughts
📝 **Summary Mode**: I can work with what we've discussed so far  
🎯 **Focus Shift**: We could switch to a different goal that feels more natural
💭 **Reflection Time**: Maybe you need more time to think about this goal

**What would work best for you?** I'm here to support your career journey in whatever way feels most comfortable.

*Click 'Show Summary' to see what we've gathered so far, or let me know if you'd like to try a different approach.*
                    """
                    session["messages"].append({
                        "type": "question",
                        "content": break_suggestion,
                        "topic_idx": 0,
                        "summary": session["summary"]
                    })
                    session["questions_asked"] = max_questions  # End the interview gracefully
                    st.session_state[pass_count_key] = 0  # Reset for next session
                except Exception as e:
                    # Fallback to basic empathetic message
                    break_suggestion = f"""
🌟 **I notice you've skipped several questions - that's totally okay!** 

Maybe we need a different approach for **{goal_data['title']}**. 

**What would work best for you?** I'm here to support your career journey in whatever way feels most comfortable.

*Click 'Show Summary' to see what we've gathered so far.*
                    """
                    session["messages"].append({
                        "type": "question",
                        "content": break_suggestion,
                        "topic_idx": 0,
                        "summary": session["summary"]
                    })
                    session["questions_asked"] = max_questions
                    st.session_state[pass_count_key] = 0
        
        st.rerun()

    pending_key = f"pending_milestone_{interview_key}"
    if pending_key in st.session_state:
        suggestion = st.session_state[pending_key]
        
        # Enhanced milestone suggestion UI
        st.markdown("---")
        st.markdown("### 🎯 **AI Detected a New Milestone!**")
        st.info(f"**The AI detected:** '{suggestion['name']}' as a key step that enabled your achievement.")
        
        with st.form(key=f"add_milestone_form_{interview_key}", clear_on_submit=True):
            st.markdown("**📝 Milestone Details:**")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Milestone Name", value=suggestion["name"], help="The name of the milestone/achievement")
            with col2:
                score = st.slider("Importance Score", 1, 10, 5, help="How important was this step?")
            
            st.markdown("**🔗 Causal Connection:**")
            st.markdown(f"*This milestone will be connected as a prerequisite to the goal or existing milestones*")
            
            # Get all milestones for this goal
            milestones = tracker.get_ordered_milestones_for_goal(selected_person, selected_goal)
            milestone_options = {ms['id']: ms['name'] for ms in milestones}
            
            # Add the goal itself as an option
            goal_data = tracker.get_goals(selected_person)[selected_goal]
            milestone_options[selected_goal] = f"GOAL: {goal_data['title']}"
            
            connect_to = st.selectbox(
                "Connect this milestone to (what it enables):", 
                list(milestone_options.keys()), 
                format_func=lambda x: milestone_options[x],
                help="Select which milestone or goal this new step directly enabled"
            )
            
            st.markdown("**💡 This creates a causal link:** New Milestone → Selected Target")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("✅ Add Milestone", use_container_width=True, type="primary")
            with col2:
                if st.form_submit_button("❌ Skip", use_container_width=True):
                    del st.session_state[pending_key]
                    st.rerun()
            
            if submitted:
                # Check if milestone with similar name already exists
                existing_milestones = tracker.get_ordered_milestones_for_goal(selected_person, selected_goal)
                milestone_exists = any(
                    existing_ms['name'].lower().strip() == name.lower().strip() 
                    for existing_ms in existing_milestones
                )
                
                if milestone_exists:
                    st.error(f"⚠️ A milestone with similar name already exists: '{name}'")
                    st.info("💡 Please modify the name or skip this suggestion.")
                else:
                    # Use the new function to create the correct causal link
                    success = tracker.insert_causal_milestone(
                        person=selected_person, 
                        goal_id=selected_goal, 
                        new_milestone_name=name, 
                        new_milestone_score=score, 
                        enabled_milestone_id=connect_to
                    )
                    if success:
                        st.success(f"🎉 **Causal Link Added!** '{name}' is now shown as a prerequisite for '{milestone_options[connect_to]}'")
                        st.balloons()
                        del st.session_state[pending_key]
                        st.rerun()
                    else:
                        st.error("❌ Failed to add causal link. Please check the logs.")

    # Show interview controls
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🔄 Reset Discussion", use_container_width=True):
            del st.session_state[interview_key]
            st.rerun()

    with col2:
        # NEW: Enhanced summary generation focusing on prerequisites and missing milestones
        summary_button_label = "📊 Show Summary" if not session.get("show_summary_ui") else "🙈 Hide Summary"
        if st.button(summary_button_label, use_container_width=True):
            # If we are about to show it, generate the summary now
            if not session.get("show_summary_ui"):
                with st.spinner("Analyzing conversation for missing prerequisites..."):
                    conversation_text = "\n".join([f"{msg['type']}: {msg['content']}" for msg in session["messages"]])
                    existing_milestones = [ms['name'] for ms in milestones]
                    
                    # Check if conversation has meaningful content
                    if not conversation_text.strip() or len(session["messages"]) < 2:
                        st.warning("⚠️ Not enough conversation data. Please answer a few questions first before generating summary.")
                        session["summary_suggestions"] = []
                    else:
                        analysis_prompt = f"""Based on this conversation about the goal "{goal_data['title']}", identify specific missing prerequisites and their logical connections.

                        EXISTING MILESTONES (do not suggest these): {existing_milestones}
                        
                        Conversation: {conversation_text}
                        
                        Extract 5-8 NEW, specific, actionable prerequisites or steps. For each new milestone, specify what it should connect to:
                        - Connect to existing milestones when it directly enables them
                        - Connect to other NEW milestones when there's a logical prerequisite sequence
                        - Create realistic prerequisite chains (e.g., Step A enables Step B, Step B enables existing milestone)
                        
                        Format response as: 
                        1. [New Milestone Name] → connects to [existing milestone name OR other new milestone name]
                        2. [New Milestone Name] → connects to [existing milestone name OR other new milestone name]
                        etc.
                        
                        EXAMPLE for "Get Bachelor's Degree" goal:
                        1. Research university requirements → connects to Submit applications
                        2. Gather recommendation letters → connects to Submit applications  
                        3. Submit applications → connects to Apply to University
                        4. Take preparatory math course → connects to Pass entrance exam
                        
                        Notice: Steps 1&2 both connect to step 3 (new-to-new), and step 3 connects to existing milestone.
                        Focus on creating logical prerequisite flows, not just isolated connections.
                        
                        IMPORTANT: Always provide at least 3 suggestions even if conversation is brief."""
                        
                        try:
                            analysis_response = agent.client.chat.completions.create(
                                model="gpt-4-turbo", 
                                messages=[{"role": "user", "content": analysis_prompt}], 
                                max_tokens=600  # Increased for more suggestions
                            )
                            analysis = analysis_response.choices[0].message.content
                            
                            # Parse the response to extract milestone suggestions with connections  
                            suggestions = []
                            suggested_milestone_names = []  # Track names of suggested milestones
                            
                            # Enhanced parsing with multiple patterns
                            lines = analysis.split('\n')
                            for line in lines:
                                line = line.strip()
                                if not line:
                                    continue
                                    
                                # Try different parsing patterns
                                patterns = [
                                    r'(\d+\.?\s*)(.*?)\s*→\s*connects to\s*(.*)',
                                    r'(\d+\.?\s*)(.*?)\s*->\s*connects to\s*(.*)',
                                    r'(\d+\.?\s*)(.*?)\s*→\s*(.*)',
                                    r'(\d+\.?\s*)(.*?)\s*->\s*(.*)',
                                    r'(\d+\.?\s*)(.*?)\s*connects to\s*(.*)'
                                ]
                                
                                parsed = False
                                for pattern in patterns:
                                    match = re.match(pattern, line, re.IGNORECASE)
                                    if match:
                                        milestone_name = match.group(2).strip()
                                        connect_part = match.group(3).strip()
                                        
                                        if milestone_name and connect_part:
                                            suggestions.append({
                                                'name': milestone_name,
                                                'connects_to': connect_part
                                            })
                                            suggested_milestone_names.append(milestone_name)
                                            parsed = True
                                            break
                                
                                # If no pattern matched but line has content, try to extract anyway
                                if not parsed and any(keyword in line.lower() for keyword in ['learn', 'get', 'obtain', 'complete', 'finish', 'start', 'begin', 'research', 'study', 'practice']):
                                    # Extract potential milestone name
                                    clean_line = re.sub(r'^\d+\.?\s*', '', line).strip()
                                    if clean_line and len(clean_line) > 5:  # Reasonable length
                                        suggestions.append({
                                            'name': clean_line,
                                            'connects_to': 'Goal'  # Default connection
                                        })
                                        suggested_milestone_names.append(clean_line)
                            
                            # Enhance suggestions with new milestone awareness
                            for suggestion in suggestions:
                                # Check if connects_to refers to another suggested milestone
                                connects_to_lower = suggestion['connects_to'].lower()
                                for suggested_name in suggested_milestone_names:
                                    if suggested_name.lower() in connects_to_lower or connects_to_lower in suggested_name.lower():
                                        suggestion['connects_to_new_milestone'] = suggested_name
                                        break
                            
                            # Fallback: if no suggestions were parsed, create some basic ones
                            if not suggestions:
                                fallback_suggestions = [
                                    {'name': f'Research requirements for {goal_data["title"]}', 'connects_to': 'Goal', 'used': False},
                                    {'name': f'Gather resources for {goal_data["title"]}', 'connects_to': 'Goal', 'used': False},
                                    {'name': f'Create plan for {goal_data["title"]}', 'connects_to': 'Goal', 'used': False}
                                ]
                                suggestions = fallback_suggestions
                                st.info("ℹ️ Used fallback suggestions due to parsing issues.")
                            else:
                                # Ensure all suggestions have the used flag
                                for suggestion in suggestions:
                                    if 'used' not in suggestion:
                                        suggestion['used'] = False
                            
                            session["summary_suggestions"] = suggestions
                            
                        except Exception as e:
                            st.error(f"Failed to generate summary: {e}")
                            # Provide fallback suggestions
                            fallback_suggestions = [
                                {'name': f'Research requirements for {goal_data["title"]}', 'connects_to': 'Goal', 'used': False},
                                {'name': f'Gather necessary resources', 'connects_to': 'Goal', 'used': False},
                                {'name': f'Create detailed action plan', 'connects_to': 'Goal', 'used': False},
                                {'name': f'Set up learning environment', 'connects_to': 'Goal', 'used': False}
                            ]
                            session["summary_suggestions"] = fallback_suggestions
                            st.info("ℹ️ Used fallback suggestions due to API error.")
                
                # NEW: Trigger Enhanced Causality Analysis when showing summary
                causality_key = f"causality_analysis_{selected_person}_{selected_goal}"
                if causality_key not in st.session_state.causality_analysis_results:
                    try:
                        # Run comprehensive causality analysis
                        analysis_results = st.session_state.causality_agent.run_comprehensive_analysis(
                            milestones=milestones,
                            goal_title=goal_data['title'],
                            person_name=selected_person,
                            analysis_types=['cofounders', 'counterfactuals', 'interventions']
                        )
                        st.session_state.causality_analysis_results[causality_key] = analysis_results
                    except Exception as e:
                        st.error(f"Causality analysis failed: {e}")
                        st.session_state.causality_analysis_results[causality_key] = None
                        
            # Toggle the flag and rerun
            session["show_summary_ui"] = not session.get("show_summary_ui", False)
            st.rerun()

    with col3:
        # NEW: Causality Analysis Button
        causality_button_label = "🔍 Causal Analysis" if not st.session_state.get("show_causality_ui") else "🙈 Hide Analysis"
        if st.button(causality_button_label, use_container_width=True):
            st.session_state.show_causality_ui = not st.session_state.get("show_causality_ui", False)
            
            # Trigger causality analysis if not already done
            causality_key = f"causality_analysis_{selected_person}_{selected_goal}"
            if st.session_state.show_causality_ui and causality_key not in st.session_state.causality_analysis_results:
                try:
                    with st.spinner("Running Enhanced Causality Analysis..."):
                        analysis_results = st.session_state.causality_agent.run_comprehensive_analysis(
                            milestones=milestones,
                            goal_title=goal_data['title'],
                            person_name=selected_person,
                            analysis_types=['cofounders', 'counterfactuals', 'interventions']
                        )
                        st.session_state.causality_analysis_results[causality_key] = analysis_results
                except Exception as e:
                    st.error(f"Causality analysis failed: {e}")
                    st.session_state.causality_analysis_results[causality_key] = None
            st.rerun()

    with col4:
        # Reset the questions counter if needed
        if st.button("🔄 Continue Questions", use_container_width=True):
            session["questions_asked"] = 0
            session["max_questions"] = max_questions + 3  # Allow 3 more questions
            st.rerun()

    # NEW: Enhanced summary UI with pagination and connection management
    if session.get("show_summary_ui") and session.get("summary_suggestions"):
        st.markdown("---")
        st.info("**📋 Missing Prerequisites & Connections Found**")
        st.write(f"Based on your discussion about **{goal_data['title']}**, here are missing prerequisites and their suggested connections:")
        
        # Summary statistics and controls
        added_milestones_key = f"added_milestones_{interview_key}"
        if added_milestones_key not in st.session_state:
            st.session_state[added_milestones_key] = set()
        
        # Pagination setup
        pagination_key = f"suggestions_page_size_{interview_key}"
        if pagination_key not in st.session_state:
            st.session_state[pagination_key] = 5  # Show 5 by default
        
        total_suggestions = len(session["summary_suggestions"])
        current_page_size = st.session_state[pagination_key]
        added_count = len(st.session_state[added_milestones_key])
        remaining_count = total_suggestions - added_count
        
        col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)
        with col_stat1:
            st.metric("Total Found", total_suggestions)
        with col_stat2:
            st.metric("Currently Showing", min(current_page_size, total_suggestions))
        with col_stat3:
            st.metric("Added", added_count)
        with col_stat4:
            st.metric("Remaining", remaining_count)
        with col_stat5:
            # Extend more button
            if current_page_size < total_suggestions:
                if st.button(f"📈 Show More (+{min(5, total_suggestions - current_page_size)})", use_container_width=True):
                    st.session_state[pagination_key] = min(current_page_size + 5, total_suggestions)
                    st.rerun()
            elif total_suggestions > 5:
                if st.button("📉 Show Less", use_container_width=True):
                    st.session_state[pagination_key] = 5
                    st.rerun()
        
        # Reset options row
        col_reset1, col_reset2 = st.columns(2)
        with col_reset1:
            reset_option = st.selectbox(
                "Reset Options:", 
                ["Reset Status", "Reset & Remove", "Clear All"],
                help="Reset Status: Clear tracking only | Reset & Remove: Remove newly added milestones | Clear All: Remove all interview milestones"
            )
        with col_reset2:
            if st.button("🔄 Execute Reset", help=f"Execute: {reset_option}", use_container_width=True):
                if reset_option == "Reset Status":
                    # Current behavior: just clear tracking
                    st.session_state[added_milestones_key] = set()
                    st.success("✅ Status reset! You can add suggestions again.")
                
                elif reset_option == "Reset & Remove":
                    # Enhanced: Remove milestones that were added AND clear tracking
                    interview_milestones_key = f"interview_milestones_{interview_key}"
                    if interview_milestones_key in st.session_state:
                        milestones_to_remove = st.session_state[interview_milestones_key]
                        removed_count = 0
                        
                        for milestone_id in milestones_to_remove.copy():
                            if tracker.remove_milestone(selected_person, selected_goal, milestone_id):
                                removed_count += 1
                                milestones_to_remove.discard(milestone_id)
                        
                        st.session_state[added_milestones_key] = set()
                        st.success(f"✅ Removed {removed_count} milestones and reset status!")
                    else:
                        st.session_state[added_milestones_key] = set()
                        st.info("✅ No interview milestones to remove. Status reset.")
                
                elif reset_option == "Clear All":
                    # Nuclear option: remove ALL milestones added during ANY interview session
                    all_interview_keys = [key for key in st.session_state.keys() if key.startswith("interview_milestones_")]
                    total_removed = 0
                    
                    for key in all_interview_keys:
                        milestones_to_remove = st.session_state[key]
                        for milestone_id in milestones_to_remove.copy():
                            if tracker.remove_milestone(selected_person, selected_goal, milestone_id):
                                total_removed += 1
                        del st.session_state[key]
                    
                    # Clear all tracking
                    tracking_keys = [key for key in st.session_state.keys() if "added_milestones_" in key]
                    for key in tracking_keys:
                        st.session_state[key] = set()
                    
                    st.success(f"✅ Cleared all! Removed {total_removed} interview milestones.")
                
                st.rerun()

        # Display suggestions with pagination - filter out used suggestions
        active_suggestions = [s for s in session["summary_suggestions"] if not s.get('used', False)]
        total_active = len(active_suggestions)
        suggestions_to_show = active_suggestions[:current_page_size]
        
        # Update metrics to reflect active suggestions
        col_stat1.metric("Total Available", total_active)
        col_stat2.metric("Currently Showing", len(suggestions_to_show))
        
        # Update show more/less buttons
        if current_page_size < total_active:
            with col_stat5:
                if st.button(f"📈 Show More (+{min(5, total_active - current_page_size)})", use_container_width=True, key=f"show_more_active_{interview_key}"):
                    st.session_state[pagination_key] = min(current_page_size + 5, total_active)
                    st.rerun()
        elif total_active > 5:
            with col_stat5:
                if st.button("📉 Show Less", use_container_width=True, key=f"show_less_active_{interview_key}"):
                    st.session_state[pagination_key] = 5
                    st.rerun()
        
        if not suggestions_to_show:
            st.info("🎉 All suggestions have been processed! Generate more by continuing the conversation and clicking 'Show Summary' again.")
            return
        
        for display_index, suggestion in enumerate(suggestions_to_show):
            # Find the original index in the full suggestions list
            original_index = session["summary_suggestions"].index(suggestion)
            
            st.markdown(f"### {display_index+1}. `{suggestion['name']}`")
            col1, col2, col3, col4 = st.columns([0.35, 0.25, 0.2, 0.2])
            with col1:
                st.markdown(f"**Suggested connection:** {suggestion['connects_to']}")
            with col2:
                milestones = tracker.get_ordered_milestones_for_goal(selected_person, selected_goal)
                connection_options = {ms['id']: ms['name'] for ms in milestones}
                connection_options[selected_goal] = f"GOAL: {goal_data['title']}"
                suggested_milestones = session.get("summary_suggestions", [])
                for idx, sugg in enumerate(suggested_milestones):
                    if sugg['name'] != suggestion['name'] and not sugg.get('used', False):
                        suggestion_key = f"NEW_{idx}_{sugg['name']}"
                        connection_options[suggestion_key] = f"NEW: {sugg['name']}"
                current_connection = selected_goal
                if suggestion.get('connects_to_new_milestone'):
                    for opt_id, opt_name in connection_options.items():
                        if suggestion['connects_to_new_milestone'].lower() in opt_name.lower():
                            current_connection = opt_id
                            break
                else:
                    for opt_id, opt_name in connection_options.items():
                        if suggestion['connects_to'].lower() in opt_name.lower() or opt_name.lower() in suggestion['connects_to'].lower():
                            current_connection = opt_id
                            break
                new_connection = st.selectbox(
                    "Connect to:",
                    list(connection_options.keys()),
                    format_func=lambda x: connection_options[x],
                    index=list(connection_options.keys()).index(current_connection) if current_connection in connection_options else 0,
                    key=f"connection_{original_index}_{interview_key}",
                    help="Select what this milestone enables. NEW milestones will be added in dependency order."
                )
            with col3:
                milestone_score = st.slider(
                    "Importance",
                    min_value=1,
                    max_value=10,
                    value=5,
                    key=f"score_{original_index}_{interview_key}",
                    help="How important is this milestone?"
                )
            with col4:
                added_milestones_key = f"added_milestones_{interview_key}"
                if added_milestones_key not in st.session_state:
                    st.session_state[added_milestones_key] = set()
                milestone_id = f"{suggestion['name']}_{new_connection}"
                already_added = milestone_id in st.session_state[added_milestones_key]
                if already_added:
                    st.button("✅ Added", key=f"summary_added_{original_index}_{interview_key}", 
                            use_container_width=True, disabled=True, 
                            help="This milestone has already been added")
                else:
                    if st.button("➕ Add", key=f"summary_add_{original_index}_{interview_key}", use_container_width=True):
                        # DEBUG: Show what connection is actually being used
                        st.write(f"DEBUG: Connecting '{suggestion['name']}' to '{connection_options[new_connection]}'")
                        st.write(f"DEBUG: new_connection value = '{new_connection}'")
                        
                        existing_milestones = tracker.get_ordered_milestones_for_goal(selected_person, selected_goal)
                        milestone_exists = any(
                            existing_ms['name'].lower().strip() == suggestion['name'].lower().strip() 
                            for existing_ms in existing_milestones
                        )
                        if milestone_exists:
                            st.error(f"⚠️ A milestone with similar name already exists: '{suggestion['name']}'")
                        else:
                            if new_connection.startswith("NEW_"):
                                pending_connections_key = f"pending_connections_{interview_key}"
                                if pending_connections_key not in st.session_state:
                                    st.session_state[pending_connections_key] = {}
                                target_milestone_name = new_connection.split("_", 2)[-1]
                                st.session_state[pending_connections_key][suggestion['name']] = {
                                    'target_name': target_milestone_name,
                                    'score': milestone_score
                                }
                                # For NEW connections, temporarily connect to goal until target exists
                                success = tracker.insert_causal_milestone(
                                    person=selected_person,
                                    goal_id=selected_goal,
                                    new_milestone_name=suggestion['name'],
                                    new_milestone_score=milestone_score,
                                    enabled_milestone_id=selected_goal  # Temporarily connect to goal
                                )
                                if success:
                                    st.toast(f"✅ Added: {suggestion['name']} (Score: {milestone_score}) - will connect to '{target_milestone_name}' when available", icon="🔗")
                                else:
                                    st.error(f"❌ Failed to add milestone: {suggestion['name']}")
                            else:
                                success = tracker.insert_causal_milestone(
                                    person=selected_person,
                                    goal_id=selected_goal,
                                    new_milestone_name=suggestion['name'],
                                    new_milestone_score=milestone_score,
                                    enabled_milestone_id=new_connection
                                )
                                if success:
                                    st.toast(f"✅ Added: {suggestion['name']} (Score: {milestone_score})", icon="🎉")
                                else:
                                    st.error(f"❌ Failed to add milestone: {suggestion['name']}")
                            if success:
                                st.session_state[added_milestones_key].add(milestone_id)
                                interview_milestones_key = f"interview_milestones_{interview_key}"
                                if interview_milestones_key not in st.session_state:
                                    st.session_state[interview_milestones_key] = set()
                                current_milestones = tracker.get_ordered_milestones_for_goal(selected_person, selected_goal)
                                new_milestone_id = None
                                for ms in current_milestones:
                                    if ms['name'] == suggestion['name'] and ms.get('is_causal', False):
                                        new_milestone_id = ms['id']
                                        break
                                if new_milestone_id:
                                    st.session_state[interview_milestones_key].add(new_milestone_id)
                                pending_connections_key = f"pending_connections_{interview_key}"
                                if pending_connections_key in st.session_state:
                                    pending_connections = st.session_state[pending_connections_key]
                                    resolved_connections = []
                                    for pending_name, connection_info in pending_connections.items():
                                        if connection_info['target_name'] == suggestion['name']:
                                            for ms in current_milestones:
                                                if ms['name'] == pending_name and ms.get('is_causal', False):
                                                    success_update = tracker._update_milestone_connection(
                                                        selected_person, selected_goal, ms['id'], new_milestone_id
                                                    )
                                                    if success_update:
                                                        resolved_connections.append(pending_name)
                                                        st.toast(f"🔗 Connected: {pending_name} → {suggestion['name']}", icon="🔗")
                                                    break
                                    for resolved in resolved_connections:
                                        if resolved in pending_connections:
                                            del pending_connections[resolved]
                                # --- Mark suggestion as used instead of removing it ---
                                # This preserves indices and pagination
                                session["summary_suggestions"][original_index]['used'] = True
                                
                                # AI-generate a new suggestion and append it if we need more
                                if len([s for s in session["summary_suggestions"] if not s.get('used', False)]) < 3:
                                    try:
                                        conversation_text = "\n".join([f"{msg['type']}: {msg['content']}" for msg in session["messages"]])
                                        existing_milestones = [ms['name'] for ms in tracker.get_ordered_milestones_for_goal(selected_person, selected_goal)]
                                        analysis_prompt = f"""Based on this conversation about the goal \"{goal_data['title']}\", identify a new specific missing prerequisite and its logical connection.\n\nEXISTING MILESTONES (do not suggest these): {existing_milestones}\n\nConversation: {conversation_text}\n\nExtract ONE NEW, specific, actionable prerequisite or step. For the new milestone, specify what it should connect to (existing milestone or goal).\nFormat response as: [New Milestone Name] → connects to [existing milestone name OR goal]\nIf no more suggestions, reply with 'NO_SUGGESTION'."""
                                        analysis_response = agent.client.chat.completions.create(
                                            model="gpt-4-turbo",
                                            messages=[{"role": "user", "content": analysis_prompt}],
                                            max_tokens=200
                                        )
                                        analysis = analysis_response.choices[0].message.content.strip()
                                        if analysis and 'NO_SUGGESTION' not in analysis:
                                            # Parse the response for a new suggestion
                                            if '→ connects to' in analysis:
                                                parts = analysis.split('→ connects to')
                                                if len(parts) == 2:
                                                    milestone_name = parts[0].strip().lstrip('1234567890. ').strip()
                                                    connects_to = parts[1].strip()
                                                    session["summary_suggestions"].append({
                                                        'name': milestone_name,
                                                        'connects_to': connects_to,
                                                        'used': False
                                                    })
                                    except Exception as e:
                                        st.info(f"No more AI suggestions available: {e}")
                                st.rerun()

    if st.session_state.get("show_causality_ui"):
        causality_key = f"causality_analysis_{selected_person}_{selected_goal}"
        if causality_key in st.session_state.causality_analysis_results:
            analysis_results = st.session_state.causality_analysis_results[causality_key]
            
            if analysis_results:
                st.markdown("---")
                st.markdown("### 🔍 **Causality Analysis**")
                st.info(f"Advanced causal analysis for **{goal_data['title']}** - Revealing hidden patterns and opportunities")
                
                # Create tabs for different analysis types
                analysis_tabs = st.tabs(["🤝 Cofounders", "🔄 Counterfactuals", "⚡ Interventions"])
                
                # Cofounders Analysis Tab
                with analysis_tabs[0]:
                    if 'cofounder_analysis' in analysis_results:
                        cofounder_data = analysis_results['cofounder_analysis']
                        
                        if cofounder_data.get('cofounder_suggestions'):
                            st.markdown("#### 🤝 Potential Cofounders & Collaborators")
                            st.write("Based on your causal network, here are collaboration opportunities that could strengthen your journey:")
                            
                            for i, suggestion in enumerate(cofounder_data['cofounder_suggestions']):
                                with st.expander(f"**{suggestion.get('cofounder_type', 'Collaborator')}** - {suggestion.get('cofounder_description', 'N/A')[:50]}..."):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.write("**Target Milestones:**")
                                        target_milestones = suggestion.get('target_milestones', [])
                                        for ms_id in target_milestones:
                                            milestone_info = tracker.get_milestone(selected_person, ms_id)
                                            if milestone_info:
                                                st.write(f"• {milestone_info['name']}")
                                        
                                        st.write(f"**Contribution:** {suggestion.get('contribution_type', 'N/A')}")
                                        
                                    with col2:
                                        st.write(f"**Network Impact:** {suggestion.get('network_impact', 'N/A')}")
                                        confidence = suggestion.get('confidence', 0)
                                        st.metric("Confidence", f"{confidence:.1%}")
                                        
                                    # Interactive question for user
                                    question = suggestion.get('collaboration_question', 'Did you work with anyone like this?')
                                    st.markdown(f"**💭 Reflection Question:** {question}")
                                    
                                    col_yes, col_no, col_maybe = st.columns(3)
                                    with col_yes:
                                        if st.button(f"✅ Yes", key=f"cofounder_yes_{i}"):
                                            st.success("Great! This validates the analysis.")
                                    with col_no:
                                        if st.button(f"❌ No", key=f"cofounder_no_{i}"):
                                            st.info("This could be a missed opportunity to explore.")
                                    with col_maybe:
                                        if st.button(f"🤔 Maybe", key=f"cofounder_maybe_{i}"):
                                            st.warning("Consider reaching out to potential collaborators.")
                        
                        # Collaboration insights
                        if 'collaboration_insights' in cofounder_data:
                            insights = cofounder_data['collaboration_insights']
                            st.markdown("#### 📊 Collaboration Insights")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if 'most_beneficial_partnerships' in insights:
                                    st.write("**Most Beneficial Partnerships:**")
                                    for partnership in insights['most_beneficial_partnerships']:
                                        st.write(f"• {partnership}")
                            
                            with col2:
                                if 'network_gaps' in insights:
                                    st.write("**Network Gaps:**")
                                    st.write(insights['network_gaps'])
                    else:
                        st.warning("No cofounder analysis available.")
                
                # Counterfactual Analysis Tab
                with analysis_tabs[1]:
                    if 'counterfactual_analysis' in analysis_results:
                        counterfactual_data = analysis_results['counterfactual_analysis']
                        
                        if counterfactual_data.get('counterfactual_scenarios'):
                            st.markdown("#### 🔄 What-If Scenarios")
                            st.write("Explore alternative paths and hidden insights about your journey:")
                            
                            for i, scenario in enumerate(counterfactual_data['counterfactual_scenarios']):
                                impact_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                                impact_icon = impact_color.get(scenario.get('impact_level', 'Medium'), '🟡')
                                
                                with st.expander(f"{impact_icon} **{scenario.get('scenario_title', 'Scenario')}** ({scenario.get('scenario_type', 'Unknown')})"):
                                    st.markdown(f"**What-If:** {scenario.get('what_if_question', 'N/A')}")
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write("**Predicted Outcome:**")
                                        st.write(scenario.get('predicted_outcome', 'N/A'))
                                        
                                        st.write("**Network Changes:**")
                                        st.write(scenario.get('network_changes', 'N/A'))
                                        
                                    with col2:
                                        st.write("**Insights Revealed:**")
                                        st.write(scenario.get('insights_revealed', 'N/A'))
                                        
                                        probability = scenario.get('probability_assessment', 0)
                                        st.metric("Probability", f"{probability:.1%}")
                                    
                                    st.markdown("**💡 Actionable Lessons:**")
                                    st.info(scenario.get('actionable_lessons', 'No specific lessons identified.'))
                        
                        # Key insights
                        if 'key_insights' in counterfactual_data:
                            insights = counterfactual_data['key_insights']
                            st.markdown("#### 🎯 Key Insights")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                critical = insights.get('most_critical_milestones', [])
                                st.metric("Critical Milestones", len(critical))
                                if critical:
                                    st.write("**Most Critical:**")
                                    for ms_id in critical[:3]:
                                        milestone_info = tracker.get_milestone(selected_person, ms_id)
                                        if milestone_info:
                                            st.write(f"• {milestone_info['name']}")
                            
                            with col2:
                                alt_paths = insights.get('alternative_paths_identified', 0)
                                st.metric("Alternative Paths", alt_paths)
                                
                            with col3:
                                resilience = insights.get('resilience_assessment', 'Unknown')
                                st.metric("Path Resilience", resilience)
                    else:
                        st.warning("No counterfactual analysis available.")
                
                # Intervention Analysis Tab
                with analysis_tabs[2]:
                    if 'intervention_analysis' in analysis_results:
                        intervention_data = analysis_results['intervention_analysis']
                        
                        if intervention_data.get('intervention_results'):
                            st.markdown("#### ⚡ Intervention Effects")
                            st.write("Analyze the impact of removing critical milestones or connections:")
                            
                            for i, result in enumerate(intervention_data['intervention_results']):
                                severity_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                                severity_icon = severity_color.get(result.get('impact_severity', 'Medium'), '🟡')
                                
                                intervention_type = result.get('intervention_type', 'unknown')
                                target_name = result.get('target_name', 'Unknown')
                                
                                with st.expander(f"{severity_icon} **Remove:** {target_name} ({intervention_type.replace('_', ' ').title()})"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.write("**Impact Metrics:**")
                                        connectivity_change = result.get('connectivity_change', 0)
                                        efficiency_change = result.get('efficiency_change', 0)
                                        
                                        st.metric("Connectivity Loss", f"{connectivity_change:.2f}")
                                        st.metric("Efficiency Loss", f"{efficiency_change:.2f}")
                                        
                                        affected = result.get('affected_milestones', [])
                                        st.metric("Affected Milestones", len(affected))
                                        
                                    with col2:
                                        st.write("**Effects:**")
                                        if result.get('network_fragmentation'):
                                            st.error("⚠️ Network fragmentation")
                                        if result.get('cascade_effects'):
                                            st.warning("🔄 Cascade effects")
                                        
                                        severity = result.get('impact_severity', 'Medium')
                                        st.metric("Impact Severity", severity)
                                    
                                    if affected:
                                        st.write("**Affected Milestones:**")
                                        for ms_id in affected[:5]:  # Show max 5
                                            milestone_info = tracker.get_milestone(selected_person, ms_id)
                                            if milestone_info:
                                                st.write(f"• {milestone_info['name']}")
                        
                        # Intervention insights
                        if 'insights' in intervention_data:
                            insights = intervention_data['insights']
                            st.markdown("#### 🛡️ Network Resilience")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                vulnerabilities = insights.get('critical_vulnerabilities', 0)
                                st.metric("Critical Vulnerabilities", vulnerabilities)
                                
                            with col2:
                                cascade_risks = insights.get('cascade_risks', 0)
                                st.metric("Cascade Risks", cascade_risks)
                                
                            with col3:
                                resilience = insights.get('network_resilience', 'Unknown')
                                resilience_color = {"High": "success", "Medium": "warning", "Low": "error"}
                                st.metric("Overall Resilience", resilience)
                            
                            if 'optimization_recommendations' in insights:
                                st.markdown("**🔧 Optimization Recommendations:**")
                                for rec in insights['optimization_recommendations']:
                                    st.info(f"💡 {rec}")
                            
                            if 'most_fragile_connections' in insights:
                                st.markdown("**🔗 Most Fragile Connections:**")
                                for connection in insights['most_fragile_connections'][:3]:
                                    st.warning(f"⚠️ {connection}")
                    else:
                        st.warning("No intervention analysis available.")
                
                # Analysis metadata
                st.markdown("---")
                st.caption(f"Analysis generated on {analysis_results.get('analysis_timestamp', 'Unknown')} | "
                         f"Graph: {analysis_results.get('graph_metrics', {}).get('total_milestones', 0)} milestones, "
                         f"{analysis_results.get('graph_metrics', {}).get('total_relationships', 0)} relationships")
            else:
                st.error("Failed to load causality analysis results.")
        else:
            st.info("Click 'Causal Analysis' button to run advanced analysis.")

    # === SAFETY MONITORING PANEL ===
    # Show safety agent statistics and status under the chatbot
    st.markdown("---")
    st.markdown("### 🛡️ Safety Monitoring")
    
    # Create two columns for the monitoring information
    col_stats, col_status = st.columns(2)
    
    with col_stats:
        st.markdown("#### Moderation Statistics")
        if 'moderation_stats' in st.session_state:
            stats = st.session_state.moderation_stats
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Checks", stats['total_checks'])
                st.metric("Flagged Questions", stats['flagged_questions'])
            with col2:
                st.metric("Flagged Answers", stats['flagged_answers'])
                st.metric("AI Interventions", stats['interventions'])
            
            # Show moderation efficiency
            if stats['total_checks'] > 0:
                efficiency = ((stats['total_checks'] - stats['flagged_questions'] - stats['flagged_answers']) / stats['total_checks']) * 100
                st.metric("Discussion Quality", f"{efficiency:.1f}%")
            else:
                st.metric("Discussion Quality", "100%")
        
    with col_status:
        st.markdown("#### Current Safety Status")
        if 'safety_moderator' in st.session_state:
            moderator_status = st.session_state.safety_moderator.get_status()
            
            # Display key status information in a more user-friendly way
            if moderator_status:
                st.info(f"**Violations:** {moderator_status.get('consecutive_violations', 0)}/{moderator_status.get('max_violations', 3)}")
                
                # Color-coded safety level
                violations = moderator_status.get('consecutive_violations', 0)
                max_violations = moderator_status.get('max_violations', 3)
                
                if violations == 0:
                    st.success("🟢 Safety Level: Excellent")
                elif violations == 1:
                    st.warning("🟡 Safety Level: Good")
                elif violations == 2:
                    st.warning("🟠 Safety Level: Caution")
                else:
                    st.error("🔴 Safety Level: Alert")
            else:
                st.error("Safety moderator status unavailable")
        else:
            st.error("Safety moderator not initialized")
    
    # Reset button
    if st.button("🔄 Reset Safety Stats", help="Clear moderation statistics and reset safety status"):
        st.session_state.moderation_stats = {
            'total_checks': 0,
            'flagged_questions': 0,
            'flagged_answers': 0,
            'suggestions_provided': 0,
            'interventions': 0
        }
        if 'safety_moderator' in st.session_state:
            st.session_state.safety_moderator.reset()
        st.success("Safety statistics reset!")
        st.rerun()

def render_data_export():
    if st.session_state.data_loaded:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 💾 Export Data")
        json_data = st.session_state.tracker.save_data()
        st.sidebar.download_button(
            label="📥 Download Updated JSON",
            data=json_data,
            file_name=f"career_data_updated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            help="Download your current progress with all changes"
        )

# --- Main Application ---
def main():
    initialize_session_state()
    st.markdown('<h1 class="main-header">Robee\'s Career Milestone Tracker</h1>', unsafe_allow_html=True)
    render_sidebar()
    render_main_content()
    render_data_export()

if __name__ == "__main__":
    main()