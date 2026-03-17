import unittest
import unit as U
from unicodedata import category as cat

class TestUnit(unittest.TestCase):

    def test_chars(self):
            p1_test_strings = [
                "",                                
                "a",       
                "abcdefghijklmnopqrstuvwxyz",
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                "0123456789",                     
                "!@#$%^&*()_+",
                "João maçã",               
                "Teste com 🚀 emoji",
                "a" * 1000,
                "   ",              
                "Olá \u00A0 Mundo", 
            ]
        
            parser = U.Chars()
        
            # PART 1: Standard behaviour with total reconstruction
            for s in p1_test_strings:
                with self.subTest(string=s):
                    result = parser.parse(s)
                    joined = result.reconstruct()
                    expected_index_len = sum(1 for c in s if not cat(c).startswith('Z'))
                    
                    self.assertEqual(len(result.index), expected_index_len)
                    self.assertEqual(len(joined), len(s))
                    self.assertEqual(joined, s)

            # PART2: Reconstruction with Select
            with self.subTest(string="Reconstruction with Select"):
                
                # CASE A: simple phrase with spaces
                res_a = parser.parse("Oi, tu")
                self.assertEqual(res_a.reconstruct({0, 4}), "O t")
                self.assertEqual(res_a.reconstruct(set()), " ")

                # CASE B: simple phrase with no spaces
                res_b = parser.parse("Python")
                self.assertEqual(res_b.reconstruct({0, 1, 5}), "Pyn")
                self.assertEqual(res_b.reconstruct(set()), "")

                #CASE C: Several separators
                res_c = parser.parse("A   B")
                self.assertEqual(res_c.reconstruct({0}), "A   ")
                self.assertEqual(res_c.reconstruct({4}), "   B")

                # CASE D: No Select
                res_d = parser.parse("Teste 123")
                self.assertEqual(res_d.reconstruct(), "Teste 123")
                
                # CASE E: Selecting a Separator
                res_e = parser.parse("A B")
                self.assertEqual(res_e.reconstruct({0, 1}), "A ")

                # CASE F: Selecting an unicode grapheme cluster.
                # Current Behaviour:treat each unicode char in a grapheme cluster
                # as an individual character.
                res_e = parser.parse("A Bandeira do Brasil:🇧🇷")
                self.assertEqual(res_e.reconstruct({0, 21}), "A   🇧")


 

    def test_not_char(self):
            
        # PART 1: Standard Behaviour
        with self.subTest(part="Standard Behaviour"):
            
            # Case A: Parses words using the whitespace shorthand
            parser_s = U.NotChar(r"\s")
            res_s = parser_s.parse("hello world\tpython")
            self.assertEqual(res_s.sequence, ["hello", " ", "world", "\t", "python"])
            self.assertEqual(res_s.index, {0, 2, 4})

            # Case B: Parses lines separated by a literal newline character
            parser_n = U.NotChar("\n")
            res_n = parser_n.parse("line1\nline2")
            self.assertEqual(res_n.sequence, ["line1", "\n", "line2"])
            self.assertEqual(res_n.index, {0, 2})

        # PART 2: Edge Cases
        with self.subTest(part="Edge Cases"):
            parser = U.NotChar(r"\s")

            # Case A: Handles strings consisting solely of multiple whitespace types
            res_only_sep = parser.parse("  \t  ")
            self.assertEqual(res_only_sep.sequence, ["  \t  "])
            self.assertEqual(res_only_sep.index, set())

            # Case B: Groups consecutive spaces into a single structural chunk
            res_multi = parser.parse("a   b")
            self.assertEqual(res_multi.sequence, ["a", "   ", "b"])
            self.assertEqual(res_multi.index, {0, 2})

            # Case C: Captures leading and trailing whitespace accurately
            res_edges = parser.parse(" space ")
            self.assertEqual(res_edges.sequence, [" ", "space", " "])
            self.assertEqual(res_edges.index, {1})

        # PART 3: Reconstruction with Selection
        with self.subTest(part="Reconstruction with Selection"):
            parser = U.NotChar(r"\s")
            res = parser.parse("word1 word2 word3") 
            
            # Case A: Reconstructs text while preserving original spacing between removed items
            self.assertEqual(res.reconstruct({0, 4}), "word1  word3")

            # Case B: Returns only the original whitespace structure when selection is empty
            self.assertEqual(res.reconstruct(set()), "  ")

            # Case C: Verifies that passing None returns the exact original input string
            self.assertEqual(res.reconstruct(None), "word1 word2 word3")

if __name__ == "__main__":
    unittest.main()