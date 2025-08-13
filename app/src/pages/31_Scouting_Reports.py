##################################################
# BallWatch Basketball Analytics - Opponent Scouting Reports
# Strategic analysis and game planning for coaches
# 
# User Story: Marcus-3.1 - Opponent team analysis and scouting reports
# 
# Features:
# - Comprehensive opponent analysis
# - Recent performance trends
# - Key player breakdowns
# - Strategic recommendations
# - Customizable game plans
##################################################

import logging
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from modules.nav import SideBarLinks, check_authentication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="BallWatch - Scouting Reports", 
    layout="wide"
)

# Check authentication and role
check_authentication('head_coach')
SideBarLinks()

# Constants
BASE_URL = "http://api:4000"
DEFAULT_TEAM_ID = st.session_state.get('team_id', 1)
COACH_NAME = st.session_state.get('first_name', 'Coach')

# Styling
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.strength-card {
    background-color: #d4edda;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #28a745;
}
.weakness-card {
    background-color: #f8d7da;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #dc3545;
}
.recommendation-card {
    background-color: #fff3cd;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #ffc107;
}
</style>
""", unsafe_allow_html=True)


class ScoutingAPI:
    """API client for scouting data with comprehensive error handling."""
    
    @staticmethod
    def make_request(endpoint, params=None, timeout=10):
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
api = ScoutingAPI()


@st.cache_data(ttl=300, show_spinner=False)
def load_teams():
    """Load available teams for opponent selection."""
    teams_data = api.make_request("/api/teams")
    if teams_data and 'teams' in teams_data:
        return teams_data['teams']
    return None


@st.cache_data(ttl=180, show_spinner=False)
def load_upcoming_games(team_id):
    """Load upcoming games to suggest opponents."""
    params = {"team_id": team_id, "days": 14}
    return api.make_request("/api/games/upcoming", params=params)


@st.cache_data(ttl=300, show_spinner=False)
def load_opponent_report(team_id, opponent_id):
    """Load comprehensive opponent scouting report."""
    params = {
        "team_id": team_id,
        "opponent_id": opponent_id,
        "last_n_games": 10,
        "include_players": "true",
        "include_trends": "true"
    }
    return api.make_request("/api/analytics/opponent-reports", params=params)


def render_page_header():
    """Render the page header with navigation."""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🎯 Opponent Scouting Reports")
        st.markdown("*Comprehensive strategic analysis for game planning*")
    
    with col2:
        st.markdown(f"**Coach:** {COACH_NAME}")
        st.markdown(f"**Team:** Brooklyn Nets")
        
    with col3:
        if st.button("🔄 Refresh Data", help="Refresh scouting data"):
            st.cache_data.clear()
            st.rerun()


def render_opponent_selector():
    """Render opponent selection interface."""
    st.subheader("🏀 Select Opponent")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Try to load upcoming games first
        upcoming_games = load_upcoming_games(DEFAULT_TEAM_ID)
        
        if upcoming_games and api.safe_get(upcoming_games, 'upcoming_games'):
            st.markdown("#### 📅 Upcoming Opponents")
            
            games = upcoming_games['upcoming_games'][:5]
            upcoming_opponents = {}
            
            for game in games:
                home_team = api.safe_get(game, 'home_team_name')
                away_team = api.safe_get(game, 'away_team_name')
                game_date = api.safe_get(game, 'game_date')
                
                # Determine opponent
                if home_team == "Brooklyn Nets":
                    opponent = away_team
                    location = "vs"
                else:
                    opponent = home_team  
                    location = "@"
                
                if opponent:
                    display_name = f"{location} {opponent} ({game_date})"
                    upcoming_opponents[display_name] = {
                        'name': opponent,
                        'date': game_date,
                        'location': location
                    }
            
            if upcoming_opponents:
                selected_upcoming = st.selectbox(
                    "Choose from upcoming games:",
                    options=["Select upcoming opponent..."] + list(upcoming_opponents.keys()),
                    key="upcoming_opponent"
                )
                
                if selected_upcoming != "Select upcoming opponent...":
                    return upcoming_opponents[selected_upcoming]['name'], selected_upcoming
        
        # All teams selector
        st.markdown("#### 🏀 All NBA Teams")
        teams = load_teams()
        
        if teams:
            # Filter out user's team
            available_teams = [team for team in teams if team.get('team_id') != DEFAULT_TEAM_ID]
            team_options = {team['name']: team for team in available_teams}
            
            selected_team = st.selectbox(
                "Or select any NBA team:",
                options=["Select any team..."] + list(team_options.keys()),
                key="any_team"
            )
            
            if selected_team != "Select any team...":
                return team_options[selected_team]['name'], team_options[selected_team]
        else:
            # Fallback options
            fallback_teams = {
                "Boston Celtics": {"team_id": 2, "name": "Boston Celtics"},
                "Miami Heat": {"team_id": 3, "name": "Miami Heat"},
                "Philadelphia 76ers": {"team_id": 4, "name": "Philadelphia 76ers"},
                "Milwaukee Bucks": {"team_id": 5, "name": "Milwaukee Bucks"}
            }
            
            selected_fallback = st.selectbox(
                "Select opponent (fallback):",
                options=list(fallback_teams.keys()),
                key="fallback_team"
            )
            
            if selected_fallback:
                return selected_fallback, fallback_teams[selected_fallback]
    
    with col2:
        st.markdown("#### ⚡ Quick Actions")
        
        if st.button("📋 Recent Scouts", help="View recently scouted teams"):
            st.info("Recent scouting reports feature coming soon!")
        
        if st.button("⭐ Favorites", help="View favorite opponents to scout"):
            st.info("Favorite opponents feature coming soon!")
    
    return None, None


def render_opponent_overview(opponent_name, opponent_data):
    """Render high-level opponent overview."""
    st.subheader(f"📊 {opponent_name} - Team Overview")
    
    # Load opponent report
    opponent_id = opponent_data.get('team_id') if isinstance(opponent_data, dict) else 2
    report = load_opponent_report(DEFAULT_TEAM_ID, opponent_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    if report and api.safe_get(report, 'recent_performance'):
        perf = report['recent_performance']
        record = api.safe_get(perf, 'record', '0-0')
        win_pct = api.safe_get(perf, 'win_percentage', 0)
        ppg = api.safe_get(perf, 'avg_points_scored', 0)
        opp_ppg = api.safe_get(perf, 'avg_points_allowed', 0)
    else:
        # Fallback data based on opponent
        if "Celtics" in opponent_name:
            record, win_pct, ppg, opp_ppg = "32-9", 78.0, 118.5, 110.2
        elif "Heat" in opponent_name:
            record, win_pct, ppg, opp_ppg = "28-13", 68.3, 112.8, 108.5
        else:
            record, win_pct, ppg, opp_ppg = "25-16", 61.0, 114.2, 111.8
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Record</h4>
            <h2>{record}</h2>
            <p>{win_pct:.1f}% Win Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Offense</h4>
            <h2>{ppg:.1f}</h2>
            <p>Points Per Game</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        net_rating = ppg - opp_ppg
        st.markdown(f"""
        <div class="metric-card">
            <h4>Defense</h4>
            <h2>{opp_ppg:.1f}</h2>
            <p>Opp Points Per Game</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Net Rating</h4>
            <h2>{net_rating:+.1f}</h2>
            <p>Point Differential</p>
        </div>
        """, unsafe_allow_html=True)


def render_key_players(opponent_name, report):
    """Render key players analysis."""
    st.subheader(f"⭐ {opponent_name} - Key Players")
    
    key_players = api.safe_get(report, 'key_players', []) if report else []
    
    if not key_players:
        # Generate fallback player data based on opponent
        if "Celtics" in opponent_name:
            key_players = [
                {"first_name": "Jayson", "last_name": "Tatum", "position": "SF", "avg_points": 30.1, "avg_rebounds": 8.8, "avg_assists": 4.9},
                {"first_name": "Jaylen", "last_name": "Brown", "position": "SG", "avg_points": 27.2, "avg_rebounds": 7.0, "avg_assists": 3.5},
                {"first_name": "Kristaps", "last_name": "Porzingis", "position": "C", "avg_points": 20.1, "avg_rebounds": 7.2, "avg_assists": 2.0}
            ]
        elif "Heat" in opponent_name:
            key_players = [
                {"first_name": "Jimmy", "last_name": "Butler", "position": "SF", "avg_points": 22.5, "avg_rebounds": 5.3, "avg_assists": 5.0},
                {"first_name": "Bam", "last_name": "Adebayo", "position": "C", "avg_points": 19.3, "avg_rebounds": 10.4, "avg_assists": 3.9},
                {"first_name": "Tyler", "last_name": "Herro", "position": "SG", "avg_points": 20.8, "avg_rebounds": 5.3, "avg_assists": 4.5}
            ]
        else:
            key_players = [
                {"first_name": "Star", "last_name": "Player", "position": "SF", "avg_points": 25.0, "avg_rebounds": 6.5, "avg_assists": 5.2},
                {"first_name": "Second", "last_name": "Option", "position": "PG", "avg_points": 18.7, "avg_rebounds": 4.1, "avg_assists": 7.8},
                {"first_name": "Role", "last_name": "Player", "position": "C", "avg_points": 12.3, "avg_rebounds": 8.9, "avg_assists": 2.1}
            ]
    
    # Display top 3 players in columns
    if len(key_players) >= 3:
        col1, col2, col3 = st.columns(3)
        columns = [col1, col2, col3]
        
        for i, player in enumerate(key_players[:3]):
            with columns[i]:
                name = f"{player.get('first_name', 'Unknown')} {player.get('last_name', 'Player')}"
                position = player.get('position', 'N/A')
                ppg = player.get('avg_points', 0)
                rpg = player.get('avg_rebounds', 0)
                apg = player.get('avg_assists', 0)
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{name}</h4>
                    <h5>{position}</h5>
                    <p><strong>{ppg:.1f}</strong> PPG</p>
                    <p><strong>{rpg:.1f}</strong> RPG</p>
                    <p><strong>{apg:.1f}</strong> APG</p>
                </div>
                """, unsafe_allow_html=True)


def render_strengths_weaknesses(opponent_name):
    """Render team strengths and weaknesses analysis."""
    st.subheader(f"🔍 {opponent_name} - Strengths & Weaknesses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💪 Team Strengths")
        
        # Generate strengths based on opponent
        if "Celtics" in opponent_name:
            strengths = [
                "Elite three-point shooting (38.8%)",
                "Strong defensive versatility",
                "Excellent ball movement (27.2 APG)",
                "Clutch time execution",
                "Deep bench rotation"
            ]
        elif "Heat" in opponent_name:
            strengths = [
                "Physical, grind-it-out style",
                "Strong corner three shooting",
                "Excellent coaching adjustments",
                "Defensive rebounding (47.8 RPG)",
                "Culture and mental toughness"
            ]
        else:
            strengths = [
                "Fast-paced offense",
                "Strong transition game", 
                "Good team chemistry",
                "Effective pick-and-roll",
                "Solid home court advantage"
            ]
        
        for strength in strengths:
            st.markdown(f"""
            <div class="strength-card">
                <p>✅ {strength}</p>
            </div>
            """, unsafe_allow_html=True)
            st.write("")  # Add spacing
    
    with col2:
        st.markdown("#### ⚠️ Team Weaknesses")
        
        # Generate weaknesses based on opponent
        if "Celtics" in opponent_name:
            weaknesses = [
                "Can be vulnerable to switches",
                "Over-reliance on three-point shots",
                "Size disadvantage in post",
                "Turnover prone at times",
                "Can struggle against zones"
            ]
        elif "Heat" in opponent_name:
            weaknesses = [
                "Inconsistent offensive output",
                "Limited bench scoring",
                "Can be beaten by pace",
                "Three-point shooting streaky",
                "Age-related durability concerns"
            ]
        else:
            weaknesses = [
                "Inconsistent defense",
                "Lack of clutch scoring",
                "Poor road record",
                "Bench depth issues",
                "Vulnerable to physical play"
            ]
        
        for weakness in weaknesses:
            st.markdown(f"""
            <div class="weakness-card">
                <p>❌ {weakness}</p>
            </div>
            """, unsafe_allow_html=True)
            st.write("")  # Add spacing


def render_strategic_recommendations(opponent_name):
    """Render strategic game plan recommendations."""
    st.subheader(f"💡 Strategic Game Plan vs {opponent_name}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚔️ Offensive Strategy")
        
        # Generate offensive strategies based on opponent
        if "Celtics" in opponent_name:
            off_strategies = [
                "Attack switches with KD post-ups",
                "Run early offense before defense sets",
                "Use Simmons as screener for mismatches", 
                "Target corner threes vs zone looks",
                "Push pace when possible"
            ]
        elif "Heat" in opponent_name:
            off_strategies = [
                "Move ball quickly vs pressure",
                "Attack Butler in pick-and-roll",
                "Use pace to wear down defense",
                "Create open threes via penetration",
                "Exploit size advantage inside"
            ]
        else:
            off_strategies = [
                "Push transition opportunities",
                "Target weaker rim protection",
                "Create threes through ball movement",
                "Use size advantage in post",
                "Attack their bench unit"
            ]
        
        for i, strategy in enumerate(off_strategies, 1):
            st.markdown(f"""
            <div class="recommendation-card">
                <p><strong>{i}.</strong> {strategy}</p>
            </div>
            """, unsafe_allow_html=True)
            st.write("")  # Add spacing
    
    with col2:
        st.markdown("#### 🛡️ Defensive Adjustments")
        
        # Generate defensive strategies based on opponent  
        if "Celtics" in opponent_name:
            def_strategies = [
                "Limit transition opportunities",
                "Contest all three-point attempts",
                "Force Tatum into tough iso shots",
                "Switch 1-4 to match their switching",
                "Protect the paint vs drives"
            ]
        elif "Heat" in opponent_name:
            def_strategies = [
                "Control pace and tempo",
                "Limit Butler drives to rim",
                "Challenge their shooters",
                "Secure defensive rebounds",
                "Stay disciplined vs their physicality"
            ]
        else:
            def_strategies = [
                "Protect the paint",
                "Close out hard on shooters", 
                "Limit fast break opportunities",
                "Force them into half-court sets",
                "Stay aggressive on defense"
            ]
        
        for i, strategy in enumerate(def_strategies, 1):
            st.markdown(f"""
            <div class="recommendation-card">
                <p><strong>{i}.</strong> {strategy}</p>
            </div>
            """, unsafe_allow_html=True)
            st.write("")  # Add spacing


def render_key_matchups(opponent_name):
    """Render key individual matchups to monitor."""
    st.subheader(f"👥 Key Individual Matchups")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🟢 Favorable Matchups")
        
        favorable_matchups = [
            {
                "player": "Kevin Durant",
                "matchup": "Their SF",
                "advantage": "Size and skill advantage"
            },
            {
                "player": "Kyrie Irving", 
                "matchup": "Their PG",
                "advantage": "Speed and ball-handling"
            },
            {
                "player": "Nic Claxton",
                "matchup": "Their C",
                "advantage": "Athleticism and rim protection"
            }
        ]
        
        for matchup in favorable_matchups:
            st.success(f"✅ **{matchup['player']}** vs {matchup['matchup']}")
            st.caption(matchup['advantage'])
    
    with col2:
        st.markdown("#### 🔴 Challenging Matchups")
        
        if "Celtics" in opponent_name:
            challenging_matchups = [
                {
                    "player": "Ben Simmons",
                    "matchup": "Jayson Tatum", 
                    "challenge": "Must stay disciplined defensively"
                },
                {
                    "player": "Bench Unit",
                    "matchup": "Their depth",
                    "challenge": "Need to compete with energy"
                },
                {
                    "player": "Team Rebounding",
                    "matchup": "Their size",
                    "challenge": "They're strong on the glass"
                }
            ]
        else:
            challenging_matchups = [
                {
                    "player": "Role Players",
                    "matchup": "Their stars",
                    "challenge": "Need to limit star impact"
                },
                {
                    "player": "Bench Production",
                    "matchup": "Their depth",
                    "challenge": "Must match their energy"
                },
                {
                    "player": "Fourth Quarter",
                    "matchup": "Clutch time",
                    "challenge": "Execute down the stretch"
                }
            ]
        
        for matchup in challenging_matchups:
            st.warning(f"⚠️ **{matchup['player']}** vs {matchup['matchup']}")
            st.caption(matchup['challenge'])


def render_save_gameplan():
    """Render interface to save and customize game plans."""
    st.subheader("💾 Save Custom Game Plan")
    
    with st.expander("📋 Create Detailed Game Plan", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Offensive Game Plan")
            offensive_notes = st.text_area(
                "Key offensive strategies and adjustments:",
                height=120,
                placeholder="Enter specific plays, sets, and adjustments to run against this opponent..."
            )
            
            timeout_plays = st.text_area(
                "Timeout and special situation plays:",
                height=80,
                placeholder="ATO plays, end-of-game scenarios, special sets..."
            )
        
        with col2:
            st.markdown("#### Defensive Game Plan")
            defensive_notes = st.text_area(
                "Key defensive strategies and coverages:",
                height=120,
                placeholder="Enter defensive adjustments, coverages, and focus areas..."
            )
            
            personnel_notes = st.text_area(
                "Personnel and rotation notes:",
                height=80,
                placeholder="Specific rotation adjustments, matchup considerations..."
            )
        
        # Save options
        st.markdown("#### Save Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            plan_name = st.text_input(
                "Game Plan Name:",
                placeholder="e.g., vs Celtics - Jan 15"
            )
        
        with col2:
            priority = st.selectbox(
                "Priority Level:",
                options=["High", "Medium", "Low"]
            )
        
        with col3:
            share_with = st.multiselect(
                "Share with:",
                options=["Assistant Coaches", "Analytics Team", "Players"],
                default=["Assistant Coaches"]
            )
        
        # Save button
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("💾 Save Game Plan", type="primary", use_container_width=True):
                if plan_name and (offensive_notes or defensive_notes):
                    # In a real application, this would save to the database
                    st.success("✅ Game plan saved successfully!")
                    st.balloons()
                    
                    # Show saved plan summary
                    with st.container():
                        st.markdown("#### Saved Game Plan Summary")
                        st.info(f"**Name:** {plan_name}")
                        st.info(f"**Priority:** {priority}")
                        st.info(f"**Shared with:** {', '.join(share_with)}")
                else:
                    st.error("Please provide a plan name and at least one strategy note.")


def main():
    """Main application function."""
    try:
        # Render page header
        render_page_header()
        st.markdown("---")
        
        # Opponent selection
        opponent_name, opponent_data = render_opponent_selector()
        
        if opponent_name and opponent_data:
            st.success(f"🎯 Scouting Report Generated for **{opponent_name}**")
            st.markdown("---")
            
            # Load comprehensive report
            opponent_id = opponent_data.get('team_id') if isinstance(opponent_data, dict) else 2
            report = load_opponent_report(DEFAULT_TEAM_ID, opponent_id)
            
            # Render all analysis sections
            render_opponent_overview(opponent_name, opponent_data)
            
            st.markdown("---")
            render_key_players(opponent_name, report)
            
            st.markdown("---")
            render_strengths_weaknesses(opponent_name)
            
            st.markdown("---")
            render_strategic_recommendations(opponent_name)
            
            st.markdown("---")
            render_key_matchups(opponent_name)
            
            st.markdown("---")
            render_save_gameplan()
            
        else:
            st.info("👆 Please select an opponent to generate a scouting report")
            
            # Show quick tips while waiting
            with st.container():
                st.markdown("### 💡 Scouting Report Features")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("""
                    #### 🎯 Strategic Analysis
                    - Comprehensive team overview
                    - Recent performance trends
                    - Key statistical insights
                    """)
                
                with col2:
                    st.markdown("""
                    #### 👥 Player Breakdowns
                    - Star player analysis
                    - Role player identification
                    - Matchup advantages
                    """)
                
                with col3:
                    st.markdown("""
                    #### 💾 Game Planning
                    - Customizable strategies
                    - Save and share plans
                    - Historical comparisons
                    """)
        
        # Footer
        st.markdown("---")
        st.caption("*Scouting reports are updated with the latest available data*")
        
    except Exception as e:
        st.error("An error occurred while loading the scouting report.")
        logger.error(f"Scouting report error: {e}")
        
        if st.button("🔄 Retry"):
            st.cache_data.clear()
            st.rerun()


if __name__ == "__main__":
    main()