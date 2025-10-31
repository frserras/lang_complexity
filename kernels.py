# Equation 2
def morphological_deletion_kernel(size_original_compressed, size_degraded_compressed):
    return -size_degraded_compressed / size_original_compressed


# Equation 3
def syntactic_deletion_kernel(size_original_compressed, size_degraded_compressed):
    return size_degraded_compressed / size_original_compressed


# Equation 4
def pragmatic_deletion_kernel(size_original_compressed, size_degraded_compressed):
    return size_degraded_compressed / size_original_compressed


# Equation 5
def morphological_replacement_kernel(size_original_compressed, size_degraded_compressed):
    return size_original_compressed / size_degraded_compressed


# Equation 6
def morphological_shuffler_kernel(size_original_compressed, size_degraded_compressed):
    return size_degraded_compressed / size_original_compressed