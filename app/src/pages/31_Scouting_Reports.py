import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()
st.title('Opponent Scouting Reports')
st.write("This page will provide comprehensive scouting reports on opponents.")