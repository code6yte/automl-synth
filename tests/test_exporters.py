"""Tests for exporters."""

import os
import json
import tempfile
from automl_synth.exporters.csv_exporter import export_csv
from automl_synth.exporters.jsonl_exporter import export_jsonl
from automl_synth.types import GeneratedRow


def make_row(id, text, label="positive"):
    return GeneratedRow(
        id=id, text=text, label=label, topic="topic",
        source_agent="generator", difficulty="medium", synthetic_quality_score=0.8,
    )


def test_csv_export():
    rows = [make_row(1, "test text", "positive"), make_row(2, "another text", "negative")]
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = export_csv(rows, f.name)
        assert os.path.exists(path)
        with open(path) as fp:
            content = fp.read()
            assert "id,text,label" in content
            assert "test text" in content


def test_jsonl_export():
    rows = [make_row(1, "test text", "positive")]
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = export_jsonl(rows, f.name)
        assert os.path.exists(path)
        with open(path) as fp:
            line = fp.readline()
            data = json.loads(line)
            assert data["text"] == "test text"
            assert data["label"] == "positive"
