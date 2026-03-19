import kernels as K
import unittest

class TestKernels(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "morphological_deletion": [
                ((100, 50), -0.5),
                ((10, 2), -0.2),
                ((0.5, 250), -500.0),
                ((354567.987, 67.89), -0.00019147244672148024),
                ((450.65786, 0.000564), -1.2515037461013107e-06)
            ],
            "syntactic_deletion": [
                ((100, 50), 0.5),
                ((10, 2), 0.2),
                ((0.5, 250), 500.0),
                ((354567.987, 67.89), 0.00019147244672148024),
                ((450.65786, 0.000564), 1.2515037461013107e-06)
            ],
            "pragmatic_deletion": [
                ((100, 50), 0.5),
                ((10, 2), 0.2),
                ((0.5, 250), 500.0),
                ((354567.987, 67.89), 0.00019147244672148024),
                ((450.65786, 0.000564), 1.2515037461013107e-06)
            ],
            "morphological_replacement": [
                ((100, 50), 2.0),
                ((10, 2), 5.0),
                ((0.5, 250), 0.002),
                ((354567.987, 67.89), 5222.683561643836),
                ((450.65786, 0.000564), 799038.7588652482)
            ]
        }

    def test_morphological_deletion_kernel(self):
        for (args, expected) in self.test_data["morphological_deletion"]:
            with self.subTest(args=args):
                result = K.morphological_deletion_kernel(*args)
                self.assertAlmostEqual(result, expected, places=10)

    def test_syntactic_deletion_kernel(self):
        for (args, expected) in self.test_data["syntactic_deletion"]:
            with self.subTest(args=args):
                result = K.syntactic_deletion_kernel(*args)
                self.assertAlmostEqual(result, expected, places=10)

    def test_pragmatic_deletion_kernel(self):
        for (args, expected) in self.test_data["pragmatic_deletion"]:
            with self.subTest(args=args):
                result = K.pragmatic_deletion_kernel(*args)
                self.assertAlmostEqual(result, expected, places=10)

    def test_morphological_replacement_kernel(self):
        for (args, expected) in self.test_data["morphological_replacement"]:
            with self.subTest(args=args):
                result = K.morphological_replacement_kernel(*args)
                self.assertAlmostEqual(result, expected, places=10)

if __name__ == "__main__":
    unittest.main()