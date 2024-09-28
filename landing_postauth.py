import streamlit as st

def landing_postauth(navigate_to):
    st.title("Welcome to Your Dashboard")
    
    if st.toggle('Choose your Mode', False):
        navigate_to('')

    if st.button("Access the App"):
        navigate_to('test')
    
    st.write("More content about the app can be added here.")
