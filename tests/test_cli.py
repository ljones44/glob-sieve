import contextlib
import io
import os
import tempfile
import unittest

from globsieve.cli import main


class CliTests(unittest.TestCase):
    def _run(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = main(argv)
        return status, out.getvalue()

    def _write(self, dir, name, content):
        path = os.path.join(dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        return path

    def test_positional_pattern_matches_paths_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._write(tmp, "paths.txt", "foo.py\nsrc/bar.py\nREADME.md\n")
            status, out = self._run(["*.py", paths])
        self.assertEqual(status, 0)
        self.assertEqual(out, "foo.py\n")

    def test_pattern_file_ors_patterns_together(self):
        with tempfile.TemporaryDirectory() as tmp:
            patterns = self._write(tmp, "patterns.txt", "*.py\n*.md\n")
            paths = self._write(tmp, "paths.txt", "foo.py\nnotes.md\nfoo.txt\n")
            status, out = self._run(["-f", patterns, paths])
        self.assertEqual(status, 0)
        self.assertEqual(out, "foo.py\nnotes.md\n")

    def test_pattern_file_leaves_all_positionals_as_files(self):
        # Without --pattern-file, the first positional would be swallowed as
        # the pattern; with it, every positional is a paths file instead.
        with tempfile.TemporaryDirectory() as tmp:
            patterns = self._write(tmp, "patterns.txt", "*.py\n")
            paths_a = self._write(tmp, "a.txt", "foo.py\n")
            paths_b = self._write(tmp, "b.txt", "bar.py\nbar.txt\n")
            status, out = self._run(["-f", patterns, paths_a, paths_b])
        self.assertEqual(status, 0)
        self.assertEqual(out, "foo.py\nbar.py\n")

    def test_pattern_file_with_blank_lines_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            patterns = self._write(tmp, "patterns.txt", "*.py\n\n*.md\n")
            paths = self._write(tmp, "paths.txt", "foo.py\nnotes.md\n")
            status, out = self._run(["-f", patterns, paths])
        self.assertEqual(status, 0)
        self.assertEqual(out, "foo.py\nnotes.md\n")

    def test_no_pattern_and_no_pattern_file_errors(self):
        with self.assertRaises(SystemExit):
            self._run([])

    def test_empty_pattern_file_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            patterns = self._write(tmp, "patterns.txt", "")
            paths = self._write(tmp, "paths.txt", "foo.py\n")
            with self.assertRaises(SystemExit):
                self._run(["-f", patterns, paths])


if __name__ == "__main__":
    unittest.main()
