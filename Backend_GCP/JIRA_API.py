import pdfplumber
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()  # 👈 Loads vars from .env file
endpoint = os.getenv("JIRA_API_ENDPOINT")
api_key = os.getenv("JIRA_API_TOKEN")
pdf_path = "sample_jira_bug.pdf"

# === Step 1: Extract fields from PDF ===
def extract_fields_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + '\n'

    # Dummy extraction: You’ll need proper parsing logic here
    fields = {}
    lines = text.splitlines()
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


# === Step 2: Format the JIRA payload ===
def prepare_jira_payload(fields):
    payload = {
        "fields": {
            "project": {
                "key": "DP"
            },
            "issuetype": {
                "name": "Bug"  # Q1: Bug, Task, etc.
            },
            "summary": "Video fails to play on HDMI input - regression",  # Q5
            "description": "Steps to reproduce:\n1. Open the app\n2. Click the button\nExpected: X\nActual: Y",
            # ✅ should be a string, not a set
            "priority": {
                "name": "Medium"  # Q2
            },
            "labels": [
                "Regression", "STB", "New_Test-New_Functionality"  # ✅ should be a list of strings
            ],
            "components": [
                {"name": "Defect_scrub"}  # ✅ list of dicts
            ],
            "environment": "DTH Sky Q"  # ✅ plain string
        }
    }

    return payload


# === Step 3: Create JIRA ticket ===
def create_jira_ticket(jira_url, auth, payload):
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"{jira_url}/rest/api/2/issue",
        headers=headers,
        auth=auth,
        data=json.dumps(payload)
    )
    if response.status_code == 201:
        print("✅ JIRA Bug Created:", response.json()["key"])
    else:
        print("❌ Failed to create bug:", response.status_code, response.text)


# === MAIN EXECUTION ===
if __name__ == "__main__":
  # Path to your PDF with 18 fields
    auth = ("piya21294@gmail.com", api_key)  # Use API token, not password
    fields = extract_fields_from_pdf(pdf_path)
    payload = prepare_jira_payload(fields)
    create_jira_ticket(endpoint, auth, payload)
