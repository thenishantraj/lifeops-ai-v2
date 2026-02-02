"""
LifeOps AI v2 - Complete Fixed Version
"""
import streamlit as st
import os
import sys
import time
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="LifeOps AI v2.0",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple Database Manager
class DatabaseManager:
    """Simple SQLite database manager"""
    
    def __init__(self, db_path: str = "lifeops_simple.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                priority INTEGER DEFAULT 3,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id TEXT PRIMARY KEY,
                date TEXT DEFAULT CURRENT_DATE,
                health_score REAL DEFAULT 50,
                stress_level INTEGER DEFAULT 5,
                sleep_hours REAL DEFAULT 7,
                tasks_completed INTEGER DEFAULT 0,
                notes TEXT
            )
        ''')
        
        # Notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                category TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bills table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id TEXT PRIMARY KEY,
                name TEXT,
                amount REAL,
                due_date TEXT,
                paid BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_task(self, task_data: Dict[str, Any]) -> str:
        """Save a task to database"""
        task_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (id, title, description, category, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            task_id,
            task_data.get('title', 'Untitled Task'),
            task_data.get('description', ''),
            task_data.get('category', 'general'),
            task_data.get('priority', 3)
        ))
        
        conn.commit()
        conn.close()
        return task_id
    
    def complete_task(self, task_id: str):
        """Mark task as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
    
    def get_tasks(self, completed: bool = False, limit: int = 50) -> List[Dict]:
        """Get tasks from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, category, priority, created_at, completed
            FROM tasks 
            WHERE completed = ?
            ORDER BY priority ASC, created_at DESC
            LIMIT ?
        ''', (1 if completed else 0, limit))
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'category': row[3],
                'priority': row[4],
                'created_at': row[5],
                'completed': bool(row[6])
            })
        
        conn.close()
        return tasks
    
    def save_progress(self, progress_data: Dict[str, Any]) -> str:
        """Save daily progress"""
        progress_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO progress (id, health_score, stress_level, sleep_hours, tasks_completed, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            progress_id,
            progress_data.get('health_score', 50),
            progress_data.get('stress_level', 5),
            progress_data.get('sleep_hours', 7),
            progress_data.get('tasks_completed', 0),
            progress_data.get('notes', '')
        ))
        
        conn.commit()
        conn.close()
        return progress_id
    
    def get_weekly_progress(self) -> List[Dict]:
        """Get last 7 days of progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, health_score, stress_level, sleep_hours, tasks_completed
            FROM progress
            ORDER BY date DESC
            LIMIT 7
        ''')
        
        progress = []
        for row in cursor.fetchall():
            progress.append({
                'date': row[0],
                'health_score': float(row[1] or 50),
                'stress_level': int(row[2] or 5),
                'sleep_hours': float(row[3] or 7),
                'tasks_completed': int(row[4] or 0)
            })
        
        conn.close()
        
        # If no data, return sample data
        if not progress:
            today = datetime.now().strftime('%Y-%m-%d')
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                progress.append({
                    'date': date,
                    'health_score': 60 + i * 5,
                    'stress_level': 7 - i,
                    'sleep_hours': 6.5 + i * 0.5,
                    'tasks_completed': i + 2
                })
        
        return progress
    
    def save_note(self, note_data: Dict[str, Any]) -> str:
        """Save note to database"""
        note_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notes (id, title, content, category)
            VALUES (?, ?, ?, ?)
        ''', (
            note_id,
            note_data['title'],
            note_data['content'],
            note_data.get('category', 'general')
        ))
        
        conn.commit()
        conn.close()
        return note_id
    
    def get_notes(self, limit: int = 20) -> List[Dict]:
        """Get notes from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, category, created_at
            FROM notes
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        notes = []
        for row in cursor.fetchall():
            notes.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'category': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        return notes
    
    def add_bill(self, bill_data: Dict[str, Any]) -> str:
        """Add bill to tracker"""
        bill_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bills (id, name, amount, due_date, paid)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            bill_id,
            bill_data['name'],
            bill_data['amount'],
            bill_data.get('due_date', datetime.now().strftime('%Y-%m-%d')),
            bill_data.get('paid', 0)
        ))
        
        conn.commit()
        conn.close()
        return bill_id
    
    def get_bills(self) -> List[Dict]:
        """Get all bills"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, amount, due_date, paid
            FROM bills
            ORDER BY due_date
        ''')
        
        bills = []
        for row in cursor.fetchall():
            bills.append({
                'id': row[0],
                'name': row[1],
                'amount': float(row[2] or 0),
                'due_date': row[3],
                'paid': bool(row[4])
            })
        
        conn.close()
        return bills

# Initialize database
db = DatabaseManager()

# Smart Timer Class
class SmartTimer:
    """Pomodoro timer"""
    
    def __init__(self):
        self.is_running = False
        self.remaining = 25 * 60  # 25 minutes
        self.mode = "focus"
        
    def start(self):
        self.is_running = True
        
    def pause(self):
        self.is_running = False
        
    def reset(self):
        self.is_running = False
        self.remaining = 25 * 60
        self.mode = "focus"
        
    def get_display(self) -> str:
        minutes = self.remaining // 60
        seconds = self.remaining % 60
        return f"{minutes:02d}:{seconds:02d}"

# Main Application Class
class LifeOpsApp:
    """Main application class"""
    
    def __init__(self):
        self.timer = SmartTimer()
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state"""
        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = 'dashboard'
        if 'task_filter' not in st.session_state:
            st.session_state.task_filter = 'all'
        if 'user_inputs' not in st.session_state:
            st.session_state.user_inputs = {
                'stress_level': 5,
                'sleep_hours': 7,
                'monthly_budget': 2000,
                'current_expenses': 1500
            }
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
    
    def render_sidebar(self):
        """Render sidebar"""
        with st.sidebar:
            st.title("🚀 LifeOps v2.0")
            st.caption("Personal Productivity Dashboard")
            
            st.divider()
            st.subheader("Navigation")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Dashboard", use_container_width=True):
                    st.session_state.active_tab = 'dashboard'
                    st.rerun()
            with col2:
                if st.button("🤖 Agents", use_container_width=True):
                    st.session_state.active_tab = 'agent'
                    st.rerun()
            
            st.divider()
            st.subheader("Quick Stats")
            
            tasks = db.get_tasks(completed=False)
            completed = db.get_tasks(completed=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Active Tasks", len(tasks))
            with col2:
                st.metric("Completed", len(completed))
            
            st.divider()
            st.subheader("Timer")
            
            timer_cols = st.columns(3)
            with timer_cols[0]:
                if st.button("▶️", use_container_width=True):
                    self.timer.start()
            with timer_cols[1]:
                if st.button("⏸️", use_container_width=True):
                    self.timer.pause()
            with timer_cols[2]:
                if st.button("🔄", use_container_width=True):
                    self.timer.reset()
            
            st.markdown(f"**{self.timer.get_display()}** - {self.timer.mode.title()}")
            
            # Progress
            st.divider()
            total = len(tasks) + len(completed)
            if total > 0:
                completion_rate = (len(completed) / total) * 100
                st.progress(completion_rate / 100)
                st.caption(f"Completion: {completion_rate:.1f}%")
    
    def render_dashboard(self):
        """Render main dashboard"""
        st.title("📊 Dashboard")
        st.caption("Your Personal Command Center")
        
        # Top Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.render_metric_card("Health Score", "82", "+2%", "#10B981", "🏥")
        
        with col2:
            tasks = db.get_tasks(completed=False)
            st.metric("Pending Tasks", len(tasks))
        
        with col3:
            bills = db.get_bills()
            unpaid = sum(b['amount'] for b in bills if not b['paid'])
            st.metric("Unpaid Bills", f"${unpaid:.0f}")
        
        with col4:
            progress = db.get_weekly_progress()
            streak = len([p for p in progress if p['tasks_completed'] > 0])
            st.metric("Current Streak", f"{streak} days")
        
        st.divider()
        
        # Main Content
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Active Tasks")
            self.render_task_list()
            
            st.subheader("📝 Quick Note")
            self.render_quick_note()
        
        with col2:
            st.subheader("📈 Progress Overview")
            self.render_progress_chart()
            
            st.subheader("🛠️ Quick Tools")
            self.render_quick_tools()
    
    def render_task_list(self):
        """Render task list"""
        # Filter buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("All", use_container_width=True):
                st.session_state.task_filter = 'all'
                st.rerun()
        with col2:
            if st.button("Health", use_container_width=True):
                st.session_state.task_filter = 'health'
                st.rerun()
        with col3:
            if st.button("Study", use_container_width=True):
                st.session_state.task_filter = 'study'
                st.rerun()
        with col4:
            if st.button("Finance", use_container_width=True):
                st.session_state.task_filter = 'finance'
                st.rerun()
        
        # Get and filter tasks
        tasks = db.get_tasks(completed=False)
        if st.session_state.task_filter != 'all':
            tasks = [t for t in tasks if t['category'] == st.session_state.task_filter]
        
        # Display tasks
        if tasks:
            for task in tasks:
                col1, col2, col3 = st.columns([4, 1, 1])
                
                with col1:
                    category_color = {
                        'health': '#10B981',
                        'finance': '#F59E0B',
                        'study': '#3B82F6',
                        'general': '#8B5CF6'
                    }.get(task['category'], '#6B7280')
                    
                    st.markdown(f"""
                    <div style='padding: 10px; margin: 5px 0; border-left: 4px solid {category_color}; background: #F9FAFB; border-radius: 4px;'>
                        <strong>{task['title']}</strong><br>
                        <small style='color: #6B7280;'>{task['description'][:60]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    priority_labels = {1: "⚡", 2: "🔥", 3: "⚪"}
                    st.write(priority_labels.get(task['priority'], "⚪"))
                
                with col3:
                    if st.button("✓", key=f"complete_{task['id']}"):
                        db.complete_task(task['id'])
                        st.success(f"Completed: {task['title']}")
                        time.sleep(0.5)
                        st.rerun()
        else:
            st.info("No tasks found. Add some tasks to get started!")
        
        # Add new task
        with st.expander("Add New Task"):
            title = st.text_input("Task Title")
            description = st.text_area("Description")
            category = st.selectbox("Category", ["general", "health", "finance", "study"])
            priority = st.selectbox("Priority", [("Normal", 3), ("High", 2), ("Urgent", 1)], 
                                  format_func=lambda x: x[0])[1]
            
            if st.button("Add Task", type="primary") and title:
                task_data = {
                    'title': title,
                    'description': description,
                    'category': category,
                    'priority': priority
                }
                db.save_task(task_data)
                st.success("Task added!")
                time.sleep(0.5)
                st.rerun()
    
    def render_quick_note(self):
        """Render quick note form"""
        title = st.text_input("Note Title", key="note_title")
        content = st.text_area("Content", height=100, key="note_content")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save", use_container_width=True, type="primary") and title and content:
                note_data = {
                    'title': title,
                    'content': content
                }
                db.save_note(note_data)
                st.success("Note saved!")
                time.sleep(0.5)
                st.rerun()
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.rerun()
        
        # Show recent notes
        notes = db.get_notes(limit=3)
        if notes:
            st.markdown("**Recent Notes:**")
            for note in notes:
                with st.expander(f"{note['title']}"):
                    st.write(note['content'])
    
    def render_progress_chart(self):
        """Render progress chart"""
        progress_data = db.get_weekly_progress()
        
        if progress_data:
            # Create a simple chart
            df = pd.DataFrame(progress_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            fig = go.Figure()
            
            # Add health score line
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['health_score'],
                mode='lines+markers',
                name='Health Score',
                line=dict(color='#10B981', width=3)
            ))
            
            # Add stress level line
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['stress_level'] * 10,  # Scale for visibility
                mode='lines+markers',
                name='Stress Level (scaled)',
                line=dict(color='#EF4444', width=3)
            ))
            
            fig.update_layout(
                height=300,
                showlegend=True,
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=20, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show metrics
            col1, col2 = st.columns(2)
            with col1:
                avg_health = df['health_score'].mean()
                st.metric("Avg Health", f"{avg_health:.0f}")
            with col2:
                avg_stress = df['stress_level'].mean()
                st.metric("Avg Stress", f"{avg_stress:.1f}/10")
        else:
            st.info("No progress data yet. Log your daily progress!")
        
        # Log progress form
        with st.expander("Log Daily Progress"):
            col1, col2 = st.columns(2)
            with col1:
                health = st.slider("Health Score", 0, 100, 75)
                stress = st.slider("Stress Level", 1, 10, 5)
            with col2:
                sleep = st.number_input("Sleep Hours", 0.0, 12.0, 7.0, step=0.5)
                tasks_completed = st.number_input("Tasks Completed", 0, 50, 0)
            
            notes = st.text_area("Notes for today")
            
            if st.button("Save Progress", type="primary"):
                progress_data = {
                    'health_score': health,
                    'stress_level': stress,
                    'sleep_hours': sleep,
                    'tasks_completed': tasks_completed,
                    'notes': notes
                }
                db.save_progress(progress_data)
                st.success("Progress saved!")
                time.sleep(0.5)
                st.rerun()
    
    def render_quick_tools(self):
        """Render quick tools"""
        tabs = st.tabs(["💰 Bills", "📅 Calendar", "📊 Export"])
        
        with tabs[0]:
            st.subheader("Bill Tracker")
            
            # Add bill form
            with st.expander("Add New Bill"):
                name = st.text_input("Bill Name")
                amount = st.number_input("Amount", 0.0, 10000.0, 100.0)
                due_date = st.date_input("Due Date")
                
                if st.button("Add Bill", type="primary") and name and amount > 0:
                    bill_data = {
                        'name': name,
                        'amount': amount,
                        'due_date': due_date.strftime("%Y-%m-%d")
                    }
                    db.add_bill(bill_data)
                    st.success("Bill added!")
                    time.sleep(0.5)
                    st.rerun()
            
            # Show bills
            bills = db.get_bills()
            if bills:
                unpaid = [b for b in bills if not b['paid']]
                if unpaid:
                    st.write(f"**{len(unpaid)} unpaid bills:**")
                    for bill in unpaid[:3]:
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            st.write(bill['name'])
                        with col2:
                            st.write(f"${bill['amount']:.2f}")
                        with col3:
                            if st.button("💳", key=f"pay_{bill['id']}"):
                                st.success(f"Paid {bill['name']}")
                else:
                    st.success("All bills paid! 🎉")
            else:
                st.info("No bills tracked yet.")
        
        with tabs[1]:
            st.subheader("Calendar Integration")
            
            # Mock calendar events
            tasks = db.get_tasks(completed=False)[:5]
            
            st.info("Calendar would sync with your tasks here")
            
            if tasks:
                st.write("**Upcoming tasks:**")
                for i, task in enumerate(tasks[:3]):
                    event_time = datetime.now() + timedelta(hours=i*2)
                    st.write(f"⏰ {event_time.strftime('%I:%M %p')} - {task['title']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Sync Now"):
                    st.success("Calendar synced!")
            with col2:
                if st.button("View Full Calendar"):
                    st.info("Calendar view would open here")
        
        with tabs[2]:
            st.subheader("Data Export")
            
            # Collect data
            data = {
                'tasks': db.get_tasks(completed=True) + db.get_tasks(completed=False),
                'progress': db.get_weekly_progress(),
                'notes': db.get_notes(),
                'bills': db.get_bills(),
                'export_date': datetime.now().isoformat()
            }
            
            # Download button
            st.download_button(
                label="📥 Download All Data",
                data=json.dumps(data, indent=2),
                file_name=f"lifeops_export_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                type="primary"
            )
            
            st.divider()
            st.write("**Quick Stats Export:**")
            
            tasks_count = len(data['tasks'])
            completed_count = len([t for t in data['tasks'] if t['completed']])
            bills_count = len(data['bills'])
            
            st.write(f"• Total Tasks: {tasks_count}")
            st.write(f"• Completed: {completed_count}")
            st.write(f"• Bills Tracked: {bills_count}")
    
    def render_agent_control(self):
        """Render agent control panel"""
        st.title("🤖 AI Agents")
        st.caption("Intelligent Life Optimization")
        
        # Agent status cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style='background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
                <div style='font-size: 2em;'>🧠</div>
                <h4 style='color: #10B981;'>Health Agent</h4>
                <div style='color: #10B981; font-weight: bold;'>ONLINE</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
                <div style='font-size: 2em;'>💰</div>
                <h4 style='color: #F59E0B;'>Finance Agent</h4>
                <div style='color: #10B981; font-weight: bold;'>ONLINE</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
                <div style='font-size: 2em;'>📚</div>
                <h4 style='color: #3B82F6;'>Study Agent</h4>
                <div style='color: #10B981; font-weight: bold;'>ONLINE</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style='background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
                <div style='font-size: 2em;'>👑</div>
                <h4 style='color: #8B5CF6;'>Coordinator</h4>
                <div style='color: #F59E0B; font-weight: bold;'>ANALYZING</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Configuration panel
        with st.expander("⚙️ Configuration", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Health Parameters")
                stress = st.slider("Stress Level", 1, 10, 5)
                sleep = st.number_input("Sleep Hours", 0, 12, 7)
                exercise = st.selectbox("Exercise", ["None", "Light", "Moderate", "Intense"])
            
            with col2:
                st.subheader("Study Parameters")
                study_hours = st.number_input("Study Hours/Day", 0, 12, 3)
                exam_days = st.number_input("Days Until Exam", 0, 365, 30)
                focus = st.slider("Focus Duration (min)", 15, 120, 45)
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.subheader("Finance Parameters")
                budget = st.number_input("Monthly Budget", 0, 10000, 2000)
                expenses = st.number_input("Current Expenses", 0, 10000, 1500)
            
            with col4:
                st.subheader("Primary Goal")
                goal = st.text_area("What do you want to achieve?", 
                                  "Balance study, health, and finances effectively")
            
            # Store inputs
            st.session_state.user_inputs = {
                'stress_level': stress,
                'sleep_hours': sleep,
                'monthly_budget': budget,
                'current_expenses': expenses,
                'study_hours': study_hours,
                'goal': goal
            }
        
        st.divider()
        
        # Execution controls
        st.subheader("🚀 Execute Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧠 Analyze Health", use_container_width=True, type="primary"):
                with st.spinner("Health agent analyzing..."):
                    time.sleep(2)
                    st.session_state.analysis_results = {
                        'health': "✅ **HEALTH ANALYSIS COMPLETE**\n\n**Recommendations:**\n1. Increase sleep to 8 hours\n2. Add 30-min daily walk\n3. Practice 5-min breathing exercises when stressed\n4. Stay hydrated (8 glasses/day)\n\n**Expected Benefits:**\n• 20% energy increase\n• 30% stress reduction\n• Better focus and mood"
                    }
                    st.success("Health analysis complete!")
        
        with col2:
            if st.button("💰 Analyze Finances", use_container_width=True, type="primary"):
                with st.spinner("Finance agent analyzing..."):
                    time.sleep(2)
                    st.session_state.analysis_results = {
                        'finance': "✅ **FINANCE ANALYSIS COMPLETE**\n\n**Recommendations:**\n1. Create $500 emergency fund\n2. Cut unnecessary subscriptions ($50/month)\n3. Automate bill payments\n4. Track expenses daily\n\n**Projections:**\n• Save $200/month\n• 3-month safety buffer\n• Reduced financial stress"
                    }
                    st.success("Finance analysis complete!")
        
        with col3:
            if st.button("📚 Analyze Study", use_container_width=True, type="primary"):
                with st.spinner("Study agent analyzing..."):
                    time.sleep(2)
                    st.session_state.analysis_results = {
                        'study': "✅ **STUDY ANALYSIS COMPLETE**\n\n**Recommendations:**\n1. Pomodoro technique (25min work, 5min break)\n2. Morning study sessions (most productive)\n3. Weekly review sessions\n4. Active recall practice\n\n**Schedule:**\n• 3hrs/day focused study\n• 1hr review every Sunday\n• Practice tests weekly"
                    }
                    st.success("Study analysis complete!")
        
        # Full analysis button
        st.divider()
        if st.button("🔄 EXECUTE FULL LIFE ANALYSIS", use_container_width=True, type="primary"):
            with st.spinner("All agents analyzing your life..."):
                time.sleep(3)
                st.session_state.analysis_results = {
                    'health': "✅ **HEALTH AGENT:** Optimal sleep (8hrs), daily exercise (30min), stress management techniques implemented.",
                    'finance': "✅ **FINANCE AGENT:** Budget optimized, $200/month savings identified, expense tracking automated.",
                    'study': "✅ **STUDY AGENT:** Efficient schedule created (3hrs/day), focus techniques recommended, review system setup.",
                    'coordinator': "✅ **LIFE COORDINATOR:** All domains integrated. Priority: Study (60%), Health (25%), Finance (15%). Weekly check-ins scheduled."
                }
                st.success("✅ FULL LIFE ANALYSIS COMPLETE!")
                
                # Add sample tasks
                sample_tasks = [
                    {'title': 'Morning meditation', 'description': '5-minute breathing exercise', 'category': 'health', 'priority': 3},
                    {'title': 'Study session 1', 'description': '25-minute focused study', 'category': 'study', 'priority': 2},
                    {'title': 'Track expenses', 'description': 'Log today\'s spending', 'category': 'finance', 'priority': 3},
                    {'title': 'Evening walk', 'description': '30-minute walk after dinner', 'category': 'health', 'priority': 3},
                    {'title': 'Weekly review', 'description': 'Review progress and plan next week', 'category': 'general', 'priority': 2}
                ]
                
                for task in sample_tasks:
                    db.save_task(task)
        
        # Display results
        if st.session_state.get('analysis_results'):
            st.divider()
            st.subheader("📊 Analysis Results")
            
            results = st.session_state.analysis_results
            
            tabs = st.tabs(["Health", "Finance", "Study", "Coordination"])
            
            with tabs[0]:
                st.markdown(f"""
                <div style='background: #F0F9FF; padding: 20px; border-radius: 10px; border-left: 4px solid #10B981;'>
                    {results.get('health', 'No health analysis yet.')}
                </div>
                """, unsafe_allow_html=True)
            
            with tabs[1]:
                st.markdown(f"""
                <div style='background: #FFFBEB; padding: 20px; border-radius: 10px; border-left: 4px solid #F59E0B;'>
                    {results.get('finance', 'No finance analysis yet.')}
                </div>
                """, unsafe_allow_html=True)
            
            with tabs[2]:
                st.markdown(f"""
                <div style='background: #EFF6FF; padding: 20px; border-radius: 10px; border-left: 4px solid #3B82F6;'>
                    {results.get('study', 'No study analysis yet.')}
                </div>
                """, unsafe_allow_html=True)
            
            with tabs[3]:
                st.markdown(f"""
                <div style='background: #F5F3FF; padding: 20px; border-radius: 10px; border-left: 4px solid #8B5CF6;'>
                    {results.get('coordinator', 'No coordination analysis yet.')}
                </div>
                """, unsafe_allow_html=True)
            
            # Generate plan button
            if st.button("📋 Generate Action Plan", type="primary"):
                with st.spinner("Creating your personalized action plan..."):
                    time.sleep(2)
                    st.success("Action plan generated! Check your tasks dashboard.")
    
    def render_metric_card(self, title, value, delta, color, icon):
        """Render a metric card"""
        st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;'>
            <div style='font-size: 2em;'>{icon}</div>
            <div style='font-size: 2em; font-weight: bold; color: #1F2937;'>{value}</div>
            <div style='color: #6B7280; font-size: 0.9em; margin-top: 5px;'>{title}</div>
            <div style='color: {color}; font-size: 0.8em; margin-top: 5px;'>{delta}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Main application runner"""
        self.render_sidebar()
        
        if st.session_state.active_tab == 'dashboard':
            self.render_dashboard()
        else:
            self.render_agent_control()

# Run the app
if __name__ == "__main__":
    app = LifeOpsApp()
    app.run()
