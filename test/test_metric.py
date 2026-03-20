import random
import unittest
from unittest.mock import Mock, call
from degrader import Degrader
from compressor import Compressor
from metric import DegradeAndCompress
import kernels as K
from complexity import complexities
from test.snapshot import integration_results, integration_test_input
import warnings

class TestDegradeAndCompress(unittest.TestCase):

    def test_orchestration_with_mocks(self):
        # Create mocks based on your real imported classes
        mock_degrader = Mock(spec=Degrader)
        mock_degrader.degrade.return_value = "degraded_text"

        mock_compressor = Mock(spec=Compressor)
        mock_compressor.compress.side_effect = ["compressed_original", "compressed_degraded"]

        # Mocking the kernel callable
        mock_kernel = Mock()
        mock_kernel.return_value = 42.0

        # Instantiate the metric passing the mocks
        metric = DegradeAndCompress(
            degrader=mock_degrader, 
            compressor=mock_compressor, 
            kernel=mock_kernel
        )

        result = metric.compute("original_text")

        # Asserts (verifications)
        self.assertEqual(result, 42.0)
        mock_degrader.degrade.assert_called_once_with("original_text")
        
        expected_calls = [call("original_text"), call("degraded_text")]
        mock_compressor.compress.assert_has_calls(expected_calls, any_order=False)
        self.assertEqual(mock_compressor.compress.call_count, 2)
        
        # len("compressed_original") is 19
        # len("compressed_degraded") is 19
        mock_kernel.assert_called_once_with(19, 19)


    def test_integration_with_snapshot_and_fixed_seed(self):
        for metric_name in complexities.keys():
            with self.subTest(metric_name=metric_name):
                random.seed(42)
                test_result = complexities[metric_name].compute(integration_test_input)
                if not metric_name in integration_results.keys():
                    warnings.warn(f"INTEGRATION WITH SNAPSHOT TEST: snapshot result for " 
                                  "metric {metric_name}. Skipping test.")
                    continue
                expected_result = integration_results[metric_name]
                self.assertAlmostEqual(test_result, expected_result, places=5)



if __name__ == '__main__':
    unittest.main()