import unittest
import unit as U

class TestUnit(unittest.TestCase):
    
    def test_chars(self):
        s = "abcdefghijklmnopqrstuvwxyz"
        parser = U.Chars()
        
        result = parser.parse(s)
        joined = result.reconstruct()
        
        self.assertEqual(len(result.index), len(s))
        self.assertEqual(len(joined), len(s))
        self.assertEqual(joined, s)

    def test_non_spaces(self):
        s = " ".join("abcdefghijklmnopqrstuvwxyz")
        parser = U.NotChar(" ")
        
        result = parser.parse(s)
        joined = result.reconstruct()

        self.assertEqual(len(joined), len(s))
        self.assertEqual(joined, s) 

    def test_lines(self):
        s = "\n".join("abcdefghijklmnopqrstuvwxyz")
        parser = U.NotChar("\n")
        
        result = parser.parse(s)
        joined = result.reconstruct()
        
        self.assertEqual(len(joined), len(s))
        self.assertEqual(joined, s)

if __name__ == "__main__":
    unittest.main()