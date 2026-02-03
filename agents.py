"""
LifeOps AI v2 - Fixed Agents (No Tools Version to fix OpenAI Error)
"""
import os
from typing import List
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class LifeOpsAgents:
    def __init__(self):
        # Gemini Model Configuration
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    def create_health_agent(self) -> Agent:
        return Agent(
            role="Health and Wellness Expert",
            goal="Provide actionable health advice and medicine management strategies.",
            backstory="Dr. Maya Patel, a holistic health expert who focuses on stress management, sleep optimization, and practical medicine adherence.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            # Tools removed to prevent OpenAI embedding crashes
            tools=[] 
        )
    
    def create_finance_agent(self) -> Agent:
        return Agent(
            role="Personal Finance Advisor",
            goal="Create practical budgets and bill payment strategies.",
            backstory="Alex Chen, a pragmatic financial planner who specializes in student budgets, expense tracking, and savings optimization.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[]
        )
    
    def create_study_agent(self) -> Agent:
        return Agent(
            role="Learning Specialist",
            goal="Optimize study schedules and focus techniques.",
            backstory="Prof. James Wilson, an expert in cognitive science and productivity, known for Pomodoro techniques and exam preparation strategies.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[]
        )
    
    def create_life_coordinator(self) -> Agent:
        return Agent(
            role="Life Coordinator",
            goal="Integrate advice from all domains into a unified plan.",
            backstory="Sophia Williams, a master strategist who resolves conflicts between health, finance, and study goals to create a balanced lifestyle.",
            verbose=True,
            allow_delegation=False, # Manual coordination handles this
            llm=self.llm,
            tools=[]
        )

    def get_all_agents(self) -> List[Agent]:
        return [
            self.create_health_agent(),
            self.create_finance_agent(),
            self.create_study_agent(),
            self.create_life_coordinator()
        ]
