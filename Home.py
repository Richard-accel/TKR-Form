import streamlit as st

st.set_page_config(page_title="TKR Portal", layout="centered")

st.title("🏥 Total Knee Replacement (TKR) Portal")

st.markdown("Welcome to the TKR clinical data platform. Choose a section to begin:")

# Correct page paths (relative to pages/)
col1, col2, col3 = st.columns(3)

with col1:
    st.page_link("pages/preOpDashboard.py", label="📊 Pre-Op Dashboard", icon="📊")
    st.page_link("pages/preOpCSV.py", label="📝 Pre-Op CSV Export", icon="📄")

with col2:
    st.page_link("pages/intraOpDashboard.py", label="📊 Intra-Op Dashboard", icon="📊")
    st.page_link("pages/intraOpCSV.py", label="📝 Intra-Op CSV Export", icon="📄")

with col3:
    st.page_link("pages/postOpDashboard.py", label="📊 Post-Op Dashboard", icon="📊")
    st.page_link("pages/postOpCSV.py", label="📝 Post-Op CSV Export", icon="📄")
