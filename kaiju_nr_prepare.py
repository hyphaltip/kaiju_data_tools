#!/usr/bin/env python3
"""
Kaiju NR database preparation script.

This script prepares a non-redundant protein database for Kaiju by extracting
sequences from NCBI databases based on taxon IDs from a taxon list file.

It replicates the functionality of:
    IDS=$(cut -f1 kaiju-taxonlistEuk.tsv | perl -p -e 's/\\n/,/g' | perl -p -e 's/,$/\\n/')
    blastdbcmd -taxids $IDS -db $DB/swissprot -out $SCRATCH/euk_nr.txt -dbtype prot -outfmt ">%a_%T %t\\n%s" -target_only
    perl -p -e 's/\\\\n/\\n/' $SCRATCH/euk_nr.txt > $SCRATCH/euk_nr.faa
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def read_taxon_ids(input_file):
    """
    Read taxon IDs from the first column of a TSV file.
    
    Args:
        input_file: Path to the input TSV file
        
    Returns:
        Comma-separated string of taxon IDs
    """
    try:
        taxon_ids = []
        with open(input_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    # Get the first column (split by tab)
                    fields = line.split('\t')
                    if fields:
                        taxon_ids.append(fields[0])
        
        # Join with commas
        return ','.join(taxon_ids)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)


def run_blastdbcmd(taxon_ids, db_path, output_file, dbtype='prot', 
                   outfmt='>%a_%T %t\\n%s', target_only=True):
    """
    Run blastdbcmd to extract sequences based on taxon IDs.
    
    Args:
        taxon_ids: Comma-separated string of taxon IDs
        db_path: Path to the BLAST database
        output_file: Output file path
        dbtype: Database type (default: 'prot')
        outfmt: Output format string (default: '>%a_%T %t\\n%s')
        target_only: Whether to use -target_only flag
    """
    cmd = [
        'blastdbcmd',
        '-taxids', taxon_ids,
        '-db', db_path,
        '-out', output_file,
        '-dbtype', dbtype,
        '-outfmt', outfmt
    ]
    
    if target_only:
        cmd.append('-target_only')
    
    try:
        print(f"Running: {' '.join(cmd)}", file=sys.stderr)
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running blastdbcmd: {e}", file=sys.stderr)
        if e.stdout:
            print(f"stdout: {e.stdout}", file=sys.stderr)
        if e.stderr:
            print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: blastdbcmd not found. Please ensure BLAST+ is installed.", file=sys.stderr)
        sys.exit(1)


def convert_literal_newlines(input_file, output_file):
    """
    Convert literal \\n in the file to actual newlines.
    
    Args:
        input_file: Input file path
        output_file: Output file path
    """
    try:
        with open(input_file, 'r') as f_in:
            content = f_in.read()
        
        # Replace literal \n with actual newlines
        content = content.replace('\\n', '\n')
        
        with open(output_file, 'w') as f_out:
            f_out.write(content)
            
        print(f"Converted literal newlines: {input_file} -> {output_file}", file=sys.stderr)
    except Exception as e:
        print(f"Error converting newlines: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Prepare non-redundant protein database for Kaiju',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input TSV file with taxon IDs in first column (e.g., kaiju-taxonlistEuk.tsv)'
    )
    
    parser.add_argument(
        '-d', '--database',
        required=True,
        help='Path to BLAST database (e.g., /srv/projects/db/ncbi/preformatted/20260128/swissprot)'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output directory or file prefix'
    )
    
    parser.add_argument(
        '--dbtype',
        default='prot',
        help='Database type (default: prot)'
    )
    
    parser.add_argument(
        '--outfmt',
        default='>%%a_%%T %%t\\n%%s',
        help='Output format string (default: >%%a_%%T %%t\\n%%s)'
    )
    
    parser.add_argument(
        '--no-target-only',
        action='store_true',
        help='Do not use -target_only flag'
    )
    
    args = parser.parse_args()
    
    # Determine output paths
    if os.path.isdir(args.output):
        # If output is a directory, use default filenames
        intermediate_file = os.path.join(args.output, 'euk_nr.txt')
        final_output = os.path.join(args.output, 'euk_nr.faa')
    else:
        # Use output as prefix
        intermediate_file = f"{args.output}.txt"
        final_output = f"{args.output}.faa"
    
    # Step 1: Read taxon IDs from input file
    print(f"Reading taxon IDs from {args.input}...", file=sys.stderr)
    taxon_ids = read_taxon_ids(args.input)
    print(f"Found {len(taxon_ids.split(','))} taxon IDs", file=sys.stderr)
    
    # Step 2: Run blastdbcmd
    print(f"Extracting sequences from database {args.database}...", file=sys.stderr)
    run_blastdbcmd(
        taxon_ids,
        args.database,
        intermediate_file,
        dbtype=args.dbtype,
        outfmt=args.outfmt,
        target_only=not args.no_target_only
    )
    
    # Step 3: Convert literal newlines to actual newlines
    print(f"Processing output file...", file=sys.stderr)
    convert_literal_newlines(intermediate_file, final_output)
    
    print(f"Done! Final output: {final_output}", file=sys.stderr)


if __name__ == '__main__':
    main()
