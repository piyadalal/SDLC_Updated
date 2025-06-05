import openai
import os
from dotenv import load_dotenv
import sys
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import json

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()  # 👈 Loads vars from .env file

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")



client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version=api_version
)

response = client.embeddings.create(
    input=["first phrase","second phrase","third phrase"],
    model=deployment
)

def generate_ac_tc(requirement_text: str):
    prompt = (
        "You are a software QA expert.\n"
        "Given the high-level requirement below, generate:\n"
        "1. A list of clear Acceptance Criteria.\n"
        "2. Corresponding Test Cases for each acceptance criteria.\n\n"
        f"Requirement: {requirement_text}\n\n"
        "Output as JSON with keys 'acceptance_criteria' (list of strings) and 'test_cases' (list of strings).\n"
    )

    response = openai.ChatCompletion.create(
        engine=deployment,  # ✅ Not deployment_name
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except Exception as e:
        print("Failed to parse JSON output:", e)
        print("Raw content:", content)
        return None



def get_embedding(text: str):
    response = client.embeddings.create(
        deployment_name=embedding_deployment,
        input=text
    )
    return response.data[0].embedding





search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(search_api_key)
)

def upload_documents(requirement, ac_list, tc_list):
    documents = []
    for i, (ac, tc) in enumerate(zip(ac_list, tc_list)):
        ac_emb = get_embedding(ac)
        tc_emb = get_embedding(tc)
        documents.append({
            "id": f"ac-{i}",
            "requirement": requirement,
            "type": "acceptance_criteria",
            "content": ac,
            "contentVector": ac_emb
        })
        documents.append({
            "id": f"tc-{i}",
            "requirement": requirement,
            "type": "test_case",
            "content": tc,
            "contentVector": tc_emb
        })

    result = search_client.upload_documents(documents)
    print(f"Uploaded {len(documents)} documents:", result)


def main():
    requirement = input("Enter a high-level requirement: ")
    result = generate_ac_tc(requirement)
    if not result:
        print("Failed to generate AC and TC.")
        return
    ac_list = result.get("acceptance_criteria", [])
    tc_list = result.get("test_cases", [])
    print("Acceptance Criteria:", ac_list)
    print("Test Cases:", tc_list)

    upload_documents(requirement, ac_list, tc_list)

if __name__ == "__main__":
    main()
