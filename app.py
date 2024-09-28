import streamlit as st
from landing_preauth import landing_preauth
from login import login
from landing_postauth import landing_postauth
from camera import camera
from llm import llm

# Initialize session state to track page
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'landing'

# Page navigation logic
def navigate_to(page):
    st.session_state['current_page'] = page
    st.experimental_rerun()

# Page display based on current state
if st.session_state['current_page'] == 'landing':
    landing_page(navigate_to)
elif st.session_state['current_page'] == 'login':
    login_page(navigate_to)
elif st.session_state['current_page'] == 'post_login':
    post_login_page(navigate_to)
elif st.session_state['current_page'] == 'camera':
    camera_page(navigate_to)
elif st.session_state['current_page'] == 'llm_output':
    llm_output_page(navigate_to)
