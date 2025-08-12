import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome General Manager, {st.session_state.get('first_name', 'Guest')}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('Track Player Progress',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/41_Player_Progress.py')

if st.button('Update Draft Rankings',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/42_Draft_Rankings.py')

if st.button('Analyze Contract Efficiency',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/43_Contract_Efficiency.py')