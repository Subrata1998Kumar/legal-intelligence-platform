import os
import streamlit as st
import httpx

st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

auth = st.session_state.get("auth")
if not auth or st.session_state.get("role") != "Admin":
    st.error("Access Restricted. Admins only.")
    st.stop()

st.title("⚙️ Global Administration Dashboard")

st.subheader("Ingested Documents Registry")
try:
    r = httpx.get(f"{BACKEND_URL}/documents/list", auth=auth)
    if r.status_code == 200:
        docs = r.json()
        if not docs:
            st.info("No documents uploaded yet.")
        else:
            for d in docs:
                st.write(f"📁 **{d['filename']}** | Clearance: `{d['security_clearance']}` | SHA-256 Hash: `{d['file_hash']}`")
    else:
        st.error("Error listing documents.")
except Exception:
    st.error("Backend server connection failed.")