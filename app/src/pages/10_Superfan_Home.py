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

if st.button('View Player Stats',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/11_Player_Stats.py')

if st.button('Player Comparisons',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/12_Player_Comparison.py')

if st.button('Historical Game Results',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/13_Historical_Game_Results.py')