import argparse
import logging
import bz2
import gzip
import zpaq
from compressors import dzip, alphazip, bsc_python

import random
from functools import partial
from itertools import product
from pathlib import Path

import pandas as pd

from data.util import sort_values, by_field, df_to_str
from mycode.wals import language_to_wals_code

from compressor import Compressor
from degrader import Degrader

from metric import DegradeAndCompress
from kernels import morphological_deletion_kernel, syntactic_deletion_kernel, pragmatic_deletion_kernel, \
    morphological_replacement_kernel, morphological_shuffler_kernel


def build_experiment_name(path, encoding, seed, percent, runs, basefilename):
    fname = "complexity_%s_%d_%d_%d_%s" % (encoding, percent, runs, seed, basefilename)
    return Path(path) / fname

def experiments(df, computations, runs):
    results = dict(
        language=[],
        wals=[],
        metric=[],
        algorithm=[],
        value=[],
        run_id=[],
    )

    by_languages = {
        lang: df_to_str(dfl) for lang, dfl in by_field(df, "language").items()
    }

    it = product(computations, by_languages, range(runs))
    for computation, language, run in it:
        metric, algorithm = computation

        logging.warning("%20s %20s %20s %10d" % (metric, language, algorithm, run))

        results["language"].append(language)
        results["wals"].append(language_to_wals_code[language])

        results["metric"].append(metric)
        results["algorithm"].append(algorithm)

        text = by_languages[language]
        value = computations[computation].compute(text)

        results["value"].append(value)
        results["run_id"].append(run)

    return pd.DataFrame(results)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename",
        type=Path,
        help="Should be a csv file with the following columns: book, chapter, language, verse_number, text",
    )
    parser.add_argument("encoding", choices=["utf-8", "utf-16", "utf-32", "ascii"])
    parser.add_argument(
        "percent",
        type=int,
        default=20,
        help="Degradation amount. In word deletion, for example, percent=20 means that 20% of the words will be deleted.",
    )
    parser.add_argument(
        "runs", type=int, default=5, help="How many times repeat each experiment"
    )
    parser.add_argument(
        "seed", type=int, default=42, help="Random seed used for the experiments"
    )
    parser.add_argument("output", type=Path, default = "output.txt", help="Where to save the results")
    args = parser.parse_args()
    return args

def main(args):
    random.seed(args.seed)

    rng = random
    percent = args.percent / 100
    df = sort_values(pd.read_csv(args.filename))

    sampler = dict(rng=rng, percent=percent)
    shuffler = dict(rng=rng)

    partial_metric_ids = {
    "del-verses": partial(
        DegradeAndCompress,
        degrader=Degrader.new("deletion", "lines", percent=percent),
        kernel=pragmatic_deletion_kernel
    ),
    "del-words": partial(
        DegradeAndCompress,
        degrader=Degrader.new("deletion", "words", percent=percent),
        kernel=syntactic_deletion_kernel
    ),
    "del-chars": partial(
        DegradeAndCompress,
        degrader=Degrader.new("deletion", "chars", percent=percent),
        kernel=morphological_deletion_kernel
    ),
    "delUni-chars": partial(
        DegradeAndCompress,
        degrader=Degrader.new("random_char_replacementUnic", "chars", percent=percent),
        kernel=morphological_deletion_kernel
    ),
    "delUni-words": partial(
        DegradeAndCompress,
        degrader=Degrader.new("random_word_replacementUnic", "words", percent=percent),
        kernel=syntactic_deletion_kernel
    ),
    "shuf-word": partial(
        DegradeAndCompress,
        degrader=Degrader.new("word_shuffler", "words"),
        kernel=morphological_shuffler_kernel
    ),
    "rep-words": partial(
        DegradeAndCompress,
        degrader=Degrader.new("replacement", "words"),
        kernel=morphological_replacement_kernel
    ),
    "do-nothing": partial(
        DegradeAndCompress,
        degrader=Degrader.new("sameness", "words"),
        kernel=morphological_deletion_kernel
    ),
    }

    compression_algorithms = {
        c.name: c
        for c in [
            Compressor("gzip", args.encoding, gzip.compress, compresslevel=9),
            Compressor("bz2", args.encoding, bz2.compress, compresslevel=9),
            Compressor("zpaq", args.encoding, zpaq.compress),
            Compressor("bsc", args.encoding,  bsc_python.compress),
            Compressor("none", args.encoding, lambda x: x),
        ]
    }

    computations = {
        (k, c): partial_metric_ids[k](compressor=compression_algorithms[c])
        for k, c in product(partial_metric_ids, compression_algorithms)
    }

    logging.warning("Computing experiments")
    results = experiments(df, computations, args.runs)
    fname = build_experiment_name(
        args.output,
        args.encoding,
        args.seed,
        args.percent,
        args.runs,
        args.filename.name,
    )
    results.to_csv(fname, index=False)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)


