from fpdf import FPDF
import re
import pdfplumber
import vertexai
from vertexai.preview.generative_models import GenerativeModel

vertexai.init(project="uk-labs-hackathon-1-0625-dev", location="europe-west1")

model = GenerativeModel("gemini-2.0-flash-001")
#full_text = open("WatchList.pdf", "r").read()
file_path = "log_file.pdf"



def stream_and_filter_log(file_path, pattdef extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file and returns as a string."""
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_textern=r"ERROR"):
    """Yields lines from a log file (PDF or plain text) matching the regex pattern."""
    regex = re.compile(pattern, re.IGNORECASE)

    if file_path.endswith(".pdf"):
        print("Detected PDF log file. Extracting text...")
        full_text = extract_text_from_pdf(file_path)
        lines = full_text.splitlines()
    else:
        print("Detected plain text log file. Reading directly...")
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

    for line in lines:
        if regex.search(line):
            yield line.strip()

def chunk_lines(lines, max_chars=8000):
    """Yields chunks of lines up to max_chars."""
    chunk = []
    total_chars = 0
    for line in lines:
        if total_chars + len(line) > max_chars:
            yield "\n".join(chunk)
            chunk = []
            total_chars = 0
        chunk.append(line)
        total_chars += len(line)
    if chunk:
        yield "\n".join(chunk)

def analyze_log_chunks(chunks, model):
    """Sends each chunk to Gemini and prints the analysis. Also saves PDF report."""
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
        response = model.generate_content(prompt)
        output_text = response.text
        print(output_text)

        for line in output_text.split("\n"):
            pdf.multi_cell(0, 10, line)

    pdf.output("gemini_analysis_report.pdf")
    print("✅ PDF report saved as 'gemini_analysis_report.pdf'")

# === MAIN USAGE ===
def run_analysis():
    vertexai.init(project="uk-labs-hackathon-1-0625-dev", location="europe-west1")
    model = GenerativeModel("gemini-2.0-flash-001")
    filtered_lines = stream_and_filter_log(file_path, pattern=r"ERROR|404|No signal")
    chunks = chunk_lines(filtered_lines, max_chars=8000)
    analyze_log_chunks(chunks, model)

if __name__ == "__main__":
    run_analysis()
