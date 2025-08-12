logger = logging.getLogger(__name__)

Python
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()
st.title('Draft Analysis')
st.write("This page will provide tools for draft analysis and player evaluation.")
# Add your draft analysis code here