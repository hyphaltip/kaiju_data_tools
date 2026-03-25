#!/usr/bin/env python3
"""Filter FASTA sequences based on exclude patterns in the header line."""

import argparse
import io
import sys


DEFAULT_EXCLUDED_SPECIES = ["[Homo sapiens]"]
DEFAULT_EXCLUDED_DESCRIPTIONS = [
    "immunoglobulin heavy chain",
    "immunoglobulin light chain",
]


EXAMPLES = """\
examples:
  # Use defaults (exclude Homo sapiens and immunoglobulin heavy/light chain)
  %(prog)s < input.fasta > output.fasta

  # Add an extra species exclusion on top of defaults
  %(prog)s --exclude-species "[Mus musculus]" < input.fasta > output.fasta

  # Replace defaults entirely with custom patterns
  %(prog)s --no-defaults \\
      --exclude-species "[Homo sapiens]" \\
      --exclude-description "hypothetical protein" \\
      < input.fasta > output.fasta

  # Multiple patterns
  %(prog)s \\
      --exclude-species "[Mus musculus]" \\
      --exclude-description "immunoglobulin kappa chain" \\
      < input.fasta > output.fasta
"""

REPLACEMENT_CHAR = '\ufffd'


def open_with_latin1_fallback(path):
    """Open a file using UTF-8, replacing undecodable bytes with the Unicode replacement char."""
    return open(path, 'r', encoding='utf-8', errors='replace')


def wrap_stdin_bytes():
    """Wrap sys.stdin.buffer so undecodable bytes become the Unicode replacement char."""
    return io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')


def parse_args():
    parser = argparse.ArgumentParser(
        description="Filter FASTA file, excluding sequences whose headers match specified patterns",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--input',
        metavar='FILE',
        default=None,
        help='Input FASTA file (default: stdin)'
    )
    parser.add_argument(
        '--output',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='Output file (default: stdout)'
    )
    parser.add_argument(
        '--exclude-species',
        metavar='SPECIES',
        action='append',
        dest='excluded_species',
        default=None,
        help=(
            'Exclude sequences containing this species string (case-sensitive, '
            'e.g. "[Homo sapiens]"). Can be specified multiple times. '
            f'Defaults to: {DEFAULT_EXCLUDED_SPECIES}'
        )
    )
    parser.add_argument(
        '--exclude-description',
        metavar='PATTERN',
        action='append',
        dest='excluded_descriptions',
        default=None,
        help=(
            'Exclude sequences whose header contains this string (case-insensitive). '
            'Can be specified multiple times. '
            f'Defaults to: {DEFAULT_EXCLUDED_DESCRIPTIONS}'
        )
    )
    parser.add_argument(
        '--no-defaults',
        action='store_true',
        help='Do not apply default exclusion patterns; only use patterns specified on the command line'
    )
    return parser.parse_args()


def is_excluded(header: str, excluded_species: list, excluded_descriptions: list) -> bool:
    if any(s in header for s in excluded_species):
        return True
    header_lower = header.lower()
    return any(term in header_lower for term in excluded_descriptions)


def filter_fasta(infile, outfile, excluded_species, excluded_descriptions):
    header = None
    seq_lines = []
    skip = False
    linenum = 0

    for line in infile:
        linenum += 1
        if REPLACEMENT_CHAR in line:
            if line.startswith('>'):
                print(
                    f"WARNING: line {linenum}: non-UTF-8 bytes in header, skipping sequence: {line.rstrip()!r}",
                    file=sys.stderr,
                )
                # flush pending record first
                if header and not skip:
                    outfile.write(header)
                    outfile.writelines(seq_lines)
                header = line
                skip = True
                seq_lines = []
            else:
                print(
                    f"WARNING: line {linenum}: non-UTF-8 bytes in sequence line, skipping",
                    file=sys.stderr,
                )
                skip = True
            continue

        if line.startswith('>'):
            if header and not skip:
                outfile.write(header)
                outfile.writelines(seq_lines)
            header = line
            skip = is_excluded(line, excluded_species, excluded_descriptions)
            seq_lines = []
        else:
            if not skip:
                seq_lines.append(line)

    # Write last record
    if header and not skip:
        outfile.write(header)
        outfile.writelines(seq_lines)


def main():
    args = parse_args()

    if args.no_defaults:
        excluded_species = args.excluded_species or []
        excluded_descriptions = args.excluded_descriptions or []
    else:
        excluded_species = DEFAULT_EXCLUDED_SPECIES + (args.excluded_species or [])
        excluded_descriptions = DEFAULT_EXCLUDED_DESCRIPTIONS + (args.excluded_descriptions or [])

    if args.input is None:
        infile = wrap_stdin_bytes()
        close_input = False
    else:
        infile = open_with_latin1_fallback(args.input)
        close_input = True

    try:
        filter_fasta(infile, args.output, excluded_species, excluded_descriptions)
    finally:
        if close_input:
            infile.close()
        if args.output is not sys.stdout:
            args.output.close()


if __name__ == "__main__":
    main()
