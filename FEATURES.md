# FEATURES.md — Feature Specification

## MVP Features

### 1. Topic Input
User enters any text classification topic.

Examples:

```text
Classify news headlines into politics, sports, technology, entertainment, and business
```

```text
Classify mobile app reviews into praise, bug_report, feature_request, usability_issue, and pricing_complaint
```

### 2. Web-Assisted Research
The Research Agent performs a web search and gives snippets to the LLM.

The LLM returns:

- task type
- labels
- label descriptions
- patterns
- seed examples
- common confusions

### 3. Synthetic Dataset Generation
The Generator Agent creates labeled text rows.

It must generate domain-correct examples.

News topic → headlines.

App review topic → user reviews.

Support ticket topic → support messages.

Toxic comment topic → comments.

### 4. Dataset Cleaning
Remove:

- empty rows
- duplicates
- too-short text
- meta-language
- label leakage
- repeated fragments

### 5. Dataset Quality Analysis
Show:

- total rows
- labels
- rows per label
- class balance ratio
- duplicate rows
- missing values
- average words
- unique text ratio
- meta-language rows
- label leakage rows
- repeated fragments
- source-agent distribution
- difficulty distribution
- final quality score
- warnings

### 6. Dataset Preview
Show sample rows grouped by label.

### 7. Export
Export:

- CSV
- JSONL
- PDF Dataset Card
- JSON quality report
- JSON research report

### 8. Dashboard
Dashboard has:

- search-style topic input
- generation progress
- label summary
- quality score cards
- table preview
- downloads

### 9. CLI
CLI supports:

```bash
automl-synth generate
```

```bash
automl-synth serve
```

```bash
automl-synth doctor
```

## Feature Priorities

Priority 1:

- CLI generate
- provider config
- research agent
- generator agent
- cleaning
- quality analysis
- CSV/JSONL/PDF export

Priority 2:

- FastAPI server
- dashboard static serving
- React dashboard

Priority 3:

- curl install script
- better doctor command
- tests and README

## Explicitly Excluded Features

Do not build:

- AutoML training
- prediction testing
- model metrics
- LLM fine-tuning
- login/accounts
- database storage
- dataset sharing marketplace
- arbitrary command execution
