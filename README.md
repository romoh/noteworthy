# Noteworthy

📝 AI-powered, customizable release notes for git repos. Because every commit deserves to be Noteworthy.

 ![Project Logo](assets/logo.png)

## Getting Started

```bash
# Clone the repo
git clone https://github.com/romoh/noteworthy.git
cd noteworthy

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the tool
PYTHONPATH=src python -m noteworthy.main --shoutout --highlights --output-format markdown --output-file release_notes.md --repo-url https://github.com/owner/repo

# Run tests
 PYTHONPATH=src pytest tests/test.py -s
```

## 🚀 AI-Powered Release Notes with Azure OpenAI

This project uses Azure OpenAI and LangGraph to generate human-readable, categorized release notes from your commit history.

### Setup Azure OpenAI

1. **Deploy a model** in your Azure OpenAI resource (e.g., gpt-35-turbo or gpt-4).
2. **Get your credentials:**
   - API Key
   - Endpoint (e.g., https://YOUR-RESOURCE-NAME.openai.azure.com/)
   - Deployment name (the name you gave your model deployment)
   - API version (e.g., 2023-05-15)
3. **Set the following environment variables:**

```bash
export AZURE_OPENAI_API_KEY=your-azure-key
export AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE-NAME.openai.azure.com/
export AZURE_OPENAI_DEPLOYMENT=your-deployment-name
export AZURE_OPENAI_API_VERSION=2023-05-15
```

### Run the Release Notes Generator

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the generator (example):
```bash
python -m src.noteworthy.main --repo-url https://github.com/owner/repo --from-tag v1.0.0 --to-tag v1.1.0 --shoutout
```

The tool will use Azure OpenAI under the hood to generate and format your release notes!
