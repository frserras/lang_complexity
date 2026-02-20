import math
import unittest
import re
from test_NewDegrader import Degrader


class testDegrader(unittest.TestCase):

    def test_deletion_char(self):
        s = "abcdefghijklmnopqrstuvwxyz"
        p = 0.1
        q = 1 - p
        d = Degrader.new("deletion", "chars", percent=p)
        o = d.degrade(s)

        len_degraded = len(o)
        len_expected = math.ceil(len(s) * q)

        self.assertEqual(len_degraded, len_expected)

    def test_deletion_lines(self):
        st = "abcdefghijklmnopqrstuvwxyz"
        s = "\n".join(st)
        p = 0.1
        q = 1 - p
        d = Degrader.new("deletion", "lines", percent=p)
        o = d.degrade(s)

        len_degraded = len(o)
        len_expected = len(s) - int(len(st) * p)
        self.assertEqual(len_degraded, len_expected)

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

    def test_random_char_replacementUnic(self):
        s = "abcdefghijklmnopqrstuvwxyz"
        p = 0.1
        d = Degrader.new("random_char_replacementUnic", "chars", percent=p)
        o = d.degrade(s)

        # comprimento da string não mudou
        self.assertEqual(len(o), len(s))

        # porcentagem de caracteres alterados está próxima do esperado
        changed_chars = sum(1 for a, b in zip(s, o) if a != b)
        expected_changes = int(len(s) * p)
        self.assertAlmostEqual(changed_chars, expected_changes, delta=1)

        # caracteres alterados são diferentes dos originais
        for a, b in zip(s, o):
            if a != b:
                self.assertNotEqual(a, b)

    def test_random_word_replacementUnic(self):
        s = "The quick brown fox jumps over the lazy hot dog."
        p = 0.5
        unicode_char = '∑'
        d = Degrader.new("random_word_replacementUnic", "words", percent=p, unicode_char=unicode_char)
        o = d.degrade(s)

        # Verifica se o comprimento da string de saída é o mesmo que o da entrada
        self.assertEqual(len(o), len(s))

        # Conta o número de palavras substituídas
        original_words = s.split()
        replaced_words = [word for word in o.split() if set(word) == {unicode_char}]
        num_replaced = len(replaced_words)

        # Verifica se a porcentagem de palavras substituídas está próxima do esperado
        expected_replacements = int(len(original_words) * p)
        self.assertAlmostEqual(num_replaced, expected_replacements, delta=1)

        # Verifica se as palavras substituídas têm o mesmo comprimento que as originais
        for orig, repl in zip(s.split(), o.split()):
            if set(repl) == {unicode_char}:
                self.assertEqual(len(orig), len(repl))

        # Verifica se a pontuação foi preservada
        original_punctuation = re.findall(r'[^\w\s]', s)
        result_punctuation = re.findall(rf'[^\w\s{re.escape(unicode_char)}]', o)
        self.assertEqual(original_punctuation, result_punctuation)

        # Verifica se a estrutura geral (palavras/pontuação/espaços) foi mantida
        def tokenize(text, unicode_char=None):
            if unicode_char:
                pattern = rf'{re.escape(unicode_char)}+|\w+|[^\w\s]|\s+'
            else:
                pattern = r'\w+|[^\w\s]|\s+'
            return re.findall(pattern, text)

        original_structure = tokenize(s)
        result_structure = tokenize(o, unicode_char)
        self.assertEqual(len(original_structure), len(result_structure))

        # Verifica se cada token foi substituído corretamente ou mantido igual
        for orig, res in zip(original_structure, result_structure):
            if orig.isalnum():
                self.assertTrue(res.isalnum() or set(res) == {unicode_char})
            else:
                self.assertEqual(orig, res)

    def test_random_word_replacementUnic_full_replacement(self):
        s = "The quick brown fox jumps over the lazy dog."
        p = 1.0
        unicode_char = '∑'
        d = Degrader.new("random_word_replacementUnic", "words", percent=p, unicode_char=unicode_char)
        o = d.degrade(s)

        # Verifica se todas as palavras foram substituídas
        words = o.split()
        for word in words:
            self.assertTrue(set(word) == {unicode_char} or not word.isalnum())

        # Verifica se a pontuação foi preservada
        self.assertEqual(o[-1], '.')

    def test_random_word_replacementUnic_no_replacement(self):
        s = "The quick brown fox jumps over the lazy dog."
        p = 0.0
        unicode_char = '∑'
        d = Degrader.new("random_word_replacementUnic", "words", percent=p, unicode_char=unicode_char)
        o = d.degrade(s)

        # Verifica se nenhuma palavra foi substituída
        self.assertEqual(s, o)

    def test_random_word_replacementUnic_with_punctuation(self):
        s = "Hello, world! This is a test: how well does it work?"
        p = 0.5
        unicode_char = '∑'
        d = Degrader.new("random_word_replacementUnic", "words", percent=p, unicode_char=unicode_char)
        o = d.degrade(s)

        def tokenize(text, unicode_char):
            pattern = f'{re.escape(unicode_char)}+|\\w+|[^\\w\\s]'
            return [token if not all(c == unicode_char for c in token) else token
                    for token in re.findall(pattern, text)]

        original_tokens = tokenize(s, unicode_char)
        result_tokens = tokenize(o, unicode_char)

        self.assertEqual(len(original_tokens), len(result_tokens))

        for orig, res in zip(original_tokens, result_tokens):
            if not orig.isalnum():
                self.assertEqual(orig, res)  # Pontuação deve permanecer inalterada
            else:
                if all(c == unicode_char for c in res):
                    self.assertEqual(len(orig), len(res))  # Palavras substituídas devem ter o mesmo comprimento
                else:
                    self.assertEqual(orig, res)  # Palavras não substituídas devem permanecer iguais

        # Verifica se as palavras substituídas não incluem pontuação
        for word in o.split():
            if all(c == unicode_char for c in word):
                self.assertTrue(all(c == unicode_char for c in word))  # Verifica se a palavra é composta apenas pelo caractere Unicode

        # Verifica se a porcentagem de palavras substituídas está próxima do esperado
        word_count = sum(1 for token in original_tokens if token.isalnum())
        replaced_count = sum(1 for token in result_tokens if all(c == unicode_char for c in token))
        expected_replacements = int(word_count * p)
        self.assertAlmostEqual(replaced_count, expected_replacements, delta=1)

    def test_word_shuffle(self):
        s = "The quick brown fox jumps over the lazy dog"
        d = Degrader.new("word_shuffle", "words")
        o = d.degrade(s)

        # número de palavras não mudou
        self.assertEqual(len(o.split()), len(s.split()))

        # todas as palavras originais estão presentes no resultado
        self.assertEqual(set(o.split()), set(s.split()))

        # ordem das palavras é diferente (a menos que por acaso seja igual)
        self.assertNotEqual(o, s)

    def test_word_shuffle_with_separators_and_spaces(self):
        s = "!Essas, string. É um exemplo de embaralhamento?! Quero que tudo esteja barulhento; mas então voce de um jeito... Testar separadores é muito importe » pois assim faremos um bom trabalho—Pelo menos eu espero que sim. "
        d = Degrader.new("word_shuffle", "words", seed=42)
        o = d.degrade(s)
        p = 0.2

        # último caractere não-espaço é um separador ou uma letra
        last_non_space = o.rstrip()[-1]
        self.assertTrue(last_non_space in d.strategy.separators or last_non_space.isalpha())

        # todos os separadores originais estão presentes
        for sep in d.strategy.separators:
            if sep in s:
                self.assertIn(sep, o)

        # todas as palavras originais estão presentes
        original_words = set(re.findall(r'\w+', s))
        result_words = set(re.findall(r'\w+', o))
        self.assertEqual(original_words, result_words)

        # ordem das palavras é diferente (a menos que por acaso seja igual)
        self.assertNotEqual(s, o)

        # número de espaços é o mesmo
        self.assertEqual(s.count(' '), o.count(' '))

        # estrutura geral de separadores e palavras é mantida
        original_structure = re.findall(r'(\W+|\w+)', s)
        result_structure = re.findall(r'(\W+|\w+)', o)
        self.assertEqual(len(original_structure), len(result_structure))

        for orig, res in zip(original_structure, result_structure):
            if not orig.isalnum():
                self.assertEqual(orig, res)  # Separadores devem permanecer inalterados
            else:
                self.assertTrue(res.isalnum())  # Palavras devem ser substituídas por outras palavras


if __name__ == "__main__":
    unittest.main()
