import streamlit as st

st.set_page_config(page_title="GenAI SDLC Automation", layout="centered")
st.title("🧠 GenAI-Powered SDLC Flow")
st.markdown("A streamlined demo to showcase automation across the SDLC using GenAI.")
st.divider()

# 1️⃣ Upload Business Requirements
st.header("1️⃣ Upload Business Requirements")
req_file = st.file_uploader("Upload a .txt file with raw business requirements:", type="txt")
requirements = ""
if req_file:
    requirements = req_file.read().decode("utf-8")
    st.success("Requirements uploaded!")
    st.text_area("📄 Raw Requirements", requirements, height=150)
    if st.button("🔄 Generate User Stories", key="gen_user_stories"):
        st.success("✅ Generated User Stories:")
        st.text("- As a user, I want to...\n- As an admin, I need...")

st.divider()

# 2️⃣ Upload User Stories
st.header("2️⃣ Upload User Stories")
us_file = st.file_uploader("Upload user stories to generate test cases:", type="txt")
user_stories = ""
if us_file:
    user_stories = us_file.read().decode("utf-8")
    st.success("User Stories uploaded!")
    st.text_area("📄 User Stories", user_stories, height=150)
    if st.button("🧪 Generate Test Cases", key="gen_test_cases"):
        st.success("✅ Test Cases:")
        st.text("- Positive: Test login with valid credentials\n- Negative: Test login with invalid password\n- Boundary: Test username at max length")

st.divider()

# 3️⃣ Defect Handling
st.header("3️⃣ Defect Handling")
if st.button("🐞 Generate JIRA Defect Template", key="gen_jira_defect"):
    st.success("✅ JIRA Defect Template:")
    st.text("Summary: Login fails for valid users\nComponent: Backend\nPriority: High\nTags: login, backend, critical")

st.divider()

# 4️⃣ Root Cause Analysis
st.header("4️⃣ Root Cause Analysis")
log_file = st.file_uploader("Upload log file for defect analysis:", type="txt")
logs = ""
if log_file:
    logs = log_file.read().decode("utf-8")
    st.success("Logs uploaded!")
    st.text_area("📜 Log Snippet", logs, height=150)
    if st.button("🔍 Run Root Cause Analysis", key="run_root_cause"):
        st.success("✅ Root Cause:")
        st.text("NullPointerException in AuthService at line 42\nSuggested Fix: Check for null token in user session")

st.divider()
st.markdown("© 2025 Labweek | Built for Idea #2946")