"""
Vote Processing Agent - Handles milestone voting and approval workflow
"""
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import math

class VoteProcessingAgent:
    """
    Primary Responsibilities:
    - Process and validate milestone votes
    - Manage voting workflows and approval processes
    - Track voting patterns and consensus
    - Handle vote aggregation and decision making
    - Advanced group scoring and analysis
    """
    
    def __init__(self):
        self.vote_tracker = VoteTracker()
        self.consensus_engine = ConsensusEngine()
        self.approval_manager = ApprovalManager()
        self.voting_analytics = VotingAnalytics()
        
        # Voting configuration
        self.voting_config = {
            "approval_threshold": 0.6,  # 60% approval required
            "minimum_votes": 3,
            "voting_window_hours": 24,
            "tie_breaking_method": "admin_decision"
        }
        
    def process_vote(self, milestone_id: str, vote: bool, user_id: str, 
                    context: Dict = None, weight: float = 1.0) -> Dict:
        """Process a single vote for a milestone"""
        
        # Validate vote
        validation_result = self._validate_vote(milestone_id, user_id, vote, context)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result["error"],
                "milestone_id": milestone_id
            }
        
        # Record vote
        vote_record = self.vote_tracker.record_vote(milestone_id, user_id, vote, weight, context)
        
        # Check if voting should be concluded
        conclusion_check = self._check_voting_conclusion(milestone_id)
        
        result = {
            "success": True,
            "milestone_id": milestone_id,
            "vote_recorded": vote_record,
            "current_status": self.get_voting_status(milestone_id),
            "voting_concluded": conclusion_check["concluded"]
        }
        
        if conclusion_check["concluded"]:
            final_decision = self.conclude_voting(milestone_id)
            result["final_decision"] = final_decision
            
        return result
        
    def batch_process_votes(self, votes: List[Dict]) -> Dict:
        """Process multiple votes in batch"""
        results = []
        summary = {
            "total_votes": len(votes),
            "successful_votes": 0,
            "failed_votes": 0,
            "concluded_votings": 0
        }
        
        for vote_data in votes:
            milestone_id = vote_data.get("milestone_id")
            vote = vote_data.get("vote")
            user_id = vote_data.get("user_id")
            context = vote_data.get("context", {})
            weight = vote_data.get("weight", 1.0)
            
            result = self.process_vote(milestone_id, vote, user_id, context, weight)
            results.append(result)
            
            if result["success"]:
                summary["successful_votes"] += 1
                if result.get("voting_concluded", False):
                    summary["concluded_votings"] += 1
            else:
                summary["failed_votes"] += 1
                
        return {
            "batch_results": results,
            "summary": summary,
            "processed_at": datetime.now().isoformat()
        }
        
    def conclude_voting(self, milestone_id: str) -> Dict:
        """Conclude voting for a milestone and make final decision"""
        voting_data = self.vote_tracker.get_milestone_votes(milestone_id)
        
        if not voting_data:
            return {"error": "No voting data found for milestone"}
            
        # Calculate final consensus
        consensus_result = self.consensus_engine.calculate_consensus(voting_data)
        
        # Make approval decision
        approval_decision = self.approval_manager.make_decision(
            consensus_result, self.voting_config
        )
        
        # Record final decision
        final_result = {
            "milestone_id": milestone_id,
            "decision": approval_decision["decision"],
            "approval_score": consensus_result["approval_score"],
            "total_votes": consensus_result["total_votes"],
            "confidence": consensus_result["confidence"],
            "reasoning": approval_decision["reasoning"],
            "concluded_at": datetime.now().isoformat()
        }
        
        # Mark voting as concluded
        self.vote_tracker.conclude_voting(milestone_id, final_result)
        
        return final_result
        
    def get_voting_status(self, milestone_id: str) -> Dict:
        """Get current voting status for a milestone"""
        voting_data = self.vote_tracker.get_milestone_votes(milestone_id)
        
        if not voting_data:
            return {"status": "no_votes", "milestone_id": milestone_id}
            
        current_consensus = self.consensus_engine.calculate_consensus(voting_data)
        
        return {
            "milestone_id": milestone_id,
            "status": "active" if not voting_data.get("concluded", False) else "concluded",
            "total_votes": current_consensus["total_votes"],
            "approval_score": current_consensus["approval_score"],
            "confidence": current_consensus["confidence"],
            "time_remaining": self._calculate_time_remaining(voting_data),
            "needs_votes": self._check_if_more_votes_needed(voting_data)
        }
        
    def get_voting_analytics(self, milestone_ids: List[str] = None, 
                           time_period: int = 30) -> Dict:
        """Get voting analytics and patterns"""
        return self.voting_analytics.generate_analytics(
            milestone_ids, time_period, self.vote_tracker
        )
        
    def get_user_voting_history(self, user_id: str, limit: int = 50) -> Dict:
        """Get voting history for a specific user"""
        return self.vote_tracker.get_user_voting_history(user_id, limit)
    
    # === ENHANCED GROUP SCORING METHODS ===
    
    def calculate_group_score(self, group_milestones: List[Dict]) -> Dict:
        """Calculate comprehensive group scoring based on milestone votes"""
        if not group_milestones:
            return {
                'total_vote_score': 0,
                'avg_vote_score': 0,
                'thumbs_down_count': 0,
                'problematic_score': 0,
                'confidence': 0.0,
                'decision': 'insufficient_data'
            }
        
        group_vote_scores = []
        thumbs_down_count = 0
        total_votes = 0
        positive_votes = 0
        
        for milestone in group_milestones:
            vote_summary = milestone.get('vote_summary', {})
            thumbs_up = vote_summary.get('thumbs_up', 0)
            thumbs_down = vote_summary.get('thumbs_down', 0)
            
            # Calculate individual milestone score
            milestone_score = thumbs_up - thumbs_down
            group_vote_scores.append(milestone_score)
            
            if thumbs_down > 0:
                thumbs_down_count += 1
                
            total_votes += thumbs_up + thumbs_down
            positive_votes += thumbs_up
        
        # Calculate group metrics
        total_vote_score = sum(group_vote_scores)
        avg_vote_score = total_vote_score / len(group_vote_scores) if group_vote_scores else 0
        
        # Enhanced problematic score calculation
        problematic_score = avg_vote_score - (thumbs_down_count * 0.5)
        
        # Calculate group confidence
        confidence = positive_votes / total_votes if total_votes > 0 else 0.5
        
        # Determine group status
        decision = self._determine_group_status(avg_vote_score, thumbs_down_count, len(group_milestones), confidence)
        
        return {
            'total_vote_score': total_vote_score,
            'avg_vote_score': round(avg_vote_score, 2),
            'thumbs_down_count': thumbs_down_count,
            'problematic_score': round(problematic_score, 2),
            'confidence': round(confidence, 2),
            'decision': decision,
            'total_milestones': len(group_milestones),
            'total_votes': total_votes,
            'positive_votes': positive_votes
        }
    
    def should_remove_group(self, group_analysis: Dict, threshold: float = 0.8) -> bool:
        """Enhanced logic to determine if a group should be removed"""
        if not group_analysis['total_milestones']:
            return False
        
        # Use VoteProcessingAgent's sophisticated decision making
        thumbs_down_ratio = group_analysis['thumbs_down_count'] / group_analysis['total_milestones']
        
        # Multiple criteria for removal
        criteria_met = 0
        
        # Criterion 1: High ratio of thumbs down milestones
        if thumbs_down_ratio >= threshold:
            criteria_met += 1
            
        # Criterion 2: Very low problematic score
        if group_analysis['problematic_score'] < -2:
            criteria_met += 1
            
        # Criterion 3: Low confidence with negative average
        if group_analysis['confidence'] < 0.3 and group_analysis['avg_vote_score'] < 0:
            criteria_met += 1
            
        # Criterion 4: High vote engagement but overwhelmingly negative
        if group_analysis['total_votes'] >= 3 and group_analysis['avg_vote_score'] < -1:
            criteria_met += 1
        
        # Require at least 2 criteria for removal recommendation
        return criteria_met >= 2
    
    def analyze_milestone_groups(self, groups: List[Dict]) -> Dict:
        """Comprehensive analysis of all milestone groups"""
        if not groups:
            return {'error': 'No groups provided for analysis'}
        
        analyzed_groups = []
        
        for group in groups:
            milestones = group.get('milestones', [])
            group_analysis = self.calculate_group_score(milestones)
            
            # Add removal recommendation
            group_analysis['should_remove'] = self.should_remove_group(group_analysis)
            
            # Add focus priority
            group_analysis['focus_priority'] = self._calculate_focus_priority(group_analysis)
            
            analyzed_groups.append({
                **group,
                'analysis': group_analysis
            })
        
        # Sort by focus priority (highest first)
        analyzed_groups.sort(key=lambda x: x['analysis']['focus_priority'], reverse=True)
        
        # Overall analysis
        total_groups = len(analyzed_groups)
        problematic_groups = sum(1 for g in analyzed_groups if g['analysis']['should_remove'])
        high_priority_groups = sum(1 for g in analyzed_groups if g['analysis']['focus_priority'] > 0.7)
        
        return {
            'groups': analyzed_groups,
            'summary': {
                'total_groups': total_groups,
                'problematic_groups': problematic_groups,
                'high_priority_groups': high_priority_groups,
                'removal_rate': problematic_groups / total_groups if total_groups > 0 else 0,
                'overall_health': self._calculate_overall_health(analyzed_groups)
            }
        }
    
    def get_enhanced_milestone_vote_summary(self, person: str, goal_id: str, milestone_id: str, 
                                          existing_votes: List[Dict] = None) -> Dict:
        """Enhanced vote summary using VoteProcessingAgent's algorithms"""
        if existing_votes is None:
            existing_votes = []
        
        thumbs_up = sum(1 for vote in existing_votes if vote.get('vote', False))
        thumbs_down = sum(1 for vote in existing_votes if not vote.get('vote', False))
        total_votes = len(existing_votes)
        
        # Use ConsensusEngine for better confidence calculation
        if total_votes > 0:
            # Create voting data structure
            voting_data = {
                'votes': [{'vote': vote.get('vote', False), 'weight': 1.0} for vote in existing_votes]
            }
            consensus_result = self.consensus_engine.calculate_consensus(voting_data)
            confidence = consensus_result['confidence']
        else:
            confidence = 0.5
        
        return {
            'thumbs_up': thumbs_up,
            'thumbs_down': thumbs_down,
            'total_votes': total_votes,
            'score': thumbs_up - thumbs_down,
            'confidence': round(confidence, 2),
            'approval_rate': thumbs_up / total_votes if total_votes > 0 else 0,
            'consensus_level': self._get_consensus_level(confidence, thumbs_up, thumbs_down)
        }
    
    def _determine_group_status(self, avg_score: float, thumbs_down_count: int, 
                               total_milestones: int, confidence: float) -> str:
        """Determine the status of a milestone group"""
        if total_milestones == 0:
            return 'empty'
        
        thumbs_down_ratio = thumbs_down_count / total_milestones
        
        if avg_score >= 1 and confidence > 0.7:
            return 'excellent'
        elif avg_score >= 0 and thumbs_down_ratio < 0.3:
            return 'good'
        elif avg_score >= -1 and thumbs_down_ratio < 0.5:
            return 'needs_attention'
        elif thumbs_down_ratio >= 0.7 or avg_score < -2:
            return 'critical'
        else:
            return 'problematic'
    
    def _calculate_focus_priority(self, group_analysis: Dict) -> float:
        """Calculate priority score for focusing on this group (0-1 scale)"""
        priority = 0.0
        
        # High thumbs down count increases priority
        thumbs_down_ratio = group_analysis['thumbs_down_count'] / group_analysis['total_milestones']
        priority += thumbs_down_ratio * 0.4
        
        # Low average score increases priority
        if group_analysis['avg_vote_score'] < 0:
            priority += abs(group_analysis['avg_vote_score']) * 0.1
        
        # Low problematic score increases priority
        if group_analysis['problematic_score'] < 0:
            priority += abs(group_analysis['problematic_score']) * 0.1
        
        # High vote engagement increases priority
        if group_analysis['total_votes'] > 2:
            priority += min(group_analysis['total_votes'] / 10, 0.2)
        
        # Low confidence with votes increases priority
        if group_analysis['total_votes'] > 0 and group_analysis['confidence'] < 0.5:
            priority += (0.5 - group_analysis['confidence']) * 0.2
        
        return min(priority, 1.0)
    
    def _calculate_overall_health(self, analyzed_groups: List[Dict]) -> str:
        """Calculate overall health of all groups"""
        if not analyzed_groups:
            return 'unknown'
        
        total = len(analyzed_groups)
        critical = sum(1 for g in analyzed_groups if g['analysis']['decision'] == 'critical')
        problematic = sum(1 for g in analyzed_groups if g['analysis']['decision'] == 'problematic')
        good = sum(1 for g in analyzed_groups if g['analysis']['decision'] in ['good', 'excellent'])
        
        critical_ratio = critical / total
        problematic_ratio = problematic / total
        good_ratio = good / total
        
        if critical_ratio > 0.3:
            return 'critical'
        elif problematic_ratio > 0.5:
            return 'needs_attention'
        elif good_ratio > 0.6:
            return 'good'
        else:
            return 'fair'
    
    def _get_consensus_level(self, confidence: float, thumbs_up: int, thumbs_down: int) -> str:
        """Get human-readable consensus level"""
        if thumbs_up == 0 and thumbs_down == 0:
            return 'no_votes'
        elif confidence >= 0.9:
            return 'strong_consensus'
        elif confidence >= 0.7:
            return 'good_consensus'
        elif confidence >= 0.5:
            return 'weak_consensus'
        else:
            return 'no_consensus'
    
    # Interface compatibility methods
    def add_milestone_vote(self, person: str, goal_id: str, milestone_id: str, vote: bool) -> bool:
        """Add a vote for a milestone (interface compatibility)"""
        try:
            user_id = f"{person}_user"  # Create user ID from person
            context = {
                "person": person,
                "goal_id": goal_id,
                "milestone_id": milestone_id
            }
            
            result = self.process_vote(milestone_id, vote, user_id, context)
            return result.get("success", False)
        except Exception:
            return False
    
    def get_milestone_vote_summary(self, person: str, goal_id: str, milestone_id: str) -> Dict:
        """Get vote summary for a milestone (interface compatibility)"""
        try:
            voting_data = self.vote_tracker.get_milestone_votes(milestone_id)
            if not voting_data:
                return {'upvotes': 0, 'downvotes': 0}
            
            votes = voting_data.get("votes", [])
            upvotes = sum(1 for vote in votes if vote["vote"])
            downvotes = len(votes) - upvotes
            
            return {
                'upvotes': upvotes,
                'downvotes': downvotes,
                'total_votes': len(votes)
            }
        except Exception:
            return {'upvotes': 0, 'downvotes': 0}
    
    def has_milestone_vote(self, person: str, goal_id: str, milestone_id: str) -> bool:
        """Check if milestone has votes (interface compatibility)"""
        try:
            voting_data = self.vote_tracker.get_milestone_votes(milestone_id)
            if not voting_data:
                return False
            return len(voting_data.get("votes", [])) > 0
        except Exception:
            return False
    
    def has_any_milestone_votes(self, person: str, goal_id: str) -> bool:
        """Check if there are any votes for any milestone in the goal (interface compatibility)"""
        try:
            # This would need to be implemented based on how voting data is stored
            # For now, return False as fallback
            return False
        except Exception:
            return False
    
    def get_milestone_current_vote(self, person: str, goal_id: str, milestone_id: str):
        """Get current user vote for milestone (interface compatibility)"""
        try:
            user_id = f"{person}_user"
            user_vote = self.vote_tracker.get_user_vote(milestone_id, user_id)
            if user_vote:
                return user_vote["vote"]
            return None
        except Exception:
            return None
    
    def clear_milestone_vote(self, person: str, goal_id: str, milestone_id: str) -> bool:
        """Clear vote for milestone (interface compatibility)"""
        try:
            user_id = f"{person}_user"
            voting_data = self.vote_tracker.get_milestone_votes(milestone_id)
            if not voting_data:
                return False
            
            # Remove user's vote from the voting session
            votes = voting_data.get("votes", [])
            original_count = len(votes)
            voting_data["votes"] = [vote for vote in votes if vote["user_id"] != user_id]
            
            # Also remove from user's voting history
            if user_id in self.vote_tracker.user_votes:
                self.vote_tracker.user_votes[user_id] = [
                    entry for entry in self.vote_tracker.user_votes[user_id] 
                    if entry["milestone_id"] != milestone_id
                ]
            
            return len(voting_data["votes"]) < original_count
        except Exception:
            return False
        
    def _validate_vote(self, milestone_id: str, user_id: str, vote: bool, 
                      context: Dict = None) -> Dict:
        """Validate a vote before processing"""
        
        # Check if milestone exists
        if not milestone_id:
            return {"valid": False, "error": "Milestone ID is required"}
            
        # Check if user ID is valid
        if not user_id:
            return {"valid": False, "error": "User ID is required"}
            
        # Check if vote is boolean
        if not isinstance(vote, bool):
            return {"valid": False, "error": "Vote must be boolean (True/False)"}
            
        # Check if user has already voted
        existing_vote = self.vote_tracker.get_user_vote(milestone_id, user_id)
        if existing_vote:
            return {"valid": False, "error": "User has already voted on this milestone"}
            
        # Check if voting is still open
        voting_data = self.vote_tracker.get_milestone_votes(milestone_id)
        if voting_data and voting_data.get("concluded", False):
            return {"valid": False, "error": "Voting for this milestone has already concluded"}
            
        return {"valid": True}
        
    def _check_voting_conclusion(self, milestone_id: str) -> Dict:
        """Check if voting should be concluded"""
        voting_data = self.vote_tracker.get_milestone_votes(milestone_id)
        
        if not voting_data:
            return {"concluded": False, "reason": "No voting data"}
            
        # Check minimum votes
        vote_count = len(voting_data.get("votes", []))
        if vote_count < self.voting_config["minimum_votes"]:
            return {"concluded": False, "reason": "Insufficient votes"}
            
        # Check time window
        start_time = datetime.fromisoformat(voting_data["started_at"])
        elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
        
        if elapsed_hours >= self.voting_config["voting_window_hours"]:
            return {"concluded": True, "reason": "Time window expired"}
            
        # Check for unanimous decision
        consensus = self.consensus_engine.calculate_consensus(voting_data)
        if consensus["confidence"] >= 0.95:  # Very high confidence
            return {"concluded": True, "reason": "Strong consensus reached"}
            
        return {"concluded": False, "reason": "Voting continues"}
        
    def _calculate_time_remaining(self, voting_data: Dict) -> Optional[float]:
        """Calculate remaining time for voting in hours"""
        if voting_data.get("concluded", False):
            return None
            
        start_time = datetime.fromisoformat(voting_data["started_at"])
        elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
        remaining = self.voting_config["voting_window_hours"] - elapsed_hours
        
        return max(0, remaining)
        
    def _check_if_more_votes_needed(self, voting_data: Dict) -> bool:
        """Check if more votes are needed for a decision"""
        if voting_data.get("concluded", False):
            return False
            
        vote_count = len(voting_data.get("votes", []))
        min_votes = self.voting_config["minimum_votes"]
        
        return vote_count < min_votes


class VoteTracker:
    """Tracks and stores voting data"""
    
    def __init__(self):
        self.voting_sessions = {}  # milestone_id -> voting session data
        self.user_votes = defaultdict(list)  # user_id -> list of vote records
        self.vote_counter = 0
        
    def record_vote(self, milestone_id: str, user_id: str, vote: bool, 
                   weight: float = 1.0, context: Dict = None) -> Dict:
        """Record a vote for a milestone"""
        
        # Initialize voting session if needed
        if milestone_id not in self.voting_sessions:
            self.voting_sessions[milestone_id] = {
                "milestone_id": milestone_id,
                "started_at": datetime.now().isoformat(),
                "votes": [],
                "concluded": False
            }
            
        # Create vote record
        self.vote_counter += 1
        vote_record = {
            "vote_id": f"vote_{self.vote_counter}",
            "user_id": user_id,
            "vote": vote,
            "weight": weight,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        # Add to voting session
        self.voting_sessions[milestone_id]["votes"].append(vote_record)
        
        # Add to user voting history
        self.user_votes[user_id].append({
            "milestone_id": milestone_id,
            "vote_record": vote_record
        })
        
        return vote_record
        
    def get_milestone_votes(self, milestone_id: str) -> Optional[Dict]:
        """Get all votes for a milestone"""
        return self.voting_sessions.get(milestone_id)
        
    def get_user_vote(self, milestone_id: str, user_id: str) -> Optional[Dict]:
        """Get user's vote for a specific milestone"""
        voting_session = self.voting_sessions.get(milestone_id)
        if not voting_session:
            return None
            
        for vote in voting_session["votes"]:
            if vote["user_id"] == user_id:
                return vote
                
        return None
        
    def get_user_voting_history(self, user_id: str, limit: int = 50) -> Dict:
        """Get voting history for a user"""
        user_history = self.user_votes.get(user_id, [])
        
        # Sort by timestamp, most recent first
        sorted_history = sorted(
            user_history,
            key=lambda x: x["vote_record"]["timestamp"],
            reverse=True
        )
        
        # Apply limit
        limited_history = sorted_history[:limit]
        
        # Calculate statistics
        total_votes = len(user_history)
        positive_votes = sum(1 for entry in user_history if entry["vote_record"]["vote"])
        
        return {
            "user_id": user_id,
            "total_votes": total_votes,
            "positive_votes": positive_votes,
            "negative_votes": total_votes - positive_votes,
            "positive_rate": positive_votes / total_votes if total_votes > 0 else 0,
            "voting_history": limited_history
        }
        
    def conclude_voting(self, milestone_id: str, final_result: Dict):
        """Mark voting as concluded with final result"""
        if milestone_id in self.voting_sessions:
            self.voting_sessions[milestone_id]["concluded"] = True
            self.voting_sessions[milestone_id]["final_result"] = final_result
            self.voting_sessions[milestone_id]["concluded_at"] = datetime.now().isoformat()
            
    def get_all_voting_sessions(self) -> Dict:
        """Get all voting sessions"""
        return self.voting_sessions.copy()


class ConsensusEngine:
    """Calculates consensus and confidence scores"""
    
    def __init__(self):
        self.consensus_methods = {
            "simple_majority": self._simple_majority,
            "weighted_average": self._weighted_average,
            "confidence_weighted": self._confidence_weighted
        }
        
    def calculate_consensus(self, voting_data: Dict, method: str = "weighted_average") -> Dict:
        """Calculate consensus for voting data"""
        votes = voting_data.get("votes", [])
        
        if not votes:
            return {
                "approval_score": 0.0,
                "total_votes": 0,
                "confidence": 0.0,
                "method": method
            }
            
        # Use specified consensus method
        consensus_func = self.consensus_methods.get(method, self._weighted_average)
        result = consensus_func(votes)
        
        result["method"] = method
        result["total_votes"] = len(votes)
        
        return result
        
    def _simple_majority(self, votes: List[Dict]) -> Dict:
        """Simple majority consensus"""
        positive_votes = sum(1 for vote in votes if vote["vote"])
        total_votes = len(votes)
        
        approval_score = positive_votes / total_votes
        confidence = self._calculate_confidence_simple(total_votes, approval_score)
        
        return {
            "approval_score": approval_score,
            "confidence": confidence,
            "positive_votes": positive_votes,
            "negative_votes": total_votes - positive_votes
        }
        
    def _weighted_average(self, votes: List[Dict]) -> Dict:
        """Weighted average consensus"""
        total_weight = sum(vote.get("weight", 1.0) for vote in votes)
        weighted_positive = sum(
            vote.get("weight", 1.0) for vote in votes if vote["vote"]
        )
        
        if total_weight == 0:
            return {"approval_score": 0.0, "confidence": 0.0}
            
        approval_score = weighted_positive / total_weight
        confidence = self._calculate_confidence_weighted(votes, approval_score)
        
        return {
            "approval_score": approval_score,
            "confidence": confidence,
            "total_weight": total_weight,
            "weighted_positive": weighted_positive
        }
        
    def _confidence_weighted(self, votes: List[Dict]) -> Dict:
        """Confidence-weighted consensus"""
        # This method would incorporate individual voter confidence if available
        # For now, fall back to weighted average
        return self._weighted_average(votes)
        
    def _calculate_confidence_simple(self, total_votes: int, approval_score: float) -> float:
        """Calculate confidence for simple majority"""
        # Higher confidence with more votes and clearer majorities
        vote_confidence = min(total_votes / 10, 1.0)  # Max confidence at 10 votes
        
        # Distance from 0.5 indicates clearer consensus
        margin_confidence = abs(approval_score - 0.5) * 2
        
        return (vote_confidence + margin_confidence) / 2
        
    def _calculate_confidence_weighted(self, votes: List[Dict], approval_score: float) -> float:
        """Calculate confidence for weighted consensus"""
        total_weight = sum(vote.get("weight", 1.0) for vote in votes)
        
        # Weight-based confidence
        weight_confidence = min(total_weight / 10, 1.0)
        
        # Margin-based confidence
        margin_confidence = abs(approval_score - 0.5) * 2
        
        # Weight distribution confidence (more uniform weights = higher confidence)
        weights = [vote.get("weight", 1.0) for vote in votes]
        weight_variance = self._calculate_variance(weights)
        distribution_confidence = 1.0 / (1.0 + weight_variance)
        
        return (weight_confidence + margin_confidence + distribution_confidence) / 3
        
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if len(values) <= 1:
            return 0.0
            
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance


class ApprovalManager:
    """Manages approval decisions based on consensus"""
    
    def __init__(self):
        self.decision_rules = self._load_decision_rules()
        
    def make_decision(self, consensus_result: Dict, voting_config: Dict) -> Dict:
        """Make approval decision based on consensus and configuration"""
        approval_score = consensus_result.get("approval_score", 0.0)
        confidence = consensus_result.get("confidence", 0.0)
        total_votes = consensus_result.get("total_votes", 0)
        
        approval_threshold = voting_config.get("approval_threshold", 0.6)
        minimum_votes = voting_config.get("minimum_votes", 3)
        
        # Apply decision rules
        decision_result = self._apply_decision_rules(
            approval_score, confidence, total_votes, 
            approval_threshold, minimum_votes
        )
        
        return decision_result
        
    def _apply_decision_rules(self, approval_score: float, confidence: float,
                            total_votes: int, threshold: float, min_votes: int) -> Dict:
        """Apply decision rules to determine approval"""
        
        # Check minimum votes requirement
        if total_votes < min_votes:
            return {
                "decision": "insufficient_votes",
                "reasoning": f"Only {total_votes} votes received, minimum {min_votes} required",
                "final_approval": False
            }
            
        # Check approval threshold
        if approval_score >= threshold:
            # High approval score
            if confidence >= 0.7:
                return {
                    "decision": "approved",
                    "reasoning": f"High approval ({approval_score:.2f}) with good confidence ({confidence:.2f})",
                    "final_approval": True
                }
            else:
                return {
                    "decision": "conditionally_approved",
                    "reasoning": f"High approval ({approval_score:.2f}) but low confidence ({confidence:.2f})",
                    "final_approval": True
                }
        else:
            # Low approval score
            if confidence >= 0.7:
                return {
                    "decision": "rejected",
                    "reasoning": f"Low approval ({approval_score:.2f}) with good confidence ({confidence:.2f})",
                    "final_approval": False
                }
            else:
                return {
                    "decision": "needs_more_votes",
                    "reasoning": f"Low approval ({approval_score:.2f}) and low confidence ({confidence:.2f})",
                    "final_approval": False
                }
                
    def _load_decision_rules(self) -> Dict:
        """Load decision rules configuration"""
        return {
            "high_confidence_threshold": 0.8,
            "medium_confidence_threshold": 0.5,
            "unanimous_threshold": 0.95,
            "strong_majority_threshold": 0.75,
            "simple_majority_threshold": 0.6
        }


class VotingAnalytics:
    """Provides analytics and insights on voting patterns"""
    
    def __init__(self):
        pass
        
    def generate_analytics(self, milestone_ids: List[str] = None, 
                          time_period: int = 30, vote_tracker: VoteTracker = None) -> Dict:
        """Generate comprehensive voting analytics"""
        
        if not vote_tracker:
            return {"error": "Vote tracker not provided"}
            
        all_sessions = vote_tracker.get_all_voting_sessions()
        
        # Filter by time period
        cutoff_date = datetime.now() - timedelta(days=time_period)
        filtered_sessions = {}
        
        for milestone_id, session in all_sessions.items():
            if milestone_ids and milestone_id not in milestone_ids:
                continue
                
            start_time = datetime.fromisoformat(session["started_at"])
            if start_time >= cutoff_date:
                filtered_sessions[milestone_id] = session
                
        if not filtered_sessions:
            return {"message": "No voting data found for specified criteria"}
            
        # Calculate analytics
        analytics = {
            "period_days": time_period,
            "total_voting_sessions": len(filtered_sessions),
            "session_analytics": self._analyze_sessions(filtered_sessions),
            "vote_analytics": self._analyze_votes(filtered_sessions),
            "timing_analytics": self._analyze_timing(filtered_sessions),
            "consensus_analytics": self._analyze_consensus(filtered_sessions)
        }
        
        return analytics
        
    def _analyze_sessions(self, sessions: Dict) -> Dict:
        """Analyze voting sessions"""
        concluded_sessions = sum(1 for s in sessions.values() if s.get("concluded", False))
        active_sessions = len(sessions) - concluded_sessions
        
        # Calculate average votes per session
        total_votes = sum(len(s.get("votes", [])) for s in sessions.values())
        avg_votes_per_session = total_votes / len(sessions) if sessions else 0
        
        # Approval rates for concluded sessions
        approved_sessions = 0
        concluded_sessions_list = [s for s in sessions.values() if s.get("concluded", False)]
        
        for session in concluded_sessions_list:
            final_result = session.get("final_result", {})
            if final_result.get("final_approval", False):
                approved_sessions += 1
                
        approval_rate = approved_sessions / concluded_sessions if concluded_sessions > 0 else 0
        
        return {
            "total_sessions": len(sessions),
            "concluded_sessions": concluded_sessions,
            "active_sessions": active_sessions,
            "avg_votes_per_session": round(avg_votes_per_session, 2),
            "approval_rate": round(approval_rate, 2),
            "approved_sessions": approved_sessions
        }
        
    def _analyze_votes(self, sessions: Dict) -> Dict:
        """Analyze individual votes"""
        all_votes = []
        for session in sessions.values():
            all_votes.extend(session.get("votes", []))
            
        if not all_votes:
            return {"message": "No votes found"}
            
        positive_votes = sum(1 for vote in all_votes if vote["vote"])
        total_votes = len(all_votes)
        
        # Weight analysis
        weights = [vote.get("weight", 1.0) for vote in all_votes]
        avg_weight = sum(weights) / len(weights)
        
        # User participation
        unique_users = len(set(vote["user_id"] for vote in all_votes))
        
        return {
            "total_votes": total_votes,
            "positive_votes": positive_votes,
            "negative_votes": total_votes - positive_votes,
            "positive_rate": round(positive_votes / total_votes, 2),
            "average_weight": round(avg_weight, 2),
            "unique_voters": unique_users,
            "votes_per_user": round(total_votes / unique_users, 2) if unique_users > 0 else 0
        }
        
    def _analyze_timing(self, sessions: Dict) -> Dict:
        """Analyze timing patterns"""
        concluded_sessions = [s for s in sessions.values() if s.get("concluded", False)]
        
        if not concluded_sessions:
            return {"message": "No concluded sessions to analyze"}
            
        durations = []
        for session in concluded_sessions:
            start_time = datetime.fromisoformat(session["started_at"])
            end_time = datetime.fromisoformat(session.get("concluded_at", session["started_at"]))
            duration_hours = (end_time - start_time).total_seconds() / 3600
            durations.append(duration_hours)
            
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        return {
            "concluded_sessions": len(concluded_sessions),
            "avg_duration_hours": round(avg_duration, 2),
            "min_duration_hours": round(min_duration, 2),
            "max_duration_hours": round(max_duration, 2),
            "quick_decisions": sum(1 for d in durations if d < 1),  # Less than 1 hour
            "long_decisions": sum(1 for d in durations if d > 12)   # More than 12 hours
        }
        
    def _analyze_consensus(self, sessions: Dict) -> Dict:
        """Analyze consensus patterns"""
        consensus_engine = ConsensusEngine()
        
        consensus_scores = []
        confidence_scores = []
        
        for session in sessions.values():
            if session.get("votes"):
                consensus = consensus_engine.calculate_consensus(session)
                consensus_scores.append(consensus["approval_score"])
                confidence_scores.append(consensus["confidence"])
                
        if not consensus_scores:
            return {"message": "No consensus data available"}
            
        avg_consensus = sum(consensus_scores) / len(consensus_scores)
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Categorize consensus levels
        high_consensus = sum(1 for score in consensus_scores if score > 0.8)
        medium_consensus = sum(1 for score in consensus_scores if 0.4 <= score <= 0.8)
        low_consensus = sum(1 for score in consensus_scores if score < 0.4)
        
        return {
            "total_analyzed": len(consensus_scores),
            "avg_consensus_score": round(avg_consensus, 2),
            "avg_confidence_score": round(avg_confidence, 2),
            "high_consensus_count": high_consensus,
            "medium_consensus_count": medium_consensus,
            "low_consensus_count": low_consensus,
            "consensus_distribution": {
                "high": round(high_consensus / len(consensus_scores), 2),
                "medium": round(medium_consensus / len(consensus_scores), 2),
                "low": round(low_consensus / len(consensus_scores), 2)
            }
        }

