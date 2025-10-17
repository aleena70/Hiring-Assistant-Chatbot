"""
Main Streamlit application for the TalentScout Hiring Assistant.
We build the user interface and handle the conversation flow.

To run the app, navigate to this folder in your terminal and type:
streamlit run app.py
"""

import streamlit as st
import os
import sys
from datetime import datetime

# To make sure Python can find our other project files in their folders.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our custom-built modules.
from chatbot import HiringAssistant
from utils.data_handler import DataHandler

# --- Page & Style Configuration ---
# Browser tab 
st.set_page_config(
    page_title="TalentScout AI - Hiring Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS 
# We're hiding the default Streamlit header/footer for a cleaner look.
st.markdown("""
<style>
   
    header[data-testid="stHeader"], footer {
        visibility: hidden;
    }
    
    /* text color. */
    html, body, [class*="st-"], div, p, span, label, h1, h2, h3, h4, h5, h6 {
        color: #000 !important;
    }

    /* app background. */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #000 !important;
    }

    /*  chat bubbles  */
    div[data-testid="stChatMessageContent"] {
        background-color: white !important;
        border-radius: 15px !important;
        padding: 15px !important;
        color: #000 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
    }

    /* Removing default container around chat messages */
    div[data-testid="stChatMessage"] {
        background: none !important;
        box-shadow: none !important;
    }

    /* main header at the top of the page. */
    .main-header {
        background: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        color: #000 !important;
        font-family: 'Poppins', sans-serif;
    }

    /* sidebar */
    section[data-testid="stSidebar"] {
        background-color: white !important;
        color: #000 !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }

    section[data-testid="stSidebar"] * {
        color: #000 !important;
    }

    /* chat input box */
    div[data-testid="stChatInput"] {
        background-color: white !important;
        color: #000 !important;
        border-radius: 10px !important;
        border: 1px solid #ccc !important;
        padding: 8px !important;
    }

    textarea, input, .stTextInput>div>div>input {
        background-color: white !important;
        color: #000 !important;
        border: 1px solid #ccc !important;
    }

    /* General button styling. */
    button, [role="button"] {
        color: #000 !important;
        border-radius: 8px !important;
        border: none !important;
    }

    div[data-testid="stSidebar"] button:hover {
        background-color: #bfdbfe !important;
    }

    /* Progress bar color. */
    .stProgress > div > div > div {
        background-color: #000 !important;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """
    This function sets up our app's "memory" for each user session.
    It makes sure we have a place to store messages, the chatbot instance, etc.
    """
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = HiringAssistant()
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    if 'data_handler' not in st.session_state:
        st.session_state.data_handler = DataHandler()
    if 'conversation_ended' not in st.session_state:
        st.session_state.conversation_ended = False


def display_progress():
    """
    A function to show the candidate's progress in the sidebar.
    It updates in real-time as they provide information
    """
    st.sidebar.title(" Interview Progress")

    # Only show progress if we've actually started collecting data.
    if st.session_state.chatbot.candidate_data:
        data = st.session_state.chatbot.candidate_data

        st.sidebar.subheader("Collected Info:")

        # Check for each piece of info and show a checkmark if we have it.
        if 'name' in data:
            st.sidebar.success(f"✅ Name: {data['name']}")
        else:
            st.sidebar.info("⏳ Name")

        if 'email' in data:
            st.sidebar.success(f"✅ Email: {data['email']}")
        else:
            st.sidebar.info("⏳ Email")

        if 'phone' in data:
            st.sidebar.success(f"✅ Phone: {data['phone']}")
        else:
            st.sidebar.info("⏳ Phone")

        if 'experience' in data:
            st.sidebar.success(f"✅ Experience: {data['experience']}")
        else:
            st.sidebar.info("⏳ Experience")

        if 'position' in data:
            st.sidebar.success(f"✅ Position: {data['position']}")
        else:
            st.sidebar.info("⏳ Position")

        if 'location' in data:
            st.sidebar.success(f"✅ Location: {data['location']}")
        else:
            st.sidebar.info("⏳ Location")

        if 'techstack' in data:
            st.sidebar.success(f"✅ Tech Stack: {data['techstack']}")
        else:
            st.sidebar.info("⏳ Tech Stack")

        # For the technical questions, a progress bar.
        if 'questions' in data:
            answered = len(data.get('answers', []))
            total = len(data['questions'])
            st.sidebar.subheader("Technical Questions:")
            st.sidebar.progress(answered / total if total > 0 else 0)
            st.sidebar.write(f"{answered} of {total} answered")

    st.sidebar.markdown("---")
    st.sidebar.info(" Feel free to type 'bye' or 'exit' to end the chat anytime.")


# --- Main Application Logic ---
def main():
    """Streamlit app."""
    
    # Session memory 
    initialize_session_state()

    # Display the main header.
    st.markdown("""
        <div class="main-header">
            <h1> TalentScout AI</h1>
            <p>Your Intelligent Hiring Assistant</p>
            <p>Powered by AI Agents • RAG-Enhanced • Secure</p>
        </div>
    """, unsafe_allow_html=True)

    # Welcome message from our chatbot
    if not st.session_state.conversation_started:
        welcome_message = st.session_state.chatbot.start_conversation()
        st.session_state.messages.append({"role": "assistant", "content": welcome_message})
        st.session_state.conversation_started = True

    # Display all the messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # text color 
            st.write(f"<span style='color:black'>{message['content']}</span>", unsafe_allow_html=True)

    # Chat input box
    if not st.session_state.conversation_ended:
        user_input = st.chat_input("Type your message here...")

        if user_input:
            # Add the user's message to our chat history.
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Check if the user wants to end the conversation.
            exit_keywords = ['bye', 'exit', 'quit', 'goodbye', 'end', 'stop']
            if any(keyword in user_input.lower() for keyword in exit_keywords):
                farewell = st.session_state.chatbot.end_conversation()
                st.session_state.messages.append({"role": "assistant", "content": farewell})

                # Save data
                if st.session_state.chatbot.candidate_data:
                    try:
                        filename = st.session_state.data_handler.save_candidate(
                            st.session_state.chatbot.candidate_data
                        )
                        st.sidebar.success(f"✅ Chat saved: {filename}")
                    except Exception as e:
                        st.sidebar.error(f"Oh no, an error saving: {str(e)}")

                st.session_state.conversation_ended = True
                st.rerun() # Refresh the page to show the "conversation ended" message.

            else:
                # If it's not an exit command, process the message
                try:
                    response = st.session_state.chatbot.process_message(user_input)
                    st.session_state.messages.append({"role": "assistant", "content": response})

                    # If the chatbot tells us the interview is complete, save the data.
                    if st.session_state.chatbot.current_stage == 'complete':
                        try:
                            filename = st.session_state.data_handler.save_candidate(
                                st.session_state.chatbot.candidate_data
                            )
                            st.sidebar.success(" Interview complete & saved!")
                        except:
                            # Silently fail if saving doesn't work right at the end.
                            pass

                    st.rerun() # Refresh to show the new messages.

                except Exception as e:
                    # Error
                    error_msg = f"My apologies, I seem to have encountered a small glitch. Let's try that again. Error: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.rerun()

    else:
        # Message once chat ends
        st.info("👋 Conversation ended. Feel free to start a new one from the sidebar!")

    # Display the progress sidebar.
    display_progress()

if __name__ == "__main__":
    main()