import logging
logger = logging.getLogger(__name__)
import streamlit as st
from modules.nav import SideBarLinks

"""Data Engineer home: pipeline and DB tools."""

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome Data Engineer, {st.session_state.get('first_name', 'Guest')}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

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
</style>
''', unsafe_allow_html=True)

cards = [
    {'title': 'Data Pipelines', 'desc': 'Monitor and manage ETL pipelines, view recent runs and failures.', 'page': 'pages/21_Data_Pipelines.py', 'emoji': '🔁', 'color': '#84CC16'},
    {'title': 'System Health', 'desc': 'Inspect system health metrics and alerts for data infrastructure.', 'page': 'pages/22_System_Health.py', 'emoji': '❤️', 'color': '#0369A1'},
    {'title': 'Data Cleanup', 'desc': 'Run cleanup jobs and review data quality reports.', 'page': 'pages/23_Data_Cleanup.py', 'emoji': '🧹', 'color': '#F97316'}
]

cols = st.columns(len(cards))
for i, card in enumerate(cards):
    with cols[i]:
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
        if st.button(f"Open {card['title']}", key=f"de_open_{i}"):
            st.switch_page(card['page'])