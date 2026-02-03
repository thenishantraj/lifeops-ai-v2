"""
LifeOps AI v2 - Enhanced Utility Functions
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List  # Added List import here
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import re

def load_env():
    """Load environment variables"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    return api_key

def format_date(date_str: str) -> str:
    """Format date for display"""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return date.strftime("%B %d, %Y")
    except:
        return date_str

def calculate_days_until(target_date: str) -> int:
    """Calculate days until a target date"""
    try:
        target = datetime.strptime(target_date, "%Y-%m-%d")
        today = datetime.now()
        return (target - today).days
    except:
        return 0

def create_health_chart(stress_level: int, hours_sleep: int = 7, exercise_minutes: int = 30):
    """Create a health dashboard chart v2"""
    fig = go.Figure()
    
    # Stress level gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=stress_level,
        title={'text': "Stress Level"},
        domain={'row': 0, 'column': 0},
        gauge={
            'axis': {'range': [None, 10]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 3], 'color': "green"},
                {'range': [3, 7], 'color': "yellow"},
                {'range': [7, 10], 'color': "red"}
            ]
        }
    ))
    
    fig.update_layout(
        grid={'rows': 1, 'columns': 1, 'pattern': "independent"},
        height=300
    )
    
    return fig

def create_finance_chart(budget: float, expenses: float = 0):
    """Create a finance chart v2"""
    savings = budget - expenses if budget > expenses else 0
    labels = ['Budget', 'Recommended Expenses', 'Savings']
    values = [budget, expenses, savings]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=['#2E86AB', '#A23B72', '#F18F01']
    )])
    
    fig.update_layout(
        title="Budget Allocation",
        height=300
    )
    
    return fig

def create_study_schedule(days_until_exam: int, study_hours_per_day: int):
    """Create a study schedule timeline v2"""
    if days_until_exam <= 0:
        days_until_exam = 7  # Default to one week
        
    dates = []
    hours = []
    
    for i in range(days_until_exam):
        date = datetime.now() + timedelta(days=i)
        dates.append(date.strftime("%b %d"))
        
        # Taper study hours as exam approaches
        if i < days_until_exam - 3:
            hours.append(study_hours_per_day)
        elif i == days_until_exam - 1:
            hours.append(2)  # Light review on last day
        else:
            hours.append(study_hours_per_day * 0.7)
    
    fig = go.Figure(data=[go.Bar(
        x=dates,
        y=hours,
        marker_color='#2E86AB',
        text=hours,
        textposition='auto'
    )])
    
    fig.update_layout(
        title="Recommended Study Schedule",
        xaxis_title="Date",
        yaxis_title="Study Hours",
        height=300
    )
    
    return fig

def create_insight_card(title: str, content: str, agent: str, color: str = "#2E86AB"):
    """Create a formatted insight card v2"""
    agent_colors = {
        "Health": "#4CAF50",
        "Finance": "#FF9800",
        "Study": "#2196F3",
        "Coordinator": "#9C27B0",
        "Reflection": "#607D8B"
    }
    
    card_color = agent_colors.get(agent, color)
    
    card = f"""
    <div style="
        background: linear-gradient(135deg, {card_color}20, {card_color}10);
        border-left: 4px solid {card_color};
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="
                width: 12px;
                height: 12px;
                background-color: {card_color};
                border-radius: 50%;
                margin-right: 10px;
            "></div>
            <h4 style="margin: 0; color: {card_color}; font-weight: 600;">{title}</h4>
        </div>
        <p style="margin: 0; color: #333; line-height: 1.6;">{content}</p>
        <div style="
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid rgba(0,0,0,0.1);
            font-size: 0.8em;
            color: #666;
        ">
            🤖 <strong>Agent:</strong> {agent} | 🚀 <strong>LifeOps v2</strong>
        </div>
    </div>
    """
    
    return card

def parse_agent_output(output: str) -> Dict[str, Any]:
    """Parse agent output into structured data v2"""
    try:
        # Try to extract JSON-like content
        if "```json" in output:
            json_str = output.split("```json")[1].split("```")[0].strip()
        elif "```" in output:
            json_str = output.split("```")[1].strip()
            if json_str.startswith("json"):
                json_str = json_str[4:].strip()
        else:
            # Look for JSON-like structure
            start_idx = output.find("{")
            end_idx = output.rfind("}")
            if start_idx != -1 and end_idx != -1:
                json_str = output[start_idx:end_idx+1]
            else:
                return {"raw_output": output}
        
        return json.loads(json_str)
    except:
        return {"raw_output": output}

def extract_action_items(text: str) -> List[str]:
    """Extract potential action items from text"""
    # Regex patterns for action items
    patterns = [
        r"•\s*(.*?\.)",  # Bullet points
        r"\d+\.\s*(.*?\.)",  # Numbered lists
        r"-?\s*(.*?\.)",  # Dash lists
        r"Action:\s*(.*?\.)",  # Action: format
        r"Task:\s*(.*?\.)",  # Task: format
        r"Do:\s*(.*?\.)",  # Do: format
    ]
    
    actions = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        actions.extend(matches)
    
    # Filter and clean
    cleaned = []
    for action in actions:
        action = action.strip()
        if len(action) > 10 and not action.startswith("http"):  # Meaningful length, not URLs
            cleaned.append(action[:200])  # Limit length
    
    return cleaned[:10]  # Return top 10

def create_weekly_summary(data: Dict[str, Any]) -> str:
    """Create a weekly summary from data"""
    summary = f"""
    ## Weekly Summary - {datetime.now().strftime('%B %d, %Y')}
    
    **Performance Metrics:**
    - Actions Completed: {data.get('completed', 0)}/{data.get('total', 0)}
    - Study Hours: {data.get('study_hours', 0)}
    - Exercise Sessions: {data.get('exercise', 0)}
    - Average Sleep: {data.get('sleep_avg', 0):.1f} hours
    
    **Financial Summary:**
    - Budget Spent: ${data.get('spent', 0):.2f}
    - Savings: ${data.get('savings', 0):.2f}
    - Bills Paid: {data.get('bills_paid', 0)}
    
    **Health Indicators:**
    - Average Stress: {data.get('stress_avg', 0)}/10
    - Energy Level: {data.get('energy_avg', 0)}/10
    - Focus Score: {data.get('focus_avg', 0)}/10
    """
    
    return summary
