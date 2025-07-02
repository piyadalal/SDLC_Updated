import streamlit as st
from dotenv import load_dotenv
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import Settings
import os
from vertexai.preview.generative_models import GenerativeModel
import vertexai
from fpdf import FPDF
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
#st.markdown("A streamlined demo to showcase automation across the SDLC using GenAI.")
#st.divider()
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
    with cols[i*2]:
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
        with cols[i*2 + 1]:
            st.markdown(
                "<div style='font-size:2rem; text-align:center;'>&#8594;</div>",
                unsafe_allow_html=True
            )

# steps = [
#     "Business Requirements -> User Story",
#     "User Story -> Acceptance criteria",
#     "Acceptance Criteria -> Test Case Generation",
#     "Defect Handling",
#     "Defect Log file Analysis"
# ]
#
# if "current_step" not in st.session_state:
#     st.session_state["current_step"] = steps[0]
#
# # Set all button columns to the same width, and arrow columns to a small width
# button_width = 1.5
# arrow_width = 0.3
# widths = []
# for i in range(len(steps)):
#     widths.append(button_width)
#     if i < len(steps) - 1:
#         widths.append(arrow_width)
#
# cols = st.columns(widths)
# # Replace arrow markdown with a div for vertical centering
# for i, step in enumerate(steps):
#     # Button column
#     if cols[i*2].button(
#         step,
#         key=f"step_btn_{step}",
#         use_container_width=True,
#         type="primary" if st.session_state["current_step"] == step else "secondary",
#         help=step
#     ):
#         st.session_state["current_step"] = step
#         st.rerun()
#     # Arrow column (except after last button)
#     if i < len(steps) - 1:
#         with cols[i*2 + 1]:
#             st.markdown(
#                 "<div class='arrow-col' style='font-size:2rem;'>&#8594;</div>",
#                 unsafe_allow_html=True
#             )

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
            key="requirements_input"
        )
        uploaded_file = st.file_uploader(
            "Drag and drop file here\nLimit 200MB per file • TXT or PDF",
            type=["txt", "pdf"],
            label_visibility="collapsed"
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
                disabled=True
            )


            # # Save uploaded file locally
            # file_path = f"/tmp/{uploaded_file.name}"
            # with open(file_path, "wb") as f:
            #     f.write(uploaded_file.getbuffer())
            #
            # # Extract text from PDF
            # doc = fitz.open(file_path)
            # full_text = ""
            # for page in doc:
            #     full_text += page.get_text()




            # uploaded_text = uploaded_file.read().decode("utf-8")
            # st.session_state["requirements_input"] = uploaded_text
            # requirements = uploaded_text

        # if st.button("🔄 Generate User Stories", key="gen_user_stories"):
        #     if requirements.strip():
        #         with st.spinner("Generating user stories..."):
        #             prompt = (
        #                 "Given the following business requirements, generate user stories in the format:\n"
        #                 "- As a <user>, I want to <goal> so that <reason>.\n\n"
        #                 f"Business Requirements:\n{requirements}\n\nUser Stories:"
        #             )
        #             response = llm.complete(prompt)
        #             st.success("✅ Generated User Stories:")
        #             st.text(response)
        #     else:
        #         st.warning("Please paste requirements or upload a file.")
            # Create two columns for buttons side-by-side
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🧠 Generate User Stories using Gemini"):
                    with st.spinner("Generating user stories using Gemini"):
                        vertexai.init(project="uk-labs-hackathon-1-0625-dev", location="europe-west1")
                        model = GenerativeModel("gemini-2.0-flash-001")
                        acceptance_criteria = """
                                               As a User of a STB, I want to be able to 
                                               """

                        prompt = f"""
                               You are a senior QA engineer and business analyst working on the nCRM side of the STB customer Database
                               functionality for a Sky DE STB product. Based on the provided product requirements, generate:
                               1. One or more **User Stories** (formatted with territory/platform, user role, and business goal). 
                               Here is how the requirements looks like :
                               {full_text}
                               """
                        response = model.generate_content(prompt)
                        output_text = response.text

                        st.success("✅ User Stories generated successfully:")
                        pdf_data = text_to_pdf(output_text)
                        st.download_button(
                            label="📄 Download User Story as PDF",
                            data=pdf_data,
                            file_name="gemini_User_story.pdf",
                            mime="application/pdf"
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
                                mime="application/pdf"
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
            key="user_stories_input"
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


    # if st.button("🧪 Generate Test Cases using gpt", key="gen_test_cases"):
    #         if user_stories.strip():
    #             with st.spinner("Generating test cases using gpt..."):
    #                 prompt = (
    #                     "Given the following user stories, generate test cases in the format:\n"
    #                     "- Positive: ...\n- Negative: ...\n- Boundary: ...\n\n"
    #                     f"User Stories:\n{user_stories}\n\nTest Cases:"
    #                 )
    #                 response = llm.complete(prompt)
    #                 st.success("✅ Test Cases:")
    #                 st.text(response)
    #         else:
    #             st.warning("Please paste user stories or upload a file.")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧠 Generate Acceptance Criteria using Gemini"):
            with st.spinner("Generating Acceptance Criteria using Gemini..."):

                # Dynamically pick the final source
                user_stories_source = user_input_text.strip() or uploaded_text.strip()

                if not user_stories_source:
                    st.warning("Please provide user stories via text area or file upload.")
                else:
                    vertexai.init(project="uk-labs-hackathon-1-0625-dev", location="europe-west1")
                    model = GenerativeModel("gemini-2.0-flash-001")

                    prompt = f"""
                    You are a senior QA engineer and business analyst working on the nCRM side of the STB customer Database
                               functionality for a Sky DE STB product. Based on the provided user stories, generate:
                    1. For each User Story, provide **detailed Acceptance Criteria** strictly in the 
                    "Given / When / Then" format, with no AND statements.

                    Here are the user stories:
                    {user_stories_source}
                    """

                    response = model.generate_content(prompt)
                    output_text = response.text

                st.success("✅ Acceptance Criteria generated successfully:")
                pdf_data = text_to_pdf(output_text)
                st.download_button(
                    label="📄 Download Acceptance Criteria as PDF",
                    data=pdf_data,
                    file_name="gemini_Acceptance_Criteria.pdf",
                    mime="application/pdf"
                )
                st.text_area("📋 Generated Acceptance Criteria", output_text, height=500)

    with col2:
        if st.button("🔄 Generate Acceptance Criteria using GPT"):
            # Choose from user input text area or uploaded text
            input_text = user_input_text.strip() or uploaded_text.strip()

            if input_text:
                with st.spinner("Generating acceptance criteria using GPT..."):
                    prompt_gpt = (
                        "Given the following business requirements, generate user stories in the format:\n"
                        "- As a <user>, I want to <goal> so that <reason>.\n\n"
                        f"Business Requirements:\n{input_text}\n\nUser Stories:"
                    )
                    response = llm.complete(prompt_gpt)
                    output_text_gpt = response

                    st.success("✅ Acceptance criteria generated successfully (GPT):")
                    st.text_area("📋 Generated Acceptance Criteria (GPT)", output_text_gpt, height=500)
                    # Convert generated text to PDF bytes
                    pdf_data_gpt = text_to_pdf(output_text_gpt.text)

                    # Download button for GPT-generated PDF
                    st.download_button(
                        label="📄 Download Acceptance Criteria as PDF (GPT)",
                        data=pdf_data_gpt,
                        file_name="gpt_acceptance_criteria.pdf",
                        mime="application/pdf"
                    )
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