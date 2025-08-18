"""Player progress tracking and metrics."""

import os
import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime
from modules.nav import SideBarLinks
from modules import api_client

st.set_page_config(page_title='Player Progress - General Manager', layout='wide')
SideBarLinks()

api_client.ensure_api_base()

# Debug mode removed

st.title('Player Progress & Development — General Manager')
st.caption('Track player development, evaluations, and generate development plans.')

def call_get_raw(endpoint: str, params=None, timeout=10):
    return api_client.api_get(endpoint, params=params, timeout=timeout)


def call_post_raw(endpoint: str, data=None, timeout=10):
    return api_client.api_post(endpoint, data=data, timeout=timeout)


def call_put_raw(endpoint: str, data=None, timeout=10):
    return api_client.api_put(endpoint, data=data, timeout=10)


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

def make_request(endpoint, method='GET', data=None):
    # Call backend endpoints directly so this helper can be used anywhere in the file
    try:
        if endpoint.startswith('/basketball/players') and method == 'GET':
            return {'players': get_players({})}
        if endpoint.startswith('/strategy/draft-evaluations') and method == 'GET':
            resp = call_get_raw('/strategy/draft-evaluations')
            if isinstance(resp, dict) and 'evaluations' in resp:
                return {'evaluations': resp.get('evaluations', [])}
            if isinstance(resp, list):
                return {'evaluations': resp}
            return {'evaluations': []}
        if endpoint.startswith('/strategy/draft-evaluations') and method == 'PUT':
            # endpoint expected like '/strategy/draft-evaluations/{id}'
            return call_put_raw(endpoint, data)
    except Exception:
        logger.exception('Exception in make_request')
    return None

# Load data
if st.button("Load Player Data"):
    players_data = make_request("/basketball/players")
    loaded_players = []
    if isinstance(players_data, dict):
        loaded_players = players_data.get('players') or []
    elif isinstance(players_data, list):
        loaded_players = players_data
    st.session_state['players'] = loaded_players
    st.success(f"Loaded {len(loaded_players)} players")

    # Also load evaluations for development insights
    eval_data = make_request("/strategy/draft-evaluations")
    if eval_data and 'evaluations' in eval_data:
        st.session_state['evaluations'] = eval_data['evaluations']

# Main content
if 'players' in st.session_state or 'evaluations' in st.session_state:
    tab1, tab2, tab3 = st.tabs(["Progress Overview", "Individual Tracking", "Development Plans"])
    
    with tab1:
        st.header("Player Progress Overview")
        
        # Use evaluations data if available, otherwise use players data
        if 'evaluations' in st.session_state:
            evaluations = st.session_state['evaluations']
            df = pd.DataFrame(evaluations)
            
            # Create progress metrics
            if not df.empty and 'overall_rating' in df.columns and 'potential_rating' in df.columns:
                # Convert rating columns to numeric
                df['overall_rating'] = pd.to_numeric(df['overall_rating'], errors='coerce').fillna(50)
                df['potential_rating'] = pd.to_numeric(df['potential_rating'], errors='coerce').fillna(50)
                df['offensive_rating'] = pd.to_numeric(df.get('offensive_rating', 50), errors='coerce').fillna(50)
                df['defensive_rating'] = pd.to_numeric(df.get('defensive_rating', 50), errors='coerce').fillna(50)
                
                df['progress_score'] = df['potential_rating'] - df['overall_rating']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Players", len(df))
                
                with col2:
                    high_potential = len(df[df['potential_rating'] >= 85])
                    st.metric("High Potential", high_potential)
                
                with col3:
                    avg_rating = df['overall_rating'].mean()
                    st.metric("Avg Rating", f"{avg_rating:.1f}")
                
                with col4:
                    avg_progress = df['progress_score'].mean()
                    st.metric("Avg Growth Room", f"{avg_progress:.1f}")
                
                # Progress scatter plot
                if len(df) > 0:
                    fig = px.scatter(
                        df,
                        x='overall_rating',
                        y='potential_rating',
                        color='position' if 'position' in df.columns else None,
                        title="Current Rating vs Potential",
                        labels={
                            'overall_rating': 'Current Rating',
                            'potential_rating': 'Potential Rating'
                        }
                    )
                    
                    # Add diagonal reference line
                    fig.add_trace(
                        go.Scatter(x=[0, 100], y=[0, 100], 
                                  mode='lines', 
                                  line=dict(dash='dash', color='gray'),
                                  showlegend=False,
                                  name='Equal Line')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Position breakdown
                if 'position' in df.columns:
                    position_stats = df.groupby('position').agg({
                        'overall_rating': 'mean',
                        'potential_rating': 'mean',
                        'progress_score': 'mean'
                    }).round(1)
                    
                    fig_pos = px.bar(
                        position_stats,
                        y=position_stats.index,
                        x='progress_score',
                        title="Average Growth Potential by Position",
                        orientation='h'
                    )
                    st.plotly_chart(fig_pos, use_container_width=True)
            else:
                st.warning("Missing rating data for progress calculations.")
    
    with tab2:
        st.header("Individual Player Tracking")
        
        if 'evaluations' in st.session_state:
            evaluations = st.session_state['evaluations']
            
            if evaluations:
                # Player selector
                player_options = {}
                for eval in evaluations:
                    display_name = f"{eval['first_name']} {eval['last_name']} ({eval.get('position', 'N/A')})"
                    player_options[display_name] = eval
                
                selected_player = st.selectbox(
                    "Select Player:",
                    options=list(player_options.keys()),
                    key="gm_progress_selected_player"
                )
                
                if selected_player:
                    player_data = player_options[selected_player]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader(f"{player_data['first_name']} {player_data['last_name']}")
                        
                        # Convert ratings to numeric for display
                        overall_rating = pd.to_numeric(player_data.get('overall_rating', 0), errors='coerce') or 0
                        potential_rating = pd.to_numeric(player_data.get('potential_rating', 0), errors='coerce') or 0
                        growth_room = potential_rating - overall_rating
                        
                        # Player info
                        st.info(f"""
                        **Player Profile**
                        - Position: {player_data.get('position', 'N/A')}
                        - Overall Rating: {overall_rating}
                        - Potential Rating: {potential_rating}
                        - Growth Room: {growth_room} points
                        """)
                        
                        # Strengths and weaknesses
                        if player_data.get('strengths'):
                            st.success(f"**Strengths:** {player_data['strengths']}")
                        
                        if player_data.get('weaknesses'):
                            st.warning(f"**Weaknesses:** {player_data['weaknesses']}")
                    
                    with col2:
                        # Rating breakdown radar chart
                        categories = ['Overall', 'Offense', 'Defense', 'Potential']
                        values = [
                            pd.to_numeric(player_data.get('overall_rating', 50), errors='coerce') or 50,
                            pd.to_numeric(player_data.get('offensive_rating', 50), errors='coerce') or 50,
                            pd.to_numeric(player_data.get('defensive_rating', 50), errors='coerce') or 50,
                            pd.to_numeric(player_data.get('potential_rating', 50), errors='coerce') or 50
                        ]
                        
                        fig_radar = go.Figure()
                        fig_radar.add_trace(go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill='toself',
                            name='Current Ratings'
                        ))
                        
                        fig_radar.update_layout(
                            polar=dict(
                                radialaxis=dict(visible=True, range=[0, 100])
                            ),
                            title="Player Rating Breakdown"
                        )
                        st.plotly_chart(fig_radar, use_container_width=True)
                    
                    # Scout notes
                    if player_data.get('scout_notes'):
                        st.text_area("Scout Notes", value=player_data['scout_notes'], disabled=True)
    
    with tab3:
        st.header("Development Plans")
        
        if 'evaluations' in st.session_state:
            evaluations = st.session_state['evaluations']
            df = pd.DataFrame(evaluations)
            
            if not df.empty and 'overall_rating' in df.columns and 'potential_rating' in df.columns:
                # Convert rating columns to numeric
                df['overall_rating'] = pd.to_numeric(df['overall_rating'], errors='coerce').fillna(50)
                df['potential_rating'] = pd.to_numeric(df['potential_rating'], errors='coerce').fillna(50)
                
                # Calculate development priority
                df['growth_potential'] = df['potential_rating'] - df['overall_rating']
                df['development_priority'] = df['growth_potential']
                
                # Sort by development priority
                df_sorted = df.nlargest(10, 'development_priority')
                
                st.subheader("Top Development Priorities")
                
                # Development priority chart
                if not df_sorted.empty:
                    fig_dev = px.bar(
                        df_sorted,
                        x='development_priority',
                        y=df_sorted.apply(lambda x: f"{x['first_name']} {x['last_name']}", axis=1),
                        orientation='h',
                        title="Players with Highest Development Potential",
                        labels={'development_priority': 'Growth Potential (Points)', 'y': 'Player'}
                    )
                    st.plotly_chart(fig_dev, use_container_width=True)
                
                # Development recommendations table
                st.subheader("Development Recommendations")
                
                if not df_sorted.empty:
                    dev_table = df_sorted[['first_name', 'last_name', 'position', 'overall_rating', 'potential_rating', 'growth_potential']].copy()
                    dev_table['recommendation'] = dev_table['growth_potential'].apply(
                        lambda x: 'Priority Focus' if x > 20 else 'Regular Development' if x > 10 else 'Maintain Current'
                    )
                    
                    st.dataframe(
                        dev_table.style.background_gradient(subset=['growth_potential'], cmap='YlOrRd'),
                        use_container_width=True
                    )
                
                # Development insights
                st.subheader("Development Insights")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    avg_growth = df['growth_potential'].mean()
                    st.metric("Average Growth Potential", f"{avg_growth:.1f} points")
                
                with col2:
                    high_growth = len(df[df['growth_potential'] > 15])
                    st.metric("High Growth Players", high_growth)
            else:
                st.warning("Missing rating data for development analysis.")

else:
    st.info("Click 'Load Player Data' to begin tracking player progress and development.")
    

def get_draft_evaluations():
    # lightweight local placeholder — other pages implement full logic
    try:
        data = call_get_raw('/strategy/draft-evaluations')
        if isinstance(data, dict) and 'evaluations' in data:
            return data['evaluations']
        if isinstance(data, list):
            return data
    except Exception:
        logger.exception('Exception in get_draft_evaluations')
    return []


def update_evaluation(evaluation_id, data):
    try:
        return call_put_raw(f"/strategy/draft-evaluations/{evaluation_id}", data)
    except Exception:
        logger.exception('Exception in update_evaluation')
    return None