import streamlit as st
from dotenv import load_dotenv
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import Settings
import os

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI LLM
llm = AzureOpenAI(
    deployment_name=os.environ["AZURE_COMPLETION_MODEL"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version=os.environ["OPENAI_API_VERSION"],
)

# Initialize Azure OpenAI Embeddings
embed_model = AzureOpenAIEmbedding(
    deployment_name=os.environ["AZURE_EMBEDDING_MODEL"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version=os.environ["OPENAI_API_VERSION"],
)

# Assign global settings
Settings.llm = llm
Settings.embed_model = embed_model

response = llm.complete("Say hello from Azure OpenAI!")
print("Model response:", response)

st.set_page_config(page_title="GenAI SDLC Automation", layout="wide")
# Centered title at the top
st.markdown(
    """
    <h1 style='
        text-align:center;
        margin-top:2px;
        margin-bottom:32px;
    '>🧠 GenAI-Powered SDLC Flow</h1>
    """,
    unsafe_allow_html=True
)
#st.markdown("A streamlined demo to showcase automation across the SDLC using GenAI.")
#st.divider()

steps = [
    "Business Requirements",
    "User Stories",
    "Test Case Generation",
    "Defect Handling",
    "Root Cause Analysis"
]

if "current_step" not in st.session_state:
    st.session_state["current_step"] = steps[0]

# Set all button columns to the same width, and arrow columns to a small width
button_width = 1.5
arrow_width = 0.3
widths = []
for i in range(len(steps)):
    widths.append(button_width)
    if i < len(steps) - 1:
        widths.append(arrow_width)

cols = st.columns(widths)
# Replace arrow markdown with a div for vertical centering
for i, step in enumerate(steps):
    # Button column
    if cols[i*2].button(
        step,
        key=f"step_btn_{step}",
        use_container_width=True,
        type="primary" if st.session_state["current_step"] == step else "secondary",
        help=step
    ):
        st.session_state["current_step"] = step
        st.rerun()
    # Arrow column (except after last button)
    if i < len(steps) - 1:
        with cols[i*2 + 1]:
            st.markdown(
                "<div class='arrow-col' style='font-size:2rem;'>&#8594;</div>",
                unsafe_allow_html=True
            )

section = st.session_state["current_step"]

if section == "Business Requirements":
    st.header("1️⃣ Upload Business Requirements")
    with st.container():
        st.markdown("**Paste your business requirements below or upload a file:**")
        if "requirements_input" not in st.session_state:
            st.session_state["requirements_input"] = ""
        requirements = st.text_area(
            "",
            value=st.session_state["requirements_input"],
            height=300,
            key="requirements_input"
        )
        uploaded_file = st.file_uploader(
            "Drag and drop file here\nLimit 200MB per file • TXT",
            type="txt",
            label_visibility="collapsed"
        )
        if uploaded_file:
            uploaded_text = uploaded_file.read().decode("utf-8")
            st.session_state["requirements_input"] = uploaded_text
            requirements = uploaded_text

        if st.button("🔄 Generate User Stories", key="gen_user_stories"):
            if requirements.strip():
                with st.spinner("Generating user stories..."):
                    prompt = (
                        "Given the following business requirements, generate user stories in the format:\n"
                        "- As a <user>, I want to <goal> so that <reason>.\n\n"
                        f"Business Requirements:\n{requirements}\n\nUser Stories:"
                    )
                    response = llm.complete(prompt)
                    st.success("✅ Generated User Stories:")
                    st.text(response)
            else:
                st.warning("Please paste requirements or upload a file.")

elif section == "User Stories":
    st.header("2️⃣ Upload User Stories")
    with st.container():
        st.markdown("**Paste your user stories below or upload a file:**")
        if "user_stories_input" not in st.session_state:
            st.session_state["user_stories_input"] = ""
        user_stories = st.text_area(
            "",
            value=st.session_state["user_stories_input"],
            height=200,
            key="user_stories_input"
        )
        us_file = st.file_uploader(
            "Drag and drop file here\nLimit 200MB per file • TXT",
            type="txt",
            label_visibility="collapsed"
        )
        if us_file:
            uploaded_text = us_file.read().decode("utf-8")
            st.session_state["user_stories_input"] = uploaded_text
            user_stories = uploaded_text

        if st.button("🧪 Generate Test Cases", key="gen_test_cases"):
            if user_stories.strip():
                with st.spinner("Generating test cases..."):
                    prompt = (
                        "Given the following user stories, generate test cases in the format:\n"
                        "- Positive: ...\n- Negative: ...\n- Boundary: ...\n\n"
                        f"User Stories:\n{user_stories}\n\nTest Cases:"
                    )
                    response = llm.complete(prompt)
                    st.success("✅ Test Cases:")
                    st.text(response)
            else:
                st.warning("Please paste user stories or upload a file.")

elif section == "Test Case Generation":
    st.header("3️⃣ Test Case Generation")
    with st.container():
        st.markdown("**Paste your user stories below or upload a file:**")
        if "test_case_user_stories_input" not in st.session_state:
            st.session_state["test_case_user_stories_input"] = ""
        user_stories = st.text_area(
            "",
            value=st.session_state["test_case_user_stories_input"],
            height=200,
            key="test_case_user_stories_input"
        )
        tc_file = st.file_uploader(
            "Drag and drop file here\nLimit 200MB per file • TXT",
            type="txt",
            label_visibility="collapsed"
        )
        if tc_file:
            uploaded_text = tc_file.read().decode("utf-8")
            st.session_state["test_case_user_stories_input"] = uploaded_text
            user_stories = uploaded_text

        if st.button("🧪 Generate Test Cases", key="gen_test_cases_tc"):
            if user_stories.strip():
                with st.spinner("Generating test cases..."):
                    prompt = (
                        "Given the following user stories, generate test cases in the format:\n"
                        "- Positive: ...\n- Negative: ...\n- Boundary: ...\n\n"
                        f"User Stories:\n{user_stories}\n\nTest Cases:"
                    )
                    response = llm.complete(prompt)
                    st.success("✅ Test Cases:")
                    st.text(response)
            else:
                st.warning("Please paste user stories or upload a file.")

elif section == "Defect Handling":
    st.header("4️⃣ Defect Handling")
    if st.button("🐞 Generate JIRA Defect Template", key="gen_jira_defect"):
        st.success("✅ JIRA Defect Template:")
        st.text("Summary: Login fails for valid users\nComponent: Backend\nPriority: High\nTags: login, backend, critical")

elif section == "Root Cause Analysis":
    st.header("5️⃣ Root Cause Analysis")
    log_file = st.file_uploader("Upload log file for defect analysis:", type="txt")
    logs = ""
    if log_file:
        logs = log_file.read().decode("utf-8")
        st.success("Logs uploaded!")
        st.text_area("📜 Log Snippet", logs, height=150)
        if st.button("🔍 Run Root Cause Analysis", key="run_root_cause"):
            st.success("✅ Root Cause:")


# st.divider()
# Custom CSS for buttons, arrows, and sticky footer
st.markdown("""
    <style>
    button[kind="primary"], button[kind="secondary"] {
        min-height: 70px !important;
        font-size: 1.1rem !important;
    }
    .arrow-col {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100vw;
        background: rgba(255,255,255,0.95);
        text-align: center;
        padding: 10px 0 5px 0;
        z-index: 99999;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Add a flexible spacer to push divider and footer to the bottom
st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)

# Divider and sticky footer at the bottom
st.markdown("<hr style='margin:0; padding:0;'>", unsafe_allow_html=True)
st.markdown(
    "<div class='footer'>© 2025 Labweek | Built for Idea #2946</div>",
    unsafe_allow_html=True
)