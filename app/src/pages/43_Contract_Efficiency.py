import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Free Agency",
    page_icon="💰",
    layout="wide"
)

# Back button at the top
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    if st.button("← Back to Home", type="secondary", use_container_width=True):
        st.switch_page("General_Manager_Home.py")  # Update with your home page filename

# Title and header
st.title("💰 Free Agency Management")
st.markdown("### Analyze free agents, evaluate contracts, and build your championship roster")

# API Base URL
API_BASE_URL = "http://localhost:5000"

# NBA Teams for context
NBA_TEAMS = {
    1: "Boston Celtics", 2: "Brooklyn Nets", 3: "New York Knicks",
    4: "Philadelphia 76ers", 5: "Toronto Raptors", 6: "Chicago Bulls",
    7: "Cleveland Cavaliers", 8: "Detroit Pistons", 9: "Indiana Pacers",
    10: "Milwaukee Bucks", 11: "Atlanta Hawks", 12: "Charlotte Hornets",
    13: "Miami Heat", 14: "Orlando Magic", 15: "Washington Wizards",
    16: "Denver Nuggets", 17: "Minnesota Timberwolves", 18: "Oklahoma City Thunder",
    19: "Portland Trail Blazers", 20: "Utah Jazz", 21: "Golden State Warriors",
    22: "Los Angeles Clippers", 23: "Los Angeles Lakers", 24: "Phoenix Suns",
    25: "Sacramento Kings", 26: "Dallas Mavericks", 27: "Houston Rockets",
    28: "Memphis Grizzlies", 29: "New Orleans Pelicans", 30: "San Antonio Spurs"
}

# Function to fetch free agents
def fetch_free_agents():
    try:
        response = requests.get(f"{API_BASE_URL}/strategy/draft-evaluations", 
                               params={'evaluation_type': 'free_agent'})
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

# Function to fetch team info
def fetch_team_info(team_id):
    try:
        response = requests.get(f"{API_BASE_URL}/teams/{team_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

# Sidebar filters
st.sidebar.header("🔍 Free Agent Filters")

# Your team selection (Andre's team)
your_team = st.sidebar.selectbox(
    "Your Team",
    list(NBA_TEAMS.values()),
    index=0  # Default to Celtics or change to Andre's team
)
your_team_id = [k for k, v in NBA_TEAMS.items() if v == your_team][0]

st.sidebar.markdown("---")

# Position filter
position_filter = st.sidebar.multiselect(
    "Positions",
    ["PG", "SG", "SF", "PF", "C"],
    default=["PG", "SG", "SF", "PF", "C"]
)

# Salary range
salary_range = st.sidebar.slider(
    "Expected Salary Range ($M)",
    min_value=0.0,
    max_value=50.0,
    value=(0.0, 35.0),
    step=0.5
)

# Rating filter
rating_min = st.sidebar.slider(
    "Minimum Overall Rating",
    min_value=60,
    max_value=95,
    value=70,
    step=5
)

# Age filter
age_range = st.sidebar.slider(
    "Age Range",
    min_value=18,
    max_value=40,
    value=(22, 32)
)

# Contract preference
contract_pref = st.sidebar.selectbox(
    "Contract Strategy",
    ["Best Value", "Win Now", "Future Assets", "Balanced"]
)

# Cap space settings (these would come from your team's actual data)
SALARY_CAP = 136.0  # NBA salary cap
LUXURY_TAX = 165.0  # Luxury tax threshold
YOUR_CURRENT_PAYROLL = 118.5  # Your team's current payroll

# Calculate available space
available_cap = SALARY_CAP - YOUR_CURRENT_PAYROLL
luxury_room = LUXURY_TAX - YOUR_CURRENT_PAYROLL

# Fetch free agents data
fa_data = fetch_free_agents()

# Create sample data if API is not available
if not fa_data or not fa_data.get('evaluations'):
    # Sample free agents data for demonstration
    free_agents = pd.DataFrame({
        'player_id': range(1, 21),
        'first_name': ['Damian', 'Pascal', 'Fred', 'OG', 'Gary', 'Dillon', 'Austin', 
                       'Kelly', 'Gabe', 'Tobias', 'Kyle', 'Buddy', 'PJ', 'Malik',
                       'Cameron', 'Jalen', 'Christian', 'Tyus', 'Cedi', 'Derrick'],
        'last_name': ['Lillard', 'Siakam', 'VanVleet', 'Anunoby', 'Trent Jr', 'Brooks', 'Reaves',
                     'Oubre Jr', 'Vincent', 'Harris', 'Kuzma', 'Hield', 'Washington', 'Monk',
                     'Johnson', 'McDaniels', 'Wood', 'Jones', 'Osman', 'Rose'],
        'position': ['PG', 'PF', 'PG', 'SF', 'SG', 'SG', 'SG', 'SF', 'PG', 'SF', 
                    'PF', 'SG', 'PF', 'SG', 'SF', 'SG', 'C', 'PG', 'SF', 'PG'],
        'age': [33, 29, 29, 26, 25, 28, 25, 28, 27, 31, 
               28, 31, 25, 26, 27, 25, 28, 27, 28, 35],
        'overall_rating': [88, 85, 82, 81, 78, 76, 77, 75, 73, 74,
                          77, 76, 72, 74, 71, 73, 75, 74, 70, 68],
        'offensive_rating': [92, 83, 85, 76, 80, 78, 79, 77, 72, 71,
                           79, 82, 68, 78, 69, 75, 78, 72, 68, 65],
        'defensive_rating': [72, 84, 76, 86, 75, 73, 72, 71, 73, 75,
                           72, 68, 76, 68, 73, 70, 70, 75, 71, 64],
        'potential_rating': [88, 86, 82, 85, 82, 76, 82, 75, 76, 74,
                           77, 76, 78, 78, 74, 78, 75, 76, 70, 68],
        'expected_salary': [45.0, 38.0, 32.0, 28.0, 18.0, 12.0, 15.0, 11.0, 8.5, 10.0,
                          13.0, 10.5, 6.5, 9.0, 5.5, 7.0, 8.0, 6.0, 4.5, 2.5],
        'years_exp': [11, 7, 7, 6, 5, 6, 3, 6, 5, 9,
                     6, 11, 4, 7, 4, 4, 8, 8, 7, 14],
        'previous_team': ['POR', 'TOR', 'HOU', 'TOR', 'TOR', 'HOU', 'LAL', 'PHI', 'LAL', 'PHI',
                        'WAS', 'IND', 'CHA', 'SAC', 'BKN', 'MIN', 'DAL', 'WAS', 'CLE', 'NYK']
    })
else:
    free_agents = pd.DataFrame(fa_data['evaluations'])

# Apply filters
if position_filter:
    free_agents = free_agents[free_agents['position'].isin(position_filter)]

if 'age' in free_agents:
    free_agents = free_agents[
        (free_agents['age'] >= age_range[0]) & 
        (free_agents['age'] <= age_range[1])
    ]

if 'overall_rating' in free_agents:
    free_agents = free_agents[free_agents['overall_rating'] >= rating_min]

if 'expected_salary' in free_agents:
    free_agents = free_agents[
        (free_agents['expected_salary'] >= salary_range[0]) & 
        (free_agents['expected_salary'] <= salary_range[1])
    ]

# Calculate advanced metrics
free_agents['value_score'] = (free_agents['overall_rating'] / (free_agents['expected_salary'] + 1)).round(2)
free_agents['efficiency_rating'] = (
    (free_agents['overall_rating'] * 0.4) + 
    (free_agents['offensive_rating'] * 0.3) + 
    (free_agents['defensive_rating'] * 0.3)
).round(1)
free_agents['contract_value'] = free_agents['value_score'].apply(
    lambda x: '💎 Excellent' if x > 5 else ('✅ Good' if x > 3 else ('⚠️ Fair' if x > 2 else '❌ Poor'))
)

# Top metrics row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="🏀 Available FAs",
        value=len(free_agents),
        delta=f"{len(free_agents[free_agents['overall_rating'] >= 80])} elite"
    )

with col2:
    st.metric(
        label="💵 Cap Space",
        value=f"${available_cap:.1f}M",
        delta=f"${luxury_room:.1f}M to tax",
        delta_color="normal" if available_cap > 0 else "inverse"
    )

with col3:
    top_targets = len(free_agents[free_agents['value_score'] >= 4])
    st.metric(
        label="🎯 Top Targets",
        value=top_targets,
        delta="High value"
    )

with col4:
    avg_age = free_agents['age'].mean()
    st.metric(
        label="📊 Avg Age",
        value=f"{avg_age:.1f}",
        delta="FA Pool"
    )

with col5:
    affordable = len(free_agents[free_agents['expected_salary'] <= available_cap])
    st.metric(
        label="✅ Affordable",
        value=affordable,
        delta=f"Within cap"
    )

st.markdown("---")

# Main content tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Target Board", 
    "📊 Market Analysis", 
    "💎 Value Finder",
    "🤝 Contract Negotiator",
    "📋 Roster Builder",
    "📈 Impact Projections"
])

with tab1:
    st.subheader("🎯 Free Agent Target Board")
    
    # Create tiers
    free_agents['tier'] = pd.cut(
        free_agents['overall_rating'],
        bins=[0, 70, 75, 80, 85, 100],
        labels=['Role Player', 'Rotation', 'Starter', 'Star', 'Superstar']
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Interactive scatter plot
        fig = px.scatter(
            free_agents,
            x='expected_salary',
            y='overall_rating',
            size='age',
            color='tier',
            hover_data=['first_name', 'last_name', 'position', 'value_score', 'contract_value'],
            labels={
                'expected_salary': 'Expected Salary ($M)',
                'overall_rating': 'Overall Rating',
                'tier': 'Player Tier'
            },
            title="Free Agent Market Map",
            color_discrete_map={
                'Superstar': '#FFD700',
                'Star': '#FF4500',
                'Starter': '#32CD32',
                'Rotation': '#4169E1',
                'Role Player': '#808080'
            }
        )
        
        # Add value zones
        fig.add_shape(
            type="rect", x0=0, y0=78, x1=available_cap, y1=100,
            fillcolor="green", opacity=0.1,
            line=dict(color="green", width=2, dash="dash")
        )
        fig.add_annotation(
            x=available_cap/2, y=89, 
            text="🎯 Affordable Target Zone", 
            showarrow=False,
            font=dict(color="green", size=12)
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("### 🏆 Priority Targets")
        
        # Top value players by tier
        for tier in ['Superstar', 'Star', 'Starter']:
            tier_players = free_agents[free_agents['tier'] == tier].nlargest(3, 'value_score')
            if not tier_players.empty:
                st.write(f"**{tier}s**")
                for _, player in tier_players.iterrows():
                    affordability = "✅" if player['expected_salary'] <= available_cap else "❌"
                    st.write(f"{affordability} {player['first_name']} {player['last_name']} ({player['position']})")
                    st.caption(f"${player['expected_salary']:.1f}M | Rating: {player['overall_rating']}")
                st.write("")

with tab2:
    st.subheader("📊 Free Agent Market Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Position supply and demand
        position_analysis = free_agents.groupby('position').agg({
            'player_id': 'count',
            'expected_salary': 'mean',
            'overall_rating': 'mean'
        }).round(1)
        position_analysis.columns = ['Available', 'Avg Salary ($M)', 'Avg Rating']
        
        fig_pos = px.bar(
            position_analysis,
            x=position_analysis.index,
            y='Available',
            color='Avg Rating',
            title="Position Availability & Quality",
            labels={'index': 'Position', 'Available': 'Number of Players'},
            color_continuous_scale='YlOrRd'
        )
        st.plotly_chart(fig_pos, use_container_width=True)
    
    with col2:
        # Age distribution
        fig_age = px.histogram(
            free_agents,
            x='age',
            color='tier',
            nbins=15,
            title="Age Distribution by Tier",
            labels={'age': 'Age', 'count': 'Number of Players'}
        )
        st.plotly_chart(fig_age, use_container_width=True)
    
    # Market trends
    st.write("### 💹 Market Trends")
    
    # Rating vs Salary correlation
    fig_trend = px.scatter(
        free_agents,
        x='overall_rating',
        y='expected_salary',
        color='position',
        size='age',
        trendline="ols",
        title="Market Rate Analysis: Rating vs Expected Salary",
        labels={'overall_rating': 'Overall Rating', 'expected_salary': 'Expected Salary ($M)'}
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with tab3:
    st.subheader("💎 Value Finder")
    
    # Value categories
    free_agents['value_category'] = pd.cut(
        free_agents['value_score'],
        bins=[0, 2, 3, 5, 100],
        labels=['Overpriced', 'Fair Value', 'Good Value', 'Excellent Value']
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Value matrix
        fig_value = px.scatter(
            free_agents,
            x='age',
            y='value_score',
            size='expected_salary',
            color='value_category',
            hover_data=['first_name', 'last_name', 'position', 'overall_rating'],
            title="Value Analysis: Finding Hidden Gems",
            labels={'age': 'Age', 'value_score': 'Value Score (Rating/Salary)'},
            color_discrete_map={
                'Excellent Value': '#00FF00',
                'Good Value': '#90EE90',
                'Fair Value': '#FFD700',
                'Overpriced': '#FF6347'
            }
        )
        fig_value.add_hline(y=3, line_dash="dash", line_color="gray", 
                           annotation_text="Good Value Threshold")
        fig_value.update_layout(height=450)
        st.plotly_chart(fig_value, use_container_width=True)
    
    with col2:
        st.write("### 💎 Best Values")
        
        best_values = free_agents.nlargest(5, 'value_score')
        for _, player in best_values.iterrows():
            st.success(f"""
            **{player['first_name']} {player['last_name']}**
            - Position: {player['position']}
            - Age: {player['age']}
            - Rating: {player['overall_rating']}
            - Salary: ${player['expected_salary']:.1f}M
            - Value: {player['value_score']:.2f}
            """)
    
    # Detailed value table
    st.write("### 📋 Value Rankings")
    
    value_display = free_agents.nlargest(10, 'value_score')[
        ['first_name', 'last_name', 'position', 'age', 'overall_rating', 
         'expected_salary', 'value_score', 'value_category', 'contract_value']
    ].copy()
    
    st.dataframe(
        value_display.style.format({
            'expected_salary': '${:.1f}M',
            'overall_rating': '{:.0f}',
            'value_score': '{:.2f}'
        }).background_gradient(subset=['value_score'], cmap='RdYlGn'),
        use_container_width=True,
        height=400
    )

with tab4:
    st.subheader("🤝 Contract Negotiator")
    
    # Player selection
    player_names = free_agents.apply(
        lambda x: f"{x['first_name']} {x['last_name']} ({x['position']}) - ${x['expected_salary']:.1f}M",
        axis=1
    )
    selected_player_name = st.selectbox("Select Player to Negotiate", player_names)
    
    if selected_player_name:
        player_idx = player_names[player_names == selected_player_name].index[0]
        player = free_agents.iloc[player_idx]
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.info(f"""
            **Player Profile**
            - Name: {player['first_name']} {player['last_name']}
            - Position: {player['position']}
            - Age: {player['age']}
            - Overall: {player['overall_rating']}
            - Offense: {player['offensive_rating']}
            - Defense: {player['defensive_rating']}
            """)
            
            # Contract parameters
            st.write("### 📝 Contract Offer")
            
            offered_salary = st.slider(
                "Annual Salary ($M)",
                min_value=1.0,
                max_value=min(50.0, available_cap),
                value=float(player['expected_salary'] * 0.9),
                step=0.5
            )
            
            contract_years = st.slider("Years", 1, 5, 3)
            
            guaranteed_pct = st.slider("Guaranteed %", 50, 100, 80, 5)
        
        with col2:
            st.write("### 📊 Contract Structure")
            
            # Options
            team_option = st.checkbox("Team Option (Final Year)")
            player_option = st.checkbox("Player Option (Final Year)")
            ntc = st.checkbox("No-Trade Clause")
            
            # Incentives
            st.write("**Incentives**")
            all_star = st.checkbox("All-Star Bonus (+$2M)")
            playoffs = st.checkbox("Playoffs Bonus (+$1M)")
            championship = st.checkbox("Championship (+$3M)")
            
            total_incentives = (all_star * 2) + (playoffs * 1) + (championship * 3)
            
        with col3:
            st.write("### 💰 Deal Summary")
            
            base_total = offered_salary * contract_years
            guaranteed = base_total * (guaranteed_pct / 100)
            max_value = base_total + (total_incentives * contract_years)
            
            st.success(f"""
            **Contract Details**
            - Base: ${offered_salary:.1f}M x {contract_years} years
            - Total: ${base_total:.1f}M
            - Guaranteed: ${guaranteed:.1f}M
            - Max Value: ${max_value:.1f}M
            """)
            
            # Calculate likelihood
            salary_diff = abs(offered_salary - player['expected_salary']) / player['expected_salary']
            base_likelihood = 100 - (salary_diff * 100)
            
            # Adjust for options
            if player_option: base_likelihood += 15
            if team_option: base_likelihood -= 10
            if ntc: base_likelihood += 10
            if guaranteed_pct >= 90: base_likelihood += 10
            
            likelihood = min(100, max(0, base_likelihood))
            
            st.write("### 🎲 Acceptance Probability")
            st.progress(likelihood / 100)
            st.write(f"{likelihood:.0f}% chance of acceptance")
            
            # Cap impact
            if offered_salary <= available_cap:
                st.success(f"✅ Fits within cap space")
                st.write(f"Remaining: ${available_cap - offered_salary:.1f}M")
            else:
                st.error(f"❌ Exceeds cap by ${offered_salary - available_cap:.1f}M")

with tab5:
    st.subheader("📋 Roster Builder")
    
    st.write("Build your ideal free agency haul by selecting multiple players")
    
    # Multi-player selection
    selected_players = st.multiselect(
        "Select Players to Sign",
        player_names,
        max_selections=5
    )
    
    if selected_players:
        roster_data = []
        total_salary = 0
        
        for player_name in selected_players:
            player_idx = player_names[player_names == player_name].index[0]
            player = free_agents.iloc[player_idx]
            
            roster_data.append({
                'Name': f"{player['first_name']} {player['last_name']}",
                'Position': player['position'],
                'Age': player['age'],
                'Rating': player['overall_rating'],
                'Expected Salary': player['expected_salary'],
                'Value Score': player['value_score']
            })
            total_salary += player['expected_salary']
        
        roster_df = pd.DataFrame(roster_data)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("### Selected Players")
            st.dataframe(
                roster_df.style.format({
                    'Expected Salary': '${:.1f}M',
                    'Value Score': '{:.2f}'
                }).background_gradient(subset=['Rating'], cmap='YlGn'),
                use_container_width=True
            )
            
            # Position balance
            position_counts = roster_df['Position'].value_counts()
            fig_pos = px.pie(
                values=position_counts.values,
                names=position_counts.index,
                title="Position Distribution",
                hole=0.4
            )
            st.plotly_chart(fig_pos, use_container_width=True)
        
        with col2:
            st.write("### 💰 Financial Summary")
            
            new_payroll = YOUR_CURRENT_PAYROLL + total_salary
            
            st.metric("Total FA Cost", f"${total_salary:.1f}M")
            st.metric("New Payroll", f"${new_payroll:.1f}M")
            
            if new_payroll <= SALARY_CAP:
                st.success(f"✅ Under salary cap")
                st.write(f"Room: ${SALARY_CAP - new_payroll:.1f}M")
            elif new_payroll <= LUXURY_TAX:
                st.warning(f"⚠️ Over cap, under tax")
                st.write(f"Over cap: ${new_payroll - SALARY_CAP:.1f}M")
            else:
                st.error(f"❌ In luxury tax")
                st.write(f"Tax bill: ${(new_payroll - LUXURY_TAX) * 1.5:.1f}M")
            
            # Team improvement
            avg_rating = roster_df['Rating'].mean()
            st.write("### 📈 Projected Impact")
            st.progress(avg_rating / 100)
            st.write(f"Avg Rating: {avg_rating:.1f}")
            
            if avg_rating >= 80:
                st.success("🏆 Championship Contender")
            elif avg_rating >= 75:
                st.info("🎯 Playoff Team")
            else:
                st.warning("🔧 Development Needed")

with tab6:
    st.subheader("📈 Impact Projections")
    
    st.write("Analyze how free agent signings would impact your team")
    
    # Current team rating (simulated)
    current_team_rating = 78.5
    
    # Calculate projections
    if selected_players:
        # Impact calculation
        new_players_avg = roster_df['Rating'].mean()
        roster_size = 15  # NBA roster size
        new_team_rating = (current_team_rating * (roster_size - len(selected_players)) + 
                          total_salary) / roster_size
        
        improvement = new_team_rating - current_team_rating
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Rating projection
            fig_impact = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=new_team_rating,
                delta={'reference': current_team_rating},
                title={'text': "Projected Team Rating"},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkgreen"},
                       'steps': [
                           {'range': [0, 70], 'color': "lightgray"},
                           {'range': [70, 80], 'color': "yellow"},
                           {'range': [80, 90], 'color': "lightgreen"},
                           {'range': [90, 100], 'color': "green"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 85}}
            ))
            fig_impact.update_layout(height=400)
            st.plotly_chart(fig_impact, use_container_width=True)
        
        with col2:
            # Win projection
            current_wins = 41
            projected_wins = current_wins + (improvement * 2.5)  # Rough conversion
            
            st.metric("Current Wins", current_wins)
            st.metric("Projected Wins", f"{projected_wins:.0f}", f"+{projected_wins - current_wins:.0f}")
            
            if projected_wins >= 50:
                st.success("🏆 Title Contender")
            elif projected_wins >= 45:
                st.info("🎯 Playoff Lock")
            elif projected_wins >= 38:
                st.warning("🎲 Play-In Tournament")
            else:
                st.error("🎰 Lottery Team")
            
            # Playoff odds
            playoff_odds = min(95, max(5, (projected_wins - 35) * 5))
            st.write("### Playoff Probability")
            st.progress(playoff_odds / 100)
            st.write(f"{playoff_odds:.0f}% chance")
    else:
        st.info("Select players in the Roster Builder tab to see projections")

# Bottom recommendations
st.markdown("---")
st.subheader("🎯 Strategic Recommendations")

rec_col1, rec_col2, rec_col3 = st.columns(3)

with rec_col1:
    st.info("""
    **💎 Best Values**
    - Target players with 4+ value scores
    - Focus on ages 24-28 for longevity
    - Prioritize two-way players
    """)

with rec_col2:
    st.warning("""
    **⚠️ Market Insights**
    - Guard market is saturated
    - Premium on 3&D wings
    - Centers are undervalued
    """)

with rec_col3:
    st.success("""
    **✅ Recommended Strategy**
    - Sign 1 star + 2-3 role players
    - Keep flexibility for mid-season
    - Maintain cap space for extensions
    """)

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Cap Space: ${available_cap:.1f}M | {your_team}")