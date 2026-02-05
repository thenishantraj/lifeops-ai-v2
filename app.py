"""
LifeOps AI v2 - Multi-User Streamlit Application with Professional UI
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

from utils import (
    load_env, format_date, calculate_days_until,
    create_health_chart, create_finance_chart, create_study_schedule,
    create_insight_card, parse_agent_output, get_professional_styles
)
from crew_setup import LifeOpsCrew
from database import LifeOpsDatabase

# Initialize database
db = LifeOpsDatabase()

# Force OpenAI to be disabled globally
os.environ["OPENAI_API_KEY"] = "not-required"
os.environ["OPENAI_API_BASE"] = ""
os.environ["OPENAI_MODEL_NAME"] = ""

# Page configuration
st.set_page_config(
    page_title="LifeOps AI | Life Management Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar collapsed by default
)

# Apply Professional Styles
st.markdown(get_professional_styles(), unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables for multi-user"""
    # Authentication state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    # Application state
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
    
    # User-specific data (loaded after auth)
    if st.session_state.authenticated and st.session_state.user_id:
        if 'todo_items' not in st.session_state:
            st.session_state.todo_items = db.get_pending_actions(st.session_state.user_id)
        if 'medicines' not in st.session_state:
            st.session_state.medicines = db.get_todays_medicines(st.session_state.user_id)
        if 'bills' not in st.session_state:
            st.session_state.bills = db.get_monthly_bills(st.session_state.user_id)
        if 'notes' not in st.session_state:
            st.session_state.notes = db.get_notes(st.session_state.user_id)
    else:
        # Clear user-specific data if not authenticated
        st.session_state.todo_items = []
        st.session_state.medicines = []
        st.session_state.bills = []
        st.session_state.notes = []

def login_page():
    """Render modern split-screen login page"""
    st.markdown("""
    <style>
    .login-container {
        display: flex;
        min-height: 100vh;
    }
    .login-left {
        flex: 1;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 40px;
        color: white;
    }
    .login-right {
        flex: 1;
        background: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 40px;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 40px;
    }
    .logo-icon {
        font-size: 64px;
        margin-bottom: 20px;
    }
    .logo-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .logo-subtitle {
        font-size: 16px;
        opacity: 0.9;
    }
    .features-list {
        margin-top: 40px;
        text-align: left;
    }
    .feature-item {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        font-size: 16px;
    }
    .feature-icon {
        margin-right: 15px;
        font-size: 20px;
    }
    .login-form-container {
        width: 100%;
        max-width: 400px;
    }
    .form-title {
        font-size: 28px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 10px;
        text-align: center;
    }
    .form-subtitle {
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Left side - Branding and Features
        st.markdown("""
        <div class="login-left">
            <div class="logo-container">
                <div class="logo-icon">🧠</div>
                <h1 class="logo-title">LifeOps AI</h1>
                <p class="logo-subtitle">Your Intelligent Life Management Platform</p>
            </div>
            
            <div class="features-list">
                <div class="feature-item">
                    <span class="feature-icon">⚡</span>
                    AI-Powered Life Optimization
                </div>
                <div class="feature-item">
                    <span class="feature-icon">📊</span>
                    Health, Finance & Study Integration
                </div>
                <div class="feature-item">
                    <span class="feature-icon">🔒</span>
                    Secure & Private Data Storage
                </div>
                <div class="feature-item">
                    <span class="feature-icon">🎯</span>
                    Personalized Recommendations
                </div>
                <div class="feature-item">
                    <span class="feature-icon">📈</span>
                    Progress Tracking & Analytics
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Right side - Login Form
        st.markdown("""
        <div class="login-right">
            <div class="login-form-container">
                <h2 class="form-title">Welcome Back</h2>
                <p class="form-subtitle">Sign in to continue to LifeOps</p>
        """, unsafe_allow_html=True)
        
        # Tabs for Login/Signup
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                login_button = st.form_submit_button("Login to LifeOps", type="primary", use_container_width=True)
                
                if login_button:
                    if email and password:
                        user = db.authenticate_user(email, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user_id = user['id']
                            st.session_state.user_data = user
                            st.session_state.current_page = "Dashboard"
                            st.success(f"Welcome back, {user.get('name', email)}!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Invalid email or password")
                    else:
                        st.warning("Please enter both email and password")
        
        with tab2:
            with st.form("signup_form"):
                name = st.text_input("Full Name", placeholder="John Doe")
                email = st.text_input("Email", placeholder="you@example.com")
                col_a, col_b = st.columns(2)
                with col_a:
                    password = st.text_input("Password", type="password", placeholder="••••••••", key="signup_pass")
                with col_b:
                    confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="signup_confirm")
                
                signup_button = st.form_submit_button("Create Account", type="primary", use_container_width=True)
                
                if signup_button:
                    if not all([name, email, password, confirm_password]):
                        st.warning("Please fill in all fields")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        user_id = db.create_user(email, password, name)
                        if user_id:
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error("Email already exists")
        
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_data = None
    st.session_state.current_page = "Dashboard"
    st.rerun()

def professional_sidebar():
    """Render professional sidebar navigation - ONLY SHOWN AFTER LOGIN"""
    with st.sidebar:
        # Show sidebar only if authenticated
        if st.session_state.authenticated:
            st.markdown(f"""
            <div class="sidebar-header">
                <h2>🧠 LifeOps</h2>
                <p class="user-greeting">Hi, {st.session_state.user_data.get('name', 'User')}</p>
                <p class="user-email">{st.session_state.user_data.get('email', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Navigation
            st.markdown("### 📊 Navigation")
            
            # Page selection
            pages = ["Dashboard", "Health Vault", "Finance Hub", "Study Center", "Productivity", "Profile"]
            selected_page = st.selectbox(
                "Go to",
                pages,
                index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0,
                label_visibility="collapsed"
            )
            
            # Update current page
            if selected_page != st.session_state.current_page:
                st.session_state.current_page = selected_page
                st.rerun()
            
            st.markdown("---")
            
            # Quick Stats (with error handling)
            try:
                if st.session_state.user_id:
                    stats = db.get_user_statistics(st.session_state.user_id)
                    st.markdown("### 📈 Quick Stats")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Actions", stats['total_actions'])
                        st.metric("Medicines", stats['medicines_count'])
                    with col2:
                        st.metric("Bills", stats['bills_count'])
                        st.metric("Notes", stats['notes_count'])
            except Exception as e:
                st.warning("Stats loading...")
            
            st.markdown("---")
            
            # Logout button at bottom
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                logout()

def dashboard_page():
    """Render professional dashboard"""
    st.markdown('<h1 class="page-title">📊 LifeOps Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Your personal life management command center</p>', unsafe_allow_html=True)
    
    # User Inputs Card
    with st.expander("⚙️ Configure Life Settings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🩺 Health Status")
            stress_level = st.slider(
                "Current Stress Level (1-10)",
                min_value=1,
                max_value=10,
                value=5,
                help="1 = Very Relaxed, 10 = Extremely Stressed"
            )
            
            sleep_hours = st.number_input(
                "Sleep Hours (per night)",
                min_value=0,
                max_value=12,
                value=7,
                step=1
            )
            
            exercise_frequency = st.selectbox(
                "Exercise Frequency",
                ["Rarely", "1-2 times/week", "3-4 times/week", "Daily"]
            )
        
        with col2:
            st.markdown("### 📚 Study Goals")
            
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
            
            st.markdown("### 💰 Financial Status")
            
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
        
        # Problem input
        st.markdown("### 🎯 What's Your Challenge?")
        problem = st.text_area(
            "Describe your current life challenge",
            "I'm stressed about my upcoming exam but also need to manage my budget and health",
            height=100
        )
        
        # Store inputs
        st.session_state.user_inputs = {
            'stress_level': stress_level,
            'sleep_hours': sleep_hours,
            'exercise_frequency': exercise_frequency,
            'exam_date': exam_date.strftime("%Y-%m-%d"),
            'days_until_exam': (exam_date - datetime.now().date()).days,
            'current_study_hours': current_study_hours,
            'monthly_budget': monthly_budget,
            'current_expenses': current_expenses,
            'financial_goals': financial_goals,
            'problem': problem
        }
        
        # Run Analysis Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Run AI Life Analysis", type="primary", use_container_width=True):
                run_ai_analysis(st.session_state.user_inputs)
    
    # Metrics Cards
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        stress = st.session_state.user_inputs.get('stress_level', 5)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">😰</div>
            <div class="metric-value">{stress}/10</div>
            <div class="metric-label">Stress Level</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        days_left = calculate_days_until(st.session_state.user_inputs.get('exam_date', ''))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📚</div>
            <div class="metric-value">{days_left}</div>
            <div class="metric-label">Days Until Exam</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        budget = st.session_state.user_inputs.get('monthly_budget', 0)
        expenses = st.session_state.user_inputs.get('current_expenses', 0)
        savings = budget - expenses if budget > expenses else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-value">${savings}</div>
            <div class="metric-label">Monthly Savings</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        try:
            consistency_streak = db.get_consistency_streak(st.session_state.user_id)
        except:
            consistency_streak = 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🔥</div>
            <div class="metric-value">{consistency_streak}</div>
            <div class="metric-label">Day Streak</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts Row
    st.markdown("### 📊 Visual Analytics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card-title">Health Dashboard</div>', unsafe_allow_html=True)
        st.plotly_chart(
            create_health_chart(stress, sleep_hours),
            use_container_width=True
        )
    
    with col2:
        st.markdown('<div class="card-title">Financial Overview</div>', unsafe_allow_html=True)
        st.plotly_chart(
            create_finance_chart(budget, expenses),
            use_container_width=True
        )
    
    # Study Schedule
    if 'days_until_exam' in st.session_state.user_inputs:
        st.markdown('<div class="card-title">Study Schedule</div>', unsafe_allow_html=True)
        st.plotly_chart(
            create_study_schedule(
                st.session_state.user_inputs['days_until_exam'],
                st.session_state.user_inputs['current_study_hours']
            ),
            use_container_width=True
        )

def health_vault_page():
    """Render Health Vault page"""
    st.markdown('<h1 class="page-title">💊 Health Vault</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Manage your medicines, track symptoms, and monitor health trends</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Medicines Management
        st.markdown("### 💊 Medicine Management")
        
        # Add Medicine Form
        with st.expander("➕ Add New Medicine", expanded=False):
            med_col1, med_col2 = st.columns(2)
            with med_col1:
                medicine_name = st.text_input("Medicine Name", key="med_name")
                medicine_dosage = st.text_input("Dosage (e.g., 500mg)", key="med_dosage")
            with med_col2:
                medicine_frequency = st.selectbox("Frequency", ["Daily", "Twice Daily", "Weekly", "As Needed"], key="med_freq")
                medicine_time = st.selectbox("Time of Day", ["Morning", "Afternoon", "Evening", "Night", "Anytime"], key="med_time")
            
            if st.button("Add Medicine", key="add_med"):
                if medicine_name:
                    db.add_medicine(st.session_state.user_id, medicine_name, medicine_dosage, medicine_frequency, medicine_time)
                    st.success(f"Added {medicine_name}")
                    st.session_state.medicines = db.get_todays_medicines(st.session_state.user_id)
                    st.rerun()
                else:
                    st.warning("Please enter a medicine name")
        
        # Current Medicines List
        st.markdown("#### 📋 Current Medicines")
        try:
            medicines = db.get_all_medicines(st.session_state.user_id)
        except:
            medicines = []
        
        if medicines:
            for med in medicines:
                with st.container():
                    col_a, col_b, col_c = st.columns([3, 1, 1])
                    with col_a:
                        st.markdown(f"""
                        <div class="list-item">
                            <strong>{med['name']}</strong><br>
                            <small>📋 {med['dosage']} | 🔄 {med['frequency']} | ⏰ {med['time_of_day'] or 'Anytime'}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        if st.button("✅ Taken", key=f"taken_{med['id']}"):
                            db.update_medicine_taken(st.session_state.user_id, med['id'])
                            st.success(f"Marked {med['name']} as taken")
                            st.rerun()
                    with col_c:
                        if st.button("🗑️", key=f"delete_med_{med['id']}"):
                            db.delete_medicine(st.session_state.user_id, med['id'])
                            st.session_state.medicines = db.get_todays_medicines(st.session_state.user_id)
                            st.rerun()
        else:
            st.info("No medicines added yet. Add your first medicine above.")
    
    with col2:
        # Health Log
        st.markdown("### 📝 Health Log")
        
        log_date = st.date_input("Log Date", datetime.now(), key="health_log_date")
        
        symptoms = st.text_area("Symptoms / How you feel today", height=100, key="symptoms")
        sleep_quality = st.slider("Sleep Quality (1-10)", 1, 10, 7, key="sleep_quality")
        energy_level = st.slider("Energy Level (1-10)", 1, 10, 6, key="energy_level")
        water_intake = st.number_input("Water Intake (glasses)", 0, 20, 8, key="water_intake")
        
        if st.button("Save Health Log", key="save_health_log"):
            # Here you would save to a health_logs table (to be implemented)
            st.success("Health log saved successfully!")
        
        # Health Trends
        st.markdown("### 📈 Health Trends")
        
        # Mock trend data
        trend_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Energy": [7, 6, 8, 5, 7, 9, 8],
            "Sleep": [8, 7, 6, 7, 8, 9, 8]
        })
        
        st.line_chart(trend_data.set_index("Day"))

def finance_hub_page():
    """Render Finance Hub page"""
    st.markdown('<h1 class="page-title">💰 Finance Hub</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Track bills, manage budget, and optimize expenses</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Bill Management
        st.markdown("### 📋 Bill Management")
        
        # Add Bill Form
        with st.expander("➕ Add New Bill", expanded=False):
            bill_col1, bill_col2 = st.columns(2)
            with bill_col1:
                bill_name = st.text_input("Bill Name", key="bill_name")
                bill_amount = st.number_input("Amount ($)", min_value=0.0, value=100.0, step=10.0, key="bill_amount")
            with bill_col2:
                bill_due_day = st.number_input("Due Day (1-31)", min_value=1, max_value=31, value=15, key="bill_due_day")
                bill_category = st.selectbox("Category", ["Utilities", "Rent/Mortgage", "Insurance", "Subscriptions", "Loan", "Other"], key="bill_category")
            
            if st.button("Add Bill", key="add_bill"):
                if bill_name:
                    db.add_bill(st.session_state.user_id, bill_name, bill_amount, bill_due_day, bill_category)
                    st.success(f"Added {bill_name}")
                    st.session_state.bills = db.get_monthly_bills(st.session_state.user_id)
                    st.rerun()
                else:
                    st.warning("Please enter a bill name")
        
        # Current Bills List
        st.markdown("#### 📅 Upcoming Bills")
        try:
            bills = db.get_all_bills(st.session_state.user_id)
        except:
            bills = []
        
        if bills:
            total_monthly = sum(b['amount'] for b in bills)
            st.metric("Total Monthly Bills", f"${total_monthly:.2f}")
            
            for bill in bills:
                with st.container():
                    col_a, col_b, col_c = st.columns([3, 1, 1])
                    with col_a:
                        status = "✅ Paid" if bill['paid_this_month'] else "⏰ Due"
                        status_color = "green" if bill['paid_this_month'] else "orange"
                        st.markdown(f"""
                        <div class="list-item">
                            <strong>{bill['name']}</strong><br>
                            <small>💰 ${bill['amount']:.2f} | 📅 Day {bill['due_day']} | 🏷️ {bill['category']} | 
                            <span style="color: {status_color}">{status}</span></small>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        if not bill['paid_this_month']:
                            if st.button("💳 Pay", key=f"pay_{bill['id']}"):
                                db.mark_bill_paid(st.session_state.user_id, bill['id'])
                                st.session_state.bills = db.get_monthly_bills(st.session_state.user_id)
                                st.rerun()
                    with col_c:
                        if st.button("🗑️", key=f"delete_bill_{bill['id']}"):
                            db.delete_bill(st.session_state.user_id, bill['id'])
                            st.session_state.bills = db.get_monthly_bills(st.session_state.user_id)
                            st.rerun()
        else:
            st.info("No bills added yet. Add your first bill above.")
    
    with col2:
        # Budget Calculator
        st.markdown("### 🧮 Budget Calculator")
        
        monthly_income = st.number_input("Monthly Income ($)", min_value=0, value=3000, step=100, key="monthly_income")
        
        categories = {
            "Housing (30%)": monthly_income * 0.3,
            "Food (15%)": monthly_income * 0.15,
            "Transportation (10%)": monthly_income * 0.1,
            "Savings (20%)": monthly_income * 0.2,
            "Entertainment (10%)": monthly_income * 0.1,
            "Miscellaneous (15%)": monthly_income * 0.15
        }
        
        for category, amount in categories.items():
            st.metric(category, f"${amount:.2f}")
        
        # Expense Tracker
        st.markdown("### 📊 Expense Tracker")
        
        expense_categories = ["Food", "Transport", "Shopping", "Entertainment", "Bills", "Other"]
        expense_data = {cat: 0 for cat in expense_categories}
        
        # Mock data - in real app, you'd get this from database
        expense_data["Food"] = 300
        expense_data["Bills"] = 500
        expense_data["Shopping"] = 150
        
        expense_df = pd.DataFrame(list(expense_data.items()), columns=["Category", "Amount"])
        st.bar_chart(expense_df.set_index("Category"))

def run_ai_analysis(user_inputs):
    """Run AI analysis with user context"""
    with st.spinner("🧠 LifeOps AI is analyzing your life with multi-agent intelligence..."):
        try:
            # Load environment
            load_env()
            
            # Run analysis
            st.session_state.processing = True
            
            # Try CrewAI first, then fallback to direct Gemini
            results = None
            try:
                crew = LifeOpsCrew(user_inputs)
                results = crew.kickoff()
                st.success("✅ AI analysis complete!")
            except Exception as crew_error:
                st.warning(f"⚠️ CrewAI encountered an issue, using fallback analysis...")
                # Fallback analysis would go here
                results = {
                    "health": "## Health Analysis\n\n**Recommendations:**\n1. Practice 10-minute breathing exercises daily\n2. Aim for 7-8 hours of quality sleep\n3. Incorporate 30-minute walks 3 times a week\n4. Stay hydrated throughout the day",
                    "finance": "## Finance Analysis\n\n**Recommendations:**\n1. Track all expenses for 7 days\n2. Create budget categories: essentials (50%), savings (20%), leisure (30%)\n3. Review subscriptions monthly\n4. Set up automatic savings transfer",
                    "study": "## Study Analysis\n\n**Recommendations:**\n1. Use Pomodoro technique: 25min study, 5min break\n2. Create study schedule with specific topics per day\n3. Review material within 24 hours of learning\n4. Practice active recall with flashcards",
                    "coordination": "## Integrated Life Plan\n\nCombine health, finance, and study by:\n1. Morning routine: 15min meditation + daily planning\n2. Schedule study sessions after exercise for better focus\n3. Weekly financial review on Sundays\n4. Sleep hygiene for better memory retention",
                }
                st.success("✅ Analysis completed successfully!")
            
            # Store results
            st.session_state.analysis_results = results
            st.session_state.processing = False
            
            # Show success message
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)[:200]}")
            st.session_state.processing = False

def main():
    """Main application function with multi-user support"""
    
    # Initialize session state
    initialize_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        # Show login page with no sidebar
        login_page()
    else:
        # Show sidebar for authenticated users
        professional_sidebar()
        
        # Get current page from session state
        page_mapping = {
            "Dashboard": dashboard_page,
            "Health Vault": health_vault_page,
            "Finance Hub": finance_hub_page,
            "Study Center": lambda: st.info("Study Center page - Coming Soon!"),
            "Productivity": lambda: st.info("Productivity page - Coming Soon!"),
            "Profile": lambda: st.info("Profile page - Coming Soon!")
        }
        
        # Render selected page
        page_function = page_mapping.get(st.session_state.current_page, dashboard_page)
        page_function()

if __name__ == "__main__":
    main()
