##################################################
# This is the main/entry-point file for the 
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks

# streamlit supports reguarl and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout = 'wide')

# If a user is at this page, we assume they are not 
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false. 
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel. 
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

# set the title of the page and provide a simple prompt. 
logger.info("Loading the Home page of the app")
st.title('BallWatch Basketball Analytics Application')
st.write('\n\n')
st.write('### Select a user to log in:')

# Create a dropdown menu for user selection
user_options = {
    "Johnny Evans - The Superfan": {
        "role": "superfan",
        "first_name": "Johnny",
        "page": "pages/10_Superfan_Home.py", #update this
        "bio": "Johnny Evans (25M) is an avid basketball fan who stays up to date with all his favorite players and teams. He finds typical basketball media sources too surface-level and appreciates an analytical approach to the game. On top of this, he likes to do some sports betting in his free time, and is always looking to find an edge."
    },
    "Mike Lewis - Data Engineer": {
        "role": "data_engineer", 
        "first_name": "Mike",
        "page": "pages/20_Data_Engineer_Home.py", #update this
        "bio": "Mike has a B.S. in Computer Science and 7 years of experience as a data engineer, specializing in real-time data pipelines and sports analytics. He's passionate about basketball and joined BallWatch to help elevate the game through better backend systems. Mike's primary responsibility is to ensure that BallWatch's data infrastructure stays reliable, accurate, and scalable. He manages ingestion from live APIs, updates datasets post-game, and occasionally runs manual queries for analysts or coaches. He also supports feature development by designing new tables or optimizing old ones."
    },
    "Marcus Thompson - Head Coach": {
        "role": "head_coach",
        "first_name": "Marcus", 
        "page": "pages/30_Head_Coach_Home.py", #update this
        "bio": "Marcus Thompson is the new head coach of the Nets, and together with the new GM, he wants to bring analytical basketball to Brooklyn. During his previous head coaching stints, he was often bogged down by dense spreadsheets and large PDF reports that were difficult to digest in between games. To coach effectively, he needs actionable insights and clear recommendations that help him plan strategies and make adjustments on the fly. This approach allows him to communicate confidently with his players while making decisions he knows are backed by solid statistics."
    },
    "Andre Wu - General Manager": {
        "role": "general_manager",
        "first_name": "Andre", 
        "page": "pages/20_Admin_Home.py", #update this
        "bio": "Andre Wu is the new general manager for the Brooklyn Nets. Historically plagued with losing seasons, Brooklyn is tired of losing and has high expectations for Andre Wu in his first season as the organization's general. Andre Wu plans to rely heavily on advanced analytics and statistics to help rebuild the Nets organization."
    }
}

selected_user = st.selectbox(
    "Choose a user:",
    options=list(user_options.keys()),
    index=0
)

# Display bio for selected user
if selected_user:
    user_info = user_options[selected_user]
    st.write("---")
    st.write(f"**About {user_info['first_name']}:**")
    st.write(user_info['bio'])
    st.write("---")

# Login button
if st.button("Login", type='primary', use_container_width=True):
    if selected_user:
        user_info = user_options[selected_user]
        
        # Set session state variables
        st.session_state['authenticated'] = True
        st.session_state['role'] = user_info['role']
        st.session_state['first_name'] = user_info['first_name']
        
        # Log the login action
        logger.info(f"Logging in as {selected_user}")
        
        # Navigate to the appropriate page
        st.switch_page(user_info['page'])