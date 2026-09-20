import argparse
import sys

from .core import compile_pattern


def _read_lines(fh):
    for line in fh:
        line = line.rstrip("\n")
        if line:
            yield line


def _read_null_separated(fh):
    # NUL isn't a line terminator Python's text-mode iteration understands,
    # so this has to buffer and split rather than iterate line by line.
    for item in fh.read().split("\0"):
        if item:
            yield item


def _iter_paths(files, use_null=False):
    reader = _read_null_separated if use_null else _read_lines
    if not files:
        yield from reader(sys.stdin)
        return
    for name in files:
        if name == "-":
            yield from reader(sys.stdin)
        else:
            with open(name, "r", encoding="utf-8") as fh:
                yield from reader(fh)


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
    parser.add_argument(
        "-0",
        "--null",
        action="store_true",
        help="paths are NUL-separated on input (e.g. from find -print0) "
        "and printed NUL-separated on output, instead of newline-separated",
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

    end = "\0" if args.null else "\n"
    found = False
    for path in _iter_paths(files, use_null=args.null):
        is_match = any(regex.fullmatch(path) is not None for regex in regexes)
        if is_match != args.invert:
            print(path, end=end)
            found = True
    return 0 if found else 1


if __name__ == "__main__":
    raise SystemExit(main())
