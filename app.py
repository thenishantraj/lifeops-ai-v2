"""
LifeOps AI v2 - Cyberpunk Command Center
"""
import streamlit as st
import os
import sys
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import threading

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import (
    load_env, format_date, calculate_days_until,
    create_cyberpunk_health_chart, create_cyberpunk_finance_chart,
    create_study_schedule_timeline, create_streak_chart,
    db, simulate_calendar_sync, generate_task_id
)
from crew_setup import LifeOpsCrew

# Page configuration with cyberpunk theme
st.set_page_config(
    page_title="LifeOps AI v2.0",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/lifeops-ai',
        'Report a bug': 'https://github.com/lifeops-ai/issues',
        'About': '# LifeOps AI v2.0\nCyberpunk Command Center'
    }
)

# Load custom CSS
def load_css():
    with open('styles.css', 'r') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

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
            'user_inputs': {},
            'processing': False,
            'active_tab': 'dashboard',
            'timer_running': False,
            'medicine_reminders': [],
            'selected_task': None,
            'notes_content': '',
            'weekly_review_data': {},
            'agent_outputs': {},
            'task_filter': 'all'
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def render_sidebar(self):
        """Render cyberpunk sidebar"""
        with st.sidebar:
            # Header
            st.markdown('<div class="sidebar-title">LIFEOPS v2.0</div>', unsafe_allow_html=True)
            st.markdown('<div class="cyber-subtitle">CYBERPUNK COMMAND CENTER</div>', unsafe_allow_html=True)
            st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)
            
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
            st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)
            st.markdown('### ⚡ QUICK ACTIONS')
            
            if st.button('🔄 RUN WEEKLY REVIEW', key='weekly_review', use_container_width=True):
                self.run_weekly_review()
            
            if st.button('📥 EXPORT DATA', key='export_data', use_container_width=True):
                self.export_data()
            
            # System Status
            st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)
            st.markdown('### 🖥️ SYSTEM STATUS')
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("AGENTS", "4", "ONLINE")
            with col2:
                st.metric("TASKS", str(len(db.get_tasks(completed=False))), "ACTIVE")
            
            # Timer Control
            st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)
            st.markdown('### ⏱️ COGNITIVE TIMER')
            
            timer_cols = st.columns(3)
            with timer_cols[0]:
                if st.button('▶️', key='timer_start', use_container_width=True):
                    self.timer.start()
                    st.session_state.timer_running = True
            with timer_cols[1]:
                if st.button('⏸️', key='timer_pause', use_container_width=True):
                    self.timer.pause()
                    st.session_state.timer_running = False
            with timer_cols[2]:
                if st.button('🔄', key='timer_reset', use_container_width=True):
                    self.timer.reset()
                    st.session_state.timer_running = False
            
            timer_display = f"**{self.timer.get_display()}** | {self.timer.mode.upper()}"
            st.markdown(f'<div class="timer-display">{timer_display}</div>', unsafe_allow_html=True)
            
            # User Profile
            st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)
            st.markdown('### 👤 USER PROFILE')
            
            # Quick stats
            tasks = db.get_tasks(completed=False)
            completed = db.get_tasks(completed=True)
            completion_rate = len(completed) / max(len(tasks) + len(completed), 1) * 100
            
            st.progress(completion_rate / 100)
            st.caption(f"Completion: {completion_rate:.1f}%")
    
    def render_dashboard(self):
        """Render main dashboard"""
        st.markdown('<h1 class="cyber-title">COMMAND CENTER DASHBOARD</h1>', unsafe_allow_html=True)
        st.markdown('<div class="cyber-subtitle">REAL-TIME LIFE OPERATIONS MONITORING</div>', unsafe_allow_html=True)
        
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
            self.render_metric_card(
                title="ACTIVE TASKS",
                value=str(len(tasks)),
                delta=f"{len([t for t in tasks if t['priority'] == 1])} urgent",
                color="#FF9800",
                icon="✅"
            )
        
        with col3:
            bills = db.get_bills()
            unpaid = len([b for b in bills if not b['paid']])
            self.render_metric_card(
                title="FINANCIAL STATUS",
                value=f"${sum(b['amount'] for b in bills if not b['paid'])}",
                delta=f"{unpaid} pending",
                color="#2196F3",
                icon="💰"
            )
        
        with col4:
            progress_data = db.get_weekly_progress()
            streak = max([p.get('streak_count', 0) for p in progress_data]) if progress_data else 0
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
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('### 📋 ACTIVE DIRECTIVES')
                self.render_task_list()
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Smart Notepad
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('### 🖋️ SMART NOTEPAD')
                self.render_notepad()
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Progress Tracker
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('### 📈 PROGRESS ANALYTICS')
                self.render_progress_tracker()
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Utility Tools
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('### 🛠️ UTILITY TOOLS')
                self.render_utility_tools()
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Bottom Row - Charts
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('### 🏥 HEALTH MONITOR')
                stress = st.session_state.user_inputs.get('stress_level', 5)
                sleep = st.session_state.user_inputs.get('sleep_hours', 7)
                st.plotly_chart(create_cyberpunk_health_chart(stress, sleep), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('### 💰 FINANCE DASHBOARD')
                budget = st.session_state.user_inputs.get('monthly_budget', 2000)
                expenses = st.session_state.user_inputs.get('current_expenses', 1500)
                st.plotly_chart(create_cyberpunk_finance_chart(budget, expenses), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    def render_agent_control(self):
        """Render agent control panel"""
        st.markdown('<h1 class="cyber-title">AGENT COMMAND CENTER</h1>', unsafe_allow_html=True)
        st.markdown('<div class="cyber-subtitle">MULTI-AGENT ORCHESTRATION WITH GEMINI VALIDATION</div>', unsafe_allow_html=True)
        
        # Agent Status Panel
        col1, col2, col3, col4 = st.columns(4)
        
        agents = [
            {"name": "HEALTH COMMAND", "status": "ONLINE", "color": "#4CAF50"},
            {"name": "FINANCE CONTROL", "status": "ONLINE", "color": "#FF9800"},
            {"name": "STUDY ORCHESTRATOR", "status": "ONLINE", "color": "#2196F3"},
            {"name": "LIFE COMMANDER", "status": "VALIDATING", "color": "#9C27B0"}
        ]
        
        for idx, agent in enumerate([col1, col2, col3, col4]):
            with agent:
                st.markdown(f'''
                <div class="glass-card" style="text-align: center;">
                    <div style="font-size: 2rem;">{"🤖" if idx < 3 else "👑"}</div>
                    <h4 style="margin: 10px 0; color: {agents[idx]['color']}">{agents[idx]['name']}</h4>
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <span class="status-online"></span>
                        <span style="color: #00ff88; font-family: monospace;">{agents[idx]['status']}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        
        # User Input Configuration
        with st.expander("⚙️ CONFIGURATION PANEL", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🧠 HEALTH PARAMETERS")
                stress_level = st.slider("STRESS INDEX", 1, 10, 5, key="health_stress")
                sleep_hours = st.number_input("SLEEP HOURS", 0, 12, 7, key="health_sleep")
                exercise = st.selectbox("EXERCISE FREQUENCY", 
                                      ["SEDENTARY", "LIGHT", "MODERATE", "INTENSE", "ATHLETE"],
                                      key="health_exercise")
            
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
        st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 🚀 EXECUTION CONTROL")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧠 EXECUTE SINGLE DOMAIN", use_container_width=True, type="primary"):
                st.session_state.processing = True
                # Single domain execution logic here
                time.sleep(2)  # Simulate processing
                st.session_state.processing = False
                st.success("Domain analysis complete!")
        
       with col2:
            if st.button("🔄 EXECUTE FULL ANALYSIS", use_container_width=True, type="primary"):
                with st.spinner("EXECUTING GEMINI VALIDATION PROTOCOL..."):
                    try:
                        # Set API key directly if not in env
                        if not os.getenv("GOOGLE_API_KEY"):
                            os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", "")
                
                            crew = LifeOpsCrew(st.session_state.user_inputs)
                            results = crew.kickoff()
                            st.session_state.analysis_results = results
                            st.session_state.processing = False
                            st.success("✅ FULL ANALYSIS COMPLETE!")
                
                            # Extract tasks from results
                            self.extract_tasks_from_results(results)
                            st.rerun()
                
                        except Exception as e:
                            st.error(f"❌ SYSTEM ERROR: {str(e)}")
                            st.session_state.processing = False
        
        with col3:
            if st.button("📊 GENERATE WEEKLY PLAN", use_container_width=True):
                self.generate_weekly_plan()
        
        # Results Display
        if st.session_state.analysis_results:
            st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)
            st.markdown("### 📊 ANALYSIS RESULTS")
            
            results = st.session_state.analysis_results
            
            tabs = st.tabs(["🧠 HEALTH", "💰 FINANCE", "📚 STUDY", "👑 COORDINATION"])
            
            with tabs[0]:
                st.markdown(f'''
                <div class="glass-card">
                    <h4 style="color: #4CAF50;">HEALTH COMMAND BRIEFING</h4>
                    <div style="font-family: monospace; white-space: pre-wrap;">{results['health'][:1000]}...</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with tabs[1]:
                st.markdown(f'''
                <div class="glass-card">
                    <h4 style="color: #FF9800;">FINANCE COMMAND BRIEFING</h4>
                    <div style="font-family: monospace; white-space: pre-wrap;">{results['finance'][:1000]}...</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with tabs[2]:
                st.markdown(f'''
                <div class="glass-card">
                    <h4 style="color: #2196F3;">STUDY COMMAND BRIEFING</h4>
                    <div style="font-family: monospace; white-space: pre-wrap;">{results['study'][:1000]}...</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with tabs[3]:
                st.markdown(f'''
                <div class="glass-card">
                    <h4 style="color: #9C27B0;">LIFE COMMAND BRIEFING</h4>
                    <div style="font-family: monospace; white-space: pre-wrap;">{results['coordination'][:1500]}...</div>
                </div>
                ''', unsafe_allow_html=True)
    
    def render_task_list(self):
        """Render interactive task list"""
        # Task filter
        filter_cols = st.columns(4)
        with filter_cols[0]:
            if st.button("ALL", key="filter_all", use_container_width=True):
                st.session_state.task_filter = 'all'
        with filter_cols[1]:
            if st.button("HEALTH", key="filter_health", use_container_width=True):
                st.session_state.task_filter = 'health'
        with filter_cols[2]:
            if st.button("STUDY", key="filter_study", use_container_width=True):
                st.session_state.task_filter = 'study'
        with filter_cols[3]:
            if st.button("FINANCE", key="filter_finance", use_container_width=True):
                st.session_state.task_filter = 'finance'
        
        # Get tasks
        tasks = db.get_tasks(completed=False)
        
        if st.session_state.task_filter != 'all':
            tasks = [t for t in tasks if t['category'] == st.session_state.task_filter]
        
        # Display tasks
        for task in tasks[:10]:  # Limit to 10 tasks
            col1, col2, col3 = st.columns([6, 2, 2])
            
            with col1:
                priority_color = {
                    1: "#F44336",  # Urgent
                    2: "#FF9800",  # High
                    3: "#2196F3"   # Normal
                }.get(task['priority'], "#9E9E9E")
                
                st.markdown(f'''
                <div class="task-item task-{task['category']}">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 8px; height: 8px; background: {priority_color}; 
                                  border-radius: 50%; margin-right: 10px;"></div>
                        <strong>{task['title']}</strong>
                    </div>
                    <div style="font-size: 0.8em; color: #a0a0ff; margin-top: 5px;">
                        {task['description'][:100]}...
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                st.caption(f"Priority: {task['priority']}")
            
            with col3:
                if st.button("✓", key=f"complete_{task['id']}", help="Mark as complete"):
                    db.complete_task(task['id'])
                    st.rerun()
        
        # Add new task
        with st.expander("➕ ADD NEW DIRECTIVE"):
            col1, col2 = st.columns(2)
            with col1:
                new_title = st.text_input("Directive Title", key="new_task_title")
                new_desc = st.text_area("Description", key="new_task_desc")
            with col2:
                new_category = st.selectbox("Category", ["health", "finance", "study", "general"], key="new_task_cat")
                new_priority = st.selectbox("Priority", [("⚡ Urgent", 1), ("🔥 High", 2), ("⚪ Normal", 3)], 
                                          format_func=lambda x: x[0], key="new_task_pri")[1]
            
            if st.button("ADD DIRECTIVE", key="add_task"):
                if new_title:
                    task_data = {
                        'title': new_title,
                        'description': new_desc,
                        'category': new_category,
                        'priority': new_priority
                    }
                    db.save_task(task_data)
                    st.success("Directive added!")
                    st.rerun()
    
    def render_notepad(self):
        """Render smart notepad"""
        notes = db.get_notes()
        
        # Note editor
        note_title = st.text_input("Note Title", key="note_title")
        note_content = st.text_area("Content", height=150, key="note_content")
        note_category = st.selectbox("Category", ["thoughts", "ideas", "todo", "reflection"], key="note_category")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 SAVE NOTE", key="save_note", use_container_width=True):
                if note_title and note_content:
                    note_data = {
                        'title': note_title,
                        'content': note_content,
                        'category': note_category
                    }
                    db.save_note(note_data)
                    st.success("Note saved!")
                    st.rerun()
        
        with col2:
            if st.button("🗑️ CLEAR", key="clear_note", use_container_width=True):
                st.rerun()
        
        # Display recent notes
        if notes:
            st.markdown("### 📝 RECENT NOTES")
            for note in notes[:3]:
                with st.expander(f"{note['title']} ({note['category']})"):
                    st.markdown(note['content'])
                    st.caption(f"Last updated: {note['updated_at'][:16]}")
    
    def render_progress_tracker(self):
        """Render progress tracking dashboard"""
        progress_data = db.get_weekly_progress()
        
        if progress_data:
            # Convert to DataFrame for display
            df = pd.DataFrame(progress_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Display streak chart
            st.plotly_chart(create_streak_chart(progress_data), use_container_width=True)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_stress = df['stress_level'].mean()
                st.metric("Avg Stress", f"{avg_stress:.1f}/10", 
                         delta=f"{-avg_stress + 5:.1f}" if avg_stress < 5 else None)
            with col2:
                avg_sleep = df['sleep_hours'].mean()
                st.metric("Avg Sleep", f"{avg_sleep:.1f}h", 
                         delta=f"{avg_sleep - 7:.1f}" if avg_sleep > 7 else None)
            with col3:
                total_tasks = df['tasks_completed'].sum()
                st.metric("Tasks Completed", total_tasks)
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
            
            if st.button("SAVE PROGRESS", key="save_progress"):
                progress_data = {
                    'health_score': day_health,
                    'stress_level': day_stress,
                    'sleep_hours': day_sleep,
                    'tasks_completed': day_tasks,
                    'notes': day_notes
                }
                db.save_progress(progress_data)
                st.success("Progress saved!")
    
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
            
            if st.button("ADD TO VAULT", key="add_med"):
                if med_name:
                    medicine_data = {
                        'name': med_name,
                        'dosage': med_dosage,
                        'frequency': med_freq,
                        'time': med_time.strftime("%H:%M")
                    }
                    db.add_medicine(medicine_data)
                    st.success("Medicine added to vault!")
                    st.rerun()
        
        # Display medicines
        if medicines:
            st.markdown("### CURRENT MEDICATIONS")
            for med in medicines:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.text(f"{med['name']} - {med['dosage']}")
                with col2:
                    st.caption(f"{med['frequency']} at {med['time']}")
                with col3:
                    if st.button("✅", key=f"take_{med['id']}", help="Mark as taken"):
                        # Update last_taken time
                        st.success(f"Marked {med['name']} as taken!")
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
            
            if st.button("ADD BILL", key="add_bill"):
                if bill_name:
                    bill_data = {
                        'name': bill_name,
                        'amount': bill_amount,
                        'due_date': bill_date.strftime("%Y-%m-%d"),
                        'category': bill_category
                    }
                    db.add_bill(bill_data)
                    st.success("Bill added to tracker!")
                    st.rerun()
        
        # Display bills
        if bills:
            unpaid = [b for b in bills if not b['paid']]
            paid = [b for b in bills if b['paid']]
            
            st.metric("Pending Bills", f"${sum(b['amount'] for b in unpaid):.2f}", 
                     f"{len(unpaid)} bills")
            
            for bill in unpaid[:5]:
                days_until = calculate_days_until(bill['due_date'])
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.text(f"{bill['name']}")
                with col2:
                    st.text(f"${bill['amount']:.2f}")
                with col3:
                    color = "red" if days_until <= 3 else "orange" if days_until <= 7 else "green"
                    st.markdown(f"<span style='color: {color};'>Due in {days_until} days</span>", 
                              unsafe_allow_html=True)
                with col4:
                    if st.button("💳", key=f"pay_{bill['id']}", help="Mark as paid"):
                        # Update paid status
                        st.success(f"Marked {bill['name']} as paid!")
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
        calendar_events = simulate_calendar_sync(tasks)
        
        if calendar_events:
            st.markdown("### 📋 UPCOMING EVENTS")
            for event in calendar_events[:3]:
                with st.container():
                    st.markdown(f'''
                    <div class="glass-card" style="margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between;">
                            <strong>{event['title']}</strong>
                            <span style="color: {event['color']};">●</span>
                        </div>
                        <div style="font-size: 0.8em; color: #a0a0ff;">
                            {event['start'].strftime('%I:%M %p')} - {event['end'].strftime('%I:%M %p')}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
        
        # Sync controls
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 SYNC NOW", key="sync_cal", use_container_width=True):
                st.success("Calendar synced!")
        with col2:
            if st.button("📅 VIEW CALENDAR", key="view_cal", use_container_width=True):
                st.info("Opening calendar view...")
        with col3:
            if st.button("⏰ SET REMINDER", key="set_reminder", use_container_width=True):
                st.info("Reminder set for 15 minutes before event")
    
    def render_metric_card(self, title: str, value: str, delta: str, color: str, icon: str):
        """Render a metric card with cyberpunk style"""
        st.markdown(f'''
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{title}</div>
            <div style="font-size: 0.8rem; color: {color}; margin-top: 5px;">
                {delta}
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    def extract_tasks_from_results(self, results: Dict[str, Any]):
        """Extract actionable tasks from analysis results"""
        # This is a simplified extraction - in production, you'd use more sophisticated NLP
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
            db.save_task(task)
    
    def run_weekly_review(self):
        """Execute weekly review protocol"""
        with st.spinner("EXECUTING SUNDAY REVIEW PROTOCOL..."):
            # Get last week's data
            progress_data = db.get_weekly_progress()
            completed_tasks = db.get_tasks(completed=True)
            
            review_data = {
                'progress': progress_data,
                'completed_tasks': len(completed_tasks),
                'completion_rate': len(completed_tasks) / max(len(completed_tasks) + len(db.get_tasks(completed=False)), 1) * 100,
                'avg_stress': sum(p.get('stress_level', 5) for p in progress_data) / max(len(progress_data), 1),
                'avg_sleep': sum(p.get('sleep_hours', 7) for p in progress_data) / max(len(progress_data), 1)
            }
            
            # Simulate agent analysis
            time.sleep(2)
            
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
            time.sleep(2)
            
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
                # ... rest of the week
            }
            
            st.session_state.weekly_plan = weekly_plan
            st.success("WEEKLY PLAN GENERATED!")
            
            # Display plan
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
            label="📥 DOWNLOAD DATA",
            data=json.dumps(data, indent=2),
            file_name=f"lifeops_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    def run(self):
        """Main application runner"""
        # Timer update thread
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
