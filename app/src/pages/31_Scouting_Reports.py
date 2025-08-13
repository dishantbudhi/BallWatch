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
    
    your_team = st.selectbox("Select Your Team:", team_names)
    selected_opponent = st.selectbox("Select a team to scout:", team_names)

    if st.button("Get Scouting Report"):
        your_team_id = [team['team_id']
                        for team in teams_data['teams'] if team['name'] == your_team][0]
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