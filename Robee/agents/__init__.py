"""
Robee Agent System - Modular agent-based architecture for career roadmap management

This package contains specialized agents for different aspects of the Robee pipeline:
- Interface Agent: UI management and user interaction
- Safety Agent: Content moderation and safety monitoring
- Roadmap Structure Agent: Data structure and graph management
- Gap Filler Agent: Gap detection and milestone suggestion
- Causality Structure Verifier Agent: Causal relationship verification
- Orchestrator Agent: Workflow coordination and agent management
- Interview Management Agent: Interview workflow and conversation management
- LLM Communication Agent: API communication with language models
- Vote Processing Agent: Milestone voting and approval workflow
"""

from .interface_agent import InterfaceAgent, SessionStateManager, VoteProcessor, UIManager
from .safety_agent import SafetyAgent, ContentModerator, SafetyMonitor, ViolationTracker
from .roadmap_structure_agent import RoadmapStructureAgent, DataStructureManager, AdjacencyMatrixManager, MilestoneManager
from .gap_filler_agent import GapFillerAgent, GapDetector, PatternAnalyzer, MilestoneSuggester
from .causality_structure_verifier_agent import CausalityStructureVerifierAgent, RelationshipVerifier, StructureAnalyzer, NetworkValidator
from .orchestrator_agent import OrchestratorAgent 
# from .llm_communication_agent import LLMCommunicationAgent, APIManager, PromptOptimizer, ResponseProcessor, CostTracker
from .vote_processing_agent import VoteProcessingAgent, VoteTracker, ConsensusEngine, ApprovalManager, VotingAnalytics
from .counterfactual_agent import CounterfactualAgent, ScenarioGenerator, ImpactAnalyzer, AlternativePathFinder, DependencyAnalyzer
from .cva_agent import CVAAgent, ConfounderDetector, CollaboratorAnalyzer, NetworkMapper, StrategicPartnershipFinder
from .milestone_generation_agent import MilestoneGenerationAgent, MilestoneSuggestion, MilestoneParser, TaxonomyClassifier, ImportanceAnalyzer, ConnectionSuggester
# from .roadmap_extraction_agent import RoadmapExtractionAgent, MilestoneExtractor, DependencyAnalyzer, RoadmapClassifier, RoadmapGenerator
# from .data_persistence_agent import DataPersistenceAgent, FileBackend, DynamoDBBackend, StorageManager, SessionDataManager, BackupManager, ConnectionManager
# from .error_handling_agent import ErrorHandlingAgent, ErrorLogger, RecoveryManager, DegradationManager
# from .network_analysis_agent import NetworkAnalysisAgent, CentralityCalculator, CommunityDetector, PathAnalyzer
from .summarization_agent import SummarizationAgent
from .transcription_agent import TranscriptionAgent, AudioProcessor, SpeechRecognizer, SpeakerIdentifier
from .milestone_refinement_agent import MilestoneRefinementAgent, MilestoneValidator, DependencyOptimizer, DescriptionEnhancer

__all__ = [
    # Main Agent Classes
    'InterfaceAgent',
    'SafetyAgent', 
    'RoadmapStructureAgent',
    'GapFillerAgent',
    'CausalityStructureVerifierAgent',
    'OrchestratorAgent',
    'InterviewManagementAgent',
    'LLMCommunicationAgent',
    'VoteProcessingAgent',
    'CounterfactualAgent',
    'CVAAgent',
    'InterventionAnalysisAgent',
    'MilestoneGenerationAgent',
    'RoadmapExtractionAgent',
    'DataPersistenceAgent',
    'ErrorHandlingAgent',
    'NetworkAnalysisAgent',
    'SummarizationAgent',
    'TranscriptionAgent',
    'MilestoneRefinementAgent',
    
    # Supporting Classes - Interface Agent
    'SessionStateManager',
    'VoteProcessor', 
    'UIManager',
    
    # Supporting Classes - Safety Agent
    'ContentModerator',
    'SafetyMonitor',
    'ViolationTracker',
    
    # Supporting Classes - Roadmap Structure Agent
    'DataStructureManager',
    'AdjacencyMatrixManager', 
    'MilestoneManager',
    
    # Supporting Classes - Gap Filler Agent
    'GapDetector',
    'PatternAnalyzer',
    'MilestoneSuggester',
    
    # Supporting Classes - Causality Structure Verifier Agent
    'RelationshipVerifier',
    'StructureAnalyzer',
    'NetworkValidator',
    
    # Supporting Classes - Orchestrator Agent
    'OrchestratorAgent',
    
    # Supporting Classes - Interview Management Agent
    'ConversationManager',
    'QuestionGenerator',
    'ResponseGenerator',
    'InterviewTracker',
    
    # Supporting Classes - LLM Communication Agent
    'APIManager',
    'PromptOptimizer',
    'ResponseProcessor',
    'CostTracker',
    
    # Supporting Classes - Vote Processing Agent
    'VoteTracker',
    'ConsensusEngine',
    'ApprovalManager',
    'VotingAnalytics',
    
    # Supporting Classes - Counterfactual Agent
    'CounterfactualAnalyzer',
    'ScenarioGenerator',
    'OutcomePredictor',
    
    # Supporting Classes - CVA Agent
    'CausalVariableAnalyzer',
    'VariableTracker',
    'EffectMeasurer',
    
    # Supporting Classes - Intervention Analysis Agent
    'InterventionPlanner',
    'ImpactAnalyzer',
    'StrategyOptimizer',
    
    # Supporting Classes - Milestone Generation Agent
    'ConversationAnalyzer',
    'MilestoneExtractor',
    'TaxonomyClassifier',
    
    # Supporting Classes - Roadmap Extraction Agent
    'TextAnalyzer',
    'MilestoneExtractorFromText',
    'RoadmapClassifier',
    
    # Supporting Classes - Data Persistence Agent
    'FileBackend',
    'DynamoDBBackend',
    'SessionManager',
    
    # Supporting Classes - Error Handling Agent
    'ErrorLogger',
    'RecoveryManager',
    'DegradationManager',
    
    # Supporting Classes - Network Analysis Agent
    'CentralityCalculator',
    'CommunityDetector',
    'PathAnalyzer',
    
    # Supporting Classes - Summarization Agent
    'TextProcessor',
    'ConversationAnalyzer',
    'ContentExtractor',
    
    # Supporting Classes - Transcription Agent
    'AudioProcessor',
    'SpeechRecognizer',
    'SpeakerIdentifier',
    
    # Supporting Classes - Milestone Refinement Agent
    'MilestoneValidator',
    'DependencyOptimizer',
    'DescriptionEnhancer'
]

# Agent factory for easy instantiation
class AgentFactory:
    """Factory class for creating and configuring agents"""
    
    @staticmethod
    def create_interface_agent():
        """Create and configure Interface Agent"""
        return InterfaceAgent()
        
    @staticmethod
    def create_safety_agent():
        """Create and configure Safety Agent"""
        return SafetyAgent()
        
    @staticmethod
    def create_roadmap_structure_agent():
        """Create and configure Roadmap Structure Agent"""
        return RoadmapStructureAgent()
        
    @staticmethod
    def create_gap_filler_agent():
        """Create and configure Gap Filler Agent"""
        return GapFillerAgent()
        
    @staticmethod
    def create_causality_verifier_agent():
        """Create and configure Causality Structure Verifier Agent"""
        return CausalityStructureVerifierAgent()
        

    # @staticmethod
    # def create_llm_communication_agent(openai_key: str = None, groq_key: str = None):
    #     """Create and configure LLM Communication Agent"""
    #     return LLMCommunicationAgent(openai_key, groq_key)
        
    @staticmethod
    def create_vote_processing_agent():
        """Create and configure Vote Processing Agent"""
        return VoteProcessingAgent()
        
    @staticmethod
    def create_orchestrator_agent(agents_config: dict = None):
        """Create and configure Orchestrator Agent"""
        return OrchestratorAgent(agents_config or {})
        
    @staticmethod
    def create_complete_agent_system(openai_key: str = None, groq_key: str = None):
        """Create a complete agent system with all agents configured"""
        
        # Create individual agents
        agents = {
            'interface_agent': AgentFactory.create_interface_agent(),
            'safety_agent': AgentFactory.create_safety_agent(),
            'roadmap_structure_agent': AgentFactory.create_roadmap_structure_agent(),
            'gap_filler_agent': AgentFactory.create_gap_filler_agent(),
            'causality_verifier': AgentFactory.create_causality_verifier_agent(),
            'interview_agent': AgentFactory.create_interview_management_agent(openai_key),
            'llm_agent': AgentFactory.create_llm_communication_agent(openai_key, groq_key),
            'vote_agent': AgentFactory.create_vote_processing_agent(),
            'counterfactual_agent': CounterfactualAgent(),
            'cva_agent': CVAAgent(),
            'milestone_generation_agent': MilestoneGenerationAgent(),
            # 'roadmap_extraction_agent': RoadmapExtractionAgent(),
            # 'data_persistence_agent': DataPersistenceAgent(),
            # 'error_handling_agent': ErrorHandlingAgent(),
            # 'network_analysis_agent': NetworkAnalysisAgent(),
            'summarization_agent': SummarizationAgent(),
            'transcription_agent': TranscriptionAgent(),
            'milestone_refinement_agent': MilestoneRefinementAgent()
        }
        
        # Create agents configuration for orchestrator
        agents_config = {
            'available_agents': list(agents.keys()),
            'default_workflows': ['analysis_pipeline', 'interview_workflow', 'milestone_generation'],
            'communication_protocols': ['direct', 'async', 'pipeline']
        }
        
        # Create orchestrator with configuration
        orchestrator = AgentFactory.create_orchestrator_agent(agents_config)
        
        # Register all agents with orchestrator
        for agent_name, agent_instance in agents.items():
            orchestrator.register_agent(agent_name, agent_instance)
            
        return {
            'orchestrator': orchestrator,
            'agents': agents
        }

# Version information
__version__ = "1.0.0"
__author__ = "Robee Development Team"
__description__ = "Modular agent-based architecture for career roadmap management"
