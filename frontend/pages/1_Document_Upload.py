import os
import streamlit as st
import httpx

st.set_page_config(page_title="Document Ingestion", page_icon="📥", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

auth = st.session_state.get("auth")
if not auth:
    st.warning("Please log in from the home screen first.")
    st.stop()

st.title("📥 Secure Document Ingestion")
st.markdown("Upload Government Orders, notifications, judgments, or bills to the local database.")

uploaded_file = st.file_uploader("Select a file (.pdf, .docx, .doc, .txt, .md, .sql)", type=["pdf", "docx", "doc", "txt", "md", "sql"])

# Define role-based dropdown selection
clearance_options = ["Legal_Officer", "Senior_Advisor", "Admin"]
user_role = st.session_state.role

if user_role == "Admin":
    clearance = st.selectbox("Assign Minimum Security Clearance", clearance_options, index=0)
else:
    try:
        default_idx = clearance_options.index(user_role)
    except ValueError:
        default_idx = 0
    clearance = st.selectbox(
        "Assign Minimum Security Clearance", 
        clearance_options, 
        index=default_idx, 
        disabled=True,
        help="Only Administrators can assign a custom clearance level. Your files are automatically tagged with your own role clearance."
    )

if st.button("Ingest Document"):
    if not uploaded_file:
        st.error("Please select a file.")
    else:
        data = {"security_clearance": clearance}
        filename_lower = uploaded_file.name.lower()
        if filename_lower.endswith(".pdf"):
            content_type = "application/pdf"
        elif filename_lower.endswith(".docx"):
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif filename_lower.endswith(".doc"):
            content_type = "application/msword"
        else:
            content_type = "text/plain"
            
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), content_type)}
        
        with st.spinner("Processing document chunks, running table extraction/OCR, & generating vector embeddings..."):
            try:
                r = httpx.post(f"{BACKEND_URL}/documents/upload", auth=auth, data=data, files=files, timeout=90.0)
                if r.status_code == 200:
                    res = r.json()
                    st.success(f"Successfully uploaded: {res['filename']} (ID: {res['id']})")
                    st.info(f"File integrity hash generated (SHA-256): {res['file_hash'][:12]}...")
                    st.markdown(f"""
                    **Ingestion Audit:**
                    - Text Chunks Generated: `{res['text_chunks']}`
                    - Table Chunks Extracted: `{res['table_chunks']}`
                    - OCR Fallback Triggered: `{res['ocr_triggered']}`
                    """)
                else:
                    st.error(f"Upload failed: {r.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Failed to connect to backend service. Error: {str(e)}")