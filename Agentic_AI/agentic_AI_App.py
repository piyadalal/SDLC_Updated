import streamlit as st
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.prompts import PromptTemplate
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain_google_vertexai import VertexAI

# Initialize your LLM
llm = VertexAI(model_name="models/gemini-2.0-flash-001")  # or your model name

# Define prompts
story_prompt = PromptTemplate.from_template(
    "Given the following requirement:\n\n{requirement}\n\nGenerate user stories with acceptance criteria."
)

testcase_prompt = PromptTemplate.from_template(
    "Given the user story:\n\n{story}\n\nGenerate detailed test cases including steps and expected results."
)

log_analysis_prompt = PromptTemplate.from_template(
    "Analyze the following log and determine if it indicates a defect:\n\n{log}\n\nGive a summary of the defect if any."
)

# Define tool functions
def generate_user_stories(requirement: str) -> str:
    prompt = story_prompt.format(requirement=requirement)
    return llm(prompt)

def generate_test_cases(story: str) -> str:
    prompt = testcase_prompt.format(story=story)
    return llm(prompt)

def analyze_logs(log: str) -> str:
    prompt = log_analysis_prompt.format(log=log)
    return llm(prompt)

# Setup tools
tools = [
    Tool(name="GenerateUserStories", func=generate_user_stories, description="Generate user stories from a requirement."),
    Tool(name="GenerateTestCases", func=generate_test_cases, description="Generate test cases from a user story."),
    Tool(name="AnalyzeLogs", func=analyze_logs, description="Analyze logs for potential defects."),
    PythonREPLTool()  # Optional: lets the agent run Python code
]

# Initialize agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False  # You can set True to debug
)

# Streamlit UI
st.title("Agentic AI: Testcase & Log Analysis Tool")

requirement_input = st.text_area("Enter Requirement:", height=150)
log_input = st.text_area("Enter Logs:", height=150)

if st.button("Run Agentic AI"):
    if requirement_input.strip() == "":
        st.warning("Please enter a requirement.")
    else:
        # Compose prompt for agent
        query = (
            f"Generate user stories, test cases, and analyze these logs: {log_input} "
            f"for this requirement: {requirement_input}"
        )
        with st.spinner("Running agent..."):
            result = agent.run(query)
        st.subheader("Agent Output")
        st.text_area("Result", value=result, height=300)
