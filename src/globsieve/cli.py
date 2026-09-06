import argparse
import sys

from .core import compile_pattern


def _read_lines(fh):
    for line in fh:
        line = line.rstrip("\n")
        if line:
            yield line


def _iter_paths(files):
    if not files:
        yield from _read_lines(sys.stdin)
        return
    for name in files:
        if name == "-":
            yield from _read_lines(sys.stdin)
        else:
            with open(name, "r", encoding="utf-8") as fh:
                yield from _read_lines(fh)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="globsieve",
        description="Print which of a list of paths match a glob pattern.",
    )
    parser.add_argument("pattern", help="glob pattern, e.g. 'src/**/*.py'")
    parser.add_argument(
        "files",
        nargs="*",
        help="files with one path per line; omit, or pass -, to read stdin",
    )
    parser.add_argument(
        "-v",
        "--invert",
        action="store_true",
        help="print paths that do NOT match instead of ones that do",
    )
    args = parser.parse_args(argv)

    regex = compile_pattern(args.pattern)
    found = False
    for path in _iter_paths(args.files):
        is_match = regex.fullmatch(path) is not None
        if is_match != args.invert:
            print(path)
            found = True
    return 0 if found else 1


if __name__ == "__main__":
    raise SystemExit(main())
