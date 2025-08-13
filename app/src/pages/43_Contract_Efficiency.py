import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()
st.title('Contract Efficiency & Free Agency Management')

BASE_URL = "http://api:4000"

def make_request(endpoint, method='GET', data=None):
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == 'GET':
            response = requests.get(url)
        elif method == 'PUT':
            response = requests.put(url, json=data)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# Load data
if st.button("Load Free Agent Data"):
    # Load players data
    players_data = make_request("/basketball/players")
    if players_data and 'players' in players_data:
        st.session_state['players'] = players_data['players']
        
    # Load evaluations for contract efficiency analysis
    eval_data = make_request("/strategy/draft-evaluations")
    if eval_data and 'evaluations' in eval_data:
        st.session_state['evaluations'] = eval_data['evaluations']
        st.success(f"Loaded {len(eval_data['evaluations'])} player evaluations")

# Salary cap settings
SALARY_CAP = 136.0
LUXURY_TAX = 165.0
CURRENT_PAYROLL = 118.5
available_cap = SALARY_CAP - CURRENT_PAYROLL
luxury_room = LUXURY_TAX - CURRENT_PAYROLL

# Main content
if 'evaluations' in st.session_state:
    evaluations = st.session_state['evaluations']
    df = pd.DataFrame(evaluations)
    
    # Add estimated salary based on rating
    if not df.empty and 'overall_rating' in df.columns:
        # Convert ratings to numeric
        df['overall_rating'] = pd.to_numeric(df['overall_rating'], errors='coerce').fillna(50)
        df['offensive_rating'] = pd.to_numeric(df.get('offensive_rating', 50), errors='coerce').fillna(50)
        df['defensive_rating'] = pd.to_numeric(df.get('defensive_rating', 50), errors='coerce').fillna(50)
        df['potential_rating'] = pd.to_numeric(df.get('potential_rating', 50), errors='coerce').fillna(50)
        
        # Estimate salary based on rating (simplified formula)
        df['estimated_salary'] = (df['overall_rating'] * 0.5).round(1)
        df['value_score'] = (df['overall_rating'] / (df['estimated_salary'] + 1)).round(2)
        df['contract_efficiency'] = df['value_score'].apply(
            lambda x: 'Excellent' if x > 5 else ('Good' if x > 3 else ('Fair' if x > 2 else 'Poor'))
        )
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Available Players", len(df))
        
        with col2:
            st.metric("Cap Space", f"${available_cap:.1f}M")
        
        with col3:
            high_value = len(df[df['value_score'] >= 4])
            st.metric("High Value Players", high_value)
        
        with col4:
            affordable = len(df[df['estimated_salary'] <= available_cap])
            st.metric("Affordable Options", affordable)
        
        # Tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs(["Contract Values", "Market Analysis", "Player Comparison", "Signing Strategy"])
        
        with tab1:
            st.header("Contract Value Analysis")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Value scatter plot
                fig = px.scatter(
                    df,
                    x='estimated_salary',
                    y='overall_rating',
                    color='value_score',
                    size='potential_rating',
                    hover_data=['first_name', 'last_name', 'position'],
                    title="Player Value vs Estimated Contract",
                    labels={
                        'estimated_salary': 'Estimated Salary ($M)',
                        'overall_rating': 'Overall Rating',
                        'value_score': 'Value Score'
                    },
                    color_continuous_scale='RdYlGn'
                )
                
                # Add value zones
                fig.add_shape(
                    type="rect", x0=0, y0=75, x1=available_cap, y1=100,
                    fillcolor="green", opacity=0.1,
                    line=dict(color="green", width=2, dash="dash")
                )
                fig.add_annotation(
                    x=available_cap/2, y=85, 
                    text="Target Zone", 
                    showarrow=False,
                    font=dict(color="green", size=12)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Best Values")
                
                best_values = df.nlargest(5, 'value_score')
                for _, player in best_values.iterrows():
                    with st.container():
                        st.success(f"""
                        **{player['first_name']} {player['last_name']}**
                        - Position: {player.get('position', 'N/A')}
                        - Rating: {player['overall_rating']:.0f}
                        - Est. Salary: ${player['estimated_salary']:.1f}M
                        - Value: {player['value_score']:.2f}
                        """)
            
            # Value rankings table
            st.subheader("Contract Efficiency Rankings")
            
            efficiency_table = df.nlargest(10, 'value_score')[
                ['first_name', 'last_name', 'position', 'overall_rating', 
                 'estimated_salary', 'value_score', 'contract_efficiency']
            ].copy()
            
            st.dataframe(
                efficiency_table.style.format({
                    'estimated_salary': '${:.1f}M',
                    'overall_rating': '{:.0f}',
                    'value_score': '{:.2f}'
                }).background_gradient(subset=['value_score'], cmap='RdYlGn'),
                use_container_width=True
            )
        
        with tab2:
            st.header("Free Agent Market Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Position market analysis
                if 'position' in df.columns:
                    position_stats = df.groupby('position').agg({
                        'overall_rating': 'mean',
                        'estimated_salary': 'mean',
                        'value_score': 'mean'
                    }).round(1)
                    
                    fig_pos = px.bar(
                        position_stats,
                        x=position_stats.index,
                        y='value_score',
                        color='overall_rating',
                        title="Average Value Score by Position",
                        labels={'index': 'Position', 'value_score': 'Average Value Score'},
                        color_continuous_scale='YlOrRd'
                    )
                    st.plotly_chart(fig_pos, use_container_width=True)
            
            with col2:
                # Rating distribution
                fig_rating = px.histogram(
                    df,
                    x='overall_rating',
                    nbins=15,
                    title="Player Rating Distribution",
                    labels={'overall_rating': 'Overall Rating', 'count': 'Number of Players'}
                )
                st.plotly_chart(fig_rating, use_container_width=True)
            
            # Salary vs Rating correlation
            st.subheader("Market Rate Analysis")
            
            fig_correlation = px.scatter(
                df,
                x='overall_rating',
                y='estimated_salary',
                color='position' if 'position' in df.columns else None,
                title="Rating vs Estimated Salary",
                labels={'overall_rating': 'Overall Rating', 'estimated_salary': 'Estimated Salary ($M)'}
            )
            
            # Add manual trend line
            if len(df) > 1:
                x_min, x_max = df['overall_rating'].min(), df['overall_rating'].max()
                y_min, y_max = df['estimated_salary'].min(), df['estimated_salary'].max()
                
                fig_correlation.add_trace(
                    go.Scatter(
                        x=[x_min, x_max],
                        y=[y_min, y_max],
                        mode='lines',
                        line=dict(dash='dash', color='red'),
                        name='Trend',
                        showlegend=False
                    )
                )
            
            st.plotly_chart(fig_correlation, use_container_width=True)
        
        with tab3:
            st.header("Player Comparison Tool")
            
            # Multi-select for comparison
            player_options = {}
            for _, player in df.iterrows():
                display_name = f"{player['first_name']} {player['last_name']} ({player.get('position', 'N/A')})"
                player_options[display_name] = player
            
            selected_players = st.multiselect(
                "Select Players to Compare:",
                options=list(player_options.keys()),
                max_selections=5
            )
            
            if selected_players:
                comparison_data = []
                
                for player_name in selected_players:
                    player = player_options[player_name]
                    comparison_data.append({
                        'Player': f"{player['first_name']} {player['last_name']}",
                        'Position': player.get('position', 'N/A'),
                        'Overall': player['overall_rating'],
                        'Offense': player['offensive_rating'],
                        'Defense': player['defensive_rating'],
                        'Potential': player['potential_rating'],
                        'Est. Salary': player['estimated_salary'],
                        'Value Score': player['value_score']
                    })
                
                comparison_df = pd.DataFrame(comparison_data)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Comparison table
                    st.dataframe(
                        comparison_df.style.format({
                            'Est. Salary': '${:.1f}M',
                            'Overall': '{:.0f}',
                            'Offense': '{:.0f}',
                            'Defense': '{:.0f}',
                            'Potential': '{:.0f}',
                            'Value Score': '{:.2f}'
                        }).background_gradient(subset=['Value Score'], cmap='RdYlGn'),
                        use_container_width=True
                    )
                
                with col2:
                    # Radar chart comparison
                    fig_radar = go.Figure()
                    
                    for _, player in comparison_df.iterrows():
                        fig_radar.add_trace(go.Scatterpolar(
                            r=[player['Overall'], player['Offense'], player['Defense'], player['Potential']],
                            theta=['Overall', 'Offense', 'Defense', 'Potential'],
                            fill='toself',
                            name=player['Player']
                        ))
                    
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 100])
                        ),
                        title="Player Comparison Radar"
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
        
        with tab4:
            st.header("Contract Signing Strategy")
            
            # Budget allocation
            st.subheader("Budget Allocation")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **Current Financial Status**
                - Salary Cap: ${SALARY_CAP:.1f}M
                - Current Payroll: ${CURRENT_PAYROLL:.1f}M
                - Available Cap Space: ${available_cap:.1f}M
                - Room to Luxury Tax: ${luxury_room:.1f}M
                """)
            
            with col2:
                # Contract simulator
                st.subheader("Contract Simulator")
                
                if player_options:
                    selected_player = st.selectbox(
                        "Player to Sign:",
                        options=list(player_options.keys())
                    )
                    
                    if selected_player:
                        player = player_options[selected_player]
                        
                        offered_salary = st.slider(
                            "Offer Amount ($M)",
                            min_value=1.0,
                            max_value=min(50.0, available_cap),
                            value=float(player['estimated_salary']),
                            step=0.5
                        )
                        
                        contract_years = st.slider("Contract Years", 1, 5, 3)
                        
                        total_value = offered_salary * contract_years
                        
                        st.success(f"""
                        **Contract Offer**
                        - Player: {player['first_name']} {player['last_name']}
                        - Annual: ${offered_salary:.1f}M
                        - Total: ${total_value:.1f}M
                        - Cap Impact: ${offered_salary:.1f}M
                        """)
                        
                        # Fit analysis
                        if offered_salary <= available_cap:
                            remaining_cap = available_cap - offered_salary
                            st.success(f"Fits in cap space. Remaining: ${remaining_cap:.1f}M")
                        else:
                            st.error(f"Exceeds cap by ${offered_salary - available_cap:.1f}M")
            
            # Signing recommendations
            st.subheader("Strategic Recommendations")
            
            rec_col1, rec_col2, rec_col3 = st.columns(3)
            
            with rec_col1:
                # High value targets
                high_value_players = df[df['value_score'] >= 4].nlargest(3, 'overall_rating')
                
                st.success("**High Value Targets**")
                for _, player in high_value_players.iterrows():
                    st.write(f"• {player['first_name']} {player['last_name']} - {player['value_score']:.2f}")
            
            with rec_col2:
                # Position needs
                affordable_players = df[df['estimated_salary'] <= available_cap]
                position_counts = affordable_players['position'].value_counts() if 'position' in affordable_players.columns else pd.Series()
                
                st.info("**Available by Position**")
                for pos, count in position_counts.head(5).items():
                    st.write(f"• {pos}: {count} players")
            
            with rec_col3:
                # Budget strategy
                st.warning("**Budget Strategy**")
                st.write(f"• Max signing: ${available_cap:.1f}M")
                st.write(f"• Multiple targets: 2-3 players")
                st.write(f"• Reserve: ${max(5, available_cap * 0.2):.1f}M")
    else:
        st.warning("No rating data available for contract analysis.")

else:
    st.info("Click 'Load Free Agent Data' to begin contract efficiency analysis.")
    
    # Show expected data structure
    st.subheader("Expected Data Structure")
    st.code("""
    Contract analysis requires:
    - Player identification (first_name, last_name, position)
    - Performance ratings (overall_rating, offensive_rating, defensive_rating)
    - Potential rating for future value assessment
    - Market value estimation based on performance
    """)

# Footer with key insights
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Available Cap Space: ${available_cap:.1f}M")