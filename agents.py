"""
LifeOps AI v2 - Fixed Agents file
"""
import os
from typing import List
from crewai import Agent
# 1. CHANGE: langchain की जगह crewai.tools का use करें
from crewai.tools import tool 
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# 2. CHANGE: Tools को क्लास से बाहर (Global Scope) में रखें
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
        # 3. CHANGE: Model का नाम सही करें (gemini-pro या gemini-1.5-flash)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    def create_health_agent(self) -> Agent:
        return Agent(
            role="Health and Wellness Expert",
            goal="Optimize health...",
            backstory="Dr. Maya Patel...",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            # 4. CHANGE: Tools की लिस्ट में सीधे फंक्शन का नाम लिखें (self.tools नहीं)
            tools=[schedule_action_item, set_reminder]
        )
    
    def create_finance_agent(self) -> Agent:
        return Agent(
            role="Personal Finance Advisor",
            goal="Manage finances...",
            backstory="Alex Chen...",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[schedule_action_item]
        )
    
    def create_study_agent(self) -> Agent:
        return Agent(
            role="Learning Specialist",
            goal="Optimize study...",
            backstory="Prof. James Wilson...",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[schedule_action_item, set_reminder]
        )
    
    def create_life_coordinator(self) -> Agent:
        return Agent(
            role="Life Coordinator",
            goal="Orchestrate life domains...",
            backstory="Sophia Williams...",
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
