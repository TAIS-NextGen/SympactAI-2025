"""
Interface Agent - Handles UI communication, votes, and interface updates
"""
import streamlit as st
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

class InterfaceAgent:
    """
    Primary Responsibilities:
    - Communicate with interface
    - Receive thumbs up/down votes from interface  
    - Process roadmap updates from interview discussions
    - Send updates to the interface
    - Compute thumbs up/down scores
    """
    
    def __init__(self):
        self.session_state_manager = SessionStateManager()
        self.vote_processor = VoteProcessor()
        self.ui_manager = UIManager()
        
    def initialize_interface(self, title: str = "Robee", icon: str = "🐝"):
        """Initialize Streamlit interface configuration"""
        st.set_page_config(
            page_title=title,
            page_icon=icon,
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    def setup_css_styling(self):
        """Apply custom CSS styling to the interface"""
        css_styles = """
        <style>
        .chat-container {
            max-height: 400px;
            overflow-y: auto;
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 8px;
            margin: 1rem 0;
        }
        .user-message {
            background-color: #e3f2fd;
            padding: 0.75rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border-left: 4px solid #2196f3;
        }
        .assistant-message {
            background-color: #f3e5f5;
            padding: 0.75rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border-left: 4px solid #9c27b0;
        }
        .vote-button {
            margin: 0.25rem;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            border: none;
            cursor: pointer;
        }
        .vote-up {
            background-color: #4caf50;
            color: white;
        }
        .vote-down {
            background-color: #f44336;
            color: white;
        }
        .milestone-card {
            background-color: white;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #ddd;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
        """
        st.markdown(css_styles, unsafe_allow_html=True)
        
    def display_chat_interface(self, chat_key: str, goal_title: str = "") -> Optional[str]:
        """Display chat interface and handle user input"""
        st.subheader(f"💬 Discussion about: {goal_title}")
        
        # Display chat history
        if chat_key in st.session_state:
            for message in st.session_state[chat_key]:
                if message["role"] == "user":
                    st.markdown(f'<div class="user-message"><strong>You:</strong> {message["content"]}</div>', 
                              unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="assistant-message"><strong>AI:</strong> {message["content"]}</div>', 
                              unsafe_allow_html=True)
        
        # User input
        user_input = st.text_input("Your response:", key=f"input_{chat_key}")
        
        if st.button("Send", key=f"send_{chat_key}"):
            if user_input:
                return user_input
        return None
        
    def display_voting_interface(self, milestone_id: str, milestone_name: str, tracker=None, person=None, goal_id=None) -> Optional[bool]:
        """Display voting interface for milestones with current vote status"""
        st.markdown(f"### 👍👎 Vote on this Milestone")
        st.markdown(f"**{milestone_name}**")
        
        # Get current vote status if tracker is provided
        has_vote = False
        current_vote = None
        if tracker and person and goal_id:
            has_vote = tracker.has_milestone_vote(person, goal_id, milestone_id)
            current_vote = tracker.get_milestone_current_vote(person, goal_id, milestone_id)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        if has_vote:
            # Show current vote status with disabled buttons
            with col1:
                st.button("👍", key=f"up_{milestone_id}", disabled=True, help="You already voted")
            with col2:
                st.button("👎", key=f"down_{milestone_id}", disabled=True, help="You already voted")
            with col3:
                vote_text = "👍 Liked" if current_vote else "👎 Disliked"
                st.markdown(f"*Current: {vote_text}*")
                st.markdown("*You have already voted on this milestone*")
            return None
        else:
            # Show active voting buttons
            with col1:
                if st.button("👍", key=f"up_{milestone_id}", help="This milestone is correct and important"):
                    return True
            with col2:
                if st.button("👎", key=f"down_{milestone_id}", help="This milestone is wrong or unimportant"):
                    return False
            with col3:
                st.markdown("👍 = Correct & Important")
                st.markdown("👎 = Wrong or Unimportant")
            return None
        
    def display_milestone_form(self, suggested_milestone: Dict = None) -> Dict:
        """Display form for adding/editing milestones"""
        with st.form(key="milestone_form", clear_on_submit=True):
            st.subheader("Add New Milestone")
            
            name = st.text_input(
                "Milestone Name", 
                value=suggested_milestone.get("name", "") if suggested_milestone else ""
            )
            description = st.text_area("Description (optional)")
            score = st.slider("Importance Score", 1, 10, 5)
            
            # Parent milestone selection
            parent_options = self._get_available_milestones()
            parent_id = st.selectbox(
                "Connect to milestone:", 
                options=list(parent_options.keys()),
                format_func=lambda x: parent_options.get(x, "None")
            )
            
            submitted = st.form_submit_button("Add Milestone")
            
            if submitted and name:
                return {
                    "name": name,
                    "description": description,
                    "score": score,
                    "parent_id": parent_id,
                    "timestamp": datetime.now().isoformat()
                }
        return {}
        
    def display_feedback_interface(self, context: str) -> Dict:
        """Display general feedback collection interface"""
        st.subheader("📝 Your Feedback")
        
        feedback_type = st.selectbox(
            "Feedback Type:",
            ["General", "Missing Milestone", "Wrong Connection", "Other"]
        )
        
        feedback_text = st.text_area(f"Feedback about: {context}")
        
        if st.button("Submit Feedback"):
            if feedback_text:
                return {
                    "type": feedback_type,
                    "text": feedback_text,
                    "context": context,
                    "timestamp": datetime.now().isoformat()
                }
        return {}
        
    def update_interface_state(self, key: str, value: Any):
        """Update interface state"""
        st.session_state[key] = value
        
    def get_interface_state(self, key: str, default: Any = None) -> Any:
        """Get interface state value"""
        return st.session_state.get(key, default)
        
    def display_progress_indicator(self, current_step: int, total_steps: int, step_name: str):
        """Display progress indicator"""
        progress = current_step / total_steps
        st.progress(progress)
        st.caption(f"Step {current_step}/{total_steps}: {step_name}")
        
    def display_notification(self, message: str, type: str = "info"):
        """Display notifications to user"""
        if type == "success":
            st.success(message)
        elif type == "error":
            st.error(message)
        elif type == "warning":
            st.warning(message)
        else:
            st.info(message)
            
    def store_conversation_message(self, chat_key: str, role: str, content: str):
        """Store conversation message in session state"""
        if chat_key not in st.session_state:
            st.session_state[chat_key] = {"messages": []}
            
        message_data = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "type": "answer" if role == "user" else "question"
        }
        
        st.session_state[chat_key]["messages"].append(message_data)
        
    def get_conversation_summary(self, chat_key: str) -> str:
        """Generate a summary of the conversation"""
        if chat_key not in st.session_state:
            return "No conversation yet"
            
        messages = st.session_state[chat_key].get("messages", [])
        if not messages:
            return "No messages in conversation"
            
        message_count = len(messages)
        recent_topics = []
        
        # Extract recent topics from last 3 messages
        for msg in messages[-3:]:
            content = msg.get("content", "")
            if len(content) > 50:
                recent_topics.append(content[:50] + "...")
            else:
                recent_topics.append(content)
                
        return f"Conversation with {message_count} messages. Recent topics: {'; '.join(recent_topics)}"
        
    def create_enhanced_conversation_context(self, session_messages: list, goal_title: str, max_length: int = 1000) -> str:
        """Create enhanced conversation context for AI responses"""
        career_messages = []
        for msg in session_messages:
            content = msg.get("content", "")
            # Filter out safety/moderation messages
            if not any(keyword in content.lower() for keyword in ["safety", "moderation", "discussion focus", "keep our conversation"]):
                career_messages.append(content)
        
        # Join recent messages for context
        recent_context = " | ".join(career_messages[-5:]) if career_messages else ""
        context_with_goal = f"Goal: {goal_title} | {recent_context}"
        
        # Truncate if too long
        if len(context_with_goal) > max_length:
            context_with_goal = context_with_goal[:max_length] + "..."
        
        return context_with_goal
        
    def _get_available_milestones(self) -> Dict[str, str]:
        """Get available milestones for selection"""
        # This would be populated by the graph manager
        if "milestones" in st.session_state:
            return {ms["id"]: ms["name"] for ms in st.session_state["milestones"]}
        return {"none": "No parent"}


class SessionStateManager:
    """Manages Streamlit session state"""
    
    def __init__(self):
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize default session state values"""
        defaults = {
            "chat_history": [],
            "milestones": [],
            "votes": {},
            "current_goal": None,
            "current_person": None,
            "analysis_results": {},
            "feedback_history": []
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
                
    def store_conversation(self, chat_key: str, role: str, content: str):
        """Store conversation message"""
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []
            
        st.session_state[chat_key].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_conversation_history(self, chat_key: str) -> List[Dict]:
        """Get conversation history"""
        return st.session_state.get(chat_key, [])
        
    def store_milestone_data(self, milestone_data: Dict):
        """Store milestone data"""
        if "milestones" not in st.session_state:
            st.session_state["milestones"] = []
        st.session_state["milestones"].append(milestone_data)
        
    def update_analysis_results(self, analysis_type: str, results: Dict):
        """Store analysis results"""
        if "analysis_results" not in st.session_state:
            st.session_state["analysis_results"] = {}
        st.session_state["analysis_results"][analysis_type] = results


class VoteProcessor:
    """Handles vote processing and score computation"""
    
    def __init__(self):
        self.vote_history = {}
        
    def process_vote(self, milestone_id: str, vote: bool, user_id: str = "default") -> Dict:
        """Process a thumbs up/down vote"""
        vote_data = {
            "milestone_id": milestone_id,
            "vote": vote,  # True for thumbs up, False for thumbs down
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in session state
        vote_key = f"vote_{milestone_id}"
        st.session_state[vote_key] = vote
        
        # Update vote history
        if milestone_id not in self.vote_history:
            self.vote_history[milestone_id] = []
        self.vote_history[milestone_id].append(vote_data)
        
        return vote_data
        
    def compute_vote_scores(self, milestone_id: str) -> Dict:
        """Compute aggregated vote scores for a milestone"""
        votes = self.vote_history.get(milestone_id, [])
        
        if not votes:
            return {"score": 0, "positive": 0, "negative": 0, "total": 0}
            
        positive_votes = sum(1 for vote in votes if vote["vote"])
        negative_votes = sum(1 for vote in votes if not vote["vote"])
        total_votes = len(votes)
        
        # Calculate score (percentage positive)
        score = (positive_votes / total_votes) * 100 if total_votes > 0 else 0
        
        return {
            "score": score,
            "positive": positive_votes,
            "negative": negative_votes,
            "total": total_votes
        }
        
    def get_vote_summary(self, milestone_ids: List[str]) -> Dict:
        """Get vote summary for multiple milestones"""
        summary = {}
        for milestone_id in milestone_ids:
            summary[milestone_id] = self.compute_vote_scores(milestone_id)
        return summary
        
    def has_user_voted(self, milestone_id: str, user_id: str = "default") -> bool:
        """Check if user has already voted on milestone"""
        votes = self.vote_history.get(milestone_id, [])
        return any(vote["user_id"] == user_id for vote in votes)


class UIManager:
    """Manages UI components and layouts"""
    
    def create_sidebar(self) -> Dict:
        """Create and manage sidebar"""
        with st.sidebar:
            st.title("🐝 Robee Control Panel")
            
            # Navigation
            page = st.selectbox(
                "Navigate to:",
                ["Roadmap Viewer", "Interview", "Analysis", "Settings"]
            )
            
            # Quick stats
            st.subheader("📊 Quick Stats")
            if "milestones" in st.session_state:
                milestone_count = len(st.session_state["milestones"])
                st.metric("Total Milestones", milestone_count)
                
            if "analysis_results" in st.session_state:
                analysis_count = len(st.session_state["analysis_results"])
                st.metric("Completed Analyses", analysis_count)
                
            return {"current_page": page}
            
    def create_tabs(self, tab_names: List[str]) -> Dict:
        """Create tab interface"""
        tabs = st.tabs(tab_names)
        return {name: tab for name, tab in zip(tab_names, tabs)}
        
    def create_columns(self, ratios: List[int]):
        """Create column layout"""
        return st.columns(ratios)
        
    def display_metrics_dashboard(self, metrics: Dict):
        """Display metrics in a dashboard format"""
        cols = st.columns(len(metrics))
        
        for i, (label, value) in enumerate(metrics.items()):
            with cols[i]:
                if isinstance(value, dict) and "value" in value:
                    st.metric(
                        label=label,
                        value=value["value"],
                        delta=value.get("delta", None)
                    )
                else:
                    st.metric(label=label, value=value)
