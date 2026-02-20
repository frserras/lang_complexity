import kernels as K
from metric import DegradeAndCompress
from degrader import Degrader
from functools import partial
from compressor import Compressor

complexities = {
    # gzip
    "morphology_deletion_gzip": DegradeAndCompress(
        Degrader.new("deletion", "chars", percent=0.1),
        Compressor.new("gzip", compresslevel=9),
        K.morphological_deletion_kernel,
    ),
    "syntactic_deletion_gzip": DegradeAndCompress(
        Degrader.new("deletion", "words", percent=0.1),
        Compressor.new("gzip", compresslevel=9),
        K.syntactic_deletion_kernel,
    ),
    "pragmatic_deletion_gzip": DegradeAndCompress(
        Degrader.new("deletion", "lines", percent=0.1),
        Compressor.new("gzip", compresslevel=9),
        K.pragmatic_deletion_kernel,
    ),
    "morphology_replacement_gzip": DegradeAndCompress(
        Degrader.new("replacement", "words"),
        Compressor.new("gzip", compresslevel=9),
        K.morphological_replacement_kernel,
    ),
    "size_gzip": DegradeAndCompress(
        Degrader.new("sameness", "chars"),
        Compressor.new("gzip", compresslevel=9),
        lambda original, degraded: float(original),
    ),
    # bzip2
    "morphology_deletion_bzip2": DegradeAndCompress(
        Degrader.new("deletion", "chars", percent=0.1),
        Compressor.new("bzip2", compresslevel=9),
        K.morphological_deletion_kernel,
    ),
    "syntactic_deletion_bzip2": DegradeAndCompress(
        Degrader.new("deletion", "words", percent=0.1),
        Compressor.new("bzip2", compresslevel=9),
        K.syntactic_deletion_kernel,
    ),
    "pragmatic_deletion_bzip2": DegradeAndCompress(
        Degrader.new("deletion", "lines", percent=0.1),
        Compressor.new("bzip2", compresslevel=9),
        K.pragmatic_deletion_kernel,
    ),
    "morphology_replacement_bzip2": DegradeAndCompress(
        Degrader.new("replacement", "words"),
        Compressor.new("bzip2", compresslevel=9),
        K.morphological_replacement_kernel,
    ),
    "size_bzip2": DegradeAndCompress(
        Degrader.new("sameness", "chars"),
        Compressor.new("bzip2", compresslevel=9),
        lambda original, degraded: float(original),
    ),
    #zpaq
    "morphology_deletion_zpaq": DegradeAndCompress(
        Degrader.new("deletion", "chars", percent=0.1),
        Compressor.new("zpaq"),
        K.morphological_deletion_kernel,
    ),
    "syntactic_deletion_zpaq": DegradeAndCompress(
        Degrader.new("deletion", "words", percent=0.1),
        Compressor.new("zpaq"),
        K.syntactic_deletion_kernel,
    ),
    "pragmatic_deletion_zpaq": DegradeAndCompress(
        Degrader.new("deletion", "lines", percent=0.1),
        Compressor.new("zpaq"),
        K.pragmatic_deletion_kernel,
    ),
    "morphology_replacement_zpaq": DegradeAndCompress(
        Degrader.new("replacement", "words"),
        Compressor.new("zpaq"),
        K.morphological_replacement_kernel,
    ),
    "size_zpaq": DegradeAndCompress(
        Degrader.new("sameness", "chars"),
        Compressor.new("zpaq"),
        lambda original, degraded: float(original),
    ),
    #Sequitur
    ''''morphology_deletion_sequitur': DegradeAndCompress(
        Degrader.new("deletion", "chars", percent=0.1),
        Compressor.new("sequitur"),
        K.morphological_deletion_kernel,
    ),
    'syntactic_deletion_sequitur': DegradeAndCompress(
        Degrader.new("deletion", "words", percent=0.1),
        Compressor.new("sequitur"),
        K.syntactic_deletion_kernel,
    ),
    'pragmatic_deletion_sequitur': DegradeAndCompress(
        Degrader.new("deletion", "lines", percent=0.1),
        Compressor.new("sequitur"),
        K.pragmatic_deletion_kernel,
    ),
    'morphology_replacement_sequitur': DegradeAndCompress(
        Degrader.new("replacement", "words"),
        Compressor.new("sequitur"),
        K.morphological_replacement_kernel,
    ),
    "size_sequitur": DegradeAndCompress(
        Degrader.new("sameness", "chars"),
        Compressor.new("sequitur", compresslevel=9),
        lambda original, degraded: float(original),
    ),
       '''
    #BSC 
    "morphology_deletion_bsc": DegradeAndCompress(
        Degrader.new("deletion", "chars", percent=0.1),
        Compressor.new("bsc"),
        K.morphological_deletion_kernel,
    ),
    "syntactic_deletion_bsc": DegradeAndCompress(
        Degrader.new("deletion", "words", percent=0.1),
        Compressor.new("bsc"),
        K.syntactic_deletion_kernel,
    ),
    "pragmatic_deletion_bsc": DegradeAndCompress(
        Degrader.new("deletion", "lines", percent=0.1),
        Compressor.new("bsc"),
        K.pragmatic_deletion_kernel,
    ),
    "morphology_replacement_bsc": DegradeAndCompress(
        Degrader.new("replacement", "words"),
        Compressor.new("bsc"),
        K.morphological_replacement_kernel,
    ), 
    "size_bsc": DegradeAndCompress(
        Degrader.new("sameness", "chars"),
        Compressor.new("bsc"),
        lambda original, degraded: float(original),
    ),
    #AlphaZip
   '''"morphology_deletion_alphazip": DegradeAndCompress(
        Degrader.new("deletion", "chars", percent=0.1),
        Compressor.new("alphazip"),
        K.morphological_deletion_kernel,
    ),
    "syntactic_deletion_alphazip": DegradeAndCompress(
        Degrader.new("deletion", "words", percent=0.1),
        Compressor.new("alphazip"),
        K.syntactic_deletion_kernel,
    ),
    "pragmatic_deletion_alphazip": DegradeAndCompress(
        Degrader.new("deletion", "lines", percent=0.1),
        Compressor.new("alphazip"),
        K.pragmatic_deletion_kernel,
    ),
    "morphology_replacement_alphazip": DegradeAndCompress(
        Degrader.new("replacement", "words"),
        Compressor.new("alphazip"),
        K.morphological_replacement_kernel,
    ), 
    "size_alphazip": DegradeAndCompress(
        Degrader.new("sameness", "chars"),
        Compressor.new("alphazip"),
        lambda original, degraded: float(original),
    ),
    '''
    #DZip
    '''
    "morphology_deletion_dzip": DegradeAndCompress(
        Degrader.new("deletion", "chars", percent=0.1),
        Compressor.new("dzip"),
        K.morphological_deletion_kernel,
    ),
    "syntactic_deletion_dzip": DegradeAndCompress(
        Degrader.new("deletion", "words", percent=0.1),
        Compressor.new("dzip"),
        K.syntactic_deletion_kernel,
    ),
    "pragmatic_deletion_dzip": DegradeAndCompress(
        Degrader.new("deletion", "lines", percent=0.1),
        Compressor.new("dzip"),
        K.pragmatic_deletion_kernel,
    ),
    "morphology_replacement_dzip": DegradeAndCompress(
        Degrader.new("replacement", "words"),
        Compressor.new("dzip"),
        K.morphological_replacement_kernel,
    ), 
    "size_dzip": DegradeAndCompress(
        Degrader.new("sameness", "chars"),
        Compressor.new("dzip"),
        lambda original, degraded: float(original),
    ),
    '''
    # none
    "morphology_deletion_none": DegradeAndCompress(
        Degrader.new("deletion", "chars", percent=0.1),
        Compressor.new("none"),
        K.morphological_deletion_kernel,
    ),
    "syntactic_deletion_none": DegradeAndCompress(
        Degrader.new("deletion", "words", percent=0.1),
        Compressor.new("none"),
        K.syntactic_deletion_kernel,
    ),
    "pragmatic_deletion_none": DegradeAndCompress(
        Degrader.new("deletion", "lines", percent=0.1),
        Compressor.new("none"),
        K.pragmatic_deletion_kernel,
    ),
    "morphology_replacement_none": DegradeAndCompress(
        Degrader.new("replacement", "words"),
        Compressor.new("none"),
        K.morphological_replacement_kernel,
    ),
    "size_none": DegradeAndCompress(
        Degrader.new("sameness", "chars"),
        Compressor.new("none"),
        lambda original, degraded: float(original),
    ),
}

if __name__ == '__main__': 
    with open("./test/test_texto.txt", 'r', encoding='utf-8') as arquivo:
        texto = arquivo.read()
 
    for nome_da_complexidade, objeto_complexidade in complexities.items(): 
        print(f"\nCalculando: {nome_da_complexidade}...")
        try:
            resultado = objeto_complexidade.compute(texto)
            print(f"Resultado: {resultado}")
        except Exception as e:
            print(f"ERRO ao calcular '{nome_da_complexidade}': {e}")
