# LifeOps AI v2.0 - Architecture Documentation

## System Overview
LifeOps AI is a multi-agent AI personal operations manager with cyberpunk-themed interface.

## Tech Stack
- **Frontend**: Streamlit
- **AI Orchestration**: CrewAI 
- **LLM**: Google
- **Database**: SQLite 
- **Visualization**: Plotly
- **Styling**: Custom CSS with Glassmorphism effects

## Database Schema


## Agent System
- Health & Wellness Command Officer
- Finance Operations Director
- Cognitive Performance Architect
- Life Operations Commander
- Weekly Reflection Agent

## Setup Instructions
1. Install requirements: `pip install -r requirements.txt`
2. Set GOOGLE_API_KEY in .env file
3. Run: `streamlit run app.py`

## Deployment
- Local: Streamlit local server
- Cloud: Streamlit Cloud, Hugging Face Spaces
- Docker: Containerized deployment available
