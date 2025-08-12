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

"""
As a data engineer, I need to UPDATE player and team stats in the database nightly so users always access the most recent analytics. 
As a data engineer, I need to INSERT new rookie player profiles with scouting data so coaches can track them before their NBA debut. 
As a data engineer, I need to DELETE duplicate or erroneous data entries from staging tables so that data integrity is maintained before production loads.
As a data engineer, I need to view data quality validation reports so I can ensure accurate stats are available for analysis.
As a data engineer, I need to monitor system performance metrics so I can identify and fix issues before they affect users.
As a data engineer, I need to DELETE error logs and failed data loads older than 30 days so storage remains optimized.
"""

if st.button('Data Pipelines',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/21_Data_Pipelines.py')

if st.button('System Health',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/22_System_Health.py')

# pick a third user story and add a page