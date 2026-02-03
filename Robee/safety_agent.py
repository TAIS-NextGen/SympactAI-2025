import json
import asyncio
import nest_asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
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

class GroqInterviewModerator:
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

    def _get_context_hash(self, context: InterviewContext) -> str:
        """Generate hash for context caching"""
        return f"{context.topic}{context.stage}{'_'.join(sorted(context.key_skills))}"

    def _create_system_prompt(self, context: InterviewContext, is_chatbot_question: bool) -> str:
        """Create optimized system prompt for Groq"""
        context_hash = self._get_context_hash(context)

        # Use cached prompt if context hasn't changed
        if context_hash == self._last_context_hash and context_hash in self._context_cache:
            return self._context_cache[context_hash][is_chatbot_question]

        # Create new prompts
        base_context = f"""Interview Context:
- Topic: {context.topic}
- Stage: {context.stage}
- Key Skills: {', '.join(context.key_skills)}

You are an interview moderator. Respond with ONLY a JSON object."""

        if is_chatbot_question:
            system_prompt = f"""{base_context}

Evaluate if the chatbot's question fits the interview context.

Response format:
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "reason": "brief explanation",
    "suggested_question": "better question if invalid, null if valid"
}}

Rules:
- Valid if relates to topic, skills, or stage
- Invalid if about personal life, entertainment, weather, off-topic subjects
- Keep suggested_question concise and relevant"""

        else:
            system_prompt = f"""{base_context}

Evaluate if the interviewee's answer fits the interview context.

Response format:
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "reason": "brief explanation",
    "realignment_message": "polite redirect if invalid, null if valid"
}}

Rules:
- Valid if addresses interview topic or demonstrates relevant skills
- Invalid if about personal life, entertainment, weather, completely off-topic
- Keep realignment_message polite and redirecting to interview topic"""

        # Cache the prompts
        if context_hash not in self._context_cache:
            self._context_cache[context_hash] = {}
        self._context_cache[context_hash][is_chatbot_question] = system_prompt
        self._last_context_hash = context_hash

        return system_prompt

    def _fallback_check(self, text: str, context: InterviewContext) -> Tuple[bool, float, str]:
        """Fast fallback check using regex patterns"""
        text_lower = text.lower()

        # Check for obvious off-topic content
        if self.fallback_patterns['off_topic'].search(text_lower):
            return False, 0.8, "Contains off-topic content"

        # Check for adversarial patterns
        if self.fallback_patterns['adversarial'].search(text_lower):
            return False, 0.9, "Contains adversarial patterns"

        # Simple keyword relevance check
        topic_words = context.topic.lower().split()
        skill_words = [skill.lower() for skill in context.key_skills]
        all_relevant_words = topic_words + skill_words

        matches = sum(1 for word in all_relevant_words if word in text_lower)
        if matches >= 1:
            return True, 0.6, "Contains relevant keywords"

        # Default to uncertain
        return True, 0.3, "Uncertain - allowing by default"

    def check_chatbot_question(self, question: str, context: InterviewContext, conversation_history: str = "") -> ModerationResult:
        """Check chatbot question with Groq API"""
        try:
            system_prompt = self._create_system_prompt(context, is_chatbot_question=True)

            user_message = f"Question: {question}"
            if conversation_history:
                user_message += f"\nRecent conversation: {conversation_history[-500:]}"  # Limit context

            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,  # Low temperature for consistent evaluation
                max_tokens=200,   # Limit response length
                top_p=0.9
            )

            result_json = json.loads(response.choices[0].message.content)

            if result_json["is_valid"]:
                self.consecutive_violations = 0
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
            is_valid, confidence, reason = self._fallback_check(question, context)
            if is_valid:
                self.consecutive_violations = 0
                return ModerationResult(
                    is_valid=True,
                    message="Question approved (fallback evaluation).",
                    confidence=confidence
                )
            else:
                return ModerationResult(
                    is_valid=False,
                    message=f"Question rejected (fallback): {reason}",
                    suggested_question=self._generate_fallback_question(context),
                    confidence=confidence
                )

    def check_interviewee_answer(self, answer: str, context: InterviewContext, conversation_history: str = "") -> ModerationResult:
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
                max_tokens=150,
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
            is_valid, confidence, reason = self._fallback_check(answer, context)
            if is_valid:
                self.consecutive_violations = 0
                return ModerationResult(
                    is_valid=True,
                    message="Answer approved (fallback evaluation).",
                    confidence=confidence
                )
            else:
                self.consecutive_violations += 1

                if self.consecutive_violations >= self.max_violations:
                    return ModerationResult(
                        is_valid=False,
                        message="Interview terminated due to repeated off-topic responses.",
                        should_stop=True,
                        confidence=confidence
                    )

                return ModerationResult(
                    is_valid=False,
                    message=self._generate_realignment_message(context, self.consecutive_violations),
                    confidence=confidence
                )

    async def check_chatbot_question_async(self, question: str, context: InterviewContext, conversation_history: str = "") -> ModerationResult:
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
                self.consecutive_violations = 0
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

    async def check_interviewee_answer_async(self, answer: str, context: InterviewContext, conversation_history: str = "") -> ModerationResult:
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
                max_tokens=150,
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

    def _generate_fallback_question(self, context: InterviewContext) -> str:
        """Generate fallback question without API"""
        templates = {
            'intro': f"Can you tell me about your background in {context.topic}?",
            'technical': f"How would you approach a problem involving {context.topic}?",
            'behavioral': f"Tell me about a time when you used {context.topic} skills.",
            'wrap-up': f"What questions do you have about {context.topic}?"
        }
        return templates.get(context.stage, templates['technical'])

    def _generate_realignment_message(self, context: InterviewContext, violation_count: int) -> str:
        """Generate realignment message without API"""
        messages = [
            f"Let's focus on {context.topic}. Could you please address the interview question?",
            f"I'd like to keep our discussion about {context.topic}. Can you share your relevant experience?",
            f"Please stay on topic about {context.topic}. Tell me about your experience with this.",
            f"This is important: let's focus on {context.topic} for our interview.",
            f"Final reminder: please keep responses related to {context.topic}."
        ]
        return messages[min(violation_count - 1, len(messages) - 1)]

    def get_status(self) -> Dict:
        """Get current moderation status"""
        return {
            "consecutive_violations": self.consecutive_violations,
            "max_violations": self.max_violations,
            "remaining_violations": max(0, self.max_violations - self.consecutive_violations),
            "should_stop": self.consecutive_violations >= self.max_violations,
            "cache_size": len(self._context_cache)
        }

    def reset(self):
        """Reset violation counter"""
        self.consecutive_violations = 0

    def clear_cache(self):
        """Clear prompt cache"""
        self._context_cache.clear()
        self._last_context_hash = None

# Optimized usage functions
def moderate_interview_input_groq(
    text: str,
    is_chatbot_question: bool,
    interview_topic: str,
    groq_api_key: str,
    interview_stage: str = "technical",
    key_skills: List[str] = None,
    conversation_history: str = "",
    moderator: GroqInterviewModerator = None,
    model: str = "llama-3.1-8b-instant"
) -> Dict:
    """
    Moderate interview inputs using Groq API

    Args:
        text: Input text to moderate
        is_chatbot_question: True for chatbot questions, False for interviewee answers
        interview_topic: Current interview topic
        groq_api_key: Your Groq API key
        interview_stage: Current stage
        key_skills: List of relevant skills
        conversation_history: Recent conversation context
        moderator: Existing moderator instance
        model: Groq model to use
    """

    if moderator is None:
        moderator = GroqInterviewModerator(groq_api_key, model=model)

    if key_skills is None:
        key_skills = []

    context = InterviewContext(
        topic=interview_topic,
        stage=interview_stage,
        key_skills=key_skills
    )

    if is_chatbot_question:
        result = moderator.check_chatbot_question(text, context, conversation_history)
        return {
            "type": "chatbot_question",
            "is_valid": result.is_valid,
            "message": result.message,
            "suggested_question": result.suggested_question,
            "should_resample": not result.is_valid,
            "should_stop": result.should_stop,
            "confidence": result.confidence,
            "status": moderator.get_status()
        }
    else:
        result = moderator.check_interviewee_answer(text, context, conversation_history)
        return {
            "type": "interviewee_answer",
            "is_valid": result.is_valid,
            "message": result.message,
            "should_realign": not result.is_valid and not result.should_stop,
            "should_stop": result.should_stop,
            "confidence": result.confidence,
            "status": moderator.get_status()
        }

async def moderate_interview_input_groq_async(
    text: str,
    is_chatbot_question: bool,
    interview_topic: str,
    groq_api_key: str,
    interview_stage: str = "technical",
    key_skills: List[str] = None,
    conversation_history: str = "",
    moderator: GroqInterviewModerator = None,
    model: str = "moonshotai/kimi-k2-instruct"
) -> Dict:
    """Async version for better performance"""

    if moderator is None:
        moderator = GroqInterviewModerator(groq_api_key, model=model)

    if key_skills is None:
        key_skills = []

    context = InterviewContext(
        topic=interview_topic,
        stage=interview_stage,
        key_skills=key_skills
    )

    if is_chatbot_question:
        result = await moderator.check_chatbot_question_async(text, context, conversation_history)
        return {
            "type": "chatbot_question",
            "is_valid": result.is_valid,
            "message": result.message,
            "suggested_question": result.suggested_question,
            "should_resample": not result.is_valid,
            "should_stop": result.should_stop,
            "confidence": result.confidence,
            "status": moderator.get_status()
        }
    else:
        result = await moderator.check_interviewee_answer_async(text, context, conversation_history)
        return {
            "type": "interviewee_answer",
            "is_valid": result.is_valid,
            "message": result.message,
            "should_realign": not result.is_valid and not result.should_stop,
            "should_stop": result.should_stop,
            "confidence": result.confidence,
            "status": moderator.get_status()
        }

    
async def main_async_test():
    """Example usage of the async converter"""

    # Get API key from environment
    GROQ_API_KEY = 'your_groq_api_key_here'  # Replace with your actual Groq API key or environment variable
    if not GROQ_API_KEY:
        print("Please set GROQ_API_KEY environment variable")
        exit(1)

    # Initialize moderator
    moderator = GroqInterviewModerator(GROQ_API_KEY, model="moonshotai/kimi-k2-instruct")

    print("=== Testing Groq-Powered Interview Moderation ===")

    # Test good chatbot question
    result1 = moderate_interview_input_groq(
        text="Can you explain how you would implement a binary search algorithm in Python?",
        is_chatbot_question=True,
        interview_topic="Python Programming",
        groq_api_key=GROQ_API_KEY,
        key_skills=["Python", "algorithms", "data structures"],
        moderator=moderator
    )
    print("Good chatbot question:")
    print(json.dumps(result1, indent=2))

    # Test bad chatbot question
    result2 = moderate_interview_input_groq(
        text="What's your favorite movie and why?",
        is_chatbot_question=True,
        interview_topic="Python Programming",
        groq_api_key=GROQ_API_KEY,
        key_skills=["Python", "algorithms", "data structures"],
        moderator=moderator
    )
    print("\nBad chatbot question:")
    print(json.dumps(result2, indent=2))

    # Test async version
    result = await moderate_interview_input_groq_async(
        text="I think Python is great for data science applications.",
        is_chatbot_question=False,
        interview_topic="Python Programming",
        groq_api_key=GROQ_API_KEY,
        key_skills=["Python", "data science"],
        moderator=moderator
    )
    print("\nAsync interviewee answer:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    # Run async test
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main_async_test())