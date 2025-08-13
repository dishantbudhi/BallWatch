import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome Head Coach, {st.session_state.get('first_name', 'Guest')}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('View Scouting Reports',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/31_Scouting_Reports.py')

if st.button('Analyze Lineups',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/32_Lineup_Analysis.py')

if st.button('View Season Summaries',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/33_Season_Summaries.py')

if st.button('Player Matchup Analysis',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/34_Player_Matchup.py')
