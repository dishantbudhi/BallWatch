import logging
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')
SideBarLinks()
st.title('Season Summaries')

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
    selected_team = st.selectbox(
        "Select a team to view season summary:", team_names)

    if st.button("Get Season Summary"):
        team_id = [team['team_id']
                   for team in teams_data['teams'] if team['name'] == selected_team][0]
        summary_data = make_request(
            f"/analytics/season-summaries?entity_type=team&entity_id={team_id}")

        if summary_data and 'summary' in summary_data and summary_data['summary'] is not None:
            summary = summary_data['summary']
            st.subheader(
                f"Season Summary for {summary.get('team_name', selected_team)}")

            # Display metrics
            # FIX: Cast wins, losses, and games_played to int to prevent TypeError
            wins = int(summary.get('wins', 0))
            losses = int(summary.get('losses', 0))
            games_played = int(summary.get('games_played', 0))

            col1, col2, col3 = st.columns(3)
            col1.metric("Wins", wins)
            col2.metric("Losses", losses)
            if games_played > 0:
                win_percentage = (wins / games_played) * 100
                col3.metric("Win %", f"{win_percentage:.2f}%")

            # Display gauge chart for point differential
            avg_scored = float(summary.get('avg_points_scored', 0))
            avg_allowed = float(summary.get('avg_points_allowed', 0))
            point_diff = avg_scored - avg_allowed

            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=avg_scored,
                title={'text': "Point Differential"},
                delta={'reference': avg_allowed,
                       'relative': False, 'valueformat': ".1f"},
                gauge={'axis': {'range': [80, 140]},
                       'steps': [
                           {'range': [80, 100], 'color': "lightgray"},
                           {'range': [100, 120], 'color': "gray"}],
                       'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': avg_allowed}}))
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("View Raw Data"):
                st.write(summary)
        else:
            st.error(
                "Could not retrieve season summary. The API may be down or the data is unavailable.")