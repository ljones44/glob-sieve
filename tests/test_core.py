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

    def test_ignore_case(self):
        self.assertFalse(match("FOO.PY", "*.py"))
        self.assertTrue(match("FOO.PY", "*.py", ignore_case=True))
        self.assertTrue(match("src/Foo.py", "SRC/**/*.PY", ignore_case=True))
        self.assertFalse(match("src/Foo.py", "SRC/**/*.PY"))

    def test_ignore_case_applies_to_character_class(self):
        self.assertTrue(match("A.py", "[ab].py", ignore_case=True))
        self.assertFalse(match("A.py", "[ab].py"))

    def test_brace_expansion(self):
        self.assertTrue(match("foo.py", "foo.{py,txt}"))
        self.assertTrue(match("foo.txt", "foo.{py,txt}"))
        self.assertFalse(match("foo.md", "foo.{py,txt}"))

    def test_brace_expansion_combines_with_other_syntax(self):
        self.assertTrue(match("src/foo.yml", "src/**/*.{yml,yaml}"))
        self.assertTrue(match("src/pkg/foo.yaml", "src/**/*.{yml,yaml}"))
        self.assertFalse(match("src/foo.json", "src/**/*.{yml,yaml}"))

    def test_nested_brace_expansion(self):
        self.assertTrue(match("foo.yml", "foo.{md,{yml,yaml}}"))
        self.assertTrue(match("foo.yaml", "foo.{md,{yml,yaml}}"))
        self.assertTrue(match("foo.md", "foo.{md,{yml,yaml}}"))
        self.assertFalse(match("foo.json", "foo.{md,{yml,yaml}}"))

    def test_brace_group_without_comma_is_literal(self):
        self.assertTrue(match("a{b}c", "a{b}c"))
        self.assertFalse(match("abc", "a{b}c"))

    def test_unmatched_brace_is_literal(self):
        self.assertTrue(match("a{b", "a{b"))


if __name__ == "__main__":
    unittest.main()
