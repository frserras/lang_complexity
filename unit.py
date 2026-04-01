import re
from itertools import chain
from unicodedata import category as cat
from abc import ABC, abstractmethod
from typing import List, NamedTuple, Optional, Set


class ParseResult(NamedTuple):
    sequence: List[str]
    index: Set[int]

    def reconstruct(self, select: Optional[Set[int]] = None):
        if select is None:
            return "".join(self.sequence)

        sequence = (
            s
            for i, s in enumerate(self.sequence)
            if (i in select or i not in self.index)
        )
        output = "".join(sequence)
        return output

    def iter(self):
        for i, s in enumerate(self.sequence):
            if i in self.index:
                yield s


class UnitParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> ParseResult: ...


class Chars(UnitParser):
    def __init__(self, ignore_punctuation: bool = False):
        self.ignore_punctuation = ignore_punctuation

    def parse(self, text: str, ignore_punctuation: bool = False) -> ParseResult:
        indexed_sequence = [c for c in text]
        idx = [
            i for (i, c) in enumerate(indexed_sequence) 
            if not (cat(c).startswith("Z") or 
                    (self.ignore_punctuation and cat(c).startswith("P")))
        ]
        output = ParseResult(indexed_sequence, set(idx))
        return output
    

class NotChar(UnitParser):
    def __init__(self, char: str):
        self.char = char

    def parse(self, text: str) -> ParseResult:
        seq = []
        idx = set()
        for i, (fst, snd) in enumerate(
            re.findall(r"([^%s]+)|(%s+)" % (self.char, self.char), text)
        ):
            if elem := fst:
                idx.add(i)
            else:
                elem = snd
            seq.append(elem)
        output = ParseResult(seq, idx)
        return output
