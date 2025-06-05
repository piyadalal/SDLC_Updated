from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import re
from openpyxl import Workbook
import fitz


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
#with open("WatchList User Stories and Accep_12141b9615ce444a83dee70f5db808cd-050625-1222-276.pdf", "r") as file:
#    acc_criteria = file.read()

with fitz.open("WatchList User Stories and Accep_12141b9615ce444a83dee70f5db808cd-050625-1222-276.pdf") as doc:
    acc_criteria = ""
    for page in doc:
        acc_criteria += page.get_text()

response = ai_client.chat.completions.create(
    model=openai_deployment,
    messages=[{"role": "system", "content": "You are a QA assitant."},
              {"role": "user", "content": f"""Read the user stories, acceptance criteria and generate test cases in a table format. Each test case should include step-by-step actions and each step with expected results. Include both positive and negative test cases, and consider edge cases where applicable. Format the output as a table with columns: 'Test Case ID', 'Test Scenario', 'Step', 'Expected Result'"

Acceptance_criteria:
{acc_criteria}
"""}]
)

print(response.choices[0].message.content)

content = response.choices[0].message.content



# === Parse the test cases ===
test_cases = []

# Split by each test case
blocks = re.split(r"#### Test Case \d+:", content)

for block in blocks[1:]:  # First split is empty before the first test case
    #print("block 1")
    title_match = re.match(r" \*\*(.+?)\*\*", block)
    #print(title_match)
    title = title_match.group(1).strip() if title_match else "Untitled"

    description = re.search(r"- \*\*Description:\*\*\s*(.+)", block)
    preconditions = re.search(r"- \*\*Preconditions:\*\*\s*(.+)", block)
    steps_block = re.search(r"- \*\*Test Steps:\*\*(.+)", block, re.DOTALL)
    #print(description, preconditions, steps_block)

    description = description.group(1).strip() if description else ""
    preconditions = preconditions.group(1).strip() if preconditions else ""
    steps_text = steps_block.group(1).strip() if steps_block else ""
    #print("Stripped output")
    #print(description, preconditions, steps_text)

    # Find steps and expected results
    step_pattern = re.findall(r"\d+\.\s+(.*?)\n\s*- \*\*Expected Result:\*\*\s*(.*?)\n?", steps_text, re.DOTALL)

    for i, (action, expected) in enumerate(step_pattern, start=1):
        test_cases.append([
            f"TC-{len(test_cases)+1:03}",
            title,
            description,
            preconditions,
            f"Step {i}",
            action.strip().replace("\n", " "),
            expected.strip().replace("\n", " ")
        ])

# === Write to Excel ===
wb = Workbook()
ws = wb.active
ws.title = "Test Cases"

# Write headers
ws.append(["Test Case ID", "Title", "Description", "Preconditions", "Step #", "Action", "Expected Result"])

# Write rows
for row in test_cases:
    ws.append(row)

# Save file
output_file = "structured_test_cases.xlsx"
wb.save(output_file)
print(f"✅ Test cases saved to: {output_file}")
