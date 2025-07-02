import streamlit as st
from dotenv import load_dotenv
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import Settings
import os
from fpdf import FPDF
import fitz  # PyMuPDF
from vertexai.preview.language_models import GenerativeModel
import vertexai
import subprocess

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
    unsafe_allow_html=True,
)

steps = [
    "Business Requirements",
    "User Story",
    "Test Case Generation",
    "Defect Handling",
    "Root Cause Analysis",
]

descriptions = {
    "Business Requirements": "📄 Turn Business Requirements into user stories.",
    "User Story": "✅ Auto-generate ACs from User Stories",
    "Test Case Generation": "🧪 Auto-generate test cases from ACs.",
    "Defect Handling": "🐞 Create Defect templates in JIRA based on defect description",
    "Root Cause Analysis": "🔍 Detect root causes from logs files for a defect.",
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
            type="primary" if st.session_state["current_step"] == step else "secondary",
        )
        # Add mini description below the button
        st.markdown(
            f"<div style='font-size:0.8rem; color:gray; text-align:center;'>{descriptions[step]}</div>",
            unsafe_allow_html=True,
        )
        if clicked:
            st.session_state["current_step"] = step
            st.experimental_rerun()

    # Arrow between steps
    if i < len(steps) - 1:
        with cols[i * 2 + 1]:
            st.markdown(
                "<div style='font-size:2rem; text-align:center;'>&#8594;</div>",
                unsafe_allow_html=True,
            )


section = st.session_state["current_step"]


def text_to_pdf(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    lines = text.split('\n')
    for line in lines:
        pdf.cell(0, 10, line, ln=True)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes


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
            key="requirements_input",
        )
        uploaded_file = st.file_uploader(
            "Drag and drop file here\nLimit 200MB per file • TXT or PDF",
            type=["txt", "pdf"],
            label_visibility="collapsed",
        )
        if uploaded_file:
            file_ext = uploaded_file.name.split(".")[-1].lower()
            if file_ext == "pdf":
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                full_text = ""
                for page in doc:
                    full_text += page.get_text()
            elif file_ext == "txt":
                full_text = uploaded_file.read().decode("utf-8")
            else:
                st.error("Unsupported file type.")
                full_text = ""
            st.text_area(
                "📄 Preview of uploaded file content (read-only):",
                value=full_text,
                height=200,
                disabled=True,
            )

        # Create two columns for buttons side-by-side
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🧠 Generate User Stories using Gemini"):
                with st.spinner("Generating user stories using Gemini"):
                    prompt = f"""
                    You are a senior QA engineer and business analyst working on the nCRM side of the STB customer Database
                    functionality for a Sky DE STB product. Based on the provided product requirements, generate:
                    1. One or more **User Stories** (formatted with territory/platform, user role, and business goal).
                    Here is how the requirements looks like :
                    {full_text}
                    """

                    # Run Ollama with Mistral model
                    result = subprocess.run(
                        ['ollama', 'run', 'mistral'],
                        input=prompt.encode(),
                        stdout=subprocess.PIPE
                    )

                    output_text = result.stdout.decode()
                    #print(output_text)

                    st.success("✅ User Stories generated successfully:")
                    pdf_data = text_to_pdf(output_text)
                    st.download_button(
                        label="📄 Download User Story as PDF",
                        data=pdf_data,
                        file_name="gemini_User_story.pdf",
                        mime="application/pdf",
                    )
                    st.text_area("📋 Generated User Stories", output_text, height=500)

        with col2:
            if st.button("🔄 Generate User Stories using GPT"):
                if full_text.strip():
                    with st.spinner("Generating user stories using GPT..."):
                        prompt_gpt = (
                            "Given the following business requirements, generate user stories in the format:\n"
                            "- As a <user>, I want to <goal> so that <reason>.\n\n"
                            f"Business Requirements:\n{full_text}\n\nUser Stories:"
                        )
                        response = llm.complete(prompt_gpt)
                        output_text_gpt = response

                    st.success("✅ User Stories generated successfully (GPT):")
                    st.text_area("📋 Generated User Stories (GPT)", output_text_gpt, height=500)

                    # Convert generated text to PDF bytes
                    pdf_data_gpt = text_to_pdf(output_text_gpt)

                    # Download button for GPT-generated PDF
                    st.download_button(
                        label="📄 Download User Story as PDF (GPT)",
                        data=pdf_data_gpt,
                        file_name="gpt_User_story.pdf",
                        mime="application/pdf",
                    )
                else:
                    st.warning("Please paste requirements or upload a file.")


elif section == "User Story":
    st.header("2️⃣ Upload User Stories")

    with st.container():
        st.markdown("**Paste your user stories below or upload a file:**")

        # Text area for manual input (independent from file upload)
        user_input_text = st.text_area(
            label="",
            placeholder="Type or paste user stories here...",
            height=200,
            key="user_stories_input",
        )

        # File uploader input (stored separately)
        us_file = st.file_uploader(
            "Or upload a file (TXT or PDF)",
            type=["txt", "pdf"],
            label_visibility="collapsed",
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

        st.text_area(
            "📄 Preview of uploaded file content (read-only):",
            value=uploaded_text,
            height=200,
            disabled=True,
        )

        # Final text source logic: Prefer manual input if not empty
        final_user_stories = user_input_text.strip() or uploaded_text.strip()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🧠 Generate Acceptance Criteria using Gemini"):
                with st.spinner("Generating Acceptance Criteria using Gemini..."):

                    # Dynamically pick the final source
                    user_stories_source = user_input_text.strip() or uploaded_text.strip()

                    if not user_stories_source:
                        st.warning("Please provide user stories via text area or file upload.")
                    else:
                        vertexai.init(
                            project="uk-labs-hackathon-1-0625-dev", location="europe-west1"
                        )
                        model = GenerativeModel("gemini-2.0-flash-001")

                        prompt = f"""
You are a senior QA engineer and business analyst working on the nCRM side of the STB customer Database
functionality for a Sky DE STB product. Based on the provided user stories, generate acceptance criteria formatted as a bullet list.
User Stories:
{user_stories_source}
Acceptance Criteria:
"""

                        response = model.generate_content(prompt)
                        output_text = response.text

                        st.success("✅ Acceptance Criteria generated successfully:")
                        pdf_data = text_to_pdf(output_text)
                        st.download_button(
                            label="📄 Download Acceptance Criteria as PDF",
                            data=pdf_data,
                            file_name="gemini_acceptance_criteria.pdf",
                            mime="application/pdf",
                        )
                        st.text_area("📋 Generated Acceptance Criteria", output_text, height=400)

        with col2:
            if st.button("🔄 Generate Acceptance Criteria using GPT"):
                if final_user_stories:
                    with st.spinner("Generating Acceptance Criteria using GPT..."):
                        prompt_gpt = f"""
Given the following user stories, generate acceptance criteria as a bullet list:

{final_user_stories}

Acceptance Criteria:
"""
                        response = llm.complete(prompt_gpt)
                        output_text_gpt = response

                    st.success("✅ Acceptance Criteria generated successfully (GPT):")
                    st.text_area("📋 Generated Acceptance Criteria (GPT)", output_text_gpt, height=400)

                    pdf_data_gpt = text_to_pdf(output_text_gpt)

                    st.download_button(
                        label="📄 Download Acceptance Criteria as PDF (GPT)",
                        data=pdf_data_gpt,
                        file_name="gpt_acceptance_criteria.pdf",
                        mime="application/pdf",
                    )
                else:
                    st.warning("Please paste user stories or upload a file.")


elif section == "Test Case Generation":
    st.header("3️⃣ Generate Test Cases")

    st.info(
        "Upload acceptance criteria or paste them below. Then generate test cases automatically."
    )

    ac_text = st.text_area(
        label="Paste Acceptance Criteria here:",
        height=300,
        key="ac_input",
    )

    ac_file = st.file_uploader(
        "Or upload a file with acceptance criteria (TXT or PDF)",
        type=["txt", "pdf"],
        label_visibility="collapsed",
    )

    ac_file_text = ""

    if ac_file:
        file_ext = ac_file.name.split(".")[-1].lower()
        if file_ext == "pdf":
            doc = fitz.open(stream=ac_file.read(), filetype="pdf")
            for page in doc:
                ac_file_text += page.get_text()
        elif file_ext == "txt":
            ac_file_text = ac_file.read().decode("utf-8")
        else:
            st.error("Unsupported file type.")

    # Combine text inputs, preferring text area over file
    acceptance_criteria_text = ac_text.strip() or ac_file_text.strip()

    if st.button("🧠 Generate Test Cases using GPT"):
        if acceptance_criteria_text:
            with st.spinner("Generating test cases using GPT..."):
                prompt_gpt = f"""
Given the following acceptance criteria, generate detailed test cases:

{acceptance_criteria_text}

Test Cases:
"""
                response = llm.complete(prompt_gpt)
                test_cases_output = response

            st.success("✅ Test cases generated successfully:")
            st.text_area("📋 Generated Test Cases", test_cases_output, height=500)

            pdf_data = text_to_pdf(test_cases_output)
            st.download_button(
                label="📄 Download Test Cases as PDF",
                data=pdf_data,
                file_name="test_cases.pdf",
                mime="application/pdf",
            )
        else:
            st.warning("Please paste acceptance criteria or upload a file.")


elif section == "Defect Handling":
    st.header("4️⃣ Defect Handling")

    defect_description = st.text_area(
        "Describe the defect:",
        height=150,
        key="defect_description",
    )

    if st.button("🐞 Generate Defect Template in JIRA format"):
        if defect_description.strip():
            with st.spinner("Generating defect template..."):
                prompt = f"""
You are a QA engineer generating a JIRA defect template. Given the defect description below, generate a JIRA defect ticket content with fields like Summary, Description, Steps to Reproduce, Expected Result, Actual Result, Severity, and Priority.

Defect Description:
{defect_description}
"""
                response = llm.complete(prompt)
                jira_ticket = response

            st.success("✅ Defect template generated:")
            st.text_area("📋 JIRA Defect Ticket", jira_ticket, height=400)
        else:
            st.warning("Please enter a defect description.")


elif section == "Root Cause Analysis":
    st.header("5️⃣ Root Cause Analysis")

    log_text = st.text_area(
        "Paste the log files or error messages here:",
        height=400,
        key="log_input",
    )

    if st.button("🔍 Analyze Logs for Root Cause"):
        if log_text.strip():
            with st.spinner("Analyzing logs..."):
                prompt = f"""
You are a senior QA engineer. Analyze the following logs and identify the most likely root cause(s) of the defect, with explanation:

Logs:
{log_text}
"""
                response = llm.complete(prompt)
                root_cause_analysis = response

            st.success("✅ Root cause analysis complete:")
            st.text_area("📋 Root Cause Analysis", root_cause_analysis, height=400)
        else:
            st.warning("Please paste log content to analyze.")
