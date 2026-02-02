"""
LifeOps AI v2 - Enhanced Utility Functions
"""
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import uuid
import hashlib

class DatabaseManager:
    """SQLite database manager for progress tracking"""
    
    def __init__(self, db_path: str = "lifeops_v2.db"):
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
                agent TEXT,
                priority INTEGER,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP,
                completed_at TIMESTAMP,
                category TEXT,
                streak_count INTEGER DEFAULT 0
            )
        ''')
        
        # Progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id TEXT PRIMARY KEY,
                date TEXT,
                health_score REAL,
                finance_score REAL,
                study_score REAL,
                stress_level INTEGER,
                sleep_hours REAL,
                tasks_completed INTEGER,
                notes TEXT
            )
        ''')
        
        # Medicine vault
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicine_vault (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                dosage TEXT,
                frequency TEXT,
                time TEXT,
                reminder_enabled BOOLEAN DEFAULT 1,
                last_taken TIMESTAMP
            )
        ''')
        
        # Bills tracker
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                amount REAL,
                due_date TEXT,
                recurring BOOLEAN DEFAULT 1,
                category TEXT,
                paid BOOLEAN DEFAULT 0
            )
        ''')
        
        # Notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                category TEXT,
                pinned BOOLEAN DEFAULT 0
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
            INSERT INTO tasks (id, title, description, agent, priority, created_at, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            task_data['title'],
            task_data.get('description', ''),
            task_data.get('agent', 'system'),
            task_data.get('priority', 3),
            datetime.now().isoformat(),
            task_data.get('category', 'general')
        ))
        
        conn.commit()
        conn.close()
        return task_id
    
    def complete_task(self, task_id: str):
        """Mark task as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks 
            SET completed = 1, completed_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), task_id))
        
        conn.commit()
        conn.close()
    
    def get_tasks(self, completed: bool = False, limit: int = 50) -> List[Dict]:
        """Get tasks from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, agent, priority, created_at, completed, category
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
                'agent': row[3],
                'priority': row[4],
                'created_at': row[5],
                'completed': bool(row[6]),
                'category': row[7]
            })
        
        conn.close()
        return tasks
    
    def save_progress(self, progress_data: Dict[str, Any]) -> str:
        """Save daily progress"""
        progress_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO progress (id, date, health_score, finance_score, study_score, 
                                stress_level, sleep_hours, tasks_completed, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            progress_id,
            progress_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            progress_data.get('health_score', 0),
            progress_data.get('finance_score', 0),
            progress_data.get('study_score', 0),
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
            SELECT date, health_score, finance_score, study_score, stress_level, 
                   sleep_hours, tasks_completed
            FROM progress
            ORDER BY date DESC
            LIMIT 7
        ''')
        
        progress = []
        for row in cursor.fetchall():
            progress.append({
                'date': row[0],
                'health_score': row[1],
                'finance_score': row[2],
                'study_score': row[3],
                'stress_level': row[4],
                'sleep_hours': row[5],
                'tasks_completed': row[6]
            })
        
        conn.close()
        return progress
    
    def add_medicine(self, medicine_data: Dict[str, Any]) -> str:
        """Add medicine to vault"""
        medicine_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO medicine_vault (id, name, dosage, frequency, time, reminder_enabled)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            medicine_id,
            medicine_data['name'],
            medicine_data.get('dosage', ''),
            medicine_data.get('frequency', 'daily'),
            medicine_data.get('time', '09:00'),
            medicine_data.get('reminder_enabled', 1)
        ))
        
        conn.commit()
        conn.close()
        return medicine_id
    
    def get_medicines(self) -> List[Dict]:
        """Get all medicines"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, dosage, frequency, time, reminder_enabled, last_taken
            FROM medicine_vault
            ORDER BY time
        ''')
        
        medicines = []
        for row in cursor.fetchall():
            medicines.append({
                'id': row[0],
                'name': row[1],
                'dosage': row[2],
                'frequency': row[3],
                'time': row[4],
                'reminder_enabled': bool(row[5]),
                'last_taken': row[6]
            })
        
        conn.close()
        return medicines
    
    def add_bill(self, bill_data: Dict[str, Any]) -> str:
        """Add bill to tracker"""
        bill_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bills (id, name, amount, due_date, recurring, category, paid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            bill_id,
            bill_data['name'],
            bill_data['amount'],
            bill_data.get('due_date', datetime.now().strftime('%Y-%m-%d')),
            bill_data.get('recurring', 1),
            bill_data.get('category', 'utilities'),
            bill_data.get('paid', 0)
        ))
        
        conn.commit()
        conn.close()
        return bill_id
    
    def get_bills(self, month: Optional[str] = None) -> List[Dict]:
        """Get bills for current month"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if month:
            cursor.execute('''
                SELECT id, name, amount, due_date, category, paid
                FROM bills
                WHERE strftime('%Y-%m', due_date) = ?
                ORDER BY due_date
            ''', (month,))
        else:
            cursor.execute('''
                SELECT id, name, amount, due_date, category, paid
                FROM bills
                ORDER BY due_date
            ''')
        
        bills = []
        for row in cursor.fetchall():
            bills.append({
                'id': row[0],
                'name': row[1],
                'amount': row[2],
                'due_date': row[3],
                'category': row[4],
                'paid': bool(row[5])
            })
        
        conn.close()
        return bills
    
    def save_note(self, note_data: Dict[str, Any]) -> str:
        """Save note to database"""
        note_id = note_data.get('id', str(uuid.uuid4()))
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO notes (id, title, content, created_at, updated_at, category, pinned)
            VALUES (?, ?, ?, COALESCE((SELECT created_at FROM notes WHERE id = ?), ?), ?, ?, ?)
        ''', (
            note_id,
            note_data['title'],
            note_data['content'],
            note_id,
            now,
            now,
            note_data.get('category', 'general'),
            note_data.get('pinned', 0)
        ))
        
        conn.commit()
        conn.close()
        return note_id
    
    def get_notes(self, category: Optional[str] = None) -> List[Dict]:
        """Get notes from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT id, title, content, created_at, updated_at, category, pinned
                FROM notes
                WHERE category = ?
                ORDER BY pinned DESC, updated_at DESC
            ''', (category,))
        else:
            cursor.execute('''
                SELECT id, title, content, created_at, updated_at, category, pinned
                FROM notes
                ORDER BY pinned DESC, updated_at DESC
            ''')
        
        notes = []
        for row in cursor.fetchall():
            notes.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'created_at': row[3],
                'updated_at': row[4],
                'category': row[5],
                'pinned': bool(row[6])
            })
        
        conn.close()
        return notes

# Initialize database
db = DatabaseManager()

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
        return date.strftime("%b %d, %Y")
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

def create_cyberpunk_health_chart(stress_level: int, sleep_hours: int = 7):
    """Create cyberpunk-style health chart"""
    fig = go.Figure()
    
    # Health metrics radial chart
    categories = ['Stress', 'Sleep', 'Energy', 'Recovery', 'Focus']
    values = [stress_level, min(sleep_hours, 10), 8, 6, 7]
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line_color='rgb(102, 126, 234)',
        name='Health Metrics'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                gridcolor='rgba(255,255,255,0.1)',
                tickcolor='rgba(255,255,255,0.5)'
            ),
            bgcolor='rgba(10,10,20,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffff',
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    return fig

def create_cyberpunk_finance_chart(budget: float, expenses: float):
    """Create cyberpunk-style finance chart"""
    categories = ['Rent', 'Food', 'Transport', 'Health', 'Study', 'Entertainment', 'Savings']
    values = [800, 300, 150, 100, 200, 150, budget - expenses]
    
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=values,
        marker_color=['#667eea', '#764ba2', '#9f7aea', '#ed64a6', '#f56565', '#ed8936', '#48bb78'],
        marker_line_color='rgba(255,255,255,0.3)',
        marker_line_width=1,
        opacity=0.8
    )])
    
    fig.update_layout(
        title=dict(
            text="Budget Allocation Matrix",
            font=dict(color='white', size=14)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffff',
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            tickangle=45
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)'
        )
    )
    
    return fig

def create_study_schedule_timeline(days_until_exam: int, study_hours: int):
    """Create study schedule timeline with cyberpunk theme"""
    dates = []
    hours = []
    
    for i in range(min(days_until_exam, 14)):
        date = datetime.now() + timedelta(days=i)
        dates.append(date.strftime("%b %d"))
        
        # Smart scheduling with tapering
        if i == 0:
            hours.append(study_hours)
        elif i < days_until_exam - 7:
            hours.append(study_hours * 1.1)
        elif i < days_until_exam - 3:
            hours.append(study_hours * 0.9)
        elif i == days_until_exam - 1:
            hours.append(study_hours * 0.5)
        else:
            hours.append(study_hours * 0.7)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=hours,
        mode='lines+markers',
        line=dict(color='#00ffff', width=3, shape='spline'),
        marker=dict(size=8, color='#ff00ff'),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 255, 0.1)',
        name='Study Hours'
    ))
    
    fig.update_layout(
        title=dict(
            text="Cognitive Load Timeline",
            font=dict(color='white', size=14)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffff',
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            tickangle=45
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            title="Hours/Day"
        )
    )
    
    return fig

def create_streak_chart(streak_data: List[Dict]):
    """Create consistency streak chart"""
    if not streak_data:
        return create_empty_chart("No streak data yet")
    
    dates = [item['date'] for item in streak_data]
    counts = [item['streak_count'] for item in streak_data]
    
    fig = go.Figure(data=[go.Bar(
        x=dates,
        y=counts,
        marker_color='#00ff88',
        marker_line_color='rgba(0, 255, 136, 0.5)',
        marker_line_width=1,
        opacity=0.8,
        name='Consistency Streak'
    )])
    
    fig.update_layout(
        title=dict(
            text="Consistency Streak Dashboard",
            font=dict(color='white', size=14)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffff',
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            tickangle=45
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            title="Days"
        )
    )
    
    return fig

def create_empty_chart(message: str):
    """Create empty chart placeholder"""
    fig = go.Figure()
    
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color="white")
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200
    )
    
    return fig

def generate_task_id(title: str) -> str:
    """Generate deterministic task ID"""
    return hashlib.md5(title.encode()).hexdigest()[:8]

def simulate_calendar_sync(tasks: List[Dict], start_date: datetime = None):
    """Simulate Google Calendar sync"""
    if start_date is None:
        start_date = datetime.now()
    
    calendar_events = []
    for i, task in enumerate(tasks[:5]):  # Limit to 5 events
        event_time = start_date + timedelta(hours=i*2)
        calendar_events.append({
            'title': task['title'],
            'start': event_time,
            'end': event_time + timedelta(hours=1),
            'color': get_category_color(task.get('category', 'general'))
        })
    
    return calendar_events

def get_category_color(category: str) -> str:
    """Get color for task category"""
    color_map = {
        'health': '#4CAF50',
        'finance': '#FF9800',
        'study': '#2196F3',
        'general': '#9C27B0',
        'urgent': '#F44336'
    }
    return color_map.get(category.lower(), '#667eea')