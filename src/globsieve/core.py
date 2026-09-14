"""Translate shell-style glob patterns into regexes and match paths against them.

This follows pathlib/glob semantics, not fnmatch semantics: a lone '*' matches
within one path segment only, and '**' matches zero or more whole segments.
fnmatch would let a plain '*' slide across directory separators, which makes
patterns like '*.py' silently match 'build/generated/thing.py' too.

`{a,b}` brace groups are expanded before translation, the way a shell would
expand them, rather than being folded into the regex translation itself.
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


def _find_matching_brace(pattern, start):
    """Return the index of the '}' matching pattern[start] == '{', or -1."""
    depth = 0
    for i in range(start, len(pattern)):
        if pattern[i] == "{":
            depth += 1
        elif pattern[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _split_top_level_commas(text):
    """Split text on commas that aren't inside a nested {...} group."""
    parts = []
    depth = 0
    start = 0
    for i, c in enumerate(text):
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c == "," and depth == 0:
            parts.append(text[start:i])
            start = i + 1
    parts.append(text[start:])
    return parts


def expand_braces(pattern):
    """Expand `{a,b,c}` groups into the list of concrete patterns they stand for.

    This is purely textual, like a shell's brace expansion: it runs before
    any other glob syntax is considered, so it doesn't know about `[...]`
    classes. A `{...}` group with no top-level comma isn't an expansion at
    all and is left as literal text, same as bash does.
    """
    i = pattern.find("{")
    if i == -1:
        return [pattern]
    j = _find_matching_brace(pattern, i)
    if j == -1:
        return [pattern]
    body = pattern[i + 1 : j]
    parts = _split_top_level_commas(body)
    if len(parts) == 1:
        rest = expand_braces(pattern[i + 1 :])
        return [pattern[: i + 1] + r for r in rest]
    prefix, suffix = pattern[:i], pattern[j + 1 :]
    results = []
    for part in parts:
        results.extend(expand_braces(prefix + part + suffix))
    return results


def compile_pattern(pattern, ignore_case=False):
    """Compile a glob pattern into a regex meant to be used with fullmatch()."""
    flags = re.IGNORECASE if ignore_case else 0
    alternatives = expand_braces(pattern)
    regex = "|".join(f"(?:{translate(p)})" for p in alternatives)
    return re.compile(regex, flags)


def match(path, pattern, ignore_case=False):
    """Return True if path matches the glob pattern."""
    return compile_pattern(pattern, ignore_case).fullmatch(path) is not None
