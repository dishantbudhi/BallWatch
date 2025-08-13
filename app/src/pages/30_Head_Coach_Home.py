##################################################
# BallWatch Basketball Analytics - Head Coach Dashboard
# Main dashboard for Head Coach persona (Marcus Thompson)
# 
# User Stories Supported:
# - Marcus-3.1: View upcoming opponent analysis and scouting reports
# - Marcus-3.2: Analyze player matchups for strategic planning
# - Marcus-3.3: Review team roster and player status
# - Marcus-3.4: Evaluate lineup effectiveness and rotations
# - Marcus-3.5: Create and manage game plans
# - Marcus-3.6: Track season progress and team goals
##################################################

import logging
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from modules.nav import SideBarLinks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="BallWatch - Head Coach Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Navigation
SideBarLinks()

# Constants
BASE_URL = "http://api:4000"
DEFAULT_TEAM_ID = st.session_state.get('team_id', 1)  # Brooklyn Nets
COACH_NAME = st.session_state.get('first_name', 'Marcus')

# Check authentication
if not st.session_state.get('authenticated', False) or st.session_state.get('role') != 'head_coach':
    st.error("Access denied. Please log in as Head Coach.")
    st.stop()


class APIClient:
    """Centralized API client with error handling."""
    
    @staticmethod
    def make_request(endpoint, method='GET', params=None, data=None, timeout=10):
        """Make API request with comprehensive error handling."""
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method == 'GET':
                response = requests.get(url, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=timeout)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            if response.status_code in [200, 201]:
                try:
                    return response.json()
                except ValueError as e:
                    logger.error(f"Invalid JSON response: {e}")
                    return None
            elif response.status_code == 404:
                logger.warning(f"Resource not found: {endpoint}")
                return None
            elif response.status_code >= 500:
                logger.error(f"Server error {response.status_code} for {endpoint}")
                return None
            else:
                logger.warning(f"API returned status {response.status_code} for {endpoint}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {endpoint}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {endpoint}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {endpoint}: {e}")
            return None

    @staticmethod
    def safe_get(dictionary, *keys, default=None):
        """Safely get nested dictionary values."""
        try:
            for key in keys:
                dictionary = dictionary[key]
            return dictionary
        except (KeyError, TypeError, AttributeError):
            return default


# Initialize API client
api = APIClient()


@st.cache_data(ttl=300, show_spinner=False)
def load_team_overview(team_id):
    """Load team overview data with caching."""
    return api.make_request(f"/api/teams/{team_id}")


@st.cache_data(ttl=180, show_spinner=False)
def load_upcoming_games(team_id, days=7):
    """Load upcoming games for the team."""
    params = {"team_id": team_id, "days": days}
    return api.make_request("/api/games/upcoming", params=params)


@st.cache_data(ttl=300, show_spinner=False)
def load_team_roster(team_id):
    """Load current team roster."""
    params = {"include_stats": "true"}
    return api.make_request(f"/api/teams/{team_id}/players", params=params)


@st.cache_data(ttl=600, show_spinner=False)
def load_season_summary(team_id):
    """Load season summary data."""
    params = {"entity_type": "team", "entity_id": team_id}
    return api.make_request("/api/analytics/season-summaries", params=params)


def render_header():
    """Render the dashboard header with current time and team info."""
    current_time = datetime.now().strftime("%I:%M %p")
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.title(f"🏀 Welcome Coach {COACH_NAME}!")
        st.markdown(f"**{current_date}** • {current_time}")
        
    with col2:
        # Team logo placeholder
        st.markdown("### Brooklyn Nets")
        st.markdown("*Eastern Conference*")
        
    with col3:
        # Quick status indicator
        if st.button("🔄 Refresh Data", help="Refresh all dashboard data"):
            st.cache_data.clear()
            st.rerun()


def render_priority_alerts():
    """Render priority alerts and action items."""
    st.subheader("⚡ Priority Alerts")
    
    # Load recent team data
    roster_data = load_team_roster(DEFAULT_TEAM_ID)
    season_data = load_season_summary(DEFAULT_TEAM_ID)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚨 Alerts")
        
        alerts = []
        
        # Generate alerts based on data
        if season_data:
            summary = api.safe_get(season_data, 'summary')
            if summary:
                win_pct = api.safe_get(summary, 'wins', 0) / max(api.safe_get(summary, 'games_played', 1), 1)
                if win_pct < 0.500:
                    alerts.append(("warning", f"Team record below .500 ({win_pct:.1%})"))
                
                avg_points = api.safe_get(summary, 'avg_points_scored', 0)
                if avg_points > 0 and avg_points < 110:
                    alerts.append(("error", f"Low offensive output: {avg_points:.1f} PPG"))
        
        if roster_data:
            injured_count = len([p for p in api.safe_get(roster_data, 'players', []) 
                               if api.safe_get(p, 'status') == 'injured'])
            if injured_count > 0:
                alerts.append(("warning", f"{injured_count} player(s) on injury report"))
        
        # Default alerts if no data
        if not alerts:
            alerts = [
                ("info", "Next game preparation needed"),
                ("warning", "Review bench rotation effectiveness"),
                ("info", "Opponent scouting report available")
            ]
        
        for alert_type, message in alerts[:5]:  # Limit to 5 alerts
            if alert_type == "error":
                st.error(f"🔴 {message}")
            elif alert_type == "warning":
                st.warning(f"🟡 {message}")
            else:
                st.info(f"🔵 {message}")
    
    with col2:
        st.markdown("#### ✅ Action Items")
        
        # Time-based action items
        current_hour = datetime.now().hour
        if current_hour < 12:  # Morning
            action_items = [
                "Review film from last game",
                "Prepare today's practice plan",
                "Check injury status updates",
                "Review opponent scouting report"
            ]
        elif current_hour < 18:  # Afternoon
            action_items = [
                "Conduct team practice session",
                "Hold individual player meetings",
                "Finalize rotation adjustments",
                "Coordinate with training staff"
            ]
        else:  # Evening
            action_items = [
                "Finalize tomorrow's game plan",
                "Review starting lineup",
                "Prepare media talking points",
                "Update coaching staff notes"
            ]
        
        for item in action_items:
            st.markdown(f"• {item}")


def render_navigation_tools():
    """Render main navigation tools for coaches."""
    st.subheader("🎯 Coaching Tools")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(
            "🎯 **Scouting Reports**", 
            use_container_width=True, 
            help="Analyze opponents and prepare strategic game plans"
        ):
            st.switch_page("pages/31_Scouting_Reports.py")
            
        st.caption("Opponent analysis & strategy")

    with col2:
        if st.button(
            "📊 **Lineup Analysis**", 
            use_container_width=True, 
            help="Optimize player combinations and rotations"
        ):
            st.switch_page("pages/32_Lineup_Analysis.py")
            
        st.caption("Rotation optimization")

    with col3:
        if st.button(
            "📈 **Season Summary**", 
            use_container_width=True, 
            help="Track season progress and team performance"
        ):
            st.switch_page("pages/33_Season_Summaries.py")
            
        st.caption("Progress tracking")
        
    with col4:
        if st.button(
            "🔄 **Player Matchups**", 
            use_container_width=True, 
            help="Analyze individual player matchup advantages"
        ):
            # Could link to a player matchup analysis page
            st.info("Feature coming soon!")
            
        st.caption("Matchup analysis")


def render_team_snapshot():
    """Render current team performance snapshot."""
    st.subheader("📊 Team Snapshot")
    
    # Load data
    roster_data = load_team_roster(DEFAULT_TEAM_ID)
    season_data = load_season_summary(DEFAULT_TEAM_ID)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Extract metrics or use defaults
    if season_data and api.safe_get(season_data, 'summary'):
        summary = season_data['summary']
        games_played = api.safe_get(summary, 'games_played', 41)
        wins = api.safe_get(summary, 'wins', 24)
        losses = api.safe_get(summary, 'losses', 17)
        avg_points = api.safe_get(summary, 'avg_points_scored', 114.2)
    else:
        games_played, wins, losses, avg_points = 41, 24, 17, 114.2
    
    roster_size = len(api.safe_get(roster_data, 'players', [])) if roster_data else 15
    
    with col1:
        st.metric(
            "Season Record", 
            f"{wins}-{losses}", 
            delta=f"{(wins/(wins+losses))*100:.1f}% Win Rate" if wins+losses > 0 else None
        )
    
    with col2:
        st.metric("Points Per Game", f"{avg_points:.1f}", "Offense")
    
    with col3:
        st.metric("Active Roster", str(roster_size), "Players")
    
    with col4:
        games_remaining = 82 - games_played
        st.metric("Games Remaining", str(games_remaining), "Regular Season")


def render_upcoming_schedule():
    """Render upcoming games and schedule."""
    st.subheader("📅 Upcoming Schedule")
    
    upcoming_games = load_upcoming_games(DEFAULT_TEAM_ID, days=10)
    
    if upcoming_games and api.safe_get(upcoming_games, 'upcoming_games'):
        games = upcoming_games['upcoming_games'][:5]  # Show next 5 games
        
        for i, game in enumerate(games, 1):
            game_date = api.safe_get(game, 'game_date', 'TBD')
            game_time = api.safe_get(game, 'game_time', 'TBD')
            home_team = api.safe_get(game, 'home_team_name', 'TBD')
            away_team = api.safe_get(game, 'away_team_name', 'TBD')
            venue = api.safe_get(game, 'venue', 'TBD')
            
            # Determine if home or away
            is_home = home_team == "Brooklyn Nets"
            opponent = away_team if is_home else home_team
            location = "vs" if is_home else "@"
            
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.write(f"**Game {i}**")
                st.write(f"{game_date}")
                
            with col2:
                st.write(f"**{location} {opponent}**")
                st.write(f"{game_time} • {venue}")
                
            with col3:
                if st.button(f"Scout", key=f"scout_{i}", help=f"View scouting report for {opponent}"):
                    st.session_state['selected_opponent'] = opponent
                    st.switch_page("pages/31_Scouting_Reports.py")
    else:
        # Fallback schedule
        fallback_games = [
            {"date": "Jan 15", "opponent": "Boston Celtics", "location": "vs", "time": "7:30 PM"},
            {"date": "Jan 17", "opponent": "Miami Heat", "location": "@", "time": "8:00 PM"},
            {"date": "Jan 19", "opponent": "Philadelphia 76ers", "location": "vs", "time": "7:00 PM"},
            {"date": "Jan 21", "opponent": "Orlando Magic", "location": "@", "time": "7:00 PM"},
            {"date": "Jan 23", "opponent": "Charlotte Hornets", "location": "vs", "time": "7:30 PM"}
        ]
        
        for i, game in enumerate(fallback_games, 1):
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.write(f"**Game {i}**")
                st.write(game['date'])
                
            with col2:
                st.write(f"**{game['location']} {game['opponent']}**")
                st.write(game['time'])
                
            with col3:
                if st.button(f"Scout", key=f"scout_{i}", help=f"Scout {game['opponent']}"):
                    st.info("Scouting feature available in full version")


def render_player_highlights():
    """Render key player performance highlights."""
    st.subheader("🌟 Player Highlights")
    
    roster_data = load_team_roster(DEFAULT_TEAM_ID)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔥 Top Performers")
        
        if roster_data and api.safe_get(roster_data, 'players'):
            # Sort players by average points
            players = roster_data['players']
            top_performers = sorted(
                [p for p in players if api.safe_get(p, 'avg_points', 0) > 0], 
                key=lambda x: api.safe_get(x, 'avg_points', 0), 
                reverse=True
            )[:3]
            
            for player in top_performers:
                name = f"{api.safe_get(player, 'first_name', 'Unknown')} {api.safe_get(player, 'last_name', 'Player')}"
                position = api.safe_get(player, 'position', 'N/A')
                ppg = api.safe_get(player, 'avg_points', 0)
                apg = api.safe_get(player, 'avg_assists', 0)
                rpg = api.safe_get(player, 'avg_rebounds', 0)
                
                st.markdown(f"**{name}** ({position})")
                st.markdown(f"  📈 {ppg:.1f} PPG, {apg:.1f} APG, {rpg:.1f} RPG")
        else:
            # Fallback data
            fallback_players = [
                {"name": "Kevin Durant", "pos": "SF", "ppg": 29.2, "apg": 6.8, "rpg": 6.7},
                {"name": "Kyrie Irving", "pos": "PG", "ppg": 27.1, "apg": 5.3, "rpg": 4.8},
                {"name": "Nic Claxton", "pos": "C", "ppg": 12.1, "apg": 2.1, "rpg": 8.7}
            ]
            
            for player in fallback_players:
                st.markdown(f"**{player['name']}** ({player['pos']})")
                st.markdown(f"  📈 {player['ppg']:.1f} PPG, {player['apg']:.1f} APG, {player['rpg']:.1f} RPG")
    
    with col2:
        st.markdown("#### 📋 Focus Areas")
        
        focus_areas = [
            {"area": "Improve transition defense", "priority": "High", "status": "In Progress"},
            {"area": "Fourth quarter execution", "priority": "High", "status": "Needs Work"},
            {"area": "Bench scoring consistency", "priority": "Medium", "status": "Monitoring"},
            {"area": "Defensive rebounding", "priority": "Medium", "status": "Improved"},
        ]
        
        for focus in focus_areas:
            priority_color = "🔴" if focus["priority"] == "High" else "🟡" if focus["priority"] == "Medium" else "🟢"
            st.markdown(f"{priority_color} **{focus['area']}**")
            st.markdown(f"  Status: {focus['status']}")


def render_coaching_notes():
    """Render coaching notes and reminders."""
    st.subheader("📝 Coaching Notes")
    
    # Initialize session state for notes
    if 'coach_notes' not in st.session_state:
        st.session_state.coach_notes = [
            {
                'date': (datetime.now() - timedelta(days=1)).strftime("%b %d"),
                'note': 'Team responded well to new offensive sets in practice'
            },
            {
                'date': (datetime.now() - timedelta(days=2)).strftime("%b %d"),
                'note': 'Need to address defensive rebounding issues'
            }
        ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display existing notes
        st.markdown("#### Recent Notes")
        
        for note in st.session_state.coach_notes[-5:]:  # Show last 5 notes
            with st.expander(f"{note['date']} - {note['note'][:50]}..."):
                st.write(note['note'])
    
    with col2:
        # Add new note
        st.markdown("#### Quick Note")
        
        with st.form("add_note_form"):
            note_text = st.text_area(
                "Add a coaching note:", 
                height=100,
                placeholder="Enter observations, reminders, or insights..."
            )
            
            if st.form_submit_button("💾 Save Note", use_container_width=True):
                if note_text.strip():
                    new_note = {
                        'date': datetime.now().strftime("%b %d"),
                        'note': note_text.strip()
                    }
                    st.session_state.coach_notes.append(new_note)
                    st.success("Note saved!")
                    st.rerun()
                else:
                    st.error("Please enter a note before saving.")


def render_system_status():
    """Render system status and data freshness."""
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # API status check
        health_data = api.make_request("/api/health")
        if health_data and api.safe_get(health_data, 'status') == 'healthy':
            st.success("🟢 System Online")
        else:
            st.error("🔴 System Issues")
    
    with col2:
        last_refresh = datetime.now().strftime('%I:%M %p')
        st.info(f"🔄 Last Update: {last_refresh}")
    
    with col3:
        st.info(f"👤 Coach: {COACH_NAME}")
    
    with col4:
        st.info(f"🏀 Team ID: {DEFAULT_TEAM_ID}")


def main():
    """Main dashboard rendering function."""
    try:
        # Render all dashboard sections
        render_header()
        
        st.markdown("---")
        render_priority_alerts()
        
        st.markdown("---")
        render_navigation_tools()
        
        st.markdown("---")
        render_team_snapshot()
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            render_upcoming_schedule()
            
        with col2:
            render_player_highlights()
        
        st.markdown("---")
        render_coaching_notes()
        
        render_system_status()
        
    except Exception as e:
        st.error("An error occurred while loading the dashboard.")
        logger.error(f"Dashboard error: {e}")
        
        if st.button("🔄 Retry"):
            st.cache_data.clear()
            st.rerun()


if __name__ == "__main__":
    main()