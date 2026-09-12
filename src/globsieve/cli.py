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
    parser.add_argument(
        "args",
        nargs="*",
        metavar="pattern [file ...]",
        help="glob pattern followed by files with one path per line; "
        "omit the pattern if --pattern-file is given",
    )
    parser.add_argument(
        "-v",
        "--invert",
        action="store_true",
        help="print paths that do NOT match instead of ones that do",
    )
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="match case-insensitively",
    )
    parser.add_argument(
        "-f",
        "--pattern-file",
        metavar="FILE",
        help="file with one glob pattern per line, ORed together; "
        "when given, every positional argument is treated as a path file",
    )
    args = parser.parse_args(argv)

    if args.pattern_file is not None:
        patterns = []
        with open(args.pattern_file, "r", encoding="utf-8") as fh:
            patterns.extend(_read_lines(fh))
        if not patterns:
            parser.error(f"{args.pattern_file!r} has no patterns in it")
        files = args.args
    else:
        if not args.args:
            parser.error("no pattern given: pass a pattern argument or --pattern-file")
        patterns = [args.args[0]]
        files = args.args[1:]

    regexes = [compile_pattern(p, ignore_case=args.ignore_case) for p in patterns]

    found = False
    for path in _iter_paths(files):
        is_match = any(regex.fullmatch(path) is not None for regex in regexes)
        if is_match != args.invert:
            print(path)
            found = True
    return 0 if found else 1


if __name__ == "__main__":
    raise SystemExit(main())
