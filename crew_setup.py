"""
LifeOps AI v2 - Enhanced Crew Orchestration
"""
from crewai import Crew, Process
from agents import LifeOpsAgents
from tasks import LifeOpsTasks
from typing import Dict, Any, List
import json

class LifeOpsCrew:
    """Main crew orchestrator for LifeOps AI v2 with enhanced validation"""
    
    def __init__(self, user_context: Dict[str, Any]):
        self.user_context = user_context
        self.tasks = LifeOpsTasks(user_context)
        self.agents = LifeOpsAgents()
    
    def kickoff(self) -> Dict[str, Any]:
        """Execute the complete LifeOps v2 analysis with Gemini Validation"""
        
        print("🚀 INITIATING LIFEOPS v2.0 ANALYSIS PROTOCOL...")
        
        # Phase 1: Individual Domain Analysis
        print("🔍 PHASE 1: DOMAIN ANALYSIS")
        
        print("🧠 DEPLOYING HEALTH COMMAND AGENT...")
        health_task = self.tasks.create_health_analysis_task()
        health_result = health_task.execute()
        
        print("💰 DEPLOYING FINANCE CONTROL AGENT...")
        finance_task = self.tasks.create_finance_analysis_task()
        finance_result = finance_task.execute()
        
        print("📚 DEPLOYING STUDY ORCHESTRATOR AGENT...")
        study_task = self.tasks.create_study_analysis_task()
        study_result = study_task.execute()
        
        # Phase 2: Gemini Validation Protocol
        print("🔄 PHASE 2: GEMINI VALIDATION PROTOCOL")
        
        coordination_task = self.tasks.create_life_coordination_task(
            health_result,
            finance_result,
            study_result
        )
        
        print("👑 DEPLOYING LIFE COMMANDER AGENT...")
        coordination_result = coordination_task.execute()
        
        # Phase 3: Compile and Validate Results
        print("📊 PHASE 3: RESULT COMPILATION")
        
        results = {
            "health": health_result,
            "finance": finance_result,
            "study": study_result,
            "coordination": coordination_result,
            "cross_domain_insights": self._extract_cross_domain_insights(coordination_result),
            "validation_status": self._validate_results(coordination_result),
            "user_context": self.user_context,
            "timestamp": self._get_timestamp(),
            "version": "2.0"
        }
        
        print("✅ LIFEOPS v2.0 ANALYSIS COMPLETE!")
        print(f"📊 VALIDATION STATUS: {results['validation_status']}")
        
        return results
    
    def _extract_cross_domain_insights(self, coordination_output: str) -> str:
        """Extract enhanced cross-domain insights with validation markers"""
        lines = coordination_output.split('\n')
        insights = []
        
        # Look for validation markers and cross-domain indicators
        validation_keywords = ['✓', 'VALIDATED', 'CERT-', 'APPROVED', 'SYNERGY']
        cross_domain_keywords = ['BECAUSE', 'THEREFORE', 'IMPACTS', 'AFFECTS', 'RELATES TO']
        
        for line in lines:
            line_upper = line.upper()
            if any(keyword in line_upper for keyword in validation_keywords + cross_domain_keywords):
                insights.append(line)
            elif 'STRESS' in line_upper and any(domain in line_upper for domain in ['STUDY', 'FINANCE', 'HEALTH']):
                insights.append(line)
            elif 'BUDGET' in line_upper and any(domain in line_upper for domain in ['HEALTH', 'STUDY', 'TIME']):
                insights.append(line)
        
        if insights:
            return "\n".join(insights[:10])  # Return top 10 insights
        
        # Fallback: extract first coherent paragraph
        paragraphs = coordination_output.split('\n\n')
        for para in paragraphs:
            if len(para.split()) > 20:  # Look for substantial paragraphs
                return para[:500] + "..."
        
        return "Cross-domain validation insights integrated into coordination plan."
    
    def _validate_results(self, coordination_output: str) -> str:
        """Validate coordination results"""
        checks = []
        
        # Check for validation markers
        if 'VALIDATION CERTIFICATE' in coordination_output.upper():
            checks.append("✓ Validation certificates issued")
        
        if 'CONFLICT RESOLUTION' in coordination_output.upper():
            checks.append("✓ Conflicts resolved")
        
        if any(keyword in coordination_output.upper() for keyword in ['SCHEDULE', 'TIMELINE', 'CALENDAR']):
            checks.append("✓ Schedule integration")
        
        if any(keyword in coordination_output.upper() for keyword in ['PRIORITY', 'URGENT', 'IMPORTANT']):
            checks.append("✓ Priority assignment")
        
        if len(checks) >= 3:
            return "PASSED - " + " | ".join(checks)
        elif checks:
            return "PARTIAL - " + " | ".join(checks)
        else:
            return "BASIC - No advanced validation markers found"
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def run_sequential_crew(self):
        """Alternative: Run as a single crew with sequential process"""
        agents = self.agents.get_all_agents()
        
        # Get all tasks
        tasks = [
            self.tasks.create_health_analysis_task(),
            self.tasks.create_finance_analysis_task(),
            self.tasks.create_study_analysis_task(),
        ]
        
        # Add coordination task
        coordination_task = self.tasks.create_life_coordination_task(
            "", "", ""  # Placeholders, will be filled by context
        )
        tasks.append(coordination_task)
        
        # Create crew with enhanced configuration
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.sequential,
            memory=True,
            cache=True,
            max_rpm=50,
            share_crew=True
        )
        
        return crew.kickoff()
    
    def run_reflection_crew(self, week_data: Dict[str, Any]):
        """Run weekly reflection crew"""
        print("🔄 INITIATING WEEKLY REFLECTION PROTOCOL...")
        
        reflection_task = self.tasks.create_reflection_task(week_data)
        reflection_agent = self.agents.create_reflection_agent()
        
        reflection_task.agent = reflection_agent
        result = reflection_task.execute()
        
        return {
            "reflection": result,
            "week_data": week_data,
            "timestamp": self._get_timestamp()
        }