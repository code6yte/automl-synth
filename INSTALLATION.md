# INSTALLATION.md — Installation and Requirements

## Installation Goals

Installation must fully satisfy runtime requirements for:

- CLI command
- FastAPI server
- LLM provider calls
- DuckDuckGo-style search
- CSV export
- JSONL export
- PDF export
- Dashboard serving

## End User Installation

Preferred:

```bash
pipx install git+https://github.com/<owner>/automl-synth.git
```

Curl installer:

```bash
curl -fsSL https://raw.githubusercontent.com/<owner>/automl-synth/main/install.sh | bash
```

Local development:

```bash
git clone https://github.com/<owner>/automl-synth.git
cd automl-synth
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## install.sh Requirements

The installer must:

1. Detect OS.
2. Verify Python 3.11+.
3. Install pipx if missing.
4. Run `python -m pipx ensurepath`.
5. Install package using pipx.
6. Verify `automl-synth --help` works.
7. Run `automl-synth doctor`.
8. Print `.env` setup instructions.

## Python Dependency Installation

Dependencies must be declared in `pyproject.toml`, not manually installed one by one.

Required dependencies:

```text
typer[all]
rich
fastapi
uvicorn[standard]
pydantic
pydantic-settings
python-dotenv
httpx
pandas
ddgs
reportlab
platformdirs
```

These satisfy:

- CLI
- API server
- config
- HTTP LLM calls
- dataset handling
- search
- PDF export
- user config path

## Frontend Build Requirement

For end users, the package should include prebuilt dashboard static files:

```text
automl_synth/dashboard/dist/
```

If dashboard static files are included, Node.js is not required for end users.

For developers who modify dashboard:

```bash
cd frontend
npm install
npm run build
```

Then copy build output into:

```text
automl_synth/dashboard/dist/
```

## API Key Setup

The installer must not ask for API key interactively unless simple prompt mode is implemented.

Instead, print:

```bash
export LLM_PROVIDER=openrouter
export LLM_BASE_URL=https://openrouter.ai/api/v1
export LLM_API_KEY="your_key_here"
export LLM_MODEL="openrouter/free"
```

Or create config file:

```text
~/.config/automl-synth/.env
```

## Doctor Command Requirements

`automl-synth doctor` must check:

- Python version
- package version
- output directory write permission
- LLM provider settings
- API key presence for OpenRouter
- LLM endpoint reachability
- search package import
- PDF export availability
- dashboard static files availability

Doctor should not fail just because API key is missing. It should show:

```text
LLM provider: not configured
Status: action required
```

## Offline Behavior

If OpenRouter key is missing and Ollama is not configured:

- CLI should not crash during doctor.
- Generate command should return a clear error:

```text
No working LLM provider configured. Set LLM_API_KEY or configure Ollama/custom provider.
```

## Search Installation

Search dependency is installed through package dependency:

```text
ddgs
```

No browser driver, Selenium, Playwright, or external search engine binary should be required.

## Installer Must Not

- Install Ollama automatically.
- Install Node for end users.
- Modify shell profile aggressively.
- Run arbitrary generated commands.
- Store API keys in frontend files.
