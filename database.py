"""
LifeOps AI v2 - Enhanced Multi-User Database Module with Migration Support
"""
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class LifeOpsDatabase:
    """SQLite database for LifeOps AI v2 with Multi-User Support and Migration"""
    
    def __init__(self, db_path="lifeops_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables and multi-user support"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if we need to migrate from old schema
        self._check_and_migrate(cursor)
        
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
                completed_at TIMESTAMP
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
                last_taken TIMESTAMP
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
                paid_this_month BOOLEAN DEFAULT 0
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
                notes TEXT
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
                reflections TEXT
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
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _check_and_migrate(self, cursor):
        """Check for old schema and migrate if needed"""
        try:
            # Check if old tables exist without user_id
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='action_items'")
            if cursor.fetchone():
                # Check if user_id column exists in action_items
                cursor.execute("PRAGMA table_info(action_items)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'user_id' not in columns:
                    print("⚠️ Detected old schema. Please delete the existing database file 'lifeops_data.db'")
                    print("⚠️ Then restart the application to use the new multi-user schema.")
                    return False
            return True
        except Exception as e:
            print(f"Error checking schema: {e}")
            return False
    
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
            SELECT COUNT(*) as streak FROM (
                SELECT DATE(completed_at) as date
                FROM action_items 
                WHERE completed = 1 AND user_id = ?
                GROUP BY DATE(completed_at)
            )
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
        if result and result[0]:
            return {
                'total_minutes': result[0],
                'avg_score': float(result[1] or 0),
                'sessions': result[2]
            }
        return {
            'total_minutes': 0,
            'avg_score': 0,
            'sessions': 0
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
    
    # ========== STATISTICS METHODS ==========
    
    def get_user_statistics(self, user_id: int) -> Dict:
        """Get comprehensive statistics for user"""
        stats = {}
        
        try:
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
                
        except Exception as e:
            print(f"Error getting user statistics: {e}")
            # Return default stats
            stats = {
                'total_actions': 0,
                'completed_actions': 0,
                'medicines_count': 0,
                'bills_count': 0,
                'notes_count': 0,
                'completion_rate': 0
            }
        
        return stats
    
    def check_database_health(self) -> Dict:
        """Check database health and provide status"""
        health = {
            'tables': [],
            'user_count': 0,
            'status': 'healthy'
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            health['tables'] = [table[0] for table in tables]
            
            # Count users
            cursor.execute("SELECT COUNT(*) FROM users")
            health['user_count'] = cursor.fetchone()[0] or 0
            
            conn.close()
            
        except Exception as e:
            health['status'] = f'error: {str(e)}'
            
        return health
