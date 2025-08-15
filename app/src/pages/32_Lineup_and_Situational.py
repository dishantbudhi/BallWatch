import os
import logging
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks
import plotly.express as px
from modules import api_client
import traceback

logger = logging.getLogger(__name__)

api_client.ensure_api_base()


def call_get_raw(endpoint: str, params: dict | None = None, timeout=5):
    """Enhanced API call with better error handling."""
    try:
        return api_client.api_get(endpoint, params=params, timeout=timeout)
    except Exception as e:
        logger.error(f"API call failed for {endpoint}: {e}")
        st.error(f"API call failed: {e}")
        return None


def call_post_raw(endpoint: str, data: dict | None = None, timeout=5):
    """Enhanced POST call with error handling."""
    try:
        return api_client.api_post(endpoint, data=data, timeout=timeout)
    except Exception as e:
        logger.error(f"POST call failed for {endpoint}: {e}")
        st.error(f"POST call failed: {e}")
        return None


def get_teams(timeout=5):
    """Get teams with improved error handling and data validation."""
    try:
        data = api_client.api_get('/basketball/teams', timeout=timeout)
        if isinstance(data, dict) and 'teams' in data:
            teams = data.get('teams', []) or []
        elif isinstance(data, list):
            teams = data or []
        else:
            logger.warning(f"Unexpected teams data format: {type(data)}")
            return []

        # Deduplicate by team_id and validate data
        seen = set()
        unique = []
        for t in teams:
            if not isinstance(t, dict):
                logger.warning(f"Invalid team data: {t}")
                continue
                
            tid = t.get('team_id') or t.get('id')
            name = t.get('name')
            
            if tid is None or not name:
                logger.warning(f"Team missing required fields: {t}")
                continue
                
            try:
                key = int(tid)
            except Exception:
                key = str(tid)
                
            if key in seen:
                continue
                
            seen.add(key)
            unique.append(t)
            
        logger.info(f"Successfully loaded {len(unique)} teams")
        return unique
        
    except Exception as e:
        logger.error(f"Failed to get teams: {e}")
        st.error(f"Failed to load teams: {e}")
        return []


def get_lineup_configurations(endpoint_or_query: str):
    """Enhanced lineup configurations with better error handling."""
    try:
        path, params = api_client._parse_endpoint_with_query(endpoint_or_query)
    except Exception:
        # fallback implementation
        import urllib.parse
        parsed = urllib.parse.urlparse(endpoint_or_query)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        params = {k: v[0] for k, v in qs.items()}
    
    try:
        result = call_get_raw(path or '/analytics/lineup-configurations', params)
        logger.info(f"Lineup configurations result: {type(result)}")
        return result
    except Exception as e:
        logger.error(f"Failed to get lineup configurations: {e}")
        st.error(f"Failed to load lineup data: {e}")
        return None


def get_situational_performance(endpoint_or_query: str):
    """Enhanced situational performance with better error handling."""
    try:
        path, params = api_client._parse_endpoint_with_query(endpoint_or_query)
    except Exception:
        import urllib.parse
        parsed = urllib.parse.urlparse(endpoint_or_query)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        params = {k: v[0] for k, v in qs.items()}
    
    try:
        result = call_get_raw(path or '/analytics/situational-performance', params)
        logger.info(f"Situational performance result: {type(result)}")
        return result
    except Exception as e:
        logger.error(f"Failed to get situational performance: {e}")
        st.error(f"Failed to load situational data: {e}")
        return None


st.set_page_config(page_title='Lineup & Situational - Head Coach', layout='wide')
SideBarLinks()
st.title('Lineup & Situational Analysis — Head Coach')
st.caption('Analyze lineup effectiveness and situational performance.')


def make_request(endpoint, method='GET', data=None):
    """Enhanced request handler with comprehensive error handling."""
    try:
        if endpoint.startswith('/basketball/teams') and method == 'GET':
            teams = get_teams() or []
            return {'teams': teams}
        if endpoint.startswith('/analytics/lineup-configurations'):
            return get_lineup_configurations(endpoint) or {}
        if endpoint.startswith('/analytics/situational-performance'):
            return get_situational_performance(endpoint) or {}
        return {}
    except Exception as e:
        logger.error(f"Request failed for {endpoint}: {e}")
        st.error(f"Request failed: {e}")
        return {}


# Enhanced error handling for teams data loading
try:
    teams_response = make_request('/basketball/teams')
    if not teams_response or 'teams' not in teams_response:
        st.error("❌ Unable to load teams data. Please check your API connection.")
        st.info("💡 **Troubleshooting Steps:**")
        st.info("1. Verify the Flask API is running on port 4000")
        st.info("2. Check database connection")
        st.info("3. Ensure /basketball/teams endpoint is accessible")
        st.stop()
        
    teams = teams_response.get('teams', [])
    if not teams:
        st.warning("⚠️ No teams found in the database.")
        st.stop()
        
except Exception as e:
    st.error(f"❌ Critical error loading teams: {e}")
    with st.expander("🔍 Debug Information"):
        st.text(f"Exception: {type(e).__name__}")
        st.text(f"Message: {str(e)}")
        st.text(traceback.format_exc())
    st.stop()

# Tabs for Lineup Analysis and Situational Performance
tab1, tab2 = st.tabs(['Lineup Analysis', 'Situational Performance'])

with tab1:
    st.header('Lineup Analysis')
    
    # Enhanced team selection with validation
    if not teams:
        st.error("No teams available for analysis.")
    else:
        try:
            team_names = [t.get('name') for t in teams if t.get('name')]
            team_id_map = {t.get('name'): t.get('team_id') or t.get('id') for t in teams if t.get('name')}
            
            if not team_names:
                st.error("No valid team names found.")
            else:
                # Get user's team context if available
                user_team = st.session_state.get('team_name')
                default_idx = 0
                if user_team in team_names:
                    default_idx = team_names.index(user_team)
                
                selected_team = st.selectbox('Select a team to analyze lineups:', 
                                           team_names, 
                                           index=default_idx)
                
                if st.button('Get Lineup Analysis', key='lineup_analysis'):
                    team_id = team_id_map.get(selected_team)
                    
                    if team_id is None:
                        st.error('❌ Selected team ID not found. Please try another team.')
                        with st.expander('🔍 Debug: Available Teams'):
                            st.json({name: tid for name, tid in team_id_map.items()})
                    else:
                        try:
                            team_id = int(team_id)
                        except Exception:
                            pass
                            
                        with st.spinner('Loading lineup analysis...'):
                            data = make_request(f'/analytics/lineup-configurations?team_id={team_id}')
                            
                        if not data:
                            st.error('❌ No response from lineup configurations endpoint.')
                            with st.expander('🔍 Troubleshooting'):
                                st.info(f"Endpoint: /analytics/lineup-configurations?team_id={team_id}")
                                st.info("Check server logs for detailed error information")
                                # Attempt to fetch raw response for debugging
                                try:
                                    import requests as _req
                                    base = api_client.ensure_api_base()
                                    raw = _req.get(f"{base}/analytics/lineup-configurations", params={'team_id': team_id}, timeout=5)
                                    st.info(f"Raw HTTP status: {raw.status_code}")
                                    with st.expander('Raw server response'):
                                        try:
                                            st.text(raw.text)
                                            st.json(raw.json())
                                        except Exception:
                                            st.text(raw.text)
                                except Exception as e:
                                    st.warning(f'Could not fetch raw response: {e}')
                            
                        elif 'lineup_effectiveness' not in data:
                            st.error('❌ Invalid response format from lineup endpoint.')
                            with st.expander('🔍 Raw API Response'):
                                st.json(data)
                                
                        else:
                            lineup_data = data['lineup_effectiveness']
                            
                            if not lineup_data:
                                st.warning(f'⚠️ No lineup data available for {selected_team}.')
                                st.info('💡 This might mean:')
                                st.info('• Team has no recorded lineup configurations')
                                st.info('• Database tables need to be populated')
                                st.info('• Lineup tracking is not enabled for this team')
                                
                            else:
                                try:
                                    df = pd.DataFrame(lineup_data)
                                    st.success(f'✅ Found {len(df)} lineup configurations for {selected_team}')
                                    
                                    # Enhanced data validation and handling
                                    if df.empty:
                                        st.error('Lineup data returned empty after processing.')
                                    else:
                                        # Handle plus_minus column with comprehensive validation
                                        if 'plus_minus' in df.columns:
                                            df['plus_minus'] = pd.to_numeric(df['plus_minus'], errors='coerce')
                                            
                                            # Check for all NaN values
                                            if df['plus_minus'].isna().all():
                                                st.warning('⚠️ No plus/minus values available. Creating placeholder data for visualization.')
                                                df['plus_minus'] = 0
                                            else:
                                                # Fill NaN values with 0 for incomplete data
                                                df['plus_minus'].fillna(0, inplace=True)
                                        else:
                                            st.info('ℹ️ Plus/minus data not available. Using placeholder values.')
                                            df['plus_minus'] = 0

                                        # Enhanced lineup labeling
                                        if 'lineup' not in df.columns:
                                            df['lineup'] = df.index.map(lambda x: f'Lineup {x+1}')
                                        
                                        # Sort data for better visualization
                                        df_sorted = df.sort_values(by='plus_minus', ascending=False)

                                        # Enhanced visualization
                                        fig = px.bar(
                                            df_sorted, 
                                            x='plus_minus', 
                                            y='lineup', 
                                            orientation='h', 
                                            color='plus_minus',
                                            color_continuous_scale='RdBu',
                                            title=f'Lineup Effectiveness for {selected_team}',
                                            labels={'plus_minus': 'Plus/Minus', 'lineup': 'Lineup'}
                                        )
                                        fig.update_layout(height=max(400, len(df) * 40))
                                        st.plotly_chart(fig, use_container_width=True)

                                        # Enhanced recommendations
                                        try:
                                            top3 = df_sorted.head(3)
                                            st.subheader('🎯 Top Rotation Suggestions')
                                            
                                            for idx, row in top3.iterrows():
                                                plus_minus = row['plus_minus']
                                                lineup_name = row['lineup']
                                                
                                                if plus_minus >= 5:
                                                    st.success(f"🔥 Elite: {lineup_name} (+{plus_minus:.1f}) - Keep as primary rotation")
                                                elif plus_minus >= 2:
                                                    st.info(f"👍 Good: {lineup_name} (+{plus_minus:.1f}) - Consider for key moments")
                                                elif plus_minus > 0:
                                                    st.warning(f"⚠️ Average: {lineup_name} (+{plus_minus:.1f}) - Monitor performance")
                                                else:
                                                    st.error(f"📉 Needs work: {lineup_name} ({plus_minus:.1f}) - Review strategy")

                                            # Strategic insights
                                            st.markdown('''
                                                <div style="padding:15px;border-radius:10px;border:1px solid #ddd;background:#f8f9fa;margin-top:20px">
                                                <h4>📋 Strategic Insights</h4>
                                                <ul>
                                                <li><strong>Best Lineup:</strong> Focus starting lineup minutes during crucial 4th quarter moments</li>
                                                <li><strong>Rotations:</strong> Use top 3 lineups for 80% of playing time</li>
                                                <li><strong>Development:</strong> Work with negative plus/minus lineups in practice scenarios</li>
                                                </ul>
                                                </div>
                                            ''', unsafe_allow_html=True)
                                            
                                        except Exception as e:
                                            st.error(f"Error generating recommendations: {e}")

                                        # Enhanced data table
                                        with st.expander('📊 Detailed Lineup Data'):
                                            # Add additional metrics if available
                                            display_df = df_sorted.copy()
                                            if 'offensive_rating' in display_df.columns:
                                                display_df['offensive_rating'] = pd.to_numeric(display_df['offensive_rating'], errors='coerce')
                                            if 'defensive_rating' in display_df.columns:
                                                display_df['defensive_rating'] = pd.to_numeric(display_df['defensive_rating'], errors='coerce')
                                                
                                            st.dataframe(display_df, use_container_width=True)
                                            
                                except Exception as e:
                                    st.error(f"❌ Error processing lineup data: {e}")
                                    with st.expander('🔍 Debug Information'):
                                        st.text(f"Exception: {type(e).__name__}")
                                        st.text(f"Message: {str(e)}")
                                        st.text("Raw data:")
                                        st.json(lineup_data)
                        
        except Exception as e:
            st.error(f"❌ Error in lineup analysis: {e}")
            with st.expander('🔍 Debug Information'):
                st.text(traceback.format_exc())

with tab2:
    st.header('Situational Performance')
    
    if not teams:
        st.error("No teams available for situational analysis.")
    else:
        try:
            team_names = [t.get('name') for t in teams if t.get('name')]
            team_id_map = {t.get('name'): t.get('team_id') or t.get('id') for t in teams if t.get('name')}
            
            # Get user's team context if available
            user_team = st.session_state.get('team_name')
            default_idx = 0
            if user_team in team_names:
                default_idx = team_names.index(user_team)
            
            selected_team = st.selectbox('Select team:', 
                                       team_names, 
                                       key='situ_team',
                                       index=default_idx)
            
            team_id = team_id_map.get(selected_team)

            if st.button('Load Situational Data', key='situational_analysis'):
                if team_id is None:
                    st.error('❌ Selected team ID not found.')
                    with st.expander('🔍 Debug: Available Teams'):
                        st.json({name: tid for name, tid in team_id_map.items()})
                else:
                    try:
                        team_id = int(team_id)
                    except Exception:
                        pass
                    
                    with st.spinner('Loading situational performance data...'):
                        data = make_request(f'/analytics/situational-performance?team_id={team_id}')
                    
                    if not data:
                        st.error('❌ No response from situational performance endpoint.')
                        with st.expander('🔍 Troubleshooting'):
                            st.info(f"Endpoint: /analytics/situational-performance?team_id={team_id}")
                            st.info("Check server logs for detailed error information")
                            
                    elif 'situational' not in data:
                        st.error('❌ Invalid response format from situational endpoint.')
                        with st.expander('🔍 Raw API Response'):
                            st.json(data)
                            
                    else:
                        situ = data.get('situational') or {}

                        # If situational payload is empty, surface clear message and skip analysis
                        if not situ or (isinstance(situ, dict) and not any(v for v in situ.values())):
                            st.warning(f'ℹ️ Situational performance data not available for {selected_team}.')
                            # Keep the per-section info messages for clarity
                            st.info('ℹ️ Clutch performance data not available.')
                            st.info('ℹ️ Quarter-by-quarter data not available.')
                            st.info('ℹ️ Close games data not available.')
                        else:
                            # Enhanced clutch performance display
                            if situ.get('clutch'):
                                st.subheader('🔥 Clutch Performance')
                                clutch_data = situ['clutch']

                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric('Offensive Rating', f"{clutch_data.get('off_rating', 0):.1f}")
                                with col2:
                                    st.metric('Defensive Rating', f"{clutch_data.get('def_rating', 0):.1f}")
                                with col3:
                                    st.metric('Net Rating', f"{clutch_data.get('net_rating', 0):.1f}")
                                with col4:
                                    st.metric('Clutch Games', clutch_data.get('games', 0))

                                # Clutch performance interpretation
                                net_rating = clutch_data.get('net_rating', 0)
                                if net_rating > 5:
                                    st.success(f"🔥 Elite clutch performance! {selected_team} excels in pressure situations.")
                                elif net_rating > 0:
                                    st.info(f"👍 Good clutch performance. {selected_team} handles pressure well.")
                                elif net_rating > -5:
                                    st.warning(f"⚠️ Average clutch performance. Room for improvement in pressure situations.")
                                else:
                                    st.error(f"📉 Poor clutch performance. {selected_team} struggles in pressure situations.")
                            else:
                                st.info('ℹ️ Clutch performance data not available.')

                            # Enhanced quarter-by-quarter analysis
                            if situ.get('by_quarter'):
                                st.subheader('📊 Quarter-by-Quarter Performance')
                                try:
                                    dfq = pd.DataFrame(situ['by_quarter'])
                                    dfq['quarter'] = dfq['quarter'].astype(str)

                                    fig = px.bar(
                                        dfq,
                                        x='quarter',
                                        y=['avg_points_for', 'avg_points_against'],
                                        barmode='group',
                                        title=f'Average Points by Quarter - {selected_team}',
                                        labels={
                                            'quarter': 'Quarter',
                                            'value': 'Points',
                                            'variable': 'Metric'
                                        }
                                    )
                                    fig.update_layout(height=400)
                                    st.plotly_chart(fig, use_container_width=True)

                                    # Quarter analysis
                                    dfq['point_differential'] = dfq['avg_points_for'] - dfq['avg_points_against']
                                    best_quarter = dfq.loc[dfq['point_differential'].idxmax(), 'quarter']
                                    worst_quarter = dfq.loc[dfq['point_differential'].idxmin(), 'quarter']

                                    st.info(f"🏆 Strongest Quarter: Q{best_quarter}")
                                    st.warning(f"⚠️ Weakest Quarter: Q{worst_quarter}")

                                except Exception as e:
                                    st.error(f"Error processing quarter data: {e}")
                                    st.json(situ['by_quarter'])
                            else:
                                st.info('ℹ️ Quarter-by-quarter data not available.')

                            # Enhanced close games analysis
                            if situ.get('close_games'):
                                st.subheader('⚡ Close Games Performance')
                                try:
                                    close_df = pd.DataFrame(situ['close_games'])
                                    if not close_df.empty:
                                        # Calculate win percentage in close games
                                        close_df['won'] = close_df['team_score'] > close_df['opp_score']
                                        close_wins = close_df['won'].sum()
                                        total_close = len(close_df)
                                        win_pct = (close_wins / total_close) * 100 if total_close > 0 else 0

                                        st.metric(f'Close Games Record', f'{close_wins}-{total_close - close_wins} ({win_pct:.1f}%)')

                                        # Show recent close games
                                        display_df = close_df[['game_date', 'team_score', 'opp_score', 'won']].copy()
                                        display_df['result'] = display_df['won'].map({True: 'W', False: 'L'})
                                        display_df = display_df.drop('won', axis=1)
                                        st.dataframe(display_df, use_container_width=True)
                                    else:
                                        st.info('No close games found in recent history.')
                                except Exception as e:
                                    st.error(f"Error processing close games: {e}")
                            else:
                                st.info('ℹ️ Close games data not available.')

                            # Enhanced practice recommendations
                            st.subheader('🏀 Practice Focus Recommendations')
                            recommendations = []

                            # Clutch recommendations
                            if situ.get('clutch'):
                                net_rating = situ['clutch'].get('net_rating', 0)
                                if net_rating < 0:
                                    recommendations.append('🎯 **Clutch Scenarios:** Practice late-game execution, ball security, and pressure free throws.')

                            # Quarter recommendations
                            if situ.get('by_quarter'):
                                try:
                                    dfq = pd.DataFrame(situ['by_quarter'])
                                    dfq['differential'] = dfq['avg_points_for'] - dfq['avg_points_against']
                                    worst_q = dfq.loc[dfq['differential'].idxmin(), 'quarter']
                                    recommendations.append(f'📈 **Q{worst_q} Focus:** Improve offensive efficiency and defensive stops in quarter {worst_q}.')
                                except Exception:
                                    pass

                            # Close games recommendations
                            if situ.get('close_games'):
                                try:
                                    close_df = pd.DataFrame(situ['close_games'])
                                    if not close_df.empty:
                                        win_rate = (close_df['team_score'] > close_df['opp_score']).mean()
                                        if win_rate < 0.5:
                                            recommendations.append('⚡ **Close Games:** Work on maintaining composure and executing plays under pressure.')
                                except Exception:
                                    pass

                            # Display recommendations
                            if recommendations:
                                for rec in recommendations:
                                    st.info(rec)
                            else:
                                # Only show success when situational data existed but no recommendations were needed
                                st.success(f'🎉 {selected_team} shows strong situational performance across all metrics!')
        except Exception as e:
            st.error(f"❌ Error in situational analysis: {e}")
            with st.expander('🔍 Debug Information'):
                st.text(traceback.format_exc())