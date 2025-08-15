import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome Superfan, {st.session_state.get('first_name', 'Guest')}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

# Unified CSS for persona pages (consistent look & feel)
st.markdown('''
<style>
.card {
  border: 1px solid #E6E6E6;
  border-radius: 12px;
  padding: 16px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfbff 100%);
  box-shadow: 0 6px 18px rgba(16,24,40,0.06);
  min-height: 150px;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
}
.card-header { display:flex; align-items:center; gap:8px; }
.card-title { font-weight:700; font-size:18px; margin:0; }
.card-desc { color:#475569; margin-top:8px; margin-bottom:12px; }
.card-cta { margin-top:8px; }
</style>
''', unsafe_allow_html=True)

cards = [
    {'title': 'Player Comparison', 'desc': 'Compare player statistics side-by-side with visualizations and metrics.', 'page': 'pages/12_Player_Comparison.py', 'emoji': '⚖️', 'color': '#7C3AED'},
    {'title': 'Player Finder', 'desc': 'Search and filter players by attributes to discover hidden gems.', 'page': 'pages/11_Player_Finder.py', 'emoji': '🔎', 'color': '#0891B2'},
    {'title': 'Game Analysis', 'desc': 'Explore historical game results and performance trends.', 'page': 'pages/13_Historical_Game_Results.py', 'emoji': '📊', 'color': '#F59E0B'}
]

cols = st.columns(len(cards))
for i, card in enumerate(cards):
    with cols[i]:
        # Card container with a colored accent at the top
        st.markdown(f"""
        <div class='card' style='border-top:4px solid {card['color']}'>
          <div class='card-header'>
            <div class='card-emoji'>{card['emoji']}</div>
            <div>
              <div class='card-title'>{card['title']}</div>
              <div class='card-desc'>{card['desc']}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # spacer between card and button
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

        if st.button(f"Open {card['title']}", key=f"sf_open_{i}"):
            st.switch_page(card['page'])
