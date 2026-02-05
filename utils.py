"""
LifeOps AI v2 - Enhanced Utility Functions with Professional UI Styles
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import re

def get_professional_styles() -> str:
    """Return professional CSS styles for the Unstop-like UI"""
    return """
    <style>
        /* Base Styles */
        .main {
            background: #f0f2f5 !important;
            color: #333;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* Auth Pages */
        .auth-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .auth-card {
            background: white;
            border-radius: 16px;
            padding: 40px;
            width: 100%;
            max-width: 480px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        }
        
        .auth-title {
            color: #2c3e50;
            font-size: 32px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 8px;
        }
        
        .auth-subtitle {
            color: #7f8c8d;
            text-align: center;
            margin-bottom: 32px;
            font-size: 16px;
        }
        
        .auth-footer {
            text-align: center;
            margin-top: 32px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
        }
        
        /* Dashboard Styles */
        .dashboard-title {
            color: #2c3e50;
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .dashboard-subtitle {
            color: #7f8c8d;
            font-size: 16px;
            margin-bottom: 32px;
        }
        
        .page-title {
            color: #2c3e50;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .page-subtitle {
            color: #7f8c8d;
            font-size: 16px;
            margin-bottom: 32px;
        }
        
        /* Cards */
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08);
            text-align: center;
            border: 1px solid #e0e0e0;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }
        
        .metric-icon {
            font-size: 24px;
            margin-bottom: 12px;
        }
        
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 4px;
        }
        
        .metric-label {
            font-size: 14px;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .card-title {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 16px;
        }
        
        /* List Items */
        .list-item {
            background: white;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 8px;
            border-left: 4px solid #3498db;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .list-item:hover {
            background: #f8f9fa;
        }
        
        /* Sidebar */
        .sidebar-header {
            padding: 24px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            margin-bottom: 24px;
            color: white;
        }
        
        .sidebar-header h2 {
            color: white;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .user-greeting {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .user-email {
            font-size: 12px;
            opacity: 0.9;
        }
        
        /* Timer */
        .timer-container {
            background: white;
            border-radius: 16px;
            padding: 32px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }
        
        .timer-phase {
            display: inline-block;
            padding: 8px 24px;
            border-radius: 50px;
            color: white;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 24px;
        }
        
        .timer-display-large {
            font-size: 64px;
            font-weight: 700;
            font-family: 'Courier New', monospace;
            color: #2c3e50;
            margin-bottom: 16px;
        }
        
        .timer-subject {
            font-size: 16px;
            color: #7f8c8d;
        }
        
        /* Profile */
        .profile-card {
            background: white;
            border-radius: 16px;
            padding: 32px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .profile-avatar {
            font-size: 64px;
            margin-bottom: 16px;
        }
        
        .profile-stats {
            margin-top: 24px;
            border-top: 1px solid #e0e0e0;
            padding-top: 16px;
        }
        
        .stat-item {
            margin-bottom: 8px;
        }
        
        .stat-value {
            font-weight: 600;
            color: #2c3e50;
        }
        
        .stat-label {
            font-size: 14px;
            color: #7f8c8d;
        }
        
        /* Tips and Items */
        .tip-item {
            background: white;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 8px;
            border-left: 4px solid #2ecc71;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .session-item {
            background: white;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            border: 1px solid #e0e0e0;
        }
        
        /* Date Display */
        .date-display {
            background: white;
            border-radius: 8px;
            padding: 12px 16px;
            text-align: center;
            font-weight: 600;
            color: #2c3e50;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        /* Form Elements */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select,
        .stNumberInput > div > div > input {
            background: white !important;
            border: 1px solid #ddd !important;
            color: #333 !important;
            border-radius: 8px !important;
            font-size: 14px !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #3498db !important;
            box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2) !important;
        }
        
        /* Buttons */
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: white !important;
            border-radius: 8px;
            padding: 4px;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #7f8c8d !important;
            font-weight: 600;
            border-radius: 6px;
            padding: 8px 16px;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
        }
        
        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #bdc3c7;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #95a5a6;
        }
    </style>
    """

# The rest of your existing utility functions remain the same...
# [Keep all your existing functions: load_env, format_date, calculate_days_until, 
# create_health_chart, create_finance_chart, create_study_schedule,
# create_insight_card, parse_agent_output, extract_action_items, create_weekly_summary]

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
            'bar': {'color': "#3498db"},
            'steps': [
                {'range': [0, 3], 'color': "#2ecc71"},
                {'range': [3, 7], 'color': "#f39c12"},
                {'range': [7, 10], 'color': "#e74c3c"}
            ]
        }
    ))
    
    fig.update_layout(
        grid={'rows': 1, 'columns': 1, 'pattern': "independent"},
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#2c3e50'}
    )
    
    return fig

def create_finance_chart(budget: float, expenses: float = 0):
    """Create a finance chart v2"""
    savings = budget - expenses if budget > expenses else 0
    labels = ['Budget', 'Expenses', 'Savings']
    values = [budget, expenses, savings]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=['#3498db', '#e74c3c', '#2ecc71']
    )])
    
    fig.update_layout(
        title="Budget Allocation",
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#2c3e50'}
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
        marker_color='#3498db',
        text=hours,
        textposition='auto'
    )])
    
    fig.update_layout(
        title="Recommended Study Schedule",
        xaxis_title="Date",
        yaxis_title="Study Hours",
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#2c3e50'}
    )
    
    return fig

def create_insight_card(title: str, content: str, agent: str, color: str = "#3498db"):
    """Create a formatted insight card v2"""
    agent_colors = {
        "Health": "#2ecc71",
        "Finance": "#f39c12",
        "Study": "#3498db",
        "Coordinator": "#9b59b6",
        "Reflection": "#95a5a6"
    }
    
    card_color = agent_colors.get(agent, color)
    
    card = f"""
    <div style="
        background: linear-gradient(135deg, {card_color}20, {card_color}10);
        border-left: 4px solid {card_color};
        padding: 24px;
        border-radius: 12px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 16px;">
            <div style="
                width: 12px;
                height: 12px;
                background-color: {card_color};
                border-radius: 50%;
                margin-right: 12px;
            "></div>
            <h4 style="margin: 0; color: {card_color}; font-weight: 600; font-size: 18px;">{title}</h4>
        </div>
        <p style="margin: 0; color: #2c3e50; line-height: 1.6; font-size: 14px;">{content}</p>
        <div style="
            margin-top: 20px;
            padding-top: 16px;
            border-top: 1px solid rgba(0,0,0,0.1);
            font-size: 12px;
            color: #7f8c8d;
        ">
            🤖 <strong>Agent:</strong> {agent} | 🚀 <strong>LifeOps AI v2</strong>
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
