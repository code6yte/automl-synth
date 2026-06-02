"""Hybrid SVD + ngram model for local text generation.

Uses ngram for grammatical word ordering and SVD word vectors
for semantic diversity when the ngram gets stuck.
"""

from __future__ import annotations

import random
import re
from collections import defaultdict

import numpy as np


class HybridTextModel:
    """Hybrid SVD + ngram model for synthetic text generation.

    - Ngram component preserves word ordering from training data
    - SVD component provides semantic fallback when ngram has no continuation
    - Produces grammatically coherent text with good topic relevance
    """

    def __init__(self, n: int = 3, n_components: int = 50, seed: int = 42):
        self.n = n
        self.n_components = n_components
        self.seed = seed
        self.rng = random.Random(seed)

        self.ngram_counts: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.start_ngrams: list[tuple[str, ...]] = []

        self.vocab: list[str] = []
        self.word_index: dict[str, int] = {}
        self.word_vectors: np.ndarray | None = None

        self.trained = False

    def train(self, texts: list[str]) -> None:
        """Train both ngram and SVD components."""
        tokenized = [self._tokenize(t) for t in texts if t.strip()]
        tokenized = [t for t in tokenized if len(t) >= 3]

        if not tokenized:
            return

        all_words: list[str] = []
        vocab_set: set[str] = set()

        for tokens in tokenized:
            all_words.extend(tokens)
            vocab_set.update(tokens)

            if len(tokens) >= self.n:
                for i in range(len(tokens) - self.n + 1):
                    context = tuple(tokens[i:i + self.n - 1])
                    next_word = tokens[i + self.n - 1]
                    self.ngram_counts[context][next_word] += 1
                self.start_ngrams.append(tuple(tokens[:self.n - 1]))

        self.vocab = sorted(vocab_set)
        self.word_index = {w: i for i, w in enumerate(self.vocab)}

        if self.start_ngrams:
            self.trained = True

        self._build_svd(tokenized)

    def _build_svd(self, tokenized: list[list[str]]) -> None:
        """Build SVD word vectors from co-occurrence matrix."""
        vocab_size = len(self.vocab)
        if vocab_size < 3:
            return

        cooc = np.zeros((vocab_size, vocab_size), dtype=np.float64)

        for tokens in tokenized:
            indices = [self.word_index[w] for w in tokens if w in self.word_index]
            for i in range(len(indices)):
                start = max(0, i - 3)
                end = min(len(indices), i + 4)
                for j in range(start, end):
                    if i != j:
                        cooc[indices[i], indices[j]] += 1.0

        cooc = np.log1p(cooc)

        try:
            U, S, Vt = np.linalg.svd(cooc, full_matrices=False)
            k = min(self.n_components, len(S))
            self.word_vectors = U[:, :k] * S[:k]
        except np.linalg.LinAlgError:
            self.word_vectors = np.eye(vocab_size)[:, :min(vocab_size, self.n_components)]

    def generate(
        self,
        min_words: int = 10,
        max_words: int = 40,
        seed_words: list[str] | None = None,
        temperature: float = 0.8,
    ) -> str:
        """Generate text using hybrid ngram+SVD approach.

        Primary: ngram sampling with backoff (n → n-1 → ... → 1).
        Enhancement: SVD reranking of top candidates for topic coherence.
        """
        if not self.trained:
            return ""

        target_len = self.rng.randint(min_words, max_words)

        if seed_words:
            clean_seeds = [s.lower() for s in seed_words if s.lower() in self.word_index]
            if clean_seeds:
                context = tuple(clean_seeds[:self.n - 1])
            else:
                context = self._random_start()
        else:
            context = self._random_start()

        words = list(context)

        for _ in range(target_len - len(context)):
            next_word = self._sample_with_backoff(context, temperature, words)

            if next_word is None:
                break

            words.append(next_word)
            context = tuple(words[-(self.n - 1):])

        return self._detokenize(words)

    def _sample_with_backoff(
        self,
        context: tuple[str, ...],
        temperature: float,
        generated_words: list[str],
    ) -> str | None:
        """Sample next word with ngram backoff, reranked by SVD similarity."""
        candidates: dict[str, float] = {}

        for n in range(len(context), 0, -1):
            ctx = context[-n:]
            if ctx in self.ngram_counts:
                total = sum(self.ngram_counts[ctx].values())
                for word, count in self.ngram_counts[ctx].items():
                    candidates[word] = candidates.get(word, 0) + (count / total) * (n / len(context))
                break

        if not candidates:
            return self._svd_fallback(generated_words[-1], temperature)

        if self.word_vectors is not None and generated_words:
            last = generated_words[-1]
            if last in self.word_index:
                idx = self.word_index[last]
                vec = self.word_vectors[idx]
                norms = np.linalg.norm(self.word_vectors, axis=1)
                all_sims = (self.word_vectors @ vec) / (norms * np.linalg.norm(vec) + 1e-10)
                for word in list(candidates.keys()):
                    if word in self.word_index:
                        candidates[word] *= max(0.5, 1.0 + all_sims[self.word_index[word]] * 0.3)

        words = list(candidates.keys())
        weights = list(candidates.values())

        temp_adjusted = [w ** (1.0 / max(temperature, 0.1)) for w in weights]
        total = sum(temp_adjusted)
        if total <= 0:
            return None

        r = self.rng.random() * total
        cumulative = 0.0
        for word, w in zip(words, temp_adjusted):
            cumulative += w
            if r <= cumulative:
                return word
        return words[-1]

    def _random_start(self) -> tuple[str, ...]:
        """Pick a random start context."""
        if self.start_ngrams:
            return self.rng.choice(self.start_ngrams)
        if self.vocab:
            return (self.vocab[self.rng.randint(0, len(self.vocab) - 1)],)
        return ("the",)

    def _svd_fallback(self, word: str, temperature: float) -> str | None:
        """Fallback: find semantically similar word using SVD."""
        if word not in self.word_index or self.word_vectors is None:
            return None

        idx = self.word_index[word]
        vec = self.word_vectors[idx]
        norms = np.linalg.norm(self.word_vectors, axis=1)
        mask = norms > 0
        if not mask.any():
            return None

        sims = (self.word_vectors @ vec) / (norms * np.linalg.norm(vec) + 1e-10)
        sims = np.exp(sims / max(temperature, 0.1))
        sims[~mask] = 0

        total = sims.sum()
        if total <= 0:
            return None

        probs = sims / total
        choice = self.rng.choices(range(len(self.vocab)), weights=probs.tolist(), k=1)[0]
        return self.vocab[choice]

    def generate_batch(
        self,
        count: int,
        min_words: int = 10,
        max_words: int = 40,
        seed_words: list[str] | None = None,
        temperature: float = 0.8,
    ) -> list[str]:
        """Generate multiple texts."""
        return [
            self.generate(
                min_words=min_words,
                max_words=max_words,
                seed_words=seed_words,
                temperature=temperature,
            )
            for _ in range(count)
        ]

    def _tokenize(self, text: str) -> list[str]:
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"\b\d{2,}\b", "", text)
        text = re.sub(r"(\w)(\w{20,})", r"\1", text)
        text = re.sub(r"[^\w\s']", " ", text.lower())
        words = [w for w in text.split() if w and len(w) > 2 and not w.isdigit() and not w.startswith("amp")]
        return words[:40]

    def _detokenize(self, words: list[str]) -> str:
        if not words:
            return ""
        result = words[0].capitalize()
        for w in words[1:]:
            if w in ("i",):
                result += " I"
            elif w in (
                "a", "an", "the", "in", "on", "at", "for", "to",
                "of", "and", "or", "is", "was", "are", "were", "by",
                "with", "from", "as", "its", "it", "not", "but",
            ):
                result += f" {w}"
            else:
                result += f" {w}"
        if result[-1] not in (".", "!", "?"):
            result += "."
        return result


def train_from_snippets(
    snippets: list[str],
    n: int = 3,
    n_components: int = 50,
    seed: int = 42,
) -> HybridTextModel:
    """Train a hybrid ngram+SVD model from web search snippets."""
    model = HybridTextModel(n=n, n_components=n_components, seed=seed)
    model.train([s for s in snippets if len(s.split()) >= n])
    return model
