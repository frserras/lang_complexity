import random
import re
import os
from abc import ABC, abstractmethod
from unit import ParseResult
from typing import List


class Strategy(ABC):
    @abstractmethod
    def execute(self, presult: ParseResult) -> str: ...


class Sameness(Strategy):
    def execute(self, presult: ParseResult) -> str:
        return presult.reconstruct()


class Deletion(Strategy):
    def __init__(self, percent: float, seed=None):
        super().__init__()
        self.percent = percent
        self.rng = random.Random(seed)

    def execute(self, presult: ParseResult) -> str:
        values = list(presult.index)
        sample = set(self.rng.sample(values, k=int(len(values) * self.percent)))
        output = presult.reconstruct(select=presult.index - sample)
        return output

class Replacement(Strategy):
    def __init__(self, seed=None):
        super().__init__()
        self.rng = random.Random(seed)

    def execute(self, presult: ParseResult) -> str:
        pseq = list(presult.iter())
        unique = list(set(pseq))
        self.rng.shuffle(unique)
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


class RandomCharReplacementUnic(Strategy):
    def __init__(self, percent: float, seed=None, unicode_char='∑'):
        super().__init__()
        self.percent = percent
        self.rng = random.Random(seed)
        self.unicode_char = unicode_char

    def execute(self, presult: ParseResult) -> str:
        chars = list(presult.sequence)
        non_space_indices = [i for i, char in enumerate(chars) if not char.isspace()]
        num_to_replace = int(len(non_space_indices) * self.percent)
        indices_to_replace = self.rng.sample(non_space_indices, num_to_replace)

        for idx in indices_to_replace:

            chars[idx] = self.unicode_char

        return ''.join(chars)


class RandomWordReplacementUnic(Strategy):
    def __init__(self, percent: float, seed=None, unicode_char='∑'):
        super().__init__()
        self.percent = percent
        self.rng = random.Random(seed)
        self.unicode_char = unicode_char

    def execute(self, presult: ParseResult) -> str:
        text = ''.join(presult.sequence)

        # Tokeniza o texto preservando palavras, espaços e pontuação
        tokens: List[str] = re.findall(r'\w+|\s+|[^\w\s]', text)

        # Identifica índices de palavras (excluindo espaços e pontuação)
        word_indices = [i for i, token in enumerate(tokens) if token.isalnum()]

        # Calcula quantas palavras substituir
        num_to_replace = int(len(word_indices) * self.percent)

        # Seleciona aleatoriamente as palavras para substituir
        indices_to_replace = self.rng.sample(word_indices, num_to_replace)

        # Substitui as palavras selecionadas
        for idx in indices_to_replace:
            word = tokens[idx]
            tokens[idx] = self.unicode_char * len(word)

        # Junta os tokens de volta em uma string
        return ''.join(tokens)

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