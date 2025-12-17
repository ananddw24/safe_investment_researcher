import streamlit as st
import os
from dotenv import load_dotenv
from advisor_agent import AdvisorAgent

# Page Configuration
st.set_page_config(
    page_title="Investment Advisor Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    with open("styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = None

# Sidebar - Configuration
with st.sidebar:
    st.title("Settings")
    
    # API Key Handling
    load_dotenv()
    env_key = os.getenv("GOOGLE_API_KEY")
    
    api_key_input = st.text_input(
        "Google AI API Key", 
        value=env_key if env_key else "",
        type="password",
        help="Get your key from Google AI Studio"
    )

    # Country Selection
    country = st.selectbox(
        "Select Your Country",
        ["United States", "United Kingdom", "Canada", "Australia", "India", "Germany", "France", "Japan", "Brazil", "Other (Global)"],
        index=0,
        help="Customize advice for your local regulations and assets."
    )

    # Model Selection (Free Tier Optimization)
    model_name = st.selectbox(
        "Select AI Model",
        ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemma-3-12b"],
        index=0,
        help="Use 'Flash-Lite' for fastest response, 'Flash' for balance. All optimized for free tier."
    )
    
    if api_key_input:
        # Check if agent needs re-initialization (if key, country, or model changed)
        # Simplify check logic for readability
        settings_changed = (
            "agent_country" not in st.session_state or 
            st.session_state.agent_country != country or
            "agent_model" not in st.session_state or
            st.session_state.agent_model != model_name
        )

        if settings_changed:
            if st.button("Initialize Advisor with Settings"):
                agent = AdvisorAgent(api_key_input, country, model_name)
                if agent.validate_api_key():
                    st.session_state.agent = agent
                    st.session_state.agent_country = country
                    st.session_state.agent_model = model_name
                    st.success(f"Advisor Configured!\nCountry: {country}\nModel: {model_name}")
                    # Clear history on re-init
                    st.session_state.messages = []
                else:
                    st.error("Invalid API Key")
        elif st.session_state.agent is None:
             if st.button("Connect Advisor"):
                agent = AdvisorAgent(api_key_input, country, model_name)
                if agent.validate_api_key():
                    st.session_state.agent = agent
                    st.session_state.agent_country = country
                    st.session_state.agent_model = model_name
                    st.success(f"Advisor Connected!")
                else:
                    st.error("Invalid API Key")

    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("Specialized AI Investment Advisor for budgets of **$10 - $50 / day**.")
    st.markdown("Powered by **Google Gemini**.")


# Main Chat Interface
st.title("📈 Strategic Investment Advisor")
st.markdown("Ask me how to invest your daily budget optimally.")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("I have $20/day, what's a good strategy?"):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Convert to Agent Response
    if st.session_state.agent:
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            # Stream the response
            try:
                for chunk in st.session_state.agent.ask(prompt):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                
                # Add to history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Error generating response: {e}")
    else:
        with st.chat_message("assistant"):
            st.warning("Please enter your Google API Key in the sidebar to start.")

