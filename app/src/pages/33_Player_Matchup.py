import os
import logging
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks
import plotly.graph_objects as go
from modules import api_client

logger = logging.getLogger(__name__)
api_client.ensure_api_base()

def call_get_raw(endpoint: str, params: dict | None = None, timeout=5):
    return api_client.api_get(endpoint, params=params, timeout=timeout)


def get_players(params: dict | None = None):
    try:
        return api_client.get_players(params=params)
    except Exception:
        data = api_client.api_get('/basketball/players', params=params)
        if isinstance(data, dict) and 'players' in data:
            return data.get('players', [])
        if isinstance(data, list):
            return data
        return []

def get_player_matchup(endpoint_or_query: str):
    path, params = api_client._parse_endpoint_with_query(endpoint_or_query)
    return call_get_raw(path or '/analytics/player-matchups', params)

st.set_page_config(page_title='Player Matchup - Head Coach', layout='wide')
SideBarLinks()
st.title('Player Matchup — Head Coach')
st.write('')

def make_request(endpoint, method='GET', data=None):
    if endpoint.startswith('/basketball/players') and method == 'GET':
        players = get_players(data or {}) or []
        return {'players': players}
    if endpoint.startswith('/analytics/player-matchups') and method == 'GET':
        return get_player_matchup(endpoint) or {}
    return {}

players = get_players({}) or []
# Normalize to list of dicts
if isinstance(players, dict) and 'players' in players:
    players = players['players'] or []
if not isinstance(players, list):
    players = []

if players:
    # Deduplicate by player_id
    dedup_map = {}
    for p in players:
        if isinstance(p, dict):
            pid = p.get('player_id') or p.get('id')
            if pid not in dedup_map:
                dedup_map[pid] = p
    unique_players = list(dedup_map.values())
    player_names = sorted([f"{(p.get('first_name') or '').strip()} {(p.get('last_name') or '').strip()}".strip() for p in unique_players if isinstance(p, dict)])

    c1, c2 = st.columns(2)
    with c1:
        p1 = st.selectbox('Player 1', player_names, index=0)
    with c2:
        p2 = st.selectbox('Player 2', player_names, index=1 if len(player_names) > 1 else 0)

    if st.button('Get Matchup Analysis'):
        if p1 == p2:
            st.warning('Please select two different players.')
        else:
            try:
                p1_id = [p.get('player_id') for p in unique_players if f"{p.get('first_name','')} {p.get('last_name','')}".strip() == p1][0]
                p2_id = [p.get('player_id') for p in unique_players if f"{p.get('first_name','')} {p.get('last_name','')}".strip() == p2][0]
            except Exception:
                st.error('Failed to resolve player IDs')
                p1_id = p2_id = None

            if p1_id and p2_id:
                data = make_request(f'/analytics/player-matchups?player1_id={p1_id}&player2_id={p2_id}') or {}
                if data and 'summary' in data:
                    s = data['summary']
                    p1s = s['player1']
                    p2s = s['player2']

                    st.subheader(f'{p1} vs {p2}')
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(f"{p1} Avg PPG", f"{p1s['avg_points']:.1f}")
                        st.write(f"Off: {p1s.get('offensive_rating','N/A')}")
                        st.write(f"Def: {p1s.get('defensive_rating','N/A')}")
                    with col2:
                        st.metric(f"{p2} Avg PPG", f"{p2s['avg_points']:.1f}")
                        st.write(f"Off: {p2s.get('offensive_rating','N/A')}")
                        st.write(f"Def: {p2s.get('defensive_rating','N/A')}")
                    with col3:
                        adv = s.get('advantage','Unknown')
                        if adv == 'Player1':
                            st.success(f'Advantage: {p1}')
                        elif adv == 'Player2':
                            st.success(f'Advantage: {p2}')
                        elif adv == 'Even':
                            st.info('Advantage: Even')
                        else:
                            st.write('Advantage: N/A')

                        if s.get('recommendation'):
                            st.markdown('**Tactical Recommendation**')
                            st.info(s.get('recommendation'))

                    try:
                        labels = ['Offense','Defense']
                        v1 = [p1s.get('offensive_rating',0), p1s.get('defensive_rating',0)]
                        v2 = [p2s.get('offensive_rating',0), p2s.get('defensive_rating',0)]
                        fig = go.Figure()
                        fig.add_trace(go.Scatterpolar(r=v1+[v1[0]], theta=labels+[labels[0]], fill='toself', name=p1))
                        fig.add_trace(go.Scatterpolar(r=v2+[v2[0]], theta=labels+[labels[0]], fill='toself', name=p2))
                        fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=True, height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass

                    if data.get('matchup_games'):
                        st.subheader('Recent Matchups')
                        dfm = pd.DataFrame(data['matchup_games'])
                        st.dataframe(dfm, use_container_width=True, hide_index=True)

                    # Removed raw API response per request

 
