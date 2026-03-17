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
            with self.subTest(string="Reconstrução Parcial - Múltiplos Cenários"):
                
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