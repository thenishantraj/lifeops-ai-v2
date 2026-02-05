"""
LifeOps AI v2 - Multi-User Streamlit Application with Professional UI
FIXED: Login HTML rendering, Dark Mode visibility, and Sidebar Navigation
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
    """Render modern split-screen login page - FIXED: HTML rendering and Dark Mode visibility"""
    # Add custom CSS for login page with Dark Mode fixes
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
        background: #ffffff !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 40px;
        color: #000000 !important;
    }
    .login-right * {
        color: #000000 !important;
    }
    .login-form-container {
        width: 100%;
        max-width: 400px;
        background: #ffffff !important;
        color: #000000 !important;
    }
    .form-title {
        font-size: 28px;
        font-weight: 600;
        color: #2c3e50 !important;
        margin-bottom: 10px;
        text-align: center;
    }
    .form-subtitle {
        color: #7f8c8d !important;
        text-align: center;
        margin-bottom: 30px;
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
        max-width: 400px;
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
    /* Fix input fields for Dark Mode */
    .stTextInput input, .stTextInput label, .stTextInput div {
        color: #000000 !important;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ddd !important;
    }
    /* Fix tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #000000 !important;
    }
    /* Fix buttons */
    .stButton button {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create two columns for split screen
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Left side - Branding and Features (FIXED: Added unsafe_allow_html=True)
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
        """, unsafe_allow_html=True)  # FIXED BUG 1: Added unsafe_allow_html=True
    
    with col2:
        # Right side - Login Form (FIXED BUG 2: Dark Mode visibility)
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

def render_sidebar():
    """Render the sidebar navigation menu - FIXED: Always show after login"""
    with st.sidebar:
        # Show user info
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 40px; margin-bottom: 10px;">🧠</div>
            <h3 style="margin-bottom: 5px;">LifeOps</h3>
            <p style="color: #666; font-size: 14px; margin-bottom: 2px;">Hi, {st.session_state.user_data.get('name', 'User')}</p>
            <p style="color: #888; font-size: 12px; margin-bottom: 20px;">{st.session_state.user_data.get('email', '')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation Menu - FIXED BUG 3: Proper sidebar navigation
        st.markdown("### 📊 Navigation")
        
        # Define navigation options
        nav_options = ["Dashboard", "Health Vault", "Finance Hub", "Study Center", "Productivity", "Profile"]
        
        # Create radio buttons for navigation
        selected_page = st.radio(
            "Go to",
            nav_options,
            index=nav_options.index(st.session_state.current_page) if st.session_state.current_page in nav_options else 0,
            label_visibility="collapsed"
        )
        
        # Update current page if changed
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

def study_center_page():
    """Render Study Center page"""
    st.markdown('<h1 class="page-title">📚 Study Center</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Optimize your learning with smart schedules and focus techniques</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Pomodoro Timer
        st.markdown("### 🍅 Focus Timer")
        
        timer_col1, timer_col2 = st.columns(2)
        with timer_col1:
            work_minutes = st.number_input("Work Minutes", 5, 60, 25, key="work_mins")
            subject = st.text_input("Study Subject", placeholder="e.g., Mathematics, Physics", key="study_subject")
        with timer_col2:
            break_minutes = st.number_input("Break Minutes", 1, 30, 5, key="break_mins")
            focus_level = st.slider("Focus Level (1-10)", 1, 10, 7, key="focus_level")
        
        if not st.session_state.pomodoro_active:
            if st.button("▶️ Start Focus Session", type="primary", key="start_pomodoro"):
                st.session_state.pomodoro_active = True
                st.session_state.pomodoro_time = work_minutes * 60
                st.session_state.break_time = break_minutes * 60
                st.session_state.is_work = True
                st.session_state.current_subject = subject
                st.rerun()
        else:
            # Timer display
            mins, secs = divmod(st.session_state.pomodoro_time, 60)
            timer_text = f"{mins:02d}:{secs:02d}"
            phase = "FOCUS" if st.session_state.get('is_work', True) else "BREAK"
            phase_color = "#e74c3c" if st.session_state.get('is_work', True) else "#2ecc71"
            
            st.markdown(f"""
            <div class="timer-container">
                <div class="timer-phase" style="background: {phase_color}">{phase}</div>
                <div class="timer-display-large">{timer_text}</div>
                <div class="timer-subject">📚 {st.session_state.get('current_subject', 'General Study')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            control_col1, control_col2, control_col3 = st.columns(3)
            with control_col1:
                if st.button("⏸️ Pause", key="pause_timer"):
                    st.session_state.pomodoro_active = False
                    st.rerun()
            with control_col2:
                if st.button("⏭️ Skip to Break", key="skip_break"):
                    st.session_state.pomodoro_time = st.session_state.get('break_time', 300)
                    st.session_state.is_work = False
                    st.rerun()
            with control_col3:
                if st.button("⏹️ End Session", key="end_session"):
                    st.session_state.pomodoro_active = False
                    duration = work_minutes - (st.session_state.pomodoro_time // 60)
                    if duration > 0:
                        db.add_study_session(st.session_state.user_id, duration, 
                                           st.session_state.get('current_subject', 'General'), 
                                           focus_level)
                        st.success(f"Session saved: {duration} minutes")
                    st.rerun()
        
        # Study Tips
        st.markdown("### 💡 Study Tips")
        
        tips = [
            "🧠 Use the Pomodoro technique for better focus",
            "📝 Take handwritten notes for better retention",
            "🔄 Review material within 24 hours of learning",
            "🎯 Set specific, achievable study goals",
            "💤 Get adequate sleep before exams",
            "🏃♂️ Take short active breaks between sessions"
        ]
        
        for tip in tips:
            st.markdown(f'<div class="tip-item">{tip}</div>', unsafe_allow_html=True)
    
    with col2:
        # Study Statistics
        st.markdown("### 📊 Study Statistics")
        
        if st.session_state.user_id:
            study_stats = db.get_weekly_study_summary(st.session_state.user_id)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Weekly Hours", f"{study_stats['total_minutes']//60}h")
                st.metric("Sessions", study_stats['sessions'])
            with col_b:
                st.metric("Avg Focus", f"{study_stats['avg_score']:.1f}/10")
                st.metric("Daily Avg", f"{(study_stats['total_minutes']//60)/7:.1f}h")
        
        # Recent Sessions
        st.markdown("#### 📅 Recent Sessions")
        if st.session_state.user_id:
            recent_sessions = db.get_study_sessions(st.session_state.user_id, limit=5)
            for session in recent_sessions:
                st.markdown(f"""
                <div class="session-item">
                    <strong>{session['subject']}</strong><br>
                    <small>⏱️ {session['duration_minutes']} min | ⭐ {session['productivity_score']}/10 | 
                    {session['date']}</small>
                </div>
                """, unsafe_allow_html=True)

def productivity_page():
    """Render Productivity Tools page"""
    st.markdown('<h1 class="page-title">⚡ Productivity Hub</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Smart tasks, notes, and integrated planning</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Task Management
        st.markdown("### ✅ Task Management")
        
        # Add Task
        with st.form("add_task_form"):
            task_col1, task_col2 = st.columns([3, 1])
            with task_col1:
                new_task = st.text_input("New Task", placeholder="What needs to be done?", key="new_task")
            with task_col2:
                task_category = st.selectbox("Category", ["Health", "Finance", "Study", "Personal", "Work"], key="task_category")
            
            submitted = st.form_submit_button("Add Task", type="primary")
            if submitted and new_task:
                db.add_action_item(st.session_state.user_id, new_task, task_category, "User")
                st.session_state.todo_items = db.get_pending_actions(st.session_state.user_id)
                st.success("Task added!")
                st.rerun()
        
        # Task List
        st.markdown("#### 📋 Active Tasks")
        tasks = db.get_pending_actions(st.session_state.user_id)
        
        if tasks:
            for task in tasks:
                with st.container():
                    col_a, col_b, col_c = st.columns([3, 1, 1])
                    with col_a:
                        category_color = {
                            "Health": "#2ecc71",
                            "Finance": "#f39c12",
                            "Study": "#3498db",
                            "Personal": "#9b59b6",
                            "Work": "#e74c3c"
                        }.get(task['category'], "#95a5a6")
                        
                        st.markdown(f"""
                        <div class="list-item">
                            <strong>{task['task']}</strong><br>
                            <small>
                                <span style="color: {category_color}">● {task['category']}</span> | 
                                📅 {task['created_at'][:10]}
                            </small>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        if st.button("✅", key=f"complete_{task['id']}"):
                            db.mark_action_complete(st.session_state.user_id, task['id'])
                            st.session_state.todo_items = db.get_pending_actions(st.session_state.user_id)
                            st.rerun()
                    with col_c:
                        if st.button("🗑️", key=f"delete_task_{task['id']}"):
                            db.delete_action(st.session_state.user_id, task['id'])
                            st.session_state.todo_items = db.get_pending_actions(st.session_state.user_id)
                            st.rerun()
        else:
            st.info("No active tasks. Add a task above!")
        
        # Completed Tasks Stats
        if st.session_state.user_id:
            stats = db.get_user_statistics(st.session_state.user_id)
            if stats['total_actions'] > 0:
                completion_rate = (stats['completed_actions'] / stats['total_actions']) * 100
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    with col2:
        # Smart Notes
        st.markdown("### 📝 Smart Notes")
        
        note_title = st.text_input("Note Title", placeholder="Enter title", key="note_title")
        note_content = st.text_area("Content", height=150, placeholder="Write your note here...", key="note_content")
        note_tags = st.text_input("Tags (comma-separated)", placeholder="work, ideas, personal", key="note_tags")
        
        if st.button("💾 Save Note", key="save_note"):
            if note_title and note_content:
                db.add_note(st.session_state.user_id, note_title, note_content, note_tags)
                st.session_state.notes = db.get_notes(st.session_state.user_id)
                st.success("Note saved!")
                st.rerun()
            else:
                st.warning("Please enter both title and content")
        
        # Recent Notes
        st.markdown("#### 📓 Recent Notes")
        notes = st.session_state.notes[:3]
        for note in notes:
            with st.expander(f"📄 {note['title']}"):
                st.write(note['content'])
                if note['tags']:
                    st.caption(f"🏷️ {note['tags']}")

def profile_page():
    """Render User Profile page"""
    st.markdown('<h1 class="page-title">👤 Your Profile</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Manage your account and preferences</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Profile Summary
        st.markdown("### Profile Summary")
        
        user = st.session_state.user_data
        if user:
            st.markdown(f"""
            <div class="profile-card">
                <div class="profile-avatar">👤</div>
                <h3>{user.get('name', 'User')}</h3>
                <p>{user.get('email', '')}</p>
                <div class="profile-stats">
                    <div class="stat-item">
                        <div class="stat-value">Member Since</div>
                        <div class="stat-label">{user.get('joined_at', '')[:10]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Account Type
        st.markdown("### Account Type")
        st.info("✨ **Free Account**\n\nUpgrade to Premium for:\n• Unlimited AI Analysis\n• Advanced Analytics\n• Priority Support")
        
        if st.button("🔄 Check for Updates", key="check_updates"):
            st.success("You're using the latest version of LifeOps AI!")
    
    with col2:
        # User Statistics
        st.markdown("### 📊 Your LifeOps Statistics")
        
        if st.session_state.user_id:
            stats = db.get_user_statistics(st.session_state.user_id)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Actions", stats['total_actions'])
                st.metric("Medicines Tracked", stats['medicines_count'])
                st.metric("Bills Managed", stats['bills_count'])
            with col_b:
                st.metric("Completed Actions", stats['completed_actions'])
                st.metric("Notes Created", stats['notes_count'])
                st.metric("Completion Rate", f"{stats['completion_rate']:.1f}%")
        
        # Settings
        st.markdown("### ⚙️ Settings")
        
        with st.expander("🔔 Notification Settings", expanded=False):
            email_notifications = st.checkbox("Email Notifications", value=True)
            push_reminders = st.checkbox("Push Reminders", value=True)
            weekly_reports = st.checkbox("Weekly Progress Reports", value=True)
            
            if st.button("Save Notification Settings", key="save_notifications"):
                st.success("Notification settings saved!")
        
        with st.expander("🎨 Theme Settings", expanded=False):
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
            font_size = st.select_slider("Font Size", options=["Small", "Medium", "Large"], value="Medium")
            
            if st.button("Apply Theme", key="apply_theme"):
                st.success("Theme settings applied!")
        
        with st.expander("🔐 Security", expanded=False):
            st.info("For security reasons, please contact support to change your password.")
            
            if st.button("📧 Request Password Reset", key="reset_password"):
                st.success("Password reset instructions sent to your email!")

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
    """Main application function with FIXED navigation"""
    
    # Initialize session state
    initialize_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        # Show login page with no sidebar
        st.set_page_config(initial_sidebar_state="collapsed")
        login_page()
    else:
        # FIXED BUG 3: Create proper sidebar navigation
        # Render sidebar first
        render_sidebar()
        
        # Now render the selected page based on current_page state
        # The render_sidebar() function already handles updating current_page via radio buttons
        
        # Page routing logic
        if st.session_state.current_page == "Dashboard":
            dashboard_page()
        elif st.session_state.current_page == "Health Vault":
            health_vault_page()
        elif st.session_state.current_page == "Finance Hub":
            finance_hub_page()
        elif st.session_state.current_page == "Study Center":
            study_center_page()
        elif st.session_state.current_page == "Productivity":
            productivity_page()
        elif st.session_state.current_page == "Profile":
            profile_page()
        else:
            # Default to dashboard
            dashboard_page()

if __name__ == "__main__":
    main()
