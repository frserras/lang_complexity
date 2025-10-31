import unittest
import src.unit as U


class TestUnit(unittest.TestCase):
    def test_Chars(self):
        s = "abcdefghijklmnopqrstuvwxz"
        c = U.Chars()
        result = c.parse(s)
        self.assertEqual(len(result.index), len(s))
        joined = result.reconstruct()
        self.assertEqual(len(joined), len(s))
        self.assertEqual(joined, s)

    def test_NonSpaces(self):
        s = " ".join("abcdefghijklmnopqrstuvwxz")
        ns = U.NotChar(" ")
        result = ns.parse(s)
        joined = result.reconstruct()
        self.assertEqual(len(joined), len(s))
        self.assertEqual(joined, s)

    def test_Lines(self):
        s = "\n".join("abcdefghijklmnopqrstuvwxz")
        l = U.NotChar("\n")
        result = l.parse(s)
        joined = result.reconstruct()
        self.assertEqual(len(joined), len(s))
        self.assertEqual(joined, s)


if __name__ == "__main__":
    unittest.main()
