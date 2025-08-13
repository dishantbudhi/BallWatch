import logging
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')
SideBarLinks()
st.title('Player Matchup Analysis')

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

# Load players for selection
players_data = make_request("/basketball/players")
if players_data and 'players' in players_data:
    players = players_data['players']
    player_names = sorted([f"{player['first_name']} {player['last_name']}" for player in players])

    col1, col2 = st.columns(2)
    with col1:
        player1_name = st.selectbox("Select Player 1:", player_names, index=0)
    with col2:
        player2_name = st.selectbox("Select Player 2:", player_names, index=1)

    if st.button("Get Matchup Analysis"):
        if player1_name == player2_name:
            st.warning("Please select two different players.")
        else:
            player1_id = [p['player_id'] for p in players if f"{p['first_name']} {p['last_name']}" == player1_name][0]
            player2_id = [p['player_id'] for p in players if f"{p['first_name']} {p['last_name']}" == player2_name][0]

            matchup_data = make_request(f"/analytics/player-matchups?player1_id={player1_id}&player2_id={player2_id}")

            if matchup_data and 'summary' in matchup_data:
                summary = matchup_data['summary']
                player1_summary = summary['player1']
                player2_summary = summary['player2']

                st.subheader(f"Head-to-Head: {player1_name} vs. {player2_name}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(f"{player1_name}'s Avg Points", f"{player1_summary['avg_points']:.1f}")
                with col2:
                    st.metric(f"{player2_name}'s Avg Points", f"{player2_summary['avg_points']:.1f}")
                with col3:
                     st.metric("Head-to-Head Wins", f"{player1_summary['head_to_head_wins']} - {player2_summary['head_to_head_wins']}")
                
                if matchup_data['matchup_games']:
                    st.subheader("Recent Matchups")
                    df_matchups = pd.DataFrame(matchup_data['matchup_games'])
                    st.dataframe(df_matchups[[
                        'game_date', 'home_team', 'away_team', 
                        'player1_points', 'player1_rebounds', 'player1_assists',
                        'player2_points', 'player2_rebounds', 'player2_assists'
                    ]].rename(columns={
                        'game_date': 'Date',
                        'home_team': 'Home',
                        'away_team': 'Away',
                        'player1_points': f'{player1_name} PTS',
                        'player1_rebounds': f'{player1_name} REB',
                        'player1_assists': f'{player1_name} AST',
                        'player2_points': f'{player2_name} PTS',
                        'player2_rebounds': f'{player2_name} REB',
                        'player2_assists': f'{player2_name} AST'
                    }), use_container_width=True)
                else:
                    st.info("These players have not played against each other in the available data.")

                with st.expander("View Raw API Response"):
                    st.json(matchup_data)