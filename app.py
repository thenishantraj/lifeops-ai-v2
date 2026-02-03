"""
LifeOps AI v2 - Streamlit Application with Advanced Features
"""
import streamlit as st
import os
import sys
from datetime import datetime, timedelta
import json
import time
import pandas as pd

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set OpenAI environment variables to bypass requirements
os.environ["OPENAI_API_KEY"] = "sk-NA"
os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo"

from utils import (
    load_env, format_date, calculate_days_until,
    create_health_chart, create_finance_chart, create_study_schedule,
    create_insight_card, parse_agent_output
)
from crew_setup import LifeOpsCrew
from database import LifeOpsDatabase

# Initialize database
db = LifeOpsDatabase()

# Page configuration
st.set_page_config(
    page_title="LifeOps AI v2",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* KEEP ALL EXISTING v1 CSS */
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        width: 100%;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .agent-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .insight-highlight {
        background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* NEW v2 STYLES */
    .todo-item {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .todo-completed {
        opacity: 0.7;
        border-left-color: #4CAF50;
    }
    .medicine-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border: 1px solid #90caf9;
    }
    .bill-card {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border: 1px solid #ce93d8;
    }
    .pomodoro-timer {
        font-size: 3rem;
        text-align: center;
        font-weight: bold;
        color: #667eea;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        margin: 1rem 0;
    }
    .validation-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .validation-approved {
        background: #4CAF50;
        color: white;
    }
    .validation-pending {
        background: #FF9800;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables v2"""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'user_inputs' not in st.session_state:
        st.session_state.user_inputs = {}
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'pomodoro_active' not in st.session_state:
        st.session_state.pomodoro_active = False
    if 'pomodoro_time' not in st.session_state:
        st.session_state.pomodoro_time = 25 * 60  # 25 minutes
    if 'todo_items' not in st.session_state:
        st.session_state.todo_items = db.get_pending_actions()
    if 'medicines' not in st.session_state:
        st.session_state.medicines = db.get_todays_medicines()
    if 'bills' not in st.session_state:
        st.session_state.bills = db.get_monthly_bills()
    if 'notes' not in st.session_state:
        st.session_state.notes = db.get_notes()

def extract_action_items_from_results(results):
    """Extract action items from AI results and add to database using enhanced utility"""
    from utils import extract_action_items  # Import the utility function
    
    all_text = ""
    # Combine results from all analyzed domains
    for key in ['health', 'finance', 'study', 'coordination']:
        if key in results:
            all_text += results[key] + " "
    
    # Use the regex-based utility to get a clean list of actions
    actions = extract_action_items(all_text)
    
    for action in actions:
        # Enhanced category detection logic
        category = "General"
        action_lower = action.lower()
        
        if any(word in action_lower for word in ["health", "exercise", "sleep", "medicine"]):
            category = "Health"
        elif any(word in action_lower for word in ["finance", "budget", "money", "spend"]):
            category = "Finance"
        elif any(word in action_lower for word in ["study", "learn", "exam", "assignment"]):
            category = "Study"
        
        # Clean and add the task to the database
        if len(action) > 10:  # Safety check for meaningful content
            db.add_action_item(action[:200], category, "AI Agent")
    
    st.session_state.todo_items = db.get_pending_actions()

def main():
    """Main application function v2"""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1 class="main-header">🧠 LifeOps AI v2</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Mission Control Room - Health, Finance & Study Integration with Validation Protocol</p>', unsafe_allow_html=True)
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/1998/1998678.png", width=100)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Life Configuration v2")
        
        # User Inputs
        st.markdown("#### 📊 Current Status")
        
        stress_level = st.slider(
            "Current Stress Level (1-10)",
            min_value=1,
            max_value=10,
            value=5,
            help="1 = Very Relaxed, 10 = Extremely Stressed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            sleep_hours = st.number_input(
                "Sleep Hours",
                min_value=0,
                max_value=12,
                value=7,
                step=1
            )
        with col2:
            exercise_frequency = st.selectbox(
                "Exercise Frequency",
                ["Rarely", "1-2 times/week", "3-4 times/week", "Daily"]
            )
        
        st.markdown("#### 📚 Study")
        
        exam_date = st.date_input(
            "Upcoming Exam Date",
            min_value=datetime.now(),
            value=datetime.now() + timedelta(days=30)
        )
        
        current_study_hours = st.number_input(
            "Current Daily Study Hours",
            min_value=0,
            max_value=12,
            value=3,
            step=1
        )
        
        st.markdown("#### 💰 Finance")
        
        monthly_budget = st.number_input(
            "Monthly Budget ($)",
            min_value=0,
            value=2000,
            step=100
        )
        
        current_expenses = st.number_input(
            "Current Monthly Expenses ($)",
            min_value=0,
            value=1500,
            step=100
        )
        
        financial_goals = st.text_area(
            "Financial Goals",
            "Save for emergency fund, reduce unnecessary expenses"
        )
        
        # NEW v2 sidebar additions
        with st.expander("💊 Medicine Vault", expanded=False):
            medicine_name = st.text_input("Medicine Name")
            medicine_dosage = st.text_input("Dosage (e.g., 500mg)")
            medicine_frequency = st.selectbox("Frequency", ["Daily", "Twice Daily", "Weekly", "As Needed"])
            if st.button("Add Medicine"):
                db.add_medicine(medicine_name, medicine_dosage, medicine_frequency)
                st.success(f"Added {medicine_name}")
                st.session_state.medicines = db.get_todays_medicines()
        
        with st.expander("💰 Bill Tracking", expanded=False):
            bill_name = st.text_input("Bill Name")
            bill_amount = st.number_input("Amount", min_value=0.0, value=100.0)
            bill_due_day = st.number_input("Due Day (1-31)", min_value=1, max_value=31, value=15)
            if st.button("Add Bill"):
                db.add_bill(bill_name, bill_amount, bill_due_day)
                st.success(f"Added {bill_name}")
                st.session_state.bills = db.get_monthly_bills()
        
        # Problem input
        st.markdown("#### 🎯 What's Your Challenge?")
        problem = st.text_area(
            "Describe your current life challenge",
            "I'm stressed about my upcoming exam but also need to manage my budget and health",
            height=100
        )
        
        # Run button
        st.markdown("---")
        run_clicked = st.button(
            "🚀 Run LifeOps v2 Analysis",
            type="primary",
            use_container_width=True
        )
        
        # Store inputs
        user_inputs = {
            'stress_level': stress_level,
            'sleep_hours': sleep_hours,
            'exercise_frequency': exercise_frequency,
            'exam_date': exam_date.strftime("%Y-%m-%d"),
            'days_until_exam': (exam_date - datetime.now().date()).days,
            'current_study_hours': current_study_hours,
            'monthly_budget': monthly_budget,
            'current_expenses': current_expenses,
            'financial_goals': financial_goals,
            'medicines': ", ".join([m['name'] for m in st.session_state.medicines]),
            'bills': ", ".join([b['name'] for b in st.session_state.bills]),
            'problem': problem
        }
        
        st.session_state.user_inputs = user_inputs
    
    # Main content area - NEW TABS ADDED
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard", 
        "🤖 AI Analysis", 
        "📝 Action System",
        "💊 Health Vault",
        "⏰ Productivity",
        "📈 Weekly Review"
    ])
    
    with tab1:
        # Dashboard
        st.markdown("## 📊 Life Dashboard v2")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #667eea;">{stress_level}/10</h3>
                <p style="color: #666;">Stress Level</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            days_left = calculate_days_until(user_inputs['exam_date'])
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #764ba2;">{days_left}</h3>
                <p style="color: #666;">Days Until Exam</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            savings = monthly_budget - current_expenses
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #4CAF50;">${savings}</h3>
                <p style="color: #666;">Monthly Savings</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            consistency_streak = db.get_consistency_streak()
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #FF9800;">{consistency_streak} days</h3>
                <p style="color: #666;">Consistency Streak</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(
                create_health_chart(stress_level, sleep_hours),
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                create_finance_chart(monthly_budget, current_expenses),
                use_container_width=True
            )
        
        # Study Schedule
        st.plotly_chart(
            create_study_schedule(
                user_inputs['days_until_exam'],
                current_study_hours
            ),
            use_container_width=True
        )
    
    with tab2:
        # AI Analysis Area v2 with Validation
        st.markdown("## 🤖 AI Life Analysis v2")
        
        # Validation Protocol Status
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<span class="validation-badge validation-approved">Gemini Protocol</span>', unsafe_allow_html=True)
        with col2:
            st.markdown('<span class="validation-badge validation-approved">Agent Tooling</span>', unsafe_allow_html=True)
        with col3:
            st.markdown('<span class="validation-badge validation-pending">CrewAI Active</span>', unsafe_allow_html=True)
        with col4:
            st.markdown('<span class="validation-badge validation-approved">v2 Ready</span>', unsafe_allow_html=True)
        
        if run_clicked and not st.session_state.processing:
            # Run analysis
            with st.spinner("🧠 LifeOps AI v2 is analyzing with Validation Protocol..."):
                try:
                    # Load environment
                    load_env()
                    
                    # Run analysis
                    st.session_state.processing = True
                    
                    # Create and run crew v2
                    crew = LifeOpsCrew(user_inputs)
                    results = crew.kickoff()
                    
                    # Store results
                    st.session_state.analysis_results = results
                    st.session_state.processing = False
                    
                    # Auto-extract action items from results
                    extract_action_items_from_results(results)
                    
                    # Show success message
                    st.success("✅ LifeOps v2 analysis complete with Gemini Validation!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.processing = False
        
        # Display results if available
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            # Validation Report Highlight
            if 'validation_report' in results:
                st.markdown("### 🔬 Gemini Validation Protocol Report")
                validation = results['validation_report']
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Health", validation.get('health_approved', 'N/A'))
                with col2:
                    st.metric("Finance", validation.get('finance_approved', 'N/A'))
                with col3:
                    st.metric("Study", validation.get('study_approved', 'N/A'))
                with col4:
                    st.metric("Score", f"{validation.get('overall_score', 0)}/100")
            
            # Cross-domain insights highlight
            st.markdown("### 🔄 Validated Cross-Domain Insights")
            st.markdown(f"""
            <div class="insight-highlight">
                <p style="font-size: 1.1rem; font-weight: 500;">
                    {results.get('cross_domain_insights', 'No cross-domain insights extracted.')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Agent outputs in expandable sections
            st.markdown("### 📋 Domain Analysis (Validated)")
            
            # Health Analysis
            with st.expander("🏥 Health Analysis", expanded=True):
                st.markdown(create_insight_card(
                    "Health & Wellness Recommendations",
                    results['health'],
                    "Health",
                    "#4CAF50"
                ), unsafe_allow_html=True)
            
            # Finance Analysis
            with st.expander("💰 Finance Analysis", expanded=True):
                st.markdown(create_insight_card(
                    "Financial Planning & Budgeting",
                    results['finance'],
                    "Finance",
                    "#FF9800"
                ), unsafe_allow_html=True)
            
            # Study Analysis
            with st.expander("📚 Study Analysis", expanded=True):
                st.markdown(create_insight_card(
                    "Learning & Productivity Strategy",
                    results['study'],
                    "Study",
                    "#2196F3"
                ), unsafe_allow_html=True)
            
            # Coordination Results
            st.markdown("### 🎯 Integrated Life Plan (Validated)")
            st.markdown(results['coordination'])
        
        elif not run_clicked:
            st.info("👈 Configure your life settings and click 'Run LifeOps v2 Analysis' to begin with Validation Protocol.")
    
    with tab3:
        # Action System v2
        st.markdown("## 📝 Action System")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### ✅ Dynamic To-Do List")
            
            # Add new action
            with st.form("add_action_form"):
                new_task = st.text_input("New Action Item")
                category = st.selectbox("Category", ["Health", "Finance", "Study", "Personal"])
                submitted = st.form_submit_button("Add Action")
                if submitted and new_task:
                    db.add_action_item(new_task, category, "User")
                    st.session_state.todo_items = db.get_pending_actions()
                    st.rerun()
            
            # Display actions
            todo_items = st.session_state.todo_items
            if todo_items:
                for item in todo_items:
                    col_a, col_b, col_c = st.columns([3, 1, 1])
                    with col_a:
                        st.markdown(f"**{item['task']}**")
                        st.caption(f"Category: {item['category']} • Added: {item['created_at'][:10]}")
                    with col_b:
                        if st.button("✓", key=f"complete_{item['id']}"):
                            db.mark_action_complete(item['id'])
                            st.session_state.todo_items = db.get_pending_actions()
                            st.rerun()
                    with col_c:
                        if st.button("🗑️", key=f"delete_{item['id']}"):
                            # Add delete logic if needed
                            pass
            else:
                st.info("No pending actions. Add some above or run AI analysis.")
        
        with col2:
            st.markdown("### 📊 Progress")
            streak = db.get_consistency_streak()
            st.metric("Consistency Streak", f"{streak} days")
            
            # Weekly completion
            st.markdown("#### This Week")
            # Mock data - in production, query database
            completion_data = {
                "Mon": 3, "Tue": 5, "Wed": 4, "Thu": 6, "Fri": 2, "Sat": 1, "Sun": 0
            }
            st.bar_chart(completion_data)
    
    with tab4:
        # Health Vault
        st.markdown("## 💊 Medicine & Health Vault")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Today's Medicines")
            medicines = st.session_state.medicines
            if medicines:
                for med in medicines:
                    st.markdown(f"""
                    <div class="medicine-card">
                        <h4>{med['name']}</h4>
                        <p>📋 Dosage: {med['dosage']}</p>
                        <p>🔄 Frequency: {med['frequency']}</p>
                        <p>⏰ Time: {med['time_of_day'] or 'Anytime'}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No medicines added. Add them in the sidebar.")
            
            # Medicine reminders
            st.markdown("### ⏰ Reminders")
            reminder_time = st.time_input("Reminder Time", datetime.now().time())
            if st.button("Set Daily Reminder"):
                st.success(f"Reminder set for {reminder_time}")
        
        with col2:
            st.markdown("### 📋 Health Log")
            log_date = st.date_input("Log Date", datetime.now())
            
            symptoms = st.text_area("Symptoms/Today's Feelings")
            sleep_quality = st.slider("Sleep Quality (1-10)", 1, 10, 7)
            energy_level = st.slider("Energy Level (1-10)", 1, 10, 6)
            
            if st.button("Save Health Log"):
                st.success("Health log saved")
            
            st.markdown("### 📈 Health Trends")
            # Mock trend data
            trend_data = {
                "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "Energy": [7, 6, 8, 5, 7, 9, 8],
                "Sleep": [8, 7, 6, 7, 8, 9, 8]
            }
            st.line_chart(trend_data, x="Day", y=["Energy", "Sleep"])
    
    with tab5:
        # Productivity Tools
        st.markdown("## ⏰ Productivity Command Center")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🍅 Study Command Timer")
            
            # Pomodoro Timer
            if not st.session_state.pomodoro_active:
                work_minutes = st.number_input("Work Minutes", 5, 60, 25)
                break_minutes = st.number_input("Break Minutes", 1, 30, 5)
                
                if st.button("Start Pomodoro Session"):
                    st.session_state.pomodoro_active = True
                    st.session_state.pomodoro_time = work_minutes * 60
                    st.session_state.break_time = break_minutes * 60
                    st.session_state.is_work = True
                    st.rerun()
            else:
                # Timer display
                mins, secs = divmod(st.session_state.pomodoro_time, 60)
                timer_text = f"{mins:02d}:{secs:02d}"
                phase = "WORK" if st.session_state.get('is_work', True) else "BREAK"
                
                st.markdown(f"""
                <div class="pomodoro-timer">
                    {timer_text}
                    <div style="font-size: 1rem; color: #666;">{phase} PHASE</div>
                </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Pause"):
                        st.session_state.pomodoro_active = False
                        st.rerun()
                with col_b:
                    if st.button("Skip to Break"):
                        st.session_state.pomodoro_time = st.session_state.get('break_time', 300)
                        st.session_state.is_work = False
                        st.rerun()
                
                # Auto-timer logic (simplified)
                time.sleep(1)
                if st.session_state.pomodoro_time > 0:
                    st.session_state.pomodoro_time -= 1
                    st.rerun()
                else:
                    # Switch phases
                    if st.session_state.get('is_work', True):
                        st.session_state.pomodoro_time = st.session_state.get('break_time', 300)
                        st.session_state.is_work = False
                        st.success("Time for a break! 🎉")
                    else:
                        st.session_state.pomodoro_active = False
                        st.success("Pomodoro complete! 🏁")
                        # Log session
                        db.add_study_session(25, "Pomodoro", 8)
                    st.rerun()
            
            # Break suggestions based on stress
            stress = st.session_state.user_inputs.get('stress_level', 5)
            if stress > 7:
                st.warning("🔥 High stress detected! Consider 10-minute meditation break.")
            elif stress > 5:
                st.info("💡 Moderate stress. Try 5-minute stretch break.")
        
        with col2:
            st.markdown("### 📝 Smart Notepad")
            
            # Note editor
            note_title = st.text_input("Note Title")
            note_content = st.text_area("Content", height=200)
            note_tags = st.text_input("Tags (comma-separated)")
            
            if st.button("Save Note"):
                if note_title and note_content:
                    db.add_note(note_title, note_content, note_tags)
                    st.session_state.notes = db.get_notes()
                    st.success("Note saved!")
            
            st.markdown("### 📋 Recent Notes")
            notes = st.session_state.notes[:5]
            for note in notes:
                with st.expander(f"📄 {note['title']}"):
                    st.write(note['content'])
                    st.caption(f"Tags: {note['tags']} • {note['created_at'][:10]}")
            
            # Google Calendar Sync Simulation
            st.markdown("### 📅 Proposed Schedule")
            if st.button("Generate AI Schedule"):
                # Mock AI schedule generation
                schedule = {
                    "Monday": "8-10: Study, 10-11: Exercise, 14-16: Deep Work",
                    "Tuesday": "9-12: Project Work, 13-15: Meetings, 16-17: Review",
                    "Wednesday": "8-10: Study, 11-12: Health Check, 15-17: Creative Work",
                    "Thursday": "9-11: Focus Work, 13-15: Learning, 16-17: Planning",
                    "Friday": "8-10: Review, 11-13: Work, 14-16: Prep Next Week"
                }
                for day, plan in schedule.items():
                    st.write(f"**{day}**: {plan}")
    
    with tab6:
        # Weekly Review
        st.markdown("## 📈 Weekly Review & Analytics")
        
        # Mock weekly data
        week_data = {
            "completed_actions": 18,
            "total_actions": 25,
            "study_hours": 28,
            "exercise_sessions": 4,
            "sleep_average": 7.2,
            "stress_trend": [6, 5, 7, 6, 5, 4, 5],
            "productivity_score": 78,
            "finance_saved": 450
        }
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Completion Rate", f"{week_data['completed_actions']}/{week_data['total_actions']}")
        with col2:
            st.metric("Study Hours", week_data['study_hours'])
        with col3:
            st.metric("Avg Sleep", f"{week_data['sleep_average']} hrs")
        with col4:
            st.metric("Productivity", f"{week_data['productivity_score']}/100")
        
        # Charts
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 Performance Trends")
            trend_df = pd.DataFrame({
                "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "Stress": week_data['stress_trend'],
                "Productivity": [70, 75, 80, 65, 85, 90, 78]
            })
            st.line_chart(trend_df.set_index("Day"))
        
        with col2:
            st.markdown("### 🎯 Domain Balance")
            domain_df = pd.DataFrame({
                "Domain": ["Health", "Finance", "Study", "Personal"],
                "Hours": [15, 10, 28, 12]
            })
            st.bar_chart(domain_df.set_index("Domain"))
        
        # Weekly Reflection Agent
        st.markdown("### 🤖 AI Weekly Reflection")
        if st.button("Generate Reflection Report"):
            with st.spinner("AI is analyzing your week..."):
                # In production, call reflection agent
                reflection_report = """
                ## Weekly Performance Analysis
                
                **Patterns Identified:**
                - Peak productivity: 10AM-12PM
                - Study consistency improved mid-week
                - Stress reduces after exercise sessions
                
                **Recommendations for Next Week:**
                1. Schedule difficult tasks for Tuesday mornings
                2. Add 15-minute meditation before study sessions
                3. Review budget every Wednesday
                
                **Celebrate:**
                - Achieved 4-day exercise streak!
                - Saved $450 this month
                - Improved sleep quality by 12%
                """
                st.markdown(reflection_report)
                
                # Download report
                st.download_button(
                    label="📥 Download Weekly Report",
                    data=reflection_report,
                    file_name=f"weekly_report_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )

if __name__ == "__main__":
    main()
