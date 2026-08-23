import os
import streamlit as st
import httpx

st.set_page_config(page_title="Search & Retrieval", page_icon="🔍", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

auth = st.session_state.get("auth")
if not auth:
    st.warning("Please log in from the home screen first.")
    st.stop()

st.title("🔍 Semantic Precedent Search & Retrieval")

# Sidebar for managing chat sessions dynamically from the backend
with st.sidebar:
    st.subheader("Conversation History")
    
    # Fetch active user's existing sessions from the database
    sessions = []
    try:
        r = httpx.get(f"{BACKEND_URL}/chat/sessions", auth=auth)
        if r.status_code == 200:
            sessions = r.json()
    except Exception:
        st.error("Backend offline. Cannot load chat history.")
        
    # Provide an option to start a fresh thread or load a saved one
    session_options = ["➕ Start New Conversation"] + [f"💬 {s['title']} ({s['id'][:8]})" for s in sessions]
    session_ids = [None] + [s["id"] for s in sessions]
    
    # Initialize index to 0 (New Conversation)
    if "selected_session_index" not in st.session_state:
        st.session_state.selected_session_index = 0
        
    selected_idx = st.selectbox(
        "Select Session", 
        range(len(session_options)), 
        format_func=lambda i: session_options[i],
        index=st.session_state.selected_session_index,
        key="session_selector_widget"
    )
    
    # If selection changes, clear cached local messages so they can reload from the correct session id
    if selected_idx != st.session_state.selected_session_index:
        st.session_state.selected_session_index = selected_idx
        if "messages" in st.session_state:
            del st.session_state.messages
        st.rerun()

    active_session_id = session_ids[selected_idx]

# Secure Session Isolation: Retrieve and load messages strictly for the active session ID
if active_session_id is None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
else:
    # Ensure we load from the database and isolate between logins
    if "messages" not in st.session_state or st.session_state.get("current_loaded_session_id") != active_session_id:
        try:
            r = httpx.get(f"{BACKEND_URL}/chat/sessions/{active_session_id}/messages", auth=auth)
            if r.status_code == 200:
                st.session_state.messages = [{"role": m["role"], "content": m["content"]} for m in r.json()]
                st.session_state.current_loaded_session_id = active_session_id
            else:
                st.session_state.messages = []
                st.error("Failed to load session messages.")
        except Exception:
            st.session_state.messages = []
            st.error("Connection failed while loading session messages.")

st.subheader("Chat Workspace")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_query = st.chat_input("Ask a legal question (e.g., 'What is the penalty for contract non-compliance?')")

if user_query:
    # Lazily create a new session in the database if starting a fresh thread
    if active_session_id is None:
        try:
            r = httpx.post(f"{BACKEND_URL}/chat/sessions", auth=auth)
            if r.status_code == 200:
                active_session_id = r.json()["id"]
                st.session_state.current_loaded_session_id = active_session_id
                st.session_state.selected_session_index = 1  # Point to the newly created session
            else:
                st.error("Failed to create new chat session on backend.")
                st.stop()
        except Exception as e:
            st.error("Backend connection failure during session creation.")
            st.stop()

    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)
        
    with st.spinner("Retrieving authoritative chunks and generating legal advice..."):
        try:
            r = httpx.post(
                f"{BACKEND_URL}/chat/sessions/{active_session_id}/query",
                auth=auth,
                json={"message": user_query},
                timeout=60.0
            )
            if r.status_code == 200:
                res = r.json()
                response_text = res["response"]
                sources = res["sources"]
                
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                with st.chat_message("assistant"):
                    st.write(response_text)
                    
                    if sources:
                        st.markdown("#### Grounded Reference Citations:")
                        for s in sources:
                            with st.expander(f"📖 {s['filename']} (Similarity: {s['similarity']:.2f})"):
                                st.markdown(
                                    f"*   **Chunk Index**: {s['chunk_index']}\n"
                                    f"*   **Clearance Tag**: `{s['clearance']}`"
                                )
                
                # Rerun to update sidebar conversation listing titles dynamically
                st.rerun()
            else:
                st.error("Error generating answer.")
        except Exception as e:
            st.error(f"Backend connection timeout/failure: {str(e)}")