# TOOLS.md — Required Tools and Dependencies

## Runtime Requirements

Required:

- Python 3.11+
- pip
- pipx recommended for global CLI installation
- Internet access for OpenRouter and web search
- OpenRouter API key or another OpenAI-compatible API key

Optional:

- Node.js 20+ only if building the dashboard from source
- npm only if building the React dashboard
- Ollama only if user chooses local/custom LLM mode

## Python Dependencies

Recommended package dependencies:

```toml
dependencies = [
  "typer[all]",
  "rich",
  "fastapi",
  "uvicorn[standard]",
  "pydantic",
  "pydantic-settings",
  "python-dotenv",
  "httpx",
  "pandas",
  "ddgs",
  "reportlab",
  "platformdirs",
]
```

Optional dev dependencies:

```toml
[project.optional-dependencies]
dev = [
  "pytest",
  "ruff",
  "mypy",
  "types-requests",
]
```

## Frontend Dependencies

React dashboard:

```json
{
  "dependencies": {
    "@vitejs/plugin-react": "latest",
    "vite": "latest",
    "react": "latest",
    "react-dom": "latest",
    "lucide-react": "latest"
  },
  "devDependencies": {
    "typescript": "latest"
  }
}
```

Tailwind/shadcn can be added if already comfortable, but do not make it a blocker.

## LLM Providers

### OpenRouter
Default provider.

Configuration:

```env
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=your_key_here
LLM_MODEL=openrouter/free
```

OpenRouter exposes an API reference and chat completion endpoint compatible with standard HTTP requests.

### Ollama / Custom Local Provider
Optional provider.

Configuration:

```env
LLM_PROVIDER=ollama
LLM_BASE_URL=http://127.0.0.1:11434
LLM_API_KEY=
LLM_MODEL=llama3.2:1b
```

Do not require Ollama during installation.

## Search Tool
Use DuckDuckGo-compatible Python search package.

Preferred:

```text
ddgs
```

Fallback allowed:

```text
duckduckgo-search
```

Search module must fail gracefully if web search fails. The LLM can still use the topic alone.

## PDF Tool
Use:

```text
reportlab
```

PDF must be a Dataset Card, not a research paper.

## Installation Tooling

Support:

```bash
pipx install .
```

and:

```bash
curl -fsSL https://raw.githubusercontent.com/<owner>/<repo>/main/install.sh | bash
```

The install script must:

1. Check Python 3.11+.
2. Install pipx if missing.
3. Ensure pipx path.
4. Install AutoML-Synth package.
5. Verify command exists.
6. Run `automl-synth doctor`.
7. Print next steps for setting API key.

## What Installer Must Install

The Python package installation must install:

- FastAPI
- Uvicorn
- Typer
- Rich
- pandas
- pydantic
- python-dotenv
- httpx
- ddgs or DuckDuckGo search package
- reportlab
- platformdirs

The installer must not require Node unless dashboard source needs to be built.

If dashboard static build is already included in the package, Node is not required for end users.
