import re
from itertools import chain
from unicodedata import category as cat
from abc import ABC, abstractmethod
from typing import List, NamedTuple, Optional, Set
import unicodedata
from itertools import groupby
from typing import List, Set, NamedTuple, Iterable


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

class NotCat(UnitParser):
    """
    A parser that splits text based on specified major Unicode categories 
    (e.g., 'Z' for separators, 'P' for punctuation).
    """
    
    def __init__(self, categories: Iterable[str]):
        """
        Initializes the parser with a list of target Unicode categories.
        
        Args:
            categories: An iterable of category strings (e.g., ['Z', 'P']).
        """
        # Store target categories as a set for O(1) time complexity lookups.
        # We ensure we only store the uppercase first letter to match major 
        # Unicode categories robustly.
        self.categories: Set[str] = {cat[0].upper() for cat in categories}

    def parse(self, text: str) -> ParseResult:
        """
        Parses the text into continuous blocks of target categories and text.
        
        Args:
            text: The input string to be parsed.
            
        Returns:
            A ParseResult containing the ordered sequence of blocks (seq) 
            and the indices of the blocks that are not separators (idx).
        """
        seq: List[str] = []
        idx: Set[int] = set()

        def get_char_group_key(char: str) -> str:
            """
            Helper function to determine the grouping key for a character.
            """
            # unicodedata.category() returns a 2-letter string (e.g., 'Zs', 'Po').
            # The first letter represents the major category.
            major_category = cat(char)[0]
            
            # If the character's category matches our targets, group by that category.
            # Otherwise, group it as a standard 'TEXT' block.
            if major_category in self.categories:
                return major_category
            return 'TEXT'

        # itertools.groupby aggregates consecutive characters that share the same key
        for i, (group_key, char_group) in enumerate(groupby(text, key=get_char_group_key)):
            
            # If the group is not one of the separator categories, it is a text block
            if group_key == 'TEXT':
                idx.add(i)
            
            # Reconstruct the string block from the group iterator and add to sequence
            seq.append("".join(char_group))

        return ParseResult(seq, idx)
