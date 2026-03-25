import unittest
from unittest.mock import patch
from compressor import Compressor as C

class TestCompressor(unittest.TestCase):

    def test_compressor_none_returns_encoded_bytes(self):
        compressor = C.new("none", encoding="utf-8")
        text = "Hello, world!"
        result = compressor.compress(text)
        
        self.assertEqual(result, text.encode("utf-8"))
        self.assertIsInstance(result, bytes)

    def test_compression_reduces_size_for_repetitive_text(self):
            # Fetch all available compressors dynamically, ignoring "none"
            # Note: Accessing private attribute via Python's name mangling
            available_compressors = [
                name for name in C._Compressor__compressors.keys() 
                if name != "none"
            ]
            
            repetitive_text = "A" * 5000
            original_size = len(repetitive_text.encode("utf-8"))
            
            for comp_name in available_compressors:
                with self.subTest(compressor=comp_name):
                    compressor = C.new(comp_name)
                    result = compressor.compress(repetitive_text)
                    compressed_size = len(result)
                    
                    self.assertLess(compressed_size, original_size)
                    self.assertGreater(compressed_size, 0)

    def test_invalid_compressor_name_raises_keyerror(self):
        with self.assertRaises(KeyError):
            C.new("nonexistent_algorithm")

    def test_delegates_to_compressor_with_correct_args(self):
        available_compressors = [
            name for name in C._Compressor__compressors.keys() 
            if name != "none"
        ]
        
        for comp_name in available_compressors:
            with self.subTest(compressor=comp_name):
                compressor = C.new(comp_name, encoding="utf-8", compresslevel=9)
                
                # Mock the 'function' attribute directly on the compressor instance
                # This dynamically mocks gzip.compress, bz2.compress, or any future addition
                with patch.object(compressor, 'function') as mock_compress:
                    mock_compress.return_value = b"fake_bytes"
                    
                    result = compressor.compress("test")
                    
                    mock_compress.assert_called_once_with(b"test", compresslevel=9)
                    self.assertEqual(result, b"fake_bytes")



if __name__ == '__main__':
    unittest.main()



