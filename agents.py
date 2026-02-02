"""
LifeOps AI v2 - Enhanced Multi-Agent System
COMPATIBLE VERSION for all LangChain versions
"""
import os
from typing import List, Any
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try different import locations for Tool
try:
    # For newer versions (0.1.x)
    from langchain.tools import Tool
except ImportError:
    try:
        # For older versions (0.0.x)
        from langchain.agents import Tool
    except ImportError:
        # Fallback - create our own Tool class
        from typing import Callable
        class Tool:
            def __init__(self, name: str, func: Callable, description: str):
                self.name = name
                self.func = func
                self.description = description

class LifeOpsTools:
    """Simulated tools for agent tool calling"""
    
    @staticmethod
    def validate_health_recommendation(recommendation: str) -> str:
        """Validate health recommendations for safety and practicality"""
        validation_checks = [
            "✓ Medical safety assessment",
            "✓ Time feasibility check",
            "✓ Resource availability",
            "✓ Personalization factor",
            "✓ Scientific backing verification"
        ]
        return f"VALIDATION COMPLETE:\n" + "\n".join(validation_checks)
    
    @staticmethod
    def cross_domain_analysis(recommendation: str, domains: List[str]) -> str:
        """Analyze impact of recommendations across life domains"""
        return f"CROSS-DOMAIN ANALYSIS:\n• Health impact: Moderate\n• Financial impact: Low\n• Study impact: High\n• Overall synergy: 85%"
    
    @staticmethod
    def check_schedule_feasibility(task: str, duration: int) -> str:
        """Check if a task fits into the user's schedule"""
        return f"SCHEDULE FEASIBILITY: Task '{task}' of {duration} minutes fits into daily routine with 90% probability"

class LifeOpsAgents:
    """Container for all LifeOps AI v2 agents with enhanced capabilities"""
    
    def __init__(self):
        # Initialize LLM with error handling
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.7,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
        except Exception as e:
            print(f"Warning: Could not initialize Google Gemini: {e}")
            # Fallback to a mock LLM for testing
            self.llm = None
            
        self.tools = LifeOpsTools()
        
    def create_health_agent(self) -> Agent:
        """Create the Enhanced Health & Wellness Agent with tool calling"""
        # Create tools list
        tools_list = []
        try:
            tools_list = [
                Tool(
                    name="HealthValidation",
                    func=self.tools.validate_health_recommendation,
                    description="Validates health recommendations for safety"
                )
            ]
        except:
            pass  # Continue without tools if Tool class not available
        
        return Agent(
            role="Health and Wellness Command Officer",
            goal="""Optimize user's physical and mental health through predictive analysis, 
                  stress management protocols, sleep optimization algorithms, and nutrition planning.
                  Generate actionable health directives with validation checks.""",
            backstory="""You are Dr. Maya V. Patel, Chief Medical Officer of LifeOps Command Center.
                       With 20 years in predictive health analytics and biometric integration,
                       you combine real-time health data with proactive wellness strategies.
                       You pioneered the 'Health Debt Index' metric for preventive care.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=5,
            max_rpm=20,
            tools=tools_list if tools_list else None
        )
    
    def create_finance_agent(self) -> Agent:
        """Create the Enhanced Personal Finance Agent with predictive analytics"""
        tools_list = []
        try:
            tools_list = [
                Tool(
                    name="CrossDomainAnalysis",
                    func=self.tools.cross_domain_analysis,
                    description="Analyzes financial decisions across life domains"
                )
            ]
        except:
            pass
        
        return Agent(
            role="Finance Operations Director",
            goal="""Execute financial optimization protocols, predictive budgeting, 
                  expense automation, and investment trajectory planning.
                  Generate financial directives with risk assessment.""",
            backstory="""You are Alex 'Quantum' Chen, Financial Strategist for high-net-worth individuals.
                       Former hedge fund analyst turned personal finance automation expert.
                       You developed the 'Financial Autopilot' system that manages budgets
                       while maximizing quality of life investments.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=5,
            max_rpm=20,
            tools=tools_list if tools_list else None
        )
    
    def create_study_agent(self) -> Agent:
        """Create the Enhanced Learning & Productivity Agent with cognitive science"""
        tools_list = []
        try:
            tools_list = [
                Tool(
                    name="ScheduleFeasibility",
                    func=self.tools.check_schedule_feasibility,
                    description="Checks if study plans fit into schedule"
                )
            ]
        except:
            pass
        
        return Agent(
            role="Cognitive Performance Architect",
            goal="""Design optimized learning schedules using spaced repetition algorithms,
                  cognitive load management, focus state optimization, and knowledge retention protocols.
                  Generate study directives with neuroscience backing.""",
            backstory="""You are Professor James 'Cortex' Wilson, Director of Neuro-Learning Labs.
                       Your research in cognitive enhancement through AI-personalized schedules
                       revolutionized modern education. You believe in 'minimum effective dose'
                       learning combined with maximum retention protocols.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=5,
            max_rpm=20,
            tools=tools_list if tools_list else None
        )
    
    def create_life_coordinator(self) -> Agent:
        """Create the Master Life Coordinator with Gemini Validation"""
        tools_list = []
        try:
            tools_list = [
                Tool(
                    name="ValidationProtocol",
                    func=self.tools.validate_health_recommendation,
                    description="Executes Gemini Validation Protocol"
                ),
                Tool(
                    name="StrategicAnalysis",
                    func=self.tools.cross_domain_analysis,
                    description="Strategic cross-domain impact analysis"
                )
            ]
        except:
            pass
        
        return Agent(
            role="Life Operations Commander",
            goal="""Orchestrate all life domains with military precision. Validate all agent outputs
                  for logical consistency. Make strategic trade-off decisions. Implement the
                  'Gemini Validation Protocol' to ensure recommendations are coherent, practical,
                  and synergistic across all domains.""",
            backstory="""You are Commander Sophia Williams, Chief of LifeOps Command Center.
                       With triple PhDs in Systems Theory, Behavioral Economics, and AI Ethics,
                       you've coordinated life optimization for Fortune 500 executives.
                       Your 'Gemini Protocol' ensures no single domain recommendation
                       compromises overall life harmony. You think in 4D optimization matrices.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            max_iter=8,
            max_rpm=30,
            tools=tools_list if tools_list else None
        )
    
    def create_reflection_agent(self) -> Agent:
        """Create the Weekly Reflection Agent for progress analysis"""
        return Agent(
            role="Progress Analytics & Reflection Director",
            goal="""Analyze weekly progress data, identify patterns, adjust strategies,
                  and generate insights for continuous improvement. Conduct Sunday Reviews.""",
            backstory="""You are Oracle-7, the reflection and learning module of LifeOps.
                       You process historical data to predict future optimal paths.
                       Your algorithms detect subtle patterns humans miss.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=4,
            max_rpm=15
        )
    
    def get_all_agents(self) -> List[Agent]:
        """Get all agents as a list"""
        return [
            self.create_health_agent(),
            self.create_finance_agent(),
            self.create_study_agent(),
            self.create_life_coordinator(),
            self.create_reflection_agent()
        ]
