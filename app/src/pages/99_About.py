import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

SideBarLinks(show_home=True)

st.write("# About this App")

st.markdown (
    """
    This is our final project app for CS3200.  

    BallWatch transforms NBA analytics into actionable insights for teams and fans. Our platform consolidates game statistics, player performance, and team dynamics into intuitive dashboards. Core features include real-time player stats tracking, lineup optimization analysis, and opponent scouting reports. We serve four key users: superfans seeking deeper insights, data engineers maintaining data integrity, coaches making strategic decisions, and GMs evaluating roster moves. By simplifying complex analytics, BallWatch bridges the gap between raw data and winning decisions.

    Please see our developers below:
    """
        )

st.write("## Meet the Team")

col1, col2, col3 = st.columns(3)

with col1:
    st.image("assets/wes.jpeg", caption="Wesley Chapman", width=200, use_container_width=True)

with col2:
    st.image("assets/drew.jpg", caption="Andrew Dubanowitz", width=200, use_container_width=True)

with col3:
    st.image("assets/vince.jpeg", caption="Vincent Schacknies", width=200, use_container_width=True)

col4, col5 = st.columns(2)

with col4:
    st.image("assets/dishant.jpeg", caption="Dishant Budhi", width=200, use_container_width=True)

with col5:
    st.image("assets/vince.jpeg", caption="Developer 5 Name", width=200, use_container_width=True)