import kernels as K
from metric import DegradeAndCompress
from degrader import Degrader
from functools import partial
from compressor import Compressor

complexities = {
    # gzip
    "morphology_deletion_gzip": DegradeAndCompress(
        Degrader.new("deletion", "chars", strategy_arguments={'percent':0.1}),
        Compressor.new("gzip", compresslevel=9),
        K.morphological_deletion_kernel,
    ),
    "syntactic_deletion_gzip": DegradeAndCompress(
        Degrader.new("deletion", "words", strategy_arguments={'percent':0.1}),
        Compressor.new("gzip", compresslevel=9),
        K.syntactic_deletion_kernel,
    ),
    "pragmatic_deletion_gzip": DegradeAndCompress(
        Degrader.new("deletion", "lines", strategy_arguments={'percent':0.1}),
        Compressor.new("gzip", compresslevel=9),
        K.pragmatic_deletion_kernel,
    ),
    "morphology_replacement_gzip": DegradeAndCompress(
        Degrader.new("replacement", "words"),
        Compressor.new("gzip", compresslevel=9),
        K.morphological_replacement_kernel,
    ),
    # bzip2
    "morphology_deletion_bzip2": DegradeAndCompress(
        Degrader.new("deletion", "chars", strategy_arguments={'percent':0.1}),
        Compressor.new("bzip2", compresslevel=9),
        K.morphological_deletion_kernel,
    ),
    "syntactic_deletion_bzip2": DegradeAndCompress(
        Degrader.new("deletion", "words", strategy_arguments={'percent':0.1}),
        Compressor.new("bzip2", compresslevel=9),
        K.syntactic_deletion_kernel,
    ),
    "pragmatic_deletion_bzip2": DegradeAndCompress(
        Degrader.new("deletion", "lines", strategy_arguments={'percent':0.1}),
        Compressor.new("bzip2", compresslevel=9),
        K.pragmatic_deletion_kernel,
    ),
    "morphology_replacement_bzip2": DegradeAndCompress(
        Degrader.new("replacement", "words"),
        Compressor.new("bzip2", compresslevel=9),
        K.morphological_replacement_kernel,
    ),
    # none
    "morphology_deletion_none": DegradeAndCompress(
        Degrader.new("deletion", "chars", strategy_arguments={'percent':0.1}),
        Compressor.new("none"),
        K.morphological_deletion_kernel,
    ),
    "syntactic_deletion_none": DegradeAndCompress(
        Degrader.new("deletion", "words", strategy_arguments={'percent':0.1}),
        Compressor.new("none"),
        K.syntactic_deletion_kernel,
    ),
    "pragmatic_deletion_none": DegradeAndCompress(
        Degrader.new("deletion", "lines", strategy_arguments={'percent':0.1}),
        Compressor.new("none"),
        K.pragmatic_deletion_kernel,
    ),
    "morphology_replacement_none": DegradeAndCompress(
        Degrader.new("replacement", "words"),
        Compressor.new("none"),
        K.morphological_replacement_kernel,
    ),
}
