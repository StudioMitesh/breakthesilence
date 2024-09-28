import streamlit as st

def login(navigate_to):
    st.title("Log In")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Log In"):
        # Simulate a successful login for demo purposes
        st.session_state['logged_in'] = True
        navigate_to('post_login')
    
    if st.button("Log In with Google"):
        st.write("Google login is not yet implemented.")
