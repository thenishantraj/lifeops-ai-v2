"""
LifeOps AI v2 - Enhanced Multi-User Database Module
"""
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid

class LifeOpsDatabase:
    """SQLite database for LifeOps AI v2 with Multi-User Support"""
    
    def __init__(self, db_path="lifeops_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables and multi-user support"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                subscription_tier TEXT DEFAULT 'free',
                settings TEXT DEFAULT '{}'
            )
        ''')
        
        # Action items/todo list - NOW WITH USER_ID
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task TEXT NOT NULL,
                category TEXT,
                agent_source TEXT,
                due_date DATE,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Medicine vault - NOW WITH USER_ID
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                dosage TEXT,
                frequency TEXT,
                time_of_day TEXT,
                start_date DATE,
                end_date DATE,
                reminder_enabled BOOLEAN DEFAULT 1,
                last_taken TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Bill tracking - NOW WITH USER_ID
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                amount REAL,
                due_day INTEGER,
                category TEXT,
                is_recurring BOOLEAN DEFAULT 1,
                paid_this_month BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Study sessions - NOW WITH USER_ID
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE,
                duration_minutes INTEGER,
                subject TEXT,
                productivity_score INTEGER,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Weekly progress - NOW WITH USER_ID
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                week_start DATE,
                health_score INTEGER,
                finance_score INTEGER,
                study_score INTEGER,
                consistency_streak INTEGER,
                reflections TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Smart notes - NOW WITH USER_ID
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS smart_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT,
                content TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_action_items_user ON action_items(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_medicines_user ON medicines(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bills_user ON bills(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_study_sessions_user ON study_sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_smart_notes_user ON smart_notes(user_id)')
        
        conn.commit()
        conn.close()
    
    # ========== USER AUTHENTICATION METHODS ==========
    
    def hash_password(self, password: str) -> str:
        """Hash password for secure storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, email: str, password: str, name: str = "") -> Optional[int]:
        """Create a new user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, name)
                VALUES (?, ?, ?)
            ''', (email, password_hash, name))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            # Email already exists
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, email, name, joined_at, subscription_tier, settings
                FROM users 
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            
            user = cursor.fetchone()
            
            if user:
                # Update last login
                cursor.execute('''
                    UPDATE users 
                    SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (user['id'],))
                conn.commit()
            
            conn.close()
            return dict(user) if user else None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, name, joined_at, last_login, subscription_tier, settings
                FROM users 
                WHERE id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            return dict(user) if user else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    # ========== ACTION ITEMS METHODS (User-specific) ==========
    
    def add_action_item(self, user_id: int, task: str, category: str = None, 
                       agent_source: str = None, due_date: str = None) -> int:
        """Add action item for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO action_items (user_id, task, category, agent_source, due_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, task, category, agent_source, due_date))
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id
    
    def get_pending_actions(self, user_id: int) -> List[Dict]:
        """Get pending actions for specific user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM action_items 
            WHERE user_id = ? AND completed = 0 
            ORDER BY created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_all_actions(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get all actions for specific user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM action_items 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def mark_action_complete(self, user_id: int, action_id: int) -> bool:
        """Mark action as complete for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE action_items 
            SET completed = 1, completed_at = CURRENT_TIMESTAMP 
            WHERE id = ? AND user_id = ?
        ''', (action_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def delete_action(self, user_id: int, action_id: int) -> bool:
        """Delete action for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM action_items WHERE id = ? AND user_id = ?', (action_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def get_consistency_streak(self, user_id: int) -> int:
        """Calculate current streak of completed actions for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            WITH daily_completions AS (
                SELECT DATE(completed_at) as date
                FROM action_items 
                WHERE completed = 1 AND user_id = ?
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
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    # ========== MEDICINE VAULT METHODS (User-specific) ==========
    
    def add_medicine(self, user_id: int, name: str, dosage: str, 
                    frequency: str, time_of_day: str = None) -> int:
        """Add medicine for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO medicines (user_id, name, dosage, frequency, time_of_day, start_date)
            VALUES (?, ?, ?, ?, ?, DATE('now'))
        ''', (user_id, name, dosage, frequency, time_of_day))
        med_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return med_id
    
    def get_todays_medicines(self, user_id: int) -> List[Dict]:
        """Get today's medicines for specific user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM medicines 
            WHERE user_id = ? AND (end_date IS NULL OR end_date >= DATE('now'))
            ORDER BY time_of_day
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_all_medicines(self, user_id: int) -> List[Dict]:
        """Get all medicines for specific user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM medicines 
            WHERE user_id = ?
            ORDER BY name
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def delete_medicine(self, user_id: int, medicine_id: int) -> bool:
        """Delete medicine for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM medicines WHERE id = ? AND user_id = ?', (medicine_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def update_medicine_taken(self, user_id: int, medicine_id: int) -> bool:
        """Update last taken timestamp for medicine"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE medicines 
            SET last_taken = CURRENT_TIMESTAMP 
            WHERE id = ? AND user_id = ?
        ''', (medicine_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    # ========== BILL TRACKING METHODS (User-specific) ==========
    
    def add_bill(self, user_id: int, name: str, amount: float, 
                due_day: int, category: str = "Utilities") -> int:
        """Add bill for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bills (user_id, name, amount, due_day, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, name, amount, due_day, category))
        bill_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return bill_id
    
    def get_monthly_bills(self, user_id: int) -> List[Dict]:
        """Get monthly bills for specific user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM bills 
            WHERE user_id = ? AND is_recurring = 1
            ORDER BY due_day
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_all_bills(self, user_id: int) -> List[Dict]:
        """Get all bills for specific user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM bills 
            WHERE user_id = ?
            ORDER BY name
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def delete_bill(self, user_id: int, bill_id: int) -> bool:
        """Delete bill for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM bills WHERE id = ? AND user_id = ?', (bill_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def mark_bill_paid(self, user_id: int, bill_id: int) -> bool:
        """Mark bill as paid this month"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE bills 
            SET paid_this_month = 1 
            WHERE id = ? AND user_id = ?
        ''', (bill_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    # ========== STUDY SESSION METHODS (User-specific) ==========
    
    def add_study_session(self, user_id: int, duration_minutes: int, 
                         subject: str, productivity_score: int = 5) -> int:
        """Add study session for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO study_sessions (user_id, date, duration_minutes, subject, productivity_score)
            VALUES (?, DATE('now'), ?, ?, ?)
        ''', (user_id, duration_minutes, subject, productivity_score))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id
    
    def get_weekly_study_summary(self, user_id: int) -> Dict:
        """Get weekly study summary for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                SUM(duration_minutes) as total_minutes,
                AVG(productivity_score) as avg_score,
                COUNT(*) as sessions
            FROM study_sessions 
            WHERE user_id = ? AND date >= DATE('now', '-7 days')
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return {
            'total_minutes': result[0] or 0,
            'avg_score': float(result[1] or 0),
            'sessions': result[2] or 0
        }
    
    def get_study_sessions(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get recent study sessions for specific user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM study_sessions 
            WHERE user_id = ? 
            ORDER BY date DESC 
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ========== SMART NOTES METHODS (User-specific) ==========
    
    def add_note(self, user_id: int, title: str, content: str, tags: str = "") -> int:
        """Add note for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO smart_notes (user_id, title, content, tags)
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, content, tags))
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return note_id
    
    def get_notes(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get notes for specific user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM smart_notes 
            WHERE user_id = ? 
            ORDER BY updated_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_note(self, user_id: int, note_id: int, title: str, content: str, tags: str = "") -> bool:
        """Update note for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE smart_notes 
            SET title = ?, content = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        ''', (title, content, tags, note_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def delete_note(self, user_id: int, note_id: int) -> bool:
        """Delete note for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM smart_notes WHERE id = ? AND user_id = ?', (note_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    # ========== WEEKLY PROGRESS METHODS (User-specific) ==========
    
    def save_weekly_progress(self, user_id: int, week_start: str, health_score: int,
                           finance_score: int, study_score: int, consistency_streak: int,
                           reflections: str = "") -> int:
        """Save weekly progress for specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO weekly_progress 
            (user_id, week_start, health_score, finance_score, study_score, consistency_streak, reflections)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, week_start, health_score, finance_score, study_score, consistency_streak, reflections))
        progress_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return progress_id
    
    def get_weekly_progress(self, user_id: int, weeks: int = 4) -> List[Dict]:
        """Get weekly progress for specific user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM weekly_progress 
            WHERE user_id = ? 
            ORDER BY week_start DESC 
            LIMIT ?
        ''', (user_id, weeks))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ========== STATISTICS METHODS ==========
    
    def get_user_statistics(self, user_id: int) -> Dict:
        """Get comprehensive statistics for user"""
        stats = {}
        
        # Action statistics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total actions
        cursor.execute('SELECT COUNT(*) FROM action_items WHERE user_id = ?', (user_id,))
        stats['total_actions'] = cursor.fetchone()[0] or 0
        
        # Completed actions
        cursor.execute('SELECT COUNT(*) FROM action_items WHERE user_id = ? AND completed = 1', (user_id,))
        stats['completed_actions'] = cursor.fetchone()[0] or 0
        
        # Medicines count
        cursor.execute('SELECT COUNT(*) FROM medicines WHERE user_id = ?', (user_id,))
        stats['medicines_count'] = cursor.fetchone()[0] or 0
        
        # Bills count
        cursor.execute('SELECT COUNT(*) FROM bills WHERE user_id = ?', (user_id,))
        stats['bills_count'] = cursor.fetchone()[0] or 0
        
        # Notes count
        cursor.execute('SELECT COUNT(*) FROM smart_notes WHERE user_id = ?', (user_id,))
        stats['notes_count'] = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Calculate completion rate
        if stats['total_actions'] > 0:
            stats['completion_rate'] = (stats['completed_actions'] / stats['total_actions']) * 100
        else:
            stats['completion_rate'] = 0
        
        return stats
