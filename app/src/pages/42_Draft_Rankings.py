import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()
st.title('Draft Rankings & Player Evaluations')

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

st.header("Update Player Evaluation")

if st.button("Load Current Rankings"):
    data = make_request("/api/draft-evaluations")
    if data and 'evaluations' in data:
        st.session_state['evaluations'] = data['evaluations']
        st.success(f"Loaded {len(data['evaluations'])} player evaluations")

if 'evaluations' in st.session_state:
    evaluations = st.session_state['evaluations']
    
    player_options = {}
    for eval in evaluations:
        display_name = f"{eval['first_name']} {eval['last_name']} ({eval['position']}) - Rating: {eval['overall_rating']}"
        player_options[display_name] = eval
    
    selected_player = st.selectbox(
        "Select Player to Update:",
        options=list(player_options.keys())
    )
    
    if selected_player:
        current = player_options[selected_player]
        
        st.subheader(f"Updating: {current['first_name']} {current['last_name']}")
        
        # Rating sliders
        col1, col2 = st.columns(2)
        
        with col1:
            overall_rating = st.slider("Overall Rating", 0, 100, 
                int(float(current.get('overall_rating', 50))))
            offensive_rating = st.slider("Offensive Rating", 0, 100, 
                int(float(current.get('offensive_rating', 50))))
            
        with col2:
            defensive_rating = st.slider("Defensive Rating", 0, 100, 
                int(float(current.get('defensive_rating', 50))))
            potential_rating = st.slider("Potential Rating", 0, 100, 
                int(float(current.get('potential_rating', 50))))
        
        strengths = st.text_area("Strengths", value=current.get('strengths', ''))
        weaknesses = st.text_area("Weaknesses", value=current.get('weaknesses', ''))
        scout_notes = st.text_area("Scout Notes", value=current.get('scout_notes', ''))
        
        if st.button("Update Evaluation", type="primary"):
            update_data = {
                "overall_rating": overall_rating,
                "offensive_rating": offensive_rating,
                "defensive_rating": defensive_rating,
                "potential_rating": potential_rating,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "scout_notes": scout_notes
            }
            
            result = make_request(f"/api/draft-evaluations/{current['evaluation_id']}", 
                                method='PUT', data=update_data)
            
            if result:
                st.success("Evaluation updated successfully!")
                # Clear cached data to force reload
                if 'evaluations' in st.session_state:
                    del st.session_state['evaluations']
                st.rerun()