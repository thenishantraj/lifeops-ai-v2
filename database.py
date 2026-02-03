"""
LifeOps AI v2 - Database Module
"""
import sqlite3
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any

class LifeOpsDatabase:
    """SQLite database for LifeOps AI v2 features"""
    
    def __init__(self, db_path="lifeops_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Action items/todo list
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                category TEXT,
                agent_source TEXT,
                due_date DATE,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        
        # Medicine vault
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dosage TEXT,
                frequency TEXT,
                time_of_day TEXT,
                start_date DATE,
                end_date DATE,
                reminder_enabled BOOLEAN DEFAULT 1,
                last_taken TIMESTAMP
            )
        ''')
        
        # Bill tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL,
                due_day INTEGER,
                category TEXT,
                is_recurring BOOLEAN DEFAULT 1,
                paid_this_month BOOLEAN DEFAULT 0
            )
        ''')
        
        # Study sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                duration_minutes INTEGER,
                subject TEXT,
                productivity_score INTEGER,
                notes TEXT
            )
        ''')
        
        # Weekly progress
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_progress (
                week_start DATE,
                health_score INTEGER,
                finance_score INTEGER,
                study_score INTEGER,
                consistency_streak INTEGER,
                reflections TEXT
            )
        ''')
        
        # Smart notes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS smart_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Action Items methods
    def add_action_item(self, task: str, category: str = None, agent_source: str = None, due_date: str = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO action_items (task, category, agent_source, due_date)
            VALUES (?, ?, ?, ?)
        ''', (task, category, agent_source, due_date))
        conn.commit()
        conn.close()
    
    def get_pending_actions(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM action_items WHERE completed = 0 ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def mark_action_complete(self, action_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE action_items 
            SET completed = 1, completed_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (action_id,))
        conn.commit()
        conn.close()
    
    def get_consistency_streak(self) -> int:
        """Calculate current streak of completed actions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            WITH daily_completions AS (
                SELECT DATE(completed_at) as date
                FROM action_items 
                WHERE completed = 1 
                GROUP BY DATE(completed_at)
            ),
            ordered_dates AS (
                SELECT date,
                       LAG(date) OVER (ORDER BY date) as prev_date
                FROM daily_completions
            )
            SELECT COUNT(*) as streak
            FROM ordered_dates
            WHERE date = DATE(prev_date, '+1 day')
            OR prev_date IS NULL
        ''')
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    # Medicine vault methods
    def add_medicine(self, name: str, dosage: str, frequency: str, time_of_day: str = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO medicines (name, dosage, frequency, time_of_day, start_date)
            VALUES (?, ?, ?, ?, DATE('now'))
        ''', (name, dosage, frequency, time_of_day))
        conn.commit()
        conn.close()
    
    def get_todays_medicines(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM medicines 
            WHERE end_date IS NULL OR end_date >= DATE('now')
            ORDER BY time_of_day
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # Bill tracking methods
    def add_bill(self, name: str, amount: float, due_day: int, category: str = "Utilities"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bills (name, amount, due_day, category)
            VALUES (?, ?, ?, ?)
        ''', (name, amount, due_day, category))
        conn.commit()
        conn.close()
    
    def get_monthly_bills(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bills WHERE is_recurring = 1')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # Study session methods
    def add_study_session(self, duration_minutes: int, subject: str, productivity_score: int = 5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO study_sessions (date, duration_minutes, subject, productivity_score)
            VALUES (DATE('now'), ?, ?, ?)
        ''', (duration_minutes, subject, productivity_score))
        conn.commit()
        conn.close()
    
    def get_weekly_study_summary(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                SUM(duration_minutes) as total_minutes,
                AVG(productivity_score) as avg_score,
                COUNT(*) as sessions
            FROM study_sessions 
            WHERE date >= DATE('now', '-7 days')
        ''')
        result = cursor.fetchone()
        conn.close()
        return {
            'total_minutes': result[0] or 0,
            'avg_score': result[1] or 0,
            'sessions': result[2] or 0
        }
    
    # Smart notes methods
    def add_note(self, title: str, content: str, tags: str = ""):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO smart_notes (title, content, tags)
            VALUES (?, ?, ?)
        ''', (title, content, tags))
        conn.commit()
        conn.close()
    
    def get_notes(self, limit: int = 20) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM smart_notes ORDER BY updated_at DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
