import random
from unit import ParseResult
from abc import ABC, abstractmethod
import re


class Strategy(ABC):
    @abstractmethod
    def execute(self, presult: ParseResult) -> str: ...


class Sameness(Strategy):
    def execute(self, presult: ParseResult) -> str:
        return presult.reconstruct()


class Deletion(Strategy):
    def __init__(self, percent: float):
        super().__init__()
        self.percent = percent

    def execute(self, presult: ParseResult) -> str:
        values = list(presult.index)
        sample = set(random.sample(values, k=int(len(values) * self.percent)))
        output = presult.reconstruct(select=presult.index - sample)
        return output


class Replacement(Strategy):
    def execute(self, presult: ParseResult) -> str:
        pseq = list(presult.iter())
        unique = list(set(pseq))
        unique.sort()
        random.shuffle(unique)
        encode = {w: i for i, w in enumerate(unique)}
        output = "".join(
            list(
                map(
                    lambda c: "%010d" % encode[c] if c in encode else c,
                    presult.sequence,
                )
            )
        )
        return output
    
class Masking(Strategy):
    def __init__(self, percent: float, seed=None, mask='α'):
        super().__init__()
        self.percent = percent
        self.rng = random.Random(seed)
        self.mask = mask
    
    def _mask_and_reconstruct(self, units, indices_to_mask):
        for idx in indices_to_mask:
            units[idx] = len(units[idx]) * self.mask
        seq_masked = ''.join(units)
        return seq_masked

    def execute(self, presult: ParseResult) -> str:
        indices, units = list(presult.index), list(presult.sequence)
        num_to_replace = int(len(indices) * self.percent)
        indices_to_mask = self.rng.sample(indices, num_to_replace)
        output = self._mask_and_reconstruct(units, indices_to_mask)
        return output


