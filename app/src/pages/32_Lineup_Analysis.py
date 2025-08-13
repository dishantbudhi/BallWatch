import logging
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks
import plotly.express as px

logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')
SideBarLinks()
st.title('Lineup Analysis')

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
        "Select a team to analyze lineups:", team_names)

    if st.button("Get Lineup Analysis"):
        team_id = [team['team_id']
                   for team in teams_data['teams'] if team['name'] == selected_team][0]
        lineup_data = make_request(
            f"/analytics/lineup-configurations?team_id={team_id}")

        if lineup_data and 'lineup_effectiveness' in lineup_data:
            st.subheader(f"Lineup Effectiveness for {selected_team}")

            lineups_df = pd.DataFrame(lineup_data['lineup_effectiveness'])

            if not lineups_df.empty:
                # Prepare data for chart
                lineups_df = lineups_df.sort_values(
                    by='plus_minus', ascending=True)

                fig = px.bar(lineups_df,
                             x='plus_minus',
                             y='lineup',
                             orientation='h',
                             title='Lineup Plus/Minus',
                             labels={'lineup': 'Lineup',
                                     'plus_minus': 'Plus/Minus'},
                             color='plus_minus',
                             color_continuous_scale=px.colors.sequential.RdBu)
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("View Raw Data"):
                    st.table(lineups_df)
            else:
                st.warning("No lineup data available for this team.")