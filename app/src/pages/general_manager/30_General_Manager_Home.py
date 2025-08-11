logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome General Manager, {st.session_state.get('first_name', 'Guest')}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('Player Valuation',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/general_manager/31_Player_Valuation.py')

if st.button('Draft Analysis',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/general_manager/32_Draft_Analysis.py')

