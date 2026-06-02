"""Tests for the SVD-based semantic text model."""

from automl_synth.models.ngram import HybridTextModel, train_from_snippets


def test_train_and_generate():
    model = HybridTextModel(n=2, n_components=5, seed=42)
    model.train(["this is a test sentence about something nice"])
    assert model.trained
    text = model.generate(min_words=3, max_words=10)
    assert isinstance(text, str)
    assert len(text) > 0


def test_train_from_snippets():
    snippets = [
        "Islamabad is the capital city of Pakistan",
        "Beautiful places to visit in Islamabad",
        "Islamabad has many parks and green areas",
    ]
    model = train_from_snippets(snippets, n=2, n_components=5, seed=42)
    assert model.trained
    text = model.generate(min_words=5, max_words=15)
    assert len(text.split()) >= 3


def test_empty_texts():
    model = HybridTextModel(n=3, seed=42)
    model.train([])
    assert not model.trained
    text = model.generate()
    assert text == ""


def test_seed_words():
    model = HybridTextModel(n=2, n_components=5, seed=42)
    model.train(["islamabad is capital pakistan beautiful city"])
    text = model.generate(min_words=5, max_words=15, seed_words=["islamabad"])
    assert len(text.split()) >= 3


def test_generate_batch():
    model = HybridTextModel(n=2, n_components=5, seed=42)
    model.train(["hello world this is a test example"])
    texts = model.generate_batch(count=3, min_words=3, max_words=8)
    assert len(texts) == 3
    assert all(isinstance(t, str) for t in texts)
