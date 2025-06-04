# Forge App - AI PM

## Run Python script locally

### Prerequisites

cd into ForgeApp folder

Create `.env` file with the following content:

```env
AZURE_OPENAI_ENDPOINT=https://2946-ai-project-management.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_KEY=use_your_api_key
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
```

### Installation:

cd into ForgeApp/scripts folder and run following commands

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install openai pandas dotenv openpyxl
python generate_stories_excel.py
```
