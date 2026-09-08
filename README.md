# globsieve

Answers one question: of these paths, which ones match this glob pattern?

The problem it's solving: `fnmatch` (and anything built on it, which is most
of the ad-hoc filtering people write) treats `*` as matching anything,
including `/`. That means a pattern like `*.py` will happily match
`build/generated/thing.py`, which is almost never what you meant when you
wrote it. Real glob tools (`pathlib`, `git`, shells) treat `*` as bounded by
a single path segment, and use `**` for "any number of segments, including
zero". globsieve implements that version, as a standalone filter you can
drop into a pipeline.

It doesn't touch the filesystem itself. You give it a pattern and a list of
paths (as text, one per line), and it tells you which ones match. That means
it works equally well on paths that exist on disk, paths from `git
ls-files`, paths from a tarball listing, or anything else that produces a
line-oriented list.

## Usage

Filter the output of `find`:

```
$ find . -type f | globsieve 'src/**/*.py'
src/globsieve/core.py
src/globsieve/cli.py
src/globsieve/__init__.py
```

Filter a file list, and read patterns as an argument instead of stdin:

```
$ git ls-files > tracked.txt
$ globsieve '*.md' tracked.txt
README.md
```

Invert the match to see what's left over after excluding a pattern:

```
$ git ls-files | globsieve -v '*.py'
README.md
LICENSE
.gitignore
pyproject.toml
```

Multiple input files are read in order; `-` means read stdin at that point
in the list. With no file arguments at all, stdin is read by default.

Match case-insensitively with `-i`:

```
$ echo 'README.MD' | globsieve -i '*.md'
README.MD
```

The pattern language:

- `*` matches any characters except `/`, within one path segment.
- `**` as a whole segment (`**/`, `/**`, or the entire pattern) matches zero
  or more path segments.
- `?` matches exactly one character, not `/`.
- `[seq]` and `[!seq]` match a single character from (or not from) a set,
  same as shell character classes.

## Install

No dependencies beyond the standard library. From a checkout:

```
$ pip install -e .
$ globsieve '*.py' <<< $'foo.py\nsrc/bar.py'
foo.py
```

Or just run it in place: `python3 -m globsieve.cli '*.py'` from `src/`.

## Tests

```
$ python3 -m unittest discover -s tests
```
