"""
LifeOps AI v2 - Enhanced Tasks with Tool Integration
"""
from crewai import Task
from typing import Dict, Any, List
from agents import LifeOpsAgents
from datetime import datetime, timedelta
import json

class LifeOpsTasks:
    """Container for all LifeOps AI v2 tasks with tool integration"""
    
    def __init__(self, user_context: Dict[str, Any]):
        self.user_context = user_context
        self.agents = LifeOpsAgents()
    
    def create_health_analysis_task(self) -> Task:
        """Task for health agent with tool calling"""
        health_agent = self.agents.create_health_agent()
        
        return Task(
            description=f"""ANALYSIS PROTOCOL: HEALTH DOMAIN v2.0
            
            COMMAND: Execute comprehensive biometric and wellness analysis.
            
            USER PROFILE:
            - Stress Index: {self.user_context.get('stress_level', 'N/A')}/10
            - Sleep Metrics: {self.user_context.get('sleep_hours', 'N/A')} hrs | Quality: {self.user_context.get('sleep_quality', 'N/A')}
            - Exercise Frequency: {self.user_context.get('exercise_frequency', 'N/A')}
            - Nutrition Score: {self.user_context.get('nutrition_score', 'N/A')}/10
            - Energy Levels: {self.user_context.get('energy_level', 'N/A')}/10
            
            PRIMARY OBJECTIVE: {self.user_context.get('problem', 'General optimization')}
            
            REQUIRED OUTPUT SECTIONS:
            1. HEALTH DEBT INDEX Calculation (0-100)
            2. Immediate Bio-Corrections (Next 24h)
            3. Weekly Wellness Protocol
            4. Predictive Health Trajectory
            5. Tool-Validated Recommendations
            
            TOOL DEPLOYMENT:
            - Use HealthValidation tool on all recommendations
            - Generate at least 3 actionable directives with validation stamps
            
            CONSIDER CROSS-DOMAIN SYNERGY:
            - Health → Productivity conversion rate
            - Sleep quality impact on financial decisions
            - Exercise ROI on cognitive performance
            
            FORMAT: Military briefing style with validation checkmarks.""",
            agent=health_agent,
            expected_output="""HEALTH COMMAND BRIEFING:
            1. HEALTH DEBT INDEX: [Score]/100
            2. VALIDATED DIRECTIVES:
               - [✓] Directive 1 with validation
               - [✓] Directive 2 with validation
               - [✓] Directive 3 with validation
            3. WEEKLY PROTOCOL:
               - Daily routines
               - Nutrition plan
               - Recovery schedule
            4. PREDICTIVE METRICS:
               - Expected energy gain
               - Stress reduction projection
            5. TOOL VALIDATION LOG"""
        )
    
    def create_finance_analysis_task(self) -> Task:
        """Task for finance agent with predictive analytics"""
        finance_agent = self.agents.create_finance_agent()
        
        return Task(
            description=f"""ANALYSIS PROTOCOL: FINANCE DOMAIN v2.0
            
            COMMAND: Execute financial optimization with predictive modeling.
            
            FINANCIAL PARAMETERS:
            - Monthly Budget Allocation: ${self.user_context.get('monthly_budget', 'N/A')}
            - Current Expense Burn Rate: ${self.user_context.get('current_expenses', 'N/A')}/month
            - Savings Rate: {(self.user_context.get('monthly_budget', 0) - self.user_context.get('current_expenses', 0)) / max(self.user_context.get('monthly_budget', 1), 1) * 100:.1f}%
            - Financial Goals: {self.user_context.get('financial_goals', 'N/A')}
            
            PRIMARY OBJECTIVE: {self.user_context.get('problem', 'Financial optimization')}
            
            REQUIRED OUTPUT SECTIONS:
            1. FINANCIAL AUTOPILOT Configuration
            2. Predictive Budget Trajectory (30-day forecast)
            3. Expense Optimization Matrix
            4. Investment Priority Queue
            5. Cross-Domain Resource Allocation
            
            TOOL DEPLOYMENT:
            - Use CrossDomainAnalysis on major financial decisions
            - Calculate opportunity costs across domains
            
            AUTOMATION PROTOCOLS:
            - Bill payment automation rules
            - Savings auto-allocation
            - Expense categorization AI
            
            FORMAT: Financial command dashboard with predictive charts.""",
            agent=finance_agent,
            expected_output="""FINANCE COMMAND BRIEFING:
            1. AUTOPILOT STATUS: [Active/Configuring]
            2. 30-DAY FORECAST:
               - Projected savings: $X
               - Expense reduction: Y%
            3. OPTIMIZATION MATRIX:
               - High-impact changes
               - Low-effort adjustments
            4. CROSS-DOMAIN ALLOCATION:
               - Health investment: $Z
               - Study resources: $W
            5. AUTOMATION RULES DEPLOYED"""
        )
    
    def create_study_analysis_task(self) -> Task:
        """Task for study agent with cognitive optimization"""
        study_agent = self.agents.create_study_agent()
        
        days_until_exam = self.user_context.get('days_until_exam', 0)
        exam_date = self.user_context.get('exam_date', 'N/A')
        
        return Task(
            description=f"""ANALYSIS PROTOCOL: STUDY DOMAIN v2.0
            
            COMMAND: Execute cognitive optimization and knowledge acquisition protocol.
            
            LEARNING PARAMETERS:
            - Mission Critical Date: {exam_date} (T-{days_until_exam} days)
            - Current Study Throughput: {self.user_context.get('current_study_hours', 'N/A')} hrs/day
            - Focus Duration: {self.user_context.get('focus_duration', 'N/A')} min/session
            - Retention Rate Target: {self.user_context.get('retention_target', 85)}%
            
            PRIMARY OBJECTIVE: {self.user_context.get('problem', 'Academic optimization')}
            
            REQUIRED OUTPUT SECTIONS:
            1. COGNITIVE LOAD OPTIMIZATION Schedule
            2. Spaced Repetition Algorithm Configuration
            3. Focus State Management Protocol
            4. Knowledge Retention Assurance
            5. Burnout Prevention Shield
            
            TOOL DEPLOYMENT:
            - Use ScheduleFeasibility on all study blocks
            - Validate against other domain commitments
            
            NEURO-OPTIMIZATION:
            - Optimal study-rest ratios
            - Memory consolidation timing
            - Peak cognitive state alignment
            
            FORMAT: Neural network optimization report with timing diagrams.""",
            agent=study_agent,
            expected_output="""STUDY COMMAND BRIEFING:
            1. COGNITIVE LOAD MAP:
               - Daily focus blocks
               - Break optimization
            2. SPACED REPETITION SCHEDULE:
               - Review intervals
               - Practice sessions
            3. RETENTION ASSURANCE: X%
            4. FOCUS STATE PROTOCOLS:
               - Preparation rituals
               - Deep work windows
            5. VALIDATION LOG:
               - Schedule feasibility checks
               - Cross-domain conflicts resolved"""
        )
    
    def create_life_coordination_task(self, health_output: str, finance_output: str, study_output: str) -> Task:
        """Master coordination task with Gemini Validation Protocol"""
        coordinator = self.agents.create_life_coordinator()
        
        return Task(
            description=f"""GEMINI VALIDATION PROTOCOL: LIFE COORDINATION v2.0
            
            COMMAND: Execute cross-domain integration with validation checks.
            
            DOMAIN INPUTS:
            
            [HEALTH COMMAND]
            {health_output}
            
            [FINANCE COMMAND]
            {finance_output}
            
            [STUDY COMMAND]
            {study_output}
            
            USER PRIORITY DIRECTIVE: {self.user_context.get('problem', 'Multi-domain optimization')}
            
            EXECUTION PROTOCOL:
            1. GEMINI VALIDATION PHASE:
               - Logical consistency check across all domains
               - Resource conflict resolution
               - Timeline synchronization
            
            2. STRATEGIC INTEGRATION:
               - Create 4D Optimization Matrix (Time × Resource × Energy × Priority)
               - Generate Unified Command Schedule
               - Set progress tracking metrics
            
            3. VALIDATION CERTIFICATION:
               - Each directive must pass cross-domain validation
               - Issue validation certificates for approved actions
               - Flag conflicts requiring manual override
            
            4. COMMAND CENTER DEPLOYMENT:
               - Convert validated directives to executable tasks
               - Assign priority levels (Alpha, Beta, Gamma)
               - Set automated tracking parameters
            
            OUTPUT MUST INCLUDE:
            - Validation Certificate for each integrated directive
            - Conflict Resolution Log
            - 7-Day Command Schedule
            - Progress Tracking Dashboard Configuration""",
            agent=coordinator,
            expected_output="""LIFE COMMAND BRIEFING:
            
            GEMINI VALIDATION PROTOCOL: COMPLETE
            
            1. VALIDATION CERTIFICATES ISSUED:
               - [CERT-001] Health Directive: ✓ Approved
               - [CERT-002] Finance Directive: ✓ Approved
               - [CERT-003] Study Directive: ✓ Approved
            
            2. CONFLICT RESOLUTION LOG:
               - Resolved: 3 conflicts
               - Manual Override Required: 0
            
            3. UNIFIED COMMAND SCHEDULE:
               - Daily execution timeline
               - Resource allocation map
               - Priority task queue
            
            4. PROGRESS TRACKING CONFIG:
               - Key Performance Indicators
               - Daily checkpoints
               - Weekly review triggers
            
            5. 4D OPTIMIZATION MATRIX:
               - Time efficiency: X%
               - Resource utilization: Y%
               - Energy alignment: Z%
               - Priority satisfaction: W%""",
            context=[health_output, finance_output, study_output]
        )
    
    def create_reflection_task(self, week_data: Dict[str, Any]) -> Task:
        """Weekly reflection and adjustment task"""
        reflection_agent = self.agents.create_reflection_agent()
        
        return Task(
            description=f"""SUNDAY REVIEW PROTOCOL: WEEKLY REFLECTION v2.0
            
            COMMAND: Analyze past week's performance and adjust strategies.
            
            WEEKLY DATA INPUT:
            {json.dumps(week_data, indent=2)}
            
            ANALYSIS PROTOCOL:
            1. PATTERN DETECTION:
               - Success patterns replication
               - Failure pattern avoidance
               - Efficiency trend analysis
            
            2. STRATEGY ADJUSTMENT:
               - Tweak protocols based on data
               - Optimize resource allocation
               - Adjust timing parameters
            
            3. PREDICTIVE ADVISORY:
               - Next week's optimal path
               - Risk anticipation
               - Opportunity identification
            
            4. LEARNING INTEGRATION:
               - Incorporate lessons learned
               - Update personal algorithms
               - Refine goal trajectories
            
            OUTPUT: Reflection report with adjusted protocols.""",
            agent=reflection_agent,
            expected_output="""WEEKLY REFLECTION REPORT:
            
            1. PATTERN ANALYSIS:
               - Top 3 successful patterns
               - Primary improvement areas
               - Efficiency gains identified
            
            2. STRATEGY ADJUSTMENTS:
               - Modified protocols
               - Resource reallocation
               - Timing optimizations
            
            3. PREDICTIVE OUTLOOK:
               - Next week's forecast
               - Risk mitigation plan
               - Opportunity map
            
            4. LEARNING INTEGRATION:
               - Algorithm updates
               - Goal trajectory refinement
               - Personal growth metrics"""
        )