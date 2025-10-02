# BallWatch

**A full-stack basketball analytics platform with role-based access, real-time data pipelines, and advanced statistical analysis for coaches, GMs, and data engineers.**

## 🏀 Project Overview

BallWatch is a comprehensive database system built for high school basketball teams, featuring persona-driven interfaces and specialized analytics tools. The platform serves four distinct user roles with tailored dashboards and data access patterns.

## 🛠 Tech Stack

**Backend:** Flask REST API, MySQL, Docker  
**Frontend:** Streamlit, Plotly  
**Architecture:** Microservices with Docker Compose  
**Database:** Relational schema with 15+ tables

## 🚀 Quick Start

```bash
# Setup environment
cp api/.env.template api/.env
# Edit api/.env with your MYSQL_ROOT_PASSWORD

# Launch all services
docker compose up -d

# Access the application
# UI: http://localhost:8501
# API: http://localhost:4000
# DB: localhost:3200
```

## 🎯 Key Features

### Role-Based Dashboards

**Head Coach**
- Opponent scouting reports with tactical recommendations
- Lineup effectiveness analysis (plus/minus, offensive/defensive ratings)
- Player matchup advantages with H2H statistics
- Game plan creation and activation

**General Manager**
- Player evaluation and draft rankings
- Contract efficiency analysis
- Development tracking and potential assessment
- Value vs. estimated salary metrics

**Superfan**
- Advanced player search with 10+ filters
- Side-by-side player comparisons with radar charts
- Historical game analysis and box scores
- Statistical rankings and trend visualizations

**Data Engineer**
- Pipeline monitoring and retry mechanisms
- System health dashboards
- Error log management and resolution tracking
- Automated cleanup task scheduling

## 📊 Core API Endpoints

```python
# Basketball Operations
GET /basketball/teams
GET /basketball/players?position={}&team_id={}&age={}&salary={}
GET /basketball/players/{id}/stats
GET /basketball/games/{id}

# Analytics Engine
GET /analytics/lineup-configurations?team_id={}&min_games={}
GET /analytics/situational-performance?team_id={}&last_n_games={}
GET /analytics/player-matchups?player1_id={}&player2_id={}
GET /analytics/opponent-reports?team_id={}&opponent_id={}

# System Operations
GET /system/data-loads?days={}
POST /system/data-loads  # retry failed loads
GET /system/error-logs?days={}
PUT /system/data-errors/{id}  # mark resolved
```

## 🏗 Architecture

```
├── app/                    # Streamlit frontend
│   ├── src/
│   │   ├── pages/         # Role-specific dashboards
│   │   └── modules/       # API client & navigation
│   └── Dockerfile
│
├── api/                   # Flask REST backend
│   ├── backend/
│   │   ├── basketball/    # Core data routes
│   │   ├── analytics/     # Statistical analysis
│   │   ├── strategy/      # Game planning
│   │   └── admin/         # System operations
│   └── backend_app.py
│
└── database-files/        # MySQL schema & seeds
    ├── schema.sql
    └── inserts.sql
```

## 💡 Technical Highlights

- **Microservices Architecture:** Three containerized services orchestrated with Docker Compose
- **RESTful API Design:** Consistent JSON response shapes with proper error handling
- **Database Optimization:** Indexed queries for lineup combinations and player statistics
- **Caching Strategy:** Streamlit's `@st.cache_data` for reduced API calls
- **Role-Based Access Control:** Persona-driven UI with scoped data access
- **Data Pipeline Management:** Automated retry logic and error resolution workflows

## 🔧 Development

### Adding New Features
```python
# 1. Create new API endpoint in api/backend/
# 2. Add corresponding Streamlit page in app/src/pages/
# 3. Update schema in database-files/ if needed
# 4. Maintain consistent response shapes: {'data': [...]}
```

### Local Development (No Docker)
```bash
# Database
mysql -u root -p < database-files/schema.sql

# API
cd api/
pip install -r requirements.txt
python backend_app.py

# Frontend
cd app/src/
pip install -r requirements.txt
streamlit run Home.py
```

## 🐛 Troubleshooting

**"Unable to load teams data"**
- Check API container: `docker compose logs api`
- Test endpoint: `curl http://localhost:4000/basketball/teams`
- Verify `.env` configuration

**Empty datasets**
- Ensure database initialization: `docker compose up --build db`
- Check MySQL logs for startup errors

## 📈 Skills Demonstrated

- **Database Design:** Normalized schema with 15+ interconnected tables
- **API Development:** RESTful endpoints with proper error handling
- **Full-Stack Integration:** Microservices architecture with Docker
- **Data Engineering:** Pipeline monitoring and automated recovery
- **UI/UX Design:** Role-based interfaces with tailored analytics

---

*CS3200: Database Design - Northeastern University*

---
