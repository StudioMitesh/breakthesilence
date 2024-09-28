import streamlit as st
from landing_preauth import landing_preauth
from login import login
from landing_postauth import landing_postauth
from streamlit_camera import streamlit_camera
from cv.gestureRecognition import gesture_recognition
from llm import llm

# initialize page state
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'landing'

# page navigation
def navigate_to(page):
    st.session_state['current_page'] = page

# page render selection
if st.session_state['current_page'] == 'landing':
    landing_preauth(navigate_to)
elif st.session_state['current_page'] == 'login':
    login(navigate_to)
elif st.session_state['current_page'] == 'post_login':
    landing_postauth(navigate_to)
elif st.session_state['current_page'] == 'camera':
    streamlit_camera(navigate_to)
elif st.session_state['current_page'] == 'gesture_recognition':
    gesture_recognition(navigate_to)
elif st.session_state['current_page'] == 'llm_output':
    llm(navigate_to)
