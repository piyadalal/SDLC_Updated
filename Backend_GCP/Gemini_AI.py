
from fpdf import FPDF
import fitz  # PyMuPDF
from vertexai.preview.generative_models import GenerativeModel
import vertexai
vertexai.init(project="uk-labs-hackathon-1-0625-dev", location="europe-west1")

model = GenerativeModel("gemini-2.0-flash-001")
#full_text = open("WatchList.pdf", "r").read()
pdf_file = "WatchList.pdf"
doc = fitz.open(pdf_file)

full_text = ""
for page in doc:
    full_text += page.get_text()

acceptance_criteria = """
As a User of a STB, I want to be able to Add and Remove Items to my WatchList from any ShowPage
"""


prompt = f"""
You are a senior QA engineer and business analyst working on the WatchList functionality for a Sky DE STB product. Based on the provided product requirements, generate:

1. One or more **User Stories** (formatted with territory/platform, user role, and business goal).
2. For each User Story, provide **detailed Acceptance Criteria** in the "Given / When / Then" format and no so many "And" statements.
3. For each Acceptance Criterion, generate one or more **E2E test cases** in this format:

Test Case: [Clear and descriptive title]

| Test Step | Action                                                                 | Expected Result                                      |
|-----------|------------------------------------------------------------------------|------------------------------------------------------|
| Step 1    | [Describe the user action clearly]                                     | [Describe what the system should do or show]        |
| Step 2    | [Next step, continuing the user flow]                                  | [Next expected outcome]                             |
| ...       | ...                                                                    | ...                                                  |


4. Match the level of detail and formal tone used in the WatchList documentation.

Use the following prompt input to drive the feature definition:

> As a User of Sky DE STB, I want to be able to Add and Remove Items to my WatchList from any ShowPage
.
Here is how the requirements looks like :
{full_text}

"""

response = model.generate_content(prompt)
print(response.text)
output_text = response.text

pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_font("Arial", size=12)


for line in output_text.split("\n"):
    pdf.multi_cell(0, 10, line)


pdf.output("gemini_response.pdf")

print("PDF saved as gemini_response.pdf")


