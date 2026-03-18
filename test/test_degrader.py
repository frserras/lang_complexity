import math
import unittest
from degrader import Degrader
from unicodedata import category as cat
from itertools import product


class testDegrader(unittest.TestCase):

    def test_deletion_char(self):
        test_strings = [
            "abcdefghijklmnopqrstuvwxyz",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "!@#$%^&*()_+!@#$%^&*()_+",
            "0123456789012345678901234567890123456789",
            "Olá, tudo bem com você?",
            "012345 6789012 3456789012 34567 890123456789",
        ]
        deletion_percentages = [i / 10.0 for i in range(10)]

        for original_text, percent in product(test_strings, deletion_percentages):
            with self.subTest(original_text=original_text, percent=percent):
                degrader = Degrader.new("deletion", "chars", percent=percent)
                degraded_text = degrader.degrade(original_text)

                non_space_count = sum(
                    1 for char in original_text if not cat(char).startswith("Z")
                )
                space_count = len(original_text) - non_space_count
                
                retention_rate = 1.0 - percent
                expected_non_spaces = math.ceil(round(non_space_count * retention_rate, 2))
                expected_length = expected_non_spaces + space_count

                self.assertEqual(len(degraded_text), expected_length)
                self.assertTrue(set(degraded_text) <= set(original_text))



    def test_deletion_lines(self):
        test_strings = [
            "\n".join("abcdefghijklmnopqrstuvwxyz"),  # 26 linhas de 1 char
            "Linha 1\nLinha 2\nLinha 3\nLinha 4\nLinha 5\nLinha 6\nLinha 7\nLinha 8\nLinha 9\nLinha 10", # 10 linhas
            "Apenas uma unica linha sem quebras", # 1 linha
            "12345\n67890\nABCDE\nFGHIJ", # 4 linhas
            "Olá!\nTudo bem com você?\nComo estão as coisas por aí?\nEspero que tudo ótimo.", # 4 linhas variadas
        ]
        deletion_percentages = [i / 10.0 for i in range(10)]

        for original_text, percent in product(test_strings, deletion_percentages):
            with self.subTest(original_text=original_text, percent=percent):
                degrader = Degrader.new("deletion", "lines", percent=percent)
                degraded_text = degrader.degrade(original_text)


                orig_lines = original_text.split("\n")
                deg_lines = degraded_text.split("\n")


                self.assertEqual(len(deg_lines), len(orig_lines))

                retained_count = 0
                for orig, deg in zip(orig_lines, deg_lines):
                    if orig == deg:
                        retained_count += 1
                    else:
                        self.assertTrue(deg == "")

                retention_rate = 1.0 - percent
                expected_retained = math.ceil(round(len(orig_lines) * retention_rate, 2))

                self.assertEqual(retained_count, expected_retained)

    def test_deletion_word(self):
        s = " ".join("abcdefghijklmnopqrstuvwxyz")
        p = 0.1
        q = 1 - p
        d = Degrader.new("deletion", "words", percent=p)
        o = d.degrade(s)

        len_degraded = len(o.split())
        len_expected = math.ceil(len(s.split()) * q)
        self.assertEqual(len_degraded, len_expected)

    def test_replace_char(self):
        s = "abcdefghijklmnopqrstuvwxyz"
        d = Degrader.new("replacement", "chars")
        o = d.degrade(s)

        len_degraded = len(o)
        len_expected = 10 * len(s)
        self.assertEqual(len_degraded, len_expected)

    def test_replace_word(self):
        s = " ".join("abcdefghijklmnopqrstuvwxyz")
        d = Degrader.new("replacement", "words")
        o = d.degrade(s)

        len_degraded = len(o.split())
        len_expected = len(s.split())
        self.assertEqual(len_degraded, len_expected)

    def test_replace_lines(self):
        s = "\n".join("abcdefghijklmnopqrstuvwxyz")
        d = Degrader.new("replacement", "lines")
        o = d.degrade(s)

        len_degraded = len(o.split("\n"))
        len_expected = len(s.split("\n"))
        self.assertEqual(len_degraded, len_expected)

    def test_sameness(self):
        s = "".join("abcdefghijklmnopqrstuvwxyz")
        d1 = Degrader.new("sameness", "chars")
        self.assertEqual(s, d1.degrade(s))

        s = " ".join("abcdefghijklmnopqrstuvwxyz")
        d2 = Degrader.new("sameness", "words")
        self.assertEqual(s, d2.degrade(s))

        s = "\n".join("abcdefghijklmnopqrstuvwxyz")
        d3 = Degrader.new("sameness", "lines")
        self.assertEqual(s, d3.degrade(s))


if __name__ == "__main__":
    unittest.main()
