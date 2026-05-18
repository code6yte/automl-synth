# QUALITY.md — Dataset Quality Analysis Specification

## Purpose
Quality Analysis Agent evaluates the generated dataset without training any model.

## Metrics

### Basic Metrics

- total rows
- number of labels
- rows per label
- missing values
- duplicate rows

### Text Metrics

- average text length
- average word count
- vocabulary size
- unique text ratio

### Balance Metrics

- minimum class count
- maximum class count
- class balance ratio

### Synthetic Quality Metrics

- meta-language rows
- label leakage rows
- repeated fragment groups
- max fragment reuse
- difficulty distribution
- source-agent distribution

## Quality Score

Start at 100.

Penalties:

```text
class balance ratio < 0.80: -15
duplicate rows: up to -20
missing values: -15
average word count < 6: -10
unique text ratio < 0.90: -10
meta-language rows: up to -20
label leakage rows: up to -20
repeated fragments: up to -15
single source-agent only: -8
ambiguous examples < 20%: -8
```

Clamp score between 0 and 100.

## Grades

```text
90–100: Excellent
75–89: Good
60–74: Fair
0–59: Needs Improvement
```

## Warning Examples

```text
Class distribution is not balanced.
Some rows contain label names inside the text.
Repeated text fragments were detected.
Dataset has low text uniqueness.
Some rows look like descriptions rather than natural text.
```

## Output Shape

```json
{
  "quality_score": 86,
  "quality_grade": "Good",
  "total_rows": 300,
  "number_of_labels": 5,
  "label_distribution": {
    "politics": 60,
    "sports": 60
  },
  "class_balance_ratio": 1.0,
  "duplicate_rows": 0,
  "missing_values": 0,
  "average_word_count": 11.4,
  "unique_text_ratio": 0.97,
  "meta_language_rows": 0,
  "label_leakage_rows": 1,
  "repeated_fragment_groups": 2,
  "max_fragment_reuse": 3,
  "warnings": []
}
```
