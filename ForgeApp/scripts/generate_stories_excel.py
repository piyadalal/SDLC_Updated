import os
import sys
from dotenv import load_dotenv
from openai import AzureOpenAI
import pandas as pd
# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.excel_formatter import auto_format_excel

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

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

with open(os.path.join(base_dir, "data", "prjoectRequirementsData.txt"), "r") as file:
    requirement = file.read()

with open(os.path.join(base_dir, "prompts", "story_prompt.txt"), "r") as file:
    prompt_template = file.read()


# Format prompt with the actual requirement
prompt = prompt_template.replace("{requirement}", requirement)
 

# Prompt the model
response = client.chat.completions.create(
    model=deployment,
    messages=[
        { "role": "system", "content": "You are a helpful assistant that generates Jira-ready agile story breakdowns." },
        { "role": "user", "content": prompt }
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
df = df.applymap(lambda cell: (
    cell.replace("<br>", "\n")        # real line breaks in Excel
        .replace("*", "")
        .replace("**", "")
        .strip()
) if isinstance(cell, str) else cell)

# Write Excel file
excel_path = "ai_user_stories_output.xlsx"
df.to_excel(excel_path, index=False)

# Format it
auto_format_excel(excel_path)

print("✅ Excel file generated: ai_stories_output.xlsx")
