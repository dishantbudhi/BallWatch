import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# Page configuration]
st.set_page_config(
    page_title="Player Progression",
    page_icon="📈",
    layout="wide"
)

# Title and header
st.title("📈 Player Progression Tracking")
st.markdown("### Monitor player development, performance trends, and growth potential")

# API Base URL (adjust this to match your Flask backend)
API_BASE_URL = "http://localhost:5000"

# Function to fetch draft evaluations from API
def fetch_draft_evaluations(position=None, min_age=None, max_age=None):
    try:
        params = {}
        if position:
            params['position'] = position
        if min_age:
            params['min_age'] = min_age
        if max_age:
            params['max_age'] = max_age
        # Only get prospects and current players, not free agents
        params['evaluation_type'] = 'prospect'
        
        response = requests.get(f"{API_BASE_URL}/strategy/draft-evaluations", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

# Function to fetch team players
def fetch_team_players(team_id):
    try:
        response = requests.get(f"{API_BASE_URL}/teams/{team_id}/players", 
                               params={'include_stats': 'true'})
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

# NBA Teams mapping (team_id: team_name)
NBA_TEAMS = {
    1: "Boston Celtics",
    2: "Brooklyn Nets", 
    3: "New York Knicks",
    4: "Philadelphia 76ers",
    5: "Toronto Raptors",
    6: "Chicago Bulls",
    7: "Cleveland Cavaliers",
    8: "Detroit Pistons",
    9: "Indiana Pacers",
    10: "Milwaukee Bucks",
    11: "Atlanta Hawks",
    12: "Charlotte Hornets",
    13: "Miami Heat",
    14: "Orlando Magic",
    15: "Washington Wizards",
    16: "Denver Nuggets",
    17: "Minnesota Timberwolves",
    18: "Oklahoma City Thunder",
    19: "Portland Trail Blazers",
    20: "Utah Jazz",
    21: "Golden State Warriors",
    22: "Los Angeles Clippers",
    23: "Los Angeles Lakers",
    24: "Phoenix Suns",
    25: "Sacramento Kings",
    26: "Dallas Mavericks",
    27: "Houston Rockets",
    28: "Memphis Grizzlies",
    29: "New Orleans Pelicans",
    30: "San Antonio Spurs"
}

# Sidebar filters
st.sidebar.header("🔍 Filter Options")

# Team selection
selected_team_name = st.sidebar.selectbox(
    "Select Team",
    list(NBA_TEAMS.values())
)

# Get team_id from selected team name
team_id = [k for k, v in NBA_TEAMS.items() if v == selected_team_name][0]

# Fetch team roster
team_players_data = fetch_team_players(team_id)

# Player selection from team roster
if team_players_data and team_players_data.get('players'):
    team_roster = team_players_data['players']
    player_options = ["All Players"] + [
        f"{p.get('first_name', '')} {p.get('last_name', '')} ({p.get('position', '')})" 
        for p in team_roster
    ]
    
    selected_player_filter = st.sidebar.selectbox(
        "Select Player",
        player_options
    )
else:
    selected_player_filter = "All Players"
    st.sidebar.info("No players found for selected team")

position_filter = st.sidebar.selectbox(
    "Position",
    ["All", "PG", "SG", "SF", "PF", "C"]
)
position_filter = None if position_filter == "All" else position_filter

age_range = st.sidebar.slider(
    "Age Range",
    min_value=18,
    max_value=40,
    value=(19, 30)
)

progress_period = st.sidebar.selectbox(
    "Progress Period",
    ["Last Month", "Last 3 Months", "Last 6 Months", "Season"]
)

# Fetch data
eval_data = fetch_draft_evaluations(
    position=position_filter,
    min_age=age_range[0],
    max_age=age_range[1]
)

# If a specific player is selected, filter the data
if selected_player_filter != "All Players" and eval_data and eval_data.get('evaluations'):
    evaluations_temp = pd.DataFrame(eval_data['evaluations'])
    
    # Extract the selected player's name
    player_name_parts = selected_player_filter.split(" (")[0].split(" ")
    first_name = player_name_parts[0] if len(player_name_parts) > 0 else ""
    last_name = player_name_parts[1] if len(player_name_parts) > 1 else ""
    
    # Filter for the selected player
    evaluations_temp = evaluations_temp[
        (evaluations_temp['first_name'] == first_name) & 
        (evaluations_temp['last_name'] == last_name)
    ]
    
    if not evaluations_temp.empty:
        eval_data['evaluations'] = evaluations_temp.to_dict('records')
    else:
        # If no evaluation data, try to use team roster data
        if team_players_data and team_players_data.get('players'):
            for player in team_players_data['players']:
                if f"{player.get('first_name', '')} {player.get('last_name', '')}" == f"{first_name} {last_name}":
                    # Create evaluation data from roster data
                    eval_data = {
                        'evaluations': [{
                            'first_name': player.get('first_name', ''),
                            'last_name': player.get('last_name', ''),
                            'position': player.get('position', ''),
                            'age': player.get('age', 0),
                            'overall_rating': 75,  # Default rating
                            'potential_rating': 85,  # Default potential
                            'offensive_rating': 70,
                            'defensive_rating': 70,
                            'athleticism_rating': 75,
                            'current_team': selected_team_name,
                            'avg_points': player.get('avg_points', 0),
                            'avg_rebounds': player.get('avg_rebounds', 0),
                            'avg_assists': player.get('avg_assists', 0),
                            'games_played': player.get('games_played', 0),
                            'years': player.get('years_exp', 0)
                        }]
                    }
                    break

if eval_data and eval_data.get('evaluations'):
    evaluations = pd.DataFrame(eval_data['evaluations'])
    
    # Simulate progression data (in real app, this would come from historical data)
    evaluations['progress_score'] = evaluations['potential_rating'] - evaluations['overall_rating']
    evaluations['improvement_rate'] = pd.Series([2.3, -0.5, 1.8, 3.2, 0.9, 1.5, 2.8, -1.2] * (len(evaluations)//8 + 1))[:len(evaluations)]
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_players = len(evaluations)
        st.metric(
            label="📊 Players Tracked",
            value=total_players,
            delta=f"From {selected_team_name}"
        )
    
    with col2:
        improving = len(evaluations[evaluations['improvement_rate'] > 0]) if 'improvement_rate' in evaluations else 0
        st.metric(
            label="📈 Improving Players",
            value=improving,
            delta=f"{(improving/total_players*100):.0f}% of roster"
        )
    
    with col3:
        high_potential = len(evaluations[evaluations['potential_rating'] >= 85]) if 'potential_rating' in evaluations else 0
        st.metric(
            label="🌟 Elite Potential",
            value=high_potential,
            delta="85+ potential rating"
        )
    
    with col4:
        avg_progress = evaluations['progress_score'].mean() if 'progress_score' in evaluations else 0
        st.metric(
            label="🎯 Avg Growth Room",
            value=f"{avg_progress:.1f} pts",
            delta="Potential - Current"
        )
    
    st.markdown("---")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Progress Overview", 
        "📈 Individual Tracking", 
        "🎯 Development Plans",
        "📉 Performance Trends",
        "🏆 Milestone Tracking"
    ])
    
    with tab1:
        st.subheader("📊 Player Progress Overview")
        
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            # Progress Matrix
            fig_progress = px.scatter(
                evaluations,
                x='overall_rating',
                y='potential_rating',
                size='age',
                color='improvement_rate',
                hover_data=['first_name', 'last_name', 'position'],
                labels={
                    'overall_rating': 'Current Rating',
                    'potential_rating': 'Potential Rating',
                    'improvement_rate': 'Improvement Rate'
                },
                title="Player Development Matrix",
                color_continuous_scale='RdYlGn',
                color_continuous_midpoint=0
            )
            
            # Add diagonal line for reference
            fig_progress.add_trace(
                go.Scatter(x=[50, 100], y=[50, 100], 
                          mode='lines', 
                          line=dict(dash='dash', color='gray'),
                          showlegend=False)
            )
            
            fig_progress.update_layout(height=400)
            st.plotly_chart(fig_progress, use_container_width=True)
        
        with col2:
            # Improvement Distribution
            fig_improvement = px.histogram(
                evaluations,
                y='improvement_rate',
                nbins=20,
                orientation='h',
                title="Improvement Rate Distribution",
                labels={'improvement_rate': 'Monthly Improvement', 'count': 'Players'}
            )
            fig_improvement.update_layout(height=400)
            st.plotly_chart(fig_improvement, use_container_width=True)
        
        # Progress by Position
        position_progress = evaluations.groupby('position').agg({
            'improvement_rate': 'mean',
            'progress_score': 'mean',
            'overall_rating': 'mean'
        }).round(1)
        
        fig_position = px.bar(
            position_progress,
            x=position_progress.index,
            y='improvement_rate',
            title="Average Improvement Rate by Position",
            labels={'improvement_rate': 'Avg Monthly Improvement', 'position': 'Position'}
        )
        st.plotly_chart(fig_position, use_container_width=True)
    
    with tab2:
        st.subheader("📈 Individual Player Tracking")
        
        # Player selector - prioritize filtered player if one was selected
        if selected_player_filter != "All Players" and len(evaluations) > 0:
            player_names = evaluations.apply(lambda x: f"{x.get('first_name', '')} {x.get('last_name', '')} ({x.get('position', '')})", axis=1)
            # Set the default to the filtered player
            default_index = 0
            selected_player = st.selectbox("Selected Player", player_names, index=default_index)
        else:
            # Show all players from the team
            player_names = evaluations.apply(lambda x: f"{x.get('first_name', '')} {x.get('last_name', '')} ({x.get('position', '')})", axis=1)
            selected_player = st.selectbox("Select Player from " + selected_team_name, player_names)
        
        if selected_player:
            player_idx = player_names[player_names == selected_player].index[0]
            player_data = evaluations.iloc[player_idx]
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                # Player Info Card
                st.info(f"""
                **Player Profile**
                - **Name:** {player_data.get('first_name', '')} {player_data.get('last_name', '')}
                - **Position:** {player_data.get('position', 'N/A')}
                - **Age:** {player_data.get('age', 'N/A')}
                - **Team:** {player_data.get('current_team', 'N/A')}
                - **Years Pro:** {player_data.get('years', 0)}
                """)
                
                # Progress Metrics
                st.success(f"""
                **Progress Metrics**
                - **Current Rating:** {player_data.get('overall_rating', 0):.1f}
                - **Potential Rating:** {player_data.get('potential_rating', 0):.1f}
                - **Growth Room:** {player_data.get('progress_score', 0):.1f} pts
                - **Monthly Improvement:** {player_data.get('improvement_rate', 0):+.1f}%
                """)
            
            with col2:
                # Rating Breakdown
                categories = ['Overall', 'Offense', 'Defense', 'Athleticism', 'Potential']
                current_values = [
                    player_data.get('overall_rating', 0),
                    player_data.get('offensive_rating', 0),
                    player_data.get('defensive_rating', 0),
                    player_data.get('athleticism_rating', 0),
                    player_data.get('potential_rating', 0)
                ]
                
                # Simulate previous values
                previous_values = [max(0, v - player_data.get('improvement_rate', 0)) for v in current_values]
                
                fig_radar = go.Figure()
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=current_values,
                    theta=categories,
                    fill='toself',
                    name='Current',
                    line=dict(color='green')
                ))
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=previous_values,
                    theta=categories,
                    fill='toself',
                    name='Previous',
                    line=dict(color='gray', dash='dash')
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100])
                    ),
                    showlegend=True,
                    title="Skill Development"
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            
            with col3:
                # Performance Stats
                st.warning(f"""
                **Performance Stats**
                - **PPG:** {player_data.get('avg_points', 0):.1f}
                - **RPG:** {player_data.get('avg_rebounds', 0):.1f}
                - **APG:** {player_data.get('avg_assists', 0):.1f}
                - **Games Played:** {player_data.get('games_played', 0)}
                """)
                
                # Strengths and Weaknesses
                if player_data.get('strengths'):
                    st.write("**Strengths:**", player_data.get('strengths', 'N/A'))
                if player_data.get('weaknesses'):
                    st.write("**Weaknesses:**", player_data.get('weaknesses', 'N/A'))
    
    with tab3:
        st.subheader("🎯 Development Plans")
        
        # Development priority matrix
        evaluations['development_priority'] = (
            evaluations['progress_score'] * 0.5 + 
            evaluations['age'].apply(lambda x: max(0, 30-x)) * 0.3 +
            evaluations['overall_rating'].apply(lambda x: max(0, 100-x)) * 0.2
        )
        
        # Categorize players
        evaluations['development_category'] = pd.cut(
            evaluations['development_priority'],
            bins=[0, 25, 50, 75, 100],
            labels=['Maintain', 'Monitor', 'Develop', 'Priority']
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_dev_matrix = px.scatter(
                evaluations,
                x='age',
                y='progress_score',
                color='development_category',
                size='overall_rating',
                hover_data=['first_name', 'last_name', 'position'],
                title="Development Priority Matrix",
                labels={'progress_score': 'Growth Potential', 'age': 'Age'},
                color_discrete_map={
                    'Priority': '#ff4444',
                    'Develop': '#ffaa00',
                    'Monitor': '#44ff44',
                    'Maintain': '#4444ff'
                }
            )
            fig_dev_matrix.update_layout(height=400)
            st.plotly_chart(fig_dev_matrix, use_container_width=True)
        
        with col2:
            # Development Summary
            dev_summary = evaluations['development_category'].value_counts()
            fig_dev_pie = px.pie(
                values=dev_summary.values,
                names=dev_summary.index,
                title="Development Categories",
                color_discrete_map={
                    'Priority': '#ff4444',
                    'Develop': '#ffaa00',
                    'Monitor': '#44ff44',
                    'Maintain': '#4444ff'
                }
            )
            st.plotly_chart(fig_dev_pie, use_container_width=True)
        
        # Development Plans Table
        st.write("### Recommended Development Actions")
        
        dev_plans = evaluations.nlargest(10, 'development_priority')[
            ['first_name', 'last_name', 'position', 'age', 'overall_rating', 
             'potential_rating', 'progress_score', 'development_category']
        ].copy()
        
        dev_plans['Recommended Action'] = dev_plans['development_category'].map({
            'Priority': '🔴 Intensive training program',
            'Develop': '🟡 Regular skill development',
            'Monitor': '🟢 Track progress monthly',
            'Maintain': '🔵 Current program sufficient'
        })
        
        st.dataframe(
            dev_plans.style.background_gradient(subset=['progress_score'], cmap='YlOrRd'),
            use_container_width=True,
            height=400
        )
    
    with tab4:
        st.subheader("📉 Performance Trends")
        
        # Simulate monthly performance data
        months = pd.date_range(end=datetime.now(), periods=6, freq='M')
        
        # Create trend data for top players
        top_players = evaluations.nlargest(5, 'overall_rating')
        
        trend_data = []
        for _, player in top_players.iterrows():
            base_rating = player['overall_rating']
            for i, month in enumerate(months):
                trend_data.append({
                    'Player': f"{player['first_name']} {player['last_name']}",
                    'Month': month,
                    'Rating': base_rating - (5-i) * player.get('improvement_rate', 0)
                })
        
        trend_df = pd.DataFrame(trend_data)
        
        # Line chart for rating trends
        fig_trends = px.line(
            trend_df,
            x='Month',
            y='Rating',
            color='Player',
            title="Top Players Rating Progression",
            markers=True
        )
        fig_trends.update_layout(height=400)
        st.plotly_chart(fig_trends, use_container_width=True)
        
        # Performance comparison
        col1, col2 = st.columns(2)
        
        with col1:
            # Age vs Performance
            fig_age_perf = px.scatter(
                evaluations,
                x='age',
                y='overall_rating',
                color='position',
                trendline="lowess",
                title="Age vs Performance",
                labels={'age': 'Age', 'overall_rating': 'Overall Rating'}
            )
            st.plotly_chart(fig_age_perf, use_container_width=True)
        
        with col2:
            # Experience vs Improvement
            if 'years' in evaluations.columns:
                fig_exp_imp = px.scatter(
                    evaluations,
                    x='years',
                    y='improvement_rate',
                    color='position',
                    title="Experience vs Improvement Rate",
                    labels={'years': 'Years Pro', 'improvement_rate': 'Monthly Improvement %'}
                )
                st.plotly_chart(fig_exp_imp, use_container_width=True)
    
    with tab5:
        st.subheader("🏆 Milestone Tracking")
        
        # Define milestones
        milestones = {
            'Rising Star': {'rating': 75, 'age_max': 23},
            'All-Star Potential': {'rating': 85, 'age_max': 100},
            'Elite Player': {'rating': 90, 'age_max': 100},
            'Franchise Player': {'rating': 95, 'age_max': 100}
        }
        
        # Check milestone achievements
        milestone_data = []
        for _, player in evaluations.iterrows():
            player_milestones = []
            for milestone, criteria in milestones.items():
                if (player['overall_rating'] >= criteria['rating'] and 
                    player['age'] <= criteria['age_max']):
                    player_milestones.append(milestone)
            
            if player_milestones:
                milestone_data.append({
                    'Player': f"{player['first_name']} {player['last_name']}",
                    'Position': player['position'],
                    'Rating': player['overall_rating'],
                    'Age': player['age'],
                    'Milestones': ', '.join(player_milestones)
                })
        
        if milestone_data:
            milestone_df = pd.DataFrame(milestone_data)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("### Players Achieving Milestones")
                st.dataframe(
                    milestone_df.style.background_gradient(subset=['Rating'], cmap='YlGn'),
                    use_container_width=True
                )
            
            with col2:
                st.write("### Milestone Criteria")
                for name, criteria in milestones.items():
                    st.info(f"""
                    **{name}**
                    - Rating: {criteria['rating']}+
                    - Max Age: {criteria['age_max'] if criteria['age_max'] < 100 else 'Any'}
                    """)
        
        # Progress to next milestone
        st.write("### Progress to Next Milestone")
        
        next_milestone_data = []
        for _, player in evaluations.head(10).iterrows():
            current_rating = player['overall_rating']
            next_milestone = None
            points_needed = 0
            
            for milestone, criteria in sorted(milestones.items(), key=lambda x: x[1]['rating']):
                if current_rating < criteria['rating'] and player['age'] <= criteria['age_max']:
                    next_milestone = milestone
                    points_needed = criteria['rating'] - current_rating
                    break
            
            if next_milestone:
                next_milestone_data.append({
                    'Player': f"{player['first_name']} {player['last_name']}",
                    'Current Rating': current_rating,
                    'Next Milestone': next_milestone,
                    'Points Needed': points_needed,
                    'Est. Time': f"{points_needed / max(0.1, player.get('improvement_rate', 1)):.1f} months"
                })
        
        if next_milestone_data:
            next_df = pd.DataFrame(next_milestone_data)
            st.dataframe(
                next_df.style.background_gradient(subset=['Points Needed'], cmap='RdYlGn_r'),
                use_container_width=True
            )

else:
    st.warning("No player data available. Please check your API connection or filters.")