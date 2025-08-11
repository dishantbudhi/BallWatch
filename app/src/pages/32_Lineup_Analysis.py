import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()
st.title('Lineup Effectiveness Analysis')
st.write("This page will analyze the effectiveness of different lineups.")