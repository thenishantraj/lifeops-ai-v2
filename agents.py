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

# Tools in Global Scope
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
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    
    def _create_agent(self, role, goal, backstory, tools=None, allow_delegation=False):
        """Helper method to create agents with consistent configuration"""
        if tools is None:
            tools = []
            
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=allow_delegation,
            llm=self.llm,  # Explicitly use Gemini LLM
            tools=tools
        )

    def create_health_agent(self) -> Agent:
        return self._create_agent(
            role="Health and Wellness Expert",
            goal="Optimize health and wellness through personalized recommendations",
            backstory="Dr. Maya Patel, a holistic health specialist with 15 years of experience integrating modern medicine with wellness practices.",
            tools=[schedule_action_item, set_reminder]
        )
    
    def create_finance_agent(self) -> Agent:
        return self._create_agent(
            role="Personal Finance Advisor",
            goal="Manage finances effectively and build wealth",
            backstory="Alex Chen, a CFA with expertise in personal finance, budgeting, and investment strategies for millennials.",
            tools=[schedule_action_item]
        )
    
    def create_study_agent(self) -> Agent:
        return self._create_agent(
            role="Learning Specialist",
            goal="Optimize study habits and academic performance",
            backstory="Prof. James Wilson, a cognitive scientist specializing in learning techniques, memory retention, and exam preparation strategies.",
            tools=[schedule_action_item, set_reminder]
        )
    
    def create_life_coordinator(self) -> Agent:
        return self._create_agent(
            role="Life Coordinator",
            goal="Orchestrate life domains for optimal balance and productivity",
            backstory="Sophia Williams, a former project manager turned life coach who specializes in integrating health, finance, and study goals.",
            tools=[validate_cross_domain, schedule_action_item],
            allow_delegation=True
        )

    def get_all_agents(self) -> List[Agent]:
        return [
            self.create_health_agent(),
            self.create_finance_agent(),
            self.create_study_agent(),
            self.create_life_coordinator()
        ]
