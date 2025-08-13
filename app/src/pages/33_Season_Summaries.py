##################################################
# BallWatch Basketball Analytics - Season Performance Summaries
# Comprehensive season tracking and goal progress monitoring
# 
# User Story: Marcus-3.6 - Season performance summaries and goal tracking
# 
# Features:
# - Season overview with key metrics
# - Monthly performance trends
# - Goal progress tracking
# - League comparison and rankings
# - Playoff projection analysis
##################################################

import logging
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from modules.nav import SideBarLinks, check_authentication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="BallWatch - Season Summary", 
    layout="wide"
)

# Check authentication and role
check_authentication('head_coach')
SideBarLinks()

# Constants
BASE_URL = "http://api:4000"
CURRENT_SEASON = "2024-25"
DEFAULT_TEAM_ID = st.session_state.get('team_id', 1)
COACH_NAME = st.session_state.get('first_name', 'Coach')

# Styling
st.markdown("""
<style>
.season-overview-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin: 1rem 0;
}
.goal-card {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 5px solid #007bff;
    margin: 1rem 0;
}
.achievement-card {
    background-color: #d4edda;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #28a745;
}
.warning-card {
    background-color: #fff3cd;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #ffc107;
}
.danger-card {
    background-color: #f8d7da;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #dc3545;
}
.standings-row {
    padding: 0.5rem;
    margin: 0.2rem 0;
    border-radius: 5px;
}
.standings-highlight {
    background-color: #e3f2fd;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


class SeasonAnalysisAPI:
    """API client for season analysis with comprehensive error handling."""
    
    @staticmethod
    def make_request(endpoint, params=None, timeout=15):
        """Make API request with error handling."""
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, params=params, timeout=timeout)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API request failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            return None
    
    @staticmethod
    def safe_get(data, *keys, default=None):
        """Safely extract nested values."""
        try:
            for key in keys:
                data = data[key]
            return data
        except (KeyError, TypeError, AttributeError):
            return default


# Initialize API client
api = SeasonAnalysisAPI()


@st.cache_data(ttl=600, show_spinner=False)
def load_season_summary(team_id, season=CURRENT_SEASON):
    """Load comprehensive season summary data."""
    params = {
        "entity_type": "team",
        "entity_id": team_id,
        "season": season,
        "include_trends": "true",
        "include_goals": "true"
    }
    return api.make_request("/api/analytics/season-summaries", params=params)


@st.cache_data(ttl=300, show_spinner=False)
def load_team_info(team_id):
    """Load basic team information."""
    return api.make_request(f"/api/teams/{team_id}")


def generate_sample_season_data():
    """Generate realistic sample season data for demonstration."""
    return {
        'summary': {
            'team_name': 'Brooklyn Nets',
            'conference': 'Eastern',
            'division': 'Atlantic',
            'coach': 'Marcus Thompson',
            'games_played': 41,
            'wins': 24,
            'losses': 17,
            'avg_points_scored': 114.2,
            'avg_points_allowed': 110.8,
            'home_games': 21,
            'away_games': 20,
            'win_percentage': 58.5,
            'net_rating': 3.4,
            'games_remaining': 41
        }
    }


def generate_monthly_performance_data():
    """Generate month-by-month performance data."""
    months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar']
    data = []
    
    for i, month in enumerate(months):
        if i < 4:  # Only show completed months
            wins = [3, 8, 6, 7][i]
            games = [5, 12, 9, 10][i]
            losses = games - wins
            ppg = 110 + (i * 2) + np.random.normal(0, 2)
            opp_ppg = 108 + (i * 1.5) + np.random.normal(0, 2)
            
            data.append({
                'month': month,
                'games': games,
                'wins': wins,
                'losses': losses,
                'win_pct': wins / games,
                'ppg': round(ppg, 1),
                'opp_ppg': round(opp_ppg, 1),
                'net_rating': round(ppg - opp_ppg, 1)
            })
    
    return pd.DataFrame(data)


def render_page_header():
    """Render the page header with season selector."""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("📈 Season Performance Summary")
        st.markdown("*Track progress and analyze season trends*")
    
    with col2:
        selected_season = st.selectbox(
            "Season:",
            options=["2024-25", "2023-24", "2022-23"],
            index=0,
            help="Choose which season to analyze"
        )
        
    with col3:
        if st.button("🔄 Refresh Summary", help="Refresh season data"):
            st.cache_data.clear()
            st.rerun()
    
    return selected_season


def render_season_overview(season_data, season):
    """Render comprehensive season overview."""
    st.subheader("🏀 Season Overview")
    
    if not season_data:
        season_data = generate_sample_season_data()
    
    summary = api.safe_get(season_data, 'summary', {})
    
    # Main overview card
    team_name = summary.get('team_name', 'Brooklyn Nets')
    wins = summary.get('wins', 24)
    losses = summary.get('losses', 17)
    games_played = summary.get('games_played', 41)
    win_pct = (wins / games_played * 100) if games_played > 0 else 0
    
    st.markdown(f"""
    <div class="season-overview-card">
        <h2>🏀 {team_name} - {season} Season</h2>
        <h1>{wins}-{losses}</h1>
        <h3>{win_pct:.1f}% Win Percentage</h3>
        <p>{summary.get('games_remaining', 41)} games remaining in regular season</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics = [
        ("Points/Game", summary.get('avg_points_scored', 114.2), "⚡"),
        ("Opp Points/Game", summary.get('avg_points_allowed', 110.8), "🛡️"),
        ("Net Rating", summary.get('net_rating', 3.4), "📊"),
        ("Home Record", f"{summary.get('home_wins', 13)}-{summary.get('home_losses', 8)}", "🏠"),
        ("Road Record", f"{summary.get('away_wins', 11)}-{summary.get('away_losses', 9)}", "✈️")
    ]
    
    columns = [col1, col2, col3, col4, col5]
    
    for i, (label, value, emoji) in enumerate(metrics):
        with columns[i]:
            if isinstance(value, (int, float)) and label != "Net Rating":
                st.metric(f"{emoji} {label}", f"{value:.1f}")
            else:
                st.metric(f"{emoji} {label}", str(value))


def render_monthly_trends():
    """Render month-by-month performance trends."""
    st.subheader("📅 Monthly Performance Trends")
    
    # Generate or load monthly data
    monthly_df = generate_monthly_performance_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly record chart
        fig_record = go.Figure()
        
        fig_record.add_trace(go.Bar(
            name='Wins',
            x=monthly_df['month'],
            y=monthly_df['wins'],
            marker_color='#28a745',
            text=monthly_df['wins'],
            textposition='auto'
        ))
        
        fig_record.add_trace(go.Bar(
            name='Losses',
            x=monthly_df['month'],
            y=monthly_df['losses'],
            marker_color='#dc3545',
            text=monthly_df['losses'],
            textposition='auto'
        ))
        
        fig_record.update_layout(
            title='Monthly Wins & Losses',
            xaxis_title='Month',
            yaxis_title='Games',
            barmode='stack',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_record, use_container_width=True)
    
    with col2:
        # Net rating trend
        fig_rating = px.line(
            monthly_df,
            x='month',
            y='net_rating',
            title='Monthly Net Rating Trend',
            labels={'net_rating': 'Net Rating', 'month': 'Month'},
            line_shape='spline',
            markers=True
        )
        
        fig_rating.update_traces(
            line=dict(width=4, color='#007bff'),
            marker=dict(size=10)
        )
        
        # Add horizontal line at 0
        fig_rating.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7)
        
        fig_rating.update_layout(height=400)
        
        st.plotly_chart(fig_rating, use_container_width=True)


def render_goals_progress():
    """Render progress toward season goals."""
    st.subheader("🎯 Season Goals Progress")
    
    # Mock goals data with realistic targets
    goals = {
        'playoff_berth': {
            'target': 'Make Playoffs',
            'current_status': 'On Track',
            'probability': 0.72,
            'description': 'Currently 6th seed with 41 games remaining'
        },
        'wins_target': {
            'target': 45,
            'current': 24,
            'games_played': 41,
            'pace': round((24/41) * 82, 1),
            'description': 'On pace for 48 wins this season'
        },
        'development_goals': [
            {
                'goal': 'Improve Defensive Rating',
                'target': 108.0,
                'current': 110.8,
                'status': 'needs_work'
            },
            {
                'goal': 'Increase Three-Point %',
                'target': 38.0,
                'current': 36.5,
                'status': 'improving'
            },
            {
                'goal': 'Reduce Turnovers',
                'target': 12.0,
                'current': 13.4,
                'status': 'needs_work'
            },
            {
                'goal': 'Improve Bench Scoring',
                'target': 35.0,
                'current': 32.1,
                'status': 'on_track'
            }
        ]
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏆 Primary Goals")
        
        # Playoff probability
        playoff_data = goals['playoff_berth']
        prob = playoff_data['probability']
        
        if prob > 0.7:
            prob_color = "achievement-card"
            prob_icon = "🟢"
        elif prob > 0.4:
            prob_color = "warning-card"
            prob_icon = "🟡"
        else:
            prob_color = "danger-card"
            prob_icon = "🔴"
        
        st.markdown(f"""
        <div class="{prob_color}">
            <h5>{prob_icon} Playoff Chances</h5>
            <h3>{prob:.1%}</h3>
            <p>{playoff_data['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Wins target
        wins_data = goals['wins_target']
        wins_pace = wins_data['pace']
        wins_target = wins_data['target']
        
        if wins_pace >= wins_target:
            wins_color = "achievement-card"
            wins_icon = "🎯"
        elif wins_pace >= wins_target - 3:
            wins_color = "warning-card"
            wins_icon = "📊"
        else:
            wins_color = "danger-card"
            wins_icon = "📉"
        
        st.markdown(f"""
        <div class="{wins_color}">
            <h5>{wins_icon} Win Target Progress</h5>
            <h3>{wins_data['current']}/{wins_target} wins</h3>
            <p>Pace: {wins_pace} wins</p>
            <p>{wins_data['description']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📈 Development Areas")
        
        for goal in goals['development_goals']:
            status = goal['status']
            
            if status == 'on_track':
                card_class = "achievement-card"
                icon = "✅"
            elif status == 'improving':
                card_class = "warning-card"
                icon = "📈"
            else:
                card_class = "danger-card"
                icon = "❌"
            
            if goal['goal'] == 'Increase Three-Point %':
                target_display = f"{goal['target']:.1f}%"
                current_display = f"{goal['current']:.1f}%"
            else:
                target_display = f"{goal['target']:.1f}"
                current_display = f"{goal['current']:.1f}"
            
            st.markdown(f"""
            <div class="{card_class}">
                <p><strong>{icon} {goal['goal']}</strong></p>
                <p>Target: {target_display} | Current: {current_display}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("#### ⭐ Key Milestones")
        
        milestones = [
            {"milestone": "Reach .500 record", "status": "achieved", "progress": 1.0},
            {"milestone": "Win 30 games", "status": "pending", "progress": 24/30},
            {"milestone": "Top 6 seed", "status": "on_track", "progress": 0.8},
            {"milestone": "Home court advantage", "status": "pending", "progress": 0.6}
        ]
        
        for milestone in milestones:
            status = milestone['status']
            progress = milestone['progress']
            
            if status == 'achieved':
                icon = "✅"
                color = "#28a745"
            elif status == 'on_track':
                icon = "🟢"
                color = "#ffc107"
            else:
                icon = "⏳"
                color = "#6c757d"
            
            st.markdown(f"**{icon} {milestone['milestone']}**")
            
            if progress < 1.0:
                st.progress(progress)
                st.caption(f"{progress:.1%} complete")
            else:
                st.caption("✅ Completed!")


def render_detailed_statistics(season_data):
    """Render detailed season statistics breakdown."""
    st.subheader("📊 Detailed Season Statistics")
    
    summary = api.safe_get(season_data, 'summary', {}) if season_data else generate_sample_season_data()['summary']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### ⚡ Offensive Statistics")
        
        # Calculate or use default offensive stats
        ppg = summary.get('avg_points_scored', 114.2)
        fg_pct = 47.1  # Default FG%
        three_pct = 36.5  # Default 3P%
        ft_pct = 79.8  # Default FT%
        apg = 26.8  # Default assists
        
        offensive_stats = [
            ("Points Per Game", f"{ppg:.1f}", "Primary scoring output"),
            ("Field Goal %", f"{fg_pct:.1f}%", "Overall shooting efficiency"),
            ("Three-Point %", f"{three_pct:.1f}%", "Perimeter shooting"),
            ("Free Throw %", f"{ft_pct:.1f}%", "Charity stripe efficiency"),
            ("Assists Per Game", f"{apg:.1f}", "Ball movement and sharing")
        ]
        
        for stat, value, description in offensive_stats:
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.write(f"**{stat}:**")
                st.caption(description)
            with col_b:
                st.write(f"**{value}**")
    
    with col2:
        st.markdown("#### 🛡️ Defensive Statistics")
        
        opp_ppg = summary.get('avg_points_allowed', 110.8)
        opp_fg_pct = 45.2  # Default opponent FG%
        steals = 7.9  # Default steals
        blocks = 5.2  # Default blocks
        def_reb = 34.1  # Default defensive rebounds
        
        defensive_stats = [
            ("Opponent Points/Game", f"{opp_ppg:.1f}", "Points allowed"),
            ("Opponent FG %", f"{opp_fg_pct:.1f}%", "Opponent shooting %"),
            ("Steals Per Game", f"{steals:.1f}", "Defensive pressure"),
            ("Blocks Per Game", f"{blocks:.1f}", "Rim protection"),
            ("Defensive Rebounds", f"{def_reb:.1f}", "Securing possessions")
        ]
        
        for stat, value, description in defensive_stats:
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.write(f"**{stat}:**")
                st.caption(description)
            with col_b:
                st.write(f"**{value}**")
    
    with col3:
        st.markdown("#### 📊 Advanced Metrics")
        
        net_rating = summary.get('net_rating', 3.4)
        pace = 98.5  # Default pace
        eff_fg_pct = 51.2  # Default effective FG%
        ts_pct = 57.8  # Default true shooting %
        turnover_pct = 13.4  # Default turnover rate
        
        advanced_stats = [
            ("Net Rating", f"{net_rating:+.1f}", "Point differential per 100 poss"),
            ("Pace", f"{pace:.1f}", "Possessions per 48 minutes"),
            ("Effective FG%", f"{eff_fg_pct:.1f}%", "Shooting efficiency w/ 3P weight"),
            ("True Shooting %", f"{ts_pct:.1f}%", "Overall shooting efficiency"),
            ("Turnover Rate", f"{turnover_pct:.1f}%", "Turnovers per possession")
        ]
        
        for stat, value, description in advanced_stats:
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.write(f"**{stat}:**")
                st.caption(description)
            with col_b:
                st.write(f"**{value}**")


def render_conference_standings():
    """Render Eastern Conference standings context."""
    st.subheader("🏆 Eastern Conference Standings")
    
    # Mock current standings
    standings = [
        {"rank": 1, "team": "Boston Celtics", "record": "32-9", "gb": "-", "streak": "W3"},
        {"rank": 2, "team": "Miami Heat", "record": "28-13", "gb": "4.0", "streak": "L1"},
        {"rank": 3, "team": "Philadelphia 76ers", "record": "26-15", "gb": "6.0", "streak": "W2"},
        {"rank": 4, "team": "New York Knicks", "record": "25-16", "gb": "7.0", "streak": "W1"},
        {"rank": 5, "team": "Orlando Magic", "record": "25-16", "gb": "7.0", "streak": "L2"},
        {"rank": 6, "team": "Brooklyn Nets", "record": "24-17", "gb": "8.0", "streak": "W1"},
        {"rank": 7, "team": "Atlanta Hawks", "record": "22-19", "gb": "10.0", "streak": "L1"},
        {"rank": 8, "team": "Chicago Bulls", "record": "21-20", "gb": "11.0", "streak": "W2"},
        {"rank": 9, "team": "Toronto Raptors", "record": "20-21", "gb": "12.0", "streak": "L3"},
        {"rank": 10, "team": "Indiana Pacers", "record": "19-22", "gb": "13.0", "streak": "W1"}
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Current Standings")
        
        # Create standings table
        standings_html = """
        <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background-color: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                <th style="padding: 8px; text-align: left;">Rank</th>
                <th style="padding: 8px; text-align: left;">Team</th>
                <th style="padding: 8px; text-align: center;">Record</th>
                <th style="padding: 8px; text-align: center;">GB</th>
                <th style="padding: 8px; text-align: center;">Streak</th>
            </tr>
        </thead>
        <tbody>
        """
        
        for team in standings[:10]:
            row_class = "standings-highlight" if "Brooklyn Nets" in team['team'] else ""
            standings_html += f"""
            <tr class="standings-row {row_class}">
                <td style="padding: 6px; font-weight: bold;">{team['rank']}</td>
                <td style="padding: 6px;">{team['team']}</td>
                <td style="padding: 6px; text-align: center;">{team['record']}</td>
                <td style="padding: 6px; text-align: center;">{team['gb']}</td>
                <td style="padding: 6px; text-align: center;">{team['streak']}</td>
            </tr>
            """
        
        standings_html += "</tbody></table>"
        st.markdown(standings_html, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🎯 Playoff Picture")
        
        # Playoff positioning info
        current_seed = 6
        games_back = 8.0
        
        st.markdown(f"""
        <div class="goal-card">
            <h5>Current Position</h5>
            <h3>#{current_seed} Seed</h3>
            <p>{games_back} games back of 1st</p>
            <hr>
            <p><strong>Playoff Status:</strong> In Position</p>
            <p><strong>Play-in Status:</strong> Avoided</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Critical upcoming games
        st.markdown("#### 🔥 Critical Games")
        critical_games = [
            "vs Boston (1st seed)",
            "@ Miami (2nd seed)", 
            "vs Philadelphia (3rd seed)"
        ]
        
        for game in critical_games:
            st.markdown(f"🔴 **{game}**")


def render_upcoming_challenges():
    """Render analysis of upcoming schedule challenges."""
    st.subheader("🗓️ Upcoming Schedule Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📅 Next 10 Games Difficulty")
        
        # Mock upcoming schedule with difficulty ratings
        upcoming_schedule = [
            {"date": "Jan 15", "opponent": "Boston Celtics", "location": "vs", "difficulty": "Hard"},
            {"date": "Jan 17", "opponent": "Miami Heat", "location": "@", "difficulty": "Hard"},
            {"date": "Jan 19", "opponent": "Philadelphia 76ers", "location": "vs", "difficulty": "Medium"},
            {"date": "Jan 21", "opponent": "Charlotte Hornets", "location": "@", "difficulty": "Easy"},
            {"date": "Jan 23", "opponent": "Detroit Pistons", "location": "vs", "difficulty": "Easy"},
            {"date": "Jan 25", "opponent": "Orlando Magic", "location": "@", "difficulty": "Medium"},
            {"date": "Jan 27", "opponent": "Atlanta Hawks", "location": "vs", "difficulty": "Medium"},
            {"date": "Jan 29", "opponent": "Toronto Raptors", "location": "@", "difficulty": "Easy"},
            {"date": "Jan 31", "opponent": "Chicago Bulls", "location": "vs", "difficulty": "Medium"},
            {"date": "Feb 2", "opponent": "Indiana Pacers", "location": "@", "difficulty": "Easy"}
        ]
        
        hard_games = medium_games = easy_games = 0
        
        for game in upcoming_schedule:
            difficulty = game['difficulty']
            location_icon = "🏠" if game['location'] == "vs" else "✈️"
            
            if difficulty == "Hard":
                color = "🔴"
                hard_games += 1
            elif difficulty == "Medium":
                color = "🟡"
                medium_games += 1
            else:
                color = "🟢"
                easy_games += 1
            
            st.markdown(f"{color} {location_icon} **{game['date']}** - {game['opponent']}")
        
        # Schedule difficulty summary
        st.markdown("---")
        st.markdown(f"""
        **Schedule Difficulty Breakdown:**
        - 🔴 Hard: {hard_games} games
        - 🟡 Medium: {medium_games} games  
        - 🟢 Easy: {easy_games} games
        """)
    
    with col2:
        st.markdown("#### 🎯 Keys to Success")
        
        success_factors = [
            {
                "factor": "Stay healthy through tough stretch",
                "importance": "Critical",
                "note": "Avoid injuries in physical games"
            },
            {
                "factor": "Improve road performance",
                "importance": "High", 
                "note": "Currently 11-9 on the road"
            },
            {
                "factor": "Win games vs bottom teams",
                "importance": "High",
                "note": "Must beat Hornets, Pistons, Raptors"
            },
            {
                "factor": "Split vs top East teams",
                "importance": "Medium",
                "note": "Go 2-2 vs Celtics, Heat, 76ers"
            },
            {
                "factor": "Strengthen bench production",
                "importance": "Medium",
                "note": "Bench needs to step up in big games"
            }
        ]
        
        for i, factor in enumerate(success_factors, 1):
            importance = factor['importance']
            
            if importance == "Critical":
                icon = "🔴"
            elif importance == "High":
                icon = "🟡"
            else:
                icon = "🔵"
            
            st.markdown(f"**{i}. {icon} {factor['factor']}**")
            st.caption(factor['note'])
            st.write("")


def render_season_projections():
    """Render season projections and scenarios."""
    st.subheader("🔮 Season Projections")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Win Projections")
        
        # Current pace calculation
        current_wins = 24
        games_played = 41
        current_pace = (current_wins / games_played) * 82
        
        # Scenario projections
        scenarios = [
            {"name": "Current Pace", "wins": round(current_pace), "probability": "50%", "description": "Maintain current performance"},
            {"name": "Optimistic", "wins": 50, "probability": "25%", "description": "Key players stay healthy, chemistry improves"},
            {"name": "Pessimistic", "wins": 42, "probability": "25%", "description": "Injuries or chemistry issues"}
        ]
        
        for scenario in scenarios:
            wins = scenario['wins']
            prob = scenario['probability']
            
            if wins >= 47:
                color = "achievement-card"
            elif wins >= 44:
                color = "warning-card"
            else:
                color = "danger-card"
            
            st.markdown(f"""
            <div class="{color}">
                <h6>{scenario['name']} Scenario</h6>
                <h4>{wins} wins ({prob})</h4>
                <p>{scenario['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🏆 Playoff Scenarios")
        
        # Playoff probability breakdown
        playoff_scenarios = [
            {"seed": "1-2 seed", "probability": 5, "description": "Need significant improvement"},
            {"seed": "3-4 seed", "probability": 15, "description": "Requires strong finish"},
            {"seed": "5-6 seed", "probability": 45, "description": "Most likely scenario"},
            {"seed": "7-8 seed", "probability": 25, "description": "Play-in tournament"},
            {"seed": "Miss playoffs", "probability": 10, "description": "Significant decline needed"}
        ]
        
        # Create probability chart
        seed_names = [s['seed'] for s in playoff_scenarios]
        probabilities = [s['probability'] for s in playoff_scenarios]
        
        fig_playoff = px.pie(
            values=probabilities,
            names=seed_names,
            title='Playoff Seeding Probabilities',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_playoff.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>Probability: %{percent}<extra></extra>"
        )
        
        fig_playoff.update_layout(height=400)
        st.plotly_chart(fig_playoff, use_container_width=True)


def main():
    """Main application function."""
    try:
        # Render page header and get season
        selected_season = render_page_header()
        st.markdown("---")
        
        # Load season data
        with st.spinner(f"📊 Loading {selected_season} season summary..."):
            season_data = load_season_summary(DEFAULT_TEAM_ID, selected_season)
        
        # Render all analysis sections
        render_season_overview(season_data, selected_season)
        
        st.markdown("---")
        render_monthly_trends()
        
        st.markdown("---")
        render_goals_progress()
        
        st.markdown("---")
        render_detailed_statistics(season_data)
        
        st.markdown("---")
        render_conference_standings()
        
        st.markdown("---")
        render_upcoming_challenges()
        
        st.markdown("---")
        render_season_projections()
        
        # Footer with timestamp
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.caption(f"**Season:** {selected_season}")
            
        with col2:
            st.caption(f"**Team:** Brooklyn Nets")
            
        with col3:
            st.caption(f"**Updated:** {datetime.now().strftime('%B %d, %Y')}")
        
    except Exception as e:
        st.error("An error occurred while loading the season summary.")
        logger.error(f"Season summary error: {e}")
        
        if st.button("🔄 Retry"):
            st.cache_data.clear()
            st.rerun()


if __name__ == "__main__":
    main()