import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import pandas as pd
from excel_formatter import auto_format_excel


load_dotenv()  # 👈 Loads vars from .env file

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version=api_version
)

# Read your requirement from file
with open("prjoectRequirementsData.txt", "r") as file:
    requirement = file.read()

 

# Prompt the model
response = client.chat.completions.create(
    model=deployment,
    messages=[
        { "role": "system", "content": "You are a senior agile product owner." },
        { "role": "user", "content": f"""
Given the following requirement, generate:
- One Epic title
- 3–5 user stories in "As a ___, I want ___ so that ___" format
- Acceptance criteria for each
- Notes (e.g., device support, edge cases)

Output in markdown table format:
| Epic | User Story | Acceptance Criteria | Notes |

Requirement:
{requirement}
"""}
    ],
    temperature=0.6,
    max_tokens=2048
)

# Parse response content (markdown table)
content = response.choices[0].message.content
rows = [line.strip().strip('|') for line in content.splitlines() if '|' in line and not line.startswith('|---')]
parsed = [row.split('|') for row in rows]

print("=== GPT Message Content ===")
print(content)
# Save as Excel
df = pd.DataFrame(parsed[1:], columns=[col.strip() for col in parsed[0]])

# Write Excel file
excel_path = "ai_user_stories_output.xlsx"
df.to_excel(excel_path, index=False)

# Format it
auto_format_excel(excel_path)

print("✅ Excel file generated: ai_stories_output.xlsx")
