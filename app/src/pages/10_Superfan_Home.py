import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome Super Fan, {st.session_state.get('first_name', 'Guest')}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('Player Comparison',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/12_Player_Comparison.py')

if st.button('Player Stats',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/11_Player_Finder.py')
