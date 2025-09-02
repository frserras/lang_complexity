import re
import pandas as pd
from collections import Counter


def tokens(text, regex=r"[^  \n]+", flags=re.M):
    return re.findall(regex, text, flags)


def lines(text):
    return text.strip().split("\n")


def types(tokens):
    return Counter(tokens)


def spaces(text):
    num_spaces = len(re.findall(r"\s+", text))
    num_non_spaces = len(text) - num_spaces
    return num_spaces, num_non_spaces
