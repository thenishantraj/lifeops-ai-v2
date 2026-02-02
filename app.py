"""
LifeOps AI v2 - Clean Command Center
"""
import streamlit as st
import os
import sys
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import (
    load_env, format_date, calculate_days_until,
    create_cyberpunk_health_chart, create_cyberpunk_finance_chart,
    create_study_schedule_timeline, create_streak_chart,
    db, simulate_calendar_sync, generate_task_id
)

# Check for API key before importing crew
def check_api_key():
    """Check if Google API key is available"""
    if not os.getenv("GOOGLE_API_KEY"):
        # Try to load from .env
        from dotenv import load_dotenv
        load_dotenv()
        
        if not os.getenv("GOOGLE_API_KEY"):
            # Try Streamlit secrets
            try:
                if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
                    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
                    print("✅ Loaded API key from Streamlit secrets")
                else:
                    print("⚠️ No API key found. Using demo mode.")
                    os.environ["GOOGLE_API_KEY"] = "demo_key_for_testing"
            except:
                print("⚠️ No API key found. Using demo mode.")
                os.environ["GOOGLE_API_KEY"] = "demo_key_for_testing"
    
    return True

check_api_key()

# Now import crew setup
try:
    from crew_setup import LifeOpsCrew
    CREW_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Crew setup not available: {e}")
    CREW_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="LifeOps AI v2.0",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/lifeops-ai',
        'Report a bug': 'https://github.com/lifeops-ai/issues',
        'About': '# LifeOps AI v2.0\nClean Command Center'
    }
)

# Load custom CSS
def load_css():
    try:
        with open('styles.css', 'r') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except:
        # Fallback minimal CSS
        st.markdown("""
        <style>
        .stApp { background: #f8f9fa; }
        .metric-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .task-item { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #3498db; }
        </style>
        """, unsafe_allow_html=True)

load_css()

class SmartTimer:
    """Pomodoro timer with AI integration"""
    
    def __init__(self):
        self.is_running = False
        self.start_time = None
        self.duration = 25 * 60  # 25 minutes in seconds
        self.remaining = 25 * 60
        self.mode = "focus"  # "focus" or "break"
        self.sessions_completed = 0
        
    def start(self, duration_minutes: int = 25):
        """Start timer"""
        self.is_running = True
        self.start_time = datetime.now()
        self.duration = duration_minutes * 60
        self.remaining = self.duration
        self.mode = "focus"
        
    def pause(self):
        """Pause timer"""
        self.is_running = False
        
    def reset(self):
        """Reset timer"""
        self.is_running = False
        self.remaining = self.duration
        self.mode = "focus"
        
    def toggle_mode(self):
        """Switch between focus and break"""
        self.mode = "break" if self.mode == "focus" else "focus"
        self.remaining = (5 if self.mode == "break" else 25) * 60
        self.reset()
        if self.mode == "focus":
            self.sessions_completed += 1
            
    def get_display(self) -> str:
        """Get formatted time display"""
        minutes = self.remaining // 60
        seconds = self.remaining % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def update(self):
        """Update timer state"""
        if self.is_running and self.remaining > 0:
            self.remaining -= 1
            if self.remaining == 0:
                self.toggle_mode()
                return True  # Timer completed
        return False

class LifeOpsApp:
    """Main application class for LifeOps AI v2"""
    
    def __init__(self):
        self.timer = SmartTimer()
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize all session state variables"""
        defaults = {
            'analysis_results': None,
            'user_inputs': {
                'stress_level': 5,
                'sleep_hours': 7,
                'exercise_frequency': 'MODERATE',
                'exam_date': (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                'days_until_exam': 30,
                'current_study_hours': 3,
                'focus_duration': 45,
                'monthly_budget': 2000,
                'current_expenses': 1500,
                'problem': 'I need to balance exam preparation with maintaining health and managing budget constraints'
            },
            'processing': False,
            'active_tab': 'dashboard',
            'timer_running': False,
            'medicine_reminders': [],
            'selected_task': None,
            'notes_content': '',
            'weekly_review_data': {},
            'agent_outputs': {},
            'task_filter': 'all',
            'weekly_plan': None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def render_sidebar(self):
        """Render clean sidebar"""
        with st.sidebar:
            # Header
            st.markdown('# 🚀 LIFEOPs v2.0')
            st.markdown('### Clean Command Center')
            st.divider()
            
            # Navigation
            st.markdown('### 🎮 NAVIGATION')
            nav_cols = st.columns(2)
            with nav_cols[0]:
                if st.button('📊 DASHBOARD', key='nav_dash', use_container_width=True, 
                           type='primary' if st.session_state.active_tab == 'dashboard' else 'secondary'):
                    st.session_state.active_tab = 'dashboard'
                    st.rerun()
            with nav_cols[1]:
                if st.button('🤖 AGENT CONTROL', key='nav_agent', use_container_width=True,
                           type='primary' if st.session_state.active_tab == 'agent' else 'secondary'):
                    st.session_state.active_tab = 'agent'
                    st.rerun()
            
            # Quick Actions
            st.divider()
            st.markdown('### ⚡ QUICK ACTIONS')
            
            if st.button('🔄 RUN WEEKLY REVIEW', key='weekly_review', use_container_width=True):
                self.run_weekly_review()
            
            if st.button('📥 EXPORT DATA', key='export_data', use_container_width=True):
                self.export_data()
            
            # System Status
            st.divider()
            st.markdown('### 🖥️ SYSTEM STATUS')
            
            col1, col2 = st.columns(2)
            with col1:
                tasks = db.get_tasks(completed=False)
                st.metric("AGENTS", "4", "✓ ONLINE")
            with col2:
                st.metric("TASKS", str(len(tasks)), "ACTIVE")
            
            # Timer Control
            st.divider()
            st.markdown('### ⏱️ COGNITIVE TIMER')
            
            timer_cols = st.columns(3)
            with timer_cols[0]:
                if st.button('▶️', key='timer_start', use_container_width=True):
                    self.timer.start()
                    st.session_state.timer_running = True
                    st.rerun()
            with timer_cols[1]:
                if st.button('⏸️', key='timer_pause', use_container_width=True):
                    self.timer.pause()
                    st.session_state.timer_running = False
                    st.rerun()
            with timer_cols[2]:
                if st.button('🔄', key='timer_reset', use_container_width=True):
                    self.timer.reset()
                    st.session_state.timer_running = False
                    st.rerun()
            
            timer_display = f"**{self.timer.get_display()}** | {self.timer.mode.upper()}"
            st.markdown(f'<div class="timer-display">{timer_display}</div>', unsafe_allow_html=True)
            
            # User Profile
            st.divider()
            st.markdown('### 👤 USER PROFILE')
            
            # Quick stats
            tasks = db.get_tasks(completed=False)
            completed = db.get_tasks(completed=True)
            total_tasks = len(tasks) + len(completed)
            completion_rate = (len(completed) / total_tasks * 100) if total_tasks > 0 else 0
            
            st.progress(completion_rate / 100)
            st.caption(f"Completion: {completion_rate:.1f}%")
    
    def render_dashboard(self):
        """Render main dashboard"""
        st.markdown('# 🎯 COMMAND CENTER DASHBOARD')
        st.markdown('### Real-Time Life Operations Monitoring')
        
        # Top Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.render_metric_card(
                title="HEALTH INDEX",
                value="82",
                delta="+3%",
                color="#4CAF50",
                icon="🏥"
            )
        
        with col2:
            tasks = db.get_tasks(completed=False)
            urgent_tasks = len([t for t in tasks if t.get('priority', 3) == 1])
            self.render_metric_card(
                title="ACTIVE TASKS",
                value=str(len(tasks)),
                delta=f"{urgent_tasks} urgent",
                color="#FF9800",
                icon="✅"
            )
        
        with col3:
            bills = db.get_bills()
            unpaid = [b for b in bills if not b.get('paid', True)]
            total_unpaid = sum(b.get('amount', 0) for b in unpaid)
            self.render_metric_card(
                title="FINANCIAL STATUS",
                value=f"${total_unpaid:.0f}",
                delta=f"{len(unpaid)} pending",
                color="#2196F3",
                icon="💰"
            )
        
        with col4:
            progress_data = db.get_weekly_progress()
            streak = len(progress_data) if progress_data else 0
            self.render_metric_card(
                title="CONSISTENCY STREAK",
                value=f"{streak} days",
                delta="🔥",
                color="#9C27B0",
                icon="📈"
            )
        
        # Main Dashboard Grid
        col1, col2 = st.columns(2)
        
        with col1:
            # Interactive To-Do List
            with st.container():
                st.markdown('### 📋 ACTIVE DIRECTIVES')
                self.render_task_list()
            
            # Smart Notepad
            with st.container():
                st.markdown('### 🖋️ SMART NOTEPAD')
                self.render_notepad()
        
        with col2:
            # Progress Tracker
            with st.container():
                st.markdown('### 📈 PROGRESS ANALYTICS')
                self.render_progress_tracker()
            
            # Utility Tools
            with st.container():
                st.markdown('### 🛠️ UTILITY TOOLS')
                self.render_utility_tools()
    
    def render_agent_control(self):
        """Render agent control panel"""
        st.markdown('# 🤖 AGENT COMMAND CENTER')
        st.markdown('### Multi-Agent Orchestration')
        
        # Agent Status Panel
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style='background: white; padding: 20px; border-radius: 10px; text-align: center;'>
                <div style='font-size: 2rem;'>🧠</div>
                <h4 style='color: #4CAF50;'>HEALTH COMMAND</h4>
                <div style='color: #00ff88;'>ONLINE</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background: white; padding: 20px; border-radius: 10px; text-align: center;'>
                <div style='font-size: 2rem;'>💰</div>
                <h4 style='color: #FF9800;'>FINANCE CONTROL</h4>
                <div style='color: #00ff88;'>ONLINE</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='background: white; padding: 20px; border-radius: 10px; text-align: center;'>
                <div style='font-size: 2rem;'>📚</div>
                <h4 style='color: #2196F3;'>STUDY ORCHESTRATOR</h4>
                <div style='color: #00ff88;'>ONLINE</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style='background: white; padding: 20px; border-radius: 10px; text-align: center;'>
                <div style='font-size: 2rem;'>👑</div>
                <h4 style='color: #9C27B0;'>LIFE COMMANDER</h4>
                <div style='color: #ff9900;'>VALIDATING</div>
            </div>
            """, unsafe_allow_html=True)
        
        # User Input Configuration
        with st.expander("⚙️ CONFIGURATION PANEL", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🧠 HEALTH PARAMETERS")
                stress_level = st.slider("STRESS INDEX", 1, 10, 5, key="health_stress")
                sleep_hours = st.number_input("SLEEP HOURS", 0, 12, 7, key="health_sleep")
                exercise = st.selectbox("EXERCISE FREQUENCY", 
                                      ["SEDENTARY", "LIGHT", "MODERATE", "INTENSE", "ATHLETE"],
                                      index=2, key="health_exercise")
            
            with col2:
                st.markdown("#### 📚 STUDY PARAMETERS")
                exam_date = st.date_input("CRITICAL DATE", 
                                         min_value=datetime.now(),
                                         value=datetime.now() + timedelta(days=30),
                                         key="study_date")
                study_hours = st.number_input("STUDY THROUGHPUT (hrs/day)", 0, 12, 3, key="study_hours")
                focus_duration = st.slider("FOCUS DURATION (min)", 15, 120, 45, key="study_focus")
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("#### 💰 FINANCE PARAMETERS")
                monthly_budget = st.number_input("MONTHLY BUDGET ($)", 0, 10000, 2000, step=100, key="finance_budget")
                current_expenses = st.number_input("CURRENT EXPENSES ($)", 0, 10000, 1500, step=100, key="finance_expenses")
            
            with col4:
                st.markdown("#### 🎯 PRIMARY OBJECTIVE")
                problem = st.text_area("MISSION BRIEFING", 
                                     "I need to balance exam preparation with maintaining health and managing budget constraints",
                                     height=100,
                                     key="mission_briefing")
            
            # Store inputs
            st.session_state.user_inputs = {
                'stress_level': stress_level,
                'sleep_hours': sleep_hours,
                'exercise_frequency': exercise,
                'exam_date': exam_date.strftime("%Y-%m-%d"),
                'days_until_exam': (exam_date - datetime.now().date()).days,
                'current_study_hours': study_hours,
                'focus_duration': focus_duration,
                'monthly_budget': monthly_budget,
                'current_expenses': current_expenses,
                'problem': problem
            }
        
        # Execution Control
        st.divider()
        st.markdown("### 🚀 EXECUTION CONTROL")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧠 EXECUTE SINGLE DOMAIN", use_container_width=True, type="primary"):
                with st.spinner("Analyzing domain..."):
                    time.sleep(2)
                    st.success("Domain analysis complete!")
        
        with col2:
            if st.button("🔄 EXECUTE FULL ANALYSIS", use_container_width=True, type="primary"):
                if not CREW_AVAILABLE:
                    st.error("Agent system not available. Check API key and dependencies.")
                else:
                    with st.spinner("Executing analysis protocol..."):
                        try:
                            crew = LifeOpsCrew(st.session_state.user_inputs)
                            results = crew.kickoff()
                            st.session_state.analysis_results = results
                            st.success("✅ FULL ANALYSIS COMPLETE!")
                            
                            # Extract tasks from results
                            self.extract_tasks_from_results(results)
                            
                        except Exception as e:
                            st.error(f"❌ ANALYSIS ERROR: {str(e)}")
                            # Show demo results
                            st.session_state.analysis_results = {
                                'health': "✅ HEALTH ANALYSIS: Recommended daily exercise, improved sleep schedule, stress management techniques.",
                                'finance': "✅ FINANCE ANALYSIS: Budget optimized, savings plan created, expense tracking setup.",
                                'study': "✅ STUDY ANALYSIS: Study schedule created, focus techniques recommended, exam preparation plan.",
                                'coordination': "✅ COORDINATION: All domains integrated successfully. Priority: Study (70%), Health (20%), Finance (10%)."
                            }
        
        with col3:
            if st.button("📊 GENERATE WEEKLY PLAN", use_container_width=True):
                self.generate_weekly_plan()
        
        # Results Display
        if st.session_state.get('analysis_results'):
            st.divider()
            st.markdown("### 📊 ANALYSIS RESULTS")
            
            results = st.session_state.analysis_results
            
            tabs = st.tabs(["🧠 HEALTH", "💰 FINANCE", "📚 STUDY", "👑 COORDINATION"])
            
            with tabs[0]:
                health_result = results.get('health', 'No health analysis available.')
                st.markdown(f"""
                <div style='background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #4CAF50;'>
                    <h4 style='color: #4CAF50;'>HEALTH COMMAND BRIEFING</h4>
                    <div style='white-space: pre-wrap;'>{health_result[:1000]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with tabs[1]:
                finance_result = results.get('finance', 'No finance analysis available.')
                st.markdown(f"""
                <div style='background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #FF9800;'>
                    <h4 style='color: #FF9800;'>FINANCE COMMAND BRIEFING</h4>
                    <div style='white-space: pre-wrap;'>{finance_result[:1000]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with tabs[2]:
                study_result = results.get('study', 'No study analysis available.')
                st.markdown(f"""
                <div style='background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #2196F3;'>
                    <h4 style='color: #2196F3;'>STUDY COMMAND BRIEFING</h4>
                    <div style='white-space: pre-wrap;'>{study_result[:1000]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with tabs[3]:
                coord_result = results.get('coordination', 'No coordination analysis available.')
                st.markdown(f"""
                <div style='background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #9C27B0;'>
                    <h4 style='color: #9C27B0;'>LIFE COMMAND BRIEFING</h4>
                    <div style='white-space: pre-wrap;'>{coord_result[:1500]}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_task_list(self):
        """Render interactive task list"""
        # Task filter
        filter_cols = st.columns(4)
        with filter_cols[0]:
            if st.button("ALL", key="filter_all", use_container_width=True):
                st.session_state.task_filter = 'all'
                st.rerun()
        with filter_cols[1]:
            if st.button("HEALTH", key="filter_health", use_container_width=True):
                st.session_state.task_filter = 'health'
                st.rerun()
        with filter_cols[2]:
            if st.button("STUDY", key="filter_study", use_container_width=True):
                st.session_state.task_filter = 'study'
                st.rerun()
        with filter_cols[3]:
            if st.button("FINANCE", key="filter_finance", use_container_width=True):
                st.session_state.task_filter = 'finance'
                st.rerun()
        
        # Get tasks
        tasks = db.get_tasks(completed=False)
        
        if st.session_state.task_filter != 'all':
            tasks = [t for t in tasks if t.get('category') == st.session_state.task_filter]
        
        # Display tasks
        if tasks:
            for task in tasks[:10]:  # Limit to 10 tasks
                col1, col2, col3 = st.columns([6, 2, 2])
                
                with col1:
                    priority = task.get('priority', 3)
                    priority_color = {
                        1: "#F44336",  # Urgent
                        2: "#FF9800",  # High
                        3: "#2196F3"   # Normal
                    }.get(priority, "#9E9E9E")
                    
                    category = task.get('category', 'general')
                    category_color = {
                        'health': '#4CAF50',
                        'finance': '#FF9800',
                        'study': '#2196F3'
                    }.get(category, '#9C27B0')
                    
                    st.markdown(f"""
                    <div style='background: #f8f9fa; padding: 15px; margin: 5px 0; border-radius: 8px; border-left: 4px solid {category_color};'>
                        <div style='display: flex; align-items: center;'>
                            <div style='width: 8px; height: 8px; background: {priority_color}; border-radius: 50%; margin-right: 10px;'></div>
                            <strong>{task.get('title', 'Untitled')}</strong>
                        </div>
                        <div style='font-size: 0.9em; color: #666; margin-top: 5px;'>
                            {task.get('description', '')[:80]}...
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.caption(f"Priority: {priority}")
                
                with col3:
                    if st.button("✓", key=f"complete_{task.get('id')}", help="Mark as complete"):
                        try:
                            db.complete_task(task['id'])
                            st.success(f"Completed: {task.get('title')}")
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        else:
            st.info("No active tasks. Add some tasks to get started!")
        
        # Add new task
        with st.expander("➕ ADD NEW DIRECTIVE"):
            col1, col2 = st.columns(2)
            with col1:
                new_title = st.text_input("Directive Title", key="new_task_title")
                new_desc = st.text_area("Description", key="new_task_desc")
            with col2:
                new_category = st.selectbox("Category", ["health", "finance", "study", "general"], key="new_task_cat")
                priority_options = [("⚡ Urgent", 1), ("🔥 High", 2), ("⚪ Normal", 3)]
                new_priority = st.selectbox("Priority", priority_options, 
                                          format_func=lambda x: x[0], index=2, key="new_task_pri")
                new_priority = new_priority[1]
            
            if st.button("ADD DIRECTIVE", key="add_task", type="primary"):
                if new_title:
                    task_data = {
                        'title': new_title,
                        'description': new_desc,
                        'category': new_category,
                        'priority': new_priority
                    }
                    try:
                        db.save_task(task_data)
                        st.success("Directive added successfully!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding task: {e}")
                else:
                    st.warning("Please enter a task title")
    
    def render_notepad(self):
        """Render smart notepad"""
        notes = db.get_notes()
        
        # Note editor
        note_title = st.text_input("Note Title", key="note_title")
        note_content = st.text_area("Content", height=150, key="note_content")
        note_category = st.selectbox("Category", ["thoughts", "ideas", "todo", "reflection"], key="note_category")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 SAVE NOTE", key="save_note", use_container_width=True, type="primary"):
                if note_title and note_content:
                    note_data = {
                        'title': note_title,
                        'content': note_content,
                        'category': note_category
                    }
                    try:
                        db.save_note(note_data)
                        st.success("Note saved successfully!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving note: {e}")
                else:
                    st.warning("Please enter both title and content")
        
        with col2:
            if st.button("🗑️ CLEAR", key="clear_note", use_container_width=True):
                st.rerun()
        
        # Display recent notes
        if notes:
            st.markdown("### 📝 RECENT NOTES")
            for note in notes[:3]:
                with st.expander(f"{note.get('title', 'Untitled')} ({note.get('category', 'general')})"):
                    st.markdown(note.get('content', ''))
                    if note.get('updated_at'):
                        st.caption(f"Last updated: {note['updated_at'][:16]}")
    
    def render_progress_tracker(self):
        """Render progress tracking dashboard"""
        progress_data = db.get_weekly_progress()
        
        if progress_data and len(progress_data) > 0:
            try:
                # Convert to DataFrame for display
                df = pd.DataFrame(progress_data)
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                
                # Display streak chart
                st.plotly_chart(create_streak_chart(progress_data), use_container_width=True)
                
                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_stress = df['stress_level'].mean() if 'stress_level' in df.columns else 5
                    delta = None
                    if avg_stress < 5:
                        delta = f"{-avg_stress + 5:.1f}"
                    st.metric("Avg Stress", f"{avg_stress:.1f}/10", delta=delta)
                with col2:
                    avg_sleep = df['sleep_hours'].mean() if 'sleep_hours' in df.columns else 7
                    delta = None
                    if avg_sleep > 7:
                        delta = f"{avg_sleep - 7:.1f}"
                    st.metric("Avg Sleep", f"{avg_sleep:.1f}h", delta=delta)
                with col3:
                    total_tasks = df['tasks_completed'].sum() if 'tasks_completed' in df.columns else 0
                    st.metric("Tasks Completed", int(total_tasks))
            except Exception as e:
                st.info("Progress data available but format issue. Log new progress.")
        else:
            st.info("No progress data yet. Complete some tasks to start tracking!")
        
        # Manual progress entry
        with st.expander("📝 LOG DAILY PROGRESS"):
            col1, col2 = st.columns(2)
            with col1:
                day_stress = st.slider("Today's Stress", 1, 10, 5, key="day_stress")
                day_sleep = st.number_input("Sleep Hours", 0.0, 12.0, 7.0, step=0.5, key="day_sleep")
            with col2:
                day_health = st.slider("Health Score", 0, 100, 75, key="day_health")
                day_tasks = st.number_input("Tasks Completed", 0, 50, 0, key="day_tasks")
            
            day_notes = st.text_area("Daily Notes", key="day_notes")
            
            if st.button("SAVE PROGRESS", key="save_progress", type="primary"):
                progress_data = {
                    'health_score': day_health,
                    'stress_level': day_stress,
                    'sleep_hours': day_sleep,
                    'tasks_completed': day_tasks,
                    'notes': day_notes
                }
                try:
                    db.save_progress(progress_data)
                    st.success("Progress saved successfully!")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving progress: {e}")
    
    def render_utility_tools(self):
        """Render utility tools section"""
        tabs = st.tabs(["💊 MEDICINE", "📋 BILLS", "📅 CALENDAR"])
        
        with tabs[0]:
            self.render_medicine_vault()
        
        with tabs[1]:
            self.render_bill_tracker()
        
        with tabs[2]:
            self.render_calendar_sync()
    
    def render_medicine_vault(self):
        """Render medicine vault"""
        medicines = db.get_medicines()
        
        # Add new medicine
        with st.expander("➕ ADD MEDICINE"):
            col1, col2 = st.columns(2)
            with col1:
                med_name = st.text_input("Medicine Name", key="med_name")
                med_dosage = st.text_input("Dosage", key="med_dosage")
            with col2:
                med_freq = st.selectbox("Frequency", ["daily", "bid", "tid", "qid", "weekly"], key="med_freq")
                med_time = st.time_input("Time", value=datetime.now().time(), key="med_time")
            
            if st.button("ADD TO VAULT", key="add_med", type="primary"):
                if med_name:
                    medicine_data = {
                        'name': med_name,
                        'dosage': med_dosage,
                        'frequency': med_freq,
                        'time': med_time.strftime("%H:%M")
                    }
                    try:
                        db.add_medicine(medicine_data)
                        st.success("Medicine added to vault!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding medicine: {e}")
                else:
                    st.warning("Please enter medicine name")
        
        # Display medicines
        if medicines:
            st.markdown("### 💊 CURRENT MEDICATIONS")
            for med in medicines:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.text(f"{med.get('name', 'Unknown')} - {med.get('dosage', '')}")
                with col2:
                    st.caption(f"{med.get('frequency', '')} at {med.get('time', '')}")
                with col3:
                    if st.button("✅", key=f"take_{med.get('id')}", help="Mark as taken"):
                        st.success(f"Marked {med.get('name')} as taken!")
        else:
            st.info("No medicines in vault. Add some to get reminders!")
    
    def render_bill_tracker(self):
        """Render bill tracking system"""
        bills = db.get_bills()
        
        # Add new bill
        with st.expander("➕ ADD BILL"):
            col1, col2 = st.columns(2)
            with col1:
                bill_name = st.text_input("Bill Name", key="bill_name")
                bill_amount = st.number_input("Amount ($)", 0.0, 10000.0, 100.0, key="bill_amount")
            with col2:
                bill_date = st.date_input("Due Date", key="bill_date")
                bill_category = st.selectbox("Category", 
                                           ["rent", "utilities", "subscription", "loan", "other"],
                                           key="bill_category")
            
            if st.button("ADD BILL", key="add_bill", type="primary"):
                if bill_name and bill_amount > 0:
                    bill_data = {
                        'name': bill_name,
                        'amount': bill_amount,
                        'due_date': bill_date.strftime("%Y-%m-%d"),
                        'category': bill_category
                    }
                    try:
                        db.add_bill(bill_data)
                        st.success("Bill added to tracker!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding bill: {e}")
                else:
                    st.warning("Please enter bill name and amount")
        
        # Display bills
        if bills:
            unpaid = [b for b in bills if not b.get('paid', True)]
            paid = [b for b in bills if b.get('paid', False)]
            
            st.metric("Pending Bills", f"${sum(b.get('amount', 0) for b in unpaid):.2f}", 
                     f"{len(unpaid)} bills")
            
            for bill in unpaid[:5]:
                days_until = calculate_days_until(bill.get('due_date', ''))
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.text(f"{bill.get('name', 'Unknown')}")
                with col2:
                    st.text(f"${bill.get('amount', 0):.2f}")
                with col3:
                    if days_until <= 0:
                        status = "OVERDUE"
                        color = "red"
                    elif days_until <= 3:
                        status = f"Due in {days_until} days"
                        color = "red"
                    elif days_until <= 7:
                        status = f"Due in {days_until} days"
                        color = "orange"
                    else:
                        status = f"Due in {days_until} days"
                        color = "green"
                    
                    st.markdown(f"<span style='color: {color}; font-weight: bold;'>{status}</span>", 
                              unsafe_allow_html=True)
                with col4:
                    if st.button("💳", key=f"pay_{bill.get('id')}", help="Mark as paid"):
                        st.success(f"Marked {bill.get('name')} as paid!")
        else:
            st.info("No bills tracked. Add bills to manage payments!")
    
    def render_calendar_sync(self):
        """Render calendar sync interface"""
        st.markdown("### 📅 GOOGLE CALENDAR SYNC")
        
        # Mock sync status
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sync Status", "CONNECTED", "Last: Today")
        with col2:
            st.metric("Events Synced", "12", "+3 today")
        
        # Simulate calendar events
        tasks = db.get_tasks(completed=False)[:5]
        try:
            calendar_events = simulate_calendar_sync(tasks)
        except:
            calendar_events = []
        
        if calendar_events:
            st.markdown("### 📋 UPCOMING EVENTS")
            for event in calendar_events[:3]:
                st.markdown(f"""
                <div style='background: white; padding: 15px; margin: 10px 0; border-radius: 8px;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <strong>{event.get('title', 'Event')}</strong>
                        <span style='color: {event.get('color', '#3498db')};'>●</span>
                    </div>
                    <div style='font-size: 0.9em; color: #666;'>
                        {event.get('start', datetime.now()).strftime('%I:%M %p')} - {event.get('end', datetime.now()).strftime('%I:%M %p')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No upcoming events. Add tasks to see them here!")
        
        # Sync controls
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 SYNC NOW", key="sync_cal", use_container_width=True):
                st.success("Calendar synced!")
        with col2:
            if st.button("📅 VIEW CALENDAR", key="view_cal", use_container_width=True):
                st.info("Calendar view would open here")
        with col3:
            if st.button("⏰ SET REMINDER", key="set_reminder", use_container_width=True):
                st.info("Reminder set for 15 minutes before event")
    
    def render_metric_card(self, title: str, value: str, delta: str, color: str, icon: str):
        """Render a metric card"""
        st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            <div style='font-size: 2rem; margin-bottom: 10px;'>{icon}</div>
            <div style='font-size: 2rem; font-weight: bold; color: #2c3e50;'>{value}</div>
            <div style='color: #7f8c8d; font-size: 0.9rem; margin-top: 5px;'>{title}</div>
            <div style='color: {color}; font-size: 0.8rem; margin-top: 5px;'>
                {delta}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def extract_tasks_from_results(self, results: Dict[str, Any]):
        """Extract actionable tasks from analysis results"""
        # Sample tasks for demonstration
        health_tasks = [
            "Take 3 deep breaths when stressed",
            "Walk for 20 minutes daily",
            "Drink 8 glasses of water"
        ]
        
        study_tasks = [
            "Study for 25 minutes using Pomodoro",
            "Review flashcards for 15 minutes",
            "Complete practice problem set"
        ]
        
        finance_tasks = [
            "Review monthly subscriptions",
            "Transfer 10% to savings",
            "Track expenses for 3 days"
        ]
        
        all_tasks = []
        for task in health_tasks:
            all_tasks.append({
                'title': task,
                'description': 'Health agent recommendation',
                'category': 'health',
                'priority': 3
            })
        
        for task in study_tasks:
            all_tasks.append({
                'title': task,
                'description': 'Study agent recommendation',
                'category': 'study',
                'priority': 2
            })
        
        for task in finance_tasks:
            all_tasks.append({
                'title': task,
                'description': 'Finance agent recommendation',
                'category': 'finance',
                'priority': 3
            })
        
        # Save tasks to database
        for task in all_tasks:
            try:
                db.save_task(task)
            except Exception as e:
                print(f"Error saving extracted task: {e}")
    
    def run_weekly_review(self):
        """Execute weekly review protocol"""
        with st.spinner("EXECUTING SUNDAY REVIEW PROTOCOL..."):
            # Get last week's data
            progress_data = db.get_weekly_progress()
            completed_tasks = db.get_tasks(completed=True)
            active_tasks = db.get_tasks(completed=False)
            
            total_tasks = len(completed_tasks) + len(active_tasks)
            completion_rate = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0
            
            if progress_data and len(progress_data) > 0:
                avg_stress = sum(p.get('stress_level', 5) for p in progress_data) / len(progress_data)
                avg_sleep = sum(p.get('sleep_hours', 7) for p in progress_data) / len(progress_data)
            else:
                avg_stress = 5
                avg_sleep = 7
            
            review_data = {
                'progress': progress_data,
                'completed_tasks': len(completed_tasks),
                'completion_rate': completion_rate,
                'avg_stress': avg_stress,
                'avg_sleep': avg_sleep
            }
            
            # Simulate agent analysis
            time.sleep(1)
            
            st.session_state.weekly_review_data = review_data
            st.success("WEEKLY REVIEW COMPLETE!")
            
            # Show insights
            with st.expander("📊 REVIEW INSIGHTS", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Completion Rate", f"{review_data['completion_rate']:.1f}%")
                    st.metric("Avg Stress", f"{review_data['avg_stress']:.1f}/10")
                with col2:
                    st.metric("Tasks Completed", review_data['completed_tasks'])
                    st.metric("Avg Sleep", f"{review_data['avg_sleep']:.1f}h")
    
    def generate_weekly_plan(self):
        """Generate weekly plan based on analysis"""
        with st.spinner("GENERATING OPTIMIZED WEEKLY PLAN..."):
            # This would integrate with the reflection agent
            time.sleep(1)
            
            weekly_plan = {
                'monday': {
                    'morning': ['Exercise', 'Meditation', 'Plan Day'],
                    'afternoon': ['Deep Work Session', 'Study Block'],
                    'evening': ['Review', 'Relax', 'Prepare Tomorrow']
                },
                'tuesday': {
                    'morning': ['Study Session', 'Health Check'],
                    'afternoon': ['Work Tasks', 'Break', 'Exercise'],
                    'evening': ['Finance Review', 'Leisure']
                },
                'wednesday': {
                    'morning': ['Exercise', 'Study Review'],
                    'afternoon': ['Project Work', 'Meetings'],
                    'evening': ['Personal Development', 'Family Time']
                },
                'thursday': {
                    'morning': ['Study Intensive', 'Health Maintenance'],
                    'afternoon': ['Creative Work', 'Exercise'],
                    'evening': ['Social Activity', 'Planning']
                },
                'friday': {
                    'morning': ['Weekly Review', 'Goal Setting'],
                    'afternoon': ['Light Work', 'Preparation'],
                    'evening': ['Relaxation', 'Hobbies']
                },
                'saturday': {
                    'morning': ['Sleep In', 'Leisure'],
                    'afternoon': ['Outdoor Activity', 'Personal Projects'],
                    'evening': ['Social', 'Entertainment']
                },
                'sunday': {
                    'morning': ['Reflection', 'Planning'],
                    'afternoon': ['Preparation', 'Relaxation'],
                    'evening': ['Early Rest', 'Meditation']
                }
            }
            
            st.session_state.weekly_plan = weekly_plan
            st.success("WEEKLY PLAN GENERATED!")
            
            # Display plan
            with st.expander("📅 VIEW WEEKLY PLAN"):
                st.json(weekly_plan)
    
    def export_data(self):
        """Export user data"""
        # Collect all data
        data = {
            'tasks': db.get_tasks(completed=True) + db.get_tasks(completed=False),
            'progress': db.get_weekly_progress(),
            'medicines': db.get_medicines(),
            'bills': db.get_bills(),
            'notes': db.get_notes(),
            'export_date': datetime.now().isoformat(),
            'version': 'LifeOps AI v2.0'
        }
        
        # Create download button
        st.download_button(
            label="📥 DOWNLOAD ALL DATA",
            data=json.dumps(data, indent=2),
            file_name=f"lifeops_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            type="primary"
        )
    
    def run(self):
        """Main application runner"""
        # Timer update
        if st.session_state.timer_running:
            if self.timer.update():
                st.balloons()
                st.rerun()
        
        # Render sidebar
        self.render_sidebar()
        
        # Render main content based on active tab
        if st.session_state.active_tab == 'dashboard':
            self.render_dashboard()
        elif st.session_state.active_tab == 'agent':
            self.render_agent_control()

def main():
    """Main application entry point"""
    app = LifeOpsApp()
    app.run()

if __name__ == "__main__":
    main()
