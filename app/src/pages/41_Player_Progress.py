####subpage 1

logger = logging.getLogger(__name__)

Python
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()
st.title('Player Valuation')
st.write("This page will be used to assess player value and potential.")
# Add your player valuation code here