"""
LifeOps AI v2 - Enhanced Agents with CrewAI and Validation Protocol
"""
import os
from typing import List, Optional
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai.tools import tool
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# --- TOOLS MOVED TO GLOBAL SCOPE TO FIX VALIDATION ERROR ---

@tool("schedule_action_item")
def schedule_action_item(task: str, category: str, priority: str = "medium"):
    """Schedule an action item in the system"""
    return f"Action item scheduled: {task} (Category: {category}, Priority: {priority})"

@tool("set_reminder")
def set_reminder(message: str, hours_from_now: int = 24):
    """Set a reminder for future"""
    reminder_time = datetime.now() + timedelta(hours=hours_from_now)
    return f"Reminder set for {reminder_time.strftime('%Y-%m-%d %H:%M')}: {message}"

@tool("validate_cross_domain")
def validate_cross_domain(domain: str, recommendation: str, context: dict):
    """Validate recommendations across domains for consistency"""
    # Mock validation logic
    validation_checks = {
        "conflict_check": "No conflicts detected",
        "resource_alignment": "Resources properly allocated",
        "time_feasibility": "Time requirements feasible"
    }
    return json.dumps({
        "domain": domain,
        "recommendation": recommendation[:100],
        "validation": validation_checks,
        "status": "APPROVED"
    })

# --- AGENTS CLASS ---

class LifeOpsAgents:
    """Container for all LifeOps AI v2 agents with CrewAI"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        # Removed self.tools initialization as tools are now global
        
    def create_health_agent(self) -> Agent:
        """Create the Health & Wellness Agent v2"""
        return Agent(
            role="Health and Wellness Expert with Medical Knowledge",
            goal="""Optimize user's physical and mental health through balanced routines,
                  stress management, sleep optimization, nutrition advice, and medicine tracking.""",
            backstory="""You are Dr. Maya Patel, a holistic health expert with 15 years of 
                       experience in preventive medicine and stress management. You combine 
                       Eastern wellness traditions with Western medical science to create 
                       sustainable health routines. You have additional expertise in 
                       medication management and treatment adherence.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=4,
            max_rpm=15,
            tools=[schedule_action_item, set_reminder]
        )
    
    def create_finance_agent(self) -> Agent:
        """Create the Personal Finance Agent v2"""
        return Agent(
            role="Personal Finance Advisor with Bill Management",
            goal="""Help users manage their finances effectively, create budgets, 
                  optimize expenses, build savings, track bills, and maintain quality of life.""",
            backstory="""You are Alex Chen, a certified financial planner who specializes 
                       in helping professionals balance ambition with financial stability. 
                       You've helped hundreds of clients achieve financial independence 
                       through smart budgeting and investment strategies. You now also 
                       specialize in automated bill tracking and expense prediction.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=4,
            max_rpm=15,
            tools=[schedule_action_item]
        )
    
    def create_study_agent(self) -> Agent:
        """Create the Learning & Productivity Agent v2"""
        return Agent(
            role="Learning and Productivity Specialist with Focus Techniques",
            goal="""Design effective study schedules, optimize learning techniques, 
                  manage time efficiently, prevent burnout, implement Pomodoro techniques,
                  and track study progress while achieving academic goals.""",
            backstory="""You are Professor James Wilson, an educational psychologist 
                       with expertise in cognitive science and time management. You've 
                       published research on optimal learning intervals and helped 
                       thousands of students achieve academic success without burnout.
                       You developed the 'Smart Pomodoro' technique that adapts break
                       times based on cognitive fatigue.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=4,
            max_rpm=15,
            tools=[schedule_action_item, set_reminder]
        )
    
    def create_life_coordinator(self) -> Agent:
        """Create the Master Life Coordinator Agent v2 with Validation Protocol"""
        return Agent(
            role="Life Operations Coordinator with Validation Protocol",
            goal="""Orchestrate all life domains (health, finance, study) to create 
                  a balanced, sustainable lifestyle. Make trade-off decisions when 
                  conflicts arise between domains. Validate all agent outputs using
                  the Gemini Validation Protocol before finalizing recommendations.""",
            backstory="""You are Sophia Williams, a renowned life strategist who 
                       integrates multiple life domains into cohesive strategies. 
                       With degrees in psychology, business, and education, you 
                       understand how different life areas interact. You developed
                       the 'Gemini Validation Protocol' that cross-checks all 
                       recommendations for consistency and feasibility.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            max_iter=6,
            max_rpm=20,
            tools=[validate_cross_domain, schedule_action_item]
        )
    
    def create_reflection_agent(self) -> Agent:
        """Create the Weekly Reflection Agent"""
        return Agent(
            role="Weekly Performance Analyst and Reflection Guide",
            goal="""Analyze weekly performance data, identify patterns, provide insights,
                  and suggest improvements for the upcoming week based on historical data.""",
            backstory="""You are Dr. Robert Chen, a data scientist and behavioral analyst
                       who specializes in personal productivity patterns. You've developed
                       algorithms that predict optimal routines based on historical
                       performance and environmental factors.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=3,
            max_rpm=10
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

