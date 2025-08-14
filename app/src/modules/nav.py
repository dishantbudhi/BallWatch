# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has function to add certain functionality to the left side bar of the app

import streamlit as st


#### ------------------------ General ------------------------
def HomeNav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def AboutPageNav():
    st.sidebar.page_link("pages/99_About.py", label="About", icon="🧠")


#### ------------------------ Examples for Role of pol_strat_advisor ------------------------
def PolStratAdvHomeNav():
    st.sidebar.page_link(
        "pages/00_Pol_Strat_Home.py", label="Political Strategist Home", icon="👤"
    )


def WorldBankVizNav():
    st.sidebar.page_link(
        "pages/01_World_Bank_Viz.py", label="World Bank Visualization", icon="🏦"
    )


def MapDemoNav():
    st.sidebar.page_link("pages/02_Map_Demo.py", label="Map Demonstration", icon="🗺️")


## ------------------------ Examples for Role of usaid_worker ------------------------
def ApiTestNav():
    st.sidebar.page_link("pages/12_API_Test.py", label="Test the API", icon="🛜")


def PredictionNav():
    st.sidebar.page_link(
        "pages/11_Prediction.py", label="Regression Prediction", icon="📈"
    )


def ClassificationNav():
    st.sidebar.page_link(
        "pages/13_Classification.py", label="Classification Demo", icon="🌺"
    )


#### ------------------------ System Admin Role ------------------------
def AdminPageNav():
    st.sidebar.page_link("pages/20_Admin_Home.py", label="System Admin", icon="🖥️")
    st.sidebar.page_link(
        "pages/21_ML_Model_Mgmt.py", label="ML Model Management", icon="🏢"
    )


def SuperfanNav():
    """Sidebar links for the Superfan persona."""
    st.sidebar.page_link("pages/10_Superfan_Home.py", label="Superfan Home", icon="🏀")
    st.sidebar.page_link("pages/11_Player_Finder.py", label="Player Finder", icon="🔎")
    st.sidebar.page_link("pages/12_Player_Comparison.py", label="Compare Players", icon="⚖️")
    st.sidebar.page_link("pages/13_Historical_Game_Results.py", label="Game Results", icon="📊")


def DataEngineerNav():
    """Sidebar links for the Data Engineer persona."""
    st.sidebar.page_link("pages/20_Data_Engineer_Home.py", label="Data Engineer Home", icon="🛠️")
    st.sidebar.page_link("pages/21_Data_Pipelines.py", label="Data Pipelines", icon="🔁")
    st.sidebar.page_link("pages/22_System_Health.py", label="System Health", icon="❤️")
    st.sidebar.page_link("pages/23_Data_Cleanup.py", label="Data Cleanup", icon="🧹")


def HeadCoachNav():
    """Sidebar links for the Head Coach persona."""
    st.sidebar.page_link("pages/30_Head_Coach_Home.py", label="Head Coach Home", icon="🎯")
    st.sidebar.page_link("pages/31_Scouting_Reports.py", label="Scouting Reports", icon="📝")
    st.sidebar.page_link("pages/32_Lineup_Analysis.py", label="Lineup Analysis", icon="🧩")
    st.sidebar.page_link("pages/33_Season_Summaries.py", label="Season Summaries", icon="📚")
    st.sidebar.page_link("pages/34_Player_Matchup.py", label="Player Matchup", icon="🤼")


def GeneralManagerNav():
    """Sidebar links for the General Manager persona."""
    st.sidebar.page_link("pages/40_General_Manager_Home.py", label="General Manager Home", icon="🏢")
    st.sidebar.page_link("pages/41_Player_Progress.py", label="Player Progress", icon="📈")
    st.sidebar.page_link("pages/42_Draft_Rankings.py", label="Draft Rankings", icon="🧾")
    st.sidebar.page_link("pages/43_Contract_Efficiency.py", label="Contract Efficiency", icon="💼")


# --------------------------------Links Function -----------------------------------------------
def SideBarLinks(show_home=False):
    """
    This function handles adding links to the sidebar of the app based upon the logged-in user's role, which was put in the streamlit session_state object when logging in.
    """

    # add a logo to the sidebar always
    st.sidebar.image("assets/logo.png", width=150)

    # If there is no logged in user, redirect to the Home (Landing) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        # Show the Home page link (the landing page)
        HomeNav()

    # Show the other page navigators depending on the users' role.
    if st.session_state["authenticated"]:

        # Show World Bank Link and Map Demo Link if the user is a political strategy advisor role.
        if st.session_state["role"] == "pol_strat_advisor":
            PolStratAdvHomeNav()
            WorldBankVizNav()
            MapDemoNav()

        # If the user role is usaid worker, show the Api Testing page
        if st.session_state["role"] == "usaid_worker":
            PredictionNav()
            ApiTestNav()
            ClassificationNav()

        # If the user is an administrator, give them access to the administrator pages
        if st.session_state["role"] == "administrator":
            AdminPageNav()

        # Persona-specific tabs
        if st.session_state.get("role") == "superfan":
            SuperfanNav()

        if st.session_state.get("role") == "data_engineer":
            DataEngineerNav()

        if st.session_state.get("role") == "head_coach":
            HeadCoachNav()

        if st.session_state.get("role") == "general_manager":
            GeneralManagerNav()

    # Show the About page only when no user is logged in
    if not st.session_state.get("authenticated", False):
        AboutPageNav()

    if st.session_state["authenticated"]:
        # Always show a logout button if there is a logged in user
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
