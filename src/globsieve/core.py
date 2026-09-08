"""Translate shell-style glob patterns into regexes and match paths against them.

This follows pathlib/glob semantics, not fnmatch semantics: a lone '*' matches
within one path segment only, and '**' matches zero or more whole segments.
fnmatch would let a plain '*' slide across directory separators, which makes
patterns like '*.py' silently match 'build/generated/thing.py' too.
"""

import re


def _translate_bracket(pattern, i):
    """Translate a `[...]` character class starting at pattern[i] == '['.

    Returns (regex_fragment, next_index).
    """
    n = len(pattern)
    j = i + 1
    if j < n and pattern[j] == "!":
        j += 1
    if j < n and pattern[j] == "]":
        j += 1
    while j < n and pattern[j] != "]":
        j += 1
    if j >= n:
        # unterminated '[', treat it as a literal
        return re.escape("["), i + 1
    stuff = pattern[i + 1 : j]
    if stuff.startswith("!"):
        stuff = "^" + stuff[1:]
    elif stuff.startswith("^"):
        stuff = "\\" + stuff
    return "[" + stuff + "]", j + 1


def translate(pattern):
    """Convert a glob pattern into an equivalent regex pattern string."""
    i, n = 0, len(pattern)
    out = []
    while i < n:
        c = pattern[i]
        if c == "*":
            is_double = pattern[i : i + 2] == "**"
            starts_segment = i == 0 or pattern[i - 1] == "/"
            end = i + 2 if is_double else i + 1
            ends_segment = end == n or pattern[end] == "/"
            if is_double and starts_segment and ends_segment:
                if end < n:
                    out.append("(?:.*/)?")
                    i = end + 1  # also swallow the trailing slash
                else:
                    out.append(".*")
                    i = end
            else:
                out.append("[^/]*")
                i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        elif c == "[":
            fragment, i = _translate_bracket(pattern, i)
            out.append(fragment)
        else:
            out.append(re.escape(c))
            i += 1
    return "".join(out)


def compile_pattern(pattern, ignore_case=False):
    """Compile a glob pattern into a regex meant to be used with fullmatch()."""
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(translate(pattern), flags)


def match(path, pattern, ignore_case=False):
    """Return True if path matches the glob pattern."""
    return compile_pattern(pattern, ignore_case).fullmatch(path) is not None
