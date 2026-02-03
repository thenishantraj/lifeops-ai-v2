"""
LifeOps AI v2 - Enhanced Tasks for CrewAI
"""
from crewai import Task
from typing import Dict, Any
from agents import LifeOpsAgents
from datetime import datetime
import json

class LifeOpsTasks:
    """Container for all LifeOps AI v2 tasks"""
    
    def __init__(self, user_context: Dict[str, Any]):
        self.user_context = user_context
        self.agents = LifeOpsAgents()
    
    def create_health_analysis_task(self) -> Task:
        """Task for health agent v2 with medicine tracking"""
        health_agent = self.agents.create_health_agent()
        
        return Task(
            description=f"""Analyze the user's health situation comprehensively with medicine awareness:
            
            User Context:
            - Stress Level: {self.user_context.get('stress_level', 'Not specified')}/10
            - Sleep Pattern: {self.user_context.get('sleep_hours', 'Not specified')} hours
            - Exercise Frequency: {self.user_context.get('exercise_frequency', 'Not specified')}
            - Current Medicines: {self.user_context.get('medicines', 'None specified')}
            - Problem: {self.user_context.get('problem', 'No specific problem mentioned')}
            
            Your Analysis Should Include:
            1. Current health risk assessment with medicine considerations
            2. Immediate stress reduction strategies
            3. Sleep optimization plan
            4. Exercise recommendations considering current energy levels
            5. Nutrition tips for stress management
            6. Medicine adherence strategies if applicable
            7. Action items for immediate implementation
            
            Use the schedule_action_item tool for key recommendations.
            Format your output with clear sections and actionable steps.
            """,
            agent=health_agent,
            expected_output="""A comprehensive health analysis with:
            1. Risk Assessment (Low/Medium/High)
            2. Immediate Actions (next 24 hours)
            3. Medicine Management Plan (if applicable)
            4. Weekly Health Schedule
            5. Action Items (use tool to schedule)
            6. Cross-domain Considerations
            """
        )
    
    def create_finance_analysis_task(self) -> Task:
        """Task for finance agent v2 with bill tracking"""
        finance_agent = self.agents.create_finance_agent()
        
        return Task(
            description=f"""Analyze the user's financial situation with bill management:
            
            User Context:
            - Monthly Budget: ${self.user_context.get('monthly_budget', 'Not specified')}
            - Current Expenses: ${self.user_context.get('current_expenses', 'Not specified')}
            - Financial Goals: {self.user_context.get('financial_goals', 'Not specified')}
            - Recurring Bills: {self.user_context.get('bills', 'None specified')}
            - Problem: {self.user_context.get('problem', 'No specific problem mentioned')}
            
            Your Analysis Should Include:
            1. Budget allocation with bill prioritization
            2. Expense optimization opportunities
            3. Automated bill payment strategy
            4. Savings strategy considering upcoming bills
            5. Investment recommendations for health/study
            6. Action items for financial tasks
            
            Use the schedule_action_item tool for key recommendations.
            Provide specific, actionable financial advice.
            """,
            agent=finance_agent,
            expected_output="""A detailed financial plan with:
            1. Budget Allocation with Bill Calendar
            2. Expense Optimization Tips
            3. Automated Financial Workflow
            4. Savings Strategy with Bill Buffer
            5. Action Items (use tool to schedule)
            6. Cross-domain Financial Implications
            """
        )
    
    def create_study_analysis_task(self) -> Task:
        """Task for study agent v2 with Pomodoro techniques"""
        study_agent = self.agents.create_study_agent()
        
        days_until_exam = self.user_context.get('days_until_exam', 0)
        exam_date = self.user_context.get('exam_date', 'Not specified')
        
        return Task(
            description=f"""Analyze the user's study situation with focus techniques:
            
            User Context:
            - Upcoming Exam: {exam_date} ({days_until_exam} days from now)
            - Current Study Hours: {self.user_context.get('current_study_hours', 'Not specified')}/day
            - Subjects/Topics: {self.user_context.get('subjects', 'Not specified')}
            - Current Focus Level: {self.user_context.get('focus_level', 'Not specified')}/10
            - Problem: {self.user_context.get('problem', 'No specific problem mentioned')}
            
            Your Analysis Should Include:
            1. Smart Pomodoro schedule (adaptive break times)
            2. Focus technique recommendations
            3. Burnout prevention with micro-breaks
            4. Resource optimization
            5. Progress tracking system
            6. Action items for study sessions
            
            Use the schedule_action_item and set_reminder tools.
            Create a realistic, sustainable study plan.
            """,
            agent=study_agent,
            expected_output="""A comprehensive study plan with:
            1. Smart Pomodoro Schedule
            2. Focus Technique Recommendations
            3. Adaptive Break Strategy
            4. Progress Tracking System
            5. Action Items (use tools to schedule)
            6. Cross-domain Considerations
            """
        )
    
    def create_life_coordination_task(self, health_output: str, finance_output: str, study_output: str) -> Task:
        """Master task v2 with Gemini Validation Protocol"""
        coordinator = self.agents.create_life_coordinator()
        
        return Task(
            description=f"""You are the Life Operations Coordinator with Gemini Validation Protocol. 
            
            MANDATORY: Before creating final plan, you MUST validate each domain's recommendations 
            using the validate_cross_domain tool to ensure consistency and feasibility.
            
            User's Primary Problem: {self.user_context.get('problem', 'General life optimization')}
            
            Domain Insights to Validate:
            
            HEALTH ANALYSIS:
            {health_output}
            
            FINANCE ANALYSIS:
            {finance_output}
            
            STUDY ANALYSIS:
            {study_output}
            
            Your Coordination Protocol:
            1. VALIDATE each domain output using the validation tool
            2. Identify conflicts between validated recommendations
            3. Make trade-off decisions with evidence
            4. Create unified schedule with time blocking
            5. Generate Priority Matrix (Urgent/Important)
            6. Schedule action items for key tasks
            7. Provide validation report summary
            
            Your output MUST include:
            - Validation report from Gemini Validation Protocol
            - Approved recommendations
            - Rejected/modified recommendations with reasoning
            - Final integrated schedule
            """,
            agent=coordinator,
            expected_output="""A comprehensive validated life coordination plan with:
            1. GEMINI VALIDATION PROTOCOL REPORT
            2. Approved Recommendations by Domain
            3. Conflict Resolution Log
            4. Priority Matrix (Validated)
            5. Unified Weekly Schedule (Time-blocked)
            6. Scheduled Action Items
            7. Success Metrics & Validation Scores
            """,
            context=[health_output, finance_output, study_output]
        )
    
    def create_weekly_reflection_task(self, week_data: Dict[str, Any]) -> Task:
        """Task for weekly reflection agent"""
        reflection_agent = self.agents.create_reflection_agent()
        
        return Task(
            description=f"""Analyze the user's weekly performance and provide insights:
            
            Weekly Data:
            {json.dumps(week_data, indent=2)}
            
            Your Analysis Should Include:
            1. Pattern recognition in completed tasks
            2. Consistency streak analysis
            3. Productivity correlation with time of day
            4. Health-finance-study balance assessment
            5. Improvement recommendations for next week
            6. Celebration of achievements
            
            Provide data-driven insights with specific recommendations.
            """,
            agent=reflection_agent,
            expected_output="""A comprehensive weekly reflection report with:
            1. Performance Metrics Summary
            2. Pattern Analysis
            3. Consistency Score
            4. Improvement Recommendations
            5. Next Week Forecast
            6. Celebration Points
            """
        )
