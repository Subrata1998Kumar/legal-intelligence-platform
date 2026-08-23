import os
import streamlit as st
import httpx

st.set_page_config(
    page_title="Enterprise Legal Intelligence Platform",
    page_icon="⚖️",
    layout="wide"
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

# Manage session state variables
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "auth" not in st.session_state:
    st.session_state.auth = None

st.title("⚖️ Law Department - Government Secretariat")
st.subheader("Enterprise Legal Intelligence and Opinion Assistant")

# Authentication Portal
if not st.session_state.auth:
    st.info("Please log in using your credentials to access the Enterprise Legal Platform.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Basic Authentication Login")
        username_input = st.text_input("Username", value="admin")
        password_input = st.text_input("Password", type="password", value="admin")
        
        if st.button("Log In"):
            try:
                # Basic Auth login checking
                r = httpx.post(f"{BACKEND_URL}/users/login", auth=(username_input, password_input))
                if r.status_code == 200:
                    data = r.json()
                    st.session_state.username = data["username"]
                    st.session_state.role = data["role"]
                    st.session_state.auth = (username_input, password_input)
                    st.success(f"Welcome back, {username_input}! Role: {data['role']}")
                    st.rerun()
                else:
                    st.error("Authentication failed. Check credentials.")
            except Exception as e:
                st.error("Cannot connect to backend server. Ensure Docker containers are running.")
                
    with col2:
        st.write("### Security & Architecture Standard")
        st.markdown("""
        *   **Isolated Processing**: All file processing & storage is strictly sandbox-confined.
        *   **Dual-layer RBAC Documents**: Streamlit automatically pre-tags uploads based on role hierarchy.
        *   **Local IBM Granite Model**: Zero-internet leakage compliance check and legal opinion auditing.
        *   **Basic Auth & JSON User Sync**: Configured with a structured user directory loaded from `users.json`.
        *   **Pre-configured POC Accounts**:
            1.  `User: admin` / `Password: admin` (Admin Role)
            2.  `User: advisor_1` / `Password: advisor_1` (Senior Advisor Role)
            3.  `User: officer_1` / `Password: officer_1` (Legal Officer Role)
        """)
else:
    st.success(f"Authenticated as **{st.session_state.username}** ({st.session_state.role})")
    st.markdown("""
    ### Available Modules:
    1.  👈 **Document Upload**: Upload raw Text, PDF, or Word documents. Handles OCR and Table extraction automatically.
    2.  👈 **Search & Retrieval**: Contextual RAG Semantic QA & citation lookups.
    3.  👈 **Legal Opinion Workspace**: Create legally-defensible advice and trigger Ollama audits.
    4.  👈 **Admin Dashboard**: Inspect systemic audit logs and see uploaded document clearances (Admins Only).
    """)
    
    if st.button("Log Out"):
        # Clear all session state keys to prevent cross-user leakage or old chat history pollution
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Logged out successfully!")
        st.rerun()