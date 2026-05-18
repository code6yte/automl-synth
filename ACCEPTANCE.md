# ACCEPTANCE.md — Final Acceptance Criteria

## Must Pass

### CLI

Command:

```bash
automl-synth generate --topic "Classify news headlines into politics, sports, technology, entertainment, and business" --rows 250 --out ./out
```

Must create:

```text
out/dataset.csv
out/dataset.jsonl
out/dataset-card.pdf
out/quality-report.json
out/research-report.json
```

### Dataset

CSV must include:

```text
id,text,label,topic,source_agent,difficulty,synthetic_quality_score
```

### Quality

Quality report must include:

```text
quality_score
quality_grade
label_distribution
class_balance_ratio
duplicate_rows
label_leakage_rows
repeated_fragment_groups
warnings
```

### Domain Correctness

For news topic, sample rows must look like news headlines.

For app reviews, sample rows must look like user app reviews.

For support tickets, sample rows must look like support tickets.

### Dashboard

Command:

```bash
automl-synth serve
```

Must open a working dashboard at:

```text
http://127.0.0.1:8000
```

### Doctor

Command:

```bash
automl-synth doctor
```

Must check:

- Python version
- package install
- LLM config
- search import
- PDF export
- output folder permission
- dashboard files

## Must Not Include

- AutoML trainer
- prediction tester
- F1/accuracy metrics
- scikit-learn requirement
- model download
- login/database
