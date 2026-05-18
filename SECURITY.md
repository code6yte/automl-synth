# SECURITY.md — Security and Safety Rules

## API Key Safety

- Never store API keys in React source.
- Never return API keys from API endpoints.
- Read API keys only in backend config.
- `.env` must be ignored by Git.
- Provide `.env.example` only.

## LLM Tool Safety

The LLM cannot execute arbitrary system tools.

Allowed actions:

- produce JSON research plan
- produce generated text examples
- summarize quality warnings

Disallowed actions:

- shell command execution
- file deletion
- package installation
- OS modification
- reading arbitrary local files
- writing outside output directory

## Output Directory Safety

All generated files must be written only inside:

- user-specified output folder, or
- AutoML-Synth cache/run folder

Sanitize file paths.

## Data Safety

Generated data is synthetic. The report must include limitation text:

```text
This dataset is synthetic and intended for education, prototyping, and experimentation. It should not be used for safety-critical, medical, legal, financial, or production decision systems without real-world validation.
```

## Web Search Safety

Web search snippets are used as context only. The app must not scrape or redistribute full copyrighted pages.

## PDF Safety

PDF report should include generated samples and metadata only, not full web pages.
