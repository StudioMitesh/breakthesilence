import streamlit as st

def landing_postauth(navigate_to):
    st.title("Welcome to Your Dashboard")
    
    if st.button("Access the App"):
        navigate_to('camera')
    
    st.write("More content about the app can be added here.")
