import argparse
import logging
import random
from itertools import product
from pathlib import Path

import pandas as pd

from data.util import sort_values, by_field, df_to_str
from src.wals import language_to_wals_code
from complexity import complexities


def experiments(df, complexities_dict, runs):
    results = dict(
        language=[],
        wals=[],
        experiment=[],
        value=[],
        run_id=[],
    )

    by_languages = {
        lang: df_to_str(dfl) for lang, dfl in by_field(df, "language").items()
    }

    it = product(complexities_dict.items(), by_languages.items(), range(runs))

    for (experiment_name, complexity_obj), (language, text), run in it:
        logging.warning("%40s %20s %10d" % (experiment_name, language, run))

        results["language"].append(language)
        results["wals"].append(language_to_wals_code[language])
        results["experiment"].append(experiment_name)

        value = complexity_obj.compute(text)
        results["value"].append(value)

        results["run_id"].append(run)

    return pd.DataFrame(results)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename",
        type=Path,
        help="Should be a csv file with columns: book, chapter, language, verse_number, text",
    )
    parser.add_argument("encoding", choices=["utf-8", "utf-16", "utf-32", "ascii"])
    parser.add_argument(
        "runs", type=int, default=10, help="How many times to repeat each experiment"
    )
    parser.add_argument(
        "seed", type=int, default=2025, help="Random seed for the experiments"
    )
    parser.add_argument("output", type=Path, help="Where to save the results")
    args = parser.parse_args()
    return args


def main(args):
    random.seed(args.seed)
    df = sort_values(pd.read_csv(args.filename))

    logging.warning("Computing experiments")
    results = experiments(df, complexities, args.runs)

    base_filename = Path(args.filename).name
    fname = Path(args.output) / f"complexity_{args.encoding}_{args.seed}_{args.runs}_{base_filename}"
    
    results.to_csv(fname, index=False)
    logging.warning(f"Results saved to {fname}")


if __name__ == "__main__":
    args = parse_arguments()
    main(args)