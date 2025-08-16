# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has function to add certain functionality to the left side bar of the app

import streamlit as st


#### ------------------------ General ------------------------
def HomeNav():
    st.sidebar.page_link("Home.py", label="Home")
    
def AboutNav():
    st.sidebar.page_link("pages/99_About.py", label="About")

def SuperfanNav():
    """Sidebar links for the Superfan persona."""
    st.sidebar.page_link("pages/10_Superfan_Home.py", label="Home")
    st.sidebar.page_link("pages/11_Player_Finder.py", label="Player Finder")
    st.sidebar.page_link("pages/12_Player_Comparison.py", label="Compare Players")
    st.sidebar.page_link("pages/13_Historical_Game_Results.py", label="Game Results")


def DataEngineerNav():
    """Sidebar links for the Data Engineer persona."""
    st.sidebar.page_link("pages/20_Data_Engineer_Home.py", label="Home")
    st.sidebar.page_link("pages/21_Data_Pipelines.py", label="Data Pipelines")
    st.sidebar.page_link("pages/22_System_Health.py", label="System Health")
    st.sidebar.page_link("pages/23_Data_Cleanup.py", label="Data Cleanup")


def HeadCoachNav():
    """Sidebar links for the Head Coach persona."""
    st.sidebar.page_link("pages/30_Head_Coach_Home.py", label="Home")
    st.sidebar.page_link("pages/31_Scouting_Reports.py", label="Scouting & Game Planning")
    st.sidebar.page_link("pages/32_Lineup_and_Situational.py", label="Lineup & Situational")
    st.sidebar.page_link("pages/33_Player_Matchup.py", label="Player Matchup")


def GeneralManagerNav():
    """Sidebar links for the General Manager persona."""
    st.sidebar.page_link("pages/40_General_Manager_Home.py", label="Home")
    st.sidebar.page_link("pages/41_Player_Progress.py", label="Player Progress")
    st.sidebar.page_link("pages/42_Draft_Rankings.py", label="Draft Rankings")
    st.sidebar.page_link("pages/43_Contract_Efficiency.py", label="Contract Efficiency")


# --------------------------------Links Function -----------------------------------------------
def SideBarLinks(show_home=False):
    """Add persona-based links and basic auth handling to the sidebar."""

    # add a logo to the sidebar
    st.sidebar.image("assets/logo.png", width=150)

    # ensure authenticated flag exists
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if show_home:
        HomeNav()
        AboutNav()

    if st.session_state.get("authenticated"):
        if st.session_state.get("role") in ("administrator", "data_engineer"):
            DataEngineerNav()
        if st.session_state.get("role") == "superfan":
            SuperfanNav()
        if st.session_state.get("role") == "head_coach":
            HeadCoachNav()
        if st.session_state.get("role") == "general_manager":
            GeneralManagerNav()

    if st.session_state.get("authenticated"):
        if st.sidebar.button("Logout"):
            st.session_state.pop("role", None)
            st.session_state.pop("authenticated", None)
            st.session_state.pop("user_id", None)
            st.session_state.pop("username", None)
            st.switch_page("Home.py")
