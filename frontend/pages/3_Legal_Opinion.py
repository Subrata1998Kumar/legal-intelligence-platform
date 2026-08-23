import os
import streamlit as st
import httpx

st.set_page_config(page_title="Opinion Workspace", page_icon="✍️", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

auth = st.session_state.get("auth")
if not auth:
    st.warning("Please log in from the home screen first.")
    st.stop()

st.title("✍️ Government Legal Opinion Workspace")

tab1, tab2 = st.tabs(["Draft New Opinion", "Review Opinion Pipelines"])

with tab1:
    st.header("Draft Legal Advice")
    op_title = st.text_input("Opinion Subject / Title", value="Legal review of construction contract liability")
    op_content = st.text_area("Draft Opinion Content", height=250, value="The private contractor failed to complete structural milestones under section 14. Given standard secretariat protocol, the state is entitled to withhold payment.")
    
    if st.button("Submit for Risk Audit"):
        with st.spinner("Analyzing opinion drafts against precedent context..."):
            try:
                r = httpx.post(f"{BACKEND_URL}/opinions/draft", auth=auth, json={
                    "title": op_title,
                    "draft_content": op_content
                }, timeout=180.0)
                if r.status_code == 200:
                    st.success("Opinion Draft Submitted Successfully!")
                    res = r.json()
                    st.write("### AI Legal Risk Report Summary")
                    st.json(res["compliance_report"])
                else:
                    st.error("Failed to draft opinion.")
            except httpx.TimeoutException:
                st.error("The legal opinion analysis timed out. Please try again or reduce the draft size.")
            except httpx.RequestError as e:
                st.error(f"Connection failed: {e}")

with tab2:
    st.header("Opinion In-Review Queues")
    try:
        r = httpx.get(f"{BACKEND_URL}/opinions/list", auth=auth)
        if r.status_code == 200:
            opinions = r.json()
            if not opinions:
                st.info("No active opinions.")
            for op in opinions:
                st.markdown(f"### {op['title']}")
                st.markdown(f"**Current Status:** `{op['status']}`")
                st.write(op["draft_content"])
                
                with st.expander("🔎 View Automated Legal Risk Audit"):
                    rep = op["compliance_report"]
                    st.write(f"**Automated Risk Score:** `{rep.get('risk_score', 0.0)}/10`")
                    st.write("**Precedent Compliance Issues:**")
                    for p in rep.get("precedent_compliance", []):
                        st.write(f"- {p}")
                    st.write("**Conflicts of Interest Identified:**")
                    for c in rep.get("conflict_of_interest", []):
                        st.write(f"- {c}")
                    st.write("**Missing Legal References:**")
                    for m in rep.get("missing_precedents", []):
                        st.write(f"- {m}")
                
                if st.session_state.role in ["Senior_Advisor", "Admin"]:
                    new_status = st.selectbox(f"Transition Status for Opinion #{op['id']}", ["Under_Review", "Approved", "Rejected"], key=f"sel_{op['id']}")
                    if st.button(f"Commit Status Update", key=f"btn_{op['id']}"):
                        u_res = httpx.put(f"{BACKEND_URL}/opinions/{op['id']}/status", auth=auth, json={"status": new_status})
                        if u_res.status_code == 200:
                            st.success(f"Status committed successfully as: {new_status}")
                            st.rerun()
                        else:
                            st.error("Error committing status update.")
                st.markdown("---")
        else:
            st.error("Could not fetch opinions.")
    except Exception:
        st.error("Backend server offline.")