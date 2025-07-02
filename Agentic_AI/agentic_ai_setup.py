from vertexai.preview.generative_models import GenerativeModel
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
#from langchain.llms import GooglePalm
from langchain.prompts import PromptTemplate
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain_google_vertexai import VertexAI


llm = VertexAI(model_name="models/gemini-2.0-flash-001")  # or your model name



# Step 1: Setup Gemini LLM (GooglePalm)
# Make sure you set GOOGLE_API_KEY in your environment.
#llm = GooglePalm(temperature=0.3)
#llm = GenerativeModel("gemini-2.0-flash-001")

# Step 2: Define prompts for each task
story_prompt = PromptTemplate.from_template(
    "Given the following requirement:\n\n{requirement}\n\nGenerate user stories with acceptance criteria."
)

testcase_prompt = PromptTemplate.from_template(
    "Given the user story:\n\n{story}\n\nGenerate detailed test cases including steps and expected results."
)

log_analysis_prompt = PromptTemplate.from_template(
    "Analyze the following log and determine if it indicates a defect:\n\n{log}\n\nGive a summary of the defect if any."
)

# Step 3: Wrap prompt calls as tools
def generate_user_stories(requirement: str) -> str:
    prompt = story_prompt.format(requirement=requirement)
    return llm(prompt)

def generate_test_cases(story: str) -> str:
    prompt = testcase_prompt.format(story=story)
    return llm(prompt)

def analyze_logs(log: str) -> str:
    prompt = log_analysis_prompt.format(log=log)
    return llm(prompt)

tools = [
    Tool(name="GenerateUserStories", func=generate_user_stories, description="Generate user stories from a requirement."),
    Tool(name="GenerateTestCases", func=generate_test_cases, description="Generate test cases from a user story."),
    Tool(name="AnalyzeLogs", func=analyze_logs, description="Analyze logs for potential defects."),
    PythonREPLTool()  # Optional: lets the agent run Python code
]

# Step 4: Build the agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Step 5: Run it
requirement_input = "The system shall allow users to reset their password via a secure email link."
log_input = "[Error: password reset token expired]"

agent.run(
    f"Generate user stories, test cases, and analyze these logs: {log_input} for this requirement: {requirement_input}"
)
