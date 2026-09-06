import unittest

from globsieve.core import match


class TranslateTests(unittest.TestCase):
    def test_single_star_stays_within_one_segment(self):
        self.assertTrue(match("foo.py", "*.py"))
        self.assertFalse(match("src/foo.py", "*.py"))

    def test_double_star_crosses_segments(self):
        self.assertTrue(match("src/pkg/foo.py", "src/**/*.py"))
        self.assertTrue(match("src/foo.py", "src/**/*.py"))
        self.assertFalse(match("other/foo.py", "src/**/*.py"))

    def test_leading_double_star(self):
        self.assertTrue(match("a/b/c.txt", "**/c.txt"))
        self.assertTrue(match("c.txt", "**/c.txt"))

    def test_question_mark_matches_one_char_not_a_slash(self):
        self.assertTrue(match("a.py", "?.py"))
        self.assertFalse(match("ab.py", "?.py"))
        self.assertFalse(match("a/py", "?.py"))

    def test_character_class(self):
        self.assertTrue(match("a.py", "[ab].py"))
        self.assertFalse(match("c.py", "[ab].py"))
        self.assertTrue(match("c.py", "[!ab].py"))


if __name__ == "__main__":
    unittest.main()
