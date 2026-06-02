"""Word-level ngram model for local text generation."""

from __future__ import annotations

import random
import re
from collections import defaultdict


class NgramModel:
    """Word-level ngram model for synthetic text generation."""

    def __init__(self, n: int = 3, seed: int = 42):
        self.n = n
        self.seed = seed
        self.rng = random.Random(seed)
        self.ngram_counts: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.start_ngrams: list[tuple[str, ...]] = []
        self.trained = False

    def train(self, texts: list[str]) -> None:
        """Train the ngram model on a list of texts."""
        for text in texts:
            words = self._tokenize(text)
            if len(words) < self.n:
                continue
            for i in range(len(words) - self.n + 1):
                context = tuple(words[i:i + self.n - 1])
                next_word = words[i + self.n - 1]
                self.ngram_counts[context][next_word] += 1
            self.start_ngrams.append(tuple(words[:self.n - 1]))

        if self.start_ngrams:
            self.trained = True

    def generate(
        self,
        min_words: int = 15,
        max_words: int = 60,
        seed_words: list[str] | None = None,
    ) -> str:
        """Generate text using the trained ngram model."""
        if not self.trained:
            return ""

        if seed_words:
            context = tuple(seed_words)
        else:
            context = self.rng.choice(self.start_ngrams) if self.start_ngrams else ("the",)

        words = list(context)
        target_len = self.rng.randint(min_words, max_words)

        for _ in range(target_len):
            if context in self.ngram_counts:
                next_word = self._sample(context)
                if next_word is None:
                    break
                words.append(next_word)
                context = tuple(words[-(self.n - 1):])
            else:
                break

        return self._detokenize(words)

    def generate_batch(
        self,
        count: int,
        min_words: int = 15,
        max_words: int = 60,
        seed_words: list[str] | None = None,
    ) -> list[str]:
        """Generate multiple texts."""
        return [
            self.generate(min_words=min_words, max_words=max_words, seed_words=seed_words)
            for _ in range(count)
        ]

    def _sample(self, context: tuple[str, ...]) -> str | None:
        """Sample a word from the ngram distribution."""
        candidates = self.ngram_counts.get(context)
        if not candidates:
            return None
        words, counts = zip(*candidates.items())
        total = sum(counts)
        r = self.rng.randint(1, total)
        cumulative = 0
        for word, count in zip(words, counts):
            cumulative += count
            if r <= cumulative:
                return word
        return words[-1]

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into words."""
        text = re.sub(r"[^\w\s']", " ", text.lower())
        return [w for w in text.split() if w]

    def _detokenize(self, words: list[str]) -> str:
        """Convert word list back to text with basic capitalization."""
        if not words:
            return ""
        result = words[0].capitalize()
        for w in words[1:]:
            if w in ("i",):
                result += f" {w.upper()}"
            elif w in ("a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "or", "is", "was", "are", "were"):
                result += f" {w}"
            else:
                result += f" {w}"
        if not result.endswith((".", "!", "?")):
            result += "."
        return result

    def get_model_size(self) -> int:
        """Return approximate model size in bytes."""
        total = 0
        for context, candidates in self.ngram_counts.items():
            total += len(context) * 8
            for word, count in candidates.items():
                total += len(word) + 4
        return total


def train_from_snippets(
    snippets: list[str],
    n: int = 3,
    seed: int = 42,
) -> NgramModel:
    """Train an ngram model from web search snippets."""
    model = NgramModel(n=n, seed=seed)
    model.train([s for s in snippets if len(s.split()) >= n])
    return model
