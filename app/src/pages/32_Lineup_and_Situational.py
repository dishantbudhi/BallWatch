import os
import logging
import streamlit as st
import pandas as pd
from modules.nav import SideBarLinks
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules import api_client
import numpy as np
from datetime import datetime
import json

 

logger = logging.getLogger(__name__)
api_client.ensure_api_base()

def get_situational_performance(team_id: int, last_n_games: int = 20):
    """Get enhanced situational performance data."""
    try:
        endpoint = '/analytics/situational-performance'
        params = {'team_id': team_id, 'last_n_games': last_n_games}
        # Use the shared api_client wrapper
        data = api_client.api_get(endpoint, params=params, timeout=15)

        if not data:
            return None

        return data

    except Exception as e:
        logger.error(f"Error fetching situational performance: {e}")
        return None

# Page configuration
st.set_page_config(page_title='Lineup & Situational - Head Coach', layout='wide')
SideBarLinks()

# Page header
st.title('Lineup & Situational — Head Coach')

# Load teams data
@st.cache_data(ttl=300)
def load_teams():
    """Load and normalize teams response into a list of dicts."""
    try:
        # Try the high-level helper first, then fall back to raw API GET
        data = None
        try:
            data = api_client.get_teams(timeout=5)
        except Exception:
            data = None

        if not data:
            try:
                data = api_client.api_get('/basketball/teams', timeout=5)
            except Exception:
                data = None

        # If we received a JSON string, attempt to parse it
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                # leave as-is; will be handled below
                pass

        # Normalize different possible shapes into a list of team dicts
        teams = []
        if isinstance(data, dict):
            # common shapes: {"teams": [...]}, {"data": [...]}, or a single team dict
            if 'teams' in data and data.get('teams') is not None:
                raw = data.get('teams')
            elif 'data' in data and data.get('data') is not None:
                raw = data.get('data')
            else:
                raw = data

            if isinstance(raw, dict):
                teams = [raw]
            elif isinstance(raw, list):
                teams = raw
            else:
                teams = []

        elif isinstance(data, list):
            teams = data
        else:
            teams = []

        # Convert simple string lists into dicts and normalize ids
        normalized = []
        for t in teams:
            if isinstance(t, str):
                normalized.append({'name': t})
            elif isinstance(t, dict):
                if 'team_id' not in t and 'id' in t:
                    try:
                        t['team_id'] = int(t.get('id')) if t.get('id') is not None else None
                    except Exception:
                        t['team_id'] = t.get('id')
                normalized.append(t)
            elif isinstance(t, (list, tuple)):
                try:
                    team_id = int(t[0]) if len(t) > 0 and t[0] is not None else None
                except Exception:
                    team_id = t[0] if len(t) > 0 else None
                name = t[1] if len(t) > 1 else None
                normalized.append({'team_id': team_id, 'name': name})
            else:
                # ignore unexpected types
                continue

        return normalized

    except Exception as e:
        logger.error(f"Error loading teams: {e}")
        return []

teams = load_teams()

if not teams:
    st.error('⚠️ Unable to load teams data. Please check your API connection.')
    st.stop()

# Use safe access to avoid 'str' items causing AttributeError
team_names = [t.get('name') for t in teams if isinstance(t, dict) and t.get('name')]
team_map = {t.get('name'): t.get('team_id') for t in teams if isinstance(t, dict) and t.get('name') and t.get('team_id')}

# Tabs
tab1, tab2 = st.tabs(['Lineup Analysis', 'Situational Performance'])

# Tab 1: Lineup Analysis (replaced with more robust flow inspired by provided implementation)
with tab1:
    st.header('Lineup Analysis')
    
    if not team_names:
        st.warning('No teams available for analysis.')
    else:
        selected_team = st.selectbox(
            'Select a team to analyze lineups:',
            team_names,
            key='lineup_team_select'
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            analyze_btn = st.button('Get Lineup Analysis', type='primary')
        with col2:
            min_games = st.number_input('Min games together:', min_value=1, max_value=30, value=5)
        
        if analyze_btn and selected_team:
            team_id = team_map.get(selected_team)
            
            if not team_id:
                st.error('Unable to resolve team ID. Please try another team.')
            else:
                with st.spinner(f'Loading lineup data for {selected_team}...'):
                    # call the API and normalize response
                    resp = api_client.api_get('/analytics/lineup-configurations', params={'team_id': team_id, 'min_games': min_games}, timeout=15)

                if not resp:
                    st.warning(f'No lineup data available for {selected_team}.')
                else:
                    # normalize possible response shapes
                    lineups = []
                    if isinstance(resp, dict) and 'lineup_effectiveness' in resp:
                        lineups = resp.get('lineup_effectiveness') or []
                    elif isinstance(resp, dict) and 'lineup_configurations' in resp:
                        lineups = resp.get('lineup_configurations') or []
                    elif isinstance(resp, list):
                        lineups = resp
                    else:
                        # fallback: try to pull a list from resp['data'] or any list-valued field
                        if isinstance(resp, dict):
                            potential = resp.get('data') or []
                            if isinstance(potential, list):
                                lineups = potential

                    lineups = lineups or []

                    if not lineups:
                        st.info('No lineup configurations matched the filters.')
                    else:
                        # ensure consistent dict shape and robust numeric coercion
                        def _num(val):
                            try:
                                if val is None or (isinstance(val, str) and val.strip() == ''):
                                    return 0.0
                                return float(val)
                            except Exception:
                                try:
                                    # last resort
                                    return float(pd.to_numeric(val, errors='coerce'))
                                except Exception:
                                    return 0.0

                        cleaned = []
                        for l in lineups:
                            if not isinstance(l, dict):
                                continue
                            cleaned_item = {
                                'lineup': str(l.get('lineup') if l.get('lineup') is not None else l),
                                'plus_minus': _num(l.get('plus_minus', 0)),
                                'offensive_rating': _num(l.get('offensive_rating', 0)),
                                'defensive_rating': _num(l.get('defensive_rating', 0))
                            }
                            cleaned.append(cleaned_item)

                        df = pd.DataFrame(cleaned)

                        if df.empty:
                            st.info('No lineup configurations matched the filters.')
                        else:
                            df = df.sort_values('plus_minus', ascending=False).reset_index(drop=True)

                            st.subheader(f'Lineup Performance - {selected_team}')

                            # Summary metrics
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                best_pm = df['plus_minus'].max() if 'plus_minus' in df.columns else 0
                                st.metric('Best +/-', f"{best_pm:+.1f}")
                            with col2:
                                avg_pm = df['plus_minus'].mean() if 'plus_minus' in df.columns else 0
                                st.metric('Avg +/-', f"{avg_pm:+.1f}")
                            with col3:
                                best_off = df['offensive_rating'].max() if 'offensive_rating' in df.columns else 0
                                st.metric('Best Off Rating', f"{best_off:.1f}")
                            with col4:
                                best_def = df['defensive_rating'].min() if 'defensive_rating' in df.columns else 0
                                st.metric('Best Def Rating', f"{best_def:.1f}")

                            # Visualization
                            if not df.empty and 'plus_minus' in df.columns:
                                fig = px.bar(
                                    df.head(10),
                                    y='lineup',
                                    x='plus_minus',
                                    orientation='h',
                                    color='plus_minus',
                                    color_continuous_scale='RdYlGn',
                                    color_continuous_midpoint=0,
                                    title='Top 10 Lineups by Plus/Minus',
                                    labels={'plus_minus': 'Plus/Minus', 'lineup': 'Lineup'},
                                    height=400
                                )
                                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                                st.plotly_chart(fig, use_container_width=True)

                            # Recommendations
                            st.subheader('💡 Rotation Recommendations')

                            if len(df) >= 3:
                                top_lineups = df.nlargest(3, 'plus_minus')
                                bottom_lineups = df.nsmallest(2, 'plus_minus')

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown('**✅ Increase Minutes For:**')
                                    for _, row in top_lineups.iterrows():
                                        pm = row['plus_minus']
                                        lineup = row['lineup'][:50] + '...' if len(row['lineup']) > 50 else row['lineup']
                                        if pm > 5:
                                            st.success(f"{lineup} (+{pm:.1f})")
                                        elif pm > 0:
                                            st.info(f"{lineup} (+{pm:.1f})")

                                with col2:
                                    st.markdown('**⚠️ Reduce Minutes For:**')
                                    for _, row in bottom_lineups.iterrows():
                                        pm = row['plus_minus']
                                        lineup = row['lineup'][:50] + '...' if len(row['lineup']) > 50 else row['lineup']
                                        if pm < -5:
                                            st.error(f"{lineup} ({pm:.1f})")
                                        elif pm < 0:
                                            st.warning(f"{lineup} ({pm:.1f})")

                            st.subheader('Full Lineup Data')
                            display_cols = ['lineup', 'plus_minus', 'offensive_rating', 'defensive_rating']
                            pretty = df[display_cols].rename(columns={
                                'lineup': 'Lineup',
                                'plus_minus': 'Plus/Minus',
                                'offensive_rating': 'Off Rating',
                                'defensive_rating': 'Def Rating'
                            }).copy()
                            pretty['Plus/Minus'] = pretty['Plus/Minus'].map(lambda v: f"{v:+.1f}")
                            pretty['Off Rating'] = pretty['Off Rating'].map(lambda v: f"{v:.1f}")
                            pretty['Def Rating'] = pretty['Def Rating'].map(lambda v: f"{v:.1f}")
                            st.dataframe(pretty, use_container_width=True, hide_index=True)

# Tab 2: Enhanced Situational Performance
with tab2:
    st.header('Situational Performance Analytics')
    
    if not team_names:
        st.warning('No teams available for analysis.')
    else:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            selected_team_sit = st.selectbox(
                'Select team:',
                team_names,
                key='situational_team_select'
            )
        with col2:
            last_n = st.number_input('Games to analyze:', min_value=5, max_value=50, value=20)
        with col3:
            load_btn = st.button('Load Analysis', type='primary', use_container_width=True)
        
        if load_btn and selected_team_sit:
            team_id = team_map.get(selected_team_sit)
            
            if not team_id:
                st.error('Unable to resolve team ID.')
            else:
                with st.spinner(f'Analyzing {selected_team_sit} performance...'):
                    sit_data = get_situational_performance(team_id, last_n)
                
                if not sit_data or not sit_data.get('situational'):
                    st.error(f'No situational data available for {selected_team_sit}.')
                else:
                    situational = sit_data['situational']
                    st.success(f"✅ Analyzed {sit_data.get('games_analyzed', 0)} games for {selected_team_sit}")
                    
                    # Create main metrics row
                    metrics_cols = st.columns(5)
                    
                    # Overall record from analyzed games
                    if situational.get('win_loss_margins'):
                        wins = situational['win_loss_margins']['wins']['count']
                        losses = situational['win_loss_margins']['losses']['count']
                        win_pct = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
                        
                        with metrics_cols[0]:
                            st.metric('Record', f"{wins}-{losses}")
                        with metrics_cols[1]:
                            st.metric('Win %', f"{win_pct:.1f}%")
                    
                    # Clutch performance
                    if situational.get('clutch'):
                        clutch = situational['clutch']
                        with metrics_cols[2]:
                            st.metric('Clutch Record', f"{clutch['wins']}-{clutch['losses']}")
                        with metrics_cols[3]:
                            st.metric('Clutch Win %', f"{clutch['win_pct']:.1f}%")
                        with metrics_cols[4]:
                            net = clutch['net_rating']
                            st.metric('Clutch Net', f"{net:+.1f}", 
                                    delta_color='normal' if net > 0 else 'inverse')
                    
                    # Create visualization sections
                    st.markdown("---")
                    
                    # Row 1: Home/Away Splits and Win/Loss Margins
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if situational.get('home_away_splits'):
                            st.subheader('🏠 Home vs Away Performance')
                            
                            home = situational['home_away_splits']['home']
                            away = situational['home_away_splits']['away']
                            
                            # Create comparison chart
                            fig = go.Figure()
                            
                            categories = ['Games', 'Wins', 'Avg Score', 'Avg Opp Score']
                            home_values = [
                                home['games'],
                                home['wins'],
                                home['avg_score'],
                                home['avg_opp_score']
                            ]
                            away_values = [
                                away['games'],
                                away['wins'],
                                away['avg_score'],
                                away['avg_opp_score']
                            ]
                            
                            fig.add_trace(go.Bar(
                                name='Home',
                                x=categories,
                                y=home_values,
                                marker_color='green',
                                text=[f"{v:.0f}" if i < 2 else f"{v:.1f}" 
                                      for i, v in enumerate(home_values)],
                                textposition='auto'
                            ))
                            
                            fig.add_trace(go.Bar(
                                name='Away',
                                x=categories,
                                y=away_values,
                                marker_color='blue',
                                text=[f"{v:.0f}" if i < 2 else f"{v:.1f}" 
                                      for i, v in enumerate(away_values)],
                                textposition='auto'
                            ))
                            
                            fig.update_layout(
                                barmode='group',
                                height=300,
                                showlegend=True,
                                margin=dict(l=0, r=0, t=30, b=0)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Home/Away insights
                            home_win_pct = (home['wins'] / home['games'] * 100) if home['games'] > 0 else 0
                            away_win_pct = (away['wins'] / away['games'] * 100) if away['games'] > 0 else 0
                            
                            if home_win_pct - away_win_pct > 15:
                                st.info("💡 Significantly better at home - consider home court strategies")
                            elif away_win_pct - home_win_pct > 15:
                                st.success("💪 Strong road team - mental toughness advantage")
                    
                    with col2:
                        if situational.get('win_loss_margins'):
                            st.subheader('📊 Victory & Defeat Margins')
                            
                            wins = situational['win_loss_margins']['wins']
                            losses = situational['win_loss_margins']['losses']
                            
                            # Create margin distribution chart
                            fig = make_subplots(
                                rows=1, cols=2,
                                subplot_titles=('Win Margins', 'Loss Margins'),
                                specs=[[{'type': 'indicator'}, {'type': 'indicator'}]]
                            )
                            
                            fig.add_trace(go.Indicator(
                                mode="number+gauge+delta",
                                value=wins['avg_margin'],
                                title={'text': "Avg Win By"},
                                delta={'reference': 10, 'position': "bottom"},
                                gauge={'axis': {'range': [0, 30]},
                                       'bar': {'color': "green"},
                                       'steps': [
                                           {'range': [0, 5], 'color': "lightgray"},
                                           {'range': [5, 15], 'color': "gray"}],
                                       'threshold': {'line': {'color': "red", 'width': 4},
                                                    'thickness': 0.75, 'value': 20}}
                            ), row=1, col=1)
                            
                            fig.add_trace(go.Indicator(
                                mode="number+gauge+delta",
                                value=losses['avg_margin'],
                                title={'text': "Avg Loss By"},
                                delta={'reference': 10, 'position': "bottom", 'increasing': {'color': "red"}},
                                gauge={'axis': {'range': [0, 30]},
                                       'bar': {'color': "red"},
                                       'steps': [
                                           {'range': [0, 5], 'color': "lightgray"},
                                           {'range': [5, 15], 'color': "gray"}],
                                       'threshold': {'line': {'color': "green", 'width': 4},
                                                    'thickness': 0.75, 'value': 5}}
                            ), row=1, col=2)
                            
                            fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Blowout analysis
                            blowout_col1, blowout_col2 = st.columns(2)
                            with blowout_col1:
                                st.metric("Blowout Wins (20+)", wins['blowout_wins'])
                            with blowout_col2:
                                st.metric("Blowout Losses (20+)", losses['blowout_losses'])
                    
                    st.markdown("---")
                    
                    # Row 2: Scoring Trends and Close Games
                    if situational.get('scoring_runs'):
                        st.subheader('📈 Recent Game Trends')
                        
                        # Convert to DataFrame for easier plotting
                        trends_df = pd.DataFrame(situational['scoring_runs'])
                        
                        if not trends_df.empty:
                            # Create dual-axis chart for scores and margins
                            fig = make_subplots(
                                rows=2, cols=1,
                                row_heights=[0.7, 0.3],
                                subplot_titles=('Team vs Opponent Scoring', 'Point Differential'),
                                vertical_spacing=0.15
                            )
                            
                            # Add team and opponent scores
                            fig.add_trace(
                                go.Scatter(
                                    x=trends_df.index,
                                    y=trends_df['team_score'],
                                    mode='lines+markers',
                                    name='Team Score',
                                    line=dict(color='green', width=2),
                                    marker=dict(size=8)
                                ),
                                row=1, col=1
                            )
                            
                            fig.add_trace(
                                go.Scatter(
                                    x=trends_df.index,
                                    y=trends_df['opp_score'],
                                    mode='lines+markers',
                                    name='Opponent Score',
                                    line=dict(color='red', width=2),
                                    marker=dict(size=8)
                                ),
                                row=1, col=1
                            )
                            
                            # Add margin bars
                            colors = ['green' if m > 0 else 'red' for m in trends_df['margin']]
                            fig.add_trace(
                                go.Bar(
                                    x=trends_df.index,
                                    y=trends_df['margin'],
                                    name='Margin',
                                    marker_color=colors,
                                    showlegend=False
                                ),
                                row=2, col=1
                            )
                            
                            # Add average lines
                            avg_team = trends_df['team_score'].mean()
                            avg_opp = trends_df['opp_score'].mean()
                            
                            fig.add_hline(y=avg_team, line_dash="dash", line_color="green", 
                                         opacity=0.5, row=1, col=1)
                            fig.add_hline(y=avg_opp, line_dash="dash", line_color="red", 
                                         opacity=0.5, row=1, col=1)
                            fig.add_hline(y=0, line_color="black", opacity=0.3, row=2, col=1)
                            
                            fig.update_xaxes(title_text="Last N Games", row=2, col=1)
                            fig.update_yaxes(title_text="Points", row=1, col=1)
                            fig.update_yaxes(title_text="Differential", row=2, col=1)
                            
                            fig.update_layout(height=400, showlegend=True)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Trend insights
                            recent_form = trends_df.tail(5)['margin'].mean()
                            overall_form = trends_df['margin'].mean()
                            
                            if recent_form > overall_form + 5:
                                st.success("📈 Team trending upward - recent form better than average")
                            elif recent_form < overall_form - 5:
                                st.warning("📉 Team trending downward - recent struggles detected")
                    
                    # Close Games Detail
                    if situational.get('close_games') and len(situational['close_games']) > 0:
                        st.markdown("---")
                        st.subheader('🎯 Close Games Analysis (≤5 point games)')
                        
                        close_df = pd.DataFrame(situational['close_games'])
                        
                        # Create a more detailed view
                        close_df['game_date'] = pd.to_datetime(close_df['game_date'])
                        close_df = close_df.sort_values('game_date', ascending=False)
                        
                        # Styling for the dataframe
                        def style_result(row):
                            if row['result'] == 'W':
                                return ['background-color: #90EE90'] * len(row)
                            else:
                                return ['background-color: #FFB6C1'] * len(row)
                        
                        styled_df = close_df[['game_date', 'team_score', 'opp_score', 'margin', 'result']]
                        styled_df['game_date'] = styled_df['game_date'].dt.strftime('%Y-%m-%d')
                        
                        st.dataframe(
                            styled_df.style.apply(style_result, axis=1),
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    # Clutch Performers
                    if situational.get('clutch_performers'):
                        st.markdown("---")
                        st.subheader('⭐ Top Clutch Performers')
                        
                        clutch_df = pd.DataFrame(situational['clutch_performers'])
                        
                        # Create player cards
                        cols = st.columns(min(5, len(clutch_df)))
                        for idx, (_, player) in enumerate(clutch_df.iterrows()):
                            with cols[idx % len(cols)]:
                                st.markdown(f"""
                                <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center;">
                                    <h4>{player['first_name']} {player['last_name']}</h4>
                                    <p><b>{player['position']}</b></p>
                                    <p>{player['avg_points']:.1f} PPG</p>
                                    <p>{player['avg_plus_minus']:+.1f} +/-</p>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Advanced Recommendations
                    st.markdown("---")
                    st.subheader('🎯 Strategic Recommendations')
                    
                    recommendations = []
                    priority_levels = []
                    
                    # Analyze patterns for recommendations
                    if situational.get('clutch'):
                        clutch = situational['clutch']
                        if clutch['win_pct'] < 40:
                            recommendations.append("Practice late-game scenarios with pressure situations")
                            priority_levels.append("🔴 Critical")
                        elif clutch['win_pct'] < 50:
                            recommendations.append("Review clutch-time play calling and timeout usage")
                            priority_levels.append("⚠️ Important")
                        else:
                            recommendations.append("Maintain current clutch execution strategies")
                            priority_levels.append("✅ Good")
                    
                    if situational.get('home_away_splits'):
                        home = situational['home_away_splits']['home']
                        away = situational['home_away_splits']['away']
                        
                        home_net = home['avg_score'] - home['avg_opp_score']
                        away_net = away['avg_score'] - away['avg_opp_score']
                        
                        if away_net < home_net - 10:
                            recommendations.append("Focus on road game preparation and travel routine")
                            priority_levels.append("⚠️ Important")
                        
                        if home['avg_score'] < 100:
                            recommendations.append("Improve home court energy and offensive execution")
                            priority_levels.append("⚠️ Important")
                    
                    if situational.get('win_loss_margins'):
                        losses = situational['win_loss_margins']['losses']
                        if losses['blowout_losses'] >= 3:
                            recommendations.append("Address mental resilience in adversity situations")
                            priority_levels.append("🔴 Critical")
                        
                        if losses['avg_margin'] > 15:
                            recommendations.append("Implement comeback strategies and momentum shifts")
                            priority_levels.append("⚠️ Important")
                    
                    if situational.get('scoring_runs'):
                        trends_df = pd.DataFrame(situational['scoring_runs'])
                        if not trends_df.empty:
                            avg_score = trends_df['team_score'].mean()
                            if avg_score < 100:
                                recommendations.append("Increase pace and offensive efficiency")
                                priority_levels.append("⚠️ Important")
                            
                            recent_avg = trends_df.tail(3)['team_score'].mean()
                            if recent_avg < avg_score - 10:
                                recommendations.append("Address recent offensive struggles")
                                priority_levels.append("🔴 Critical")
                    
                    # Display recommendations with priority
                    if recommendations:
                        for priority, rec in zip(priority_levels, recommendations):
                            if "Critical" in priority:
                                st.error(f"{priority}: {rec}")
                            elif "Important" in priority:
                                st.warning(f"{priority}: {rec}")
                            else:
                                st.success(f"{priority}: {rec}")
                    else:
                        st.info("Mixed results across situational metrics — see charts above for details.")
                    
                    # Removed Export Report per request