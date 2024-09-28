import streamlit as st

def landing_preauth(navigate_to):
    st.title("Welcome to the Gesture-Based Communication App")
    
    if st.button("Log In"):
        navigate_to('login')
    
    if st.button("View Documentation"):
        st.write("This is where you explain how the app works.")
