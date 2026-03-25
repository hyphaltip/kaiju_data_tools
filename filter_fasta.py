#!/usr/bin/env python3
"""Filter FASTA sequences, excluding Homo sapiens and immunoglobulin heavy/light chain entries."""

import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="Filter FASTA file, excluding Homo sapiens and immunoglobulin chain sequences"
    )
    parser.add_argument(
        '--input',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='Input file (default: stdin)'
    )
    parser.add_argument(
        '--output',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='Output file (default: stdout)'
    )
    return parser.parse_args()


EXCLUDED_SPECIES = "[Homo sapiens]"
EXCLUDED_DESCRIPTIONS = (
    "immunoglobulin heavy chain",
    "immunoglobulin light chain",
)


def is_excluded(header: str) -> bool:
    if EXCLUDED_SPECIES in header:
        return True
    header_lower = header.lower()
    return any(term in header_lower for term in EXCLUDED_DESCRIPTIONS)


def filter_fasta(infile, outfile):
    header = None
    seq_lines = []
    skip = False

    for line in infile:
        if line.startswith('>'):
            if header and not skip:
                outfile.write(header)
                outfile.writelines(seq_lines)
            header = line
            skip = is_excluded(line)
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
    try:
        filter_fasta(args.input, args.output)
    finally:
        if args.input is not sys.stdin:
            args.input.close()
        if args.output is not sys.stdout:
            args.output.close()


if __name__ == "__main__":
    main()
