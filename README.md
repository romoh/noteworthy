# NoteWorthy - AI-powered customizable release notes generator. Because every commit deserves to be Noteworthy.

<div align="center">
  <img src="assets/logo.png" alt="NoteWorthy Logo" width="180"/>
</div>

## Features
- Generates human-readable, categorized release notes from commit history
- Uses AI (LangGraph + Azure OpenAI or OpenAI) for smart summarization
- Supports Markdown, HTML, and plain text output
- Contributor shoutouts

## Requirements
- Python 3.9+
- [Poetry](https://python-poetry.org/) or `pip` for dependencies

## Environment Variables

| Variable                  | Description                                                      | Example/Default                |
|---------------------------|------------------------------------------------------------------|--------------------------------|
| `LLM_BACKEND`             | LLM backend to use: `azure` (default) or `openai`                | `azure`                        |
| `AZURE_AUTH`              | Azure auth: `aad` (default, uses Entra ID) or `key` (API key)    | `aad`                          |
| `AZURE_OPENAI_DEPLOYMENT` | Azure deployment name                                            | `noteworthy`                   |
| `AZURE_OPENAI_ENDPOINT`   | Azure OpenAI endpoint                                            | `https://...azure.com/`        |
| `AZURE_OPENAI_API_KEY`    | Azure OpenAI API key (if using `AZURE_AUTH=key`)                 |                                |
| `AZURE_OPENAI_API_VERSION`| Azure OpenAI API version                                         | `2023-05-15`                   |
| `OPENAI_API_KEY`          | OpenAI API key (if using `LLM_BACKEND=openai`)                   |                                |

## Usage

### 1. **Azure OpenAI (default)**
Set these variables (AAD auth is default):
```sh
export AZURE_OPENAI_DEPLOYMENT=noteworthy
export AZURE_OPENAI_ENDPOINT=https://<your-endpoint>.openai.azure.com/
export AZURE_OPENAI_API_VERSION=2023-05-15
# For AAD auth (default):
export LLM_BACKEND=azure
export AZURE_AUTH=aad
# For API key auth:
# export AZURE_AUTH=key
# export AZURE_OPENAI_API_KEY=your-azure-openai-api-key
```

### 2. **OpenAI**
Set these variables:
```sh
export LLM_BACKEND=openai
export OPENAI_API_KEY=your-openai-api-key
```

### 3. **Run the tool**
```sh
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

PYTHONPATH=src python -m noteworthy.main --repo-url https://github.com/owner/repo
```

See `--help` for all CLI options.

---

## Example
```sh
PYTHONPATH=src python -m noteworthy.main \
  --repo-url https://github.com/microsoft/azurelinux \
  --output-format markdown \
  --output-file output/release_notes.md \
  --from-tag v0.14.0 --to-tag v0.15.0
```

## Tests

To run the tests, use:
```sh
PYTHONPATH=src pytest tests/test.py -s
```

---

## License
MIT
