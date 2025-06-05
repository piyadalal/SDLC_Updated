import streamlit as st
from dotenv import load_dotenv
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import Settings
import os
import pdfplumber
from vertexai.preview.generative_models import GenerativeModel
import vertexai
from fpdf import FPDF
import re
import fitz  # PyMuPDF

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

steps = [
    "Business Requirements",
    "User Story",
    "Test Case Generation",
    "Defect Handling",
    "Root Cause Analysis"
]

descriptions = {
    "Business Requirements": "📄 Turn Business Requirements into user stories.",
    "User Story": "✅ Auto-generate ACs from User Stories",
    "Test Case Generation": "🧪 Auto-generate test cases from ACs.",
    "Defect Handling": "🐞 Create Defect templates in JIRA based on defect description",
    "Root Cause Analysis": "🔍 Detect root causes from logs files for a defect."
}

if "current_step" not in st.session_state:
    st.session_state["current_step"] = steps[0]

# Define layout widths
button_width = 1.5
arrow_width = 0.3
widths = []
for i in range(len(steps)):
    widths.append(button_width)
    if i < len(steps) - 1:
        widths.append(arrow_width)

# Create column layout
cols = st.columns(widths)

# Build UI buttons and arrows
for i, step in enumerate(steps):
    with cols[i * 2]:
        clicked = st.button(
            step,
            key=f"step_btn_{step}",
            use_container_width=True,
            type="primary" if st.session_state["current_step"] == step else "secondary"
        )
        # Add mini description below the button
        st.markdown(
            f"<div style='font-size:0.8rem; color:gray; text-align:center;'>{descriptions[step]}</div>",
            unsafe_allow_html=True
        )
        if clicked:
            st.session_state["current_step"] = step
            st.rerun()
    # Arrow between steps
    if i < len(steps) - 1:
        with cols[i * 2 + 1]:
            st.markdown(
                "<div style='font-size:2rem; text-align:center;'>&#8594;</div>",
                unsafe_allow_html=True
            )

section = st.session_state["current_step"]

def text_to_pdf(text: str, title: str = None) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=11)
    if title:
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Arial", size=11)
    lines = text.strip().split('\n')
    for line in lines:
        pdf.multi_cell(0, 10, line)
    return pdf.output(dest='S').encode('latin1')

if section == "Business Requirements":
    st.header("1️⃣ Upload Business Requirements")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Paste your business requirements below or upload a file:**")
        if "requirements_input" not in st.session_state:
            st.session_state["requirements_input"] = ""
        requirements = st.text_area(
            "",
            value=st.session_state["requirements_input"],
            height=200,
            key="requirements_input"
        )
        uploaded_file = st.file_uploader(
            "Drag and drop file here\nLimit 200MB per file • TXT or PDF",
            type=["txt", "pdf"],
            label_visibility="collapsed"
        )
        full_text = ""
        if uploaded_file:
            file_ext = uploaded_file.name.split(".")[-1].lower()
            if file_ext == "pdf":
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                for page in doc:
                    full_text += page.get_text()
            elif file_ext == "txt":
                full_text = uploaded_file.read().decode("utf-8")
            else:
                st.error("Unsupported file type.")
                full_text = ""
            st.session_state["requirements_input"] = full_text
            requirements = full_text

        col_gemini, col_gpt = st.columns(2)

        with col_gemini:
            if st.button("🧠 Generate User Stories using Gemini"):
                if requirements.strip():
                    with st.spinner("Generating user stories using Gemini"):
                        vertexai.init(project="uk-labs-hackathon-1-0625-dev", location="europe-west1")
                        model = GenerativeModel("gemini-2.0-flash-001")
                        prompt = f"""
You are a senior QA engineer and business analyst working on the WatchList
functionality for a Sky DE STB product. Based on the provided product requirements, generate:
1. One or more **User Stories** (formatted with territory/platform, user role, and business goal). 
Here is how the requirements looks like :
{requirements}
"""
                        response = model.generate_content(prompt)
                        st.session_state["user_stories_result"] = response.text
                else:
                    st.warning("Please paste requirements or upload a file.")

        with col_gpt:
            if st.button("🔄 Generate User Stories using GPT"):
                if requirements.strip():
                    with st.spinner("Generating user stories using GPT..."):
                        prompt_gpt = (
                            "Given the following business requirements, generate user stories in the format:\n"
                            "- As a <user>, I want to <goal> so that <reason>.\n\n"
                            f"Business Requirements:\n{requirements}\n\nUser Stories:"
                        )
                        response = llm.complete(prompt_gpt)
                        st.session_state["user_stories_result"] = response
                else:
                    st.warning("Please paste requirements or upload a file.")

    with col2:
        st.markdown("**Generated User Stories:**")
        user_stories_text = st.session_state.get("user_stories_result", "")
        st.text_area(
            "",
            value=user_stories_text,
            height=318,
            key="user_stories_result_display"
        )
        pdf_bytes = text_to_pdf(user_stories_text or "", title="Generated User Stories")
        st.download_button(
            label="⬇️ Download as PDF",
            data=pdf_bytes,
            file_name="generated_user_stories.pdf",
            mime="application/pdf"
        )

elif section in ["User Story", "User Stories"]:
    st.header("2️⃣ Upload User Stories")
    col1, col2 = st.columns(2)

    with col1:
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
            "Drag and drop file here\nLimit 200MB per file • TXT or PDF",
            type=["txt", "pdf"],
            label_visibility="collapsed"
        )
        uploaded_text = ""
        if us_file:
            file_ext = us_file.name.split(".")[-1].lower()
            if file_ext == "pdf":
                doc = fitz.open(stream=us_file.read(), filetype="pdf")
                for page in doc:
                    uploaded_text += page.get_text()
            elif file_ext == "txt":
                uploaded_text = us_file.read().decode("utf-8")
            else:
                st.error("Unsupported file type.")
                uploaded_text = ""
            st.session_state["user_stories_input"] = uploaded_text
            user_stories = uploaded_text

        col_gemini, col_gpt, col_tc = st.columns(3)

        with col_gemini:
            if st.button("🧠 Generate Acceptance Criteria using Gemini"):
                if user_stories.strip():
                    with st.spinner("Generating Acceptance Criteria using Gemini..."):
                        vertexai.init(project="uk-labs-hackathon-1-0625-dev", location="europe-west1")
                        model = GenerativeModel("gemini-2.0-flash-001")
                        prompt = f"""
You are a senior QA engineer and business analyst working on the WatchList functionality for a
Sky DE STB product. Based on the provided user stories, generate:
1. For each User Story, provide **detailed Acceptance Criteria** strictly in the
"Given / When / Then" format, with no AND statements.
Here are the user stories:
{user_stories}
"""
                        response = model.generate_content(prompt)
                        st.session_state["acceptance_criteria_result"] = response.text
                else:
                    st.warning("Please paste user stories or upload a file.")

        with col_gpt:
            if st.button("🔄 Generate Acceptance Criteria using GPT"):
                if user_stories.strip():
                    with st.spinner("Generating acceptance criteria using GPT..."):
                        prompt_gpt = (
                            "Given the following user stories, generate acceptance criteria in the format:\n"
                            "Given <context>, When <action>, Then <outcome>.\n\n"
                            f"User Stories:\n{user_stories}\n\nAcceptance Criteria:"
                        )
                        response = llm.complete(prompt_gpt)
                        st.session_state["acceptance_criteria_result"] = response
                else:
                    st.warning("Please paste user stories or upload a file.")

        with col_tc:
            if st.button("🧪 Generate Test Cases", key="gen_test_cases"):
                if user_stories.strip():
                    with st.spinner("Generating test cases..."):
                        prompt = (
                            "Given the following user stories, generate test cases in the format:\n"
                            "- Positive: ...\n- Negative: ...\n- Boundary: ...\n\n"
                            f"User Stories:\n{user_stories}\n\nTest Cases:"
                        )
                        response = llm.complete(prompt)
                        st.session_state["test_cases_result"] = response
                else:
                    st.warning("Please paste user stories or upload a file.")

    with col2:
        st.markdown("**Generated Acceptance Criteria:**")
        ac_text = st.session_state.get("acceptance_criteria_result", "")
        st.text_area(
            "",
            value=ac_text,
            height=150,
            key="acceptance_criteria_result_display"
        )
        pdf_bytes_ac = text_to_pdf(ac_text or "", title="Generated Acceptance Criteria")
        st.download_button(
            label="⬇️ Download Acceptance Criteria as PDF",
            data=pdf_bytes_ac,
            file_name="generated_acceptance_criteria.pdf",
            mime="application/pdf"
        )

        st.markdown("**Generated Test Cases:**")
        test_cases_text = st.session_state.get("test_cases_result", "")
        st.text_area(
            "",
            value=test_cases_text,
            height=150,
            key="test_cases_result_display"
        )
        pdf_bytes_tc = text_to_pdf(test_cases_text or "", title="Generated Test Cases")
        st.download_button(
            label="⬇️ Download Test Cases as PDF",
            data=pdf_bytes_tc,
            file_name="generated_test_cases.pdf",
            mime="application/pdf"
        )

elif section == "Test Case Generation":
    st.header("3️⃣ Test Case Generation")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Paste your user stories or acceptance criteria below or upload a file:**")
        if "test_case_user_stories_input" not in st.session_state:
            st.session_state["test_case_user_stories_input"] = ""
        user_stories = st.text_area(
            "",
            value=st.session_state["test_case_user_stories_input"],
            height=200,
            key="test_case_user_stories_input"
        )
        tc_file = st.file_uploader(
            "Drag and drop file here\nLimit 200MB per file • TXT or PDF",
            type=["txt", "pdf"],
            label_visibility="collapsed"
        )
        uploaded_text = ""
        if tc_file:
            file_ext = tc_file.name.split(".")[-1].lower()
            if file_ext == "pdf":
                doc = fitz.open(stream=tc_file.read(), filetype="pdf")
                for page in doc:
                    uploaded_text += page.get_text()
            elif file_ext == "txt":
                uploaded_text = tc_file.read().decode("utf-8")
            else:
                st.error("Unsupported file type.")
                uploaded_text = ""
            st.session_state["test_case_user_stories_input"] = uploaded_text
            user_stories = uploaded_text

        col_gemini, col_gpt = st.columns(2)

        with col_gemini:
            if st.button("🧠 Generate Testcases using Gemini"):
                if user_stories.strip():
                    with st.spinner("Generating Testcases using Gemini..."):
                        vertexai.init(project="uk-labs-hackathon-1-0625-dev", location="europe-west1")
                        model = GenerativeModel("gemini-2.0-flash-001")
                        prompt = f"""
You are a senior QA engineer and business analyst working on the WatchList functionality for a
Sky DE STB product. Based on the provided user stories in the format:
"- As a <user>, I want to <goal> so that <reason>."
or acceptance criteria in the format "Given / When / Then", generate:
1. For each User Story or acceptance criteria, generate one or more **E2E test cases** in this format:
Test Case: [Clear and descriptive title]
| Test Step | Action | Expected Result |
|-----------|------------------------------------------------------------------------|------------------------------------------------------|
| Step 1 | [Describe the user action clearly] | [Describe what the system should do or show] |
| Step 2 | [Next step, continuing the user flow] | [Next expected outcome] |
| ... | ... | ... |

2. Match the level of detail and formal tone used in the user story or acceptance criteria documentation below.
{user_stories}
"""
                        response = model.generate_content(prompt)
                        st.session_state["test_cases_result_tc"] = response.text
                else:
                    st.warning("Please paste user stories or upload a file.")

        with col_gpt:
            if st.button("🔄 Generate Testcases using GPT"):
                if user_stories.strip():
                    with st.spinner("Generating Testcases using GPT..."):
                        prompt_gpt = (
                            f"""
You are a senior QA engineer and business analyst working on the WatchList functionality for a
Sky DE STB product. Based on the provided user stories in the format:
"- As a <user>, I want to <goal> so that <reason>."
or acceptance criteria in the format "Given / When / Then", generate:
1. For each User Story or acceptance criteria, generate one or more **E2E test cases** in this format:
Test Case: [Clear and descriptive title]
| Test Step | Action | Expected Result |
|-----------|------------------------------------------------------------------------|------------------------------------------------------|
| Step 1 | [Describe the user action clearly] | [Describe what the system should do or show] |
| Step 2 | [Next step, continuing the user flow] | [Next expected outcome] |
| ... | ... | ... |

2. Match the level of detail and formal tone used in the user story or acceptance criteria documentation below.
{user_stories}
"""
                        )
                        response = llm.complete(prompt_gpt)
                        st.session_state["test_cases_result_tc"] = response
                else:
                    st.warning("Please paste user stories or upload a file.")

    with col2:
        test_cases_text_tc = st.session_state.get("test_cases_result_tc", "")
        st.markdown("**Generated Test Cases:**")
        st.text_area(
            "",
            value=test_cases_text_tc,
            height=318,
            key="test_cases_result_tc_display"
        )
        pdf_bytes = text_to_pdf(test_cases_text_tc or "", title="Generated Test Cases")
        st.download_button(
            label="⬇️ Download as PDF",
            data=pdf_bytes,
            file_name="generated_test_cases.pdf",
            mime="application/pdf"
        )

elif section == "Defect Handling":
    st.header("4️⃣ Defect Handling")

elif section == "Root Cause Analysis":
    st.header("4️⃣ Root Cause Analysis")
    with st.container():
        st.markdown("**Paste your log file error or upload a file:**")
        # Text area for manual input (independent from file upload)
        user_input_text = st.text_area(
            label="",
            placeholder="Type or paste log file error here...",
            height=200,
            key="log_file_error_input"
        )
        # File uploader input (stored separately)
        us_file = st.file_uploader(
            "Or upload a file (TXT or PDF)",
            type=["txt", "pdf"],
            label_visibility="collapsed"
        )
        uploaded_text = ""
        if us_file:
            file_ext = us_file.name.split(".")[-1].lower()
            if file_ext == "pdf":
                import fitz  # PyMuPDF

                doc = fitz.open(stream=us_file.read(), filetype="pdf")
                for page in doc:
                    uploaded_text += page.get_text()
            elif file_ext == "txt":
                uploaded_text = us_file.read().decode("utf-8")
            else:
                st.error("Unsupported file type.")
        st.text_area(
            "📄 Preview of uploaded file content (read-only):",
            value=uploaded_text,
            height=200,
            disabled=True
        )
        # Final text source logic: Prefer manual input if not empty
        final_user_stories = user_input_text.strip() or uploaded_text.strip()

        if st.button("🧠Analyze STB Log File"):
            with st.spinner("Analyzing STB logs for issues..."):
                # Dynamically pick the final source
                user_stories_source = user_input_text.strip() or uploaded_text.strip()
                if not user_stories_source:
                    st.warning("Please provide log file error lines via text area or file upload.")
                else:
                    full_text = ""
                    with pdfplumber.open(us_file) as pdf:
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                full_text += text + "\n"
                        regex = re.compile("ERROR", re.IGNORECASE)

                        file_ext = us_file.name.split(".")[-1].lower()
                        if file_ext == "pdf":
                            print("Detected PDF log file. Extracting text...")
                            lines = full_text.splitlines()
                        else:
                            print("Detected plain text log file. Reading directly...")
                            with open(user_stories_source, "r", encoding="utf-8", errors="ignore") as f:
                                lines = f.readlines()

                            # Filter and clean lines that match the pattern
                            filtered_lines = [line.strip() for line in lines if regex.search(line)]
                        chunk = []
                        total_chars = 0
                        max_chars = 8000
                        chunks = []
                        for line in lines:
                            if total_chars + len(line) > max_chars:
                                chunks.append("\n".join(chunk))
                                chunk = []
                                total_chars = 0

                            chunk.append(line)
                            total_chars += len(line)

                        if chunk:
                            chunks.append("\n".join(chunk))
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_auto_page_break(auto=True, margin=15)
                        pdf.set_font("Arial", size=12)

                        for i, chunk in enumerate(chunks, 1):
                            prompt = f"""
                    You are a senior STB QA engineer. Analyze the following log lines and summarize:
                    1. Any known issues (e.g., 404 means 'page not found', 'No signal' → HDMI issue).
                    2. Group errors by type and give root causes if possible.
                    3. Review the following logs and identify:
                    - Any errors (e.g., HTTP 404, HDMI issues, authentication failures)
                    - The cause (if identifiable)
                    - Suggested fix or root cause in plain language

                    Respond in this format:
                    Error: [Short error]
                    Cause: [Why it happened]
                    Fix: [Suggested fix or next step]
                    Log Chunk #{i}:
                    {chunk}
                    """
                            vertexai.init(project="uk-labs-hackathon-1-0625-dev", location="europe-west1")
                            model = GenerativeModel("gemini-2.0-flash-001")
                            response = model.generate_content(prompt)
                            output_text = response.text
                            st.success("✅ Log file Analyzed successfully")
                            pdf_data = text_to_pdf(output_text)
                            st.download_button(
                                label="📄 Download Log file as PDF",
                                data=pdf_data,
                                file_name="Log_file_analysis.pdf",
                                mime="application/pdf"
                            )
                            st.text_area("📋 Detected Issues", output_text, height=500)

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
