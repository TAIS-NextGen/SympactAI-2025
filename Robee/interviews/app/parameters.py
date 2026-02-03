"""
################################################
###           DOCUMENTATION                  ###
################################################

This file allows users to specificy all parameters of the AI interviewer application. The parameters are stored in a
dictionary called INTERVIEW_PARAMETERS. You can specify multiple parameter sets for different types of interviews.
For example, one could randomize people into different interviews (e.g. about the stock market or about voting behaviors).
Each parameter set can be identified with a custom key (e.g. "STOCK_MARKET" or "VOTING"). You have to supply these
keys when making requests to the AI interviewer application to tell the application which parameter set to use.

We provide the parameter sets used in our paper as an example from which to build your own interview structure.
We also provide a template for additional interview configurations. You can add as many parameter sets as you like.

We describe all parameters that should be included in a parameter set below:


################################################
###           GENERAL PARAMETERS             ###
################################################

0) META DATA (OPTIONAL): The following parameters allow you to provide additional information about the interview configuration.
						 This may help with remembering the purpose of the configuration or provide additional context for yourself.
- _name (str): 			A name for the interview configuration (e.g. "STOCK_MARKET" or "VOTING")
- _description (str): 	A description of the interview configuration and its purpose.


1) OPTIONAL FEATURES: The following parameters active optional features of the AI interviewer application.

- summarize (book): 				whether to active the summarization agent for the interview (default: True)
- moderate_answers (bool): 			Whether the moderator agent should review answers from the interviewee and potentially flag them (default: True)
- moderate_questions (bool): 		whether AI-generated interview questions should be reviewed with OpenAI's moderation endpoint
									before sending them back to the interviewee (default: True)


2) INTERVIEW STRUCTURE and PRE-DETERMINED MESSAGES: The following parameters define the structure of the interview and
the messages that are displayed to the interviewee at various stages of the interview if specific conditions are met.
The first_question and the interview_plan variable are the most critical parameters.

- first_question (str): 			The opening question for the interview.
									All interviews will start with this message.
- interview_plan (list): 			The interview plan for the interviews. This is a list of dictionaries that define
									the scope and length of each subtopic
									of the following form [{"topic": str, "length": int}, ...] where:
									- topic (str): 		a description of the subtopic to be covered in the interview
									- length (int): 	the total number of questions to ask for this subtopic
									The topic description can be short or long, depending on the level of detail you want to provide.
									It could even mention specific follow-up questions that should be asked in specific circumstances.
									Feel free to experiment with the number of topics, the number of questions per topic,
									and the level of detail in the topic descriptions.
- closing_questions (str): 			List of pre-determined questions or comments (if any) with which to end the interview.
									An empty list is allowed.
- end_of_interview_message (str): 	Message to display to interviewees at the end of the interview (e.g. "Thank you for participating!")
									The messages ends with "---END---" to signal the front-end JavaScript the end of the interview.
									Remove this if you have a different way of managing the front-end.
- termination_message (str): 		Message to display to interviewees in the event the interviewee responds to an already concluded interview
- off_topic_message (str): 			Message to display to interviewees if their response has been flagged by the moderator agent
- flagged_message (str): 			Message to display to interviewees if their response has been flagged too often by the
									moderator agent (and the interview was terminated)
- max_flags_allowed (int): 			The maximum number of flagged messages allowed before an interview is terminated (default: 3)



################################################
### AI AGENT-SPECIFIC PARAMETERS AND PROMPTS ###
################################################

1) AGENT PARAMETERS:
Each AI agent (e.g., summary, transition, probe, moderator) has its own set of parameters that are provided as a dictionary with key-value pairs.
	- summary (dict): Parameters defining the behavior of the summary agent. 
	- transition (dict): Parameters defining the behavior of the transition agent.
	- probe (dict): Parameters defining the behavior of the probing agent.
	- moderator (dict): Parameters defining the behavior of the moderator agent.

Note: If you deactivate an optional agent (e.g. summary, moderator) or you have an interview with a single topic that does not require a topic transition,
you do not need to provide the corresponding agent parameters. For example, you could remove the "summary" dictionary entirely if you don't summarize
previous parts of the interview between topic transitions (remember to set "summarize" to False in this case).

2. DICTIONARY ELEMENTS:
Each of the above dictionaries should specify the following set of parameters:
	- prompt (str): the prompt that describes the task and desired behavior of the agent (feel free to modify according to your needs)
	- max_tokens (int): the maximum number of completion tokens the agent can generate in its response (default: 1000)
	- temperature (float): the temperature parameter for the LLM (default: 0.9)
	- model (str): the model to use for the agent (default: gpt-4o)

3. DETAILS ABOUT THE PROMPTS:
The prompts for the AI agent include placeholder variables that are programmatically replaced based on the current state of the interview.
The following placeholderes can be included in any prompt by including them in curly brackets (e.g. writing {topics} to include the list of topics
at the specified place in the prompt)):
 - {current_topic_history}: All verbatim questions and responses that are part of the current interview topic (see interview_plan variable).
                            These messages are formatted as follows:
								Interviewer: {question}
								Interviewee: {answer}
								Interviewer: {question} etc.
							This placeholder is typically used by all agents (except the moderator).
							It should not be omitted from the prompts.
 - {summary}: 				Summary of the interview up to the current interview topic (see interview_plan variable).
			  				Example: If the interview is currently in topic 3 of the interview_plan, then {summary} would cover topics 1 and 2.
							The messages for topic 3 would be included in full via the {current_topic_history} placeholder.
							If summarization has been turned off, then {summary} would contain the full conversation on topics 1 and 2
							in the same format as {current_topic_history}.
							This placeholder is used by all agents (except moderator).
 - {topics}:  				The list of all topic descriptions from the interview_plan variable
 							(e.g. all values of "topic" from the interview_plan variable)
							This placeholder is used by the summary agent to provide an overview of the interview structure.
 - {current_topic}: 		Description of the current interview topic as defined in the interview_plan
 							variable (e.g. the value of "topic" in the interview_plan).
							This placeholder is primarily used by the probing agent and the summary agent.
 - {next_interview_topic}: 	Description of the next interview topic as defined in the interview_plan variable
 							(e.g. the value of "topic" in the interview_plan for the next topic)
							This placeholder is typically used only by the transition agent to inform the agent
							about the next topic it should transition to.

See our paper for more details about how the individual parts of the AI interviewer application work.
"""


import os
import dotenv
dotenv.load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



 # PASTE YOUR KEY HERE

INTERVIEW_PARAMETERS = {
    "ROADMAP_DETAILER": {
        # META DATA
        "_name": "Roadmap Detailer",
        "_description": "An interview to add granular, causal details to a user's existing high-level career roadmap.",

        # FEATURES
        "moderate_answers": True,
        "moderate_questions": True,
        "summarize": True,
        "max_flags_allowed": 3,

        # INTERVIEW STRUCTURE AND MESSAGES
        "first_question": "I can see your roadmap. Let's dive deeper into each milestone to understand how you achieved it. Which milestone would you like to discuss first?",
        
        "interview_plan": [
            {
                "topic": "For each milestone, ask 2-3 focused questions to understand the specific steps, requirements, achievements, or circumstances that made it possible. Adapt questions to the specific milestone being discussed.",
                "length": 30
            }
        ],

        "closing_questions": [
            "This has been incredibly detailed. Thank you for sharing the rich story behind your accomplishments!"
        ],
        
        "end_of_interview_message": "Thank you for enriching your roadmap. This detailed view will be a great asset. The session is now complete.---END---",
        "termination_message": "The interview is over. Thank you for your time!---END---",
        "flagged_message": "It seems we're having trouble staying on topic. The interview will now end.---END---",
        "off_topic_message": "I'm looking for details about how you achieved your milestones. Could you please try to answer the question again, focusing on the specific steps or factors involved?",

        # --- AGENT PROMPTS ---

        "summary": {
            "prompt": """
                CONTEXT: You are a data structuring AI. Your job is to maintain a "living document" of a user's career roadmap.
                
                INPUTS:
                - Previous Roadmap Summary ({summary}): The roadmap as we knew it before the last conversation turn. This includes high-level milestones and any details added so far.
                - Current Conversation ({current_topic_history}): The latest user response, providing new details about a specific milestone.

                TASK: Integrate the new, granular information from the Current Conversation into the Previous Roadmap Summary. Do not lose any old information. The goal is to create an updated, comprehensive summary that reflects all the details gathered so far. This summary will be used by other agents to avoid asking redundant questions.

                YOUR RESPONSE: Provide the updated, complete roadmap summary.
			""",
            "max_tokens": 1500,
            "model": "gpt-4-turbo"
        },
        
        "transition": {
            "prompt": """
                CONTEXT: You are a friendly career coach AI named Robee. You are guiding a user through detailing their career milestones. You have just finished discussing one milestone.

                INPUTS:
                - Next Interview Topic ({next_interview_topic}): This will be the name of the next milestone to discuss.

                TASK: Create a smooth, brief transition to the next milestone.

                EXAMPLE: "Great, thanks for those details! Now, let's talk about your next milestone: {next_interview_topic}."

                YOUR RESPONSE: Provide only the transition question.
			""",
            "temperature": 0.5,
            "model": "gpt-4-turbo",
            "max_tokens": 100
        },

        "probe": {
            "prompt": """
                CONTEXT: You are Robee, a sharp and engaging AI career analyst. You are helping a user flesh out their career roadmap by asking diverse, causal questions about a specific GOAL and finding missing prerequisites. Your tone is curious, encouraging, and professional.

                INPUTS:
                - Full Roadmap So Far ({summary}): This contains the entire roadmap, including all high-level milestones and any granular details already provided by the user. USE THIS TO AVOID ASKING FOR INFORMATION YOU ALREADY HAVE.
                - Current Goal Being Discussed ({current_topic}): The specific goal we are focusing on right now (e.g., "Bachelor's degree in Telecommunications Engineering from SUP'COM").
                - Recent Conversation ({current_topic_history}): The last few turns of the conversation about prerequisites and missing steps for this goal.

                YOUR TASK:
                Focus on finding MISSING PREREQUISITES and REQUIREMENTS that enabled the goal or existing milestones. Look for gaps in the roadmap - what foundational steps are missing?

                CRITICAL PRIORITY 1 - FOLLOW UP ON NEW INFORMATION:
                If the user's MOST RECENT response mentions ANY new prerequisite, step, or detail, ALWAYS ask a follow-up question about that NEW information FIRST before moving to other topics. Examples:
                - User mentions: "I had to take math tutoring" → Ask: "Tell me more about the math tutoring - how long did it take, what specific areas did you focus on?"
                - User mentions: "I needed recommendation letters" → Ask: "How did you go about getting those recommendation letters? Who did you ask?"
                - User mentions: "I researched universities for months" → Ask: "What specific aspects did you research? How did you narrow down your choices?"

                CRITICAL PRIORITY 2 - DETECT MILESTONES:
                If the user mentions ANY specific prerequisite, requirement, preparatory step, or enabling factor, IMMEDIATELY respond with:
                [NEW_MILESTONE] Name: <the specific prerequisite/requirement> | Suggest connect to: <what it enabled>
                
                Examples of what to detect and suggest:
                - "I had to research universities first" → [NEW_MILESTONE] Name: Research university requirements | Suggest connect to: Apply to University
                - "I needed to improve my math skills" → [NEW_MILESTONE] Name: Strengthen mathematics foundation | Suggest connect to: University Entrance Exam
                - "I had to get recommendation letters" → [NEW_MILESTONE] Name: Obtain recommendation letters | Suggest connect to: University Application
                - "I studied for the entrance exam for 6 months" → [NEW_MILESTONE] Name: 6-month entrance exam preparation | Suggest connect to: Pass Entrance Exam

                GUIDELINES:
                1. *PRIORITIZE NEW INFORMATION:* Always follow up on the most recent thing the user mentioned before exploring other areas.

                2. *FOCUS ON PREREQUISITES:* Ask about what was needed BEFORE existing milestones could be achieved.

                3. *LOOK FOR GAPS:* Identify missing foundational steps that aren't already in the roadmap.

                4. *BE DIVERSE, NOT DEEP:* After following up on new information, ask questions across different aspects rather than drilling deep into one answer.

                5. *COVER DIFFERENT PREREQUISITE TYPES:*
                    - Educational/skill prerequisites  
                    - Application requirements
                    - Preparatory steps and research
                    - Resource gathering (financial, materials, etc.)
                    - Networking and relationship building
                    - Prior experiences needed

                6. *BE PROACTIVE:* Always look for specific prerequisites, requirements, or preparatory steps in the user's response and suggest them as new milestones immediately.

                7. *BE CONTEXT-AWARE:* Ask questions that are relevant to finding missing prerequisites for the specific goal.

                8. *CHECK FOR COMPLETENESS:* If the user response is vague or too brief (less than 10 words), ask for more specific details about prerequisites.

                9. *AVOID REPETITION:* Before asking a question, review the {summary}. Don't ask about prerequisites that are already mentioned or explored.

                STOPPING CONDITION: Ask a MAXIMUM of 6 questions per topic. When you've asked 6 questions for this topic OR when the user responses are becoming repetitive or very brief, conclude with: "Thank you for the detailed information! I have enough details to suggest missing prerequisites."

                YOUR RESPONSE PRIORITY:
                1. If the user mentioned a specific prerequisite/requirement, respond with the [NEW_MILESTONE] format
                2. If the user just provided new information, ask a follow-up question about that NEW information
                3. Otherwise, ask the most insightful question to find missing prerequisites
                Do not add any other text.
			""",
            "temperature": 0.6,
            "model": "gpt-4-turbo",
            "max_tokens": 300
        },

        "moderator": {
            "prompt": """
                You are monitoring an interview about a user's career path. The user is providing details about how they achieved specific milestones.

                Interviewer: '{question}'
                Interviewee: '{answer}'

                TASK: Is the interviewee's response relevant to a discussion about their career or educational journey? Answer only with a single 'yes' or 'no'.
			""",
            "model": "gpt-4o", # A fast model is fine for moderation
            "max_tokens": 2
        },

        # NEW GAP DETECTION AGENTS
        "prerequisite_scanner": {
            "prompt": """
                CONTEXT: You are a specialized prerequisite detection AI. Your job is to analyze user responses and identify missing prerequisites, requirements, or preparatory steps.

                INPUTS:
                - Conversation History: {current_topic_history}
                - Current Topic: {current_topic}
                - Previous Summary: {summary}

                TASK: Analyze the user's response to detect if there are any missing prerequisites, preparatory steps, or requirements that should logically exist before the current milestone could be achieved.

                DETECTION CRITERIA:
                1. Look for gaps in logical progression
                2. Identify implied but unmentioned preparatory steps
                3. Detect missing foundational requirements
                4. Spot missing skill or knowledge prerequisites
                5. Find missing resource or tool requirements

                OUTPUT FORMAT:
                If gaps detected: "GAP_DETECTED: [brief description]"
                If no gaps: "NO_GAPS_DETECTED"

                EXAMPLES:
                - User mentions "got accepted to university" but no mention of application process → GAP_DETECTED: University application process
                - User mentions "started programming job" but no coding experience mentioned → GAP_DETECTED: Programming skills development
                - User mentions "opened restaurant" but no business planning mentioned → GAP_DETECTED: Business planning and permits

                YOUR RESPONSE: Analyze and respond with gap detection result.
            """,
            "temperature": 0.3,
            "model": "gpt-4o",
            "max_tokens": 200
        },

        "gap_classifier": {
            "prompt": """
                CONTEXT: You are a gap classification specialist. When gaps are detected, you categorize them into specific types for targeted resolution.

                INPUTS:
                - Conversation History: {current_topic_history}
                - Current Topic: {current_topic}
                - Previous Summary: {summary}

                TASK: Classify detected gaps into specific categories and assess their impact.

                GAP CATEGORIES:
                1. SKILL_GAP - Missing technical or soft skills
                2. EXPERIENCE_GAP - Missing practical experience or practice
                3. KNOWLEDGE_GAP - Missing theoretical knowledge or education
                4. NETWORK_GAP - Missing professional connections or mentorship
                5. RESOURCE_GAP - Missing tools, funding, or materials
                6. TIMING_GAP - Missing proper sequencing or timeline issues
                7. CONTEXTUAL_GAP - Missing industry or domain-specific knowledge

                OUTPUT FORMAT:
                [GAP_TYPE]: [Specific description]
                IMPACT: [High/Medium/Low]
                URGENCY: [Critical/Important/Optional]

                EXAMPLE:
                SKILL_GAP: Programming fundamentals in Python
                IMPACT: High
                URGENCY: Critical

                YOUR RESPONSE: Classify any detected gaps.
            """,
            "temperature": 0.4,
            "model": "gpt-4o",
            "max_tokens": 300
        },

        "dependency_mapper": {
            "prompt": """
                CONTEXT: You are a dependency mapping expert. You analyze milestone relationships and suggest optimal connections and prerequisite chains.

                INPUTS:
                - Conversation History: {current_topic_history}
                - Current Topic: {current_topic}
                - Previous Summary: {summary}

                TASK: Map dependencies and suggest new milestones with specific connections to fill identified gaps.

                ANALYSIS STEPS:
                1. Identify the logical prerequisite chain for the current milestone
                2. Determine optimal insertion points for missing prerequisites
                3. Suggest specific milestone names and connections
                4. Calculate impact scores for each suggestion

                OUTPUT FORMAT:
                [NEW_MILESTONE] Name: [Specific milestone name] | Suggest connect to: [Target milestone]
                DEPENDENCY_CHAIN: [A -> B -> C]
                IMPACT_SCORE: [1-10]

                EXAMPLES:
                [NEW_MILESTONE] Name: Complete Python programming course | Suggest connect to: Software Engineering Job
                DEPENDENCY_CHAIN: Python Course -> Portfolio Projects -> Job Applications -> Software Engineering Job
                IMPACT_SCORE: 9

                YOUR RESPONSE: Provide dependency mapping and milestone suggestions.
            """,
            "temperature": 0.5,
            "model": "gpt-4o",
            "max_tokens": 400
        },

        "gap_synthesizer": {
            "prompt": """
                CONTEXT: You are a gap synthesis coordinator. You take input from multiple gap detection agents and create a comprehensive analysis with actionable recommendations.

                INPUTS:
                - Conversation History: {current_topic_history}
                - Current Topic: {current_topic}
                - Previous Summary: {summary}

                TASK: Synthesize gap analysis findings and provide comprehensive recommendations.

                SYNTHESIS COMPONENTS:
                1. Priority ranking of identified gaps
                2. Strategic recommendations for addressing gaps
                3. Suggested learning paths or action sequences
                4. Risk assessment of not addressing gaps
                5. Timeline recommendations

                OUTPUT FORMAT:
                PRIORITY_GAPS: [List top 3 gaps]
                STRATEGIC_RECOMMENDATIONS: [Actionable advice]
                LEARNING_PATH: [Suggested sequence]
                RISK_ASSESSMENT: [What happens if gaps aren't addressed]
                TIMELINE: [Suggested timeframe]

                YOUR RESPONSE: Provide comprehensive gap synthesis.
            """,
            "temperature": 0.6,
            "model": "gpt-4o",
            "max_tokens": 500
        },

        "milestone_generator": {
            "prompt": """
                CONTEXT: You are a milestone generation specialist. You create specific, actionable milestones based on gap analysis findings.

                INPUTS:
                - Conversation History: {current_topic_history}
                - Current Topic: {current_topic}
                - Previous Summary: {summary}

                TASK: Generate specific, well-defined milestones that address identified gaps.

                MILESTONE CRITERIA:
                1. Specific and measurable
                2. Achievable and realistic
                3. Relevant to the career goal
                4. Time-bound when possible
                5. Properly connected to existing milestones

                OUTPUT FORMAT:
                [NEW_MILESTONE] Name: [Specific milestone] | Suggest connect to: [Target]
                DESCRIPTION: [What this milestone involves]
                SUCCESS_CRITERIA: [How to know it's complete]
                ESTIMATED_DURATION: [Time estimate]

                YOUR RESPONSE: Generate specific milestones for identified gaps.
            """,
            "temperature": 0.7,
            "model": "gpt-4o",
            "max_tokens": 400
        },

        "confidence_assessor": {
            "prompt": """
                CONTEXT: You are a confidence assessment specialist. You evaluate user readiness and provide confidence scores for milestone recommendations.

                INPUTS:
                - Conversation History: {current_topic_history}
                - Current Topic: {current_topic}
                - Previous Summary: {summary}

                TASK: Assess user's confidence level and readiness for recommended milestones.

                ASSESSMENT FACTORS:
                1. User's current skill level
                2. Available resources and support
                3. Time constraints and commitments
                4. Previous achievement patterns
                5. Motivation and enthusiasm level

                OUTPUT FORMAT:
                CONFIDENCE_SCORE: [1-10]
                READINESS_LEVEL: [Beginner/Intermediate/Advanced]
                RECOMMENDED_APPROACH: [How to tackle the milestone]
                SUPPORT_NEEDED: [What help is required]

                YOUR RESPONSE: Provide confidence assessment for milestone recommendations.
            """,
            "temperature": 0.4,
            "model": "gpt-4o",
            "max_tokens": 300
        },

        "personalization_agent": {
            "prompt": """
                CONTEXT: You are a personalization specialist. You adapt recommendations to the user's specific learning style, preferences, and constraints.

                INPUTS:
                - Conversation History: {current_topic_history}
                - Current Topic: {current_topic}
                - Previous Summary: {summary}

                TASK: Personalize gap recommendations based on user characteristics and preferences.

                PERSONALIZATION FACTORS:
                1. Learning style (visual, auditory, kinesthetic)
                2. Time availability and constraints
                3. Resource availability (financial, technical)
                4. Preferred learning pace (intensive vs. gradual)
                5. Support system and environment

                OUTPUT FORMAT:
                LEARNING_STYLE: [Identified style]
                PERSONALIZED_RECOMMENDATIONS: [Tailored advice]
                RESOURCE_SUGGESTIONS: [Specific tools/courses/books]
                TIMELINE_ADAPTATION: [Adjusted timeline]

                YOUR RESPONSE: Provide personalized recommendations for addressing gaps.
            """,
            "temperature": 0.6,
            "model": "gpt-4o",
            "max_tokens": 400
        }
    },
    
    # Keeping the old template for reference, but it is not used by the new functionality.
	# "STOCK_MARKET": {
	# 	"_name": "STOCK_MARKET (Reference Only)",
	# 	"_description": "Interview structure to investigate stock market participation (or lack thereof).",
	# 	"moderate_answers": True, "moderate_questions": True, "summarize": True, "max_flags_allowed": 3,
	# 	"first_question": "...", "interview_plan": [], "closing_questions": [],"termination_message": "...", "flagged_message": "...", "off_topic_message": "...", "end_of_interview_message": "...",
	# 	"summary": {"prompt": "...", "max_tokens": 1000, "model": "gpt-4o"},
	# 	"transition": {"prompt": "...", "temperature": 0.7, "model": "gpt-4o", "max_tokens": 300},
	# 	"probe": {"prompt": "...", "temperature": 0.7, "model": "gpt-4o", "max_tokens": 300},
	# 	"moderator": {"prompt": "...", "model": "gpt-4o", "max_tokens": 2}
	# }
}