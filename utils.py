import math
import random
import string
from collections import Counter
from typing import Self

class CharDistribution:
    """
    A probability distribution over single characters.
    Supports random sampling based on stored probabilities.
    """
    
    # Class-level constant for $O(1)$ lookup of characters to ignore
    _IGNORE_CHARS: set[str] = frozenset(string.whitespace + string.punctuation)
    
    def __init__(self, probabilities: dict[str, float]) -> None:
        """
        Primary constructor. Initializes from a dictionary of probabilities.
        """
        self._validate_probabilities(probabilities)
        self._probabilities: dict[str, float] = probabilities.copy()
        
        # Pre-cache keys and values for efficient random.choices usage
        self._chars: list[str] = list(self._probabilities.keys())
        self._weights: list[float] = list(self._probabilities.values())

    @staticmethod
    def _validate_probabilities(probs: dict[str, float]) -> None:
        """Validates that keys are single chars and values form a valid distribution."""
        if not probs:
            raise ValueError("Probabilities dictionary cannot be empty.")
            
        total_probability = 0.0
        for char, prob in probs.items():
            if len(char) != 1:
                raise ValueError(f"Keys must be single characters. Invalid key: {char!r}")
            if not (0.0 <= prob <= 1.0):
                raise ValueError(f"Probability must be between 0.0 and 1.0. Invalid for {char!r}: {prob}")
            total_probability += prob
            
        if not math.isclose(total_probability, 1.0, rel_tol=1e-5):
            raise ValueError(f"Probabilities must sum to 1.0, but sum to {total_probability}")

    @classmethod
    def from_string(cls, text: str) -> Self:
        """
        Alternative constructor. Builds distribution from character frequencies,
        ignoring whitespace and punctuation.
        """
        if not text:
            raise ValueError("Input string cannot be empty.")
            
        # Generator expression to filter out ignored characters
        filtered_chars = (char for char in text if char not in cls._IGNORE_CHARS)
        counts = Counter(filtered_chars)
        
        # Calculate total valid characters after filtering
        total_chars = counts.total() if hasattr(counts, 'total') else sum(counts.values())
        
        if total_chars == 0:
            raise ValueError("Input string contains no valid characters to build a distribution.")
            
        probabilities = {char: count / total_chars for char, count in counts.items()}
        return cls(probabilities)

    def generate_string(self, length: int) -> str:
        """Generates a new string sampled from the distribution."""
        if length < 0:
            raise ValueError("Length cannot be negative.")
        if length == 0:
            return ""
            
        sampled_list = random.choices(
            population=self._chars,
            weights=self._weights,
            k=length
        )
        return "".join(sampled_list)

    # --- Dunder Methods ---

    def __rmul__(self, other: str) -> str:
        """
        Implements reflected multiplication: 'string * CharDistribution'.
        """
        if isinstance(other, str):
            return self.generate_string(len(other))
        return NotImplemented

    def __getitem__(self, char: str) -> float:
        """Allows dictionary-like access: dist['a']"""
        if len(char) != 1:
            raise ValueError("Must provide a single character.")
        return self._probabilities.get(char, 0.0)

    def __contains__(self, char: str) -> bool:
        """Allows the 'in' operator."""
        return char in self._probabilities

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"CharDistribution({self._probabilities})"
