import logging
logger = logging.getLogger(__name__)
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome Data Engineer, {st.session_state.get('first_name', 'Guest')}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('Data Pipelines',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/21_Data_Pipelines.py')

if st.button('System Health',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/22_System_Health.py')

if st.button('Data Logs and Cleanup',
                type='primary',
                use_container_width=True):
        st.switch_page('pages/23_Data_Cleanup.py')