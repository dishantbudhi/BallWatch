import logging
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')
SideBarLinks()
st.title('Scouting Reports')

BASE_URL = "http://api:4000"


def make_request(endpoint, method='GET', data=None):
    """Makes a request to the specified API endpoint."""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == 'GET':
            response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None


# Load teams for selection
teams_data = make_request("/basketball/teams")
if teams_data and 'teams' in teams_data:
    team_names = [team['name'] for team in teams_data['teams']]

    # Try to determine the user's team from session state. Map known users to their team.
    default_team_map = {
        # Head Coach & GM example
        'Marcus': 'Brooklyn Nets',
        'Andre': 'Brooklyn Nets',
        # other known first names can be added here
        'Mike': None,
        'Johnny': None
    }

    # Determine the user's team using a unique identifier if available (scalable)
    # Prefer a unique id in session_state (e.g. 'user_id', 'username', or 'user_key').
    user_identifier = (
        st.session_state.get('user_id')
        or st.session_state.get('username')
        or st.session_state.get('user_key')
    )

    default_team_name = None

    # If the logged-in user is the head coach, prefer a first-name mapping to auto-select their team
    if st.session_state.get('role') == 'head_coach':
        headcoach_firstname_map = {
            'Marcus': 'Brooklyn Nets'
        }
        fn = st.session_state.get('first_name')
        if fn and fn in headcoach_firstname_map:
            default_team_name = headcoach_firstname_map[fn]

    # 1) If we have a unique identifier, try to fetch the user's profile from the backend
    if user_identifier:
        user_profile = make_request(f"/users/{user_identifier}")
        if user_profile:
            # Accept several possible shapes returned by the API
            if isinstance(user_profile, dict):
                if user_profile.get('team_name'):
                    default_team_name = user_profile.get('team_name')
                elif user_profile.get('team') and isinstance(user_profile.get('team'), dict):
                    default_team_name = user_profile['team'].get('name')
                elif user_profile.get('team_id'):
                    # convert id to name using teams_data
                    tid = user_profile.get('team_id')
                    default_team_name = next((t['name'] for t in teams_data['teams'] if t['team_id'] == tid), None)

    # 2) Fallback to a hardcoded mapping keyed by a unique identifier (extendable)
    if not default_team_name and user_identifier:
        default_id_map = {
            # use stable unique keys (e.g. usernames or ids) here
            'marcus_thompson': 'Brooklyn Nets',
            'andre_wu': 'Brooklyn Nets'
        }
        default_team_name = default_id_map.get(user_identifier)

    # 3) Last-resort fallback to the legacy first_name mapping but warn it's not ideal
    if not default_team_name:
        first_name = st.session_state.get('first_name')
        if first_name:
            fallback_map = {
                'Marcus': 'Brooklyn Nets',
                'Andre': 'Brooklyn Nets'
            }
            default_team_name = fallback_map.get(first_name)
            if default_team_name:
                st.warning('Using first-name fallback to determine your team. Consider logging in with a unique user identifier for a more reliable experience.')

    your_team_id = None

    if default_team_name and default_team_name in team_names:
        # Display the inferred team and use its id
        st.write(f"Your Team: {default_team_name}")
        your_team_id = next((team['team_id'] for team in teams_data['teams'] if team['name'] == default_team_name), None)
    else:
        # Fall back to allowing the user to pick their team
        your_team = st.selectbox("Select Your Team:", team_names)
        your_team_id = next((team['team_id'] for team in teams_data['teams'] if team['name'] == your_team), None)

    # Always select an opponent to scout
    selected_opponent = st.selectbox("Select a team to scout:", team_names)

    if st.button("Get Scouting Report"):
        if your_team_id is None:
            st.error("Could not determine your team. Please select your team.")
        else:
            opponent_id = [team['team_id']
                           for team in teams_data['teams'] if team['name'] == selected_opponent][0]

            report_data = make_request(
                f"/analytics/opponent-reports?team_id={your_team_id}&opponent_id={opponent_id}")

        if report_data:
            st.subheader(f"Scouting Report: {selected_opponent}")

            # Display Key Metrics
            if 'recent_performance' in report_data:
                performance = report_data['recent_performance']
                avg_scored = performance.get('avg_points_scored', 0)
                avg_allowed = performance.get('avg_points_allowed', 0)

                col1, col2 = st.columns(2)
                col1.metric("Avg. Points Scored", f"{float(avg_scored):.1f}")
                col2.metric("Avg. Points Allowed", f"{float(avg_allowed):.1f}")

            # Display Key Players
            if 'key_players' in report_data and report_data['key_players']:
                st.subheader("Key Players")
                players_df = pd.DataFrame(report_data['key_players'])

                cols = st.columns(len(players_df))
                for i, player in players_df.iterrows():
                    with cols[i]:
                        st.info(
                            f"**{player['first_name']} {player['last_name']}** ({player['position']})")
                        # FIX: Convert string values to float before formatting
                        st.metric("PPG", f"{float(player['avg_points']):.1f}")
                        st.metric("RPG", f"{float(player['avg_rebounds']):.1f}")
                        st.metric("APG", f"{float(player['avg_assists']):.1f}")

            # Raw Data
            with st.expander("View Raw Data"):
                st.write(report_data)