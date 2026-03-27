import random
from unit import ParseResult
from abc import ABC, abstractmethod
import re
import os


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
    
class Shuffle(Strategy):
    def __init__(self, percent: float, seed=None):
        super().__init__()
        self.percent = percent
        self.rng = random.Random(seed)
    
    def _shuffle_and_reconstruct(self, units, indices):
        result = units.copy()
        elements_to_shuffle = [result[i] for i in indices]
        self.rng.shuffle(elements_to_shuffle)
        for index, shuffled_element in zip(indices, elements_to_shuffle):
            result[index] = shuffled_element
        shuffled_seq = ''.join(result)
        return shuffled_seq

    def execute(self, presult: ParseResult) -> str:
        indices, units = list(presult.index), list(presult.sequence)
        num_to_shuffle = int(len(indices) * self.percent)
        indices_to_shuffle = self.rng.sample(indices, num_to_shuffle)
        output = self._shuffle_and_reconstruct(units, indices_to_shuffle)
        return output
    


class WordShuffle(Strategy):
    def __init__(self, seed=None, separators_file='separators_file.txt'):
        super().__init__()
        self.rng = random.Random(seed)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.separators_file = os.path.join(script_dir, separators_file)
        self.separators = self.load_separators()
        self.separator_pattern = self.create_separator_pattern()

    def load_separators(self):
        try:
            with open(self.separators_file, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"Arquivo de separadores '{self.separators_file}' não encontrado. Usando separadores padrão.")
            return ['!', '?', '.', ',', ';']

    def create_separator_pattern(self):
        escaped_separators = [re.escape(sep) for sep in self.separators]
        return r'([' + ''.join(escaped_separators) + r']\s*)'

    def execute(self, presult: ParseResult) -> str:
        text = ''.join(presult.sequence)
        groups = re.split(self.separator_pattern, text)
        result = []
        for group in groups:
            if re.match(self.separator_pattern, group):
                result.append(group)
            else:
                leading_space = re.match(r'^\s+', group)
                trailing_space = re.search(r'\s+$', group)
                words = group.strip().split()
                self.rng.shuffle(words)
                shuffled_group = ' '.join(words)
                if leading_space:
                    shuffled_group = leading_space.group() + shuffled_group
                if trailing_space:
                    shuffled_group = shuffled_group + trailing_space.group()
                result.append(shuffled_group)
        return ''.join(result)


