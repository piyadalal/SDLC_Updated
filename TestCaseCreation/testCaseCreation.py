from openai import AzureOpenAI
from dotenv import load_dotenv
import os


load_dotenv()  # 👈 Loads vars from .env file

openai_api_endpoint = os.getenv("OPENAI_ENDPOINT")
openai_deployment = os.getenv("OPENAI_DEPLOYMENT")
openai_api_version = os.getenv("OPENAI_API_VERSION")
openai_api_key = os.getenv("OPENAI_API_KEY")

ai_client = AzureOpenAI(
    api_key=openai_api_key,
    api_version=openai_api_version,
    azure_endpoint=openai_api_endpoint
)

# Read your Acceptance criteria from file
with open("acceptance_criterias.txt", "r") as file:
    acc_criteria = file.read()


response = ai_client.chat.completions.create(
    model=openai_deployment,
    messages=[{"role": "system", "content": "You are a QA assitant."},
              {"role": "user", "content": f"""Read the acceptance criteria and generate test cases like below format. Format:"
- Description
- Preconditions
- Steps and Expected Results:
  For each step, provide:
  - Step [number]: [action]
  - Expected Result: [expected result]

Acceptance_criteria:
{acc_criteria}
"""}]
)

print(response.choices[0].message.content)
