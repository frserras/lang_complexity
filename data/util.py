from typing import Dict, List, Optional
import pandas as pd

book_order = (
    "MAT",
    "MRK",
    "LUK",
    "JHN",
    "ACT",
    "ROM",
    "1CO",
    "2CO",
    "GAL",
    "EPH",
    "PHP",
    "COL",
    "1TH",
    "2TH",
    "1TI",
    "2TI",
    "TIT",
    "PHM",
    "HEB",
    "JAS",
    "1PE",
    "2PE",
    "1JN",
    "2JN",
    "3JN",
    "JUD",
    "REV",
)

book_to_index = {book: i for i, book in enumerate(book_order)}


def df_to_str(df, field="text"):
    return "\n".join(df[field])


def sort_values(df: pd.DataFrame) -> pd.DataFrame:
    def language_book_chapter_verse(col: pd.Series) -> pd.Series:
        to_ret = col.map(book_to_index) if col.name == "book" else col
        return to_ret

    return df.sort_values(
        by=["language", "book", "chapter", "verse_number"],
        key=language_book_chapter_verse,
    )


def by_field(df: pd.DataFrame, field: str) -> Dict[str, pd.DataFrame]:
    df = sort_values(df)
    to_ret = {
        k: df[df[field] == k].drop(field, axis=1).reset_index(drop=True)
        for k in df[field].unique()
    }
    return to_ret


def lcm(df: pd.DataFrame) -> pd.DataFrame:
    langs = by_field(df, "language")
    idxs = []
    for lang, ldf in langs.items():
        idxs.append(ldf)
    cols = ["book", "chapter", "verse_number"]
    v = idxs.pop().loc[:, cols]
    while idxs:
        v = v.merge(idxs.pop(), how="inner", on=cols).loc[:, cols]
    return v


def lcm_with_cut(df: pd.DataFrame, cut: float):
    cols = ["book", "chapter", "verse_number"]
    all_verses = df.loc[:, cols].drop_duplicates(ignore_index=True)
    lang_verse_count = sorted(
        [(l, d.loc[:, cols]) for l, d in by_field(df, "language").items()],
        key=lambda x: len(x[1]),
    )
    removed = set()
    percent = list()
    for lango, ldf in lang_verse_count:
        removed.add(lango)
        s = all_verses
        for langi, ldf in lang_verse_count:
            if langi in removed:
                continue
            s = s.merge(ldf, how="inner", on=cols)
        percent.append((lango, len(s) / len(all_verses)))
    ret = [l for l, c in percent if c >= cut]
    return ret


def intersection(ldf: pd.DataFrame, cols: Optional[List[str]] = None) -> pd.DataFrame:
    cols = cols or ["book", "chapter", "verse_number"]
    bcvn = lcm(ldf)
    ret = ldf.merge(bcvn, how="inner", on=cols)
    return ret
