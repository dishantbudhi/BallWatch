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

        # Robust handling of the API response and helpful debug output
        if lineup_data is None:
            st.error("Failed to retrieve lineup data from API.")
        elif 'lineup_effectiveness' not in lineup_data:
            st.error("Unexpected API response structure from /analytics/lineup-configurations")
            with st.expander("Raw API response"):
                st.json(lineup_data)
        else:
            lineups_raw = lineup_data['lineup_effectiveness']
            st.info(f"API returned {len(lineups_raw)} lineup records")

            if not lineups_raw:
                st.warning("No lineup data available for this team.")
                with st.expander("Raw API response"):
                    st.json(lineup_data)
            else:
                # Build DataFrame robustly and coerce plus_minus to numeric
                lineups_df = pd.DataFrame(lineups_raw)

                if 'plus_minus' in lineups_df.columns:
                    lineups_df['plus_minus'] = pd.to_numeric(lineups_df['plus_minus'], errors='coerce')
                else:
                    st.warning("API response missing 'plus_minus' field. Showing raw data.")
                    with st.expander("Raw lineup data"):
                        st.json(lineups_raw)

                # Check for valid plus_minus values
                if lineups_df.empty or lineups_df.get('plus_minus') is None or lineups_df['plus_minus'].dropna().empty:
                    st.warning("No valid plus_minus values in lineup data.")
                    with st.expander("Raw lineup dataframe"):
                        st.write(lineups_df)
                else:
                    # Prepare data for chart
                    lineups_df = lineups_df.sort_values(by='plus_minus', ascending=True)

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