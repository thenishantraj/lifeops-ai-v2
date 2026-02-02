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
import time

class DatabaseManager:
    """SQLite database manager for progress tracking"""
    
    def __init__(self, db_path: str = "lifeops_v2.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables with error handling"""
        try:
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
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"⚠️ Database initialization error: {e}")
            self.create_simple_database()
    
    def create_simple_database(self):
        """Create a simpler database as fallback"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple tasks table
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
            
            # Simple progress table
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
            
            conn.commit()
            conn.close()
            print("✅ Simple database created as fallback")
        except Exception as e:
            print(f"❌ Simple database creation error: {e}")
    
    def save_task(self, task_data: Dict[str, Any]) -> str:
        """Save a task to database"""
        try:
            task_id = str(uuid.uuid4())
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tasks (id, title, description, agent, priority, created_at, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_id,
                task_data.get('title', 'Untitled Task'),
                task_data.get('description', ''),
                task_data.get('agent', 'system'),
                task_data.get('priority', 3),
                datetime.now().isoformat(),
                task_data.get('category', 'general')
            ))
            
            conn.commit()
            conn.close()
            return task_id
        except Exception as e:
            print(f"Error saving task: {e}")
            return f"error_{int(time.time())}"
    
    def complete_task(self, task_id: str):
        """Mark task as completed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tasks 
                SET completed = 1, completed_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), task_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error completing task: {e}")
    
    def get_tasks(self, completed: bool = False, limit: int = 50) -> List[Dict]:
        """Get tasks from database"""
        try:
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
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []
    
    def save_progress(self, progress_data: Dict[str, Any]) -> str:
        """Save daily progress"""
        try:
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
                progress_data.get('health_score', 50),
                progress_data.get('finance_score', 50),
                progress_data.get('study_score', 50),
                progress_data.get('stress_level', 5),
                progress_data.get('sleep_hours', 7),
                progress_data.get('tasks_completed', 0),
                progress_data.get('notes', '')
            ))
            
            conn.commit()
            conn.close()
            return progress_id
        except Exception as e:
            print(f"Error saving progress: {e}")
            return f"error_{int(time.time())}"
    
    def get_weekly_progress(self) -> List[Dict]:
        """Get last 7 days of progress"""
        try:
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
                    'health_score': float(row[1] or 50),
                    'finance_score': float(row[2] or 50),
                    'study_score': float(row[3] or 50),
                    'stress_level': int(row[4] or 5),
                    'sleep_hours': float(row[5] or 7),
                    'tasks_completed': int(row[6] or 0)
                })
            
            conn.close()
            
            # If no data, return sample data
            if not progress:
                today = datetime.now().strftime('%Y-%m-%d')
                progress.append({
                    'date': today,
                    'health_score': 75,
                    'finance_score': 60,
                    'study_score': 80,
                    'stress_level': 4,
                    'sleep_hours': 7.5,
                    'tasks_completed': 3
                })
            
            return progress
        except Exception as e:
            print(f"Error getting weekly progress: {e}")
            # Return sample data
            today = datetime.now().strftime('%Y-%m-%d')
            return [{
                'date': today,
                'health_score': 75,
                'finance_score': 60,
                'study_score': 80,
                'stress_level': 4,
                'sleep_hours': 7.5,
                'tasks_completed': 3
            }]
    
    def add_medicine(self, medicine_data: Dict[str, Any]) -> str:
        """Add medicine to vault"""
        try:
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
        except Exception as e:
            print(f"Error adding medicine: {e}")
            return f"error_{int(time.time())}"
    
    def get_medicines(self) -> List[Dict]:
        """Get all medicines"""
        try:
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
        except Exception as e:
            print(f"Error getting medicines: {e}")
            return []
    
    def add_bill(self, bill_data: Dict[str, Any]) -> str:
        """Add bill to tracker"""
        try:
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
        except Exception as e:
            print(f"Error adding bill: {e}")
            return f"error_{int(time.time())}"
    
    def get_bills(self, month: Optional[str] = None) -> List[Dict]:
        """Get bills for current month"""
        try:
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
                    'amount': float(row[2] or 0),
                    'due_date': row[3],
                    'category': row[4],
                    'paid': bool(row[5])
                })
            
            conn.close()
            return bills
        except Exception as e:
            print(f"Error getting bills: {e}")
            return []
    
    def save_note(self, note_data: Dict[str, Any]) -> str:
        """Save note to database"""
        try:
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
        except Exception as e:
            print(f"Error saving note: {e}")
            return f"error_{int(time.time())}"
    
    def get_notes(self, category: Optional[str] = None) -> List[Dict]:
        """Get notes from database"""
        try:
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
        except Exception as e:
            print(f"Error getting notes: {e}")
            return []

# Initialize database
db = DatabaseManager()

def load_env():
    """Load environment variables"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        # Try Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
                api_key = st.secrets['GOOGLE_API_KEY']
        except:
            pass
    
    if not api_key:
        print("⚠️ Warning: GOOGLE_API_KEY not found")
        api_key = "dummy_key_for_testing"  # Fallback for testing
    
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
        return 30  # Default

# Rest of the functions remain the same...
