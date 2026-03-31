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

                non_space_count_degraded = sum(
                    1 for char in degraded_text if not cat(char).startswith("Z")
                )
                space_count_degraded = len(degraded_text) - non_space_count_degraded
            
                
                retention_rate = 1.0 - percent
                expected_non_spaces = math.ceil(round(non_space_count * retention_rate, 2))
                expected_length = expected_non_spaces + space_count

                self.assertEqual(space_count, space_count_degraded)
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


    def test_deletion_words(self):
        test_strings = [
            " ".join("abcdefghijklmnopqrstuvwxyz"),
            "Uma frase normal com varias palavras de tamanhos diferentes",
            "Apenas-uma-palavra-inteira",
            "Testando   multiplos  espaços e \t tabulações",
            "123 456 789 012 345 678 901",
        ]
        deletion_percentages = [i / 10.0 for i in range(10)]

        for original_text, percent in product(test_strings, deletion_percentages):
            with self.subTest(original_text=original_text, percent=percent):
                degrader = Degrader.new("deletion", "words", percent=percent)
                degraded_text = degrader.degrade(original_text)

                orig_words = original_text.split()
                deg_words = degraded_text.split()

                retention_rate = 1.0 - percent
                expected_retained = math.ceil(round(len(orig_words) * retention_rate, 2))
                self.assertEqual(len(deg_words), expected_retained)

                orig_spaces = sum(
                    1 for char in original_text if cat(char).startswith("Z")
                )
                deg_spaces = sum(
                    1 for char in degraded_text if cat(char).startswith("Z")
                )
                self.assertEqual(orig_spaces, deg_spaces)

                self.assertTrue(set(deg_words) <= set(orig_words))

# The degrader test for the 'replacement', 'chars' mode was omitted because
# this mode isn't currently used by any of the library's implemented metrics. 
# A warning was added to the degrader's initialization to indicate that this
# combination lacks test coverage."
    # def test_replace_char(self):
    #     s = "abcdefghijklmnopqrstuvwxyz"
    #     d = Degrader.new("replacement", "chars")
    #     o = d.degrade(s)

    #     len_degraded = len(o)
    #     len_expected = 10 * len(s)
    #     self.assertEqual(len_degraded, len_expected)


    def test_replacement_words(self):
        test_strings = [
            "gato cachorro rato gato", #
            "a a a a a", 
            "Uma frase normal sem repeticoes", 
            "Testando \t espaços   e \n quebras com Testando e espaços", 
            "123 abc 123 def abc",
        ]

        for original_text in test_strings:
            with self.subTest(original_text=original_text):
                degrader = Degrader.new("replacement", "words")
                degraded_text = degrader.degrade(original_text)

                orig_words = original_text.split()
                deg_words = degraded_text.split()


                self.assertEqual(len(orig_words), len(deg_words))

                self.assertEqual(len(set(orig_words)), len(set(deg_words)))

                mapping = set(zip(orig_words, deg_words))
                self.assertEqual(len(mapping), len(set(orig_words)))

                for word in deg_words:
                    self.assertTrue(word.isdigit(), f"Textblock '{word}' is not an index.")

                orig_spaces = sum(
                    1 for char in original_text if cat(char).startswith("Z")
                )
                deg_spaces = sum(
                    1 for char in degraded_text if cat(char).startswith("Z")
                )
                self.assertEqual(orig_spaces, deg_spaces)

# The degrader test for the 'replacement', 'lines' mode was omitted because
# this mode isn't currently used by any of the library's implemented metrics. 
# A warning was added to the degrader's initialization to indicate that this
# combination lacks test coverage."

    # def test_replace_lines(self):
    #     s = "\n".join("abcdefghijklmnopqrstuvwxyz")
    #     d = Degrader.new("replacement", "lines")
    #     o = d.degrade(s)

    #     len_degraded = len(o.split("\n"))
    #     len_expected = len(s.split("\n"))
        # self.assertEqual(len_degraded, len_expected)


    def test_sameness(self):
        test_strings = [
            "abcdefghijklmnopqrstuvwxyz",
            "Uma frase normal com espaços.",
            "12345 67890 09876",
            "!@#$% ^&*() _+-=[]{}|;':,./<>?",
            "Texto\tcom\ttabs\ne\nquebras\r\nde\nlinha",
            "   Espaços no começo e no final   ",
            "Olá, mundo! 👋🌍🚀",
            "",
        ]
        
        units = ["chars", "words", "lines"]

        for original_text, unit in product(test_strings, units):
            with self.subTest(original_text=original_text, unit=unit):

                degrader = Degrader.new("sameness", unit)
                degraded_text = degrader.degrade(original_text)

                self.assertEqual(original_text, degraded_text)

    def test_masking_words(self):
            test_strings = [
                " ".join("abcdefghijklmnopqrstuvwxyz"),
                "Uma frase normal com varias palavras de tamanhos diferentes",
                "Apenas-uma-palavra-inteira",
                "Testando   multiplos  espaços e \t tabulações",
                "123 456 789 012 345 678 901",
            ]
            masking_percentages = [i / 10.0 for i in range(10)]
            mask_char = 'α'

            for original_text, percent in product(test_strings, masking_percentages):
                with self.subTest(original_text=original_text, percent=percent):
                    # Initialize degrader with the masking strategy
                    degrader = Degrader.new("masking", "words", percent=percent, mask=mask_char)
                    degraded_text = degrader.degrade(original_text)

                    # 3. Does the total number of characters remain the same?
                    self.assertEqual(
                        len(original_text), 
                        len(degraded_text), 
                        "The total character count must remain identical."
                    )

                    orig_words = original_text.split()
                    deg_words = degraded_text.split()

                    # The total number of units (words) should remain exactly the same
                    self.assertEqual(len(orig_words), len(deg_words))

                    masked_count = 0

                    for orig, deg in zip(orig_words, deg_words):
                        if orig != deg:
                            masked_count += 1
                            # 1. Were the elements actually masked?
                            # It should be replaced by the mask character while keeping its original length
                            expected_masked_word = mask_char * len(orig)
                            self.assertEqual(
                                deg, 
                                expected_masked_word,
                                f"Element was not properly masked. Expected '{expected_masked_word}', got '{deg}'"
                            )
                        else:
                            # 4. Was everything NOT in the masked index kept unaltered?
                            # If the word didn't change, it must be strictly identical to the original
                            self.assertEqual(orig, deg)

                    # 2. Was the correct amount of elements masked?
                    # Masking.execute uses: int(len(indices) * self.percent)
                    expected_masked_total = int(len(orig_words) * percent)
                    self.assertEqual(
                        masked_count, 
                        expected_masked_total,
                        f"Expected {expected_masked_total} masked elements, but found {masked_count}"
                    )

                    # Extra check: Ensure non-word characters (like spaces/tabs) were kept unaltered
                    # Assuming 'cat' is an alias for unicodedata.category
                    orig_spaces = sum(
                        1 for char in original_text if cat(char).startswith("Z")
                    )
                    deg_spaces = sum(
                        1 for char in degraded_text if cat(char).startswith("Z")
                    )
                    self.assertEqual(
                        orig_spaces, 
                        deg_spaces, 
                        "The number of whitespace characters must remain unchanged."
                    )


    def test_masking_char(self):
        test_strings = [
            "abcdefghijklmnopqrstuvwxyz",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "!@#$%^&*()_+!@#$%^&*()_+",
            "0123456789012345678901234567890123456789",
            "Olá, tudo bem com você?",
            "012345 6789012 3456789012 34567 890123456789",
        ]
        masking_percentages = [i / 10.0 for i in range(10)]
        mask_char = 'α'

        for original_text, percent in product(test_strings, masking_percentages):
            with self.subTest(original_text=original_text, percent=percent):
                degrader = Degrader.new("masking", "chars", percent=percent, mask=mask_char)
                degraded_text = degrader.degrade(original_text)

                # 3. Does the total number of characters remain the same?
                self.assertEqual(
                    len(original_text), 
                    len(degraded_text),
                    "The length of the string must remain identical during masking."
                )

                # Calculate how many valid indexable characters exist (non-spaces)
                non_space_count = sum(
                    1 for char in original_text if not cat(char).startswith("Z")
                )

                masked_count = 0

                # Iterate character by character
                for orig_char, deg_char in zip(original_text, degraded_text):
                    if orig_char != deg_char:
                        masked_count += 1
                        # 1. Was the character actually masked?
                        self.assertEqual(
                            deg_char, 
                            mask_char,
                            f"Expected mask character '{mask_char}', but got '{deg_char}'"
                        )
                    else:
                        # 4. Was everything else kept unaltered?
                        # If it didn't change, it must be the exact same character
                        self.assertEqual(orig_char, deg_char)

                # 2. Was the correct amount of characters masked?
                # Using the exact math from Masking.execute: int(len(indices) * self.percent)
                expected_masked_total = int(non_space_count * percent)
                self.assertEqual(
                    masked_count, 
                    expected_masked_total,
                    f"Expected {expected_masked_total} masked characters, but found {masked_count}"
                )

                # Extra check: Ensure non-indexable characters (like spaces) were kept unaltered
                orig_spaces = sum(
                    1 for char in original_text if cat(char).startswith("Z")
                )
                deg_spaces = sum(
                    1 for char in degraded_text if cat(char).startswith("Z")
                )
                self.assertEqual(
                    orig_spaces, 
                    deg_spaces,
                    "Whitespace characters should not be affected by character masking."
                )

if __name__ == "__main__":
    unittest.main()
