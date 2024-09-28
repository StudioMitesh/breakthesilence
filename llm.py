import streamlit as st
from gtts import gTTS

def llm(navigate_to):
    st.title("LLM Output")

    # Retrieve the gesture from session state
    gesture = st.session_state.get('gesture', 'No gesture detected')
    
    # Simulate LLM response
    llm_response = f"LLM response for gesture: {gesture}"
    st.write(llm_response)
    
    # Convert response to speech
    tts = gTTS(llm_response)
    tts.save("output.mp3")
    
    st.audio("output.mp3")
    
    if st.button("Return to Dashboard"):
        navigate_to('post_login')
