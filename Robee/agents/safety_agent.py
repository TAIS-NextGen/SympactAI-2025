"""
Safety Agent - Content moderation and safety monitoring
"""
import json
import re
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from groq import Groq, AsyncGroq

@dataclass
class InterviewContext:
    topic: str
    stage: str 
    key_skills: List[str]

@dataclass
class ModerationResult:
    is_valid: bool
    message: str
    suggested_question: Optional[str] = None
    should_stop: bool = False
    confidence: float = 0.0

class SafetyAgent:
    """
    Primary Responsibilities:
    - Moderate content and ensure safety
    - Monitor for off-topic, harmful, or inappropriate content
    - Provide real-time safety guidance
    - Track violations and enforce limits
    """
    
    def __init__(self, groq_api_key: str, max_violations: int = 5, model: str = "moonshotai/kimi-k2-instruct"):
        self.content_moderator = ContentModerator(groq_api_key, max_violations, model)
        self.safety_monitor = SafetyMonitor()
        self.violation_tracker = ViolationTracker(max_violations)
        
    def moderate_input(self, text: str, is_chatbot_question: bool, context: InterviewContext, 
                      conversation_history: str = "") -> Dict:
        """Main moderation function"""
        if is_chatbot_question:
            result = self.content_moderator.check_chatbot_question(text, context, conversation_history)
            return self._format_moderation_result(result, "chatbot_question")
        else:
            result = self.content_moderator.check_interviewee_answer(text, context, conversation_history)
            return self._format_moderation_result(result, "interviewee_answer")
            
    async def moderate_input_async(self, text: str, is_chatbot_question: bool, context: InterviewContext,
                                  conversation_history: str = "") -> Dict:
        """Async version for better performance"""
        if is_chatbot_question:
            result = await self.content_moderator.check_chatbot_question_async(text, context, conversation_history)
            return self._format_moderation_result(result, "chatbot_question")
        else:
            result = await self.content_moderator.check_interviewee_answer_async(text, context, conversation_history)
            return self._format_moderation_result(result, "interviewee_answer")
            
    def get_safety_status(self) -> Dict:
        """Get current safety status"""
        return {
            "violation_count": self.violation_tracker.get_violation_count(),
            "max_violations": self.violation_tracker.max_violations,
            "is_at_risk": self.violation_tracker.is_at_risk(),
            "safety_level": self.safety_monitor.get_safety_level(),
            "last_check": datetime.now().isoformat()
        }
        
    def reset_violations(self):
        """Reset violation counter"""
        self.violation_tracker.reset()
        
    def _format_moderation_result(self, result: ModerationResult, input_type: str) -> Dict:
        """Format moderation result for return"""
        formatted = {
            "type": input_type,
            "is_valid": result.is_valid,
            "message": result.message,
            "confidence": result.confidence,
            "should_stop": result.should_stop,
            "status": self.get_safety_status()
        }
        
        if input_type == "chatbot_question":
            formatted.update({
                "suggested_question": result.suggested_question,
                "should_resample": not result.is_valid
            })
        else:
            formatted.update({
                "should_realign": not result.is_valid and not result.should_stop
            })
            
        return formatted


class ContentModerator:
    """Handles content moderation using Groq API and fallback patterns"""
    
    def __init__(self, groq_api_key: str, max_violations: int = 5, model: str = "moonshotai/kimi-k2-instruct"):
        self.groq_client = Groq(api_key=groq_api_key)
        self.async_groq_client = AsyncGroq(api_key=groq_api_key)
        self.model = model
        self.max_violations = max_violations
        self.consecutive_violations = 0
        
        # Cache for repeated contexts to avoid redundant API calls
        self._context_cache = {}
        self._last_context_hash = None
        
        # Fallback patterns for when API fails
        self.fallback_patterns = {
            'off_topic': re.compile(r'\b(weather|food|movie|music|sport|game|family|relationship|politics|weekend|vacation|hobby|travel)\b', re.IGNORECASE),
            'adversarial': re.compile(r'\b(ignore|forget|change topic|tell me about yourself|claude|ai|assistant)\b', re.IGNORECASE)
        }
        
    def check_chatbot_question(self, question: str, context: InterviewContext, 
                              conversation_history: str = "") -> ModerationResult:
        """Check chatbot question with Groq API"""
        try:
            system_prompt = self._create_system_prompt(context, is_chatbot_question=True)
            
            user_message = f"Question: {question}"
            if conversation_history:
                user_message += f"\nRecent conversation: {conversation_history[-500:]}"
                
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=200,
                top_p=0.9
            )
            
            result_json = json.loads(response.choices[0].message.content)
            
            if result_json["is_valid"]:
                return ModerationResult(
                    is_valid=True,
                    message="Question is appropriate for the interview context.",
                    confidence=result_json.get("confidence", 0.8)
                )
            else:
                return ModerationResult(
                    is_valid=False,
                    message=f"Question doesn't fit the interview context: {result_json['reason']}",
                    suggested_question=result_json.get("suggested_question"),
                    confidence=result_json.get("confidence", 0.8)
                )
                
        except Exception as e:
            # Fallback to pattern matching
            return self._fallback_check_question(question, context)
            
    def check_interviewee_answer(self, answer: str, context: InterviewContext,
                                conversation_history: str = "") -> ModerationResult:
        """Check interviewee answer with Groq API"""
        try:
            system_prompt = self._create_system_prompt(context, is_chatbot_question=False)
            
            user_message = f"Answer: {answer}"
            if conversation_history:
                user_message += f"\nRecent conversation: {conversation_history[-500:]}"
                
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=200,
                top_p=0.9
            )
            
            result_json = json.loads(response.choices[0].message.content)
            
            if result_json["is_valid"]:
                self.consecutive_violations = 0
                return ModerationResult(
                    is_valid=True,
                    message="Answer is relevant to the interview.",
                    confidence=result_json.get("confidence", 0.8)
                )
            else:
                self.consecutive_violations += 1
                
                if self.consecutive_violations >= self.max_violations:
                    return ModerationResult(
                        is_valid=False,
                        message="Interview terminated due to repeated off-topic responses.",
                        should_stop=True,
                        confidence=result_json.get("confidence", 0.8)
                    )
                    
                realignment_msg = result_json.get("realignment_message") or self._generate_realignment_message(context, self.consecutive_violations)
                return ModerationResult(
                    is_valid=False,
                    message=realignment_msg,
                    confidence=result_json.get("confidence", 0.8)
                )
                
        except Exception as e:
            # Fallback to pattern matching
            return self._fallback_check_answer(answer, context)
            
    async def check_chatbot_question_async(self, question: str, context: InterviewContext,
                                          conversation_history: str = "") -> ModerationResult:
        """Async version for better performance"""
        try:
            system_prompt = self._create_system_prompt(context, is_chatbot_question=True)
            
            user_message = f"Question: {question}"
            if conversation_history:
                user_message += f"\nRecent conversation: {conversation_history[-500:]}"
                
            response = await self.async_groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=200,
                top_p=0.9
            )
            
            result_json = json.loads(response.choices[0].message.content)
            
            if result_json["is_valid"]:
                return ModerationResult(
                    is_valid=True,
                    message="Question is appropriate for the interview context.",
                    confidence=result_json.get("confidence", 0.8)
                )
            else:
                return ModerationResult(
                    is_valid=False,
                    message=f"Question doesn't fit the interview context: {result_json['reason']}",
                    suggested_question=result_json.get("suggested_question"),
                    confidence=result_json.get("confidence", 0.8)
                )
                
        except Exception as e:
            # Fallback to synchronous pattern matching
            return self.check_chatbot_question(question, context, conversation_history)
            
    async def check_interviewee_answer_async(self, answer: str, context: InterviewContext,
                                           conversation_history: str = "") -> ModerationResult:
        """Async version for better performance"""
        try:
            system_prompt = self._create_system_prompt(context, is_chatbot_question=False)
            
            user_message = f"Answer: {answer}"
            if conversation_history:
                user_message += f"\nRecent conversation: {conversation_history[-500:]}"
                
            response = await self.async_groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=200,
                top_p=0.9
            )
            
            result_json = json.loads(response.choices[0].message.content)
            
            if result_json["is_valid"]:
                self.consecutive_violations = 0
                return ModerationResult(
                    is_valid=True,
                    message="Answer is relevant to the interview.",
                    confidence=result_json.get("confidence", 0.8)
                )
            else:
                self.consecutive_violations += 1
                
                if self.consecutive_violations >= self.max_violations:
                    return ModerationResult(
                        is_valid=False,
                        message="Interview terminated due to repeated off-topic responses.",
                        should_stop=True,
                        confidence=result_json.get("confidence", 0.8)
                    )
                    
                realignment_msg = result_json.get("realignment_message") or self._generate_realignment_message(context, self.consecutive_violations)
                return ModerationResult(
                    is_valid=False,
                    message=realignment_msg,
                    confidence=result_json.get("confidence", 0.8)
                )
                
        except Exception as e:
            # Fallback to synchronous pattern matching
            return self.check_interviewee_answer(answer, context, conversation_history)
            
    def _create_system_prompt(self, context: InterviewContext, is_chatbot_question: bool) -> str:
        """Create optimized system prompt for Groq"""
        context_hash = self._get_context_hash(context)
        
        if context_hash == self._last_context_hash and context_hash in self._context_cache:
            return self._context_cache[context_hash]
            
        if is_chatbot_question:
            prompt = f"""You are an interview moderation assistant. Determine if the given question is appropriate for an interview about "{context.topic}" in the "{context.stage}" stage, focusing on skills: {', '.join(context.key_skills)}.

Respond ONLY with valid JSON:
{{
    "is_valid": true/false,
    "reason": "brief explanation if invalid",
    "suggested_question": "alternative question if invalid",
    "confidence": 0.0-1.0
}}

Valid questions should:
- Relate to the interview topic and skills
- Be professional and respectful
- Help assess relevant experience/knowledge

Invalid questions are:
- Off-topic (personal life, unrelated subjects)
- Inappropriate or unprofessional
- Too vague or confusing"""

        else:
            prompt = f"""You are an interview moderation assistant. Determine if the given answer is relevant to an interview about "{context.topic}" in the "{context.stage}" stage, focusing on skills: {', '.join(context.key_skills)}.

Respond ONLY with valid JSON:
{{
    "is_valid": true/false,
    "reason": "brief explanation if invalid", 
    "realignment_message": "helpful redirect message if invalid",
    "confidence": 0.0-1.0
}}

Valid answers should:
- Address the interview topic or related skills
- Show engagement with the conversation
- Provide relevant information or context

Invalid answers are:
- Completely off-topic 
- Evasive or non-responsive
- Inappropriate content"""

        self._context_cache[context_hash] = prompt
        self._last_context_hash = context_hash
        return prompt
        
    def _get_context_hash(self, context: InterviewContext) -> str:
        """Generate hash for context caching"""
        return f"{context.topic}_{context.stage}_{'_'.join(sorted(context.key_skills))}"
        
    def _fallback_check_question(self, question: str, context: InterviewContext) -> ModerationResult:
        """Fallback check using regex patterns for questions"""
        is_valid, confidence, reason = self._fallback_check(question, context)
        
        if is_valid:
            return ModerationResult(
                is_valid=True,
                message="Question appears appropriate (fallback check).",
                confidence=confidence
            )
        else:
            return ModerationResult(
                is_valid=False,
                message=f"Question may be inappropriate: {reason}",
                suggested_question=self._generate_fallback_question(context),
                confidence=confidence
            )
            
    def _fallback_check_answer(self, answer: str, context: InterviewContext) -> ModerationResult:
        """Fallback check using regex patterns for answers"""
        is_valid, confidence, reason = self._fallback_check(answer, context)
        
        if is_valid:
            return ModerationResult(
                is_valid=True,
                message="Answer appears relevant (fallback check).",
                confidence=confidence
            )
        else:
            self.consecutive_violations += 1
            return ModerationResult(
                is_valid=False,
                message=self._generate_realignment_message(context, self.consecutive_violations),
                confidence=confidence
            )
            
    def _fallback_check(self, text: str, context: InterviewContext) -> Tuple[bool, float, str]:
        """Fast fallback check using regex patterns"""
        text_lower = text.lower()
        
        # Check for off-topic content
        if self.fallback_patterns['off_topic'].search(text):
            return False, 0.7, "Contains off-topic content"
            
        # Check for adversarial content
        if self.fallback_patterns['adversarial'].search(text):
            return False, 0.8, "Contains adversarial patterns"
            
        # Basic length check
        if len(text.strip()) < 3:
            return False, 0.9, "Response too short"
            
        # If none of the negative patterns match, assume valid
        return True, 0.6, "No obvious issues detected"
        
    def _generate_fallback_question(self, context: InterviewContext) -> str:
        """Generate fallback question without API"""
        return f"Can you tell me about your experience with {context.key_skills[0] if context.key_skills else context.topic}?"
        
    def _generate_realignment_message(self, context: InterviewContext, violation_count: int) -> str:
        """Generate realignment message without API"""
        if violation_count >= 3:
            return f"Let's please stay focused on discussing {context.topic}. This is important for providing you with relevant guidance."
        else:
            return f"I'd like to keep our discussion focused on {context.topic}. Could you share something related to this topic?"


class SafetyMonitor:
    """Monitors overall safety metrics and patterns"""
    
    def __init__(self):
        self.safety_metrics = {
            "total_checks": 0,
            "violations": 0,
            "false_positives": 0,
            "manual_overrides": 0
        }
        
    def record_check(self, result: ModerationResult, manual_override: bool = False):
        """Record a safety check"""
        self.safety_metrics["total_checks"] += 1
        
        if not result.is_valid:
            self.safety_metrics["violations"] += 1
            
        if manual_override:
            self.safety_metrics["manual_overrides"] += 1
            
    def get_safety_level(self) -> str:
        """Get current safety level assessment"""
        if self.safety_metrics["total_checks"] == 0:
            return "UNKNOWN"
            
        violation_rate = self.safety_metrics["violations"] / self.safety_metrics["total_checks"]
        
        if violation_rate < 0.1:
            return "LOW_RISK"
        elif violation_rate < 0.3:
            return "MEDIUM_RISK"
        else:
            return "HIGH_RISK"
            
    def get_metrics_summary(self) -> Dict:
        """Get safety metrics summary"""
        return self.safety_metrics.copy()


class ViolationTracker:
    """Tracks violations and enforces limits"""
    
    def __init__(self, max_violations: int = 5):
        self.max_violations = max_violations
        self.consecutive_violations = 0
        self.total_violations = 0
        self.violation_history = []
        
    def record_violation(self, violation_type: str, message: str):
        """Record a violation"""
        self.consecutive_violations += 1
        self.total_violations += 1
        
        violation_record = {
            "type": violation_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "consecutive_count": self.consecutive_violations
        }
        
        self.violation_history.append(violation_record)
        
    def record_valid_interaction(self):
        """Record a valid interaction (resets consecutive count)"""
        self.consecutive_violations = 0
        
    def is_at_risk(self) -> bool:
        """Check if at risk of termination"""
        return self.consecutive_violations >= (self.max_violations - 1)
        
    def should_terminate(self) -> bool:
        """Check if should terminate due to violations"""
        return self.consecutive_violations >= self.max_violations
        
    def get_violation_count(self) -> int:
        """Get current consecutive violation count"""
        return self.consecutive_violations
        
    def reset(self):
        """Reset violation counters"""
        self.consecutive_violations = 0
        
    def get_violation_history(self) -> List[Dict]:
        """Get violation history"""
        return self.violation_history.copy()


# Utility functions for backward compatibility
def moderate_interview_input_groq(
    text: str,
    is_chatbot_question: bool,
    interview_topic: str,
    groq_api_key: str,
    interview_stage: str = "technical",
    key_skills: List[str] = None,
    conversation_history: str = "",
    moderator: SafetyAgent = None,
    model: str = "llama-3.1-8b-instant"
) -> Dict:
    """
    Moderate interview inputs using Groq API - Backward compatibility function
    """
    if moderator is None:
        moderator = SafetyAgent(groq_api_key, model=model)
        
    if key_skills is None:
        key_skills = []
        
    context = InterviewContext(
        topic=interview_topic,
        stage=interview_stage,
        key_skills=key_skills
    )
    
    return moderator.moderate_input(text, is_chatbot_question, context, conversation_history)


async def moderate_interview_input_groq_async(
    text: str,
    is_chatbot_question: bool,
    interview_topic: str,
    groq_api_key: str,
    interview_stage: str = "technical",
    key_skills: List[str] = None,
    conversation_history: str = "",
    moderator: SafetyAgent = None,
    model: str = "moonshotai/kimi-k2-instruct"
) -> Dict:
    """Async version for better performance - Backward compatibility function"""
    if moderator is None:
        moderator = SafetyAgent(groq_api_key, model=model)
        
    if key_skills is None:
        key_skills = []
        
    context = InterviewContext(
        topic=interview_topic,
        stage=interview_stage,
        key_skills=key_skills
    )
    
    return await moderator.moderate_input_async(text, is_chatbot_question, context, conversation_history)


# Backward compatibility wrapper
class GroqInterviewModerator:
    """
    Backward compatibility wrapper around SafetyAgent to maintain the old interface
    """
    
    def __init__(self, groq_api_key: str, max_violations: int = 5, model: str = "moonshotai/kimi-k2-instruct"):
        self.safety_agent = SafetyAgent(groq_api_key, max_violations, model)
        self.groq_api_key = groq_api_key
        self.max_violations = max_violations
        self.model = model
        
    @property
    def consecutive_violations(self):
        """Get consecutive violations count"""
        return self.safety_agent.violation_tracker.consecutive_violations
        
    @consecutive_violations.setter
    def consecutive_violations(self, value):
        """Set consecutive violations count"""
        self.safety_agent.violation_tracker.consecutive_violations = value
        
    def moderate_input(self, text: str, is_chatbot_question: bool, context: InterviewContext, conversation_history: str = "") -> Dict:
        """Main moderation function - wrapper for backward compatibility"""
        return self.safety_agent.moderate_input(text, is_chatbot_question, context, conversation_history)
        
    def check_chatbot_question(self, question: str, context: InterviewContext, conversation_history: str = "") -> ModerationResult:
        """Check chatbot question - wrapper for backward compatibility"""
        result = self.safety_agent.moderate_input(question, True, context, conversation_history)
        return ModerationResult(
            is_valid=result["is_valid"],
            message=result["message"],
            suggested_question=result.get("suggested_question"),
            should_stop=result["should_stop"],
            confidence=result["confidence"]
        )
        
    def check_interviewee_answer(self, answer: str, context: InterviewContext, conversation_history: str = "") -> ModerationResult:
        """Check interviewee answer - wrapper for backward compatibility"""
        result = self.safety_agent.moderate_input(answer, False, context, conversation_history)
        return ModerationResult(
            is_valid=result["is_valid"],
            message=result["message"],
            should_stop=result["should_stop"],
            confidence=result["confidence"]
        )
        
    async def check_chatbot_question_async(self, question: str, context: InterviewContext, conversation_history: str = "") -> ModerationResult:
        """Async check chatbot question - wrapper for backward compatibility"""
        result = await self.safety_agent.moderate_input_async(question, True, context, conversation_history)
        return ModerationResult(
            is_valid=result["is_valid"],
            message=result["message"],
            suggested_question=result.get("suggested_question"),
            should_stop=result["should_stop"],
            confidence=result["confidence"]
        )
        
    async def check_interviewee_answer_async(self, answer: str, context: InterviewContext, conversation_history: str = "") -> ModerationResult:
        """Async check interviewee answer - wrapper for backward compatibility"""
        result = await self.safety_agent.moderate_input_async(answer, False, context, conversation_history)
        return ModerationResult(
            is_valid=result["is_valid"],
            message=result["message"],
            should_stop=result["should_stop"],
            confidence=result["confidence"]
        )
        
    def get_status(self) -> Dict:
        """Get current moderation status - wrapper for backward compatibility"""
        safety_status = self.safety_agent.get_safety_status()
        return {
            "consecutive_violations": safety_status["violation_count"],
            "max_violations": safety_status["max_violations"],
            "remaining_violations": max(0, safety_status["max_violations"] - safety_status["violation_count"]),
            "should_stop": safety_status["violation_count"] >= safety_status["max_violations"],
            "cache_size": 0  # Not applicable in new structure
        }
        
    def reset(self):
        """Reset violation counter - wrapper for backward compatibility"""
        self.safety_agent.reset_violations()
        
    def clear_cache(self):
        """Clear cache - wrapper for backward compatibility (no-op in new structure)"""
        pass
