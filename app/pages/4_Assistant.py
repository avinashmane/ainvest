import streamlit as st
import yaml
import time
from agents.team import initialize_team
from textwrap import dedent
from app.components.login import login_screen, logged_in
from app.page_common import user

# Set Streamlit page configuration
st.set_page_config(
    page_title="Investment Assistant Team",
    page_icon="📈",
    layout="wide"
)

if not st.user.is_logged_in:
    login_screen()
else:
    logged_in()
    # --- Session State Initialization ---
    # Initialize team_session_id for this specific browser session
    if "team_session_id" not in st.session_state:
        st.session_state.team_session_id = f"streamlit-team-session-{int(time.time())}"
    # Initialize chat message history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "team" not in st.session_state:
        st.session_state.team = initialize_team()




    st.title("🤑 Assistant for Investments")
    with st.container(horizontal=True):
        samples=yaml.safe_load(dedent("""
        - Latest news on Microsoft along with negative sentiment italics in markdown
        - Get me current price of Reliance
        - 5 day chart for Reliance
        """))
        for s in samples: st.code(s) 


    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    # Handle user input
    user_query = st.chat_input("Ask the investment team anything...")

    if user_query:
        print(user_query)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_query})

        # Display user message
        with st.chat_message("user"):
            st.markdown(user_query)

        # Display team response (Streaming)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                # Use stream=True for the team run
                response_stream: RunOutput = st.session_state.team.run(user_query, stream=True) # Ensure type hint Iterator[RunResponse]

                for i,run_event in enumerate(response_stream):
                    # Check if content is present and a string
                    # print(f"{i}> ",run_event)
                    if run_event.content and isinstance(run_event.content, str):
                        if run_event.event in ['Run-Content','TeamRunContent']:
                            full_response += run_event.content
                            message_placeholder.markdown(full_response + "▌") # Add cursor effect
                        else:
                            if hasattr(st.session_state,'log'): st.session_state.log.append(run_event)
                            else: st.session_state.log=[run_event]

                message_placeholder.markdown(full_response) # Final response without cursor

                # Update memory debug information for display
                if hasattr(st.session_state.team, 'memory') and hasattr(st.session_state.team.memory, 'messages'):
                    try:
                        # Extract only role and content safely
                        st.session_state.memory_dump = [
                            {"role": m.role if hasattr(m, 'role') else 'unknown',
                            "content": m.content if hasattr(m, 'content') else str(m)}
                            for m in st.session_state.team.memory.messages
                        ]
                    except Exception as e:
                        st.session_state.memory_dump = f"Error accessing memory messages: {str(e)}"
                else:
                    st.session_state.memory_dump = "Team memory object or messages not found/accessible."

                # Add the final assistant response to Streamlit's chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.exception(e) # Show full traceback in Streamlit console for debugging
                error_message = f"An error occurred: {str(e)}\n\nPlease check your API keys and tool configurations. Try rephrasing your query."
                st.error(error_message)
                message_placeholder.markdown(f"⚠️ {error_message}")
                # Add error message to history for context
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})


