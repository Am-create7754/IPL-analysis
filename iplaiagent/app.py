import streamlit as st
import os
import sys

# Ensure the scripts directory is in path so internal imports work
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.append(SCRIPTS_DIR)

# pyrefly: ignore [missing-import]
from main import load_data
# pyrefly: ignore [missing-import]
from query_engine import handle_query

# Page config
st.set_page_config(
    page_title="IPL AI Agent",
    page_icon="🏏",
    layout="centered"
)

# Custom CSS for Premium Dark Theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0b0f19;
        color: #ffffff;
    }
    
    /* Headers */
    h1 {
        color: #00d2ff;
        text-align: center;
        font-weight: 800;
        background: -webkit-linear-gradient(#00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Avatar colors */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #161b26;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1a2333;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.title("🏏 IPL AI Analyst Engine")
st.markdown("<p style='text-align: center; color: #8892b0; margin-bottom: 2rem;'>Ask me anything about IPL matches, players, and stats from 2008 to 2024!</p>", unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def init_data():
    return load_data()

with st.spinner("Loading IPL Datasets... (This happens only once)"):
    df = init_data()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to the IPL AI Agent! 🏏 Ask me things like:\n- **'Which match had the highest runs?'**\n- **'How many runs were scored in 2020?'**\n- **'Explain match 335982 hinglish'**"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("🤔 Ask a question about IPL..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("🧠 Agent is thinking..."):
            response = handle_query(prompt, df)
            st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
