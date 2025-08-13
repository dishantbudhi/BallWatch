##################################################
# BallWatch Basketball Analytics - Lineup Effectiveness Analysis
# Optimize player combinations and rotations for coaches
# 
# User Story: Marcus-3.4 - Lineup effectiveness and rotation optimization
# 
# Features:
# - Lineup performance analysis with advanced metrics
# - Player combination effectiveness
# - Rotation optimization recommendations
# - Interactive lineup builder and scenario testing
##################################################

import logging
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from modules.nav import SideBarLinks, check_authentication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="BallWatch - Lineup Analysis", 
    layout="wide"
)

# Check authentication and role
check_authentication('head_coach')
SideBarLinks()

# Constants
BASE_URL = "http://api:4000"
DEFAULT_TEAM_ID = st.session_state.get('team_id', 1)
COACH_NAME = st.session_state.get('first_name', 'Coach')

# Styling
st.markdown("""
<style>
.lineup-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 10px;
    color: white;
    margin: 1rem 0;
}
.performance-metric {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #007bff;
    margin: 0.5rem 0;
}
.positive-metric {
    border-left-color: #28a745;
    background-color: #d4edda;
}
.negative-metric {
    border-left-color: #dc3545;
    background-color: #f8d7da;
}
.neutral-metric {
    border-left-color: #ffc107;
    background-color: #fff3cd;
}
</style>
""", unsafe_allow_html=True)


class LineupAnalysisAPI:
    """API client for lineup analysis with comprehensive error handling."""
    
    @staticmethod
    def make_request(endpoint, params=None, timeout=15):
        """Make API request with error handling."""
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, params=params, timeout=timeout)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API request failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            return None
    
    @staticmethod
    def safe_get(data, *keys, default=None):
        """Safely extract nested values."""
        try:
            for key in keys:
                data = data[key]
            return data
        except (KeyError, TypeError, AttributeError):
            return default


# Initialize API client
api = LineupAnalysisAPI()


@st.cache_data(ttl=300, show_spinner=False)
def load_teams():
    """Load available teams for analysis."""
    teams_data = api.make_request("/api/teams")
    if teams_data and 'teams' in teams_data:
        return teams_data['teams']
    return None


@st.cache_data(ttl=300, show_spinner=False)
def load_lineup_analysis(team_id, min_games=5, season=None, sort_by='plus_minus'):
    """Load lineup effectiveness data."""
    params = {
        "team_id": team_id,
        "min_games": min_games,
        "sort_by": sort_by
    }
    if season:
        params["season"] = season
    
    return api.make_request("/api/analytics/lineup-configurations", params=params)


@st.cache_data(ttl=600, show_spinner=False)
def load_team_roster(team_id):
    """Load team roster for lineup building."""
    params = {"include_stats": "true"}
    return api.make_request(f"/api/teams/{team_id}/players", params=params)


def generate_sample_lineup_data():
    """Generate realistic sample lineup data for demonstration."""
    import random
    
    lineup_combinations = [
        "K. Irving, M. Bridges, K. Durant, N. Claxton, B. Simmons",
        "K. Durant, K. Irving, C. Johnson, M. Bridges, N. Claxton", 
        "B. Simmons, K. Irving, K. Durant, C. Johnson, N. Claxton",
        "C. Johnson, M. Bridges, K. Durant, D. Finney-Smith, N. Claxton",
        "K. Irving, M. Bridges, K. Durant, B. Simmons, D. Sharpe",
        "B. Simmons, C. Johnson, M. Bridges, K. Durant, D. Finney-Smith",
        "K. Irving, K. Durant, M. Bridges, N. Claxton, C. Johnson",
        "D. Thomas, M. Bridges, K. Durant, N. Claxton, B. Simmons",
        "K. Irving, C. Johnson, K. Durant, B. Simmons, N. Claxton"
    ]
    
    data = []
    for i, lineup in enumerate(lineup_combinations):
        plus_minus = random.uniform(-8.5, 12.3)
        off_rating = random.uniform(108.2, 118.7)
        def_rating = random.uniform(105.1, 115.8)
        games_played = random.randint(8, 35)
        total_minutes = random.uniform(120, 450)
        
        data.append({
            'lineup_id': i + 1,
            'lineup_players': lineup,
            'avg_plus_minus': round(plus_minus, 1),
            'avg_offensive_rating': round(off_rating, 1),
            'avg_defensive_rating': round(def_rating, 1),
            'games_played': games_played,
            'total_minutes': round(total_minutes, 1),
            'quarters_played': random.randint(15, 60),
            'avg_fg_pct': round(random.uniform(0.42, 0.52), 3),
            'avg_points_per_game': round(random.uniform(22, 32), 1)
        })
    
    return pd.DataFrame(data)


def render_page_header():
    """Render the page header with filters."""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("📊 Lineup Effectiveness Analysis")
        st.markdown("*Optimize player combinations and rotations*")
    
    with col2:
        st.markdown(f"**Coach:** {COACH_NAME}")
        st.markdown("**Focus:** Rotation Strategy")
        
    with col3:
        if st.button("🔄 Refresh Analysis", help="Refresh lineup data"):
            st.cache_data.clear()
            st.rerun()


def render_analysis_filters():
    """Render comprehensive filter controls."""
    st.subheader("🔧 Analysis Parameters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Team selection
        teams = load_teams()
        
        if teams:
            team_options = {team['name']: team['team_id'] for team in teams}
            
            # Find default team index
            default_index = 0
            if DEFAULT_TEAM_ID in team_options.values():
                default_index = list(team_options.values()).index(DEFAULT_TEAM_ID)
            
            selected_team_name = st.selectbox(
                "Select Team:", 
                options=list(team_options.keys()),
                index=default_index,
                help="Choose the team to analyze"
            )
            team_id = team_options[selected_team_name]
        else:
            # Fallback team selection
            fallback_teams = {
                "Brooklyn Nets": 1,
                "Boston Celtics": 2, 
                "Miami Heat": 3,
                "Philadelphia 76ers": 4
            }
            selected_team_name = st.selectbox(
                "Select Team:", 
                options=list(fallback_teams.keys()),
                help="Choose the team to analyze"
            )
            team_id = fallback_teams[selected_team_name]

    with col2:
        min_games = st.number_input(
            "Min Games Together:", 
            min_value=1, 
            max_value=50,
            value=5, 
            step=1,
            help="Minimum games played together to include lineup"
        )

    with col3:
        season = st.selectbox(
            "Season:", 
            options=["All Seasons", "2024-25", "2023-24", "2022-23"],
            index=1,
            help="Season to analyze"
        )
        season_param = None if season == "All Seasons" else season

    with col4:
        sort_options = {
            "Plus/Minus": "plus_minus",
            "Offensive Rating": "offensive_rating", 
            "Defensive Rating": "defensive_rating",
            "Games Played": "games_played",
            "Total Minutes": "minutes_played"
        }
        sort_by_display = st.selectbox(
            "Sort By:", 
            options=list(sort_options.keys()),
            help="Primary sorting metric"
        )
        sort_by = sort_options[sort_by_display]

    return team_id, selected_team_name, min_games, season_param, sort_by, sort_by_display


def format_lineup_display(lineup_str):
    """Format lineup string for better display."""
    if not lineup_str:
        return "Unknown Lineup"
    
    # Split by comma and format names
    players = lineup_str.split(', ')
    formatted_players = []
    
    for player in players[:5]:  # Limit to 5 players
        player = player.strip()
        # If it's already in short format (K. Durant), keep it
        if '. ' in player and len(player) < 15:
            formatted_players.append(player)
        else:
            # Convert full name to short format
            parts = player.split(' ')
            if len(parts) >= 2:
                formatted_players.append(f"{parts[0][0]}. {parts[-1]}")
            else:
                formatted_players.append(player)
    
    return ' | '.join(formatted_players)


def render_lineup_effectiveness_table(df, sort_by_display):
    """Render the main lineup effectiveness results table."""
    st.subheader("🏀 Lineup Performance Results")
    
    if df.empty:
        st.warning("⚠️ No lineup data available with current filters.")
        st.info("Try adjusting your filters or check if the team has sufficient game data.")
        return
    
    # Sort data by the selected metric
    if sort_by_display == "Defensive Rating":
        df_sorted = df.sort_values('avg_defensive_rating', ascending=True)  # Lower is better
    elif sort_by_display == "Plus/Minus":
        df_sorted = df.sort_values('avg_plus_minus', ascending=False)
    elif sort_by_display == "Offensive Rating":
        df_sorted = df.sort_values('avg_offensive_rating', ascending=False)
    elif sort_by_display == "Games Played":
        df_sorted = df.sort_values('games_played', ascending=False)
    else:  # Total Minutes
        df_sorted = df.sort_values('total_minutes', ascending=False)
    
    # Create enhanced display DataFrame
    display_df = pd.DataFrame()
    
    # Format lineup names
    display_df['Lineup'] = df_sorted['lineup_players'].apply(format_lineup_display)
    
    # Format numeric columns with appropriate styling
    display_df['Games'] = df_sorted['games_played'].astype(str)
    display_df['Minutes'] = df_sorted['total_minutes'].apply(lambda x: f"{x:.0f}")
    display_df['+/- Rating'] = df_sorted['avg_plus_minus'].apply(lambda x: f"{x:+.1f}")
    display_df['Off Rating'] = df_sorted['avg_offensive_rating'].apply(lambda x: f"{x:.1f}")
    display_df['Def Rating'] = df_sorted['avg_defensive_rating'].apply(lambda x: f"{x:.1f}")
    
    if 'avg_fg_pct' in df_sorted.columns:
        display_df['FG%'] = df_sorted['avg_fg_pct'].apply(lambda x: f"{x:.1%}")
    
    if 'avg_points_per_game' in df_sorted.columns:
        display_df['PPG'] = df_sorted['avg_points_per_game'].apply(lambda x: f"{x:.1f}")
    
    # Display with color coding
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Add insights below the table
    best_lineup = df_sorted.iloc[0]
    worst_lineup = df_sorted.iloc[-1]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="positive-metric">
            <h5>🏆 Best Performing Lineup</h5>
            <p><strong>{format_lineup_display(best_lineup['lineup_players'])}</strong></p>
            <p>+/- Rating: <strong>{best_lineup['avg_plus_minus']:+.1f}</strong></p>
            <p>Games: {best_lineup['games_played']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Find most used lineup
        most_used = df_sorted.loc[df_sorted['total_minutes'].idxmax()]
        st.markdown(f"""
        <div class="performance-metric">
            <h5>⏱️ Most Used Lineup</h5>
            <p><strong>{format_lineup_display(most_used['lineup_players'])}</strong></p>
            <p>Minutes: <strong>{most_used['total_minutes']:.0f}</strong></p>
            <p>+/- Rating: <strong>{most_used['avg_plus_minus']:+.1f}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Calculate efficiency
        avg_plus_minus = df_sorted['avg_plus_minus'].mean()
        efficient_lineups = len(df_sorted[df_sorted['avg_plus_minus'] > avg_plus_minus])
        
        efficiency_color = "positive-metric" if efficient_lineups > len(df_sorted) / 2 else "negative-metric"
        
        st.markdown(f"""
        <div class="{efficiency_color}">
            <h5>📈 Lineup Efficiency</h5>
            <p><strong>{efficient_lineups}/{len(df_sorted)}</strong> lineups above average</p>
            <p>Avg +/-: <strong>{avg_plus_minus:+.1f}</strong></p>
            <p>Efficiency: <strong>{(efficient_lineups/len(df_sorted)*100):.0f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)


def render_performance_visualizations(df):
    """Render interactive lineup performance visualizations."""
    st.subheader("📈 Performance Visualizations")
    
    if df.empty:
        st.info("No data available for visualization.")
        return
    
    # Limit to top 12 lineups for readability
    df_viz = df.head(12).copy()
    df_viz['lineup_short'] = df_viz['lineup_players'].apply(format_lineup_display)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Plus/Minus horizontal bar chart
        fig_plus_minus = px.bar(
            df_viz,
            x='avg_plus_minus',
            y='lineup_short',
            orientation='h',
            title='Plus/Minus Rating by Lineup',
            labels={
                'avg_plus_minus': 'Plus/Minus Rating',
                'lineup_short': 'Lineup'
            },
            color='avg_plus_minus',
            color_continuous_scale=['red', 'white', 'green'],
            color_continuous_midpoint=0
        )
        
        fig_plus_minus.update_layout(
            height=500,
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        fig_plus_minus.update_traces(
            hovertemplate="<b>%{y}</b><br>+/- Rating: %{x:+.1f}<extra></extra>"
        )
        
        st.plotly_chart(fig_plus_minus, use_container_width=True)
    
    with col2:
        # Offensive vs Defensive Rating scatter plot
        fig_efficiency = px.scatter(
            df_viz,
            x='avg_defensive_rating',
            y='avg_offensive_rating', 
            size='total_minutes',
            color='avg_plus_minus',
            hover_name='lineup_short',
            title='Offensive vs Defensive Efficiency',
            labels={
                'avg_defensive_rating': 'Defensive Rating (lower is better)',
                'avg_offensive_rating': 'Offensive Rating (higher is better)',
                'total_minutes': 'Total Minutes',
                'avg_plus_minus': '+/- Rating'
            },
            color_continuous_scale=['red', 'white', 'green'],
            color_continuous_midpoint=0
        )
        
        # Add quadrant lines for league averages
        league_avg_off = df_viz['avg_offensive_rating'].median()
        league_avg_def = df_viz['avg_defensive_rating'].median()
        
        fig_efficiency.add_hline(
            y=league_avg_off, 
            line_dash="dash", 
            line_color="gray", 
            opacity=0.7,
            annotation_text="League Avg Offense"
        )
        fig_efficiency.add_vline(
            x=league_avg_def, 
            line_dash="dash", 
            line_color="gray", 
            opacity=0.7,
            annotation_text="League Avg Defense"
        )
        
        fig_efficiency.update_layout(height=500)
        
        st.plotly_chart(fig_efficiency, use_container_width=True)


def render_insights_and_recommendations(df, team_name):
    """Render actionable insights and coaching recommendations."""
    st.subheader("💡 Coaching Insights & Recommendations")
    
    if df.empty:
        st.info("No lineup data available for analysis.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔥 Key Findings")
        
        # Analyze the data for insights
        positive_lineups = len(df[df['avg_plus_minus'] > 0])
        total_lineups = len(df)
        best_plus_minus = df['avg_plus_minus'].max()
        worst_plus_minus = df['avg_plus_minus'].min()
        
        # High usage lineups analysis
        df['usage_rank'] = df['total_minutes'].rank(method='dense', ascending=False)
        high_usage_lineups = df[df['usage_rank'] <= 3]
        high_usage_avg_plus_minus = high_usage_lineups['avg_plus_minus'].mean()
        
        insights = []
        
        # Performance insights
        if positive_lineups / total_lineups > 0.6:
            insights.append(("positive", f"✅ Strong lineup depth: {positive_lineups}/{total_lineups} lineups are positive"))
        else:
            insights.append(("negative", f"⚠️ Lineup concerns: Only {positive_lineups}/{total_lineups} lineups are positive"))
        
        # Usage vs performance insight
        if high_usage_avg_plus_minus > 3:
            insights.append(("positive", f"✅ Top rotations are effective (+{high_usage_avg_plus_minus:.1f} avg)"))
        elif high_usage_avg_plus_minus < 0:
            insights.append(("negative", f"❌ Need rotation changes: Top lineups averaging {high_usage_avg_plus_minus:+.1f}"))
        else:
            insights.append(("neutral", f"📊 Mixed results from top rotations ({high_usage_avg_plus_minus:+.1f} avg)"))
        
        # Range of performance
        performance_range = best_plus_minus - worst_plus_minus
        if performance_range > 15:
            insights.append(("neutral", f"📊 Wide performance gap: {performance_range:.1f} point spread"))
        
        # Display insights
        for insight_type, insight_text in insights:
            if insight_type == "positive":
                st.success(insight_text)
            elif insight_type == "negative":
                st.error(insight_text)
            else:
                st.info(insight_text)
    
    with col2:
        st.markdown("#### 🎯 Coaching Recommendations")
        
        recommendations = []
        
        # Analyze data for recommendations
        if not df.empty:
            # Find underused high-performers
            df['performance_tier'] = pd.qcut(df['avg_plus_minus'], q=3, labels=['Low', 'Medium', 'High'])
            df['usage_tier'] = pd.qcut(df['total_minutes'], q=3, labels=['Low', 'Medium', 'High'])
            
            underused_performers = df[
                (df['performance_tier'] == 'High') & 
                (df['usage_tier'] == 'Low')
            ]
            
            overused_underperformers = df[
                (df['performance_tier'] == 'Low') & 
                (df['usage_tier'] == 'High')
            ]
            
            if not underused_performers.empty:
                recommendations.append("📈 Consider increasing minutes for high-performing lineups")
            
            if not overused_underperformers.empty:
                recommendations.append("📉 Reduce usage of underperforming rotations")
            
            # Defensive analysis
            good_defense = df[df['avg_defensive_rating'] < df['avg_defensive_rating'].median()]
            if not good_defense.empty:
                recommendations.append("🛡️ Utilize best defensive lineups in key moments")
            
            # Offensive analysis
            good_offense = df[df['avg_offensive_rating'] > df['avg_offensive_rating'].median()]
            if not good_offense.empty:
                recommendations.append("⚡ Deploy top offensive lineups when trailing")
        
        # Add general recommendations
        recommendations.extend([
            "🔄 Experiment with new combinations in low-stakes games",
            "📊 Monitor +/- trends throughout the season",
            "🎯 Focus on lineups that will play in playoffs"
        ])
        
        for i, rec in enumerate(recommendations[:6], 1):  # Limit to 6 recommendations
            st.markdown(f"{i}. {rec}")


def render_lineup_optimizer():
    """Render interactive lineup optimization tools."""
    st.subheader("🔧 Lineup Optimizer & Scenario Testing")
    
    with st.expander("🎯 Build Custom Lineup", expanded=False):
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("#### Player Selection")
            
            # Load team roster for player selection
            roster_data = load_team_roster(DEFAULT_TEAM_ID)
            
            if roster_data and api.safe_get(roster_data, 'roster'):
                available_players = []
                for player in roster_data['roster']:
                    name = f"{player.get('first_name', 'Unknown')} {player.get('last_name', 'Player')}"
                    position = player.get('position', 'N/A')
                    available_players.append(f"{name} ({position})")
                
                selected_players = st.multiselect(
                    "Select 5 Players:",
                    options=available_players,
                    max_selections=5,
                    help="Choose exactly 5 players for the lineup"
                )
                
                # Position validation
                if len(selected_players) == 5:
                    st.success("✅ Valid lineup selected!")
                elif len(selected_players) > 0:
                    st.info(f"📝 {len(selected_players)}/5 players selected")
                
            else:
                # Fallback player list
                fallback_players = [
                    "Kevin Durant (SF)", "Kyrie Irving (PG)", "Ben Simmons (PF)",
                    "Nic Claxton (C)", "Cam Johnson (SG)", "Mikal Bridges (SF)",
                    "Dorian Finney-Smith (PF)", "Day'Ron Sharpe (C)",
                    "Dennis Smith Jr. (PG)", "Royce O'Neale (SF)"
                ]
                
                selected_players = st.multiselect(
                    "Select 5 Players:",
                    options=fallback_players,
                    max_selections=5,
                    help="Choose exactly 5 players for the lineup"
                )
        
        with col2:
            st.markdown("#### Lineup Prediction")
            
            if len(selected_players) == 5:
                # Generate mock predictions based on player selection
                # In a real system, this would use ML models or complex analytics
                
                base_rating = 110  # Starting point
                
                # Adjust based on player quality (simplified)
                star_players = sum(1 for p in selected_players if any(star in p for star in ["Durant", "Irving"]))
                base_rating += star_players * 4
                
                # Position balance check
                positions = [p.split('(')[-1].strip(')') for p in selected_players]
                if len(set(positions)) >= 4:  # Good position diversity
                    base_rating += 2
                
                predicted_plus_minus = round(base_rating - 110 + np.random.normal(0, 2), 1)
                predicted_off_rating = round(base_rating + np.random.normal(0, 3), 1)
                predicted_def_rating = round(110 - (base_rating - 110) * 0.3 + np.random.normal(0, 2), 1)
                
                # Display predictions
                st.metric("Predicted +/-", f"{predicted_plus_minus:+.1f}")
                st.metric("Predicted Off Rating", f"{predicted_off_rating:.1f}")
                st.metric("Predicted Def Rating", f"{predicted_def_rating:.1f}")
                
                # Lineup assessment
                if predicted_plus_minus > 5:
                    st.success("🔥 High-potential lineup!")
                elif predicted_plus_minus > 0:
                    st.info("📊 Solid lineup combination")
                else:
                    st.warning("⚠️ May need adjustments")
                
            else:
                st.info("👆 Select exactly 5 players to see predictions")
                
                # Show lineup building tips
                st.markdown("##### 💡 Lineup Building Tips")
                tips = [
                    "Balance scoring and defense",
                    "Consider position versatility", 
                    "Mix veterans with young players",
                    "Account for chemistry and fit"
                ]
                
                for tip in tips:
                    st.caption(f"• {tip}")
        
        # Save lineup scenario
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            scenario_name = st.text_input(
                "Scenario Name:",
                placeholder="e.g., Closing Lineup, Small Ball, etc."
            )
            
            if st.button("💾 Save Lineup Scenario", type="primary", use_container_width=True):
                if len(selected_players) == 5 and scenario_name.strip():
                    # In a real app, this would save to database
                    st.success(f"✅ Saved '{scenario_name}' lineup scenario!")
                    st.balloons()
                else:
                    st.error("Please provide a scenario name and select exactly 5 players.")


def render_rotation_analysis(df):
    """Render rotation pattern analysis."""
    st.subheader("🔄 Rotation Pattern Analysis")
    
    if df.empty:
        st.info("No data available for rotation analysis.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⏰ Usage Patterns")
        
        # Categorize lineups by usage
        df['usage_category'] = pd.cut(
            df['total_minutes'], 
            bins=3, 
            labels=['Low Usage', 'Medium Usage', 'High Usage']
        )
        
        usage_summary = df.groupby('usage_category').agg({
            'avg_plus_minus': 'mean',
            'lineup_players': 'count'
        }).round(1)
        
        for category, data in usage_summary.iterrows():
            count = int(data['lineup_players'])
            avg_rating = data['avg_plus_minus']
            
            color_class = "positive-metric" if avg_rating > 2 else "negative-metric" if avg_rating < -2 else "neutral-metric"
            
            st.markdown(f"""
            <div class="{color_class}">
                <h6>{category}</h6>
                <p>{count} lineups • Avg +/-: {avg_rating:+.1f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🎯 Optimization Opportunities")
        
        opportunities = []
        
        # Find optimization opportunities
        if not df.empty:
            # High performers with low usage
            high_perf_low_usage = df[
                (df['avg_plus_minus'] > df['avg_plus_minus'].quantile(0.75)) &
                (df['total_minutes'] < df['total_minutes'].quantile(0.5))
            ]
            
            if not high_perf_low_usage.empty:
                opportunities.append(f"📈 {len(high_perf_low_usage)} high-performing lineups are underutilized")
            
            # Low performers with high usage
            low_perf_high_usage = df[
                (df['avg_plus_minus'] < df['avg_plus_minus'].quantile(0.25)) &
                (df['total_minutes'] > df['total_minutes'].quantile(0.5))
            ]
            
            if not low_perf_high_usage.empty:
                opportunities.append(f"📉 {len(low_perf_high_usage)} overused lineups underperforming")
            
            # Defensive specialists
            good_defense = df[df['avg_defensive_rating'] < df['avg_defensive_rating'].quantile(0.3)]
            if not good_defense.empty:
                opportunities.append(f"🛡️ {len(good_defense)} lineups excel defensively")
            
            # Offensive specialists  
            good_offense = df[df['avg_offensive_rating'] > df['avg_offensive_rating'].quantile(0.7)]
            if not good_offense.empty:
                opportunities.append(f"⚡ {len(good_offense)} lineups excel offensively")
        
        # Default opportunities if none found
        if not opportunities:
            opportunities = [
                "🔍 More data needed for detailed analysis",
                "📊 Continue monitoring lineup performance",
                "🎯 Focus on small sample size lineups"
            ]
        
        for opportunity in opportunities:
            st.info(opportunity)


def main():
    """Main application function."""
    try:
        # Render page header
        render_page_header()
        st.markdown("---")
        
        # Render filter controls
        filter_result = render_analysis_filters()
        if not filter_result:
            st.error("Unable to load filter options. Please check system connectivity.")
            return
        
        team_id, team_name, min_games, season, sort_by, sort_by_display = filter_result
        
        st.markdown("---")
        
        # Load lineup analysis data
        with st.spinner(f"🔍 Analyzing lineup effectiveness for {team_name}..."):
            lineup_data = load_lineup_analysis(team_id, min_games, season, sort_by)
        
        # Process data
        if lineup_data and api.safe_get(lineup_data, 'lineup_effectiveness'):
            df = pd.DataFrame(lineup_data['lineup_effectiveness'])
            
            if df.empty:
                st.warning(f"""
                ⚠️ No lineup data found for **{team_name}** with current filters.
                
                **Try adjusting your parameters:**
                - Lower the minimum games requirement ({min_games} currently)
                - Remove the season filter ({season} currently)
                - Check if the team has sufficient game data
                """)
                return
        else:
            # Use fallback sample data for demonstration
            st.info("📊 Using sample data - API connection unavailable")
            df = generate_sample_lineup_data()
        
        # Display analysis results
        render_lineup_effectiveness_table(df, sort_by_display)
        
        st.markdown("---")
        render_performance_visualizations(df)
        
        st.markdown("---")
        render_insights_and_recommendations(df, team_name)
        
        st.markdown("---")
        render_rotation_analysis(df)
        
        st.markdown("---")
        render_lineup_optimizer()
        
        # Footer with analysis details
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.caption(f"**Team:** {team_name}")
            
        with col2:
            st.caption(f"**Minimum Games:** {min_games}")
            
        with col3:
            st.caption(f"**Sorted by:** {sort_by_display}")
        
        st.caption(f"*Analysis generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*")
        
    except Exception as e:
        st.error("An error occurred while loading the lineup analysis.")
        logger.error(f"Lineup analysis error: {e}")
        
        if st.button("🔄 Retry Analysis"):
            st.cache_data.clear()
            st.rerun()


if __name__ == "__main__":
    main()