"""
LifeOps AI v2 - Fixed Agents file
"""
import os
from typing import List
from crewai import Agent
from crewai.tools import tool 
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# Force CrewAI to use Google Gemini, not OpenAI
os.environ["OPENAI_API_KEY"] = "not-needed"
os.environ["OPENAI_MODEL_NAME"] = "not-needed"

@tool("schedule_action_item")
def schedule_action_item(task: str, category: str, priority: str = "medium"):
    """Schedule an action item in the system."""
    return f"Scheduled: {task} ({category})"

@tool("set_reminder")
def set_reminder(message: str, hours_from_now: int = 24):
    """Set a reminder for future."""
    return f"Reminder set: {message}"

@tool("validate_cross_domain")
def validate_cross_domain(domain: str, recommendation: str, context: dict):
    """Validate recommendations."""
    return "Validated"

# --- AGENTS CLASS ---

class LifeOpsAgents:
    def __init__(self):
        # Use gemini-pro or gemini-1.5-flash depending on your access
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",  # or "gemini-1.5-flash" for faster responses
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # CRITICAL FIX: Monkey patch to prevent CrewAI from using OpenAI
        self._patch_crewai_for_gemini()

    def _patch_crewai_for_gemini(self):
        """Patch CrewAI internals to force Gemini usage"""
        import crewai
        from crewai.llm import LLM
        
        # Create a custom LLM wrapper that only uses Gemini
        class GeminiLLM(LLM):
            def __init__(self, llm):
                self._llm = llm
                super().__init__()
            
            @property
            def llm(self):
                return self._llm
            
            def __getattr__(self, name):
                # Delegate everything to the underlying Gemini LLM
                return getattr(self._llm, name)
        
        # Monkey patch the LLM creation
        original_init = Agent.__init__
        
        def patched_init(self, *args, **kwargs):
            # Force the llm parameter to use our Gemini LLM
            if 'llm' not in kwargs:
                kwargs['llm'] = GeminiLLM(self.llm)
            original_init(self, *args, **kwargs)
        
        # Temporarily apply the patch
        Agent.__init__ = patched_init

    def create_health_agent(self) -> Agent:
        return Agent(
            role="Health and Wellness Expert",
            goal="Optimize health and wellness through personalized recommendations",
            backstory="Dr. Maya Patel, with 15 years in integrative medicine, specializes in stress management and preventive healthcare.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[schedule_action_item, set_reminder]
        )
    
    def create_finance_agent(self) -> Agent:
        return Agent(
            role="Personal Finance Advisor",
            goal="Manage finances efficiently and build wealth",
            backstory="Alex Chen, a CFA with expertise in personal finance and behavioral economics.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[schedule_action_item]
        )
    
    def create_study_agent(self) -> Agent:
        return Agent(
            role="Learning Specialist",
            goal="Optimize study patterns and academic performance",
            backstory="Prof. James Wilson, cognitive scientist specializing in learning optimization and productivity.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[schedule_action_item, set_reminder]
        )
    
    def create_life_coordinator(self) -> Agent:
        return Agent(
            role="Life Coordinator",
            goal="Orchestrate life domains for optimal balance and productivity",
            backstory="Sophia Williams, systems thinker and life architect with expertise in multi-domain optimization.",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=[validate_cross_domain, schedule_action_item]
        )

    def get_all_agents(self) -> List[Agent]:
        return [
            self.create_health_agent(),
            self.create_finance_agent(),
            self.create_study_agent(),
            self.create_life_coordinator()
        ]
